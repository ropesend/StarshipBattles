import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
import os

# Dummy video driver
os.environ["SDL_VIDEODRIVER"] = "dummy"

from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.core.registry import RegistryManager
from game.simulation.entities.layer_data import LayerData


@pytest.fixture
def builder_warning_setup():
    pygame.init()

    # IMPORTANT: Patch DesignWorkshopScreen._create_ui since that's the real implementation
    patcher = patch('game.ui.screens.workshop_screen.DesignWorkshopScreen._create_ui')
    mock_create_ui = patcher.start()

    # Mock internal managers in both builder_screen and workshop_screen modules
    p1 = patch('game.ui.screens.workshop_screen.SpriteManager')
    p2 = patch('game.ui.screens.workshop_screen.ShipThemeManager')
    p3 = patch('game.ui.screens.workshop_screen.UIConfirmationDialog')
    p4 = patch('game.ui.screens.workshop_event_router.UIConfirmationDialog')
    p1.start()
    p2.start()
    p3.start()
    p4.start()

    context = WorkshopContext.standalone(tech_preset_name="default")
    context.on_return = MagicMock()
    builder = DesignWorkshopScreen(800, 600, context)

    # Manually setup the mocks that _create_ui would have created
    builder.ui_manager = MagicMock()
    builder.left_panel = MagicMock()
    builder.right_panel = MagicMock()
    builder.right_panel.class_dropdown = MagicMock()
    builder.right_panel.vehicle_type_dropdown = MagicMock()
    builder.layer_panel = MagicMock()
    builder.modifier_panel = MagicMock()
    builder.weapons_report_panel = MagicMock()
    builder.detail_panel = MagicMock()

    builder.left_panel.get_add_count.return_value = 1
    builder.left_panel.handle_event.return_value = None
    builder.layer_panel.handle_event.return_value = None
    builder.modifier_panel.handle_event.return_value = None
    builder.weapons_report_panel.handle_event.return_value = None

    # Reset pending action
    builder.pending_action = None
    builder.confirm_dialog = None

    yield builder

    patcher.stop()
    p1.stop()
    p2.stop()
    p3.stop()
    p4.stop()

    pygame.quit()
    RegistryManager.instance().clear()


class TestBuilderWarningLogic:
    def test_change_class_empty_ship(self, builder_warning_setup):
        """Test changing class with no components triggers immediate action (no warning)."""
        builder = builder_warning_setup
        # Ensure ship is empty
        builder.ship.layers = {'CORE': LayerData()}

        # Setup event
        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = builder.right_panel.class_dropdown
        event.text = "Cruiser"

        # Mock _execute_pending_action to verify it's called
        with patch.object(builder, 'execute_pending_action') as mock_execute:
            builder.handle_event(event)

            # Check success
            assert builder.pending_action == ('change_class', "Cruiser")
            mock_execute.assert_called_once()
            assert builder.confirm_dialog is None

    def test_change_class_non_empty_ship(self, builder_warning_setup):
        """Test changing class WITH components triggers warning dialog."""
        builder = builder_warning_setup
        # Add a dummy component
        builder.ship.layers = {'CORE': LayerData(components=['mock_comp'])}

        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = builder.right_panel.class_dropdown
        event.text = "Cruiser"

        with patch.object(builder, 'execute_pending_action') as mock_execute:
            builder.handle_event(event)

            # Check warning
            assert builder.pending_action == ('change_class', "Cruiser")
            mock_execute.assert_not_called()
            assert builder.confirm_dialog is not None

    def test_change_type_empty_ship(self, builder_warning_setup):
        """Test changing type with no components triggers immediate action."""
        builder = builder_warning_setup
        builder.ship.layers = {'CORE': LayerData()}

        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = builder.right_panel.vehicle_type_dropdown
        event.text = "Station"

        # Mock getattr for checking current type
        from game.core.registry import RegistryManager
        with patch.object(RegistryManager.instance(), 'vehicle_classes', {'Station': {'type': 'Station', 'max_mass': 5000}}):
            with patch.object(builder, 'execute_pending_action') as mock_execute:
                builder.handle_event(event)

                # Should find a pending action and execute it
                assert builder.pending_action is not None
                assert builder.pending_action[0] == 'change_type'
                mock_execute.assert_called_once()
                assert builder.confirm_dialog is None

    def test_change_type_non_empty_ship(self, builder_warning_setup):
        """Test changing type WITH components triggers warning."""
        builder = builder_warning_setup
        builder.ship.layers = {'CORE': LayerData(components=['mock_comp'])}

        event = MagicMock()
        event.type = pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        event.ui_element = builder.right_panel.vehicle_type_dropdown
        event.text = "Station"

        from game.core.registry import RegistryManager
        with patch.object(RegistryManager.instance(), 'vehicle_classes', {'Station': {'type': 'Station', 'max_mass': 5000}}):
            with patch.object(builder, 'execute_pending_action') as mock_execute:
                builder.handle_event(event)

                assert builder.pending_action is not None
                mock_execute.assert_not_called()
                assert builder.confirm_dialog is not None
