import unittest
import os

class TestBuilderRefactor(unittest.TestCase):
    def test_imports(self):
        """Test that builder_gui and extracted modules can be imported."""
        try:
            from game.ui.screens import builder_screen
            from game.simulation import preset_manager
            from game.simulation.systems import persistence as ship_io
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")

    def test_preset_manager(self):
        """Test basic functionality of PresetManager."""
        from game.simulation.preset_manager import PresetManager
        pm = PresetManager('test_presets.json')
        pm.add_preset('Test Preset', {'damage': 10})
        self.assertIn('Test Preset', pm.get_all_presets())
        pm.delete_preset('Test Preset')
        self.assertNotIn('Test Preset', pm.get_all_presets())
        
        # Cleanup
        if os.path.exists('test_presets.json'):
            os.remove('test_presets.json')

if __name__ == '__main__':
    unittest.main()
