"""Tests for StrategyInputHandler integration with InputMapper (PROJ-71 Phase 2).

Verifies that the input handler resolves hotkeys via InputMapper instead of
hardcoded pygame key checks, and that new hotkey-triggered button actions work.

Event Testing Pattern Notes:
- KEYDOWN/MOUSEBUTTONDOWN/MOUSEWHEEL: Use real pygame.event.Event() via _keydown() helper
  or direct Event construction. Real events ensure correct attribute structure.
- Tests using _keydown() helper already create real pygame events.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame

from game.core.input_actions import InputAction, KeyBinding
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
    scene.selected_fleet = None
    scene.build_queue_screen = None
    scene._camera_nav = MagicMock()
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


class TestInputHandlerAcceptsMapper:
    """StrategyInputHandler should accept input_mapper parameter."""

    def test_init_with_mapper(self, mock_scene, mapper):
        """Handler stores the mapper when provided."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        assert handler._mapper is mapper

    def test_init_without_mapper(self, mock_scene):
        """Handler works without mapper (backward compat)."""
        handler = StrategyInputHandler(mock_scene)
        assert handler._mapper is None

    def test_init_with_none_mapper(self, mock_scene):
        """Handler works with explicit None mapper."""
        handler = StrategyInputHandler(mock_scene, input_mapper=None)
        assert handler._mapper is None


class TestFleetActionsViaMapper:
    """Fleet-specific hotkeys resolved via InputMapper."""

    def test_m_triggers_move_mode(self, mock_scene, mapper):
        """Pressing M sets input mode to MOVE when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        result = handler.handle_event(_keydown(pygame.K_m))
        assert handler.input_mode == 'MOVE'
        # Verify UI event handling was invoked
        mock_scene.ui.handle_event.assert_called()

    def test_j_triggers_join_mode(self, mock_scene, mapper):
        """Pressing J sets input mode to JOIN when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        result = handler.handle_event(_keydown(pygame.K_j))
        assert handler.input_mode == 'JOIN'
        mock_scene.ui.handle_event.assert_called()

    def test_c_triggers_colonize_mode(self, mock_scene, mapper):
        """Pressing C sets input mode to COLONIZE_TARGET when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        result = handler.handle_event(_keydown(pygame.K_c))
        assert handler.input_mode == 'COLONIZE_TARGET'
        mock_scene.ui.handle_event.assert_called()

    def test_t_sets_transfer_mode(self, mock_scene, mapper):
        """Pressing T sets input mode to TRANSFER when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        result = handler.handle_event(_keydown(pygame.K_t))
        assert handler.input_mode == 'TRANSFER'
        mock_scene.ui.handle_event.assert_called()

    def test_escape_cancels_mode(self, mock_scene, mapper):
        """Pressing ESC resets input mode to SELECT."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'
        result = handler.handle_event(_keydown(pygame.K_ESCAPE))
        assert handler.input_mode == 'SELECT'
        mock_scene.ui.handle_event.assert_called()

    def test_fleet_keys_ignored_without_fleet(self, mock_scene, mapper):
        """Fleet-specific keys should be ignored when no fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        initial_mode = handler.input_mode
        result = handler.handle_event(_keydown(pygame.K_m))
        assert handler.input_mode == 'SELECT'  # Still in SELECT
        assert handler.input_mode == initial_mode  # Mode unchanged

    def test_fleet_keys_ignored_without_fleet_join(self, mock_scene, mapper):
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        initial_mode = handler.input_mode
        result = handler.handle_event(_keydown(pygame.K_j))
        assert handler.input_mode == 'SELECT'
        assert handler.input_mode == initial_mode

    def test_fleet_keys_ignored_without_fleet_colonize(self, mock_scene, mapper):
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        initial_mode = handler.input_mode
        result = handler.handle_event(_keydown(pygame.K_c))
        assert handler.input_mode == 'SELECT'
        assert handler.input_mode == initial_mode


class TestZoomAndScreenshotViaMapper:
    """Zoom and screenshot hotkeys resolved via InputMapper."""

    def test_shift_g_zooms_galaxy(self, mock_scene, mapper):
        """Shift+G triggers galaxy zoom."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_g, pygame.KMOD_SHIFT))
        mock_scene._camera_nav.zoom_to_galaxy.assert_called_once()
        # Verify UI event handling was invoked
        mock_scene.ui.handle_event.assert_called()

    def test_shift_s_zooms_system(self, mock_scene, mapper):
        """Shift+S triggers system zoom."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_s, pygame.KMOD_SHIFT))
        mock_scene._camera_nav.zoom_to_system.assert_called_once()
        mock_scene.ui.handle_event.assert_called()

    @patch('game.ui.screens.strategy_ui_action_router.get_default_screenshot_manager')
    def test_f12_takes_full_screenshot(self, mock_sm_class, mock_scene, mapper):
        """F12 triggers full screenshot via UIActionRouter."""
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_F12))
        mock_sm.capture_strategy_layer.assert_called_once()
        mock_scene.ui.handle_event.assert_called()

    @patch('game.ui.screens.strategy_ui_action_router.get_default_screenshot_manager')
    def test_f11_takes_viewport_screenshot(self, mock_sm_class, mock_scene, mapper):
        """F11 triggers viewport screenshot via UIActionRouter."""
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_F11))
        mock_sm.capture_strategy_layer.assert_called_once()
        mock_scene.ui.handle_event.assert_called()


class TestNewHotkeyButtonActions:
    """New hotkey-triggered button actions (Task 2.5)."""

    def test_enter_triggers_end_turn(self, mock_scene, mapper):
        """Enter key triggers advance_turn."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_RETURN))
        mock_scene.advance_turn.assert_called_once()
        # Verify UI event handling was invoked
        mock_scene.ui.handle_event.assert_called()

    def test_shift_p_opens_planets(self, mock_scene, mapper):
        """Shift+P key opens planet list."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_p, pygame.KMOD_SHIFT))
        mock_scene.ui.open_planet_list.assert_called_once()
        mock_scene.ui.handle_event.assert_called()

    def test_shift_d_opens_design(self, mock_scene, mapper):
        """Shift+D key opens design workshop."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_d, pygame.KMOD_SHIFT))
        mock_scene.on_design_click.assert_called_once()
        mock_scene.ui.handle_event.assert_called()

    def test_shift_b_opens_build_queues(self, mock_scene, mapper):
        """Shift+B key opens build queue list."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_b, pygame.KMOD_SHIFT))
        mock_scene.ui.open_build_queue_list.assert_called_once()
        mock_scene.ui.handle_event.assert_called()

    def test_ctrl_s_saves_game(self, mock_scene, mapper):
        """Ctrl+S saves game."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_s, pygame.KMOD_CTRL))
        mock_scene.on_save_game_click.assert_called_once()
        mock_scene.ui.handle_event.assert_called()

    def test_comma_prev_colony(self, mock_scene, mapper):
        """, key cycles to previous colony."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_COMMA))
        mock_scene.cycle_selection.assert_called_once_with('colony', -1)
        mock_scene.ui.handle_event.assert_called()

    def test_period_next_colony(self, mock_scene, mapper):
        """. key cycles to next colony."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_PERIOD))
        mock_scene.cycle_selection.assert_called_once_with('colony', 1)
        mock_scene.ui.handle_event.assert_called()

    def test_leftbracket_prev_fleet(self, mock_scene, mapper):
        """[ key cycles to previous fleet."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_LEFTBRACKET))
        mock_scene.cycle_selection.assert_called_once_with('fleet', -1)
        mock_scene.ui.handle_event.assert_called()

    def test_rightbracket_next_fleet(self, mock_scene, mapper):
        """] key cycles to next fleet."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        result = handler.handle_event(_keydown(pygame.K_RIGHTBRACKET))
        mock_scene.cycle_selection.assert_called_once_with('fleet', 1)
        mock_scene.ui.handle_event.assert_called()

    def test_o_opens_orders_with_fleet(self, mock_scene, mapper):
        """O key opens fleet orders window when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet
        result = handler.handle_event(_keydown(pygame.K_o))
        mock_scene.ui.open_orders_window.assert_called_once_with(mock_fleet)
        # Verify the correct fleet was passed
        args, _ = mock_scene.ui.open_orders_window.call_args
        assert args[0] is mock_fleet

    def test_o_ignored_without_fleet_or_planet(self, mock_scene, mapper):
        """O key does nothing when no fleet or planet selected (PROJ-238)."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        mock_scene.ui.current_selection = None  # PROJ-238: No planet selected either
        initial_mode = handler.input_mode
        result = handler.handle_event(_keydown(pygame.K_o))
        mock_scene.ui.open_orders_window.assert_not_called()
        assert handler.input_mode == initial_mode  # Mode unchanged

    def test_f_opens_fleet_report_with_fleet(self, mock_scene, mapper):
        """F key opens fleet report when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet
        result = handler.handle_event(_keydown(pygame.K_f))
        mock_scene.ui.open_fleet_report_window.assert_called_once_with(mock_fleet)
        # Verify the correct fleet was passed
        args, _ = mock_scene.ui.open_fleet_report_window.call_args
        assert args[0] is mock_fleet

    def test_f_ignored_without_fleet(self, mock_scene, mapper):
        """F key does nothing when no fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        initial_mode = handler.input_mode
        result = handler.handle_event(_keydown(pygame.K_f))
        mock_scene.ui.open_fleet_report_window.assert_not_called()
        assert handler.input_mode == initial_mode  # Mode unchanged


class TestNoMapperMeansNoKeyboardInput:
    """Without mapper, keyboard input has no effect."""

    def test_no_mapper_no_keyboard_input(self, mock_scene):
        """When mapper is None, keyboard events are not handled."""
        handler = StrategyInputHandler(mock_scene)
        mock_scene.selected_fleet = MagicMock()
        initial_mode = handler.input_mode
        result = handler.handle_event(_keydown(pygame.K_m))
        # Without mapper, mode should remain SELECT (no keyboard handling)
        assert handler.input_mode == 'SELECT'
        assert handler.input_mode == initial_mode  # Mode unchanged
        # UI still receives the event
        mock_scene.ui.handle_event.assert_called()


class TestStrategyScreenPassesMapper:
    """StrategyScreen should pass input_mapper to sub-modules."""

    def test_strategy_screen_accepts_input_mapper_param(self):
        """StrategyScreen.__init__ accepts input_mapper parameter."""
        # Verify the parameter signature exists by inspecting the constructor
        import inspect
        from game.ui.screens.strategy_screen import StrategyScreen
        sig = inspect.signature(StrategyScreen.__init__)
        assert 'input_mapper' in sig.parameters

    def test_strategy_screen_stores_input_mapper(self):
        """StrategyScreen stores input_mapper as attribute."""
        from game.ui.screens.strategy_screen import StrategyScreen
        # Check the class accepts input_mapper
        import inspect
        sig = inspect.signature(StrategyScreen.__init__)
        param = sig.parameters['input_mapper']
        assert param.default is None  # Default should be None


class TestMouseEventHandling:
    """PROJ-88 Phase 5: Mouse events handled through handle_event()."""

    def test_mousebuttondown_calls_handle_click(self, mock_scene, mapper):
        """MOUSEBUTTONDOWN event triggers handle_click via handle_event."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        # Create a mock that tracks calls
        handler.handle_click = MagicMock(return_value=True)

        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 200), 'button': 1})
        result = handler.handle_event(event)

        handler.handle_click.assert_called_once_with(100, 200, 1)
        # Verify coordinates passed correctly
        args, _ = handler.handle_click.call_args
        assert args == (100, 200, 1)

    def test_mousebuttondown_right_click(self, mock_scene, mapper):
        """Right-click MOUSEBUTTONDOWN is forwarded correctly."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_click = MagicMock(return_value=True)

        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (50, 75), 'button': 3})
        result = handler.handle_event(event)

        handler.handle_click.assert_called_once_with(50, 75, 3)
        # Verify button 3 (right click) passed correctly
        args, _ = handler.handle_click.call_args
        assert args[2] == 3

    def test_mousewheel_calls_handle_scroll(self, mock_scene, mapper):
        """MOUSEWHEEL event triggers _handle_scroll via handle_event."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler._handle_scroll = MagicMock()

        event = pygame.event.Event(pygame.MOUSEWHEEL, {'y': 1})
        result = handler.handle_event(event)

        handler._handle_scroll.assert_called_once_with(event)
        # Verify exact event object was passed
        args, _ = handler._handle_scroll.call_args
        assert args[0] is event

    def test_handle_scroll_blocked_over_sidebar(self, mock_scene, mapper):
        """Scroll events over sidebar are blocked."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.screen_width = 1920
        mock_scene.TOP_BAR_HEIGHT = 50
        mock_scene.ui._has_modal_open = MagicMock(return_value=False)
        mock_scene.camera = MagicMock()

        # Simulate mouse over sidebar (far right of screen)
        with patch('pygame.mouse.get_pos', return_value=(1800, 500)):
            event = pygame.event.Event(pygame.MOUSEWHEEL, {'y': 1})
            handler._handle_scroll(event)

        # Camera should NOT receive the scroll event
        mock_scene.camera.update_input.assert_not_called()
        # Verify modal check was made
        mock_scene.ui._has_modal_open.assert_called()

    def test_handle_scroll_blocked_over_topbar(self, mock_scene, mapper):
        """Scroll events over top bar are blocked."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.screen_width = 1920
        mock_scene.TOP_BAR_HEIGHT = 50
        mock_scene.ui._has_modal_open = MagicMock(return_value=False)
        mock_scene.camera = MagicMock()

        # Simulate mouse over top bar
        with patch('pygame.mouse.get_pos', return_value=(500, 25)):
            event = pygame.event.Event(pygame.MOUSEWHEEL, {'y': 1})
            handler._handle_scroll(event)

        # Camera should NOT receive the scroll event
        mock_scene.camera.update_input.assert_not_called()
        # Verify modal check was made
        mock_scene.ui._has_modal_open.assert_called()

    def test_handle_scroll_allowed_in_viewport(self, mock_scene, mapper):
        """Scroll events in viewport area are forwarded to camera."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.screen_width = 1920
        mock_scene.TOP_BAR_HEIGHT = 50
        mock_scene.ui._has_modal_open = MagicMock(return_value=False)
        mock_scene.camera = MagicMock()

        # Simulate mouse in viewport (middle of screen)
        # STRATEGY_SIDEBAR_WIDTH is typically 400, so 500 should be in viewport
        with patch('pygame.mouse.get_pos', return_value=(500, 300)):
            event = pygame.event.Event(pygame.MOUSEWHEEL, {'y': 1})
            handler._handle_scroll(event)

        # Camera should receive the scroll event
        mock_scene.camera.update_input.assert_called_once()
        # Verify event list structure passed to camera
        args, _ = mock_scene.camera.update_input.call_args
        assert args[0] == 0  # dt=0
        assert event in args[1]  # event in events list

    def test_handle_scroll_blocked_when_modal_open(self, mock_scene, mapper):
        """Scroll events blocked when modal is open."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.screen_width = 1920
        mock_scene.TOP_BAR_HEIGHT = 50
        mock_scene.ui._has_modal_open = MagicMock(return_value=True)  # Modal is open
        mock_scene.camera = MagicMock()

        # Mouse in viewport but modal is open
        with patch('pygame.mouse.get_pos', return_value=(500, 300)):
            event = pygame.event.Event(pygame.MOUSEWHEEL, {'y': 1})
            handler._handle_scroll(event)

        # Camera should NOT receive the scroll event
        mock_scene.camera.update_input.assert_not_called()
        # Verify modal check returned True
        mock_scene.ui._has_modal_open.assert_called()
        assert mock_scene.ui._has_modal_open.return_value is True
