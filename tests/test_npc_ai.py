"""Мінімальні автоматизовані тести без стороннього test framework."""
import unittest
from src.npc_ai import (RETREAT, STAY, classifier_metrics, controlled_cases,
                        decide, train_model)


class TestNPCPrototype(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, _, _, cls.X_test, cls.y_test = train_model()

    def test_train_test_split_and_metrics(self):
        m = classifier_metrics(self.model, self.X_test, self.y_test)
        self.assertEqual(m['test_records'], 100)
        self.assertEqual(m['train_records'], 300)
        self.assertEqual((m['tn'], m['fp'], m['fn'], m['tp']), (63, 1, 8, 28))
        self.assertAlmostEqual(m['accuracy'], .91)

    def test_all_16_controlled_scenarios(self):
        for scenario in controlled_cases():
            with self.subTest(scenario=scenario['name']):
                r = decide(scenario['record'], self.model, scenario['model_available'])
                self.assertEqual(r['recommendation'], scenario['expected'])

    def test_missing_data_rejects_new_action(self):
        r = decide({'health_pct': 10}, self.model)
        self.assertEqual((r['recommendation'], r['mode']), (STAY, 'rejected'))

    def test_missing_model_uses_hp_fallback(self):
        c = controlled_cases()[0]
        r = decide(c['record'], model=None)
        self.assertEqual((r['recommendation'], r['mode']), (RETREAT, 'fallback'))

    def test_developer_blocks_escape(self):
        c = controlled_cases()[3]
        r = decide(c['record'], self.model)
        self.assertEqual(r['recommendation'], STAY)

    def test_qa_review_without_in_game_pause(self):
        # Рішення при середній впевненості — виконати запасне правило
        # і записати приклад для подальшої перевірки людиною.
        rec = dict(health_pct=47, npc_position=[0, 0], player_position=[5.76, 0],
                   enemy_strength=0.735, player_visible=False,
                   cover_available=True, retreat_allowed=True)
        r = decide(rec, self.model)
        self.assertTrue(r['qa_review'])
        self.assertEqual(r['mode'], 'qa_review')
        self.assertEqual(r['recommendation'], STAY)


if __name__ == '__main__':
    unittest.main()
