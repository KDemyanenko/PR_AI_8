"""Відтворюване тестування фінального прототипу (python -m scripts.evaluate)."""
from pathlib import Path
import json

import pandas as pd

from src.npc_ai import (build_dataset, classifier_metrics, controlled_cases,
                        decide, train_model)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    (ROOT / 'data').mkdir(exist_ok=True)
    (ROOT / 'results').mkdir(exist_ok=True)
    model, X, y, X_test, y_test = train_model()
    metrics = classifier_metrics(model, X_test, y_test)
    dataset = X.copy()
    dataset['high_threat'] = y
    dataset['split'] = ['test' if idx in X_test.index else 'train' for idx in X.index]
    dataset.to_csv(ROOT / 'data/synthetic_npc_400.csv', index_label='record_id')

    scored_rows = []
    total_correct = 0
    for i, c in enumerate(controlled_cases(), 1):
        result = decide(c['record'], model=model, model_available=c['model_available'])
        ok = result['recommendation'] == c['expected']
        total_correct += int(ok)
        scored_rows.append({
            'case': i, 'scenario': c['name'],
            'health_pct': c['record']['health_pct'],
            'distance_m': None if c['record']['player_position'] is None else c['record']['player_position'][0],
            'enemy_strength': c['record']['enemy_strength'],
            'player_visible': c['record']['player_visible'],
            'cover_available': c['record']['cover_available'],
            'retreat_allowed': c['record']['retreat_allowed'],
            'model_available': c['model_available'],
            'expected': c['expected'], 'actual': result['recommendation'],
            'correct': ok, 'threat_score': result['threat_score'],
            'confidence': result['confidence'], 'mode': result['mode'],
            'qa_review': result['qa_review'], 'reason': result['reason']
        })
    pd.DataFrame(scored_rows).to_csv(ROOT / 'results/controlled_scenarios.csv', index=False)
    metrics['controlled_cases'] = len(scored_rows)
    metrics['controlled_correct'] = total_correct
    metrics['controlled_recommendation_rate'] = total_correct / len(scored_rows)
    (ROOT / 'results/metrics.json').write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    probs = model.predict_proba(X_test)
    pred = model.predict(X_test)
    classes = list(model.classes_)
    threat_col = classes.index(1)
    failures = X_test.loc[pred != y_test.to_numpy()].copy()
    failure_probs = probs[pred != y_test.to_numpy()]
    failure_pred = pred[pred != y_test.to_numpy()]
    failures.insert(0, 'record_id', failures.index)
    failures['ground_truth'] = y_test.loc[failures.index].to_numpy()
    failures['predicted_class'] = failure_pred
    failures['threat_score'] = failure_probs[:, threat_col].round(3)
    failures['confidence'] = failure_probs.max(axis=1).round(3)
    failures.to_csv(ROOT / 'results/misclassified_threats.csv', index=False)
    assert len(X) == 400 and len(X_test) == 100
    assert total_correct == len(scored_rows), 'Потрібно перевірити відхилення контрольних сценаріїв'
    print('Перевірка даних:', len(X), 'записів;', len(X_test), 'тестових')
    print('Матриця: TN={tn}, FP={fp}, FN={fn}, TP={tp}'.format(**metrics))
    print('Accuracy={:.1%}; Recall(high threat)={:.1%}'.format(
        metrics['accuracy'], metrics['recall_high_threat']))
    print('Контрольні сценарії: {}/{}'.format(total_correct, len(scored_rows)))
    print('Групи впевненості:', metrics['bands'])
    print('Результати записані в data/ та results/')


if __name__ == '__main__':
    main()
