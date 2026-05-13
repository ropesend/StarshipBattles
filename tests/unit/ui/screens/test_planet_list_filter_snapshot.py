"""Issue #28: PlanetListWindow per-player UI view-state contract.

Replaces the PROJ-411 Task 2.10 per-window dict (``_filter_snapshots_by_empire``)
with a slot-based opt-in into ``PerPlayerUiState`` (owned by
``StrategyGameStateManager``). The window now exposes:

- ``SNAPSHOT_SLOT = "planet_list"`` — registry key.
- ``capture_view_state() -> dict`` — produces a saved-preset-shaped snapshot.
- ``apply_view_state(state)`` — restores; ``state is None`` falls back to the
  pristine ``_default_filter_snapshot`` captured at the end of Stage 3.

``open_for_galaxy`` no longer manages snapshots — the central manager swaps
state at turn rotation, not on next-open.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.planet_list_window import PlanetListWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def window():
    """Bypass-init PlanetListWindow with a stub default snapshot."""
    with bypass_init(PlanetListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        empire = MagicMock(name="empire")
        empire.id = 0
        wm = MagicMock(name="window_manager")
        w = PlanetListWindow(rect, manager, galaxy, empire, window_manager=wm)
        w.virtual_table = MagicMock(name="virtual_table")
        w.txt_name_filter = MagicMock(name="txt_name_filter")
        w.ui_filters = {}
        w._default_filter_snapshot = {"default": "stub"}
        return w


class TestSnapshotSlot:
    def test_class_constant_for_central_registry(self):
        assert PlanetListWindow.SNAPSHOT_SLOT == "planet_list"


class TestCaptureViewState:
    def test_delegates_to_preset_capture(self, window):
        captured = {"types": {"Continental": False}}
        with patch(
            "game.ui.screens.planet_list_window.capture_planet_list_state",
            return_value=captured,
        ) as mock_capture:
            result = window.capture_view_state()

        assert result is captured
        mock_capture.assert_called_once()


class TestApplyViewState:
    def test_applies_saved_state(self, window):
        saved = {"types": {"Barren": False}, "marker": "saved"}
        with patch(
            "game.ui.screens.planet_list_window.apply_planet_list_state",
            return_value=window.columns,
        ) as mock_apply:
            window.apply_view_state(saved)

        applied = mock_apply.call_args.args[0]
        assert applied is saved

    def test_none_falls_back_to_default_snapshot(self, window):
        with patch(
            "game.ui.screens.planet_list_window.apply_planet_list_state",
            return_value=window.columns,
        ) as mock_apply:
            window.apply_view_state(None)

        applied = mock_apply.call_args.args[0]
        assert applied is window._default_filter_snapshot

    def test_none_and_no_default_is_noop(self, window):
        window._default_filter_snapshot = None
        with patch(
            "game.ui.screens.planet_list_window.apply_planet_list_state",
        ) as mock_apply:
            window.apply_view_state(None)
        mock_apply.assert_not_called()


class TestOpenForGalaxyNoLongerHandlesSnapshots:
    def test_empire_switch_does_not_capture_or_apply(self, window):
        empire_b = MagicMock(name="empire_b")
        empire_b.id = 1

        with patch(
            "game.ui.screens.planet_list_window.capture_planet_list_state",
        ) as mock_capture, patch(
            "game.ui.screens.planet_list_window.apply_planet_list_state",
        ) as mock_apply, patch.object(window, "show"), patch.object(
            window, "refresh_list"
        ):
            window.open_for_galaxy(window.galaxy, empire_b)

        mock_capture.assert_not_called()
        mock_apply.assert_not_called()


class TestNoLegacyPerWindowDict:
    """Anti-reversion: the old per-window ``_filter_snapshots_by_empire``
    dict must not be reintroduced. Single source of truth is the central
    ``PerPlayerUiState`` container."""

    def test_legacy_attr_absent(self, window):
        assert not hasattr(window, "_filter_snapshots_by_empire")
