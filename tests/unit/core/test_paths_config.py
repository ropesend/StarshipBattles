"""
Unit tests for game/core/paths.py

Tests path constants and pathlib accessors.
"""
import os
from pathlib import Path
import pytest

from game.core.paths import Paths


class TestPathConstants:
    """Tests for path constants."""

    def test_root_dir_exists(self):
        """Paths.ROOT_DIR is a real directory."""
        assert os.path.isdir(Paths.ROOT_DIR)

    def test_data_dir_exists(self):
        """Paths.DATA_DIR is a real directory."""
        assert os.path.isdir(Paths.DATA_DIR)

    def test_asset_dir_exists(self):
        """Paths.ASSET_DIR is a real directory."""
        assert os.path.isdir(Paths.ASSET_DIR)

    def test_game_dir_exists(self):
        """Paths.GAME_DIR is a real directory."""
        assert os.path.isdir(Paths.GAME_DIR)

    def test_data_dir_is_under_root(self):
        """DATA_DIR starts with ROOT_DIR."""
        assert Paths.DATA_DIR.startswith(Paths.ROOT_DIR)

    def test_core_data_files_defined(self):
        """COMPONENTS_FILE, MODIFIERS_FILE etc. are non-empty strings."""
        assert isinstance(Paths.COMPONENTS_FILE, str)
        assert len(Paths.COMPONENTS_FILE) > 0

        assert isinstance(Paths.MODIFIERS_FILE, str)
        assert len(Paths.MODIFIERS_FILE) > 0

        assert isinstance(Paths.RESOURCES_FILE, str)
        assert len(Paths.RESOURCES_FILE) > 0

    def test_components_file_exists(self):
        """Paths.COMPONENTS_FILE is a real file."""
        assert os.path.isfile(Paths.COMPONENTS_FILE)

    def test_modifiers_file_exists(self):
        """Paths.MODIFIERS_FILE is a real file."""
        assert os.path.isfile(Paths.MODIFIERS_FILE)

    def test_vehicle_classes_file_exists(self):
        """Paths.VEHICLE_CLASSES_FILE is a real file."""
        assert os.path.isfile(Paths.VEHICLE_CLASSES_FILE)


class TestPathlibAccessors:
    """Tests for pathlib.Path accessor methods."""

    def test_get_root_returns_path(self):
        """get_root() returns pathlib.Path."""
        result = Paths.get_root()
        assert isinstance(result, Path)
        assert result.is_dir()

    def test_get_data_dir_returns_path(self):
        """get_data_dir() returns pathlib.Path under root."""
        result = Paths.get_data_dir()
        assert isinstance(result, Path)
        assert result.is_dir()
        # Should be under root
        assert str(result).startswith(str(Paths.get_root()))

    def test_get_assets_dir_returns_path(self):
        """get_assets_dir() returns pathlib.Path."""
        result = Paths.get_assets_dir()
        assert isinstance(result, Path)
        assert result.is_dir()

    def test_get_output_dir_returns_path(self):
        """get_output_dir() returns pathlib.Path."""
        result = Paths.get_output_dir()
        assert isinstance(result, Path)
        # Output dir might not exist yet, but accessor should return valid path
        assert str(result).endswith("output")

    def test_get_saves_dir_returns_path(self):
        """get_saves_dir() returns pathlib.Path."""
        result = Paths.get_saves_dir()
        assert isinstance(result, Path)
        assert "saves" in str(result)

    def test_get_logs_dir_returns_path(self):
        """get_logs_dir() returns pathlib.Path."""
        result = Paths.get_logs_dir()
        assert isinstance(result, Path)
        assert "logs" in str(result)


class TestPathConsistency:
    """Tests for consistency between string paths and pathlib accessors."""

    def test_root_dir_matches_get_root(self):
        """ROOT_DIR and get_root() point to same location."""
        assert Paths.ROOT_DIR == str(Paths.get_root())

    def test_data_dir_matches_get_data_dir(self):
        """DATA_DIR and get_data_dir() point to same location."""
        assert Paths.DATA_DIR == str(Paths.get_data_dir())

    def test_asset_dir_matches_get_assets_dir(self):
        """ASSET_DIR and get_assets_dir() point to same location."""
        assert Paths.ASSET_DIR == str(Paths.get_assets_dir())
