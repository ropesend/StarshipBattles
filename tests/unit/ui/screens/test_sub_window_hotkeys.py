"""Tests for sub-window hotkey integration (PROJ-71 Phase 3).

Verifies that OrdersWindow, BuildQueueScreen, TransferDialog,
and BuildQueueListWindow accept input_mapper and dispatch hotkey actions.

PROJ-328 Phase A Task A.6 (PROJ-322 Task 5.16 — non-Orders portion):
The OrdersWindow + BuildQueueListWindow hotkey clusters now use the
two-stage bypass_init pattern (after Tasks A.2 and A.3 landed those
classes' refactors). The BuildQueueScreen cluster is unchanged
(BuildQueueScreen isn't a UIWindow subclass, no bypass_init
applies). The TransferDialog cluster is left as-is — Phase C scope
will rewrite it alongside the deep TransferDialog split.
"""
import pytest
from unittest.mock import MagicMock, patch
import pygame

from game.ui.services.input_mapper import InputMapper
from tests.fixtures.ui_widget_factory import bypass_init


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

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


# =======================================================================
# Fleet Orders Window
# =======================================================================

class TestFleetOrdersWindowHotkeys:
    """OrdersWindow should accept input_mapper and dispatch hotkey actions.

    PROJ-328 Phase A Task A.6: Migrated to bypass_init +
    MockOrdersUiBuilder so the constructed window is a real
    OrdersWindow with the cheap-state delegates (_mapper,
    _order_describer) populated honestly. ``btn_clear`` comes from
    the Mock builder.
    """

    def _make_window(self, mapper):
        """Create an OrdersWindow under bypass_init."""
        from game.ui.screens.orders_window import OrdersWindow
        from tests.fixtures.orders_ui_builder import MockOrdersUiBuilder

        mock_fleet = MagicMock()
        mock_fleet.id = 1
        mock_fleet.name = "Test Fleet"
        mock_fleet.orders = []
        mock_fleet.construction_queue = []

        with bypass_init(OrdersWindow):
            win = OrdersWindow(
                pygame.Rect(0, 0, 400, 500),
                MagicMock(name="ui_manager"),
                mock_fleet,
                window_manager=None,
                input_mapper=mapper,
                ui_builder=MockOrdersUiBuilder(),
            )
        return win

    def test_accepts_input_mapper_param(self, mapper):
        """OrdersWindow stores the mapper."""
        win = self._make_window(mapper)
        assert win._mapper is mapper

    def test_delete_calls_clear_confirmation(self, mapper):
        """Delete triggers show_clear_confirmation via InputMapper."""
        win = self._make_window(mapper)
        win.show_clear_confirmation = MagicMock()
        event = _keydown(pygame.K_DELETE)
        win._handle_keydown(event)
        win.show_clear_confirmation.assert_called_once()

    def test_no_mapper_ignores_hotkeys(self):
        """Without mapper, _handle_keydown does nothing."""
        win = self._make_window(None)
        win.show_clear_confirmation = MagicMock()
        event = _keydown(pygame.K_DELETE)
        win._handle_keydown(event)
        win.show_clear_confirmation.assert_not_called()

    def test_clear_button_tooltip(self, mapper):
        """btn_clear tooltip shows Del hint."""
        win = self._make_window(mapper)
        win._apply_tooltips()
        tooltip_text = win.btn_clear.set_tooltip.call_args[0][0]
        assert "Del" in tooltip_text


# =======================================================================
# Build Queue Screen
# =======================================================================

class TestBuildQueueScreenHotkeys:
    """BuildQueueScreen should accept input_mapper and dispatch hotkey actions."""

    def _make_screen(self, mapper):
        """Create a minimal BuildQueueScreen with mapper."""
        from game.ui.screens.build_queue_screen import BuildQueueScreen

        screen = MagicMock(spec=BuildQueueScreen)
        screen._mapper = mapper
        screen.on_close = MagicMock()
        # PROJ-180: Use panels.* directly (eradicate backward-compat properties)
        screen.panels = MagicMock()
        screen.panels.btn_close = MagicMock()
        screen.panels.btn_add_to_queue = MagicMock()
        screen.panels.btn_remove_from_queue = MagicMock()
        screen.panels.btn_category_complex = MagicMock()
        screen.panels.btn_category_ship = MagicMock()
        screen.panels.btn_category_satellite = MagicMock()
        screen.panels.btn_category_fighter = MagicMock()
        screen.controller = MagicMock()
        screen.drag_handler = MagicMock()
        screen.drag_handler.selected_design = None
        screen.selected_queue_index = None
        screen.selected_queue_indices = {0}
        screen.active_queue_source = MagicMock()
        screen.build_context = MagicMock()
        screen._close = MagicMock()
        screen._refresh_items_list = MagicMock()
        screen._refresh_queue_display = MagicMock()
        # Bind the real method
        screen._handle_keydown = BuildQueueScreen._handle_keydown.__get__(screen, BuildQueueScreen)
        return screen

    def test_escape_closes_screen(self, mapper):
        """ESC triggers _close() via InputMapper."""
        screen = self._make_screen(mapper)
        event = _keydown(pygame.K_ESCAPE)
        screen._handle_keydown(event)
        screen._close.assert_called_once()

    def test_key_1_selects_complexes(self, mapper):
        """Key 1 switches to Complexes category."""
        screen = self._make_screen(mapper)
        event = _keydown(pygame.K_1)
        screen._handle_keydown(event)
        screen.controller.set_category.assert_called_with("complex")
        screen._refresh_items_list.assert_called_once()

    def test_key_2_selects_ships(self, mapper):
        """Key 2 switches to Ships category."""
        screen = self._make_screen(mapper)
        event = _keydown(pygame.K_2)
        screen._handle_keydown(event)
        screen.controller.set_category.assert_called_with("ship")

    def test_key_3_selects_satellites(self, mapper):
        """Key 3 switches to Satellites category."""
        screen = self._make_screen(mapper)
        event = _keydown(pygame.K_3)
        screen._handle_keydown(event)
        screen.controller.set_category.assert_called_with("satellite")

    def test_key_4_selects_fighters(self, mapper):
        """Key 4 switches to Fighters category."""
        screen = self._make_screen(mapper)
        event = _keydown(pygame.K_4)
        screen._handle_keydown(event)
        screen.controller.set_category.assert_called_with("fighter")

    def test_a_adds_to_queue(self, mapper):
        """Key A adds selected design to queue."""
        screen = self._make_screen(mapper)
        screen.drag_handler.selected_design = "test_design"
        event = _keydown(pygame.K_a)
        screen._handle_keydown(event)
        screen.controller.add_to_queue.assert_called_once_with("test_design")

    def test_delete_removes_from_queue(self, mapper):
        """Delete key removes selected queue item."""
        from game.ui.screens.build_queue_screen import BuildQueueScreen
        screen = self._make_screen(mapper)
        # Bind _handle_remove and _get_active_queue since _handle_keydown delegates to them
        screen._handle_remove = BuildQueueScreen._handle_remove.__get__(screen, BuildQueueScreen)
        screen._get_active_queue = BuildQueueScreen._get_active_queue.__get__(screen, BuildQueueScreen)
        screen.selected_queue_index = 0
        screen.selected_queue_indices = set()  # Empty set for single selection mode
        active_queue = [{"design_id": "test", "turns_remaining": 5}]
        screen.active_queue_source.construction_queue = active_queue
        event = _keydown(pygame.K_DELETE)
        screen._handle_keydown(event)
        screen._refresh_queue_display.assert_called()

    def test_no_mapper_ignores_hotkeys(self):
        """Without mapper, _handle_keydown does nothing."""
        screen = self._make_screen(None)
        event = _keydown(pygame.K_ESCAPE)
        screen._handle_keydown(event)
        screen._close.assert_not_called()

    def test_close_button_tooltip(self, mapper):
        """Close button shows Esc tooltip."""
        from game.ui.screens.build_queue_screen import BuildQueueScreen
        screen = self._make_screen(mapper)
        # PROJ-180: panels already set up in _make_screen
        screen._apply_tooltips = BuildQueueScreen._apply_tooltips.__get__(screen, BuildQueueScreen)
        screen._apply_tooltips()
        tooltip_text = screen.panels.btn_close.set_tooltip.call_args[0][0]
        assert "Esc" in tooltip_text

    def test_category_button_tooltips(self, mapper):
        """Category buttons show 1-4 tooltips."""
        from game.ui.screens.build_queue_screen import BuildQueueScreen
        screen = self._make_screen(mapper)
        # PROJ-180: panels already set up in _make_screen
        screen._apply_tooltips = BuildQueueScreen._apply_tooltips.__get__(screen, BuildQueueScreen)
        screen._apply_tooltips()
        assert "1" in screen.panels.btn_category_complex.set_tooltip.call_args[0][0]
        assert "2" in screen.panels.btn_category_ship.set_tooltip.call_args[0][0]
        assert "3" in screen.panels.btn_category_satellite.set_tooltip.call_args[0][0]
        assert "4" in screen.panels.btn_category_fighter.set_tooltip.call_args[0][0]


# =======================================================================
# Transfer Dialog
# =======================================================================

class TestTransferDialogHotkeys:
    """TransferDialog should accept input_mapper and dispatch hotkey actions."""

    def _make_dialog(self, mapper):
        """Create a minimal TransferDialog with mapper."""
        from game.ui.screens.transfer_dialog import TransferDialog

        dialog = MagicMock(spec=TransferDialog)
        dialog._mapper = mapper
        dialog.btn_confirm = MagicMock()
        dialog.btn_cancel = MagicMock()
        dialog._on_confirm = MagicMock()
        dialog.kill = MagicMock()
        dialog._handle_keydown = TransferDialog._handle_keydown.__get__(dialog, TransferDialog)
        return dialog

    def test_enter_confirms(self, mapper):
        """Enter triggers _issue_order via InputMapper."""
        dialog = self._make_dialog(mapper)
        event = _keydown(pygame.K_RETURN)
        dialog._handle_keydown(event)
        dialog._on_confirm.assert_called_once()

    def test_escape_cancels(self, mapper):
        """ESC triggers kill() via InputMapper."""
        dialog = self._make_dialog(mapper)
        event = _keydown(pygame.K_ESCAPE)
        dialog._handle_keydown(event)
        dialog.kill.assert_called_once()

    def test_no_mapper_ignores_hotkeys(self):
        """Without mapper, _handle_keydown does nothing."""
        dialog = self._make_dialog(None)
        event = _keydown(pygame.K_RETURN)
        dialog._handle_keydown(event)
        dialog._on_confirm.assert_not_called()

    def test_confirm_button_tooltip(self, mapper):
        """Confirm button shows Enter tooltip."""
        dialog = self._make_dialog(mapper)
        dialog._apply_tooltips = MagicMock()
        from game.ui.screens.transfer_dialog import TransferDialog
        dialog._apply_tooltips = TransferDialog._apply_tooltips.__get__(dialog, TransferDialog)
        dialog._apply_tooltips()
        tooltip_text = dialog.btn_confirm.set_tooltip.call_args[0][0]
        assert "Enter" in tooltip_text

    def test_cancel_button_tooltip(self, mapper):
        """Cancel button shows Esc tooltip."""
        dialog = self._make_dialog(mapper)
        from game.ui.screens.transfer_dialog import TransferDialog
        dialog._apply_tooltips = TransferDialog._apply_tooltips.__get__(dialog, TransferDialog)
        dialog._apply_tooltips()
        tooltip_text = dialog.btn_cancel.set_tooltip.call_args[0][0]
        assert "Esc" in tooltip_text


# =======================================================================
# Build Queue List Window
# =======================================================================

class TestBuildQueueListWindowHotkeys:
    """BuildQueueListWindow should accept input_mapper and handle ESC.

    PROJ-328 Phase A Task A.6: Migrated to bypass_init + null builder
    so the constructed window is a real BuildQueueListWindow with
    cheap-state populated; kill() is patched out per-test to avoid
    the (mock-row-label) cleanup chain.
    """

    def _make_window(self, mapper):
        """Create a real BuildQueueListWindow under bypass_init."""
        from game.ui.screens.build_queue_list_window import BuildQueueListWindow
        from tests.fixtures.build_queue_list_ui_builder import (
            NullBuildQueueListUiBuilder,
        )

        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        with bypass_init(BuildQueueListWindow):
            win = BuildQueueListWindow(
                pygame.Rect(0, 0, 400, 300),
                MagicMock(name="ui_manager"),
                empire,
                window_manager=None,
                input_mapper=mapper,
                ui_builder=NullBuildQueueListUiBuilder(),
            )
        # Spy kill so we can assert without entering the real cleanup.
        win.kill = MagicMock()
        return win

    def test_escape_closes(self, mapper):
        """ESC triggers kill() via InputMapper."""
        win = self._make_window(mapper)
        event = _keydown(pygame.K_ESCAPE)
        win._handle_keydown(event)
        win.kill.assert_called_once()

    def test_no_mapper_ignores(self):
        """Without mapper, _handle_keydown does nothing."""
        win = self._make_window(None)
        event = _keydown(pygame.K_ESCAPE)
        win._handle_keydown(event)
        win.kill.assert_not_called()


# =======================================================================
# InputMapper passthrough from StrategyUI
# =======================================================================

class TestStrategyUIPassesMapper:
    """StrategyUI should pass input_mapper to sub-window constructors via window manager."""

    @patch('game.ui.screens.orders_window.OrdersWindow')
    def test_open_orders_passes_mapper(self, MockWindow, mapper):
        """open_orders_window passes input_mapper to OrdersWindow via window manager."""
        from game.ui.screens.strategy_window_manager import StrategyWindowManager

        scene = MagicMock()
        manager = MagicMock()
        wm = StrategyWindowManager(scene, manager, 1920, 1080, input_mapper=mapper)

        fleet = MagicMock()
        wm.open_orders_window(fleet)

        # Verify mapper was passed as keyword arg
        _, kwargs = MockWindow.call_args
        assert kwargs.get('input_mapper') is mapper

    @patch('game.ui.screens.strategy_windows.build_queue_windows.BuildQueueListWindow')
    def test_open_build_queue_list_passes_mapper(self, MockWindow, mapper):
        """open_build_queue_list passes input_mapper to BuildQueueListWindow via window manager."""
        from game.ui.screens.strategy_window_manager import StrategyWindowManager

        scene = MagicMock()
        scene.current_empire = MagicMock()
        manager = MagicMock()
        wm = StrategyWindowManager(scene, manager, 1920, 1080, input_mapper=mapper)

        wm.open_build_queue_list()

        _, kwargs = MockWindow.call_args
        assert kwargs.get('input_mapper') is mapper
