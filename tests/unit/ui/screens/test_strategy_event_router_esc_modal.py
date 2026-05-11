"""Tests for issue #18: Esc closes the topmost strategy sub-window.

Verifies the router-level Esc handler in StrategyEventRouter.route_event:

- When the menu panel is open, Esc closes the menu panel (existing behavior).
- When no menu panel is open and any StrategyModalWindow subclass is live,
  Esc calls .kill() on the topmost (last-appended) modal.
- When multiple modals are stacked, Esc closes only the topmost.
- When no menu panel and no modal are live, Esc is a no-op.

The router resolves "topmost" via list(window_manager.iter_live_modals())[-1].
Each window's kill() already fires its on_close_callback before
super().kill(), so Esc matches the X-button close path.
"""

import pytest
from unittest.mock import MagicMock
import pygame

from game.ui.screens.strategy_event_router import StrategyEventRouter


def _keydown(key):
    """Helper: create a pygame KEYDOWN event."""
    return pygame.event.Event(pygame.KEYDOWN, {'key': key, 'mod': 0})


@pytest.fixture
def mock_ui():
    """Mock StrategyUI with a window_manager whose iter_live_modals is
    controlled by a private _modals_for_test list (mirrors the helper in
    test_strategy_event_router.py).
    """
    ui = MagicMock()
    ui.width = 2560
    ui.height = 1600
    ui.menu_panel = None
    ui.fleet_context_menu = None  # issue #20

    ui.window_manager = MagicMock()
    ui.window_manager.fleet_orders_window = None
    ui.window_manager._modals_for_test = []
    ui.window_manager.iter_live_modals = lambda: iter(
        list(ui.window_manager._modals_for_test)
    )
    ui.window_manager.process_ui_callbacks.return_value = False

    # System/sector trees: drop the event.
    ui.system_tree = MagicMock()
    ui.system_tree.process_event.return_value = False
    ui.sector_tree = MagicMock()
    ui.sector_tree.process_event.return_value = False

    return ui


@pytest.fixture
def router(mock_ui):
    return StrategyEventRouter(mock_ui)


def _make_modal(name: str) -> MagicMock:
    """Create a mock modal window with a kill() method and a name."""
    m = MagicMock(name=name)
    m.alive.return_value = True
    return m


# ---------------------------------------------------------------------------
# AC: Esc closes each named window via the router walk
# ---------------------------------------------------------------------------


class TestEscClosesSingleModal:
    """Esc closes the single live modal via .kill()."""

    def test_esc_kills_planet_list_window(self, router, mock_ui):
        planet_list = _make_modal("PlanetListWindow")
        mock_ui.window_manager._modals_for_test = [planet_list]

        router.route_event(_keydown(pygame.K_ESCAPE))

        planet_list.kill.assert_called_once()

    def test_esc_kills_star_list_window(self, router, mock_ui):
        star_list = _make_modal("StarListWindow")
        mock_ui.window_manager._modals_for_test = [star_list]

        router.route_event(_keydown(pygame.K_ESCAPE))

        star_list.kill.assert_called_once()

    def test_esc_kills_empire_panel_window(self, router, mock_ui):
        empire_panel = _make_modal("EmpirePanelWindow")
        mock_ui.window_manager._modals_for_test = [empire_panel]

        router.route_event(_keydown(pygame.K_ESCAPE))

        empire_panel.kill.assert_called_once()

    def test_esc_kills_build_queue_list_window(self, router, mock_ui):
        """Regression: BuildQueueListWindow already handles Esc via its
        own _handle_keydown. The router-level walk should also call
        .kill() on it — double-kill is safe (kill() is idempotent and
        unregister_modal swallows ValueError).
        """
        build_queue = _make_modal("BuildQueueListWindow")
        mock_ui.window_manager._modals_for_test = [build_queue]

        router.route_event(_keydown(pygame.K_ESCAPE))

        build_queue.kill.assert_called_once()


# ---------------------------------------------------------------------------
# AC: Stacked modals — Esc closes only the topmost
# ---------------------------------------------------------------------------


class TestEscStackedModals:
    """When multiple modals are live, only the last-appended one closes."""

    def test_esc_kills_only_topmost(self, router, mock_ui):
        older = _make_modal("OlderModal")
        middle = _make_modal("MiddleModal")
        topmost = _make_modal("TopmostModal")
        mock_ui.window_manager._modals_for_test = [older, middle, topmost]

        router.route_event(_keydown(pygame.K_ESCAPE))

        topmost.kill.assert_called_once()
        older.kill.assert_not_called()
        middle.kill.assert_not_called()


# ---------------------------------------------------------------------------
# AC: Menu-panel branch preserved unchanged
# ---------------------------------------------------------------------------


class TestEscMenuPanelPrecedence:
    """Menu panel always wins over modal walk when both are live."""

    def test_esc_with_menu_panel_closes_menu_not_modal(self, router, mock_ui):
        mock_ui.menu_panel = MagicMock(name="menu_panel")
        modal = _make_modal("SomeModal")
        mock_ui.window_manager._modals_for_test = [modal]

        router.route_event(_keydown(pygame.K_ESCAPE))

        mock_ui.close_menu_panel.assert_called_once()
        modal.kill.assert_not_called()

    def test_esc_with_only_menu_panel_closes_menu(self, router, mock_ui):
        mock_ui.menu_panel = MagicMock(name="menu_panel")

        router.route_event(_keydown(pygame.K_ESCAPE))

        mock_ui.close_menu_panel.assert_called_once()


# ---------------------------------------------------------------------------
# AC: No modals, no menu panel — Esc is a no-op
# ---------------------------------------------------------------------------


class TestEscNoop:
    """Esc with nothing open does not raise and does not call close_menu_panel."""

    def test_esc_with_nothing_open_does_not_raise(self, router, mock_ui):
        # No modals, no menu panel.
        router.route_event(_keydown(pygame.K_ESCAPE))

        mock_ui.close_menu_panel.assert_not_called()

    def test_non_escape_keydown_does_not_kill_modal(self, router, mock_ui):
        """Other keypresses should not trigger the modal walk."""
        modal = _make_modal("SomeModal")
        mock_ui.window_manager._modals_for_test = [modal]

        router.route_event(_keydown(pygame.K_a))

        modal.kill.assert_not_called()
