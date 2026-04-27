"""
Tests for FleetNavigationService destination and path computation methods.

Tests for get_destination and compute_path methods.

PROJ-35: Unified fleet navigation logic for UI projection and turn execution.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType


class TestGetDestination:
    """Tests for FleetNavigationService.get_destination()."""

    def test_get_destination_move_order_returns_target(self):
        """MOVE order should return the target HexCoord."""
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService, NavigationState
        )

        service = FleetNavigationService()
        order = Order(OrderType.MOVE, HexCoord(5, 5))
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
        order = Order(OrderType.COLONIZE, MagicMock())
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
        order = Order(OrderType.JOIN_FLEET, target_fleet)
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

        order = Order(OrderType.MOVE_TO_FLEET, target_fleet)
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
        order = Order(OrderType.MOVE_TO_FLEET, None)
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
        order = Order(OrderType.MOVE, HexCoord(2, 0))
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
        order = Order(OrderType.MOVE, HexCoord(3, 0))
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
        order = Order(OrderType.MOVE, HexCoord(1, 0))
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
        order = Order(OrderType.MOVE, HexCoord(5, 0))  # Target is (5, 0)
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
