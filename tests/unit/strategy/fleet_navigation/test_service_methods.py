"""
Tests for FleetNavigationService methods.

Tests for get_destination, compute_path, compute_next_step, project_path,
and calculate_fleet_next_hex methods.

PROJ-35: Unified fleet navigation logic for UI projection and turn execution.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.hex_math import HexCoord
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType


class TestGetDestination:
    """Tests for FleetNavigationService.get_destination()."""

    def test_get_destination_move_order_returns_target(self):
        """MOVE order should return the target HexCoord."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        order = FleetOrder(OrderType.MOVE, HexCoord(5, 5))
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        result = service.get_destination(state, order, galaxy=None)

        assert result == HexCoord(5, 5)

    def test_get_destination_colonize_order_returns_none(self):
        """COLONIZE order should return None (not a movement order)."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        order = FleetOrder(OrderType.COLONIZE, MagicMock())
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        result = service.get_destination(state, order, galaxy=None)

        assert result is None

    def test_get_destination_join_fleet_returns_none(self):
        """JOIN_FLEET order should return None (handled separately)."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        target_fleet = MagicMock()
        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        result = service.get_destination(state, order, galaxy=None)

        assert result is None

    def test_get_destination_move_to_fleet_calls_intercept(self):
        """MOVE_TO_FLEET order should call calculate_intercept_point."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()

        # Create target fleet with location
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(10, 10)

        order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        # Mock calculate_intercept_point at the source location (where it's imported from)
        with patch(
            'game.strategy.data.pathfinding.calculate_intercept_point',
            return_value=HexCoord(5, 5)
        ) as mock_intercept:
            result = service.get_destination(state, order, galaxy=MagicMock())

        assert result == HexCoord(5, 5)
        mock_intercept.assert_called_once()

    def test_get_destination_move_to_fleet_invalid_target_returns_none(self):
        """MOVE_TO_FLEET with invalid target should return None."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()

        # Target without location attribute
        order = FleetOrder(OrderType.MOVE_TO_FLEET, None)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        result = service.get_destination(state, order, galaxy=MagicMock())

        assert result is None


class TestComputePath:
    """Tests for FleetNavigationService.compute_path()."""

    def test_compute_path_removes_start_hex_if_equals_location(self):
        """compute_path() should remove start hex if it equals current location."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=True
        )
        destination = HexCoord(3, 0)

        # Mock find_hybrid_path to return path starting with current location
        mock_path = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path',
            return_value=mock_path
        ):
            result = service.compute_path(state, destination, galaxy=MagicMock())

        # Should remove the start hex (0, 0)
        assert result == [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        assert HexCoord(0, 0) not in result

    def test_compute_path_returns_empty_if_at_destination(self):
        """compute_path() should return empty list if already at destination."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        state = NavigationState(
            location=HexCoord(5, 5),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=True
        )

        result = service.compute_path(state, HexCoord(5, 5), galaxy=MagicMock())

        assert result == []

    def test_compute_path_returns_empty_if_no_path_found(self):
        """compute_path() should return empty list if pathfinding returns None."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=True
        )

        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path',
            return_value=None
        ):
            result = service.compute_path(state, HexCoord(10, 10), galaxy=MagicMock())

        assert result == []


class TestComputeNextStep:
    """Tests for FleetNavigationService.compute_next_step()."""

    def test_compute_next_step_is_pure_no_mutation(self):
        """compute_next_step() should be pure - not mutate input state."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        order = FleetOrder(OrderType.MOVE, HexCoord(2, 0))
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0)),
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        # Store original values
        original_location = state.location
        original_path = state.path
        original_orders = state.orders

        step = service.compute_next_step(state, galaxy=MagicMock())

        # Input state should be unchanged (it's frozen anyway, but verify concept)
        assert state.location == original_location
        assert state.path == original_path
        assert state.orders == original_orders

    def test_compute_next_step_pops_from_path(self):
        """compute_next_step() should return next hex from path."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        order = FleetOrder(OrderType.MOVE, HexCoord(3, 0))
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)),
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        step = service.compute_next_step(state, galaxy=MagicMock())

        assert step.next_hex == HexCoord(1, 0)
        assert step.new_state.location == HexCoord(1, 0)
        assert step.new_state.path == (HexCoord(2, 0), HexCoord(3, 0))

    def test_compute_next_step_no_orders_returns_none(self):
        """compute_next_step() with no orders should return None."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=True
        )

        step = service.compute_next_step(state, galaxy=MagicMock())

        assert step.next_hex is None
        assert step.order_complete is False

    def test_compute_next_step_order_complete_when_path_exhausted(self):
        """compute_next_step() should mark order complete when path exhausted."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        order = FleetOrder(OrderType.MOVE, HexCoord(1, 0))
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0),),  # Only one step left
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        step = service.compute_next_step(state, galaxy=MagicMock())

        assert step.next_hex == HexCoord(1, 0)
        assert step.order_complete is True
        assert len(step.new_state.orders) == 0  # Order removed

    def test_compute_next_step_recalculates_path_when_destination_changes(self):
        """compute_next_step() should recalculate path if destination changes."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        # Order target changed to a different location than path endpoint
        order = FleetOrder(OrderType.MOVE, HexCoord(5, 0))  # Target is (5, 0)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0)),  # But path leads to (2, 0)
            orders=(order,),
            speed=5.0,
            can_warp=True
        )

        # Mock to return a new path to the actual target
        new_path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0), HexCoord(4, 0), HexCoord(5, 0)]
        with patch(
            'game.strategy.services.fleet_navigation_service.find_hybrid_path',
            return_value=new_path
        ):
            step = service.compute_next_step(state, galaxy=MagicMock())

        assert step.next_hex == HexCoord(1, 0)
        # New state path should be recalculated path minus the step taken
        assert HexCoord(5, 0) in step.new_state.path


class TestProjectPath:
    """Tests for FleetNavigationService.project_path()."""

    def test_project_path_produces_correct_segments(self):
        """project_path() should produce PathSegment objects with correct data."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, PathSegment
        )

        service = FleetNavigationService()

        # Create a fleet with a simple MOVE order and pre-computed path
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0  # 2 moves per turn
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(3, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        # Should produce 3 segments (one for each path step)
        assert len(segments) == 3
        assert all(isinstance(seg, PathSegment) for seg in segments)

        # First segment
        assert segments[0].start == HexCoord(0, 0)
        assert segments[0].end == HexCoord(1, 0)
        assert segments[0].is_warp is False

        # Last segment should be at the destination
        assert segments[-1].end == HexCoord(3, 0)

    def test_project_path_respects_max_turns(self):
        """project_path() should stop at max_turns."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Create a fleet with a long path
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=1.0  # 1 move per turn
        )
        fleet.path = [HexCoord(i, 0) for i in range(1, 20)]  # 19 steps
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(19, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=3)

        # At speed 1, should only do 3 moves (one per turn for 3 turns)
        assert len(segments) == 3

    def test_project_path_handles_warp_detection(self):
        """project_path() should detect warp jumps (hex_distance > 1)."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Create a fleet with a warp jump in the path
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )
        # Path with a warp jump: (0,0) -> (1,0) -> (5,0) which is distance > 1
        fleet.path = [HexCoord(1, 0), HexCoord(5, 0)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(5, 0))]
        fleet.can_use_warp = MagicMock(return_value=True)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        # First segment should be normal move
        assert segments[0].is_warp is False

        # Second segment should be warp (distance > 1)
        assert segments[1].is_warp is True

    def test_project_path_returns_empty_for_fleet_without_orders(self):
        """project_path() should return empty list if fleet has no orders."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = []
        fleet.orders = []
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        assert segments == []

    def test_project_path_calculates_turn_numbers(self):
        """project_path() should calculate correct turn numbers based on speed."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        # Speed 2 means 2 moves per turn
        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=2.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0), HexCoord(4, 0)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(4, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        segments = service.project_path(fleet, galaxy=MagicMock(), max_turns=5)

        # First two moves in turn 0, next two in turn 1
        assert segments[0].turn == 0
        assert segments[1].turn == 0
        assert segments[2].turn == 1
        assert segments[3].turn == 1


class TestProjectPathAsDicts:
    """Tests for FleetNavigationService.project_path_as_dicts()."""

    def test_project_path_as_dicts_returns_list_of_dicts(self):
        """project_path_as_dicts() should return list of dicts for backward compatibility."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(2, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.project_path_as_dicts(fleet, galaxy=MagicMock(), max_turns=5)

        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert len(result) == 2

        # Check dict structure
        assert 'start' in result[0]
        assert 'end' in result[0]
        assert 'turn' in result[0]
        assert 'is_warp' in result[0]
        assert 'hex' in result[0]  # Legacy field


class TestCalculateFleetNextHex:
    """Tests for FleetNavigationService.calculate_fleet_next_hex() - mutation bridge."""

    def test_calculate_fleet_next_hex_returns_next_hex(self):
        """calculate_fleet_next_hex() should return the next hex from path."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(3, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        assert result == HexCoord(1, 0)

    def test_calculate_fleet_next_hex_updates_fleet_path(self):
        """calculate_fleet_next_hex() should update fleet.path (mutation bridge)."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(3, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        # Path should be updated to remaining path
        assert fleet.path == [HexCoord(2, 0), HexCoord(3, 0)]

    def test_calculate_fleet_next_hex_pops_order_on_completion(self):
        """calculate_fleet_next_hex() should pop order when path exhausted."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = [HexCoord(1, 0)]  # Only one step - order will complete
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(1, 0))]
        fleet.can_use_warp = MagicMock(return_value=False)

        # Store original order count
        original_order_count = len(fleet.orders)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        assert result == HexCoord(1, 0)
        # Order should be popped
        assert len(fleet.orders) == original_order_count - 1

    def test_calculate_fleet_next_hex_returns_none_for_no_orders(self):
        """calculate_fleet_next_hex() should return None if no orders."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(0, 0),
            speed=5.0
        )
        fleet.path = []
        fleet.orders = []
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        assert result is None

    def test_calculate_fleet_next_hex_handles_order_complete_without_movement(self):
        """calculate_fleet_next_hex() should handle order complete when already at destination."""
        from game.strategy.services.fleet_navigation_service import FleetNavigationService

        service = FleetNavigationService()

        fleet = Fleet(
            fleet_id='test',
            owner_id=0,
            location=HexCoord(5, 5),  # Already at destination
            speed=5.0
        )
        fleet.path = []
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(5, 5))]
        fleet.can_use_warp = MagicMock(return_value=False)

        result = service.calculate_fleet_next_hex(fleet, galaxy=MagicMock())

        # Should return None but pop the order
        assert result is None
        assert len(fleet.orders) == 0
