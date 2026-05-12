"""PROJ-411 Task 1.8: Empire Overview lazy asset loading.

On panel open, only the Treasury tab content is built (the default tab).
Population content (including expensive portrait + flag pygame.image.load)
is deferred to first Population-tab selection. Idempotency flag prevents
re-builds on subsequent tab toggles.

These tests use direct method calls on a bypass-init'd EmpirePanelWindow
to avoid the full pygame_gui widget tree.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.empire_panel_window import EmpirePanelWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def bypassed_window():
    """An EmpirePanelWindow constructed via bypass_init so we can poke at
    its lazy-load state without instantiating the full widget tree.
    """
    with bypass_init(EmpirePanelWindow):
        empire = MagicMock()
        empire.id = 0
        empire.portrait_id = "qs_default"
        empire.flag_id = "qs_default"
        empire.colonies = []
        empire.race_config = MagicMock()
        empire.race_config.portrait_id = "qs_default"
        empire.race_config.flag_id = "qs_default"
        rect = pygame.Rect(0, 0, 800, 600)
        manager = MagicMock()
        window = EmpirePanelWindow(
            rect, manager, empire, window_manager=None
        )
        return window


def test_population_tab_not_built_on_open(bypassed_window) -> None:
    """``_population_tab_built`` flag is False after construction."""
    assert getattr(bypassed_window, "_population_tab_built", None) is False


def test_population_tab_marked_built_after_first_show(bypassed_window) -> None:
    """After ``_show_tab`` triggers Population, ``_population_tab_built`` is True."""
    # Simulate production-mode init so the lazy-build path is not skipped
    # by the test-only bypass guard.
    bypassed_window._window_init_bypassed = False
    # Stub the heavy builder so we only test the flag transition.
    with patch.object(bypassed_window, "_build_population_tab") as mock_build:
        bypassed_window.step_panels = [MagicMock(), MagicMock(), MagicMock()]
        bypassed_window.tab_buttons = [MagicMock(), MagicMock(), MagicMock()]
        bypassed_window._show_tab(1)  # TAB_POPULATION

    assert bypassed_window._population_tab_built is True
    assert mock_build.call_count == 1


def test_population_tab_not_rebuilt_on_second_show(bypassed_window) -> None:
    """Subsequent Population-tab shows skip the build step."""
    bypassed_window._window_init_bypassed = False
    with patch.object(bypassed_window, "_build_population_tab") as mock_build:
        bypassed_window.step_panels = [MagicMock(), MagicMock(), MagicMock()]
        bypassed_window.tab_buttons = [MagicMock(), MagicMock(), MagicMock()]
        bypassed_window._show_tab(1)  # first show
        bypassed_window._show_tab(0)  # switch away
        bypassed_window._show_tab(1)  # back to Population

    assert mock_build.call_count == 1, (
        f"_build_population_tab should be called exactly once across "
        f"multiple Population-tab shows; got {mock_build.call_count}"
    )


def test_show_tab_makes_population_panel_visible_before_lazy_build(
    bypassed_window,
) -> None:
    """Regression for AttributeError: 'UIScrollingContainer' object has no
    attribute 'vert_scroll_bar'.

    Adding a ``UIScrollingContainer`` to a hidden parent triggers pygame_gui's
    ``UIContainer.add_element`` → ``child.hide()`` path, which crashes because
    ``UIScrollingContainer.hide()`` accesses ``self.vert_scroll_bar`` before
    ``__init__`` has assigned it. The lazy-build path must therefore run only
    after the target panel has been shown.
    """
    bypassed_window._window_init_bypassed = False

    call_order: list[str] = []
    panels = [MagicMock(name=f"panel_{i}") for i in range(3)]
    panels[1].show.side_effect = lambda: call_order.append("show")
    panels[1].hide.side_effect = lambda: call_order.append("hide_population")

    with patch.object(
        bypassed_window,
        "_build_population_tab",
        side_effect=lambda *_a, **_k: call_order.append("build"),
    ):
        bypassed_window.step_panels = panels
        bypassed_window.tab_buttons = [MagicMock(), MagicMock(), MagicMock()]
        bypassed_window._show_tab(1)  # TAB_POPULATION

    assert "show" in call_order and "build" in call_order, call_order
    assert call_order.index("show") < call_order.index("build"), (
        f"Population panel must be shown before _build_population_tab runs, "
        f"otherwise UIScrollingContainer is added to a hidden parent and "
        f"crashes during __init__. Observed order: {call_order}"
    )
    assert "hide_population" not in call_order, (
        f"Population panel must not be hidden during a show-Population call; "
        f"observed order: {call_order}"
    )
