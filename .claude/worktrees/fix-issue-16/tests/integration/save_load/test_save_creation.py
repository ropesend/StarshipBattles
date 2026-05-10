"""Tests for save game creation."""
import pytest
import os
import json
from unittest.mock import patch

from game.strategy.systems.save_game_service import SaveGameService
from game.core import paths as paths_module


class TestSaveGameCreation:
    """Tests for creating save games."""

    def test_save_creates_folder_structure(self, minimal_game_session, temp_save_folder):
        """Save creates proper folder structure."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True
        assert save_path is not None
        assert os.path.exists(save_path)

        # Check folder structure
        assert os.path.exists(os.path.join(save_path, "turns"))
        assert os.path.exists(os.path.join(save_path, "designs"))
        assert os.path.exists(os.path.join(save_path, "save_metadata.json"))

    def test_save_creates_turn_file(self, minimal_game_session, temp_save_folder):
        """Save creates turn state file."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True

        # Check turn file exists
        turn_file = os.path.join(save_path, "turns", f"turn_{minimal_game_session.turn_number}.json")
        assert os.path.exists(turn_file)

        # Verify content is valid JSON
        with open(turn_file, 'r') as f:
            data = json.load(f)

        assert 'turn_number' in data
        assert 'config' in data
        assert 'galaxy' in data
        assert 'empires' in data

    def test_save_creates_metadata(self, minimal_game_session, temp_save_folder):
        """Save creates metadata file with correct info."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True

        # Check metadata
        metadata_file = os.path.join(save_path, "save_metadata.json")
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        assert metadata['version'] == SaveGameService.SAVE_VERSION
        assert 'timestamp' in metadata
        assert metadata['player_name'] == "TestPlayer"
        assert metadata['empire_count'] == 2
        assert metadata['turn_number'] == minimal_game_session.turn_number

    def test_save_updates_session_path(self, minimal_game_session, temp_save_folder):
        """Save updates game session's save_path."""
        assert minimal_game_session.save_path is None

        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True
        assert minimal_game_session.save_path == save_path

    def test_save_creates_per_empire_design_folders(self, minimal_game_session, temp_save_folder):
        """Save creates design folder for each empire."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            success, message, save_path = SaveGameService.save_game(
                minimal_game_session,
                save_name="test_save"
            )

        assert success is True

        designs_folder = os.path.join(save_path, "designs")
        for empire in minimal_game_session.empires:
            empire_folder = os.path.join(designs_folder, f"empire_{empire.id}")
            assert os.path.exists(empire_folder)

    def test_save_subsequent_turns(self, minimal_game_session, temp_save_folder):
        """Saving after multiple turns creates multiple turn files."""
        with patch.object(paths_module.Paths, 'SAVES_DIR', temp_save_folder):
            # Save turn 1
            SaveGameService.save_game(minimal_game_session, save_name="test_save")
            save_path = minimal_game_session.save_path

            # Process and save turn 2
            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

            # Process and save turn 3
            minimal_game_session.process_turn()
            SaveGameService.save_game(minimal_game_session)

        # Check all turn files exist
        turns_folder = os.path.join(save_path, "turns")
        assert os.path.exists(os.path.join(turns_folder, "turn_1.json"))
        assert os.path.exists(os.path.join(turns_folder, "turn_2.json"))
        assert os.path.exists(os.path.join(turns_folder, "turn_3.json"))
