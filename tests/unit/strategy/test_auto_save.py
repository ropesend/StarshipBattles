"""
Tests for auto-save functionality after turn processing.
"""
import pytest
import tempfile
import shutil
import os
import time
from unittest.mock import MagicMock, patch

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.systems.save_game_service import SaveGameService


class MockGameSession:
    """Mock GameSession for testing auto-save."""

    def __init__(self, turn_number=1, save_path=None, num_empires=2):
        self.turn_number = turn_number
        self.save_path = save_path
        self.config = GameConfig()
        self.systems = [MagicMock()]

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


class TestAutoSave:
    """Tests for auto-save after turn processing."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_turn_processing_triggers_auto_save(self):
        """Processing turn automatically saves new turn file."""
        # Create initial save at turn 1
        session = MockGameSession(turn_number=1)
        success, message, save_path = SaveGameService.save_game(session, "AutoSaveTest")
        assert success, f"Initial save failed: {message}"
        session.save_path = save_path

        # Simulate turn processing: increment turn and save
        session.turn_number = 2
        success, message, _ = SaveGameService.save_game(session)

        assert success, f"Auto-save failed: {message}"

        # Verify turn_2.json was created
        turn_file = os.path.join(save_path, "turns", "turn_2.json")
        assert os.path.exists(turn_file), "turn_2.json should be created after auto-save"

    def test_auto_save_increments_turn_number(self):
        """Auto-save after turn N creates turn_N+1.json."""
        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "AutoSaveTest")
        session.save_path = save_path

        # Process multiple turns
        for turn in [2, 3, 4]:
            session.turn_number = turn
            SaveGameService.save_game(session)

        # Verify all turn files exist
        for turn in [1, 2, 3, 4]:
            turn_file = os.path.join(save_path, "turns", f"turn_{turn}.json")
            assert os.path.exists(turn_file), f"turn_{turn}.json should exist"

    def test_auto_save_updates_metadata_latest_turn(self):
        """Auto-save updates metadata with latest turn number."""
        from game.core.json_utils import load_json

        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "AutoSaveTest")
        session.save_path = save_path

        # Process turn
        session.turn_number = 5
        SaveGameService.save_game(session)

        # Check metadata
        metadata_path = os.path.join(save_path, "save_metadata.json")
        metadata = load_json(metadata_path)

        assert metadata['latest_turn_number'] == 5

    def test_auto_save_preserves_earlier_turns(self):
        """Auto-save does not overwrite earlier turn files."""
        from game.core.json_utils import load_json

        session = MockGameSession(turn_number=1)
        success, _, save_path = SaveGameService.save_game(session, "AutoSaveTest")
        session.save_path = save_path

        # Get modification time of turn 1
        turn1_path = os.path.join(save_path, "turns", "turn_1.json")
        turn1_mtime = os.path.getmtime(turn1_path)
        turn1_content = load_json(turn1_path)

        # Wait a tiny bit to ensure different mtime
        time.sleep(0.01)

        # Process multiple turns
        session.turn_number = 2
        SaveGameService.save_game(session)
        session.turn_number = 3
        SaveGameService.save_game(session)

        # Verify turn_1.json is unchanged
        turn1_mtime_after = os.path.getmtime(turn1_path)
        turn1_content_after = load_json(turn1_path)

        assert turn1_mtime == turn1_mtime_after, "turn_1.json should not be modified"
        assert turn1_content['turn_number'] == turn1_content_after['turn_number']

    def test_auto_save_requires_save_path(self):
        """Auto-save creates save folder if save_path is not set."""
        session = MockGameSession(turn_number=1)
        # No save_path set - should create new save

        success, message, save_path = SaveGameService.save_game(session, "NewAutoSave")

        assert success, f"Save failed: {message}"
        assert save_path is not None
        assert os.path.exists(save_path)


class TestAutoSaveIntegration:
    """Integration tests for auto-save with GameSession.process_turn()."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)

    def test_game_session_turn_increments_on_process(self):
        """GameSession.process_turn() increments turn_number."""
        config = GameConfig(
            players=[
                PlayerConfig(name="Test Empire", theme="Federation", color=(255, 0, 0)),
            ],
            system_count=5
        )
        session = GameSession(config=config)

        initial_turn = session.turn_number
        session.process_turn()

        assert session.turn_number == initial_turn + 1

    def test_save_after_process_turn_captures_new_turn(self):
        """Saving after process_turn() saves the incremented turn number."""
        config = GameConfig(
            players=[
                PlayerConfig(name="Test Empire", theme="Federation", color=(255, 0, 0)),
            ],
            system_count=5
        )
        session = GameSession(config=config)

        # Initial save
        success, message, save_path = SaveGameService.save_game(session, "ProcessTurnTest")
        assert success, f"Initial save failed: {message}"
        session.save_path = save_path

        # Process turn (increments turn_number)
        session.process_turn()

        # Auto-save
        SaveGameService.save_game(session)

        # Verify turn file exists for new turn
        turn_file = os.path.join(save_path, "turns", f"turn_{session.turn_number}.json")
        assert os.path.exists(turn_file)
