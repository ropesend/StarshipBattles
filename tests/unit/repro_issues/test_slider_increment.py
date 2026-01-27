import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mocked_pygame_modules():
    """Patch pygame modules for isolated testing."""
    with patch.dict('sys.modules', {
        'pygame': MagicMock(),
        'pygame_gui': MagicMock(),
        'pygame_gui.elements': MagicMock(),
        'pygame_gui.core': MagicMock(),
        'pygame_gui.windows': MagicMock()
    }):
        # Import module with mocked dependencies
        import game.ui.screens.builder.legacy_components as builder_components
        yield builder_components


class TestSliderIncrement:
    def test_range_mount_increment(self, mocked_pygame_modules):
        """Test that the Range Mount slider is initialized with 0.1 increment."""
        module = mocked_pygame_modules
        manager = MagicMock()
        container = MagicMock()
        preset_manager = MagicMock()

        # Access class from imported module
        ModifierEditorPanel = module.ModifierEditorPanel

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

        with patch('game.ui.screens.builder.legacy_components.MODIFIER_REGISTRY', mock_registry):
            with patch('game.ui.screens.builder.modifier_row.UIHorizontalSlider') as MockSlider:
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
                        assert click_inc == 0.1, "Click increment should be 0.1"

                        # Assert that range values are Floats (to prevent integer stepping issues)
                        val_range = kwargs.get('value_range', (0, 0))
                        assert isinstance(val_range[0], float), "Range min should be float"
                        assert isinstance(val_range[1], float), "Range max should be float"

                assert found, "Range Mount slider should have been created"
