"""PROJ-411 Task 2.4: Window reuse contract for EventLogWindow.

``open_for_events(events, empire_name=None)`` rebinds the events list,
resets filter to ``"all"``, updates the data source, and shows the window.
Used by the registrar's reuse path so re-opens skip the ~2.5 s
widget-construction cost.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.event_log_window import EventLogWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def reusable_window():
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
        # Pretend the user had set a non-default filter under the previous open.
        window.current_filter = "production"
        return window


def test_close_button_hides_instead_of_killing(reusable_window):
    with patch.object(reusable_window, "hide") as mock_hide:
        reusable_window.on_close_window_button_pressed()
    mock_hide.assert_called_once()


def test_hide_sets_is_blocking_false_and_unregisters(reusable_window):
    with patch("pygame_gui.elements.UIWindow.hide"):
        reusable_window.hide()
    assert reusable_window.is_blocking is False
    reusable_window._window_manager.unregister_modal.assert_called_once_with(
        reusable_window
    )


def test_show_sets_is_blocking_true_and_registers(reusable_window):
    with patch("pygame_gui.elements.UIWindow.hide"), \
         patch("pygame_gui.elements.UIWindow.show"):
        reusable_window.hide()
        reusable_window._window_manager.reset_mock()
        reusable_window.show()
    assert reusable_window.is_blocking is True
    reusable_window._window_manager.register_modal.assert_called_once_with(
        reusable_window
    )


def test_open_for_events_rebinds_events(reusable_window):
    new_events = [{"category": "combat", "turn": 2, "message": "fresh"}]
    with patch.object(reusable_window, "show"), \
         patch.object(reusable_window, "_rebuild_list"):
        reusable_window.open_for_events(new_events)
    assert reusable_window.all_events is new_events


def test_open_for_events_resets_filter_to_all(reusable_window):
    reusable_window.current_filter = "production"
    with patch.object(reusable_window, "show"), \
         patch.object(reusable_window, "_rebuild_list"):
        reusable_window.open_for_events([])
    assert reusable_window.current_filter == "all"


def test_open_for_events_updates_data_source(reusable_window):
    new_events = [{"category": "combat", "turn": 2}]
    with patch.object(reusable_window, "show"), \
         patch.object(reusable_window, "_rebuild_list"):
        reusable_window.open_for_events(new_events)
    reusable_window.data_source.update_events.assert_called_once_with(new_events)


def test_open_for_events_calls_show_and_rebuild(reusable_window):
    with patch.object(reusable_window, "show") as mock_show, \
         patch.object(reusable_window, "_rebuild_list") as mock_rebuild:
        reusable_window.open_for_events([])
    mock_show.assert_called_once()
    mock_rebuild.assert_called_once()
