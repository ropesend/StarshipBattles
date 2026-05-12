"""PROJ-411 Task 2.10: Per-empire filter snapshots for PlanetListWindow.

Phase 2's window-reuse contract preserved filter / column / range state
across opens. That was correct for same-empire repeat lookups but
leaked across the hot-seat empire handoff — Player 2 saw Player 1's
filters and vice versa.

Fix: capture the outgoing empire's filter state on empire switch and
restore the incoming empire's previously-saved state (or defaults on
first sight). Uses the existing preset capture/apply infrastructure
(``capture_planet_list_state`` / ``apply_planet_list_state``) which
already handles the UI-widget sync for the filter dicts, search text,
columns, ranges, and effects.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.planet_list_window import PlanetListWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def window_with_two_empires():
    """Bypass-init PlanetListWindow with empire_a active + a default snapshot stub.

    The bypass-init path skips Stage 3 (UI builder), so the per-empire
    snapshot bookkeeping must work without real widgets. We attach a
    stub default snapshot to stand in for what production captures at
    the end of __init__.
    """
    with bypass_init(PlanetListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        empire_a = MagicMock(name="empire_a")
        empire_a.id = 0
        window_manager = MagicMock(name="window_manager")
        window = PlanetListWindow(
            rect, manager, galaxy, empire_a,
            window_manager=window_manager,
        )
        # Stage 3 wasn't run; stage-3 attrs are MagicMocks-by-default through
        # bypass_init's shell. Pre-populate the slots used by the snapshot path.
        window.virtual_table = MagicMock(name="virtual_table")
        window.txt_name_filter = MagicMock(name="txt_name_filter")
        window.ui_filters = {}
        window._default_filter_snapshot = {"default": "stub"}
        return window


def test_init_initializes_per_empire_snapshot_bookkeeping():
    """Construction sets up the per-empire snapshot dict + default slot."""
    with bypass_init(PlanetListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        empire = MagicMock(name="empire")
        empire.id = 0
        wm = MagicMock(name="window_manager")
        window = PlanetListWindow(rect, manager, galaxy, empire, window_manager=wm)
    assert hasattr(window, "_filter_snapshots_by_empire")
    assert window._filter_snapshots_by_empire == {}
    assert hasattr(window, "_default_filter_snapshot")


def test_open_for_galaxy_saves_outgoing_empire_snapshot_on_switch(
    window_with_two_empires,
):
    """Switching from empire A → empire B captures A's filter state."""
    window = window_with_two_empires
    empire_b = MagicMock(name="empire_b")
    empire_b.id = 1
    captured_snapshot = {"types": {"Continental": False}}

    with patch(
        "game.ui.screens.planet_list_window.capture_planet_list_state",
        return_value=captured_snapshot,
    ) as mock_capture, patch(
        "game.ui.screens.planet_list_window.apply_planet_list_state",
        return_value=window.columns,
    ), patch.object(window, "show"), patch.object(window, "refresh_list"):
        window.open_for_galaxy(window.galaxy, empire_b)

    assert window._filter_snapshots_by_empire[0] is captured_snapshot
    mock_capture.assert_called_once()


def test_open_for_galaxy_restores_incoming_empire_saved_snapshot(
    window_with_two_empires,
):
    """If the incoming empire has a saved snapshot, it is applied."""
    window = window_with_two_empires
    empire_b = MagicMock(name="empire_b")
    empire_b.id = 1
    saved_b_snapshot = {"types": {"Barren": False}, "marker": "b_state"}
    window._filter_snapshots_by_empire[1] = saved_b_snapshot

    with patch(
        "game.ui.screens.planet_list_window.capture_planet_list_state",
        return_value={"outgoing": "a"},
    ), patch(
        "game.ui.screens.planet_list_window.apply_planet_list_state",
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
    """First sight of a new empire applies the default snapshot, not A's state."""
    window = window_with_two_empires
    empire_b = MagicMock(name="empire_b")
    empire_b.id = 1
    # No snapshot for empire_b — default should be applied.
    assert 1 not in window._filter_snapshots_by_empire

    with patch(
        "game.ui.screens.planet_list_window.capture_planet_list_state",
        return_value={"outgoing": "a"},
    ), patch(
        "game.ui.screens.planet_list_window.apply_planet_list_state",
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
    """Re-opening for the same empire preserves filters in-place (no capture/apply)."""
    window = window_with_two_empires
    same_empire = window.empire

    with patch(
        "game.ui.screens.planet_list_window.capture_planet_list_state",
    ) as mock_capture, patch(
        "game.ui.screens.planet_list_window.apply_planet_list_state",
    ) as mock_apply, patch.object(window, "show"), patch.object(
        window, "refresh_list"
    ):
        window.open_for_galaxy(window.galaxy, same_empire)

    mock_capture.assert_not_called()
    mock_apply.assert_not_called()


def test_round_trip_a_to_b_to_a_restores_a_snapshot(window_with_two_empires):
    """A → B → A applies A's saved snapshot on return."""
    window = window_with_two_empires
    empire_a = window.empire
    empire_b = MagicMock(name="empire_b")
    empire_b.id = 1

    a_snapshot_holder = {}

    def capture_side_effect(*args, **kwargs):
        # Return a distinct dict each call so we can assert identity.
        snap = {"call_count": len(a_snapshot_holder), "args_len": len(args)}
        a_snapshot_holder[len(a_snapshot_holder)] = snap
        return snap

    with patch(
        "game.ui.screens.planet_list_window.capture_planet_list_state",
        side_effect=capture_side_effect,
    ), patch(
        "game.ui.screens.planet_list_window.apply_planet_list_state",
        return_value=window.columns,
    ) as mock_apply, patch.object(window, "show"), patch.object(
        window, "refresh_list"
    ):
        # A → B: capture A's state (snapshot_0) and save it under empire_a.id.
        window.open_for_galaxy(window.galaxy, empire_b)
        a_saved = window._filter_snapshots_by_empire[empire_a.id]
        # B → A: should apply a_saved.
        window.open_for_galaxy(window.galaxy, empire_a)

    # The second apply call should have been with A's saved snapshot.
    last_applied = mock_apply.call_args.args[0]
    assert last_applied is a_saved
