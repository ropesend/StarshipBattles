"""
Tests for SaveGameService error handling.

Covers:
- No design migration (BUG-29)
- Error logging (ERR-004)
- User-friendly errors (ERR-019)
- Exception handling (PROJ-45)
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import patch

from unittest.mock import MagicMock

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_config import GameConfig
from game.core.json_utils import save_json
from game.core import paths as paths_module


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


class TestSaveGameServiceNoDesignMigration:
    """Tests for BUG-29: New games should not inherit designs from temp folder."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)

        # Create temp designs folder with some designs (simulating previous game sessions)
        temp_designs = os.path.join(tempfile.gettempdir(), "starship_battles_temp_designs", "empire_0")
        os.makedirs(temp_designs, exist_ok=True)

        # Create a test design in temp folder
        test_design = {
            "name": "Old Design From Temp",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "mass": 1000.0,
            "layers": {}
        }
        save_json(os.path.join(temp_designs, "old_design.json"), test_design)

        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir, temp_designs

        shutil.rmtree(tmpdir)
        # Clean up temp design we created
        temp_design_file = os.path.join(temp_designs, "old_design.json")
        if os.path.exists(temp_design_file):
            os.remove(temp_design_file)

    def test_new_game_does_not_migrate_temp_designs(self, setup_tmpdir):
        """BUG-29: New game save should NOT copy designs from temp folder"""
        tmpdir, temp_designs = setup_tmpdir
        session = MockGameSession()

        success, message, save_path = SaveGameService.save_game(session, "NewGame")

        assert success, f"Save failed: {message}"

        # Check that the designs folder for empire 0 is EMPTY
        empire_designs = os.path.join(save_path, "designs", "empire_0")
        assert os.path.exists(empire_designs), "Empire designs folder should exist"

        design_files = [f for f in os.listdir(empire_designs) if f.endswith('.json')]
        assert len(design_files) == 0, f"New game should have NO designs, but found: {design_files}"


class TestSaveGameServiceErrorLogging:
    """Tests for error logging in SaveGameService (ERR-004)."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)

    def test_save_error_logs_with_traceback(self, caplog):
        """Save errors should log full traceback, not print to stdout."""
        import logging
        from game.core.exceptions import ValidationException

        session = MockGameSession()

        # Mock to_dict to raise a ValidationException (domain exception used for serialization errors)
        def raise_error():
            raise ValidationException("Test save error", code="V001")

        session.to_dict = raise_error

        with caplog.at_level(logging.ERROR):
            success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert not success
        # User-facing message should be generic (not expose internal error details)
        assert "save failed" in message.lower() or "unable to serialize" in message.lower()

        # Should have logged an error with the actual error message
        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "Should log error on save failure"
        # Internal error should be logged (not shown to user)
        assert any("Test save error" in r.message for r in error_logs)

    def test_load_error_logs_with_context(self, caplog, setup_tmpdir):
        """Load errors should log with save path context."""
        import logging
        import json

        tmpdir = setup_tmpdir

        # Create a save with valid metadata but corrupted turn file
        save_path = os.path.join(tmpdir, "saves", "BadSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)
        with open(os.path.join(save_path, "turns", "turn_1.json"), "w") as f:
            f.write("{ invalid json }")  # Corrupted JSON

        metadata = {
            "version": "3.0.0",  # Must match SaveGameService.SAVE_VERSION
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        with open(os.path.join(save_path, "save_metadata.json"), "w") as f:
            json.dump(metadata, f)

        with caplog.at_level(logging.ERROR):
            result, message = SaveGameService.load_game(save_path)

        assert result is None
        assert "corrupted" in message.lower() or "cannot read" in message.lower()
        # Should have logged an error with context
        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0, "Should log error on load failure"


class TestSaveGameServiceUserFriendlyErrors:
    """Tests for user-friendly error messages in SaveGameService (ERR-019)."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)

    def test_load_error_message_is_user_friendly(self, setup_tmpdir):
        """Load error messages should be user-friendly, not expose raw exceptions (ERR-019)."""
        tmpdir = setup_tmpdir

        # Create save with valid metadata but missing required game state fields
        save_path = os.path.join(tmpdir, "saves", "IncompleteSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        metadata = {
            "version": "3.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        # Game state with missing required fields (will cause KeyError during reconstruction)
        game_state = {
            "turn_number": 1,
            # Missing: config, galaxy, empires
        }
        save_json(os.path.join(save_path, "turns", "turn_1.json"), game_state)

        result, message = SaveGameService.load_game(save_path)

        assert result is None
        # Message should be user-friendly, not raw exception
        assert "Save file" in message or "corrupted" in message.lower()
        # Should NOT expose raw Python exception class names in user message
        assert "KeyError" not in message, f"Should not expose KeyError to user: {message}"
        assert "Traceback" not in message, f"Should not expose traceback to user: {message}"

    def test_unexpected_load_error_message_is_user_friendly(self, setup_tmpdir):
        """Unexpected errors during load should have user-friendly messages (ERR-019)."""
        tmpdir = setup_tmpdir

        # Create valid-looking save
        save_path = os.path.join(tmpdir, "saves", "TestSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        metadata = {
            "version": "3.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        game_state = {
            "turn_number": 1,
            "config": GameConfig().to_dict(),
            "galaxy": {"systems": {}, "warp_lanes": [], "radius": 4000},
            "empires": [],
            "human_player_ids": [0]
        }
        save_json(os.path.join(save_path, "turns", "turn_1.json"), game_state)

        # Mock GameSession.from_dict to raise unexpected exception
        # Need to patch at module level since import happens inside function
        with patch('game.strategy.engine.game_session.GameSession.from_dict',
                   side_effect=RuntimeError("Internal processing error")):
            result, message = SaveGameService.load_game(save_path)

        assert result is None
        # Message should be user-friendly
        assert "unexpected error" in message.lower() or "failed" in message.lower() or "corrupted" in message.lower()
        # Should NOT expose raw exception details
        assert "RuntimeError" not in message, f"Should not expose exception type: {message}"
        assert "Internal processing error" not in message, f"Should not expose internal error details: {message}"


class TestSaveGameServicePathResolution:
    """Tests for relative path resolution (TC-006)."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir, saves_dir
        shutil.rmtree(tmpdir)

    def test_load_resolves_relative_path_from_saves_dir(self, setup_tmpdir):
        """TC-006: Passing relative path resolves via SAVES_DIR."""
        tmpdir, saves_dir = setup_tmpdir

        # Create a valid save at SAVES_DIR/my_save
        save_name = "my_save"
        save_path = os.path.join(saves_dir, save_name)
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        # Valid metadata and game state
        metadata = {
            "version": "3.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        game_state = {
            "turn_number": 1,
            "config": GameConfig().to_dict(),
            "galaxy": {"systems": {}, "warp_lanes": [], "radius": 4000},
            "empires": [],
            "human_player_ids": []
        }
        save_json(os.path.join(save_path, "turns", "turn_1.json"), game_state)

        # Load using relative path (just the save name)
        result, message = SaveGameService.load_game(save_name)

        # Should succeed because it resolved "my_save" to SAVES_DIR/my_save
        assert result is not None, f"Expected load to succeed with relative path, got: {message}"


class TestSaveGameServiceHelperErrorHandling:
    """Tests for helper method error handling (TC-007).

    After PROJ-209 Phase 1 decomposition, the redundant outer exception
    handler was removed (DS-010). Each helper now handles its own errors.
    These tests verify the helper methods properly handle all error cases.
    """

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir, saves_dir
        shutil.rmtree(tmpdir)

    def test_load_json_safe_handles_permission_error(self, setup_tmpdir):
        """_load_json_safe returns error tuple for PermissionError."""
        tmpdir, _ = setup_tmpdir
        test_file = os.path.join(tmpdir, "test.json")

        # Mock load_json_required to raise PermissionError
        with patch('game.strategy.systems.save_game_service.load_json_required',
                   side_effect=PermissionError("Permission denied")):
            result, error = SaveGameService._load_json_safe(test_file, "test")

        assert result is None
        assert error is not None
        assert "permission" in error.lower()


class TestSaveGameServiceExceptionHandling:
    """Tests for PROJ-45: Proper exception handling with PersistenceException."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)

    def test_save_permission_denied_returns_clear_message(self, setup_tmpdir):
        """Save permission error should return clear message with path context."""
        session = MockGameSession()

        # Mock os.makedirs to raise PermissionError
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            success, message, save_path = SaveGameService.save_game(session, "TestGame")

        assert not success
        assert "permission" in message.lower() or "save failed" in message.lower()
        assert save_path is None

    def test_save_disk_full_returns_clear_message(self, setup_tmpdir):
        """Save disk full error should return clear message."""
        session = MockGameSession()
        success, _, save_path = SaveGameService.save_game(session, "TestGame")
        session.save_path = save_path

        # Mock save_json to return False (simulating disk full)
        with patch('game.strategy.systems.save_game_service.save_json', return_value=False):
            success, message, result_path = SaveGameService.save_game(session)

        assert not success
        assert "failed" in message.lower()

    def test_load_corrupt_metadata_returns_specific_error(self, setup_tmpdir):
        """Load with corrupt metadata should return specific error message."""
        tmpdir = setup_tmpdir
        save_path = os.path.join(tmpdir, "saves", "CorruptSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        # Write corrupt metadata
        with open(os.path.join(save_path, "save_metadata.json"), "w") as f:
            f.write("{ corrupt json }")

        result, message = SaveGameService.load_game(save_path)

        assert result is None
        assert "corrupted" in message.lower() or "metadata" in message.lower()

    def test_load_corrupt_turn_file_returns_specific_error(self, setup_tmpdir):
        """Load with corrupt turn file should return specific error message."""
        tmpdir = setup_tmpdir
        save_path = os.path.join(tmpdir, "saves", "CorruptTurnSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        # Valid metadata
        metadata = {
            "version": "3.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        # Corrupt turn file
        with open(os.path.join(save_path, "turns", "turn_1.json"), "w") as f:
            f.write("not valid json at all")

        result, message = SaveGameService.load_game(save_path)

        assert result is None
        assert "corrupted" in message.lower() or "turn" in message.lower()

    def test_load_missing_turn_file_returns_specific_error(self, setup_tmpdir):
        """Load with missing turn file should return specific error message."""
        tmpdir = setup_tmpdir
        save_path = os.path.join(tmpdir, "saves", "MissingTurnSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)

        # Valid metadata pointing to turn 5
        metadata = {
            "version": "3.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 5
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        result, message = SaveGameService.load_game(save_path)

        assert result is None
        assert "turn 5" in message.lower() or "not found" in message.lower()

    def test_delete_nonexistent_save_returns_error(self, setup_tmpdir):
        """Delete nonexistent save should return clear error."""
        success, message = SaveGameService.delete_save("NonexistentSave")

        assert not success
        assert "not found" in message.lower()

    def test_delete_permission_denied_returns_clear_message(self, setup_tmpdir):
        """Delete permission error should return clear message."""
        session = MockGameSession()
        success, message, save_path = SaveGameService.save_game(session, "TestGame")
        assert success, f"Save failed: {message}"

        # Mock shutil.rmtree to raise PermissionError
        with patch('shutil.rmtree', side_effect=PermissionError("Access denied")):
            success, message = SaveGameService.delete_save(save_path)

        assert not success
        assert "delete failed" in message.lower() or "access denied" in message.lower()

    def test_list_saves_handles_directory_error_gracefully(self, setup_tmpdir):
        """list_saves should handle directory errors gracefully."""
        # Mock os.listdir to raise error
        with patch('os.listdir', side_effect=PermissionError("Cannot list directory")):
            saves = SaveGameService.list_saves()

        # Should return empty list, not raise
        assert saves == []

    def test_list_turns_handles_directory_error_gracefully(self, setup_tmpdir):
        """list_turns should handle directory errors gracefully."""
        session = MockGameSession()
        success, message, save_path = SaveGameService.save_game(session, "TestGame")
        assert success, f"Save failed: {message}"

        # Mock os.listdir to raise error
        with patch('os.listdir', side_effect=PermissionError("Cannot list directory")):
            turns = SaveGameService.list_turns(save_path)

        # Should return empty list, not raise
        assert turns == []

    def test_get_save_info_returns_none_on_error(self, setup_tmpdir):
        """get_save_info should return None on errors, not raise."""
        # load_json catches exceptions and returns None, so mock it to return None
        # to simulate a read failure (PermissionError, etc.)
        with patch('game.strategy.systems.save_game_service.load_json',
                   return_value=None):
            info = SaveGameService.get_save_info("SomeSave")

        assert info is None

    def test_get_save_info_handles_json_decode_error(self, setup_tmpdir):
        """BUG-4: get_save_info should catch JSONDecodeError, not raise NameError.

        Previously used json.JSONDecodeError but only imported JSONDecodeError
        (bare name), causing NameError when JSONDecodeError was actually raised.
        """
        from json import JSONDecodeError

        with patch('game.strategy.systems.save_game_service.load_json',
                   side_effect=JSONDecodeError("Corrupt", "", 0)):
            info = SaveGameService.get_save_info("CorruptSave")

        assert info is None
