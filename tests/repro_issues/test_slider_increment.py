import unittest
from unittest.mock import MagicMock, patch
import sys

import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock pygame and pygame_gui
sys.modules['pygame'] = MagicMock()
sys.modules['pygame_gui'] = MagicMock()
sys.modules['pygame_gui.elements'] = MagicMock()

from builder_components import ModifierEditorPanel

class TestSliderIncrement(unittest.TestCase):
    def test_range_mount_increment(self):
        """Test that the Range Mount slider is initialized with 0.1 increment."""
        manager = MagicMock()
        container = MagicMock()
        preset_manager = MagicMock()
        
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
        
        with patch('builder_components.MODIFIER_REGISTRY', mock_registry):
            with patch('builder_components.UIHorizontalSlider') as MockSlider:
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
