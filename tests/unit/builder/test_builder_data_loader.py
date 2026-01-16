"""
Unit tests for BuilderDataLoader class.

Tests the data loading logic extracted from BuilderSceneGUI._reload_data().
"""
import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

import pygame

from game.core.registry import RegistryManager
from game.core.json_utils import save_json


class TestBuilderDataLoader(unittest.TestCase):
    """Test BuilderDataLoader file discovery and data loading."""
    
    @classmethod
    def setUpClass(cls):
        """Create temporary test directories with mock data files."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.custom_dir = os.path.join(cls.temp_dir, "custom_data")
        cls.default_dir = os.path.join(cls.temp_dir, "default_data")
        os.makedirs(cls.custom_dir)
        os.makedirs(cls.default_dir)
        
        # Create mock data files
        cls._create_mock_file(cls.custom_dir, "components.json", {"components": {}})
        cls._create_mock_file(cls.custom_dir, "test_modifiers.json", {"modifiers": {}})
        cls._create_mock_file(cls.default_dir, "modifiers.json", {"modifiers": {}})
        cls._create_mock_file(cls.default_dir, "vehicleclasses.json", {"classes": {"Escort": {"max_mass": 1000}}})
    
    @classmethod
    def _create_mock_file(cls, directory, filename, content):
        """Helper to create a JSON file with given content."""
        filepath = os.path.join(directory, filename)
        save_json(filepath, content)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up temporary directories."""
        shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        pygame.init()
        RegistryManager.instance().clear()

    def tearDown(self):
        RegistryManager.instance().clear()
        # NOTE: Do not call pygame.quit() here - the root conftest manages
        # pygame lifecycle at session scope. Calling quit() here would break
        # subsequent tests with "No video mode set" errors.

    def test_find_file_direct_match(self):
        """find_file returns direct path when file exists in custom directory."""
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.custom_dir, default_data_dir=self.default_dir)
        path, is_fallback = loader.find_file("components.json")
        
        self.assertIsNotNone(path)
        self.assertFalse(is_fallback)
        self.assertTrue(path.endswith("components.json"))
        self.assertIn("custom_data", path)
    
    def test_find_file_test_prefix_fallback(self):
        """find_file tries test_ prefixed filenames when direct match fails."""
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.custom_dir, default_data_dir=self.default_dir)
        # modifiers.json doesn't exist directly, but test_modifiers.json does
        path, is_fallback = loader.find_file("modifiers.json")
        
        self.assertIsNotNone(path)
        self.assertFalse(is_fallback)
        self.assertTrue(path.endswith("test_modifiers.json"))
    
    def test_find_file_default_fallback(self):
        """find_file falls back to default data directory when custom fails."""
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.custom_dir, default_data_dir=self.default_dir)
        # vehicleclasses.json only exists in default_dir
        path, is_fallback = loader.find_file("vehicleclasses.json")
        
        self.assertIsNotNone(path)
        self.assertTrue(is_fallback)
        self.assertIn("default_data", path)
    
    def test_find_file_not_found(self):
        """find_file returns None when no file found anywhere."""
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.custom_dir, default_data_dir=self.default_dir)
        path, is_fallback = loader.find_file("nonexistent_file.json", allow_default=True)
        
        self.assertIsNone(path)
        self.assertFalse(is_fallback)
    
    def test_find_file_multiple_names(self):
        """find_file accepts list of alternative filenames."""
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.custom_dir, default_data_dir=self.default_dir)
        # Try multiple names, first should match
        path, _ = loader.find_file(["components.json", "test_components.json"])
        
        self.assertIsNotNone(path)
        self.assertTrue(path.endswith("components.json"))
    
    def test_clear_registries_clears_registry_manager(self):
        """clear_registries calls RegistryManager.clear()."""
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.custom_dir)
        
        # Use mock to verify clear was called
        with patch.object(RegistryManager.instance(), 'clear') as mock_clear:
            loader.clear_registries()
            mock_clear.assert_called_once()


class TestBuilderDataLoaderIntegration(unittest.TestCase):
    """Integration tests using real data files."""

    def setUp(self):
        pygame.init()
        RegistryManager.instance().clear()
        # Get the data directory using path fixture
        from tests.fixtures.paths import get_data_dir
        self.data_dir = str(get_data_dir())
    
    def tearDown(self):
        RegistryManager.instance().clear()
        # NOTE: Do not call pygame.quit() here - the root conftest manages
        # pygame lifecycle at session scope. Calling quit() here would break
        # subsequent tests with "No video mode set" errors.
        from unittest.mock import patch
        patch.stopall()
    
    def test_load_all_with_real_data(self):
        """load_all successfully loads from real data directory."""
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.data_dir)
        result = loader.load_all()
        
        self.assertTrue(result.success, f"Load failed with errors: {result.errors}")
        self.assertIsNotNone(result.default_class)
        self.assertEqual(len(result.errors), 0, f"Unexpected errors: {result.errors}")
    
    def test_load_all_populates_registries(self):
        """load_all populates component and modifier registries.
        
        Note: This test verifies that load_all returns a valid result.
        Registry state verification is done via LoadResult.default_class
        which requires vehicle classes to have loaded successfully.
        """
        from game.ui.screens.builder_data_loader import BuilderDataLoader
        
        loader = BuilderDataLoader(self.data_dir)
        result = loader.load_all()
        
        # Primary assertion: load succeeded
        self.assertTrue(result.success, f"Load failed: {result.errors}")
        
        # Verify default class was found (proves vehicle classes loaded)
        self.assertIsNotNone(result.default_class)
        self.assertIsInstance(result.default_class, str)
        self.assertGreater(len(result.default_class), 0, "Default class should be non-empty")
        
        # Verify no errors occurred  
        self.assertEqual(len(result.errors), 0, f"Unexpected errors: {result.errors}")


if __name__ == '__main__':
    unittest.main()


