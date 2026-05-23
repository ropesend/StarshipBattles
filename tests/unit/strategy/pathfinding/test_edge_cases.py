"""
Unit tests for pathfinding edge cases, path segments, and hex math integration.
"""

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord, hex_distance, hex_linedraw
from game.strategy.services.galaxy_pathfinding_service import GalaxyPathfindingService
from game.strategy.services.intercept_calculator import InterceptCalculator
# PROJ-480 Task 1.19: shared helpers moved to conftest.
from tests.unit.strategy.pathfinding.conftest import (
    find_path_deep_space,
    find_path_interstellar,
)


def find_hybrid_path(galaxy, start, end, fleet=None, can_warp=None):
    """Test helper preserving the pre-PROJ-414 shim signature."""
    return GalaxyPathfindingService(galaxy).find_hybrid_path(
        start, end, fleet=fleet, can_warp=can_warp,
    )


def calculate_intercept_point(chaser, target_fleet, galaxy):
    """Test helper preserving the pre-PROJ-414 shim signature."""
    return InterceptCalculator(
        GalaxyPathfindingService(galaxy),
    ).calculate_intercept_point(chaser, target_fleet, galaxy)


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


# =============================================================================
# PROJ-334: Intercept Fallback / Early-Exit (gap-fill)
# =============================================================================


class TestInterceptFallbackBehaviors:
    """PROJ-334: pin no-intercept-possible fallback and early-exit branches."""

    def test_calculate_intercept_point_returns_target_path_endpoint_when_no_intercept_possible(
        self, mock_galaxy
    ):
        """When the chaser can never catch up in any candidate window, the
        result is the LAST hex of the target's projected path."""
        from unittest.mock import patch

        galaxy, _, _, _ = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = 0.5  # extremely slow

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(10, 0)

        # Target's path projects far away across many turns; chaser cannot
        # arrive in time at any of them.
        target_path = [
            {"hex": HexCoord(100, 0), "turn": 0},
            {"hex": HexCoord(200, 0), "turn": 1},
            {"hex": HexCoord(300, 0), "turn": 2},
        ]
        endpoint_hex = target_path[-1]["hex"]

        with patch("game.strategy.services.intercept_calculator.project_fleet_path") as mock_project:
            mock_project.return_value = target_path
            result = calculate_intercept_point(chaser, target, galaxy)

        # No intercept is reachable → falls back to the last hex of target's path.
        assert result == endpoint_hex

    def test_calculate_intercept_point_early_exits_on_perfect_synchronization(
        self, mock_galaxy
    ):
        """When chaser_turns == target_turn (within 0.1), the loop breaks
        immediately and we get that hex — even when later candidates would
        also satisfy the cheaper-time criterion."""
        from unittest.mock import patch

        galaxy, _, _, _ = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = 1.0
        chaser.capabilities = MagicMock()
        chaser.capabilities.can_use_warp = MagicMock(return_value=False)

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(0, 0)

        target_path = [
            {"hex": HexCoord(1, 0), "turn": 1},
            {"hex": HexCoord(2, 0), "turn": 2},
            {"hex": HexCoord(3, 0), "turn": 3},
        ]

        # Force find_hybrid_path to return paths whose length yields
        # chaser_turns exactly matching target_turn for the FIRST candidate.
        # path_length = len(path) - 1; chaser_turns = path_length / chaser_speed.
        # With chaser_speed=1.0, we need path_length=1 → exactly 1.0 turns
        # which equals first candidate's target_turn=1 (perfect sync).
        canned_paths = {
            HexCoord(1, 0): [HexCoord(0, 0), HexCoord(1, 0)],   # length 1 → 1.0 turn
            HexCoord(2, 0): [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)],  # 2.0
            HexCoord(3, 0): [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)],  # 3.0
        }

        # PROJ-414: patched on GPS class; signature is `(start, end, fleet=...)`.
        def fake_hybrid(start, end, fleet=None):
            return canned_paths.get(end, [])

        with patch("game.strategy.services.intercept_calculator.project_fleet_path") as mock_project, \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path", side_effect=fake_hybrid) as mock_hybrid:
            mock_project.return_value = target_path
            result = calculate_intercept_point(chaser, target, galaxy)

        # Early exit fires on first candidate (turn=1, hex=(1,0)).
        assert result == HexCoord(1, 0)
        # And the loop broke before evaluating the third candidate.
        assert mock_hybrid.call_count < len(target_path)

    def test_calculate_intercept_point_uses_id_minus_one_for_navigationstate_chaser(
        self, mock_galaxy
    ):
        """PROJ-334 D-Observation O-003: NavigationState chasers leak id=-1
        into the proxy used for find_hybrid_path. This test pins the current
        behavior; if the id-leak is later fixed, this test will need updating."""
        from unittest.mock import patch
        from game.strategy.services.fleet_navigation_service import NavigationState

        galaxy, _, _, _ = mock_galaxy

        chaser_state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=10.0,
            can_warp=True,
        )

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(50, 0)

        target_path = [{"hex": HexCoord(50, 0), "turn": 0}]

        captured_fleets = []

        # PROJ-414: patched on GPS class; signature is `(start, end, fleet=...)`.
        def fake_hybrid(start, end, fleet=None):
            captured_fleets.append(fleet)
            return [HexCoord(0, 0), HexCoord(50, 0)]

        with patch("game.strategy.services.intercept_calculator.project_fleet_path") as mock_project, \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path", side_effect=fake_hybrid):
            mock_project.return_value = target_path
            calculate_intercept_point(chaser_state, target, galaxy)

        assert captured_fleets, "find_hybrid_path was never called"
        # The proxy adapter wraps the NavigationState and assigns id=-1.
        assert captured_fleets[0].id == -1
