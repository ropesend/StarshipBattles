"""Test slider increment behavior.

PROJ-43: Updated to use mock ComponentService instead of patching MODIFIER_REGISTRY.
"""
import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_component_service():
    """Create a mock ComponentService for testing."""
    service = MagicMock()
    mock_registry = {
        'range_mount': MagicMock(
            name='Range Mount',
            type_str='linear',
            min_val=0,
            max_val=3,
            restrictions=None
        )
    }
    service.get_modifier_registry.return_value = mock_registry
    service.is_modifier_allowed.return_value = True
    return service


@pytest.fixture
def pygame_setup():
    """Initialize pygame and pygame_gui for testing."""
    pygame.init()
    pygame.display.set_mode((800, 600))
    manager = pygame_gui.UIManager((800, 600))
    container = pygame_gui.elements.UIPanel(
        pygame.Rect(0, 0, 400, 300),
        manager=manager
    )
    yield manager, container
    pygame.quit()


class TestSliderIncrement:
    def test_range_mount_increment(self, pygame_setup, mock_component_service):
        """Test that the Range Mount slider is initialized with 0.1 increment."""
        from game.ui.screens.builder.modifier_editor import ModifierEditorPanel

        manager, container = pygame_setup
        preset_manager = MagicMock()

        # PROJ-43: Pass mock service via constructor instead of patching global
        panel = ModifierEditorPanel(
            manager, container, 400, preset_manager, None,
            component_service=mock_component_service
        )

        # Setup template modifiers to include range_mount
        template_modifiers = {'range_mount': 0}

        with patch('game.ui.screens.builder.modifier_row.UIHorizontalSlider') as MockSlider:
            # Mock the slider to avoid pygame_gui validation errors
            mock_slider_instance = MagicMock()
            MockSlider.return_value = mock_slider_instance

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
