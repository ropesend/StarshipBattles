"""Tests for ``FleetNavigationService.invalidate_paths_for_graph_change`` (#31).

Broadcast helper used by warp-graph mutation handlers (OPEN_WARP_POINT,
CLOSE_WARP_POINT) to clear stale baked-in paths so the next movement
tick re-pathfinds against the updated graph.
"""
from __future__ import annotations

from types import SimpleNamespace

from game.core.hex_math import HexCoord
from game.strategy.services.fleet_navigation_service import FleetNavigationService


def _fleet(path):
    """Minimal Fleet-shaped object exposing the ``path`` attribute."""
    return SimpleNamespace(path=list(path))


def _empire(fleets):
    return SimpleNamespace(fleets=list(fleets))


class TestInvalidatePathsForGraphChange:
    def test_clears_paths_for_fleets_with_baked_in_path(self):
        f1 = _fleet([HexCoord(1, 1), HexCoord(2, 2)])
        f2 = _fleet([HexCoord(5, 5)])
        empires = [_empire([f1, f2])]
        svc = FleetNavigationService()

        svc.invalidate_paths_for_graph_change(empires)

        assert f1.path == []
        assert f2.path == []

    def test_leaves_fleets_without_paths_untouched(self):
        f_no_path = _fleet([])
        empires = [_empire([f_no_path])]
        svc = FleetNavigationService()

        svc.invalidate_paths_for_graph_change(empires)

        assert f_no_path.path == []

    def test_iterates_across_multiple_empires(self):
        f1 = _fleet([HexCoord(1, 1)])
        f2 = _fleet([HexCoord(2, 2)])
        empires = [_empire([f1]), _empire([f2])]
        svc = FleetNavigationService()

        svc.invalidate_paths_for_graph_change(empires)

        assert f1.path == []
        assert f2.path == []

    def test_empty_empires_list_is_safe(self):
        """Defensive: handler may pass [] when wired without an empires list."""
        svc = FleetNavigationService()

        # Should not raise.
        svc.invalidate_paths_for_graph_change([])
