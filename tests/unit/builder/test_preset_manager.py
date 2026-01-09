"""Tests for the PresetManager class."""
import unittest
import os
import json
import tempfile
import shutil
from game.simulation.preset_manager import PresetManager

class TestPresetManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_presets.json')
        
    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_init_creates_empty_presets_if_file_missing(self):
        """Test that manager initializes empty if file doesn't exist."""
        manager = PresetManager(self.test_file)
        self.assertEqual(manager.presets, {})

    def test_save_and_load_presets(self):
        """Test saving presets to disk and loading them back."""
        manager = PresetManager(self.test_file)
        manager.add_preset("Test Preset", {"modifier": 1})
        
        # Verify it was added in memory
        self.assertEqual(manager.get_preset("Test Preset"), {"modifier": 1})
        
        # Create a new manager instance to verify loading from disk
        manager2 = PresetManager(self.test_file)
        self.assertEqual(manager2.get_preset("Test Preset"), {"modifier": 1})

    def test_add_preset_updates_existing(self):
        """Test that adding a preset with existing name updates it."""
        manager = PresetManager(self.test_file)
        manager.add_preset("Update Me", {"val": 1})
        manager.add_preset("Update Me", {"val": 2})
        
        self.assertEqual(manager.get_preset("Update Me"), {"val": 2})

    def test_delete_preset(self):
        """Test deleting a preset."""
        manager = PresetManager(self.test_file)
        manager.add_preset("Delete Me", {})
        
        result = manager.delete_preset("Delete Me")
        self.assertTrue(result)
        self.assertIsNone(manager.get_preset("Delete Me"))
        
        # Verify it's gone from disk too
        manager2 = PresetManager(self.test_file)
        self.assertIsNone(manager2.get_preset("Delete Me"))

    def test_delete_nonexistent_preset(self):
        """Test deleting a preset that doesn't exist returns False."""
        manager = PresetManager(self.test_file)
        result = manager.delete_preset("Nonexistent")
        self.assertFalse(result)

    def test_get_all_presets(self):
        """Test retrieving all presets."""
        manager = PresetManager(self.test_file)
        manager.add_preset("P1", {})
        manager.add_preset("P2", {})
        
        all_presets = manager.get_all_presets()
        self.assertEqual(len(all_presets), 2)
        self.assertIn("P1", all_presets)
        self.assertIn("P2", all_presets)

if __name__ == '__main__':
    unittest.main()
