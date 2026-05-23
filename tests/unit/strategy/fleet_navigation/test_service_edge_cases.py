# -*- coding: utf-8 -*-
"""Edge case tests for FleetNavigationService.

Tests cover:
- NavigationState immutability and from_fleet conversion
- PathSegment serialization
- NavigationStep composition
- FleetNavigationService edge cases:
  - Empty orders
  - Non-movement orders (COLONIZE, JOIN_FLEET)
  - Path recalculation triggers
  - Zero speed handling
  - Warp vs normal movement detection
  - Mutation bridge behavior
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.services.fleet_navigation_service import (
    FleetNavigationService,
    NavigationState,
    NavigationStep,
    PathSegment,
)
from game.strategy.data.order_types import Order, OrderType


def _make_mock_fleet(
    *,
    location=None,
    path=None,
    orders=None,
    speed=5.0,
    can_use_warp=False,
    current_order=None,
):
    """Build a MagicMock fleet pre-populated with the attributes the navigation
    service consults. Lets test bodies focus on the assertion under test."""
    fleet = MagicMock()
    fleet.location = location if location is not None else HexCoord(0, 0)
    fleet.path = list(path) if path is not None else []
    fleet.orders = list(orders) if orders is not None else []
    fleet.speed = speed
    fleet.capabilities.can_use_warp.return_value = can_use_warp
    if current_order is not None:
        fleet.get_current_order.return_value = current_order
    return fleet


class TestNavigationStateImmutability:
    """Tests for NavigationState immutability."""

    def test_state_is_frozen(self):
        """NavigationState should be frozen (immutable)."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=True
        )
        with pytest.raises(AttributeError):
            state.location = HexCoord(1, 1)

    def test_state_hashable(self):
        """NavigationState should be hashable due to frozen=True."""
        state = NavigationState(
            location=HexCoord(1, 2),
            path=(HexCoord(2, 2),),
            orders=(),
            speed=3.0,
            can_warp=False
        )
        # Should not raise
        hash(state)

    def test_path_is_tuple(self):
        """Path should be stored as tuple for immutability."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0)),
            orders=(),
            speed=5.0,
            can_warp=True
        )
        assert isinstance(state.path, tuple)

    def test_orders_is_tuple(self):
        """Orders should be stored as tuple for immutability."""
        order = Order(order_type=OrderType.MOVE, target=HexCoord(5, 5))
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=False
        )
        assert isinstance(state.orders, tuple)


class TestNavigationStateFromFleet:
    """Tests for NavigationState.from_fleet()."""

    def test_from_fleet_copies_location(self):
        """from_fleet should copy fleet location."""
        fleet = MagicMock()
        fleet.location = HexCoord(3, 4)
        fleet.path = []
        fleet.orders = []
        fleet.speed = 5.0
        fleet.capabilities.can_use_warp.return_value = True

        state = NavigationState.from_fleet(fleet)
        assert state.location == HexCoord(3, 4)

    def test_from_fleet_converts_path_to_tuple(self):
        """from_fleet should convert path list to tuple."""
        fleet = MagicMock()
        fleet.location = HexCoord(0, 0)
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]
        fleet.orders = []
        fleet.speed = 5.0
        fleet.capabilities.can_use_warp.return_value = False

        state = NavigationState.from_fleet(fleet)
        assert state.path == (HexCoord(1, 0), HexCoord(2, 0))
        assert isinstance(state.path, tuple)

    def test_from_fleet_converts_orders_to_tuple(self):
        """from_fleet should convert orders list to tuple."""
        order = Order(order_type=OrderType.MOVE, target=HexCoord(5, 5))
        fleet = MagicMock()
        fleet.location = HexCoord(0, 0)
        fleet.path = []
        fleet.orders = [order]
        fleet.speed = 5.0
        fleet.capabilities.can_use_warp.return_value = False

        state = NavigationState.from_fleet(fleet)
        assert state.orders == (order,)
        assert isinstance(state.orders, tuple)

    def test_from_fleet_captures_speed(self):
        """from_fleet should capture fleet speed."""
        fleet = MagicMock()
        fleet.location = HexCoord(0, 0)
        fleet.path = []
        fleet.orders = []
        fleet.speed = 7.5
        fleet.capabilities.can_use_warp.return_value = False

        state = NavigationState.from_fleet(fleet)
        assert state.speed == 7.5

    def test_from_fleet_captures_warp_capability(self):
        """from_fleet should capture warp capability."""
        fleet = MagicMock()
        fleet.location = HexCoord(0, 0)
        fleet.path = []
        fleet.orders = []
        fleet.speed = 5.0
        fleet.capabilities.can_use_warp.return_value = True

        state = NavigationState.from_fleet(fleet)
        assert state.can_warp is True

        fleet.capabilities.can_use_warp.return_value = False
        state2 = NavigationState.from_fleet(fleet)
        assert state2.can_warp is False


class TestPathSegment:
    """Tests for PathSegment data structure."""

    def test_path_segment_creation(self):
        """PathSegment should store all fields."""
        seg = PathSegment(
            start=HexCoord(0, 0),
            end=HexCoord(1, 0),
            turn=2,
            is_warp=False
        )
        assert seg.start == HexCoord(0, 0)
        assert seg.end == HexCoord(1, 0)
        assert seg.turn == 2
        assert seg.is_warp is False

    def test_path_segment_to_dict(self):
        """to_dict should return proper dict structure."""
        seg = PathSegment(
            start=HexCoord(5, 5),
            end=HexCoord(6, 5),
            turn=1,
            is_warp=True
        )
        d = seg.to_dict()
        assert d['start'] == HexCoord(5, 5)
        assert d['end'] == HexCoord(6, 5)
        assert d['turn'] == 1
        assert d['is_warp'] is True
        assert d['hex'] == HexCoord(6, 5)  # Alias for end

    def test_path_segment_hex_alias(self):
        """to_dict should include 'hex' as alias for 'end'."""
        seg = PathSegment(
            start=HexCoord(10, 10),
            end=HexCoord(11, 10),
            turn=0,
            is_warp=False
        )
        d = seg.to_dict()
        assert d['hex'] == d['end']

    def test_path_segment_is_frozen(self):
        """PathSegment should be immutable."""
        seg = PathSegment(
            start=HexCoord(0, 0),
            end=HexCoord(1, 0),
            turn=0,
            is_warp=False
        )
        with pytest.raises(AttributeError):
            seg.turn = 5


class TestNavigationStep:
    """Tests for NavigationStep data structure."""

    def test_navigation_step_creation(self):
        """NavigationStep should store all fields."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        step = NavigationStep(
            next_hex=HexCoord(1, 0),
            new_state=state,
            order_complete=True
        )
        assert step.next_hex == HexCoord(1, 0)
        assert step.new_state == state
        assert step.order_complete is True

    def test_navigation_step_default_order_complete(self):
        """order_complete should default to False."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        step = NavigationStep(next_hex=None, new_state=state)
        assert step.order_complete is False

    def test_navigation_step_with_none_next_hex(self):
        """NavigationStep should allow None next_hex."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        step = NavigationStep(next_hex=None, new_state=state)
        assert step.next_hex is None


class TestFleetNavigationServiceEdgeCases:
    """Edge case tests for FleetNavigationService."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return FleetNavigationService()

    @pytest.fixture
    def mock_galaxy(self):
        """Create mock galaxy."""
        galaxy = MagicMock()
        return galaxy

    def test_compute_next_step_no_orders(self, service, mock_galaxy):
        """compute_next_step with no orders should return no movement."""
        state = NavigationState(
            location=HexCoord(5, 5),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        step = service.compute_next_step(state, mock_galaxy)
        assert step.next_hex is None
        assert step.new_state == state
        assert step.order_complete is False

    def test_compute_next_step_non_movement_order(self, service, mock_galaxy):
        """compute_next_step with COLONIZE order should return no movement."""
        order = Order(order_type=OrderType.COLONIZE, target=None)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=False
        )
        step = service.compute_next_step(state, mock_galaxy)
        assert step.next_hex is None
        # Order should NOT be popped (handled by other processor)
        assert step.order_complete is False
        assert len(step.new_state.orders) == 1

    def test_needs_path_recalculation_empty_path(self, service):
        """Empty path should trigger recalculation."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        assert service._needs_path_recalculation(state, HexCoord(5, 5)) is True

    def test_needs_path_recalculation_path_matches_destination(self, service):
        """Path ending at destination should not need recalculation."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0), HexCoord(5, 5)),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        assert service._needs_path_recalculation(state, HexCoord(5, 5)) is False

    def test_needs_path_recalculation_path_differs_from_destination(self, service):
        """Path not ending at destination should need recalculation."""
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(HexCoord(1, 0), HexCoord(2, 0)),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        assert service._needs_path_recalculation(state, HexCoord(5, 5)) is True

    def test_get_destination_move_order(self, service, mock_galaxy):
        """MOVE order should return target as destination."""
        target = HexCoord(10, 10)
        order = Order(order_type=OrderType.MOVE, target=target)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=False
        )
        dest = service.get_destination(state, order, mock_galaxy)
        assert dest == target

    def test_get_destination_non_movement_order(self, service, mock_galaxy):
        """COLONIZE order should return None destination."""
        order = Order(order_type=OrderType.COLONIZE, target=None)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=False
        )
        dest = service.get_destination(state, order, mock_galaxy)
        assert dest is None

    def test_get_destination_move_to_fleet_no_target(self, service, mock_galaxy):
        """MOVE_TO_FLEET with None target should return None."""
        order = Order(order_type=OrderType.MOVE_TO_FLEET, target=None)
        state = NavigationState(
            location=HexCoord(0, 0),
            path=(),
            orders=(order,),
            speed=5.0,
            can_warp=False
        )
        dest = service.get_destination(state, order, mock_galaxy)
        assert dest is None

    # NOTE: test_get_destination_move_to_fleet_target_without_location removed
    # Fleet always has location attribute - testing "target lacking location" is obsolete
    # test_get_destination_move_to_fleet_no_target covers the None target case

    def test_compute_path_already_at_destination(self, service, mock_galaxy):
        """compute_path at destination should return empty list."""
        state = NavigationState(
            location=HexCoord(5, 5),
            path=(),
            orders=(),
            speed=5.0,
            can_warp=False
        )
        path = service.compute_path(state, HexCoord(5, 5), mock_galaxy)
        assert path == []


class TestProjectPath:
    """Tests for project_path method."""

    @pytest.fixture
    def service(self):
        return FleetNavigationService()

    @pytest.mark.parametrize("speed", [0.0, -5.0], ids=["zero", "negative"])
    def test_project_path_non_positive_speed_returns_empty(self, service, speed):
        """project_path with zero or negative speed should return empty list."""
        fleet = _make_mock_fleet(path=[HexCoord(1, 0)], speed=speed)
        galaxy = MagicMock()
        assert service.project_path(fleet, galaxy) == []

    def test_project_path_empty_path_and_orders(self, service):
        """project_path with no path or orders should return empty list."""
        fleet = _make_mock_fleet(speed=5.0)
        galaxy = MagicMock()
        assert service.project_path(fleet, galaxy) == []


class TestProjectPathAsDicts:
    """Tests for project_path_as_dicts method.

    NOTE: surface overlap with `tests/unit/strategy/fleet_navigation/
    test_projection.py:146-169` is intentional. These tests pin the
    list-of-dict shape returned by the service (zero-speed empty-list
    edge case is unique to this file) while `test_projection.py`
    covers the geometric projection itself. PROJ-322 Task 1.16
    (S10-CAT4-001).
    """

    @pytest.fixture
    def service(self):
        return FleetNavigationService()

    def test_returns_list_of_dicts(self, service):
        """project_path_as_dicts should return list of dicts."""
        fleet = _make_mock_fleet(path=[HexCoord(1, 0)], speed=5.0)
        galaxy = MagicMock()
        result = service.project_path_as_dicts(fleet, galaxy)
        # May be empty if no movement orders, but should be list
        assert isinstance(result, list)

    def test_empty_with_zero_speed(self, service):
        """project_path_as_dicts with zero speed should return empty list."""
        fleet = _make_mock_fleet(speed=0.0)
        galaxy = MagicMock()
        assert service.project_path_as_dicts(fleet, galaxy) == []


class TestCalculateFleetNextHex:
    """Tests for calculate_fleet_next_hex mutation bridge."""

    @pytest.fixture
    def service(self):
        return FleetNavigationService()

    def test_no_orders_returns_none(self, service):
        """Fleet with no orders should return None."""
        fleet = _make_mock_fleet(speed=5.0, current_order=None)
        galaxy = MagicMock()
        assert service.calculate_fleet_next_hex(fleet, galaxy) is None

    def test_move_to_fleet_invalid_target_pops_order(self, service):
        """MOVE_TO_FLEET with invalid target should pop order and return None."""
        order = MagicMock()
        order.type = OrderType.MOVE_TO_FLEET
        order.target = None  # Invalid target

        fleet = _make_mock_fleet(orders=[order], speed=5.0, current_order=order)
        galaxy = MagicMock()
        assert service.calculate_fleet_next_hex(fleet, galaxy) is None
        fleet.pop_order.assert_called_once()

    # NOTE: test_move_to_fleet_target_without_location_pops_order removed
    # Fleet always has location attribute - testing "target lacking location" is obsolete
    # test_move_to_fleet_invalid_target_pops_order covers the None target case
