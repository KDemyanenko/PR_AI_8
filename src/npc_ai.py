"""Навчальний прототип C4→C5/C7 з ПР-1–ПР-7.

Призначення: оцінка ймовірності високої загрози та рекомендація
відступу NPC. НЕ реалізує рух, NavMesh і керування ігровим рушієм.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import train_test_split

SEED = 42
FEATURES = ['health_pct', 'distance_m', 'enemy_strength', 'player_visible', 'cover_available']
RETREAT = 'Відступити'
STAY = 'Залишитися/укритися'


def build_dataset(seed: int = SEED, count: int = 400):
    """Точне відтворення синтетичних даних PR-6 (не реальні логи гри)."""
    rng = np.random.default_rng(seed)
    hp = rng.integers(5, 101, count)
    distance = rng.uniform(0, 40, count).round(2)
    strength = rng.uniform(0.05, 1, count).round(3)
    visible = rng.integers(0, 2, count)
    cover = rng.integers(0, 2, count)
    risk_formula = (0.42 * (1 - hp / 100) + 0.26 * (1 - distance / 40)
                    + 0.24 * strength + 0.12 * visible - 0.06 * cover)
    y = (risk_formula >= 0.55).astype(int)
    features = pd.DataFrame({
        'health_pct': hp, 'distance_m': distance,
        'enemy_strength': strength, 'player_visible': visible,
        'cover_available': cover,
    })
    return features, pd.Series(y, name='high_threat')


def train_model():
    X, y = build_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=SEED, stratify=y)
    model = RandomForestClassifier(
        n_estimators=100, max_depth=7, min_samples_leaf=3, random_state=SEED)
    model.fit(X_train, y_train)
    return model, X, y, X_test, y_test


def classifier_metrics(model, X_test, y_test) -> dict[str, Any]:
    predictions = model.predict(X_test)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y_test, predictions, labels=[0, 1]).ravel())
    probabilities = model.predict_proba(X_test)
    confidence = probabilities.max(axis=1)
    bands = {}
    for label, mask in (
        ('auto_conf_ge_0_80', confidence >= .8),
        ('review_0_65_to_0_80', (confidence >= .65) & (confidence < .8)),
        ('reject_conf_lt_0_65', confidence < .65),
    ):
        n = int(mask.sum())
        n_correct = int((predictions[mask] == np.asarray(y_test)[mask]).sum())
        bands[label] = {'n': n, 'correct': n_correct,
                        'accuracy': n_correct / n if n else None}
    return {
        'source': 'Самостійно згенеровані синтетичні дані; мітки з формули, не реальна гра',
        'seed': SEED, 'records_total': 400, 'train_records': 300, 'test_records': 100,
        'accuracy': float(accuracy_score(y_test, predictions)),
        'recall_high_threat': float(recall_score(y_test, predictions, pos_label=1)),
        'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp,
        'confidence_is_calibrated': False,
        'bands': bands,
    }


def _valid_record(record: dict) -> tuple[dict[str, Any] | None, str | None]:
    required = ('health_pct', 'npc_position', 'player_position', 'enemy_strength',
                'player_visible', 'cover_available', 'retreat_allowed')
    if any(k not in record or record[k] is None for k in required):
        return None, 'Відсутні обов’язкові дані'
    try:
        hp = float(record['health_pct'])
        strength = float(record['enemy_strength'])
        npc = np.asarray(record['npc_position'], dtype=float)
        player = np.asarray(record['player_position'], dtype=float)
        if npc.shape != (2,) or player.shape != (2,):
            raise ValueError('координати мають містити X, Y')
        distance = float(np.linalg.norm(npc - player))
        if not np.isfinite([hp, strength, distance]).all():
            raise ValueError('NaN або нескінченні значення')
        if not (0 <= hp <= 100 and 0 <= strength <= 1):
            raise ValueError('параметр поза допустимими межами')
        if not all(type(record[k]) is bool for k in
                   ('player_visible', 'cover_available', 'retreat_allowed')):
            raise ValueError('некоректне логічне значення')
    except (TypeError, ValueError, OverflowError):
        return None, 'Некоректні дані'
    return {
        'health_pct': hp, 'distance_m': distance, 'enemy_strength': strength,
        'player_visible': int(record['player_visible']),
        'cover_available': int(record['cover_available']),
        'retreat_allowed': record['retreat_allowed'],
    }, None


def decide(record: dict, model=None, model_available: bool = True) -> dict[str, Any]:
    """Фінальна політика після ПР-7.

    - 0.80+ confidence: ML+перевірка правила DP-07;
    - [0.65, 0.80): резервне правило HP, запис на асинхронний перегляд QA;
    - менше 0.65: відкинути ML, резервне правило HP;
    - немає критичних даних: не запускати нову небезпечну дію.
    Втечу завжди обмежує retreat_allowed (C7); DP-08/DP-09 поза прототипом.
    """
    features, invalid_reason = _valid_record(record)
    base = {
        'dp_id': 'DP-07', 'uc_id': 'UC-04',
        'threat_score': None, 'confidence': None,
        'recommendation': STAY, 'mode': 'rejected',
        'qa_review': False, 'reason': invalid_reason,
        'next_step': 'C5/C7 → (за відступу C6/DP-08/DP-09) → C1',
    }
    if invalid_reason:
        base['reason'] = invalid_reason + '; безпечна зупинка до оновлення стану'
        base['qa_review'] = True
        return base

    def fallback(reason: str, mode: str, qa_review: bool) -> dict[str, Any]:
        base.update(recommendation=(RETREAT if features['health_pct'] <= 25 and
                         features['retreat_allowed'] else STAY),
                    mode=mode, reason=reason, qa_review=qa_review)
        return base

    if not model_available or model is None:
        return fallback('C4 недоступний; правило HP ≤ 25% та дозвіл C7', 'fallback', True)

    X = pd.DataFrame([[features[k] for k in FEATURES]], columns=FEATURES)
    try:
        p = model.predict_proba(X)[0]
        threat_score = float(p[list(model.classes_).index(1)])
        confidence = float(max(p))
    except (ValueError, IndexError, AttributeError):
        return fallback('Помилка оцінювання C4; правило HP ≤ 25%', 'fallback', True)

    base.update(threat_score=round(threat_score, 3), confidence=round(confidence, 3))
    if confidence < .65:
        return fallback('confidence < 0,65: відхилити ML; правило HP', 'fallback', True)
    if confidence < .80:
        return fallback('0,65 ≤ confidence < 0,80: правило HP; асинхронний перегляд QA',
                        'qa_review', True)
    retreat = (features['retreat_allowed'] and
               (features['health_pct'] <= 25 or threat_score >= .85))
    base.update(recommendation=RETREAT if retreat else STAY,
                mode='automatic',
                reason='Модель C4 + DP-07 з перевіркою обмежень C7',
                qa_review=False)
    return base


def controlled_cases() -> list[dict]:
    """16 ситуацій з ПР-6 / ПР-7, включно з помилковими даними."""
    def case(name, hp, dist, strength, visible, cover, allow, expected,
             model_available=True, missing_position=False):
        return {
            'name': name,
            'record': {'health_pct': hp, 'npc_position': [0, 0],
                       'player_position': None if missing_position else [dist, 0],
                       'enemy_strength': strength, 'player_visible': visible,
                       'cover_available': cover, 'retreat_allowed': allow},
            'expected': expected, 'model_available': model_available,
        }
    return [
        case('Низьке HP',20,5,.95,True,True,True,RETREAT),
        case('Здоровий NPC; ворог далеко',90,35,.20,False,True,True,STAY),
        case('Дуже сильний ворог поруч',55,2,.99,True,False,True,RETREAT),
        case('Босу заборонено втечу',15,2,.90,True,True,False,STAY),
        case('Спокійна ситуація',78,27,.12,False,True,True,STAY),
        case('Граничне HP=25',25,13,.30,True,False,True,RETREAT),
        case('HP=26, ворог далеко',26,37,.10,False,True,True,STAY),
        case('Сильний ворог без укриття',45,.5,.95,True,False,True,RETREAT),
        case('C4 недоступний',20,3,.85,True,True,True,RETREAT,model_available=False),
        case('Немає HP',None,3,.85,True,True,True,STAY),
        case('Проміжна впевненість',30,35,.50,True,False,True,STAY),
        case('Немає координат',12,3,.85,True,True,True,STAY,missing_position=True),
        case('HP=24, супротивник далеко',24,36,.10,False,True,True,RETREAT),
        case('HP=24, втечу заборонено',24,4,.80,True,True,False,STAY),
        case('Некоректне HP=105',105,4,.80,True,True,True,STAY),
        case('Некоректна сила ворога=-0.2',50,4,-.2,True,True,True,STAY),
    ]
