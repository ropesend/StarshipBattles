"""
Tests for SaveSelectionWindow with turn list feature.
"""
import unittest
import tempfile
import shutil
import os
from unittest.mock import MagicMock

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_config import GameConfig


class MockGameSession:
    """Mock GameSession for testing save operations."""

    def __init__(self, turn_number=1, num_empires=2):
        self.config = GameConfig()
        self.turn_number = turn_number
        self.save_path = None
        self.systems = [MagicMock()]

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


class TestSaveSelectionTurnList(unittest.TestCase):
    """Tests for turn list functionality in save selection."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_list_turns_returns_all_turns(self):
        """list_turns() returns metadata for each turn file."""
        session = MockGameSession(turn_number=1)

        # Create save with multiple turns
        success, _, save_path = SaveGameService.save_game(session, "TurnListTest")
        session.save_path = save_path

        session.turn_number = 2
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # List turns
        turns = SaveGameService.list_turns(save_path)

        self.assertEqual(len(turns), 3)
        turn_numbers = [t['turn_number'] for t in turns]
        self.assertEqual(turn_numbers, [1, 2, 3])

    def test_list_turns_includes_metadata(self):
        """Each turn entry includes filename, timestamp, and size."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "MetadataTest")

        turns = SaveGameService.list_turns(save_path)

        self.assertEqual(len(turns), 1)
        turn = turns[0]

        self.assertIn('turn_number', turn)
        self.assertIn('filename', turn)
        self.assertIn('timestamp', turn)
        self.assertIn('size', turn)
        self.assertIn('path', turn)

        self.assertEqual(turn['turn_number'], 1)
        self.assertEqual(turn['filename'], 'turn_1.json')

    def test_loading_save_defaults_to_latest(self):
        """Loading without turn_number loads latest turn."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "LatestTest")
        session.save_path = save_path

        session.turn_number = 2
        SaveGameService.save_game(session)

        session.turn_number = 5
        SaveGameService.save_game(session)

        # Load without specifying turn
        loaded, message = SaveGameService.load_game(save_path)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.turn_number, 5)

    def test_loading_specific_turn(self):
        """load_game(path, turn_number=N) loads specific turn state."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "SpecificTurnTest")
        session.save_path = save_path

        session.turn_number = 2
        SaveGameService.save_game(session)

        session.turn_number = 3
        SaveGameService.save_game(session)

        # Load specific turn
        loaded, message = SaveGameService.load_game(save_path, turn_number=2)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.turn_number, 2)

    def test_loading_nonexistent_turn_fails(self):
        """Loading turn that doesn't exist returns error."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "NonexistentTest")

        # Try to load turn 5 when only turn 1 exists
        loaded, message = SaveGameService.load_game(save_path, turn_number=5)

        self.assertIsNone(loaded)
        self.assertIn("5", message)


class TestSaveSelectionListSaves(unittest.TestCase):
    """Tests for save listing functionality."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_list_saves_returns_all_saves(self):
        """list_saves() returns all available saves."""
        # Create multiple saves - each needs a fresh session to avoid save_path reuse
        session1 = MockGameSession(turn_number=1)
        session2 = MockGameSession(turn_number=1)
        session3 = MockGameSession(turn_number=1)

        SaveGameService.save_game(session1, "Save1")
        SaveGameService.save_game(session2, "Save2")
        SaveGameService.save_game(session3, "Save3")

        saves = SaveGameService.list_saves()

        self.assertEqual(len(saves), 3)
        save_names = [s['save_name'] for s in saves]
        self.assertIn("Save1", save_names)
        self.assertIn("Save2", save_names)
        self.assertIn("Save3", save_names)

    def test_list_saves_includes_metadata(self):
        """Each save includes relevant metadata for display."""
        session = MockGameSession(turn_number=1)
        session.config.players[0].name = "Test Player"

        SaveGameService.save_game(session, "MetadataTest")

        saves = SaveGameService.list_saves()

        self.assertEqual(len(saves), 1)
        save = saves[0]

        self.assertIn('save_name', save)
        self.assertIn('save_path', save)
        self.assertIn('player_name', save)
        self.assertIn('turn_number', save)
        self.assertIn('timestamp', save)

    def test_list_saves_sorted_by_timestamp(self):
        """Saves are sorted by timestamp (newest first)."""
        import time

        # Create separate sessions to avoid save_path reuse
        session1 = MockGameSession(turn_number=1)
        session2 = MockGameSession(turn_number=1)

        SaveGameService.save_game(session1, "OldSave")
        time.sleep(0.1)  # Ensure different timestamp
        SaveGameService.save_game(session2, "NewSave")

        saves = SaveGameService.list_saves()

        # Newest first
        self.assertEqual(saves[0]['save_name'], "NewSave")
        self.assertEqual(saves[1]['save_name'], "OldSave")


class TestSaveSelectionEmpireInfo(unittest.TestCase):
    """Tests for empire information in save metadata."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir)

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tmpdir)

    def test_save_metadata_includes_empire_count(self):
        """Metadata includes number of empires."""
        session = MockGameSession(turn_number=1, num_empires=3)
        success, _, save_path = SaveGameService.save_game(session, "EmpireCountTest")

        info = SaveGameService.get_save_info(save_path)

        self.assertEqual(info['empire_count'], 3)

    def test_save_metadata_includes_empire_names(self):
        """Metadata includes list of empire names."""
        session = MockGameSession(turn_number=1, num_empires=2)
        session.empires[0].name = "Federation"
        session.empires[1].name = "Romulans"

        success, _, save_path = SaveGameService.save_game(session, "EmpireNamesTest")

        info = SaveGameService.get_save_info(save_path)

        self.assertIn("Federation", info['empire_names'])
        self.assertIn("Romulans", info['empire_names'])


if __name__ == '__main__':
    unittest.main()
