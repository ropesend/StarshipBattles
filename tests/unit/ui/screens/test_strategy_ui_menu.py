"""Tests for StrategyUI menu panel wiring (PROJ-72 Phase 2).

Tests the menu button replacement, panel management methods,
event handling for click-outside/Escape, and modal detection.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# --- Helpers ---

def _make_strategy_ui():
    """Create a StrategyUI with mocked pygame_gui dependencies.

    Returns (ui, scene_mock, manager_mock).
    """
    from game.ui.screens.strategy_ui import StrategyUI

    # Prevent actual __init__ from running (too many pygame_gui deps)
    with patch.object(StrategyUI, '__init__', lambda self, *a, **kw: None):
        ui = StrategyUI.__new__(StrategyUI)

    # Set up minimal required attributes
    scene = MagicMock()
    manager = MagicMock()

    ui.scene = scene
    ui.width = 1920
    ui.height = 1080
    ui.manager = manager
    ui.menu_panel = None

    # Mock buttons needed for event handling
    ui.btn_menu = MagicMock()
    ui.btn_menu.get_abs_rect.return_value = pygame.Rect(700, 5, 100, 40)
    ui.btn_planets = MagicMock()
    ui.btn_design = MagicMock()
    ui.btn_build_queues = MagicMock()
    ui.btn_all_queues = MagicMock()
    ui.btn_raw_data = MagicMock()
    ui.btn_colonize = MagicMock()
    ui.btn_orders = MagicMock()
    ui.btn_fleet_report = MagicMock()
    ui.btn_empire = MagicMock()
    ui.btn_research = MagicMock()
    ui.btn_build_fleet = MagicMock()

    # Modal tracking attributes (PROJ-86: now via window manager)
    ui.planet_report_panel = None
    ui.current_selection = None

    # PROJ-86: Window manager mock
    ui._window_manager = MagicMock()
    ui._window_manager.fleet_orders_window = None
    ui._window_manager.planet_list_window = None
    ui._window_manager.build_queue_list_window = None
    ui._window_manager.empire_build_queue_window = None
    ui._window_manager.fleet_report_window = None
    ui._window_manager.transfer_dialog = None
    ui._window_manager.event_log_window = None
    ui._window_manager.ui_callbacks = {}
    ui._window_manager.process_ui_callbacks.return_value = False

    # System/sector trees (mock process_event to avoid issues)
    ui.system_tree = MagicMock()
    ui.system_tree.process_event.return_value = False
    ui.sector_tree = MagicMock()
    ui.sector_tree.process_event.return_value = False

    # PROJ-86 Phase 7: Event router
    from game.ui.screens.strategy_event_router import StrategyEventRouter
    ui._event_router = StrategyEventRouter(ui)

    return ui, scene, manager


# --- Task 2.1: Menu Button Replaces Save Game ---

class TestMenuButtonAttribute:
    """Verify btn_save_game is replaced by btn_menu in StrategyUI."""

    def test_no_btn_save_game_attribute(self):
        """StrategyUI should NOT have btn_save_game after Phase 2."""
        from game.ui.screens import strategy_ui
        import inspect
        source = inspect.getsource(strategy_ui.StrategyUI)
        assert 'btn_save_game' not in source

    def test_has_btn_menu_in_source(self):
        """StrategyUI source should reference btn_menu."""
        from game.ui.screens import strategy_ui
        import inspect
        source = inspect.getsource(strategy_ui.StrategyUI)
        assert 'btn_menu' in source

    def test_has_menu_panel_attribute_in_init(self):
        """StrategyUI source should initialize menu_panel = None."""
        from game.ui.screens import strategy_ui
        import inspect
        source = inspect.getsource(strategy_ui.StrategyUI.__init__)
        assert 'menu_panel' in source


# --- Task 2.2: Panel Management Methods ---

class TestToggleMenuPanel:
    """Verify toggle_menu_panel opens/closes the panel."""

    def test_toggle_opens_panel_when_none(self):
        ui, _, _ = _make_strategy_ui()
        ui.menu_panel = None

        with patch.object(ui, 'open_menu_panel') as mock_open:
            ui.toggle_menu_panel()
            mock_open.assert_called_once()

    def test_toggle_closes_panel_when_exists(self):
        ui, _, _ = _make_strategy_ui()
        ui.menu_panel = MagicMock()  # Panel exists

        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui.toggle_menu_panel()
            mock_close.assert_called_once()


class TestOpenMenuPanel:
    """Verify open_menu_panel creates the panel correctly."""

    def test_creates_strategy_menu_panel(self):
        ui, _, manager = _make_strategy_ui()

        with patch('game.ui.screens.strategy_ui.StrategyMenuPanel') as MockPanel:
            mock_instance = MagicMock()
            MockPanel.return_value = mock_instance
            ui.open_menu_panel()

            assert ui.menu_panel is mock_instance
            MockPanel.assert_called_once()

    def test_panel_position_below_button(self):
        ui, _, manager = _make_strategy_ui()
        # btn_menu rect: x=700, y=5, w=100, h=40 => bottom=45
        ui.btn_menu.get_abs_rect.return_value = pygame.Rect(700, 5, 100, 40)

        with patch('game.ui.screens.strategy_ui.StrategyMenuPanel') as MockPanel:
            ui.open_menu_panel()
            call_args = MockPanel.call_args
            panel_rect = call_args[0][0]
            assert panel_rect.x == 700
            assert panel_rect.y == 47  # 45 + 2 gap

    def test_passes_callback(self):
        ui, _, manager = _make_strategy_ui()

        with patch('game.ui.screens.strategy_ui.StrategyMenuPanel') as MockPanel:
            ui.open_menu_panel()
            call_args = MockPanel.call_args
            callback = call_args[0][2]
            assert callback == ui._on_menu_option_selected

    def test_passes_manager(self):
        ui, _, manager = _make_strategy_ui()

        with patch('game.ui.screens.strategy_ui.StrategyMenuPanel') as MockPanel:
            ui.open_menu_panel()
            call_args = MockPanel.call_args
            assert call_args[0][1] is manager


class TestCloseMenuPanel:
    """Verify close_menu_panel kills the panel."""

    def test_kills_existing_panel(self):
        ui, _, _ = _make_strategy_ui()
        panel = MagicMock()
        ui.menu_panel = panel

        ui.close_menu_panel()

        panel.kill.assert_called_once()
        assert ui.menu_panel is None

    def test_noop_when_no_panel(self):
        ui, _, _ = _make_strategy_ui()
        ui.menu_panel = None

        # Should not raise
        ui.close_menu_panel()
        assert ui.menu_panel is None


class TestOnMenuOptionSelected:
    """Verify _on_menu_option_selected closes panel and dispatches."""

    def test_closes_panel(self):
        ui, scene, _ = _make_strategy_ui()
        ui.menu_panel = MagicMock()

        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui._on_menu_option_selected("save_game")
            mock_close.assert_called_once()

    def test_calls_scene_on_menu_option(self):
        ui, scene, _ = _make_strategy_ui()
        ui.menu_panel = MagicMock()

        with patch.object(ui, 'close_menu_panel'):
            ui._on_menu_option_selected("save_game")
            scene.on_menu_option.assert_called_once_with("save_game")

    def test_dispatches_different_options(self):
        ui, scene, _ = _make_strategy_ui()
        ui.menu_panel = MagicMock()

        with patch.object(ui, 'close_menu_panel'):
            ui._on_menu_option_selected("quit_game")
            scene.on_menu_option.assert_called_once_with("quit_game")


# --- Task 2.3: Event Handling ---

class TestMenuButtonEvent:
    """Verify btn_menu click toggles menu panel."""

    def test_btn_menu_click_toggles_panel(self):
        import pygame_gui
        ui, _, _ = _make_strategy_ui()

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = ui.btn_menu

        with patch.object(ui, 'toggle_menu_panel') as mock_toggle:
            ui.handle_event(event)
            mock_toggle.assert_called_once()


class TestClickOutsideClosesPanel:
    """Verify MOUSEBUTTONDOWN outside panel closes it."""

    def test_click_outside_panel_and_button_closes(self):
        ui, _, _ = _make_strategy_ui()
        panel = MagicMock()
        panel.get_abs_rect.return_value = pygame.Rect(700, 47, 220, 245)
        ui.menu_panel = panel

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)  # Outside both panel and button

        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui.handle_event(event)
            mock_close.assert_called_once()

    def test_click_inside_panel_does_not_close(self):
        ui, _, _ = _make_strategy_ui()
        panel = MagicMock()
        panel.get_abs_rect.return_value = pygame.Rect(700, 47, 220, 245)
        ui.menu_panel = panel

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (750, 100)  # Inside panel rect

        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui.handle_event(event)
            mock_close.assert_not_called()

    def test_click_on_menu_button_does_not_close(self):
        ui, _, _ = _make_strategy_ui()
        panel = MagicMock()
        panel.get_abs_rect.return_value = pygame.Rect(700, 47, 220, 245)
        ui.menu_panel = panel
        # Menu button rect overlaps at (700, 5, 100, 40)

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (750, 20)  # Inside menu button rect

        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui.handle_event(event)
            mock_close.assert_not_called()

    def test_no_panel_does_not_close(self):
        ui, _, _ = _make_strategy_ui()
        ui.menu_panel = None

        event = MagicMock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)

        # Should not raise
        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui.handle_event(event)
            mock_close.assert_not_called()


class TestEscapeClosesPanel:
    """Verify Escape key closes the menu panel."""

    def test_escape_closes_panel(self):
        ui, _, _ = _make_strategy_ui()
        ui.menu_panel = MagicMock()

        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE

        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui.handle_event(event)
            mock_close.assert_called_once()

    def test_escape_without_panel_does_not_close(self):
        ui, _, _ = _make_strategy_ui()
        ui.menu_panel = None

        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_ESCAPE

        with patch.object(ui, 'close_menu_panel') as mock_close:
            ui.handle_event(event)
            mock_close.assert_not_called()


class TestMenuPanelModal:
    """Verify _has_modal_open returns True when menu panel is open."""

    def test_modal_true_with_menu_panel(self):
        ui, _, _ = _make_strategy_ui()
        ui.menu_panel = MagicMock()

        assert ui._has_modal_open() is True

    def test_modal_false_without_menu_panel(self):
        ui, scene, _ = _make_strategy_ui()
        ui.menu_panel = None
        # No other modals open
        ui.fleet_orders_window = None
        ui.planet_list_window = None
        ui.fleet_report_window = None
        ui.transfer_dialog = None
        ui.build_queue_list_window = None
        ui.empire_build_queue_window = None
        # scene.build_queue_screen and scene.action_open_design also checked
        scene.build_queue_screen = None
        scene.action_open_design = False

        assert ui._has_modal_open() is False


# --- Import Verification ---

class TestStrategyMenuPanelImport:
    """Verify StrategyMenuPanel is imported in strategy_ui."""

    def test_import_exists(self):
        from game.ui.screens import strategy_ui
        import inspect
        source = inspect.getsource(strategy_ui)
        assert 'from game.ui.screens.strategy_menu_panel import StrategyMenuPanel' in source
