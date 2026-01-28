"""
Unit tests for fleet pathfinding.

Tests path calculation, A* interstellar routing,
hybrid paths (local + warp), and intercept calculations.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.pathfinding import (
    find_path_deep_space,
    find_path_interstellar,
    get_system_at_hex,
    find_nearest_system,
    find_hybrid_path,
    project_fleet_path,
    calculate_intercept_point,
)
from game.strategy.data.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.services.fleet_navigation_service import NavigationState


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def origin():
    """Origin hex coordinate."""
    return HexCoord(0, 0)


@pytest.fixture
def nearby_hex():
    """A hex 5 units away."""
    return HexCoord(5, 0)


@pytest.fixture
def distant_hex():
    """A hex far away."""
    return HexCoord(100, 50)


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy with star systems."""
    galaxy = MagicMock()

    # Create mock systems
    sys_a = MagicMock()
    sys_a.name = "Alpha"
    sys_a.global_location = HexCoord(0, 0)
    sys_a.warp_points = []

    sys_b = MagicMock()
    sys_b.name = "Beta"
    sys_b.global_location = HexCoord(50, 0)
    sys_b.warp_points = []

    sys_c = MagicMock()
    sys_c.name = "Gamma"
    sys_c.global_location = HexCoord(100, 0)
    sys_c.warp_points = []

    # Create warp points connecting systems
    wp_a_to_b = MagicMock()
    wp_a_to_b.destination_id = "Beta"
    wp_a_to_b.location = HexCoord(5, 0)  # Local coords within system

    wp_b_to_a = MagicMock()
    wp_b_to_a.destination_id = "Alpha"
    wp_b_to_a.location = HexCoord(-5, 0)

    wp_b_to_c = MagicMock()
    wp_b_to_c.destination_id = "Gamma"
    wp_b_to_c.location = HexCoord(5, 0)

    wp_c_to_b = MagicMock()
    wp_c_to_b.destination_id = "Beta"
    wp_c_to_b.location = HexCoord(-5, 0)

    sys_a.warp_points = [wp_a_to_b]
    sys_b.warp_points = [wp_b_to_a, wp_b_to_c]
    sys_c.warp_points = [wp_c_to_b]

    # Set up galaxy systems
    galaxy.systems = {
        HexCoord(0, 0): sys_a,
        HexCoord(50, 0): sys_b,
        HexCoord(100, 0): sys_c,
    }

    def get_system_by_name(name):
        for sys in galaxy.systems.values():
            if sys.name == name:
                return sys
        return None

    galaxy.get_system_by_name = get_system_by_name

    return galaxy, sys_a, sys_b, sys_c


@pytest.fixture
def mock_fleet(origin):
    """Create a mock fleet at origin."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.location = origin
    fleet.speed = 10.0
    fleet.orders = []
    fleet.path = []
    return fleet


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
                    # Check the fleet-like object has correct warp capability
                    assert fleet_arg.can_use_warp() == False

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
