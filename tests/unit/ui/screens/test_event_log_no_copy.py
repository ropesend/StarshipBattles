"""PROJ-411 Task 1.9: EventLogWindow holds a reference to the events list,
not a defensive copy.

``facade.get_all_events()`` returns a freshly-built list per call
(``[e.to_dict() for e in events]``), so the window does not need its
own redundant ``list(events)`` copy. The data source still does its
own defensive copy at construction time — that's a separate boundary.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.screens.event_log_window import EventLogWindow
from tests.fixtures.ui_widget_factory import bypass_init


def test_window_holds_reference_to_events_list_not_copy() -> None:
    """``self.all_events`` is identity-equal to the input list."""
    events_input = [{"category": "combat", "turn": 1, "message": "test"}]
    with bypass_init(EventLogWindow):
        window = EventLogWindow(
            pygame.Rect(0, 0, 800, 600),
            MagicMock(name="manager"),
            events_input,
            window_manager=None,
        )
    assert window.all_events is events_input, (
        "PROJ-411 Task 1.9: EventLogWindow should hold a reference to the "
        "events list, not a redundant defensive copy. Source "
        "(facade.get_all_events) already returns a fresh per-call list."
    )
