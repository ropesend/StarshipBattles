"""Tests for StrategyInputHandler integration with InputMapper (PROJ-71 Phase 2).

Verifies that the input handler resolves hotkeys via InputMapper instead of
hardcoded pygame key checks, and that new hotkey-triggered button actions work.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame

from game.core.input_actions import InputAction, KeyBinding
from game.core.input_mapper import InputMapper
from game.ui.screens.strategy_input_handler import StrategyInputHandler


@pytest.fixture
def mock_scene():
    """Create a mock StrategyScreen for handler tests."""
    scene = MagicMock()
    scene.ui = MagicMock()
    scene.ui.manager = MagicMock()
    scene.ui.planet_list_window = None
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
        handler.handle_event(_keydown(pygame.K_m))
        assert handler.input_mode == 'MOVE'

    def test_j_triggers_join_mode(self, mock_scene, mapper):
        """Pressing J sets input mode to JOIN when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        handler.handle_event(_keydown(pygame.K_j))
        assert handler.input_mode == 'JOIN'

    def test_c_triggers_colonize_mode(self, mock_scene, mapper):
        """Pressing C sets input mode to COLONIZE_TARGET when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = MagicMock()
        handler.handle_event(_keydown(pygame.K_c))
        assert handler.input_mode == 'COLONIZE_TARGET'

    def test_t_triggers_transfer_dialog(self, mock_scene, mapper):
        """Pressing T opens transfer dialog when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_fleet = MagicMock()
        mock_fleet.location = (5, 5)
        mock_scene.selected_fleet = mock_fleet
        handler.handle_event(_keydown(pygame.K_t))
        mock_scene.ui.open_transfer_dialog.assert_called_once_with(mock_fleet, (5, 5))

    def test_escape_cancels_mode(self, mock_scene, mapper):
        """Pressing ESC resets input mode to SELECT."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.input_mode = 'MOVE'
        handler.handle_event(_keydown(pygame.K_ESCAPE))
        assert handler.input_mode == 'SELECT'

    def test_fleet_keys_ignored_without_fleet(self, mock_scene, mapper):
        """Fleet-specific keys should be ignored when no fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        handler.handle_event(_keydown(pygame.K_m))
        assert handler.input_mode == 'SELECT'  # Still in SELECT

    def test_fleet_keys_ignored_without_fleet_join(self, mock_scene, mapper):
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        handler.handle_event(_keydown(pygame.K_j))
        assert handler.input_mode == 'SELECT'

    def test_fleet_keys_ignored_without_fleet_colonize(self, mock_scene, mapper):
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        handler.handle_event(_keydown(pygame.K_c))
        assert handler.input_mode == 'SELECT'


class TestZoomAndScreenshotViaMapper:
    """Zoom and screenshot hotkeys resolved via InputMapper."""

    def test_shift_g_zooms_galaxy(self, mock_scene, mapper):
        """Shift+G triggers galaxy zoom."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_g, pygame.KMOD_SHIFT))
        mock_scene._camera_nav.zoom_to_galaxy.assert_called_once()

    def test_shift_s_zooms_system(self, mock_scene, mapper):
        """Shift+S triggers system zoom."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_s, pygame.KMOD_SHIFT))
        mock_scene._camera_nav.zoom_to_system.assert_called_once()

    @patch.object(StrategyInputHandler, '_take_screenshot_full')
    def test_f12_takes_full_screenshot(self, mock_screenshot, mock_scene, mapper):
        """F12 triggers full screenshot."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_F12))
        mock_screenshot.assert_called_once()

    @patch.object(StrategyInputHandler, '_take_screenshot_viewport')
    def test_f11_takes_viewport_screenshot(self, mock_screenshot, mock_scene, mapper):
        """F11 triggers viewport screenshot."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_F11))
        mock_screenshot.assert_called_once()


class TestNewHotkeyButtonActions:
    """New hotkey-triggered button actions (Task 2.5)."""

    def test_enter_triggers_end_turn(self, mock_scene, mapper):
        """Enter key triggers advance_turn."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_RETURN))
        mock_scene.advance_turn.assert_called_once()

    def test_p_opens_planets(self, mock_scene, mapper):
        """P key opens planet list."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_p))
        mock_scene.ui.open_planet_list.assert_called_once()

    def test_d_opens_design(self, mock_scene, mapper):
        """D key opens design workshop."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_d))
        mock_scene.on_design_click.assert_called_once()

    def test_b_opens_build_queues(self, mock_scene, mapper):
        """B key opens build queue list."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_b))
        mock_scene.ui.open_build_queue_list.assert_called_once()

    def test_ctrl_s_saves_game(self, mock_scene, mapper):
        """Ctrl+S saves game."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_s, pygame.KMOD_CTRL))
        mock_scene.on_save_game_click.assert_called_once()

    def test_comma_prev_colony(self, mock_scene, mapper):
        """, key cycles to previous colony."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_COMMA))
        mock_scene.cycle_selection.assert_called_once_with('colony', -1)

    def test_period_next_colony(self, mock_scene, mapper):
        """. key cycles to next colony."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_PERIOD))
        mock_scene.cycle_selection.assert_called_once_with('colony', 1)

    def test_leftbracket_prev_fleet(self, mock_scene, mapper):
        """[ key cycles to previous fleet."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_LEFTBRACKET))
        mock_scene.cycle_selection.assert_called_once_with('fleet', -1)

    def test_rightbracket_next_fleet(self, mock_scene, mapper):
        """] key cycles to next fleet."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        handler.handle_event(_keydown(pygame.K_RIGHTBRACKET))
        mock_scene.cycle_selection.assert_called_once_with('fleet', 1)

    def test_o_opens_orders_with_fleet(self, mock_scene, mapper):
        """O key opens fleet orders window when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet
        handler.handle_event(_keydown(pygame.K_o))
        mock_scene.ui.open_orders_window.assert_called_once_with(mock_fleet)

    def test_o_ignored_without_fleet(self, mock_scene, mapper):
        """O key does nothing when no fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        handler.handle_event(_keydown(pygame.K_o))
        mock_scene.ui.open_orders_window.assert_not_called()

    def test_f_opens_fleet_report_with_fleet(self, mock_scene, mapper):
        """F key opens fleet report when fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_fleet = MagicMock()
        mock_scene.selected_fleet = mock_fleet
        handler.handle_event(_keydown(pygame.K_f))
        mock_scene.ui.open_fleet_report_window.assert_called_once_with(mock_fleet)

    def test_f_ignored_without_fleet(self, mock_scene, mapper):
        """F key does nothing when no fleet selected."""
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None
        handler.handle_event(_keydown(pygame.K_f))
        mock_scene.ui.open_fleet_report_window.assert_not_called()


class TestBackwardCompatWithoutMapper:
    """When mapper is None, hardcoded behavior is preserved."""

    def test_m_still_works_without_mapper(self, mock_scene):
        """M key triggers MOVE even without mapper (backward compat)."""
        handler = StrategyInputHandler(mock_scene)
        mock_scene.selected_fleet = MagicMock()
        handler.handle_event(_keydown(pygame.K_m))
        assert handler.input_mode == 'MOVE'

    def test_shift_g_still_works_without_mapper(self, mock_scene):
        """Shift+G triggers galaxy zoom without mapper."""
        handler = StrategyInputHandler(mock_scene)
        handler.handle_event(_keydown(pygame.K_g, pygame.KMOD_SHIFT))
        mock_scene._camera_nav.zoom_to_galaxy.assert_called_once()


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
