"""
Tests for SaveGameService with turn-based saves and per-empire design folders
"""
import unittest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.core.json_utils import load_json, save_json


class MockGameSession:
    """Mock GameSession for testing save operations."""

    def __init__(self, config=None, turn_number=1, num_empires=2):
        self.config = config or GameConfig()
        self.turn_number = turn_number
        self.save_path = None
        self.systems = [MagicMock()]  # At least one system

        # Create mock empires
        self.empires = []
        for i in range(num_empires):
            empire = MagicMock()
            empire.id = i
            empire.name = f"Empire {i}"
            self.empires.append(empire)

    def to_dict(self):
        return {
            'turn_number': self.turn_number,
            'save_path': self.save_path,
            'config': self.config.to_dict(),
            'galaxy': {'systems': {}, 'warp_lanes': [], 'radius': 4000},
            'empires': [{'id': e.id, 'name': e.name, 'color': (0, 0, 255),
                         'colony_ids': [], 'fleets': [], 'built_ship_designs': []}
                        for e in self.empires],
            'human_player_ids': [0, 1]
        }


class TestSaveGameServiceFolderStructure(unittest.TestCase):
    """Tests for save folder structure creation."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_save_creates_turns_folder(self):
        """First save creates turns/ subfolder"""
        session = MockGameSession()

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        self.assertTrue(success)
        turns_folder = os.path.join(save_path, "turns")
        self.assertTrue(os.path.exists(turns_folder), "turns/ folder should be created")

    def test_save_creates_per_empire_design_folders(self):
        """Save creates designs/empire_N/ for each empire"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ]
        )
        session = MockGameSession(config=config, num_empires=3)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        self.assertTrue(success)
        designs_folder = os.path.join(save_path, "designs")
        self.assertTrue(os.path.exists(designs_folder))

        # Check per-empire folders
        for i in range(3):
            empire_folder = os.path.join(designs_folder, f"empire_{i}")
            self.assertTrue(os.path.exists(empire_folder),
                            f"designs/empire_{i}/ folder should be created")

    def test_save_writes_turn_file(self):
        """Save writes to turns/turn_N.json"""
        session = MockGameSession(turn_number=5)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        self.assertTrue(success)
        turn_file = os.path.join(save_path, "turns", "turn_5.json")
        self.assertTrue(os.path.exists(turn_file),
                        f"Turn file should exist at turns/turn_5.json")

    def test_save_updates_metadata_latest_turn(self):
        """Metadata tracks latest_turn_number"""
        session = MockGameSession(turn_number=3)

        success, message, save_path = SaveGameService.save_game(session, "TestGame")

        self.assertTrue(success)
        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        self.assertEqual(metadata['latest_turn_number'], 3)

    def test_save_increment_turn_creates_new_file(self):
        """Second save creates turn_2.json, keeps turn_1.json"""
        session = MockGameSession(turn_number=1)

        # First save
        success1, _, save_path = SaveGameService.save_game(session, "TestGame")
        self.assertTrue(success1)

        # Increment turn and save again
        session.turn_number = 2
        session.save_path = save_path
        success2, _, _ = SaveGameService.save_game(session)

        self.assertTrue(success2)

        # Both turn files should exist
        turn1_file = os.path.join(save_path, "turns", "turn_1.json")
        turn2_file = os.path.join(save_path, "turns", "turn_2.json")

        self.assertTrue(os.path.exists(turn1_file), "turn_1.json should still exist")
        self.assertTrue(os.path.exists(turn2_file), "turn_2.json should be created")


class TestSaveGameServiceVersion(unittest.TestCase):
    """Tests for save version handling."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_save_version_is_2_0_0(self):
        """New saves use version 2.0.0"""
        session = MockGameSession()

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        self.assertTrue(success)
        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        self.assertEqual(metadata['version'], "2.0.0")

    def test_load_rejects_old_version(self):
        """Loading version 1.0.0 save returns error"""
        # Create save with valid structure but old version
        save_folder = os.path.join(self.tmpdir, "saves", "OldSave")
        turns_folder = os.path.join(save_folder, "turns")
        os.makedirs(turns_folder)

        # Old version metadata
        metadata = {
            'version': '1.0.0',
            'timestamp': '2026-01-01T00:00:00',
            'player_name': 'Test',
            'turn_number': 1,
            'latest_turn_number': 1
        }
        save_json(os.path.join(save_folder, "save_metadata.json"), metadata)

        # Game state in turns folder (valid structure)
        game_state = {
            'turn_number': 1,
            'config': GameConfig().to_dict(),
            'galaxy': {'systems': {}, 'warp_lanes': [], 'radius': 4000},
            'empires': [],
            'human_player_ids': [0, 1]
        }
        save_json(os.path.join(turns_folder, "turn_1.json"), game_state)

        # Attempt to load
        result, message = SaveGameService.load_game(save_folder)

        self.assertIsNone(result)
        self.assertIn("version", message.lower())


class TestSaveGameServiceLoad(unittest.TestCase):
    """Tests for loading saves."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_load_defaults_to_latest_turn(self):
        """load_game() loads highest turn number by default"""
        session = MockGameSession(turn_number=1)

        # Create save with multiple turns
        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        session.turn_number = 2
        session.save_path = save_path
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # Load without specifying turn
        loaded, message = SaveGameService.load_game(save_path)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.turn_number, 3)

    def test_load_specific_turn(self):
        """load_game(path, turn_number=N) loads specific turn"""
        session = MockGameSession(turn_number=1)

        # Create save with multiple turns
        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        session.turn_number = 2
        session.save_path = save_path
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # Load specific turn
        loaded, message = SaveGameService.load_game(save_path, turn_number=2)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.turn_number, 2)

    def test_list_turns_returns_all_turns(self):
        """list_turns() returns metadata for each turn file"""
        session = MockGameSession(turn_number=1)

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        session.turn_number = 2
        session.save_path = save_path
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # List turns
        turns = SaveGameService.list_turns(save_path)

        self.assertEqual(len(turns), 3)
        turn_numbers = [t['turn_number'] for t in turns]
        self.assertIn(1, turn_numbers)
        self.assertIn(2, turn_numbers)
        self.assertIn(3, turn_numbers)


class TestSaveGameServiceMetadata(unittest.TestCase):
    """Tests for save metadata."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_metadata_includes_empire_count(self):
        """Metadata includes number of empires"""
        config = GameConfig(
            players=[
                PlayerConfig(name="E1", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="E2", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="E3", theme="Romulans", color=(0, 0, 255)),
            ]
        )
        session = MockGameSession(config=config, num_empires=3)

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        self.assertEqual(metadata['empire_count'], 3)

    def test_metadata_includes_empire_names(self):
        """Metadata includes list of empire names"""
        session = MockGameSession(num_empires=2)
        session.empires[0].name = "Alpha Empire"
        session.empires[1].name = "Beta Empire"

        success, _, save_path = SaveGameService.save_game(session, "TestGame")

        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        self.assertIn("Alpha Empire", metadata['empire_names'])
        self.assertIn("Beta Empire", metadata['empire_names'])


if __name__ == '__main__':
    unittest.main()
