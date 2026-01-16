"""
Tests for path utility fixtures.

These utilities provide consistent path resolution for tests,
eliminating hardcoded paths like "C:\\Dev\\Starship Battles".
"""
import pytest
from pathlib import Path


class TestGetProjectRoot:
    """Tests for get_project_root()."""

    def test_returns_path_object(self):
        """Returns a Path object."""
        from tests.fixtures.paths import get_project_root

        result = get_project_root()
        assert isinstance(result, Path)

    def test_returns_existing_directory(self):
        """Returns a path that exists."""
        from tests.fixtures.paths import get_project_root

        result = get_project_root()
        assert result.exists()
        assert result.is_dir()

    def test_contains_game_directory(self):
        """Project root contains game/ directory."""
        from tests.fixtures.paths import get_project_root

        result = get_project_root()
        assert (result / "game").exists()

    def test_contains_data_directory(self):
        """Project root contains data/ directory."""
        from tests.fixtures.paths import get_project_root

        result = get_project_root()
        assert (result / "data").exists()


class TestGetDataDir:
    """Tests for get_data_dir()."""

    def test_returns_path_object(self):
        """Returns a Path object."""
        from tests.fixtures.paths import get_data_dir

        result = get_data_dir()
        assert isinstance(result, Path)

    def test_returns_existing_directory(self):
        """Returns a path that exists."""
        from tests.fixtures.paths import get_data_dir

        result = get_data_dir()
        assert result.exists()
        assert result.is_dir()

    def test_contains_components_json(self):
        """Data directory contains components.json."""
        from tests.fixtures.paths import get_data_dir

        result = get_data_dir()
        assert (result / "components.json").exists()

    def test_contains_vehicleclasses_json(self):
        """Data directory contains vehicleclasses.json."""
        from tests.fixtures.paths import get_data_dir

        result = get_data_dir()
        assert (result / "vehicleclasses.json").exists()


class TestGetAssetsDir:
    """Tests for get_assets_dir()."""

    def test_returns_path_object(self):
        """Returns a Path object."""
        from tests.fixtures.paths import get_assets_dir

        result = get_assets_dir()
        assert isinstance(result, Path)

    def test_returns_existing_directory(self):
        """Returns a path that exists."""
        from tests.fixtures.paths import get_assets_dir

        result = get_assets_dir()
        assert result.exists()
        assert result.is_dir()


class TestPathFixtures:
    """Tests for pytest fixtures."""

    def test_project_root_fixture(self, project_root):
        """project_root fixture works."""
        assert isinstance(project_root, Path)
        assert project_root.exists()

    def test_data_dir_fixture(self, data_dir):
        """data_dir fixture works."""
        assert isinstance(data_dir, Path)
        assert data_dir.exists()
        assert (data_dir / "components.json").exists()

    def test_assets_dir_fixture(self, assets_dir):
        """assets_dir fixture works."""
        assert isinstance(assets_dir, Path)
        assert assets_dir.exists()
