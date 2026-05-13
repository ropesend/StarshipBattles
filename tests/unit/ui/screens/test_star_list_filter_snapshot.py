"""Issue #28: StarListWindow per-player UI view-state contract.

Replaces the PROJ-411 Task 2.10 per-window dict (``_filter_snapshots_by_empire``)
with a slot-based opt-in into ``PerPlayerUiState``. See
``test_planet_list_filter_snapshot.py`` for the design rationale; the
Star Registry uses ``SNAPSHOT_SLOT = "star_list"``.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.star_list_window import StarListWindow
from tests.fixtures.ui_widget_factory import bypass_init


@pytest.fixture
def window():
    with bypass_init(StarListWindow):
        rect = pygame.Rect(0, 0, 1600, 800)
        manager = MagicMock(name="ui_manager")
        galaxy = MagicMock(name="galaxy")
        empire = MagicMock(name="empire")
        empire.id = 0
        wm = MagicMock(name="window_manager")
        w = StarListWindow(rect, manager, galaxy, window_manager=wm, empire=empire)
        w.virtual_table = MagicMock(name="virtual_table")
        w.txt_name_filter = MagicMock(name="txt_name_filter")
        w.ui_filters = {}
        w._default_filter_snapshot = {"default": "stub"}
        return w


class TestSnapshotSlot:
    def test_class_constant(self):
        assert StarListWindow.SNAPSHOT_SLOT == "star_list"


class TestCaptureViewState:
    def test_delegates_to_preset_capture(self, window):
        captured = {"types": {"Yellow Dwarf": False}}
        with patch(
            "game.ui.screens.star_list_window.capture_star_list_state",
            return_value=captured,
        ) as mock_capture:
            result = window.capture_view_state()
        assert result is captured
        mock_capture.assert_called_once()


class TestApplyViewState:
    def test_applies_saved_state(self, window):
        saved = {"marker": "saved"}
        with patch(
            "game.ui.screens.star_list_window.apply_star_list_state",
            return_value=window.columns,
        ) as mock_apply:
            window.apply_view_state(saved)
        applied = mock_apply.call_args.args[0]
        assert applied is saved

    def test_none_falls_back_to_default_snapshot(self, window):
        with patch(
            "game.ui.screens.star_list_window.apply_star_list_state",
            return_value=window.columns,
        ) as mock_apply:
            window.apply_view_state(None)
        applied = mock_apply.call_args.args[0]
        assert applied is window._default_filter_snapshot

    def test_none_and_no_default_is_noop(self, window):
        window._default_filter_snapshot = None
        with patch(
            "game.ui.screens.star_list_window.apply_star_list_state",
        ) as mock_apply:
            window.apply_view_state(None)
        mock_apply.assert_not_called()


class TestOpenForGalaxyNoLongerHandlesSnapshots:
    def test_empire_switch_does_not_capture_or_apply(self, window):
        empire_b = MagicMock(name="empire_b")
        empire_b.id = 1
        with patch(
            "game.ui.screens.star_list_window.capture_star_list_state",
        ) as mock_capture, patch(
            "game.ui.screens.star_list_window.apply_star_list_state",
        ) as mock_apply, patch.object(window, "show"), patch.object(
            window, "refresh_list"
        ):
            window.open_for_galaxy(window.galaxy, empire_b)
        mock_capture.assert_not_called()
        mock_apply.assert_not_called()


class TestNoLegacyPerWindowDict:
    def test_legacy_attr_absent(self, window):
        assert not hasattr(window, "_filter_snapshots_by_empire")
