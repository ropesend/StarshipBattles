"""PROJ-411 Task 2.5: Esc-close path uses ``request_close()`` so reusable
windows can hide() instead of kill().

The strategy event router's Esc handler routes to ``request_close()``
on the topmost live modal. Default ``StrategyModalWindow.request_close``
delegates to ``self.kill()`` (legacy contract). The four PROJ-411
reusable windows override ``request_close`` to call ``self.hide()``.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.empire_panel_window import EmpirePanelWindow
from game.ui.screens.event_log_window import EventLogWindow
from game.ui.screens.planet_list_window import PlanetListWindow
from game.ui.screens.star_list_window import StarListWindow
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from tests.fixtures.ui_widget_factory import bypass_init


def test_base_class_request_close_defaults_to_kill():
    """``StrategyModalWindow.request_close`` defaults to ``kill()``.

    Legacy modals get the legacy contract for free.
    """
    # Construct a bare StrategyModalWindow under bypass_init.
    with bypass_init(StrategyModalWindow):
        rect = pygame.Rect(0, 0, 100, 100)
        manager = MagicMock()
        win = StrategyModalWindow(rect, manager, window_manager=None)
    with patch.object(win, "kill") as mock_kill:
        win.request_close()
    mock_kill.assert_called_once()


@pytest.mark.parametrize(
    "window_cls",
    [PlanetListWindow, StarListWindow, EmpirePanelWindow, EventLogWindow],
    ids=lambda c: c.__name__,
)
def test_reusable_window_request_close_hides(window_cls):
    """Each of the four PROJ-411 reusable windows overrides
    ``request_close`` to call ``hide()`` instead of ``kill()``.
    """
    with bypass_init(window_cls):
        rect = pygame.Rect(0, 0, 100, 100)
        manager = MagicMock()
        if window_cls is PlanetListWindow:
            win = window_cls(rect, manager, MagicMock(), MagicMock(),
                             window_manager=None)
        elif window_cls is StarListWindow:
            win = window_cls(rect, manager, MagicMock(), window_manager=None)
        elif window_cls is EmpirePanelWindow:
            win = window_cls(rect, manager, MagicMock(), window_manager=None)
        else:  # EventLogWindow
            win = window_cls(rect, manager, [], window_manager=None)

    with patch.object(win, "hide") as mock_hide, \
         patch.object(win, "kill") as mock_kill:
        win.request_close()

    mock_hide.assert_called_once()
    mock_kill.assert_not_called()
