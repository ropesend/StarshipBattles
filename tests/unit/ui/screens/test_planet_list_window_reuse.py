"""PROJ-411 Task 2.1: Window reuse contract for PlanetListWindow.

The X-button close path calls ``hide()`` (preserving the instance for
reuse). The ``open_for_galaxy()`` method rebinds galaxy/empire/facade
context and resets per-open state. The window manager registers the
modal on ``show()`` and unregisters on ``hide()`` so background UI is
not blocked while the window is hidden.

Mirrors the PROJ-376 BuildQueueScreen pattern.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.planet_list_window import PlanetListWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def reusable_window():
    """Construct a PlanetListWindow via bypass_init for reuse-contract tests.

    We attach a MagicMock window_manager so ``register_modal`` /
    ``unregister_modal`` calls can be asserted.
    """
    with bypass_init(PlanetListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy_v1")
        empire = MagicMock(name="empire_v1")
        empire.id = 0
        window_manager = MagicMock(name="window_manager")
        window = PlanetListWindow(
            rect, manager, galaxy, empire,
            window_manager=window_manager,
        )
        # Stage 3 didn't run; pre-populate the slots the production
        # builder would have filled so show()/hide()/open_for_galaxy
        # don't AttributeError.
        window.virtual_table = MagicMock(name="virtual_table")
        window.planet_detail_panel = None
        window.btn_build_queue = None
        window.btn_navigate = None
        window.selected_planet = MagicMock(name="prev_selected_planet")
        window._search_text = "previously typed search"
        window.is_blocking = True
        # Avoid pygame_gui's hide()/show() — exercise our override only.
        # The real super().show()/hide() requires a real UI tree.
        window._called_super_show = 0
        window._called_super_hide = 0
        return window


def test_close_button_hides_instead_of_killing(reusable_window):
    """Override of ``on_close_window_button_pressed`` calls ``hide()``."""
    with patch.object(reusable_window, "hide") as mock_hide:
        reusable_window.on_close_window_button_pressed()
    mock_hide.assert_called_once()


def test_hide_sets_is_blocking_false_and_unregisters(reusable_window):
    """``hide()`` flips is_blocking to False and unregisters from modal manager."""
    # Stub the pygame_gui super().hide() — it needs real UI structure.
    with patch("pygame_gui.elements.UIWindow.hide"):
        reusable_window.hide()
    assert reusable_window.is_blocking is False
    reusable_window._window_manager.unregister_modal.assert_called_once_with(
        reusable_window
    )


def test_show_sets_is_blocking_true_and_registers(reusable_window):
    """``show()`` after ``hide()`` flips is_blocking back and re-registers."""
    with patch("pygame_gui.elements.UIWindow.hide"), \
         patch("pygame_gui.elements.UIWindow.show"):
        reusable_window.hide()
        reusable_window._window_manager.reset_mock()
        reusable_window.show()
    assert reusable_window.is_blocking is True
    reusable_window._window_manager.register_modal.assert_called_once_with(
        reusable_window
    )


def test_open_for_galaxy_rebinds_context(reusable_window):
    """``open_for_galaxy`` rebinds galaxy/empire/facade."""
    new_galaxy = MagicMock(name="galaxy_v2")
    new_empire = MagicMock(name="empire_v2")
    new_empire.id = 1
    new_facade = MagicMock(name="facade_v2")
    with patch("pygame_gui.elements.UIWindow.show"), \
         patch.object(reusable_window, "refresh_list"):
        reusable_window.open_for_galaxy(
            new_galaxy, new_empire, facade=new_facade
        )
    assert reusable_window.galaxy is new_galaxy
    assert reusable_window.empire is new_empire
    assert reusable_window._facade is new_facade


def test_open_for_galaxy_resets_per_open_state(reusable_window):
    """``open_for_galaxy`` clears selection so the new context starts clean."""
    new_galaxy = MagicMock()
    new_empire = MagicMock()
    new_empire.id = 1
    with patch("pygame_gui.elements.UIWindow.show"), \
         patch.object(reusable_window, "refresh_list"):
        reusable_window.open_for_galaxy(new_galaxy, new_empire)
    assert reusable_window.selected_planet is None


def test_open_for_galaxy_calls_show_and_refresh(reusable_window):
    """``open_for_galaxy`` calls ``show()`` and ``refresh_list()``."""
    new_galaxy = MagicMock()
    new_empire = MagicMock()
    new_empire.id = 1
    with patch.object(reusable_window, "show") as mock_show, \
         patch.object(reusable_window, "refresh_list") as mock_refresh:
        reusable_window.open_for_galaxy(new_galaxy, new_empire)
    mock_show.assert_called_once()
    mock_refresh.assert_called_once()
