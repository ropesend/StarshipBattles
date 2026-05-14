"""Unit tests for FEAT-28 mutual-pursuit rendezvous routing in
FleetNavigationService.

When two fleets are mutually pursuing each other (each fleet's current head
order is MOVE_TO_FLEET or JOIN_FLEET targeting the other), `get_destination`
must bypass the asymmetric `calculate_intercept_point` evaluator and return
the target's current hex directly. Both fleets then pathfind toward each
other along the shortest line and converge near the geometric middle.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.services.fleet_navigation_service import (
    FleetNavigationService,
    NavigationState,
)


def _make_fleet(fleet_id: int, location: HexCoord, head_order: Order | None = None) -> Fleet:
    """Build a Fleet-like mock with a single head order for mutual-pursuit tests."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = fleet_id
    fleet.location = location
    fleet.speed = 5.0
    fleet.path = []
    fleet.orders = [head_order] if head_order is not None else []
    fleet.get_current_order = MagicMock(return_value=head_order)
    fleet.capabilities = MagicMock()
    fleet.capabilities.can_use_warp = MagicMock(return_value=False)
    return fleet


@pytest.fixture
def galaxy_no_systems():
    """Galaxy with no star systems — forces deep-space line draws (no warp)."""
    galaxy = MagicMock()
    galaxy.systems = {}
    return galaxy


# ---------------------------------------------------------------------------
# _is_mutual_pursuit predicate
# ---------------------------------------------------------------------------


class TestIsMutualPursuit:
    """The `_is_mutual_pursuit(self_fleet, target_fleet)` predicate is True
    iff target's current head order is MOVE_TO_FLEET / JOIN_FLEET targeting
    self_fleet."""

    def test_true_when_target_targets_self_via_move_to_fleet(self):
        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(2, HexCoord(10, 0), Order(OrderType.MOVE_TO_FLEET, a))
        a.orders = [Order(OrderType.MOVE_TO_FLEET, b)]
        a.get_current_order = MagicMock(return_value=a.orders[0])

        service = FleetNavigationService()
        assert service._is_mutual_pursuit(a, b) is True

    def test_true_when_target_targets_self_via_join_fleet(self):
        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(2, HexCoord(10, 0), Order(OrderType.JOIN_FLEET, a))
        service = FleetNavigationService()
        assert service._is_mutual_pursuit(a, b) is True

    def test_false_when_target_has_no_orders(self):
        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(2, HexCoord(10, 0), head_order=None)
        service = FleetNavigationService()
        assert service._is_mutual_pursuit(a, b) is False

    def test_false_when_target_targets_third_party(self):
        a = _make_fleet(1, HexCoord(0, 0))
        c = _make_fleet(3, HexCoord(20, 0))
        b = _make_fleet(2, HexCoord(10, 0), Order(OrderType.MOVE_TO_FLEET, c))
        service = FleetNavigationService()
        assert service._is_mutual_pursuit(a, b) is False

    def test_false_when_target_head_order_is_move(self):
        """A MOVE order with hex target is not pursuit, even at the same hex."""
        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(
            2, HexCoord(10, 0),
            Order(OrderType.MOVE, HexCoord(0, 0)),
        )
        service = FleetNavigationService()
        assert service._is_mutual_pursuit(a, b) is False

    def test_false_when_target_head_order_is_colonize(self):
        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(
            2, HexCoord(10, 0),
            Order(OrderType.COLONIZE, MagicMock()),
        )
        service = FleetNavigationService()
        assert service._is_mutual_pursuit(a, b) is False


# ---------------------------------------------------------------------------
# get_destination MOVE_TO_FLEET branch
# ---------------------------------------------------------------------------


class TestGetDestinationMutualBranch:
    """The MOVE_TO_FLEET branch of `get_destination` returns the target's
    current location when mutual pursuit is detected, bypassing
    `calculate_intercept_point`."""

    def test_returns_target_location_for_mutual_pursuit(self, galaxy_no_systems):
        """Mutual pursuit: destination is target's current hex (no intercept)."""
        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(2, HexCoord(10, 0), Order(OrderType.JOIN_FLEET, a))
        order = Order(OrderType.MOVE_TO_FLEET, b)
        a.orders = [order]
        a.get_current_order = MagicMock(return_value=order)

        state = NavigationState.from_fleet(a)
        service = FleetNavigationService()

        # Pass self_fleet through; see Step A of FEAT-28 design.
        destination = service.get_destination(state, order, galaxy_no_systems, self_fleet=a)
        assert destination == HexCoord(10, 0)

    def test_falls_through_to_intercept_when_not_mutual(self, galaxy_no_systems):
        """Non-mutual MOVE_TO_FLEET still calls calculate_intercept_point."""
        from unittest.mock import patch

        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(2, HexCoord(10, 0))  # no orders → not mutual
        order = Order(OrderType.MOVE_TO_FLEET, b)
        a.orders = [order]

        state = NavigationState.from_fleet(a)
        service = FleetNavigationService()

        with patch(
            "game.strategy.services.intercept_calculator.InterceptCalculator.calculate_intercept_point",
            return_value=HexCoord(5, 0),
        ) as mock_intercept:
            destination = service.get_destination(
                state, order, galaxy_no_systems, self_fleet=a,
            )
            mock_intercept.assert_called_once()
            assert destination == HexCoord(5, 0)

    def test_no_self_fleet_falls_back_to_intercept(self, galaxy_no_systems):
        """When self_fleet=None (e.g. UI projection w/o fleet identity),
        get_destination falls back to today's intercept-based behavior."""
        from unittest.mock import patch

        a = _make_fleet(1, HexCoord(0, 0))
        b = _make_fleet(2, HexCoord(10, 0), Order(OrderType.JOIN_FLEET, a))
        order = Order(OrderType.MOVE_TO_FLEET, b)
        a.orders = [order]

        state = NavigationState.from_fleet(a)
        service = FleetNavigationService()

        with patch(
            "game.strategy.services.intercept_calculator.InterceptCalculator.calculate_intercept_point",
            return_value=HexCoord(8, 0),
        ) as mock_intercept:
            destination = service.get_destination(
                state, order, galaxy_no_systems, self_fleet=None,
            )
            mock_intercept.assert_called_once()
            assert destination == HexCoord(8, 0)

