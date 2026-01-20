"""
Tests for GameSession with multi-empire support
"""
import unittest
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig, THEME_DEFAULTS


class TestGameSessionMultiEmpire(unittest.TestCase):
    """Tests for GameSession multi-empire support"""

    def test_game_session_creates_n_empires(self):
        """GameSession creates empire for each PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertEqual(len(session.empires), 3)
        self.assertEqual(session.empires[0].name, "Empire A")
        self.assertEqual(session.empires[1].name, "Empire B")
        self.assertEqual(session.empires[2].name, "Empire C")

    def test_game_session_assigns_empire_ids_sequentially(self):
        """Empire IDs are 0, 1, 2, 3 based on player order"""
        config = GameConfig(
            players=[
                PlayerConfig(name=f"Empire {i}", theme=THEME_DEFAULTS[i][0], color=THEME_DEFAULTS[i][1])
                for i in range(4)
            ],
            system_count=10
        )

        session = GameSession(config=config)

        for i, empire in enumerate(session.empires):
            self.assertEqual(empire.id, i)

    def test_game_session_sets_human_player_ids(self):
        """human_player_ids reflects is_human flag from PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Human 1", theme="Federation", color=(255, 0, 0), is_human=True),
                PlayerConfig(name="AI 1", theme="Atlantians", color=(0, 255, 0), is_human=False),
                PlayerConfig(name="Human 2", theme="Romulans", color=(0, 0, 255), is_human=True),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertEqual(len(session.human_player_ids), 2)
        self.assertIn(0, session.human_player_ids)  # Human 1
        self.assertNotIn(1, session.human_player_ids)  # AI 1
        self.assertIn(2, session.human_player_ids)  # Human 2

    def test_game_session_initial_scenario_distributes_colonies(self):
        """Each empire gets a starting colony in different system"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        # Each empire should have at least one colony
        for empire in session.empires:
            self.assertGreater(len(empire.colonies), 0, f"Empire {empire.name} has no colonies")

        # Colonies should be in different systems
        colony_systems = set()
        for empire in session.empires:
            for colony in empire.colonies:
                # Find which system this colony is in
                for system in session.systems:
                    if colony in system.planets:
                        colony_systems.add(system)
                        break

        self.assertEqual(len(colony_systems), 2, "Empires should start in different systems")

    def test_game_session_3_player_setup(self):
        """3-player game creates exactly 3 empires with colonies"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertEqual(len(session.empires), 3)

        # All should have colonies
        for empire in session.empires:
            self.assertGreater(len(empire.colonies), 0)

    def test_game_session_4_player_setup(self):
        """4-player game creates exactly 4 empires with colonies"""
        config = GameConfig(
            players=[
                PlayerConfig(name=f"Empire {i}", theme=THEME_DEFAULTS[i][0], color=THEME_DEFAULTS[i][1])
                for i in range(4)
            ],
            system_count=15  # Need enough systems for 4 players
        )

        session = GameSession(config=config)

        self.assertEqual(len(session.empires), 4)

        # All should have colonies
        for empire in session.empires:
            self.assertGreater(len(empire.colonies), 0)

    def test_game_session_empire_themes_match_config(self):
        """Empire themes are set from PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Fed", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Atl", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertEqual(session.empires[0].empire_theme_id, "Federation")
        self.assertEqual(session.empires[1].empire_theme_id, "Atlantians")

    def test_game_session_empire_colors_match_config(self):
        """Empire colors are set from PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Red", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Green", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertEqual(session.empires[0].color, (255, 0, 0))
        self.assertEqual(session.empires[1].color, (0, 255, 0))

    def test_game_session_serialization_preserves_empires(self):
        """GameSession serialization preserves all empire data"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=10
        )

        original = GameSession(config=config)
        original.turn_number = 5

        data = original.to_dict()
        restored = GameSession.from_dict(data)

        self.assertEqual(len(restored.empires), 3)
        self.assertEqual(restored.turn_number, 5)
        self.assertEqual(restored.empires[0].name, "Empire A")
        self.assertEqual(restored.empires[1].name, "Empire B")
        self.assertEqual(restored.empires[2].name, "Empire C")

    def test_game_session_1_player_setup(self):
        """1-player game creates single empire"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Solo Empire", theme="Federation", color=(255, 0, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertEqual(len(session.empires), 1)
        self.assertGreater(len(session.empires[0].colonies), 0)


class TestGameSessionCompatibility(unittest.TestCase):
    """Tests for compatibility references"""

    def test_player_empire_reference(self):
        """player_empire convenience reference points to first empire"""
        config = GameConfig(
            players=[
                PlayerConfig(name="First", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Second", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertIs(session.player_empire, session.empires[0])

    def test_enemy_empire_reference(self):
        """enemy_empire convenience reference points to second empire"""
        config = GameConfig(
            players=[
                PlayerConfig(name="First", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Second", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        self.assertIs(session.enemy_empire, session.empires[1])


if __name__ == '__main__':
    unittest.main()
