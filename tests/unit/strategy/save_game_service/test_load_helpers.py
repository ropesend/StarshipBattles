"""
Tests for SaveGameService extracted helper methods.

PROJ-209 Phase 1: These tests verify the decomposed helper methods
that were extracted from load_game.
"""
import pytest
import tempfile
import shutil
import os
import json
from unittest.mock import patch, MagicMock

from game.strategy.systems.save_game_service import SaveGameService
from game.strategy.engine.game_config import GameConfig
from game.core.json_utils import save_json
from game.core import paths as paths_module


class TestLoadJsonSafe:
    """Tests for _load_json_safe helper."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        yield
        shutil.rmtree(self.tmpdir)

    def test_success_returns_data(self):
        """Successful load returns (data, None)."""
        test_file = os.path.join(self.tmpdir, "test.json")
        test_data = {"key": "value", "number": 42}
        save_json(test_file, test_data)

        result, error = SaveGameService._load_json_safe(test_file, "test")

        assert error is None
        assert result == test_data

    def test_json_decode_error_returns_error_message(self):
        """Invalid JSON returns (None, error_msg)."""
        test_file = os.path.join(self.tmpdir, "corrupt.json")
        with open(test_file, "w") as f:
            f.write("{ invalid json }")

        result, error = SaveGameService._load_json_safe(test_file, "test data")

        assert result is None
        assert error is not None
        assert "corrupted" in error.lower()
        assert "invalid JSON" in error

    def test_file_not_found_returns_error_message(self):
        """Missing file returns (None, error_msg)."""
        test_file = os.path.join(self.tmpdir, "nonexistent.json")

        result, error = SaveGameService._load_json_safe(test_file, "missing file")

        assert result is None
        assert error is not None
        assert "not found" in error.lower()

    def test_permission_error_returns_error_message(self):
        """Permission denied returns (None, error_msg)."""
        test_file = os.path.join(self.tmpdir, "test.json")

        with patch('game.strategy.systems.save_game_service.load_json_required',
                   side_effect=PermissionError("Access denied")):
            result, error = SaveGameService._load_json_safe(test_file, "protected")

        assert result is None
        assert error is not None
        assert "permission" in error.lower()

    def test_os_error_returns_error_message(self):
        """OS error returns (None, error_msg)."""
        test_file = os.path.join(self.tmpdir, "test.json")

        with patch('game.strategy.systems.save_game_service.load_json_required',
                   side_effect=OSError("Disk error")):
            result, error = SaveGameService._load_json_safe(test_file, "disk data")

        assert result is None
        assert error is not None
        assert "corrupted" in error.lower() or "cannot read" in error.lower()


class TestLoadSaveMetadata:
    """Tests for _load_save_metadata helper."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests and patch Paths.SAVES_DIR."""
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir, saves_dir
        shutil.rmtree(tmpdir)

    def _create_valid_save(self, saves_dir, save_name):
        """Helper to create a valid save structure."""
        save_path = os.path.join(saves_dir, save_name)
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)
        metadata = {
            "version": "2.0.0",
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test",
            "latest_turn_number": 1
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)
        return save_path

    def test_success_returns_metadata_with_resolved_path(self, setup_tmpdir):
        """Successful load returns metadata with _resolved_path."""
        _, saves_dir = setup_tmpdir
        save_path = self._create_valid_save(saves_dir, "TestSave")

        result, error = SaveGameService._load_save_metadata(save_path)

        assert error is None
        assert result is not None
        assert result["version"] == "2.0.0"
        assert result["player_name"] == "Test"
        assert "_resolved_path" in result
        assert result["_resolved_path"] == save_path

    def test_relative_path_resolved(self, setup_tmpdir):
        """Relative path is resolved to absolute using SAVES_DIR."""
        _, saves_dir = setup_tmpdir
        self._create_valid_save(saves_dir, "RelativeSave")

        # Pass just the save name (relative)
        result, error = SaveGameService._load_save_metadata("RelativeSave")

        assert error is None
        assert result is not None
        assert result["_resolved_path"] == os.path.join(saves_dir, "RelativeSave")

    def test_invalid_folder_returns_error(self, setup_tmpdir):
        """Invalid save folder returns error."""
        result, error = SaveGameService._load_save_metadata("NonexistentSave")

        assert result is None
        assert error is not None
        assert "invalid" in error.lower()

    def test_missing_metadata_keys_returns_error(self, setup_tmpdir):
        """Missing required metadata keys returns error."""
        _, saves_dir = setup_tmpdir
        save_path = os.path.join(saves_dir, "IncompleteSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)
        # Metadata missing 'version'
        metadata = {"timestamp": "2026-01-24T12:00:00", "player_name": "Test"}
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        result, error = SaveGameService._load_save_metadata(save_path)

        assert result is None
        assert error is not None
        assert "missing" in error.lower()
        assert "version" in error.lower()

    def test_incompatible_version_returns_error(self, setup_tmpdir):
        """Incompatible save version returns error."""
        _, saves_dir = setup_tmpdir
        save_path = os.path.join(saves_dir, "OldSave")
        os.makedirs(os.path.join(save_path, "turns"), exist_ok=True)
        metadata = {
            "version": "1.0.0",  # Old version
            "timestamp": "2026-01-24T12:00:00",
            "player_name": "Test"
        }
        save_json(os.path.join(save_path, "save_metadata.json"), metadata)

        result, error = SaveGameService._load_save_metadata(save_path)

        assert result is None
        assert error is not None
        assert "version" in error.lower()
        assert "1.0.0" in error


class TestLoadTurnData:
    """Tests for _load_turn_data helper."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "TestSave")
        os.makedirs(os.path.join(self.save_path, "turns"), exist_ok=True)
        yield
        shutil.rmtree(self.tmpdir)

    def _create_turn_file(self, turn_number, game_state=None):
        """Helper to create a turn file."""
        if game_state is None:
            game_state = {
                "turn_number": turn_number,
                "config": {},
                "galaxy": {},
                "empires": []
            }
        turn_file = os.path.join(self.save_path, "turns", f"turn_{turn_number}.json")
        save_json(turn_file, game_state)

    def test_success_returns_game_state(self):
        """Successful load returns (game_state, None)."""
        self._create_turn_file(1)
        metadata = {"latest_turn_number": 1}

        result, error = SaveGameService._load_turn_data(self.save_path, metadata)

        assert error is None
        assert result is not None
        assert result["turn_number"] == 1

    def test_explicit_turn_number_overrides_metadata(self):
        """Explicit turn_number parameter overrides metadata."""
        self._create_turn_file(1)
        self._create_turn_file(5)
        metadata = {"latest_turn_number": 1}

        result, error = SaveGameService._load_turn_data(self.save_path, metadata, turn_number=5)

        assert error is None
        assert result["turn_number"] == 5

    def test_missing_turn_file_returns_error(self):
        """Missing turn file returns error."""
        metadata = {"latest_turn_number": 99}

        result, error = SaveGameService._load_turn_data(self.save_path, metadata)

        assert result is None
        assert error is not None
        assert "turn 99" in error.lower()
        assert "not found" in error.lower()

    def test_corrupt_turn_file_returns_error(self):
        """Corrupt turn file returns error."""
        turn_file = os.path.join(self.save_path, "turns", "turn_1.json")
        with open(turn_file, "w") as f:
            f.write("not valid json")
        metadata = {"latest_turn_number": 1}

        result, error = SaveGameService._load_turn_data(self.save_path, metadata)

        assert result is None
        assert error is not None
        assert "corrupted" in error.lower() or "invalid" in error.lower()

    def test_missing_state_keys_returns_error(self):
        """Missing required game state keys returns error."""
        # Game state missing 'empires'
        game_state = {"turn_number": 1, "config": {}, "galaxy": {}}
        self._create_turn_file(1, game_state)
        metadata = {"latest_turn_number": 1}

        result, error = SaveGameService._load_turn_data(self.save_path, metadata)

        assert result is None
        assert error is not None
        assert "missing" in error.lower()


class TestReconstructGameSession:
    """Tests for _reconstruct_game_session helper."""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for tests."""
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "TestSave")
        os.makedirs(self.save_path, exist_ok=True)
        yield
        shutil.rmtree(self.tmpdir)

    def test_success_returns_game_session_with_save_path(self):
        """Successful reconstruction returns (session, None) with save_path set."""
        game_state = {
            "turn_number": 1,
            "config": GameConfig().to_dict(),
            "galaxy": {"systems": {}, "warp_lanes": [], "radius": 4000},
            "empires": [],
            "human_player_ids": []
        }

        result, error = SaveGameService._reconstruct_game_session(game_state, self.save_path)

        assert error is None
        assert result is not None
        assert result.save_path == self.save_path

    def test_key_error_returns_error_message(self):
        """KeyError during reconstruction returns user-friendly error."""
        with patch('game.strategy.engine.game_session.GameSession.from_dict',
                   side_effect=KeyError("missing_field")):
            result, error = SaveGameService._reconstruct_game_session({}, self.save_path)

        assert result is None
        assert error is not None
        assert "corrupted" in error.lower()
        assert "missing required" in error.lower()
        # Should NOT expose KeyError details
        assert "KeyError" not in error

    def test_validation_exception_returns_error_message(self):
        """ValidationException during reconstruction returns user-friendly error."""
        from game.core.exceptions import ValidationException
        with patch('game.strategy.engine.game_session.GameSession.from_dict',
                   side_effect=ValidationException("Invalid data", code="V001")):
            result, error = SaveGameService._reconstruct_game_session({}, self.save_path)

        assert result is None
        assert error is not None
        assert "corrupted" in error.lower()
        assert "invalid data format" in error.lower()

    def test_runtime_error_returns_error_message(self):
        """RuntimeError during reconstruction returns user-friendly error."""
        with patch('game.strategy.engine.game_session.GameSession.from_dict',
                   side_effect=RuntimeError("Internal error")):
            result, error = SaveGameService._reconstruct_game_session({}, self.save_path)

        assert result is None
        assert error is not None
        assert "corrupted" in error.lower()
        # Should NOT expose internal error details
        assert "Internal error" not in error
