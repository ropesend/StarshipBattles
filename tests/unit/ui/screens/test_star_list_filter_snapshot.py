"""PROJ-411 Task 2.10: Per-empire filter snapshots for StarListWindow.

Mirrors the PlanetListWindow snapshot tests. StarListWindow previously
took only ``galaxy`` in ``open_for_galaxy``; this task adds an
``empire`` argument so the registrar can drive per-empire snapshots.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.star_list_window import StarListWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def window_with_two_empires():
    with bypass_init(StarListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        empire_a = MagicMock(name="empire_a")
        empire_a.id = 0
        window_manager = MagicMock(name="window_manager")
        window = StarListWindow(
            rect, manager, galaxy,
            window_manager=window_manager,
            empire=empire_a,
        )
        window.virtual_table = MagicMock(name="virtual_table")
        window.txt_name_filter = MagicMock(name="txt_name_filter")
        window.ui_filters = {}
        window._default_filter_snapshot = {"default": "stub"}
        return window


def test_init_initializes_per_empire_snapshot_bookkeeping():
    with bypass_init(StarListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        empire = MagicMock(name="empire")
        empire.id = 0
        wm = MagicMock(name="window_manager")
        window = StarListWindow(
            rect, manager, galaxy, window_manager=wm, empire=empire
        )
    assert hasattr(window, "_filter_snapshots_by_empire")
    assert window._filter_snapshots_by_empire == {}
    assert window.empire is empire


def test_open_for_galaxy_saves_outgoing_empire_snapshot_on_switch(
    window_with_two_empires,
):
    window = window_with_two_empires
    empire_b = MagicMock(name="empire_b")
    empire_b.id = 1
    captured_snapshot = {"types": {"Main Sequence": False}}

    with patch(
        "game.ui.screens.star_list_window.capture_star_list_state",
        return_value=captured_snapshot,
    ) as mock_capture, patch(
        "game.ui.screens.star_list_window.apply_star_list_state",
        return_value=window.columns,
    ), patch.object(window, "show"), patch.object(window, "refresh_list"):
        window.open_for_galaxy(window.galaxy, empire_b)

    assert window._filter_snapshots_by_empire[0] is captured_snapshot
    mock_capture.assert_called_once()


def test_open_for_galaxy_restores_incoming_empire_saved_snapshot(
    window_with_two_empires,
):
    window = window_with_two_empires
    empire_b = MagicMock(name="empire_b")
    empire_b.id = 1
    saved_b_snapshot = {"types": {"Red Giant": False}, "marker": "b_state"}
    window._filter_snapshots_by_empire[1] = saved_b_snapshot

    with patch(
        "game.ui.screens.star_list_window.capture_star_list_state",
        return_value={"outgoing": "a"},
    ), patch(
        "game.ui.screens.star_list_window.apply_star_list_state",
        return_value=window.columns,
    ) as mock_apply, patch.object(window, "show"), patch.object(
        window, "refresh_list"
    ):
        window.open_for_galaxy(window.galaxy, empire_b)

    assert mock_apply.called
    applied_state = mock_apply.call_args.args[0]
    assert applied_state is saved_b_snapshot


def test_open_for_galaxy_new_empire_first_time_applies_defaults(
    window_with_two_empires,
):
    window = window_with_two_empires
    empire_b = MagicMock(name="empire_b")
    empire_b.id = 1
    assert 1 not in window._filter_snapshots_by_empire

    with patch(
        "game.ui.screens.star_list_window.capture_star_list_state",
        return_value={"outgoing": "a"},
    ), patch(
        "game.ui.screens.star_list_window.apply_star_list_state",
        return_value=window.columns,
    ) as mock_apply, patch.object(window, "show"), patch.object(
        window, "refresh_list"
    ):
        window.open_for_galaxy(window.galaxy, empire_b)

    applied_state = mock_apply.call_args.args[0]
    assert applied_state is window._default_filter_snapshot


def test_open_for_galaxy_same_empire_does_not_capture_or_apply(
    window_with_two_empires,
):
    window = window_with_two_empires
    same_empire = window.empire

    with patch(
        "game.ui.screens.star_list_window.capture_star_list_state",
    ) as mock_capture, patch(
        "game.ui.screens.star_list_window.apply_star_list_state",
    ) as mock_apply, patch.object(window, "show"), patch.object(
        window, "refresh_list"
    ):
        window.open_for_galaxy(window.galaxy, same_empire)

    mock_capture.assert_not_called()
    mock_apply.assert_not_called()
