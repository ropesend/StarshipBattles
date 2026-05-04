"""
Unit tests for basic pathfinding: deep space, system location, interstellar, hex distance.
"""

import pytest
from unittest.mock import MagicMock

from game.strategy.data.pathfinding import (
    find_path_deep_space,
    find_path_interstellar,
    get_system_at_hex,
    find_nearest_system,
)
from game.core.hex_math import HexCoord, hex_distance


# =============================================================================
# Test: Deep Space Path Finding
# =============================================================================


class TestDeepSpacePath:
    """Tests for find_path_deep_space function."""

    def test_same_location_returns_single_hex(self, origin):
        """Path from A to A returns just [A]."""
        path = find_path_deep_space(origin, origin)

        assert len(path) == 1
        assert path[0] == origin

    def test_adjacent_hex_returns_two_points(self, origin):
        """Path to adjacent hex returns start and end."""
        target = HexCoord(1, 0)

        path = find_path_deep_space(origin, target)

        assert len(path) == 2
        assert path[0] == origin
        assert path[1] == target

    def test_straight_line_correct_length(self, origin, nearby_hex):
        """Path length equals hex distance + 1."""
        path = find_path_deep_space(origin, nearby_hex)
        expected_length = hex_distance(origin, nearby_hex) + 1

        assert len(path) == expected_length

    def test_path_starts_at_origin(self, origin, distant_hex):
        """Path always starts at origin."""
        path = find_path_deep_space(origin, distant_hex)

        assert path[0] == origin

    def test_path_ends_at_destination(self, origin, distant_hex):
        """Path always ends at destination."""
        path = find_path_deep_space(origin, distant_hex)

        assert path[-1] == distant_hex

    def test_path_is_contiguous(self, origin, distant_hex):
        """Each step in path is adjacent to the next."""
        path = find_path_deep_space(origin, distant_hex)

        for i in range(len(path) - 1):
            dist = hex_distance(path[i], path[i + 1])
            assert dist == 1, f"Gap between {path[i]} and {path[i+1]}"

    def test_diagonal_path(self):
        """Path works for diagonal movement."""
        start = HexCoord(0, 0)
        end = HexCoord(5, 5)

        path = find_path_deep_space(start, end)

        assert path[0] == start
        assert path[-1] == end
        # Path should be contiguous
        for i in range(len(path) - 1):
            assert hex_distance(path[i], path[i + 1]) == 1

    def test_negative_coordinates(self):
        """Path works with negative coordinates."""
        start = HexCoord(-10, -5)
        end = HexCoord(-5, 0)

        path = find_path_deep_space(start, end)

        assert path[0] == start
        assert path[-1] == end

    def test_returns_list_of_hexcoords(self, origin, nearby_hex):
        """Path contains HexCoord objects."""
        path = find_path_deep_space(origin, nearby_hex)

        for point in path:
            assert isinstance(point, HexCoord)


# =============================================================================
# Test: System Location Functions
# =============================================================================


class TestSystemLocation:
    """Tests for get_system_at_hex and find_nearest_system."""

    def test_get_system_at_exact_location(self, mock_galaxy):
        """get_system_at_hex returns system at exact coordinates."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        result = get_system_at_hex(galaxy, HexCoord(0, 0))

        assert result == sys_a

    def test_get_system_at_hex_nearby(self, mock_galaxy):
        """get_system_at_hex finds system within radius."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Within default radius of 50
        result = get_system_at_hex(galaxy, HexCoord(10, 0), radius=50)

        assert result == sys_a

    def test_get_system_at_hex_outside_radius(self, mock_galaxy):
        """get_system_at_hex returns None if outside radius."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Outside small radius
        result = get_system_at_hex(galaxy, HexCoord(25, 0), radius=10)

        assert result is None

    def test_get_system_chooses_closest(self, mock_galaxy):
        """When multiple systems in radius, chooses closest."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Hex at (40, 0) is closer to Beta (50, 0) than Alpha (0, 0)
        result = get_system_at_hex(galaxy, HexCoord(40, 0), radius=60)

        assert result == sys_b

    def test_find_nearest_system_always_finds_one(self, mock_galaxy):
        """find_nearest_system finds system regardless of distance."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Very far from all systems
        result = find_nearest_system(galaxy, HexCoord(1000, 1000))

        assert result is not None

    def test_find_nearest_system_chooses_closest(self, mock_galaxy):
        """find_nearest_system returns the closest system."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Closer to Gamma
        result = find_nearest_system(galaxy, HexCoord(90, 0))

        assert result == sys_c

    def test_find_nearest_system_empty_galaxy(self):
        """find_nearest_system handles empty galaxy."""
        galaxy = MagicMock()
        galaxy.systems = {}

        result = find_nearest_system(galaxy, HexCoord(0, 0))

        assert result is None


# =============================================================================
# Test: Interstellar Pathfinding
# =============================================================================


class TestInterstellarPath:
    """Tests for find_path_interstellar (A* on warp lane network)."""

    def test_same_system_returns_single_system(self, mock_galaxy):
        """Path from system to itself returns [system]."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        path = find_path_interstellar(sys_a, sys_a, galaxy)

        assert path == [sys_a]

    def test_adjacent_systems_path(self, mock_galaxy):
        """Path between directly connected systems."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        path = find_path_interstellar(sys_a, sys_b, galaxy)

        assert path is not None
        assert len(path) == 2
        assert path[0] == sys_a
        assert path[1] == sys_b

    def test_multi_hop_path(self, mock_galaxy):
        """Path through multiple systems (A -> B -> C)."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        path = find_path_interstellar(sys_a, sys_c, galaxy)

        assert path is not None
        assert len(path) == 3
        assert path[0] == sys_a
        assert path[1] == sys_b
        assert path[2] == sys_c

    def test_disconnected_systems_returns_none(self, mock_galaxy):
        """Returns None when systems are not connected."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Add isolated system
        sys_isolated = MagicMock()
        sys_isolated.name = "Isolated"
        sys_isolated.global_location = HexCoord(500, 500)
        sys_isolated.warp_points = []
        galaxy.systems[HexCoord(500, 500)] = sys_isolated

        path = find_path_interstellar(sys_a, sys_isolated, galaxy)

        assert path is None

    def test_path_order_is_correct(self, mock_galaxy):
        """Path is in correct order from start to end."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        path = find_path_interstellar(sys_c, sys_a, galaxy)

        assert path is not None
        assert path[0] == sys_c
        assert path[-1] == sys_a


# =============================================================================
# Test: Hex Distance Helper
# =============================================================================


class TestHexDistanceIntegration:
    """Tests for hex_distance as used by pathfinding."""

    def test_same_hex_distance_zero(self):
        """Distance from hex to itself is zero."""
        h = HexCoord(5, 5)

        assert hex_distance(h, h) == 0

    def test_adjacent_hex_distance_one(self):
        """Distance to adjacent hex is one."""
        h1 = HexCoord(0, 0)
        h2 = HexCoord(1, 0)

        assert hex_distance(h1, h2) == 1

    def test_distance_symmetric(self):
        """Distance is same in both directions."""
        h1 = HexCoord(0, 0)
        h2 = HexCoord(10, 5)

        assert hex_distance(h1, h2) == hex_distance(h2, h1)

    def test_diagonal_distance(self):
        """Diagonal movement uses correct hex distance formula."""
        h1 = HexCoord(0, 0)
        h2 = HexCoord(3, 3)

        # In hex grid, diagonal movement is more expensive
        dist = hex_distance(h1, h2)
        assert dist == 6  # max(|3|, |3|, |-6|) = 6


# =============================================================================
# PROJ-334: Deep Space Path Symmetry (gap-fill)
# =============================================================================


class TestDeepSpacePathSymmetry:
    """PROJ-334: pin reversed-endpoint symmetry for find_path_deep_space."""

    def test_find_path_deep_space_path_is_symmetric_for_reversed_endpoints(self):
        """Reversing the endpoints reverses the path; lengths are identical."""
        a = HexCoord(0, 0)
        b = HexCoord(7, 4)

        forward = find_path_deep_space(a, b)
        backward = find_path_deep_space(b, a)

        assert len(forward) == len(backward)
        assert forward[0] == a and forward[-1] == b
        assert backward[0] == b and backward[-1] == a


# =============================================================================
# PROJ-334: Interstellar A* Cost Optimality (gap-fill)
# =============================================================================


class TestInterstellarPathCostOptimality:
    """PROJ-334: pin lower-distance route choice in a diamond warp graph."""

    def test_find_path_interstellar_chooses_lower_distance_route_when_two_paths_exist(self):
        """Diamond graph: A->B->D (short) vs A->C->D (long). A* picks the short route."""
        sys_a = MagicMock()
        sys_a.name = "A"
        sys_a.global_location = HexCoord(0, 0)

        sys_b = MagicMock()
        sys_b.name = "B"
        sys_b.global_location = HexCoord(10, 0)  # 10 from A

        sys_c = MagicMock()
        sys_c.name = "C"
        sys_c.global_location = HexCoord(0, 50)  # 50 from A — long detour

        sys_d = MagicMock()
        sys_d.name = "D"
        sys_d.global_location = HexCoord(20, 0)  # 10 from B

        def _wp(dest):
            wp = MagicMock()
            wp.destination_id = dest
            wp.location = HexCoord(0, 0)
            return wp

        sys_a.warp_points = [_wp("B"), _wp("C")]
        sys_b.warp_points = [_wp("A"), _wp("D")]
        sys_c.warp_points = [_wp("D")]
        sys_d.warp_points = [_wp("B"), _wp("C")]

        galaxy = MagicMock()
        galaxy.systems = {
            sys_a.global_location: sys_a,
            sys_b.global_location: sys_b,
            sys_c.global_location: sys_c,
            sys_d.global_location: sys_d,
        }
        name_map = {"A": sys_a, "B": sys_b, "C": sys_c, "D": sys_d}
        galaxy.get_system_by_name = lambda n: name_map.get(n)

        path = find_path_interstellar(sys_a, sys_d, galaxy)

        assert path is not None
        names = [s.name for s in path]
        assert names == ["A", "B", "D"]
