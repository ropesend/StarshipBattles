"""Tests for StrategyInputHandler core functionality (PROJ-111 Phase 4).

Tests input mode transitions, click handling, and edge cases. Extends
existing test_strategy_input_handler_hotkeys.py and test_strategy_input_handler_transfer.py.

Event Testing Pattern Notes:
- KEYDOWN/MOUSEBUTTONDOWN/MOUSEWHEEL: Use real pygame.event.Event() via _keydown() helper
  or direct Event construction. Real events ensure correct attribute structure.
- UI_BUTTON_PRESSED (pygame_gui): MagicMock acceptable since only .type and .ui_element
  are needed, and the handler compares ui_element by identity, not pygame internals.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame

from game.core.input_actions import InputAction
from game.core.hex_math import HexCoord
from game.ui.services.input_mapper import InputMapper
from game.ui.screens.strategy_input_handler import StrategyInputHandler


@pytest.fixture
def mock_scene():
    """Create a mock StrategyScreen for handler tests."""
    scene = MagicMock()
    scene.ui = MagicMock()
    scene.ui.manager = MagicMock()
    scene.ui.window_manager = MagicMock()  # PROJ-198: planet_list_window moved here
    scene.ui.window_manager.planet_list_window = None
    scene.ui.handle_click = MagicMock(return_value=False)
    scene.ui._has_modal_open = MagicMock(return_value=False)
    scene.selected_fleet = None
    scene.build_queue_screen = None
    scene._camera_nav = MagicMock()
    scene._fleet_ops = MagicMock()
    scene._colonization = MagicMock()
    scene._superweapons = MagicMock()
    scene.camera = MagicMock()
    scene.camera.zoom = 1.0  # PROJ-162: Fix for _resolve_click_target() comparison
    scene._get_system_at_hex = MagicMock(return_value=None)  # PROJ-162: Skip planet hit-testing
    scene.hex_size = 10
    scene.screen_width = 1920
    scene.TOP_BAR_HEIGHT = 50
    scene.empires = []
    return scene


@pytest.fixture
def mapper():
    """Create an InputMapper loaded with defaults."""
    m = InputMapper()
    from game.core.paths import Paths
    m.load(Paths.DEFAULT_KEYBINDINGS_FILE)
    return m


def _keydown(key, mod=0):
    """Helper: create a pygame KEYDOWN event."""
    return pygame.event.Event(pygame.KEYDOWN, {'key': key, 'mod': mod})


# ===========================================================================
# Input Mode Transitions
# ===========================================================================

class TestInputModeTransitions:
    """Test input mode state machine."""

    def test_all_input_modes_exist(self, mock_scene, mapper):
        """Handler should support all documented input modes."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)

        # Test entering each mode with a fleet selected
        mock_scene.selected_fleet = MagicMock()

        handler.input_mode = 'NORMAL'  # Old name, now SELECT
        handler.input_mode = 'SELECT'
        handler.input_mode = 'MOVE'
        handler.input_mode = 'JOIN'
        handler.input_mode = 'TRANSFER'
        handler.input_mode = 'COLONIZE_TARGET'
        handler.input_mode = 'IMPLODE_PLANET_TARGET'
        handler.input_mode = 'STELLERATE_STAR_TARGET'
        handler.input_mode = 'OPEN_WARP_TARGET'
        handler.input_mode = 'CLOSE_WARP_TARGET'
        handler.input_mode = 'DYSON_SPHERE_TARGET'
        handler.input_mode = 'DROP_CARGO'
        handler.input_mode = 'LOAD_CARGO'

    def test_mode_transition_guards_no_fleet(self, mock_scene, mapper):
        """Cannot enter MOVE without fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None

        handler.handle_event(_keydown(pygame.K_m))

        assert handler.input_mode == 'SELECT'

    def test_mode_transition_guards_join_no_fleet(self, mock_scene, mapper):
        """Cannot enter JOIN without fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None

        handler.handle_event(_keydown(pygame.K_j))

        assert handler.input_mode == 'SELECT'

    def test_mode_transition_guards_colonize_no_fleet(self, mock_scene, mapper):
        """Cannot enter COLONIZE_TARGET without fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None

        handler.handle_event(_keydown(pygame.K_c))

        assert handler.input_mode == 'SELECT'

    def test_entering_new_mode_from_move(self, mock_scene, mapper):
        """Entering a new mode should work from MOVE mode."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        handler.input_mode = 'MOVE'

        handler.handle_event(_keydown(pygame.K_j))

        assert handler.input_mode == 'JOIN'

    def test_escape_returns_to_select_from_move(self, mock_scene, mapper):
        """ESC should return to SELECT from MOVE mode."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'

        handler.handle_event(_keydown(pygame.K_ESCAPE))

        assert handler.input_mode == 'SELECT'

    def test_escape_returns_to_select_from_join(self, mock_scene, mapper):
        """ESC should return to SELECT from JOIN mode."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'JOIN'

        handler.handle_event(_keydown(pygame.K_ESCAPE))

        assert handler.input_mode == 'SELECT'

    def test_escape_returns_to_select_from_colonize(self, mock_scene, mapper):
        """ESC should return to SELECT from COLONIZE_TARGET mode."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'COLONIZE_TARGET'

        handler.handle_event(_keydown(pygame.K_ESCAPE))

        assert handler.input_mode == 'SELECT'

    def test_escape_returns_to_select_from_transfer(self, mock_scene, mapper):
        """ESC should return to SELECT from TRANSFER mode."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'TRANSFER'

        handler.handle_event(_keydown(pygame.K_ESCAPE))

        assert handler.input_mode == 'SELECT'


# ===========================================================================
# Click Handling
# ===========================================================================

class TestClickHandling:
    """Test handle_click() method."""

    def test_click_delegates_to_ui_first(self, mock_scene, mapper):
        """Click should check UI for handling first."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.ui.handle_click.return_value = True  # UI consumed click

        result = handler.handle_click(100, 200, 1)

        mock_scene.ui.handle_click.assert_called_once_with(100, 200, 1)
        assert result is True

    def test_click_in_select_mode_calls_picking(self, mock_scene, mapper):
        """Left-click in SELECT mode should trigger picking."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'SELECT'
        handler._click_dispatch._handle_picking = MagicMock()

        handler.handle_click(100, 200, 1)

        handler._click_dispatch._handle_picking.assert_called_once_with(100, 200)

    def test_click_in_move_mode_dispatches_move(self, mock_scene, mapper):
        """Left-click in MOVE mode should dispatch move command."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._fleet_ops.handle_move_designation.return_value = None

        handler.handle_click(100, 200, 1)

        mock_scene._fleet_ops.handle_move_designation.assert_called_once()

    def test_move_mode_error_returns_to_select(self, mock_scene, mapper):
        """BUG-93: Move error should exit MOVE mode to SELECT."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'error', 'message': 'Unreachable'
        }

        handler.handle_click(100, 200, 1)

        assert handler.input_mode == 'SELECT'

    def test_move_mode_error_building_returns_to_select(self, mock_scene, mapper):
        """BUG-93: Move error (building) should exit MOVE mode to SELECT."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'error', 'message': 'Fleet is building'
        }

        handler.handle_click(100, 200, 1)

        assert handler.input_mode == 'SELECT'

    def test_move_mode_success_returns_to_select(self, mock_scene, mapper):
        """Successful move should exit MOVE mode to SELECT (via finish_move_action)."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'
        fleet = MagicMock()
        mock_scene.selected_fleet = fleet
        mock_scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'success', 'fleet': fleet
        }

        handler.handle_click(100, 200, 1)

        # finish_move_action resets mode to SELECT (unless shift held)
        assert handler.input_mode == 'SELECT'
        mock_scene.on_ui_selection.assert_called_once_with(fleet)

    def test_right_click_in_move_mode_cancels(self, mock_scene, mapper):
        """Right-click in MOVE mode should cancel and return to SELECT."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'

        handler.handle_click(100, 200, 3)  # Right click

        assert handler.input_mode == 'SELECT'

    def test_right_click_in_join_mode_cancels(self, mock_scene, mapper):
        """Right-click in JOIN mode should cancel."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'JOIN'

        handler.handle_click(100, 200, 3)

        assert handler.input_mode == 'SELECT'

    def test_right_click_in_colonize_mode_cancels(self, mock_scene, mapper):
        """Right-click in COLONIZE_TARGET mode should cancel."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'COLONIZE_TARGET'

        handler.handle_click(100, 200, 3)

        assert handler.input_mode == 'SELECT'

    def test_click_in_colonize_mode_dispatches_colonize(self, mock_scene, mapper):
        """Left-click in COLONIZE_TARGET mode should dispatch colonize."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'COLONIZE_TARGET'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._colonization.handle_colonize_designation.return_value = None

        handler.handle_click(100, 200, 1)

        mock_scene._colonization.handle_colonize_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'  # Auto-returns to SELECT


class TestTransferModeClick:
    """Test TRANSFER mode click handling."""

    def test_click_in_transfer_mode_opens_dialog(self, mock_scene, mapper):
        """Left-click in TRANSFER mode should open transfer dialog."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'TRANSFER'
        mock_scene.selected_fleet = MagicMock()
        mock_scene.camera.screen_to_world.return_value = MagicMock(x=100, y=200)

        handler.handle_click(100, 200, 1)

        mock_scene.ui.open_transfer_dialog.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_right_click_in_transfer_mode_cancels(self, mock_scene, mapper):
        """Right-click in TRANSFER mode should cancel."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'TRANSFER'

        handler.handle_click(100, 200, 3)

        assert handler.input_mode == 'SELECT'


class TestCargoModeClicks:
    """Test DROP_CARGO and LOAD_CARGO mode clicks."""

    def test_click_in_drop_cargo_mode_opens_dialog(self, mock_scene, mapper):
        """Left-click in DROP_CARGO mode should open cargo quick dialog."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'DROP_CARGO'
        mock_scene.selected_fleet = MagicMock()
        mock_scene.camera.screen_to_world.return_value = MagicMock(x=100, y=200)

        handler.handle_click(100, 200, 1)

        mock_scene.ui.open_cargo_quick_dialog.assert_called_once()
        # Verify 'unload' mode
        call_args = mock_scene.ui.open_cargo_quick_dialog.call_args
        assert call_args[0][2] == 'unload'
        assert handler.input_mode == 'SELECT'

    def test_click_in_load_cargo_mode_opens_dialog(self, mock_scene, mapper):
        """Left-click in LOAD_CARGO mode should open cargo quick dialog."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'LOAD_CARGO'
        mock_scene.selected_fleet = MagicMock()
        mock_scene.camera.screen_to_world.return_value = MagicMock(x=100, y=200)

        handler.handle_click(100, 200, 1)

        mock_scene.ui.open_cargo_quick_dialog.assert_called_once()
        # Verify 'load' mode
        call_args = mock_scene.ui.open_cargo_quick_dialog.call_args
        assert call_args[0][2] == 'load'
        assert handler.input_mode == 'SELECT'


# ===========================================================================
# Superweapon Mode Clicks
# ===========================================================================

class TestSuperweaponModeClicks:
    """Test superweapon targeting mode click handling."""

    def test_click_in_implode_planet_mode(self, mock_scene, mapper):
        """Left-click in IMPLODE_PLANET_TARGET mode should dispatch."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'IMPLODE_PLANET_TARGET'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._superweapons.handle_implode_planet_designation.return_value = True

        handler.handle_click(100, 200, 1)

        mock_scene._superweapons.handle_implode_planet_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_click_in_stellerate_star_mode(self, mock_scene, mapper):
        """Left-click in STELLERATE_STAR_TARGET mode should dispatch."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'STELLERATE_STAR_TARGET'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._superweapons.handle_stellerate_star_designation.return_value = True

        handler.handle_click(100, 200, 1)

        mock_scene._superweapons.handle_stellerate_star_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_click_in_open_warp_mode(self, mock_scene, mapper):
        """Left-click in OPEN_WARP_TARGET mode should dispatch."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'OPEN_WARP_TARGET'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._superweapons.handle_open_warp_designation.return_value = True

        handler.handle_click(100, 200, 1)

        mock_scene._superweapons.handle_open_warp_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_click_in_close_warp_mode(self, mock_scene, mapper):
        """Left-click in CLOSE_WARP_TARGET mode should dispatch."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'CLOSE_WARP_TARGET'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._superweapons.handle_close_warp_designation.return_value = True

        handler.handle_click(100, 200, 1)

        mock_scene._superweapons.handle_close_warp_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_click_in_dyson_sphere_mode(self, mock_scene, mapper):
        """Left-click in DYSON_SPHERE_TARGET mode should dispatch."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'DYSON_SPHERE_TARGET'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._superweapons.handle_dyson_sphere_designation.return_value = True

        handler.handle_click(100, 200, 1)

        mock_scene._superweapons.handle_dyson_sphere_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'


# ===========================================================================
# Edge Cases
# ===========================================================================

class TestEdgeCases:
    """Test edge case handling."""

    def test_handle_event_ignores_unknown_event_types(self, mock_scene, mapper):
        """Unknown event types should be ignored without error."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)

        # Create an event with unknown type
        event = pygame.event.Event(pygame.USEREVENT + 100, {})

        # Should not raise
        handler.handle_event(event)

    def test_handle_event_with_build_queue_open(self, mock_scene, mapper):
        """Events should route to build queue screen when open."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        bqs = MagicMock()
        mock_scene.build_queue_screen = bqs

        event = _keydown(pygame.K_ESCAPE)
        handler.handle_event(event)

        bqs.handle_event.assert_called_once_with(event)

    def test_handle_event_with_planet_list_open(self, mock_scene, mapper):
        """Events should route to UI when planet list window is open."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        # PROJ-198: planet_list_window is now on window_manager
        mock_scene.ui.window_manager.planet_list_window = MagicMock()

        event = _keydown(pygame.K_F12)
        handler.handle_event(event)

        mock_scene.ui.handle_event.assert_called_once_with(event)

    def test_fleet_requiring_hotkey_ignored_without_fleet(self, mock_scene, mapper):
        """Fleet-requiring hotkeys should be ignored without fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None

        # O opens orders window, requires fleet
        handler.handle_event(_keydown(pygame.K_o))

        mock_scene.ui.open_orders_window.assert_not_called()

    def test_right_click_quick_move_requires_fleet(self, mock_scene, mapper):
        """Right-click quick move in SELECT mode requires fleet."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'SELECT'
        mock_scene.selected_fleet = None

        result = handler.handle_click(100, 200, 3)

        mock_scene._fleet_ops.handle_move_designation.assert_not_called()
        assert result is False

    def test_right_click_quick_move_with_fleet(self, mock_scene, mapper):
        """Right-click quick move in SELECT mode with fleet dispatches move."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'SELECT'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._fleet_ops.handle_move_designation.return_value = None

        result = handler.handle_click(100, 200, 3)

        mock_scene._fleet_ops.handle_move_designation.assert_called_once()


class TestButtonPressHandling:
    """Test UI button press event handling."""

    def test_btn_next_turn_calls_advance_turn(self, mock_scene, mapper):
        """btn_next_turn press should call advance_turn."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        event = MagicMock()
        event.type = 1025  # pygame_gui.UI_BUTTON_PRESSED value
        event.ui_element = mock_scene.ui.btn_next_turn

        handler._handle_button_press(event)

        mock_scene.advance_turn.assert_called_once()

    def test_btn_colonize_calls_on_colonize_click(self, mock_scene, mapper):
        """btn_colonize press should call on_colonize_click."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        event = MagicMock()
        event.ui_element = mock_scene.ui.btn_colonize

        handler._handle_button_press(event)

        mock_scene.on_colonize_click.assert_called_once()

    def test_btn_build_yard_calls_on_build_yard_click(self, mock_scene, mapper):
        """btn_build_yard press should call on_build_yard_click."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        event = MagicMock()
        event.ui_element = mock_scene.ui.btn_build_yard

        handler._handle_button_press(event)

        mock_scene.on_build_yard_click.assert_called_once()

    def test_btn_build_fleet_calls_on_fleet_build_click(self, mock_scene, mapper):
        """btn_build_fleet press should call on_fleet_build_click."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        event = MagicMock()
        event.ui_element = mock_scene.ui.btn_build_fleet

        handler._handle_button_press(event)

        mock_scene.on_fleet_build_click.assert_called_once()

    def test_btn_prev_colony_cycles_selection(self, mock_scene, mapper):
        """btn_prev_colony press should cycle colony selection."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        event = MagicMock()
        event.ui_element = mock_scene.ui.btn_prev_colony

        handler._handle_button_press(event)

        mock_scene.cycle_selection.assert_called_once_with('colony', -1)

    def test_btn_next_colony_cycles_selection(self, mock_scene, mapper):
        """btn_next_colony press should cycle colony selection."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        event = MagicMock()
        event.ui_element = mock_scene.ui.btn_next_colony

        handler._handle_button_press(event)

        mock_scene.cycle_selection.assert_called_once_with('colony', 1)


class TestJoinModeClick:
    """Test JOIN mode click handling."""

    def test_click_in_join_mode_dispatches_join(self, mock_scene, mapper):
        """Left-click in JOIN mode should dispatch join command."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'JOIN'
        mock_scene.selected_fleet = MagicMock()
        mock_scene._fleet_ops.handle_join_designation.return_value = {'type': 'success', 'fleet': MagicMock()}

        handler.handle_click(100, 200, 1)

        mock_scene._fleet_ops.handle_join_designation.assert_called_once()
        assert handler.input_mode == 'SELECT'

    def test_click_in_join_mode_calls_on_ui_selection(self, mock_scene, mapper):
        """Successful join should update selection."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'JOIN'
        mock_scene.selected_fleet = MagicMock()
        result_fleet = MagicMock()
        mock_scene._fleet_ops.handle_join_designation.return_value = {'type': 'success', 'fleet': result_fleet}

        handler.handle_click(100, 200, 1)

        mock_scene.on_ui_selection.assert_called_once_with(result_fleet)


# ===========================================================================
# Zone Selection (PROJ-139)
# ===========================================================================

class TestZoneSelection:
    """Test zone-aware object picking in _handle_picking()."""

    def test_picking_finds_star_via_zone_hex(self, mock_scene, mapper):
        """Clicking a hex in a star's zone should include the star in sector_contents."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)

        # Setup mock galaxy with zone registry
        mock_star = MagicMock()
        mock_star.location = HexCoord(0, 0)
        mock_galaxy = MagicMock()
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[mock_star])
        mock_scene.galaxy = mock_galaxy

        # Setup mock system that doesn't contain the star at clicked hex
        mock_system = MagicMock()
        mock_system.stars = []
        mock_system.planets = []
        mock_system.warp_points = []
        mock_system.global_location = HexCoord(0, 0)
        mock_scene._get_system_at_hex = MagicMock(return_value=mock_system)

        # Setup camera to convert screen to world
        mock_scene.camera.screen_to_world = MagicMock(return_value=MagicMock(x=0, y=0))
        mock_scene.camera.zoom = 1.0  # Low zoom, no hit testing

        # Mock UI methods
        mock_scene.ui.show_system_info = MagicMock()
        mock_scene.ui.show_sector_info = MagicMock()
        mock_scene.ui.show_detailed_report = MagicMock()
        mock_scene.on_ui_selection = MagicMock()

        handler._click_dispatch._handle_picking(100, 200)

        # Verify star was included in sector_contents via zone lookup
        show_sector_call_args = mock_scene.ui.show_sector_info.call_args
        sector_contents = show_sector_call_args[0][1]
        assert mock_star in sector_contents, "Star should be found via zone hex"

    def test_picking_finds_dyson_sphere_via_zone_hex(self, mock_scene, mapper):
        """Clicking a hex in a Dyson Sphere's zone should include it in sector_contents."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)

        # Setup mock Dyson Sphere planet with zone
        mock_dyson = MagicMock()
        mock_dyson.location = HexCoord(0, 0)
        mock_dyson.planet_type = MagicMock()
        mock_dyson.planet_type.name = "DYSON_SPHERE"

        mock_galaxy = MagicMock()
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[mock_dyson])
        mock_scene.galaxy = mock_galaxy

        # Setup mock system
        mock_system = MagicMock()
        mock_system.stars = []
        mock_system.planets = []
        mock_system.warp_points = []
        mock_system.global_location = HexCoord(0, 0)
        mock_scene._get_system_at_hex = MagicMock(return_value=mock_system)

        mock_scene.camera.screen_to_world = MagicMock(return_value=MagicMock(x=0, y=0))
        mock_scene.camera.zoom = 1.0  # Low zoom, no hit testing
        mock_scene.ui.show_system_info = MagicMock()
        mock_scene.ui.show_sector_info = MagicMock()
        mock_scene.ui.show_detailed_report = MagicMock()
        mock_scene.on_ui_selection = MagicMock()

        handler._click_dispatch._handle_picking(100, 200)

        show_sector_call_args = mock_scene.ui.show_sector_info.call_args
        sector_contents = show_sector_call_args[0][1]
        assert mock_dyson in sector_contents, "Dyson Sphere should be found via zone hex"

    def test_picking_priority_fleet_over_zone(self, mock_scene, mapper):
        """Fleets should have priority over zone objects in sector_contents."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)

        # Setup fleet at clicked hex
        mock_fleet = MagicMock()
        mock_fleet.location = HexCoord(0, 0)
        mock_empire = MagicMock()
        mock_empire.fleets = [mock_fleet]
        mock_scene.empires = [mock_empire]

        # Setup zone object at same hex
        mock_star = MagicMock()
        mock_star.location = HexCoord(0, 0)
        mock_galaxy = MagicMock()
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[mock_star])
        mock_scene.galaxy = mock_galaxy

        # No system at this hex
        mock_scene._get_system_at_hex = MagicMock(return_value=None)

        mock_scene.camera.screen_to_world = MagicMock(return_value=MagicMock(x=0, y=0))
        mock_scene.camera.zoom = 1.0  # Low zoom, no hit testing
        mock_scene.ui.show_system_info = MagicMock()
        mock_scene.ui.show_sector_info = MagicMock()
        mock_scene.ui.show_detailed_report = MagicMock()
        mock_scene.on_ui_selection = MagicMock()

        handler._click_dispatch._handle_picking(100, 200)

        show_sector_call_args = mock_scene.ui.show_sector_info.call_args
        sector_contents = show_sector_call_args[0][1]
        assert sector_contents[0] == mock_fleet, "Fleet should be first in sector_contents"
        assert mock_star in sector_contents, "Star should also be in sector_contents"
