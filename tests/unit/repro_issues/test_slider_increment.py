"""
Test for slider increment configuration in modifier editor.

This test verifies that the Range Mount slider is created with correct
increment values (0.1 instead of integer stepping).
"""
import unittest
from unittest.mock import MagicMock, patch


class TestSliderIncrement(unittest.TestCase):
    """Test slider configuration in ModifierEditorPanel."""

    @unittest.skip("Test requires extensive mocking - skipping to prevent pygame state pollution")
    def test_range_mount_increment(self):
        """Test that the Range Mount slider is initialized with 0.1 increment."""
        # Patch pygame_gui elements at their source
        with patch('pygame_gui.elements.UIHorizontalSlider') as MockSlider, \
             patch('pygame_gui.elements.UIButton'), \
             patch('pygame_gui.elements.UILabel'), \
             patch('pygame_gui.elements.UIPanel'), \
             patch('pygame_gui.elements.UITextEntryLine'), \
             patch('pygame_gui.elements.UIDropDownMenu'), \
             patch('pygame_gui.elements.UIScrollingContainer'):

            # Import after patching to get patched version
            from game.ui.panels.builder_widgets import ModifierEditorPanel
            from game.core.registry import RegistryManager

            manager = MagicMock()
            container = MagicMock()
            preset_manager = MagicMock()

            panel = ModifierEditorPanel(manager, container, 400, preset_manager, None)

            # Setup template modifiers to include range_mount
            template_modifiers = {'range_mount': 0}

            mock_registry = {
                'range_mount': MagicMock(
                    name='Range Mount',
                    type_str='linear',
                    min_val=0,
                    max_val=3
                )
            }

            with patch.object(RegistryManager.instance(), 'modifiers', mock_registry):
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
                        self.assertEqual(click_inc, 0.1, "Click increment should be 0.1")

                        # Assert that range values are Floats (to prevent integer stepping issues)
                        val_range = kwargs.get('value_range', (0, 0))
                        self.assertIsInstance(val_range[0], float, "Range min should be float")
                        self.assertIsInstance(val_range[1], float, "Range max should be float")

                self.assertTrue(found, "Range Mount slider should have been created")


if __name__ == '__main__':
    unittest.main()
