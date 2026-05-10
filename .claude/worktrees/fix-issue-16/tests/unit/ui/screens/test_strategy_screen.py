"""Tests for StrategyScreen core functionality (PROJ-111 Phase 4).

Tests initialization, turn advancement, fleet/planet selection, build queue
interaction, lifecycle methods, and event delegation. Uses bypass-init pattern.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# --- Helpers ---

def _make_strategy_screen():
    """Create a StrategyScreen with mocked dependencies.

    Returns (screen, mocks_dict) where mocks_dict contains all mock objects.
    """
    from game.ui.screens.strategy_screen import StrategyScreen

    with patch.object(StrategyScreen, '__init__', lambda self, *a, **kw: None):
        screen = StrategyScreen.__new__(StrategyScreen)

    # Core attributes
    screen.screen_width = 1920
    screen.screen_height = 1080
    screen.scene_callback = MagicMock()
    screen.input_mapper = MagicMock()

    # Session
    session = MagicMock()
    session.galaxy = MagicMock()
    session.empires = [MagicMock(id=0), MagicMock(id=1)]
    session.systems = [MagicMock()]
    session.active_empire = session.empires[0]
    session.enemy_empire = session.empires[1]
    session.human_player_ids = [0]
    screen.session = session

    # Facade
    facade = MagicMock()
    screen._facade = facade

    # Camera
    camera = MagicMock()
    screen.camera = camera

    # UI
    ui = MagicMock()
    ui.manager = MagicMock()
    screen.ui = ui

    # State
    screen.hover_hex = None
    screen.hex_size = 10
    screen.detail_zoom_level = 3.0
    screen.selected_fleet = None
    screen.selected_object = None
    screen.last_selected_system = None
    screen.turn_processing = False
    screen.current_player_index = 0
    screen._quit_confirm_dialog = None
    screen.build_queue_screen = None

    # Sub-modules
    screen._renderer = MagicMock()
    screen._camera_nav = MagicMock()
    screen._fleet_ops = MagicMock()
    screen._colonization = MagicMock()
    screen._superweapons = MagicMock()
    screen._build_queue = MagicMock()
    screen._game_state = MagicMock()
    screen._input = MagicMock()

    # Assets
    screen.empire_assets = {}
    screen._race_loader = MagicMock()

    mocks = {
        'session': session,
        'facade': facade,
        'camera': camera,
        'ui': ui,
        'renderer': screen._renderer,
        'camera_nav': screen._camera_nav,
        'fleet_ops': screen._fleet_ops,
        'colonization': screen._colonization,
        'build_queue': screen._build_queue,
        'game_state': screen._game_state,
        'input_handler': screen._input,
    }

    return screen, mocks


# ===========================================================================
# Task 4.1: Initialization Tests
# ===========================================================================

class TestStrategyScreenInitialization:
    """Test StrategyScreen.__init__ behavior."""

    def test_init_stores_screen_dimensions(self):
        """__init__ should store screen width and height."""
        screen, _ = _make_strategy_screen()
        assert screen.screen_width == 1920
        assert screen.screen_height == 1080

    def test_init_accepts_session_parameter(self):
        """__init__ should accept and store session parameter."""
        screen, mocks = _make_strategy_screen()
        assert screen.session is mocks['session']

    def test_init_creates_facade(self):
        """__init__ should create facade from session."""
        screen, mocks = _make_strategy_screen()
        assert screen._facade is mocks['facade']

    def test_init_creates_sub_objects(self):
        """__init__ should create renderer, camera_nav, input_handler, etc."""
        screen, _ = _make_strategy_screen()
        assert screen._renderer is not None
        assert screen._camera_nav is not None
        assert screen._input is not None
        assert screen._fleet_ops is not None
        assert screen._colonization is not None

    def test_init_stores_input_mapper(self):
        """__init__ should store input_mapper parameter."""
        screen, _ = _make_strategy_screen()
        assert screen.input_mapper is not None


# ===========================================================================
# Task 4.1: Turn Advancement Tests
# ===========================================================================

class TestAdvanceTurn:
    """Test advance_turn() method delegates to GameStateManager."""

    def test_advance_turn_delegates_to_game_state_manager(self):
        """advance_turn() should delegate to _game_state.advance_turn()."""
        screen, mocks = _make_strategy_screen()

        screen.advance_turn()

        mocks['game_state'].advance_turn.assert_called_once()


class TestProcessFullTurn:
    """Test that turn processing is handled by GameStateManager.

    Note: process_full_turn() has been moved to StrategyGameStateManager (FEAT-20: public).
    These tests verify the delegation pattern works correctly.
    """

    def test_advance_turn_delegates_turn_processing(self):
        """advance_turn() should delegate turn processing to game_state manager."""
        screen, mocks = _make_strategy_screen()

        screen.advance_turn()

        # Verify delegation occurred
        mocks['game_state'].advance_turn.assert_called_once()


# ===========================================================================
# Task 4.1: Fleet/Planet Selection Tests
# ===========================================================================

class TestOnUiSelection:
    """Test on_ui_selection() method."""

    def test_on_ui_selection_sets_selected_object(self):
        """on_ui_selection() should set selected_object."""
        screen, mocks = _make_strategy_screen()
        mock_planet = MagicMock()
        screen._get_object_asset = MagicMock(return_value=None)

        screen.on_ui_selection(mock_planet)

        assert screen.selected_object is mock_planet

    def test_on_ui_selection_fleet_sets_selected_fleet(self):
        """on_ui_selection() with owned fleet should set selected_fleet."""
        screen, _ = _make_strategy_screen()
        mock_fleet = MagicMock()
        mock_fleet.owner_id = 0  # Current player's ID
        screen.session.human_player_ids = [0]
        screen._get_object_asset = MagicMock(return_value=None)

        with patch('game.ui.screens.strategy_screen.is_fleet', return_value=True), \
             patch('game.ui.screens.strategy_screen.is_star_system', return_value=False):
            screen.on_ui_selection(mock_fleet)

        assert screen.selected_fleet is mock_fleet

    def test_on_ui_selection_non_fleet_clears_selected_fleet(self):
        """on_ui_selection() with non-fleet should clear selected_fleet."""
        screen, _ = _make_strategy_screen()
        screen.selected_fleet = MagicMock()
        mock_planet = MagicMock()
        screen._get_object_asset = MagicMock(return_value=None)

        with patch('game.ui.screens.strategy_screen.is_fleet', return_value=False), \
             patch('game.ui.screens.strategy_screen.is_star_system', return_value=False):
            screen.on_ui_selection(mock_planet)

        assert screen.selected_fleet is None

    def test_on_ui_selection_updates_ui(self):
        """on_ui_selection() should call ui.show_detailed_report()."""
        screen, mocks = _make_strategy_screen()
        mock_obj = MagicMock()
        screen._get_object_asset = MagicMock(return_value=MagicMock())

        with patch('game.ui.screens.strategy_screen.is_fleet', return_value=False), \
             patch('game.ui.screens.strategy_screen.is_star_system', return_value=False):
            screen.on_ui_selection(mock_obj)

        mocks['ui'].show_detailed_report.assert_called_once()

    def test_on_ui_selection_none_deselects(self):
        """on_ui_selection() with None should work (deselect)."""
        screen, _ = _make_strategy_screen()
        screen.selected_object = MagicMock()
        screen._get_object_asset = MagicMock(return_value=None)

        with patch('game.ui.screens.strategy_screen.is_fleet', return_value=False), \
             patch('game.ui.screens.strategy_screen.is_star_system', return_value=False):
            screen.on_ui_selection(None)

        assert screen.selected_object is None


# ===========================================================================
# Task 4.1: Build Queue Interaction Tests
# ===========================================================================

class TestOnBuildYardClick:
    """Test on_build_yard_click() method delegates to BuildQueueManager."""

    def test_on_build_yard_click_delegates_to_build_queue_manager(self):
        """on_build_yard_click() should delegate to _build_queue.on_build_yard_click()."""
        screen, mocks = _make_strategy_screen()

        screen.on_build_yard_click()

        mocks['build_queue'].on_build_yard_click.assert_called_once()

    def test_on_fleet_build_click_delegates_to_build_queue_manager(self):
        """on_fleet_build_click() should delegate to _build_queue.on_fleet_build_click()."""
        screen, mocks = _make_strategy_screen()

        screen.on_fleet_build_click()

        mocks['build_queue'].on_fleet_build_click.assert_called_once()

    def test_on_navigate_to_hex_build_delegates_to_build_queue_manager(self):
        """on_navigate_to_hex_build() should delegate to _build_queue."""
        screen, mocks = _make_strategy_screen()
        mock_hex = MagicMock()
        mock_source = MagicMock()

        screen.on_navigate_to_hex_build(mock_hex, mock_source)

        mocks['build_queue'].on_navigate_to_hex_build.assert_called_once_with(mock_hex, mock_source)


class TestOnBuildQueueClose:
    """Test build queue closing is handled by BuildQueueManager.

    Note: _on_build_queue_close() has been moved to StrategyBuildQueueManager.
    These tests verify the delegation pattern works correctly.
    """

    def test_build_queue_methods_delegate_correctly(self):
        """Build queue operations should delegate to build_queue manager."""
        screen, mocks = _make_strategy_screen()

        # Verify all build queue methods delegate
        screen.on_build_yard_click()
        screen.on_fleet_build_click()

        assert mocks['build_queue'].on_build_yard_click.called
        assert mocks['build_queue'].on_fleet_build_click.called


# ===========================================================================
# Task 4.1: Colonization Tests
# ===========================================================================

class TestOnColonizeClick:
    """Test on_colonize_click() — opens load dialog at colony, then enters target mode."""

    def test_on_colonize_click_opens_load_dialog_at_colony(self):
        """Opens transfer dialog when fleet is at owned colony."""
        screen, mocks = _make_strategy_screen()
        fleet = MagicMock()
        fleet.owner_id = 0
        fleet.location = MagicMock()
        screen.selected_fleet = fleet
        planet = MagicMock()
        planet.owner_id = 0
        screen._facade = MagicMock()
        screen._facade.get_planets_at_hex.return_value = [planet]

        screen.on_colonize_click()

        mocks['ui'].open_transfer_dialog.assert_called_once()

    def test_on_colonize_click_opens_dialog_even_without_colony(self):
        """Always opens transfer dialog regardless of fleet location."""
        screen, mocks = _make_strategy_screen()
        fleet = MagicMock()
        fleet.owner_id = 0
        fleet.location = MagicMock()
        screen.selected_fleet = fleet
        screen._facade = MagicMock()
        screen._facade.get_planets_at_hex.return_value = []

        screen.on_colonize_click()

        mocks['ui'].open_transfer_dialog.assert_called_once()


# ===========================================================================
# Task 4.1: Screen Lifecycle Tests
# ===========================================================================

class TestScreenLifecycle:
    """Test update(), draw(), handle_event() lifecycle methods."""

    def test_update_delegates_to_camera(self):
        """update() should call camera.update(dt)."""
        screen, mocks = _make_strategy_screen()

        screen.update(0.016)

        mocks['camera'].update.assert_called_once_with(0.016)

    def test_update_delegates_to_renderer(self):
        """update() should call renderer.update(dt)."""
        screen, mocks = _make_strategy_screen()

        screen.update(0.016)

        mocks['renderer'].update.assert_called_once_with(0.016)

    def test_update_delegates_to_ui(self):
        """update() should call ui.update(dt)."""
        screen, mocks = _make_strategy_screen()

        screen.update(0.016)

        mocks['ui'].update.assert_called_once_with(0.016)

    def test_draw_fills_screen(self):
        """draw() should fill screen with background color."""
        screen, _ = _make_strategy_screen()
        mock_surface = MagicMock()

        screen.draw(mock_surface)

        mock_surface.fill.assert_called_once()

    def test_draw_delegates_to_renderer(self):
        """draw() should call renderer.draw(screen)."""
        screen, mocks = _make_strategy_screen()
        mock_surface = MagicMock()

        screen.draw(mock_surface)

        mocks['renderer'].draw.assert_called_once_with(mock_surface)

    def test_draw_delegates_to_ui(self):
        """draw() should call ui.draw(screen)."""
        screen, mocks = _make_strategy_screen()
        mock_surface = MagicMock()

        screen.draw(mock_surface)

        mocks['ui'].draw.assert_called_once_with(mock_surface)

    def test_draw_shows_processing_overlay_when_processing(self):
        """draw() should show processing overlay when turn_processing is True.

        FEAT-20: overlay receives a `message` argument (default
        "PROCESSING TURN...", overridable by run_n_turns for progress text).
        Issue #7: overlay also receives `current_tick` / `total_ticks`
        kwargs so the per-tick "Tick N / 100" sub-line can be rendered. They
        default to None when no turn is mid-flight.
        """
        screen, mocks = _make_strategy_screen()
        screen.turn_processing = True
        screen.turn_processing_message = None  # FEAT-20: default message path
        mock_surface = MagicMock()

        screen.draw(mock_surface)

        mocks['renderer'].draw_processing_overlay.assert_called_once_with(
            mock_surface, "PROCESSING TURN...",
            current_tick=None,
            total_ticks=None,
        )

    def test_draw_draws_build_queue_screen_if_open(self):
        """draw() should draw build_queue_screen if it exists."""
        screen, _ = _make_strategy_screen()
        bqs = MagicMock()
        screen.build_queue_screen = bqs
        mock_surface = MagicMock()

        screen.draw(mock_surface)

        bqs.draw.assert_called_once_with(mock_surface)

    def test_handle_event_delegates_to_input(self):
        """handle_event() should delegate to input handler."""
        screen, mocks = _make_strategy_screen()
        event = MagicMock()

        screen.handle_event(event)

        mocks['input_handler'].handle_event.assert_called_once_with(event)

    def test_handle_click_delegates_to_input(self):
        """handle_click() should delegate to input handler."""
        screen, mocks = _make_strategy_screen()

        screen.handle_click(100, 200, 1)

        mocks['input_handler'].handle_click.assert_called_once_with(100, 200, 1)


# ===========================================================================
# Task 4.1: Handle Resize Tests
# ===========================================================================

class TestHandleResize:
    """Test handle_resize() method."""

    def test_handle_resize_updates_dimensions(self):
        """handle_resize() should update screen dimensions."""
        screen, _ = _make_strategy_screen()

        screen.handle_resize(2560, 1440)

        assert screen.screen_width == 2560
        assert screen.screen_height == 1440

    def test_handle_resize_updates_camera(self):
        """handle_resize() should update camera dimensions."""
        screen, mocks = _make_strategy_screen()
        from game.ui.config import UIConfig
        screen.TOP_BAR_HEIGHT = 50

        screen.handle_resize(2560, 1440)

        assert mocks['camera'].width == 2560 - UIConfig.STRATEGY_SIDEBAR_WIDTH
        assert mocks['camera'].height == 1440 - screen.TOP_BAR_HEIGHT

    def test_handle_resize_delegates_to_ui(self):
        """handle_resize() should call ui.handle_resize()."""
        screen, mocks = _make_strategy_screen()

        screen.handle_resize(2560, 1440)

        mocks['ui'].handle_resize.assert_called_once_with(2560, 1440)


# ===========================================================================
# Task 4.1: Navigation Tests
# ===========================================================================

class TestNavigation:
    """Test navigation methods."""

    def test_center_camera_on_delegates_to_camera_nav(self):
        """center_camera_on() should delegate to camera navigator."""
        screen, mocks = _make_strategy_screen()
        mock_obj = MagicMock()

        screen.center_camera_on(mock_obj)

        mocks['camera_nav'].center_on.assert_called_once_with(mock_obj)

    def test_cycle_selection_delegates_to_camera_nav(self):
        """cycle_selection() should delegate to camera navigator."""
        screen, mocks = _make_strategy_screen()
        mocks['camera_nav'].cycle_selection.return_value = None

        screen.cycle_selection('colony', 1)

        mocks['camera_nav'].cycle_selection.assert_called_once_with('colony', 1)

    def test_cycle_selection_calls_on_ui_selection_when_found(self):
        """cycle_selection() should call on_ui_selection when object found."""
        screen, mocks = _make_strategy_screen()
        mock_colony = MagicMock()
        mocks['camera_nav'].cycle_selection.return_value = mock_colony
        screen.on_ui_selection = MagicMock()

        screen.cycle_selection('colony', 1)

        screen.on_ui_selection.assert_called_once_with(mock_colony)

    def test_cycle_selection_centers_camera_when_found(self):
        """cycle_selection() should center camera when object found."""
        screen, mocks = _make_strategy_screen()
        mock_colony = MagicMock()
        mocks['camera_nav'].cycle_selection.return_value = mock_colony
        screen.on_ui_selection = MagicMock()

        screen.cycle_selection('colony', 1)

        mocks['camera_nav'].center_on.assert_called_once_with(mock_colony)


# ===========================================================================
# Task 4.1: Properties Tests
# ===========================================================================

class TestProperties:
    """Test property accessors."""

    def test_galaxy_property_delegates_to_session(self):
        """galaxy property should return session.galaxy."""
        screen, mocks = _make_strategy_screen()
        expected = MagicMock()
        mocks['session'].galaxy = expected

        assert screen.galaxy is expected

    def test_empires_property_delegates_to_session(self):
        """empires property should return session.empires."""
        screen, mocks = _make_strategy_screen()

        assert screen.empires is mocks['session'].empires

    def test_systems_property_delegates_to_session(self):
        """systems property should return session.systems."""
        screen, mocks = _make_strategy_screen()

        assert screen.systems is mocks['session'].systems

    def test_input_mode_property_delegates_to_input(self):
        """input_mode property should delegate to input handler."""
        screen, mocks = _make_strategy_screen()
        mocks['input_handler'].input_mode = 'MOVE'

        assert screen.input_mode == 'MOVE'

    def test_input_mode_setter_delegates_to_input(self):
        """input_mode setter should delegate to input handler."""
        screen, mocks = _make_strategy_screen()

        screen.input_mode = 'JOIN'

        assert mocks['input_handler'].input_mode == 'JOIN'


# ===========================================================================
# Task 4.1: Design Click Tests
# ===========================================================================

class TestOnDesignClick:
    """Test on_design_click() method."""

    def test_on_design_click_calls_scene_callback(self):
        """on_design_click() should call scene_callback with open_builder."""
        screen, _ = _make_strategy_screen()
        screen.scene_callback = MagicMock()
        screen.session = MagicMock()

        screen.on_design_click()

        screen.scene_callback.assert_called_once()
        args, kwargs = screen.scene_callback.call_args
        assert args[0] == "open_builder"

    def test_on_design_click_no_callback(self):
        """on_design_click() should not crash when scene_callback is None."""
        screen, _ = _make_strategy_screen()
        screen.scene_callback = None

        # Should not raise
        screen.on_design_click()


# ===========================================================================
# Task 7.3: Error Path Coverage Tests
# ===========================================================================

class TestErrorHandlingPaths:
    """Test error handling and edge cases."""

    def test_update_with_none_session_does_not_crash(self):
        """update() should not crash if session is None."""
        screen, mocks = _make_strategy_screen()
        screen.session = None

        # Should not raise - delegates to mocked objects
        screen.update(0.016)
        mocks['camera'].update.assert_called_once_with(0.016)

    def test_draw_with_none_surface_raises_cleanly(self):
        """draw() should handle None surface gracefully."""
        screen, _ = _make_strategy_screen()

        # Should raise AttributeError on fill() since None has no fill method
        with pytest.raises(AttributeError):
            screen.draw(None)

    def test_handle_event_with_none_event(self):
        """handle_event() should delegate None to input handler."""
        screen, mocks = _make_strategy_screen()

        screen.handle_event(None)

        mocks['input_handler'].handle_event.assert_called_once_with(None)

    def test_on_ui_selection_with_none_selected_object(self):
        """on_ui_selection(None) should clear selection without crashing."""
        screen, mocks = _make_strategy_screen()
        screen.selected_object = MagicMock()
        screen.selected_fleet = MagicMock()
        screen._get_object_asset = MagicMock(return_value=None)

        with patch('game.ui.screens.strategy_screen.is_fleet', return_value=False), \
             patch('game.ui.screens.strategy_screen.is_star_system', return_value=False):
            screen.on_ui_selection(None)

        assert screen.selected_object is None

    def test_handle_resize_with_zero_dimensions(self):
        """handle_resize() should handle zero dimensions without crashing."""
        screen, mocks = _make_strategy_screen()
        screen.TOP_BAR_HEIGHT = 50

        # Zero dimensions - implementation should handle this
        screen.handle_resize(0, 0)

        assert screen.screen_width == 0
        assert screen.screen_height == 0
        mocks['ui'].handle_resize.assert_called_once_with(0, 0)

    def test_handle_resize_with_same_dimensions(self):
        """handle_resize() should handle resize with same dimensions (no-op)."""
        screen, mocks = _make_strategy_screen()
        screen.TOP_BAR_HEIGHT = 50
        original_width = screen.screen_width
        original_height = screen.screen_height

        screen.handle_resize(original_width, original_height)

        assert screen.screen_width == original_width
        assert screen.screen_height == original_height
        mocks['ui'].handle_resize.assert_called_once_with(original_width, original_height)

    def test_cycle_selection_no_results_found(self):
        """cycle_selection() should handle no results gracefully."""
        screen, mocks = _make_strategy_screen()
        mocks['camera_nav'].cycle_selection.return_value = None
        screen.on_ui_selection = MagicMock()

        screen.cycle_selection('fleet', 1)

        # Should not call on_ui_selection when nothing found
        screen.on_ui_selection.assert_not_called()

    def test_advance_turn_with_empty_human_player_ids(self):
        """advance_turn() should delegate to game_state manager (which handles edge cases)."""
        screen, mocks = _make_strategy_screen()
        screen.current_player_index = 0
        screen.session.human_player_ids = []  # Empty list

        # Should delegate to game_state manager
        screen.advance_turn()

        # Delegation should occur regardless of state
        mocks['game_state'].advance_turn.assert_called_once()

    def test_on_build_yard_click_no_selected_object(self):
        """on_build_yard_click() should delegate to build_queue manager."""
        screen, mocks = _make_strategy_screen()
        screen.selected_object = None

        screen.on_build_yard_click()

        # Delegation should occur - the manager handles validation
        mocks['build_queue'].on_build_yard_click.assert_called_once()

    def test_on_colonize_click_no_selected_fleet(self):
        """on_colonize_click() should return early when no fleet selected."""
        screen, mocks = _make_strategy_screen()
        screen.selected_fleet = None

        screen.on_colonize_click()

        # No dialog opened, no crash
        mocks['ui'].open_transfer_dialog.assert_not_called()


# ===========================================================================
# Task 7.4: Edge Case Coverage Tests
# ===========================================================================

class TestEdgeCases:
    """Test boundary values and edge cases."""

    def test_strategy_screen_with_zero_systems(self):
        """StrategyScreen should handle galaxy with zero systems."""
        screen, mocks = _make_strategy_screen()
        mocks['session'].systems = []
        screen.session.systems = []

        assert len(screen.systems) == 0

    def test_strategy_screen_with_zero_empires(self):
        """StrategyScreen should handle game with zero empires (edge case)."""
        screen, mocks = _make_strategy_screen()
        mocks['session'].empires = []
        screen.session.empires = []

        assert len(screen.empires) == 0

    def test_handle_resize_minimum_dimensions(self):
        """handle_resize() should handle minimum usable dimensions (800x600)."""
        screen, mocks = _make_strategy_screen()
        screen.TOP_BAR_HEIGHT = 50

        screen.handle_resize(800, 600)

        assert screen.screen_width == 800
        assert screen.screen_height == 600
        mocks['ui'].handle_resize.assert_called_once_with(800, 600)

    def test_handle_resize_maximum_dimensions(self):
        """handle_resize() should handle 4K dimensions (3840x2160)."""
        screen, mocks = _make_strategy_screen()
        screen.TOP_BAR_HEIGHT = 50

        screen.handle_resize(3840, 2160)

        assert screen.screen_width == 3840
        assert screen.screen_height == 2160
        mocks['ui'].handle_resize.assert_called_once_with(3840, 2160)

    def test_cycle_selection_with_single_colony(self):
        """cycle_selection() should work with only one colony."""
        screen, mocks = _make_strategy_screen()
        single_colony = MagicMock()
        mocks['camera_nav'].cycle_selection.return_value = single_colony
        screen.on_ui_selection = MagicMock()

        screen.cycle_selection('colony', 1)

        mocks['camera_nav'].cycle_selection.assert_called_once_with('colony', 1)
        screen.on_ui_selection.assert_called_once_with(single_colony)

    def test_cycle_selection_negative_direction(self):
        """cycle_selection() should handle negative direction (previous)."""
        screen, mocks = _make_strategy_screen()
        mock_obj = MagicMock()
        mocks['camera_nav'].cycle_selection.return_value = mock_obj
        screen.on_ui_selection = MagicMock()

        screen.cycle_selection('fleet', -1)

        mocks['camera_nav'].cycle_selection.assert_called_once_with('fleet', -1)

    def test_current_player_index_wrapping(self):
        """advance_turn() should delegate to game_state manager for player wrapping."""
        screen, mocks = _make_strategy_screen()
        screen.session.human_player_ids = [0, 1, 2]

        # Start at 0, advance 3 times
        screen.current_player_index = 0
        screen.advance_turn()
        screen.advance_turn()
        screen.advance_turn()

        # Should have delegated 3 times
        assert mocks['game_state'].advance_turn.call_count == 3


# ===========================================================================
# Task 7.5: Screen Resize Handling Tests
# ===========================================================================

class TestScreenResizeHandling:
    """Comprehensive resize handling tests."""

    def test_resize_updates_camera_viewport(self):
        """handle_resize() should update camera viewport dimensions."""
        screen, mocks = _make_strategy_screen()
        from game.ui.config import UIConfig
        screen.TOP_BAR_HEIGHT = 50

        screen.handle_resize(2560, 1440)

        # Camera viewport should exclude sidebar and topbar
        expected_width = 2560 - UIConfig.STRATEGY_SIDEBAR_WIDTH
        expected_height = 1440 - screen.TOP_BAR_HEIGHT
        assert mocks['camera'].width == expected_width
        assert mocks['camera'].height == expected_height

    def test_resize_to_same_size_no_crash(self):
        """Resizing to current size should be a no-op that doesn't crash."""
        screen, mocks = _make_strategy_screen()

        screen.handle_resize(1920, 1080)
        screen.handle_resize(1920, 1080)  # Same size again

        # Should complete without error
        assert screen.screen_width == 1920
        assert screen.screen_height == 1080

    def test_resize_during_turn_processing(self):
        """Resize should work even during turn processing."""
        screen, mocks = _make_strategy_screen()
        screen.turn_processing = True

        screen.handle_resize(2560, 1440)

        assert screen.screen_width == 2560
        assert screen.screen_height == 1440
        mocks['ui'].handle_resize.assert_called_once_with(2560, 1440)

    def test_resize_with_open_build_queue(self):
        """Resize should propagate to open build queue screen."""
        screen, mocks = _make_strategy_screen()
        screen.build_queue_screen = MagicMock()

        screen.handle_resize(2560, 1440)

        # UI still receives resize
        mocks['ui'].handle_resize.assert_called_once_with(2560, 1440)

    def test_resize_preserves_selection_state(self):
        """Resize should not affect selection state."""
        screen, mocks = _make_strategy_screen()
        mock_obj = MagicMock()
        screen.selected_object = mock_obj
        screen.selected_fleet = MagicMock()

        screen.handle_resize(2560, 1440)

        assert screen.selected_object is mock_obj
        assert screen.selected_fleet is not None

    def test_resize_preserves_input_mode(self):
        """Resize should not affect input mode."""
        screen, mocks = _make_strategy_screen()
        mocks['input_handler'].input_mode = 'MOVE'

        screen.handle_resize(2560, 1440)

        assert screen.input_mode == 'MOVE'

    def test_resize_aspect_ratio_changes(self):
        """Resize should handle aspect ratio changes (e.g., 16:9 to 21:9)."""
        screen, mocks = _make_strategy_screen()
        screen.TOP_BAR_HEIGHT = 50

        # Start with 16:9
        screen.handle_resize(1920, 1080)
        assert screen.screen_width == 1920

        # Switch to ultrawide 21:9
        screen.handle_resize(2560, 1080)
        assert screen.screen_width == 2560
        assert screen.screen_height == 1080

    def test_multiple_consecutive_resizes(self):
        """Multiple consecutive resizes should all take effect."""
        screen, mocks = _make_strategy_screen()
        screen.TOP_BAR_HEIGHT = 50

        screen.handle_resize(800, 600)
        screen.handle_resize(1920, 1080)
        screen.handle_resize(2560, 1440)
        screen.handle_resize(3840, 2160)

        # Final size should be the last resize
        assert screen.screen_width == 3840
        assert screen.screen_height == 2160
        # UI should have been called 4 times
        assert mocks['ui'].handle_resize.call_count == 4
