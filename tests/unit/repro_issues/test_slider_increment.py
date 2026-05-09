"""Test slider increment behavior in ModifierControlRow.

PROJ-43: Updated to use mock ComponentService instead of patching MODIFIER_REGISTRY.
PROJ-129: Refactored to test ModifierControlRow directly (not legacy ModifierEditorPanel).
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
    """Initialize pygame_gui for testing."""
    pygame.display.set_mode((800, 600))
    manager = pygame_gui.UIManager((800, 600))
    container = pygame_gui.elements.UIPanel(
        pygame.Rect(0, 0, 400, 300),
        manager=manager
    )
    yield manager, container


class TestSliderIncrement:
    def test_range_mount_increment(self, pygame_setup, mock_component_service):
        """Test that the Range Mount slider is initialized with correct increment.

        PROJ-129: Tests ModifierControlRow directly since that's where slider logic resides.
        """
        from game.ui.screens.builder.modifier_row import ModifierControlRow
        from game.ui.screens.builder.modifier_config import MODIFIER_UI_CONFIG, DEFAULT_CONFIG

        manager, container = pygame_setup

        # Get config for range_mount
        config = MODIFIER_UI_CONFIG.get('range_mount', DEFAULT_CONFIG)

        # Mock modifier definition
        mock_mod_def = MagicMock()
        mock_mod_def.name = 'Range Mount'
        mock_mod_def.type_str = 'linear'
        mock_mod_def.min_val = 0
        mock_mod_def.max_val = 3
        mock_mod_def.restrictions = None

        # Create mock component with modifiers
        mock_component = MagicMock()
        mock_component.modifiers = {'range_mount': 1.5}

        with patch('game.ui.screens.builder.modifier_row.UIHorizontalSlider') as MockSlider:
            # Mock the slider to avoid pygame_gui validation errors
            mock_slider_instance = MagicMock()
            MockSlider.return_value = mock_slider_instance

            # Create the row (note: parameter order per ModifierControlRow.__init__)
            # PROJ-388: ModifierControlRow now requires a ModifierLogicService.
            row = ModifierControlRow(
                manager=manager,
                container=container,
                width=380,
                mod_id='range_mount',
                mod_def=mock_mod_def,
                config=config,
                on_change_callback=None,
                modifier_logic=MagicMock(),
            )

            # Build UI to trigger slider creation
            row.build_ui(y=0)

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
