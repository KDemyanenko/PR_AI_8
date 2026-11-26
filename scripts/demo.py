"""Демонстрація UC-04 → DP-07 без підключеного ігрового рушія."""
from pprint import pprint
from src.npc_ai import decide, train_model


def main() -> None:
    model, *_ = train_model()
    action = {
        'health_pct': 20, 'npc_position': [0, 0], 'player_position': [5, 0],
        'enemy_strength': 0.95, 'player_visible': True,
        'cover_available': True, 'retreat_allowed': True,
    }
    print('Гравець атакує NPC: C1 → C2 → C3 → C4 → C5/C7 [DP-07]')
    response = decide(action, model)
    pprint(response, sort_dicts=False)
    print('DP-08 (вибір укриття) і DP-09 (перевірка NavMesh) — передбачені архітектурою,')
    print('але не реалізовані в цьому прототипі. Команда рушію тут не надсилається.')


if __name__ == '__main__':
    main()
