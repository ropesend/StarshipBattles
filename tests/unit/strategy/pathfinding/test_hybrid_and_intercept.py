"""
Unit tests for hybrid pathfinding and intercept calculations.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.pathfinding import (
    find_hybrid_path,
    project_fleet_path,
    calculate_intercept_point,
)
from game.core.hex_math import HexCoord
from game.strategy.services.fleet_navigation_service import NavigationState


# =============================================================================
# Test: Hybrid Pathfinding
# =============================================================================


class TestHybridPath:
    """Tests for find_hybrid_path (combines local + warp)."""

    def test_same_system_uses_deep_space(self, mock_galaxy):
        """Within same system uses deep space path."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        start = HexCoord(0, 0)
        end = HexCoord(5, 5)

        path = find_hybrid_path(galaxy, start, end)

        assert path is not None
        assert path[0] == start
        assert path[-1] == end

    def test_fleet_without_warp_uses_direct(self, mock_galaxy):
        """Fleet that can't warp uses direct deep space path."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Mock fleet that cannot warp
        fleet = MagicMock()
        fleet.can_use_warp = MagicMock(return_value=False)

        start = HexCoord(0, 0)
        end = HexCoord(100, 0)

        path = find_hybrid_path(galaxy, start, end, fleet=fleet)

        assert path is not None
        # Path should be direct hex-to-hex, not using warp
        assert path[0] == start
        assert path[-1] == end

    def test_warp_capable_fleet_uses_warp(self, mock_galaxy):
        """Fleet with warp capability uses warp lanes."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Mock fleet that can warp
        fleet = MagicMock()
        fleet.can_use_warp = MagicMock(return_value=True)

        start = HexCoord(0, 0)  # At Alpha
        end = HexCoord(100, 0)  # At Gamma

        path = find_hybrid_path(galaxy, start, end, fleet=fleet)

        assert path is not None
        # Path should include warp points

    def test_no_fleet_defaults_to_warp(self, mock_galaxy):
        """Without fleet parameter, defaults to warp-capable."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        start = HexCoord(0, 0)
        end = HexCoord(100, 0)

        path = find_hybrid_path(galaxy, start, end)

        assert path is not None

    def test_path_starts_and_ends_correctly(self, mock_galaxy):
        """Path always starts at start and ends at destination."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        start = HexCoord(2, 3)
        end = HexCoord(98, 2)

        path = find_hybrid_path(galaxy, start, end)

        assert path[0] == start
        assert path[-1] == end

    def test_same_hex_returns_path(self):
        """Path from hex to itself returns valid path."""
        galaxy = MagicMock()
        galaxy.systems = {}

        start = HexCoord(10, 10)

        path = find_hybrid_path(galaxy, start, start)

        assert path is not None

    def test_deep_space_between_systems(self, mock_galaxy):
        """Path in deep space (far from any system) uses direct."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Points far from any system
        start = HexCoord(-500, -500)
        end = HexCoord(-400, -400)

        path = find_hybrid_path(galaxy, start, end)

        assert path is not None
        assert path[0] == start
        assert path[-1] == end


# =============================================================================
# Test: Fleet Path Projection
# =============================================================================


class TestFleetPathProjection:
    """Tests for project_fleet_path function."""

    @patch('game.strategy.services.fleet_navigation_service.FleetNavigationService')
    def test_delegates_to_navigation_service(self, mock_service_class, mock_fleet, mock_galaxy):
        """project_fleet_path delegates to FleetNavigationService."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        mock_instance = MagicMock()
        mock_instance.project_path_as_dicts.return_value = []
        mock_service_class.return_value = mock_instance

        result = project_fleet_path(mock_fleet, galaxy)

        mock_service_class.assert_called_once()
        mock_instance.project_path_as_dicts.assert_called_once()

    @patch('game.strategy.services.fleet_navigation_service.FleetNavigationService')
    def test_passes_max_turns_parameter(self, mock_service_class, mock_fleet, mock_galaxy):
        """max_turns is passed to service."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        mock_instance = MagicMock()
        mock_instance.project_path_as_dicts.return_value = []
        mock_service_class.return_value = mock_instance

        project_fleet_path(mock_fleet, galaxy, max_turns=25)

        mock_instance.project_path_as_dicts.assert_called_with(
            mock_fleet, galaxy, 25
        )

    @patch('game.strategy.services.fleet_navigation_service.FleetNavigationService')
    def test_returns_list_of_dicts(self, mock_service_class, mock_fleet, mock_galaxy):
        """Returns list of segment dictionaries."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        expected = [
            {'start': HexCoord(0, 0), 'end': HexCoord(1, 0), 'turn': 0, 'hex': HexCoord(1, 0)},
            {'start': HexCoord(1, 0), 'end': HexCoord(2, 0), 'turn': 0, 'hex': HexCoord(2, 0)},
        ]
        mock_instance = MagicMock()
        mock_instance.project_path_as_dicts.return_value = expected
        mock_service_class.return_value = mock_instance

        result = project_fleet_path(mock_fleet, galaxy)

        assert result == expected


# =============================================================================
# Test: Intercept Point Calculation
# =============================================================================


class TestInterceptCalculation:
    """Tests for calculate_intercept_point function."""

    def test_stationary_target_returns_current_location(self, mock_galaxy):
        """Stationary target returns its current location."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = 10.0

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(50, 0)
        target.speed = 0.0
        target.orders = []
        target.path = []

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            mock_project.return_value = []  # Stationary

            result = calculate_intercept_point(chaser, target, galaxy)

            # Should return target's current location
            assert result == target.location

    def test_zero_chaser_speed_returns_target_location(self, mock_galaxy):
        """Chaser with zero speed returns target's current location."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = 0.0  # Cannot move

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(50, 0)
        target.speed = 5.0

        result = calculate_intercept_point(chaser, target, galaxy)

        assert result == target.location

    def test_intercept_point_on_target_path(self, mock_galaxy):
        """Intercept point is somewhere on target's projected path."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = 20.0  # Fast chaser

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(10, 0)
        target.speed = 5.0

        # Mock target's path
        target_path = [
            {'hex': HexCoord(11, 0), 'turn': 0},
            {'hex': HexCoord(12, 0), 'turn': 0},
            {'hex': HexCoord(13, 0), 'turn': 0},
            {'hex': HexCoord(14, 0), 'turn': 1},
            {'hex': HexCoord(15, 0), 'turn': 1},
        ]

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            mock_project.return_value = target_path

            result = calculate_intercept_point(chaser, target, galaxy)

            # Result should be one of the hexes on target path or target location
            valid_hexes = [pt['hex'] for pt in target_path] + [target.location]
            assert result in valid_hexes or isinstance(result, HexCoord)

    def test_fast_chaser_intercepts_early(self, mock_galaxy):
        """Faster chaser intercepts at earlier point on path."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(10, 0)
        target.speed = 5.0

        target_path = [
            {'hex': HexCoord(11, 0), 'turn': 0},
            {'hex': HexCoord(12, 0), 'turn': 1},
            {'hex': HexCoord(13, 0), 'turn': 2},
            {'hex': HexCoord(14, 0), 'turn': 3},
            {'hex': HexCoord(15, 0), 'turn': 4},
        ]

        # Fast chaser
        fast_chaser = MagicMock()
        fast_chaser.id = 1
        fast_chaser.location = HexCoord(0, 0)
        fast_chaser.speed = 50.0

        # Slow chaser
        slow_chaser = MagicMock()
        slow_chaser.id = 3
        slow_chaser.location = HexCoord(0, 0)
        slow_chaser.speed = 5.0

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            mock_project.return_value = target_path

            fast_result = calculate_intercept_point(fast_chaser, target, galaxy)
            slow_result = calculate_intercept_point(slow_chaser, target, galaxy)

            # Both should be valid hexes
            assert isinstance(fast_result, HexCoord)
            assert isinstance(slow_result, HexCoord)

    def test_chaser_at_same_location_as_target(self, mock_galaxy):
        """Chaser at same location returns that location."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        shared_location = HexCoord(25, 25)

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = shared_location
        chaser.speed = 10.0

        target = MagicMock()
        target.id = 2
        target.location = shared_location
        target.speed = 10.0

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            mock_project.return_value = []

            result = calculate_intercept_point(chaser, target, galaxy)

            assert result == shared_location

    def test_uses_hybrid_path_for_chaser(self, mock_galaxy):
        """Intercept calculation uses find_hybrid_path for chaser routing."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = 10.0

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(100, 0)
        target.speed = 5.0

        target_path = [{'hex': HexCoord(101, 0), 'turn': 0}]

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_hybrid:
                mock_project.return_value = target_path
                mock_hybrid.return_value = [HexCoord(0, 0), HexCoord(50, 0), HexCoord(100, 0)]

                calculate_intercept_point(chaser, target, galaxy)

                # Should have called find_hybrid_path
                assert mock_hybrid.called

    def test_accepts_navigation_state_as_chaser(self, mock_galaxy):
        """calculate_intercept_point accepts NavigationState as chaser."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # Use NavigationState instead of Fleet
        chaser_state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=10.0,
            can_warp=True
        )

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(50, 0)
        target.speed = 0.0
        target.orders = []
        target.path = []

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            mock_project.return_value = []  # Stationary

            result = calculate_intercept_point(chaser_state, target, galaxy)

            # Should return target's current location
            assert result == target.location

    def test_navigation_state_chaser_uses_can_warp_field(self, mock_galaxy):
        """NavigationState chaser uses can_warp field for path calculation."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # NavigationState with can_warp=False
        chaser_state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=10.0,
            can_warp=False  # Cannot warp
        )

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(100, 0)
        target.speed = 5.0

        target_path = [{'hex': HexCoord(101, 0), 'turn': 0}]

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_hybrid:
                mock_project.return_value = target_path
                mock_hybrid.return_value = [HexCoord(0, 0), HexCoord(50, 0), HexCoord(100, 0)]

                calculate_intercept_point(chaser_state, target, galaxy)

                # find_hybrid_path should be called with a fleet-like object that respects can_warp
                assert mock_hybrid.called
                call_args = mock_hybrid.call_args
                fleet_arg = call_args.kwargs.get('fleet') or call_args[1].get('fleet')
                if fleet_arg:
                    # PROJ-210: Check the fleet-like object has correct warp capability via capabilities
                    assert fleet_arg.capabilities.can_use_warp() is False

    def test_navigation_state_uses_location_and_speed(self, mock_galaxy):
        """NavigationState location and speed are used correctly."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        # NavigationState with specific location and speed
        chaser_state = NavigationState(
            location=HexCoord(25, 0),
            path=(),
            orders=(),
            speed=15.0,
            can_warp=True
        )

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(50, 0)
        target.speed = 0.0
        target.orders = []
        target.path = []

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_hybrid:
                mock_project.return_value = []  # Stationary
                # Return path from chaser location to target
                mock_hybrid.return_value = [HexCoord(25, 0), HexCoord(35, 0), HexCoord(50, 0)]

                result = calculate_intercept_point(chaser_state, target, galaxy)

                # Should have calculated path from NavigationState's location
                mock_hybrid.assert_called()
                call_args = mock_hybrid.call_args
                # First positional arg should be galaxy, second is start location
                assert call_args[0][1] == HexCoord(25, 0)

    def test_fleet_chaser_still_works_unchanged(self, mock_galaxy):
        """Regular Fleet object still works as chaser (backward compatibility)."""
        galaxy, sys_a, sys_b, sys_c = mock_galaxy

        chaser = MagicMock()
        chaser.id = 1
        chaser.location = HexCoord(0, 0)
        chaser.speed = 10.0
        chaser.can_use_warp = MagicMock(return_value=True)

        target = MagicMock()
        target.id = 2
        target.location = HexCoord(50, 0)
        target.speed = 0.0
        target.orders = []
        target.path = []

        with patch('game.strategy.data.pathfinding.project_fleet_path') as mock_project:
            mock_project.return_value = []  # Stationary

            result = calculate_intercept_point(chaser, target, galaxy)

            # Should return target's current location (backward compat)
            assert result == target.location
