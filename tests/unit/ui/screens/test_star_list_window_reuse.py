"""PROJ-411 Task 2.2: Window reuse contract for StarListWindow.

Same shape as Task 2.1 (PlanetListWindow). The Star Registry doesn't
bind to a per-empire view, so ``open_for_galaxy(galaxy)`` takes only
the galaxy argument.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.star_list_window import StarListWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def reusable_window():
    with bypass_init(StarListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="world_v1")
        # PROJ-477 Phase 4: StarListWindow takes the scene.world seam.
        galaxy.iter_systems.side_effect = lambda: iter(())
        window_manager = MagicMock(name="window_manager")
        window = StarListWindow(
            rect, manager, galaxy, window_manager=window_manager
        )
        window.virtual_table = MagicMock(name="virtual_table")
        window.selected_star = MagicMock(name="prev_selected_star")
        window.is_blocking = True
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


def test_open_for_galaxy_rebinds_galaxy(reusable_window):
    new_galaxy = MagicMock(name="world_v2")
    new_galaxy.iter_systems.side_effect = lambda: iter(())
    with patch.object(reusable_window, "show"), \
         patch.object(reusable_window, "refresh_list"):
        reusable_window.open_for_galaxy(new_galaxy)
    assert reusable_window.world is new_galaxy


def test_open_for_galaxy_resets_selection(reusable_window):
    new_galaxy = MagicMock()
    with patch.object(reusable_window, "show"), \
         patch.object(reusable_window, "refresh_list"):
        reusable_window.open_for_galaxy(new_galaxy)
    assert reusable_window.selected_star is None


def test_open_for_galaxy_calls_show_and_refresh(reusable_window):
    new_galaxy = MagicMock()
    with patch.object(reusable_window, "show") as mock_show, \
         patch.object(reusable_window, "refresh_list") as mock_refresh:
        reusable_window.open_for_galaxy(new_galaxy)
    mock_show.assert_called_once()
    mock_refresh.assert_called_once()
