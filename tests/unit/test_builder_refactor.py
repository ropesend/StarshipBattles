
import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

class TestBuilderRefactor(unittest.TestCase):
    def test_imports(self):
        """Test that builder_gui and extracted modules can be imported."""
        try:
            import game.ui.screens.builder.main as builder_gui
            from game.ui.screens.planet_list_presets import PresetManager
            # PROJ-113: ShipIO moved to UI layer
            import game.ui.services.ship_io as ship_io
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")

    def test_preset_manager(self):
        """Test basic functionality of PresetManager."""
        from game.ui.screens.planet_list_presets import PresetManager
        pm = PresetManager()
        pm.save_preset('Test Preset', {'damage': 10})
        self.assertIn('Test Preset', pm.get_preset_names())
        # Verify we can retrieve the preset
        preset_data = pm.get_preset('Test Preset')
        self.assertEqual(preset_data.get('damage'), 10)

if __name__ == '__main__':
    unittest.main()
