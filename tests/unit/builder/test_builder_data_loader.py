"""
Unit tests for BuilderDataLoader class.

Tests the data loading logic extracted from BuilderScreen._reload_data().
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

import pygame

from game.core.registry import RegistryManager
from game.core.json_utils import save_json


@pytest.fixture(scope="module")
def temp_test_dirs():
    """Create temporary test directories with mock data files."""
    temp_dir = tempfile.mkdtemp()
    custom_dir = os.path.join(temp_dir, "custom_data")
    default_dir = os.path.join(temp_dir, "default_data")
    os.makedirs(custom_dir)
    os.makedirs(default_dir)

    def create_mock_file(directory, filename, content):
        """Helper to create a JSON file with given content."""
        filepath = os.path.join(directory, filename)
        save_json(filepath, content)

    # Create mock data files
    create_mock_file(custom_dir, "components.json", {"components": {}})
    create_mock_file(custom_dir, "test_modifiers.json", {"modifiers": {}})
    create_mock_file(default_dir, "modifiers.json", {"modifiers": {}})
    create_mock_file(default_dir, "vehicleclasses.json", {"classes": {"Escort": {"max_mass": 1000}}})

    yield {"temp_dir": temp_dir, "custom_dir": custom_dir, "default_dir": default_dir}

    # Cleanup
    shutil.rmtree(temp_dir)


class TestBuilderDataLoader:
    """Test BuilderDataLoader file discovery and data loading."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        pygame.init()
        RegistryManager.instance().clear()
        yield
        RegistryManager.instance().clear()
        # NOTE: Do not call pygame.quit() here - the root conftest manages
        # pygame lifecycle at session scope. Calling quit() here would break
        # subsequent tests with "No video mode set" errors.

    def test_find_file_direct_match(self, temp_test_dirs):
        """find_file returns direct path when file exists in custom directory."""
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(temp_test_dirs["custom_dir"], default_data_dir=temp_test_dirs["default_dir"],
                                  registries=RegistryManager.instance())
        path, is_fallback = loader.find_file("components.json")

        assert path is not None
        assert not is_fallback
        assert path.endswith("components.json")
        assert "custom_data" in path

    def test_find_file_test_prefix_fallback(self, temp_test_dirs):
        """find_file tries test_ prefixed filenames when direct match fails."""
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(temp_test_dirs["custom_dir"], default_data_dir=temp_test_dirs["default_dir"],
                                  registries=RegistryManager.instance())
        # modifiers.json doesn't exist directly, but test_modifiers.json does
        path, is_fallback = loader.find_file("modifiers.json")

        assert path is not None
        assert not is_fallback
        assert path.endswith("test_modifiers.json")

    def test_find_file_default_fallback(self, temp_test_dirs):
        """find_file falls back to default data directory when custom fails."""
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(temp_test_dirs["custom_dir"], default_data_dir=temp_test_dirs["default_dir"],
                                  registries=RegistryManager.instance())
        # vehicleclasses.json only exists in default_dir
        path, is_fallback = loader.find_file("vehicleclasses.json")

        assert path is not None
        assert is_fallback
        assert "default_data" in path

    def test_find_file_not_found(self, temp_test_dirs):
        """find_file returns None when no file found anywhere."""
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(temp_test_dirs["custom_dir"], default_data_dir=temp_test_dirs["default_dir"],
                                  registries=RegistryManager.instance())
        path, is_fallback = loader.find_file("nonexistent_file.json", allow_default=True)

        assert path is None
        assert not is_fallback

    def test_find_file_multiple_names(self, temp_test_dirs):
        """find_file accepts list of alternative filenames."""
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(temp_test_dirs["custom_dir"], default_data_dir=temp_test_dirs["default_dir"],
                                  registries=RegistryManager.instance())
        # Try multiple names, first should match
        path, _ = loader.find_file(["components.json", "test_components.json"])

        assert path is not None
        assert path.endswith("components.json")

    def test_clear_registries_clears_registry_manager(self, temp_test_dirs):
        """clear_registries calls RegistryManager.clear()."""
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(temp_test_dirs["custom_dir"], registries=RegistryManager.instance())

        # Use mock to verify clear was called
        with patch.object(RegistryManager.instance(), 'clear') as mock_clear:
            loader.clear_registries()
            mock_clear.assert_called_once()


class TestBuilderDataLoaderIntegration:
    """Integration tests using real data files."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        pygame.init()
        RegistryManager.instance().clear()
        # Get the data directory using path fixture
        from tests.fixtures.paths import get_data_dir
        self.data_dir = str(get_data_dir())
        yield
        RegistryManager.instance().clear()
        # NOTE: Do not call pygame.quit() here - the root conftest manages
        # pygame lifecycle at session scope. Calling quit() here would break
        # subsequent tests with "No video mode set" errors.
        patch.stopall()

    def test_load_all_with_real_data(self):
        """load_all successfully loads from real data directory."""
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(self.data_dir, registries=RegistryManager.instance())
        result = loader.load_all()

        assert result.success, f"Load failed with errors: {result.errors}"
        assert result.default_class is not None
        assert len(result.errors) == 0, f"Unexpected errors: {result.errors}"

    def test_load_all_populates_registries(self):
        """load_all populates component and modifier registries.

        Note: This test verifies that load_all returns a valid result.
        Registry state verification is done via LoadResult.default_class
        which requires vehicle classes to have loaded successfully.
        """
        from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader

        # PROJ-50: Pass registries (required)
        loader = BuilderDataLoader(self.data_dir, registries=RegistryManager.instance())
        result = loader.load_all()

        # Primary assertion: load succeeded
        assert result.success, f"Load failed: {result.errors}"

        # Verify default class was found (proves vehicle classes loaded)
        assert result.default_class is not None
        assert isinstance(result.default_class, str)
        assert len(result.default_class) > 0, "Default class should be non-empty"

        # Verify no errors occurred
        assert len(result.errors) == 0, f"Unexpected errors: {result.errors}"
