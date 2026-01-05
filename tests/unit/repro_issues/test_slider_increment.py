import unittest
from unittest.mock import MagicMock, patch
import sys

import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestSliderIncrement(unittest.TestCase):
    def setUp(self):
        # 1. Start patching sys.modules
        self.modules_patcher = patch.dict(sys.modules, {
            'pygame': MagicMock(),
            'pygame_gui': MagicMock(),
            'pygame_gui.elements': MagicMock(),
            'pygame_gui.core': MagicMock(),
            'pygame_gui.windows': MagicMock(),
            'tkinter': MagicMock(),
            'tkinter.filedialog': MagicMock()
        })
        self.modules_patcher.start()
        
        # Ensure patcher is stopped even if import fails
        self.addCleanup(self.modules_patcher.stop)
        
        # 2. Aggressively unload target modules to ensure they reload with patched dependencies
        # We need to unload 'components' because builder_components imports it,
        # and if it was already loaded with real pygame, it might cause issues.
        to_unload = [m for m in sys.modules if m.startswith('ui.') or m.startswith('game.ui.') or m == 'builder_components' or m == 'components']
        for m in to_unload:
            del sys.modules[m]
            
        def cleanup_modules():
             to_unload = [m for m in sys.modules if m.startswith('game.ui.') or m == 'components']
             for m in to_unload:
                 del sys.modules[m]
                 
        self.addCleanup(cleanup_modules)
            
        # 3. Import module
        import game.ui.panels.builder_widgets as builder_widgets
        self.module = builder_widgets

    def test_range_mount_increment(self):
        """Test that the Range Mount slider is initialized with 0.1 increment."""
        manager = MagicMock()
        container = MagicMock()
        preset_manager = MagicMock()
        
        # Access class from imported module
        ModifierEditorPanel = self.module.ModifierEditorPanel
        
        panel = ModifierEditorPanel(manager, container, 400, preset_manager, None)
        
        # Setup template modifiers to include range_mount
        template_modifiers = {'range_mount': 0}
        
        # We also need to make sure MODIFIER_REGISTRY has range_mount
        # We can mock it or use the real one. The real one is imported in builder_components
        # but let's patch it to be safe and isolated
        
        mock_registry = {
            'range_mount': MagicMock(
                name='Range Mount',
                type_str='linear',
                min_val=0,
                max_val=3
            )
        }
        
        from game.core.registry import RegistryManager
        with patch.object(RegistryManager.instance(), 'modifiers', mock_registry):
            with patch('ui.builder.modifier_row.UIHorizontalSlider') as MockSlider:
                panel.rebuild(None, template_modifiers)
                panel.layout(0)
                
                # Verify slider creation
                found = False
                for call in MockSlider.call_args_list:
                    kwargs = call.kwargs
                    obj_id = kwargs.get('object_id', '')
                    if 'range_mount' in obj_id:
                        found = True
                        click_inc = kwargs.get('click_increment')
                        print(f"DEBUG: range_mount click_increment: {click_inc}")
                        self.assertEqual(click_inc, 0.1, "Click increment should be 0.1")
                        
                        # Assert that range values are Floats (to prevent integer stepping issues)
                        val_range = kwargs.get('value_range', (0, 0))
                        print(f"DEBUG: range: {val_range}")
                        self.assertIsInstance(val_range[0], float, "Range min should be float")
                        self.assertIsInstance(val_range[1], float, "Range max should be float")
                
                self.assertTrue(found, "Range Mount slider should have been created")

if __name__ == '__main__':
    unittest.main()
