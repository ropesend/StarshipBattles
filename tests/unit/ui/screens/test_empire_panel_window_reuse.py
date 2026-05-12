"""PROJ-411 Task 2.3: Window reuse contract for EmpirePanelWindow.

Scope is **same-empire** reuse only. Hot-seat case (different empire
on re-open) falls back to destroy+rebuild handled by the registrar —
the EmpirePanelWindow itself only knows how to hide/show its own
already-built content.

Mirrors Task 2.1 minus the context-rebinding (empire is fixed).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.empire_panel_window import (
    EmpirePanelWindow,
    TAB_TREASURY,
)
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def reusable_window():
    with bypass_init(EmpirePanelWindow):
        rect = pygame.Rect(0, 0, 1400, 800)
        manager = MagicMock(name="ui_manager")
        empire = MagicMock(name="empire_v1")
        empire.id = 0
        window_manager = MagicMock(name="window_manager")
        window = EmpirePanelWindow(
            rect, manager, empire,
            window_manager=window_manager,
        )
        window.is_blocking = True
        # Pretend Population tab was visited under this empire.
        window._population_tab_built = True
        window.current_tab = 1
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


def test_open_for_empire_resets_to_treasury_tab(reusable_window):
    """``open_for_empire`` resets ``current_tab`` to Treasury so re-open lands
    on the default tab regardless of the user's last viewed tab."""
    reusable_window.current_tab = 1  # Population from previous open
    reusable_window.step_panels = [MagicMock(), MagicMock(), MagicMock()]
    reusable_window.tab_buttons = [MagicMock(), MagicMock(), MagicMock()]
    with patch.object(reusable_window, "show"):
        reusable_window.open_for_empire(reusable_window.empire)
    assert reusable_window.current_tab == TAB_TREASURY


def test_open_for_empire_calls_show(reusable_window):
    """``open_for_empire`` calls ``show()``."""
    reusable_window.step_panels = [MagicMock(), MagicMock(), MagicMock()]
    reusable_window.tab_buttons = [MagicMock(), MagicMock(), MagicMock()]
    with patch.object(reusable_window, "show") as mock_show:
        reusable_window.open_for_empire(reusable_window.empire)
    mock_show.assert_called_once()
