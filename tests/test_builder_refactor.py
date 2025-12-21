
import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBuilderRefactor(unittest.TestCase):
    def test_imports(self):
        """Test that builder_gui and extracted modules can be imported."""
        try:
            import builder_gui
            import preset_manager
            import ship_io
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")

    def test_preset_manager(self):
        """Test basic functionality of PresetManager."""
        from preset_manager import PresetManager
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
