"""Tests for edge cases: corrupted saves, version compatibility, save management, game continuity."""
import pytest
import os
import json
from unittest.mock import patch

from game.strategy.systems.save_game_service import SaveGameService
from game.core import paths as paths_module


class TestCorruptedSaves:
    """Tests for handling corrupted save files."""

    def test_load_missing_metadata(self, temp_save_folder):
        """Load fails gracefully when metadata is missing."""
        # Create incomplete save folder
        save_path = os.path.join(temp_save_folder, "broken_save")
        os.makedirs(os.path.join(save_path, "turns"))

        # No metadata file

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "Missing save_metadata.json" in message or "Invalid save" in message

    def test_load_missing_turns_folder(self, temp_save_folder):
        """Load fails gracefully when turns folder is missing."""
        # Create incomplete save folder
        save_path = os.path.join(temp_save_folder, "broken_save")
        os.makedirs(save_path)

        # Create metadata but no turns folder
        metadata = {"version": "3.0.0", "timestamp": "2026-01-23", "player_name": "Test"}
        with open(os.path.join(save_path, "save_metadata.json"), 'w') as f:
            json.dump(metadata, f)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "turns folder" in message.lower() or "invalid" in message.lower()

    def test_load_invalid_json_turn_file(self, minimal_game_session, temp_save_folder):
        """Load fails gracefully with corrupted turn JSON."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

        # Corrupt the turn file
        turn_file = os.path.join(save_path, "turns", "turn_1.json")
        with open(turn_file, 'w') as f:
            f.write("{ invalid json }")

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "corrupted" in message.lower() or "cannot read" in message.lower()

    def test_load_missing_required_fields(self, minimal_game_session, temp_save_folder):
        """Load fails gracefully when required fields are missing."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

        # Remove required field from turn file
        turn_file = os.path.join(save_path, "turns", "turn_1.json")
        with open(turn_file, 'r') as f:
            data = json.load(f)
        del data['galaxy']  # Remove required field
        with open(turn_file, 'w') as f:
            json.dump(data, f)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "missing" in message.lower() or "corrupted" in message.lower()

    def test_load_nonexistent_save(self, temp_save_folder):
        """Load fails gracefully for nonexistent save."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game("nonexistent_save")

        assert loaded_session is None
        assert "not found" in message.lower() or "invalid" in message.lower()


class TestVersionCompatibility:
    """Tests for save version handling."""

    def test_current_version_loads(self, minimal_game_session, temp_save_folder):
        """Current version saves load correctly."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, message = SaveGameService.load_game(minimal_game_session.save_path)

        assert loaded_session is not None

    def test_incompatible_version_rejected(self, temp_save_folder):
        """Incompatible versions are rejected."""
        # Create save with incompatible version
        save_path = os.path.join(temp_save_folder, "old_save")
        os.makedirs(os.path.join(save_path, "turns"))

        # Create metadata with unknown version
        metadata = {
            "version": "0.0.1",  # Incompatible version
            "timestamp": "2026-01-23",
            "player_name": "Test",
            "turn_number": 1
        }
        with open(os.path.join(save_path, "save_metadata.json"), 'w') as f:
            json.dump(metadata, f)

        # Create minimal turn file
        turn_data = {
            "turn_number": 1,
            "config": {},
            "galaxy": {},
            "empires": []
        }
        with open(os.path.join(save_path, "turns", "turn_1.json"), 'w') as f:
            json.dump(turn_data, f)

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            loaded_session, message = SaveGameService.load_game(save_path)

        assert loaded_session is None
        assert "incompatible" in message.lower() or "version" in message.lower()

class TestSaveManagement:
    """Tests for save listing and deletion."""

    def test_list_saves(self, minimal_game_session, temp_save_folder):
        """List saves returns saved games."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Create multiple saves
            SaveGameService.save_game(minimal_game_session, save_name="save_1")
            minimal_game_session.save_path = None  # Reset for new save
            SaveGameService.save_game(minimal_game_session, save_name="save_2")

            saves = SaveGameService.list_saves()

        assert len(saves) >= 2
        save_names = [s['save_name'] for s in saves]
        assert "save_1" in save_names
        assert "save_2" in save_names

    def test_list_turns(self, minimal_game_session, temp_save_folder):
        """List turns returns available turn history."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Save multiple turns
            SaveGameService.save_game(minimal_game_session, save_name="test_save")

            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            turns = SaveGameService.list_turns(minimal_game_session.save_path)

        assert len(turns) == 3
        turn_numbers = [t['turn_number'] for t in turns]
        assert 1 in turn_numbers
        assert 2 in turn_numbers
        assert 3 in turn_numbers

    def test_delete_save(self, minimal_game_session, temp_save_folder):
        """Delete save removes save folder."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="to_delete")
            save_path = minimal_game_session.save_path

            assert os.path.exists(save_path)

            success, message = SaveGameService.delete_save(save_path)

        assert success is True
        assert not os.path.exists(save_path)

    def test_delete_nonexistent_save(self, temp_save_folder):
        """Delete nonexistent save fails gracefully."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message = SaveGameService.delete_save("nonexistent")

        assert success is False
        assert "not found" in message.lower()

    def test_get_save_info(self, minimal_game_session, temp_save_folder):
        """Get save info returns metadata."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="info_test")

            info = SaveGameService.get_save_info(minimal_game_session.save_path)

        assert info is not None
        assert info['player_name'] == "TestPlayer"
        assert 'version' in info
        assert 'timestamp' in info


class TestGameContinuity:
    """Tests for continuing gameplay after load."""

    def test_can_process_turn_after_load(self, minimal_game_session, temp_save_folder):
        """Loaded game can process turns."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(minimal_game_session.save_path)

        initial_turn = loaded_session.turn_number

        # Process turn should work
        loaded_session.process_turn()

        assert loaded_session.turn_number == initial_turn + 1

    def test_can_save_after_load(self, minimal_game_session, temp_save_folder):
        """Loaded game can be saved again."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            loaded_session, _ = SaveGameService.load_game(minimal_game_session.save_path)

            loaded_session.process_turn()

            # Save should work
            success, message, _ = SaveGameService.save_game(loaded_session)

        assert success is True

    def test_multiple_save_load_cycles(self, minimal_game_session, temp_save_folder):
        """Multiple save/load cycles preserve state."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Cycle 1
            SaveGameService.save_game(minimal_game_session, save_name="cycle_test")
            session, _ = SaveGameService.load_game(minimal_game_session.save_path)

            # Cycle 2
            session.process_turn()
            SaveGameService.save_game(session)
            session, _ = SaveGameService.load_game(session.save_path)

            # Cycle 3
            session.process_turn()
            SaveGameService.save_game(session)
            session, _ = SaveGameService.load_game(session.save_path)

        # Should be at turn 3
        assert session.turn_number == 3
