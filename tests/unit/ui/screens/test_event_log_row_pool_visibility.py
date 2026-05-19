"""Obs 3 regression: row-pool widgets must stay hidden across re-open.

``EventLogWindow`` (and sibling reusable modals) uses a ``VirtualTable``
row pool. ``update_visible_rows()`` hides surplus rows via
``row["bg"].hide()``, but pygame_gui's ``UIContainer.show(True)`` cascade
fired by ``UIWindow.show()`` re-shows every descendant — re-exposing the
just-hidden surplus rows.

``StrategyModalWindow._post_show_hook()`` is the extension point that
subclasses owning a VirtualTable override to call
``virtual_table.force_update() + update_visible_rows()`` after the
cascade. ``BuildQueueScreen.show()`` already does this inline; this
suite locks the equivalent behaviour into the sibling reusable modals
(EventLogWindow, PlanetListWindow, StarListWindow).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from tests.fixtures.ui_widget_factory import bypass_init


# ---------------------------------------------------------------------------
# Test 1 — EventLogWindow.show() re-runs the row-pool visibility pass.
# ---------------------------------------------------------------------------


@pytest.fixture
def event_log_window():
    """Construct an EventLogWindow under bypass_init with a Mock VirtualTable."""
    from game.ui.screens.event_log_window import EventLogWindow

    with bypass_init(EventLogWindow):
        rect = pygame.Rect(0, 0, 1400, 800)
        manager = MagicMock(name="ui_manager")
        events = [{"category": "combat", "turn": 1, "message": "old"}]
        window_manager = MagicMock(name="window_manager")
        window = EventLogWindow(
            rect, manager, events,
            window_manager=window_manager,
            empire_name="Test Empire",
        )
        window.is_blocking = True
        window.data_source = MagicMock(name="data_source")
        window.virtual_table = MagicMock(name="virtual_table")
        return window


def test_event_log_show_reasserts_row_visibility_after_cascade(event_log_window):
    """``EventLogWindow.show()`` (via the base hook) must call
    ``virtual_table.force_update()`` and ``update_visible_rows()`` AFTER
    pygame_gui's recursive un-hide so surplus pool rows stay hidden.
    """
    with patch("pygame_gui.elements.UIWindow.show"), \
         patch("pygame_gui.elements.UIWindow.hide"):
        event_log_window.hide()
        event_log_window.virtual_table.reset_mock()
        event_log_window.show()

    event_log_window.virtual_table.force_update.assert_called()
    event_log_window.virtual_table.update_visible_rows.assert_called()


def test_event_log_show_hook_no_ops_when_virtual_table_missing(event_log_window):
    """The hook must be defensive against shell-only / pre-builder states
    where ``virtual_table`` is still ``None`` (matches the
    ``BuildQueueScreen.show()`` guard pattern)."""
    event_log_window.virtual_table = None

    with patch("pygame_gui.elements.UIWindow.show"), \
         patch("pygame_gui.elements.UIWindow.hide"):
        event_log_window.hide()
        # Must not raise.
        event_log_window.show()


def test_open_for_events_re_runs_row_visibility_pass(event_log_window):
    """Cross-empire reuse via ``open_for_events`` must still re-assert
    the row-pool visibility after the show cascade. Independent of the
    base ``show()`` hook so the data-rebind path is covered.
    """
    new_events = [{"category": "production", "turn": 5}]

    with patch.object(event_log_window, "show"):
        event_log_window.open_for_events(new_events, empire_name="Test")

    # _rebuild_list (post-show) is part of open_for_events' contract and
    # always pushes through force_update + update_visible_rows.
    event_log_window.virtual_table.force_update.assert_called()
    event_log_window.virtual_table.update_visible_rows.assert_called()


# ---------------------------------------------------------------------------
# Test 2 — PlanetListWindow.show() re-runs the row-pool visibility pass.
# ---------------------------------------------------------------------------


@pytest.fixture
def planet_list_window():
    from game.ui.screens.planet_list_window import PlanetListWindow

    with bypass_init(PlanetListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        empire = MagicMock(name="empire")
        empire.id = 0
        window_manager = MagicMock(name="window_manager")
        window = PlanetListWindow(
            rect, manager, galaxy, empire,
            window_manager=window_manager,
        )
        window.is_blocking = True
        window.virtual_table = MagicMock(name="virtual_table")
        return window


def test_planet_list_show_reasserts_row_visibility_after_cascade(planet_list_window):
    with patch("pygame_gui.elements.UIWindow.show"), \
         patch("pygame_gui.elements.UIWindow.hide"):
        planet_list_window.hide()
        planet_list_window.virtual_table.reset_mock()
        planet_list_window.show()

    planet_list_window.virtual_table.force_update.assert_called()
    planet_list_window.virtual_table.update_visible_rows.assert_called()


# ---------------------------------------------------------------------------
# Test 3 — StarListWindow.show() re-runs the row-pool visibility pass.
# ---------------------------------------------------------------------------


@pytest.fixture
def star_list_window():
    from game.ui.screens.star_list_window import StarListWindow

    with bypass_init(StarListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        window_manager = MagicMock(name="window_manager")
        window = StarListWindow(
            rect, manager, galaxy,
            window_manager=window_manager,
        )
        window.is_blocking = True
        window.virtual_table = MagicMock(name="virtual_table")
        return window


def test_star_list_show_reasserts_row_visibility_after_cascade(star_list_window):
    with patch("pygame_gui.elements.UIWindow.show"), \
         patch("pygame_gui.elements.UIWindow.hide"):
        star_list_window.hide()
        star_list_window.virtual_table.reset_mock()
        star_list_window.show()

    star_list_window.virtual_table.force_update.assert_called()
    star_list_window.virtual_table.update_visible_rows.assert_called()


# ---------------------------------------------------------------------------
# Test 4 — base class ``_post_show_hook`` default is a no-op.
# ---------------------------------------------------------------------------


def test_strategy_modal_window_default_post_show_hook_is_no_op():
    """The base hook must be a safe default for subclasses that don't
    own a VirtualTable (e.g. EmpirePanelWindow, BuildQueueListWindow)."""
    from game.ui.screens.strategy_modal_window import StrategyModalWindow

    assert hasattr(StrategyModalWindow, "_post_show_hook")
    # Construct via bypass-init style — we just need the method to exist
    # and return None when invoked on a minimal instance.
    instance = StrategyModalWindow.__new__(StrategyModalWindow)
    assert instance._post_show_hook() is None
