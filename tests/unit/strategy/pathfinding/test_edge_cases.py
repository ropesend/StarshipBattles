"""
Unit tests for pathfinding edge cases, path segments, and hex math integration.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.data.pathfinding import (
    find_path_deep_space,
    find_path_interstellar,
    find_hybrid_path,
    calculate_intercept_point,
)
from game.strategy.data.hex_math import HexCoord, hex_distance


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestPathfindingEdgeCases:
    """Edge case tests for pathfinding."""

    def test_very_long_path(self):
        """Very long deep space paths are handled."""
        start = HexCoord(0, 0)
        end = HexCoord(1000, 500)

        path = find_path_deep_space(start, end)

        assert path is not None
        assert path[0] == start
        assert path[-1] == end

    def test_negative_speed_fleet(self, mock_galaxy):
        """Negative speed handled gracefully."""
        galaxy, _, _, _ = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = -5.0  # Invalid

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(10, 0)

        result = calculate_intercept_point(chaser, target, galaxy)

        # Should return target location as fallback
        assert result == target.location

    def test_empty_galaxy_systems(self):
        """Hybrid path with empty galaxy uses deep space."""
        galaxy = MagicMock()
        galaxy.systems = {}

        start = HexCoord(0, 0)
        end = HexCoord(10, 10)

        path = find_hybrid_path(galaxy, start, end)

        assert path is not None
        assert path[0] == start
        assert path[-1] == end

    def test_fleet_without_can_use_warp_method(self, mock_galaxy):
        """Fleet object without can_use_warp attribute works."""
        galaxy, _, _, _ = mock_galaxy

        fleet = MagicMock(spec=[])  # No methods
        fleet.location = HexCoord(0, 0)

        start = HexCoord(0, 0)
        end = HexCoord(10, 10)

        # Should not raise
        path = find_hybrid_path(galaxy, start, end, fleet=fleet)

        assert path is not None

    def test_galaxy_with_no_warp_points(self):
        """Systems with no warp points still work."""
        galaxy = MagicMock()

        sys_a = MagicMock()
        sys_a.name = "Alpha"
        sys_a.global_location = HexCoord(0, 0)
        sys_a.warp_points = []

        sys_b = MagicMock()
        sys_b.name = "Beta"
        sys_b.global_location = HexCoord(100, 0)
        sys_b.warp_points = []

        galaxy.systems = {
            HexCoord(0, 0): sys_a,
            HexCoord(100, 0): sys_b,
        }
        galaxy.get_system_by_name = lambda n: sys_a if n == "Alpha" else sys_b if n == "Beta" else None

        # No warp connection - interstellar should return None
        path = find_path_interstellar(sys_a, sys_b, galaxy)

        assert path is None


# =============================================================================
# Test: Path Segment Calculations
# =============================================================================


class TestPathSegments:
    """Tests for path segment calculations used in hybrid routing."""

    def test_warp_point_global_location(self, mock_galaxy):
        """Warp point global location calculated correctly."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # sys_a at (0, 0) has warp point with local coords (5, 0)
        wp = sys_a.warp_points[0]
        global_wp_loc = sys_a.global_location + wp.location

        assert global_wp_loc == HexCoord(5, 0)

    def test_path_includes_warp_arrival(self, mock_galaxy):
        """Hybrid path includes arrival point after warp."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Fleet at Alpha, wants to reach Gamma via Beta
        fleet = MagicMock()
        fleet.can_use_warp = MagicMock(return_value=True)

        start = HexCoord(0, 0)
        end = HexCoord(100, 0)

        path = find_hybrid_path(galaxy, start, end, fleet=fleet)

        assert path is not None
        # Path should contain hexes from multiple systems


# =============================================================================
# Test: Integration with Real Hex Distance
# =============================================================================


class TestPathfindingWithHexMath:
    """Integration tests combining pathfinding with hex math."""

    def test_path_length_matches_hex_distance(self):
        """Deep space path length equals hex distance + 1."""
        start = HexCoord(10, 20)
        end = HexCoord(30, 40)

        path = find_path_deep_space(start, end)
        expected_steps = hex_distance(start, end)

        # Path includes start point
        assert len(path) == expected_steps + 1

    def test_all_path_steps_are_adjacent(self):
        """Every consecutive pair in path is adjacent."""
        start = HexCoord(0, 0)
        end = HexCoord(20, 15)

        path = find_path_deep_space(start, end)

        for i in range(len(path) - 1):
            dist = hex_distance(path[i], path[i + 1])
            assert dist == 1

    def test_path_never_backtracks(self):
        """Path never increases distance to goal."""
        start = HexCoord(0, 0)
        end = HexCoord(10, 10)

        path = find_path_deep_space(start, end)

        prev_dist = hex_distance(start, end)
        for point in path[1:]:
            curr_dist = hex_distance(point, end)
            assert curr_dist <= prev_dist
            prev_dist = curr_dist
