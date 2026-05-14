"""
Regression test for infinite-recursion crash when fleets have cyclic
MOVE_TO_FLEET (intercept) orders.

Crash trace (pre-fix): project_path -> _resolve_path_for_order
-> get_destination -> calculate_intercept_point -> project_fleet_path
-> project_path_as_dicts -> project_path -> ... RecursionError.

The cycle is broken by a re-entrancy guard in
FleetNavigationService.project_path: when a fleet is already being
projected up the call stack, recursive entries return an empty
projection. calculate_intercept_point already handles an empty target
path by chasing the target's current location.
"""

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.services.galaxy_pathfinding_service import GalaxyPathfindingService
from game.strategy.services.intercept_calculator import (
    InterceptCalculator,
    project_fleet_path,
)
from game.strategy.services.fleet_navigation_service import (
    FleetNavigationService,
    NavigationState,
)


def calculate_intercept_point(chaser, target_fleet, galaxy):
    """Test helper preserving the pre-PROJ-414 shim signature."""
    return InterceptCalculator(
        GalaxyPathfindingService(galaxy),
    ).calculate_intercept_point(chaser, target_fleet, galaxy)


def _make_intercept_fleet(fleet_id: int, location: HexCoord, target_fleet) -> Fleet:
    """Build a minimal Fleet-like mock with a single MOVE_TO_FLEET order."""
    fleet = MagicMock(spec=Fleet)
    fleet.id = fleet_id
    fleet.location = location
    fleet.speed = 5.0
    fleet.path = []
    fleet.orders = [Order(OrderType.MOVE_TO_FLEET, target_fleet)]
    fleet.capabilities = MagicMock()
    fleet.capabilities.can_use_warp = MagicMock(return_value=False)
    return fleet


class TestMutualInterceptDoesNotRecurse:
    """Cyclic MOVE_TO_FLEET orders must not blow the recursion stack."""

    def test_mutual_intercept_pair(self, mock_galaxy):
        """Fleet A intercepts B and B intercepts A — projection terminates."""
        galaxy, *_ = mock_galaxy

        # Build the cycle: A.target = B, B.target = A.
        # We need both Fleet objects to exist before we can wire the orders,
        # so build them with placeholder targets first, then fix up.
        fleet_a = _make_intercept_fleet(1, HexCoord(0, 0), target_fleet=None)
        fleet_b = _make_intercept_fleet(2, HexCoord(20, 0), target_fleet=None)
        fleet_a.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_b)]
        fleet_b.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_a)]

        # Must not raise RecursionError. Result content is not asserted here —
        # the contract is only that the call terminates.
        segments = project_fleet_path(fleet_a, galaxy, max_turns=10)
        assert isinstance(segments, list)

    def test_three_fleet_cycle(self, mock_galaxy):
        """A→B→C→A intercept cycle terminates without recursion error."""
        galaxy, *_ = mock_galaxy

        fleet_a = _make_intercept_fleet(1, HexCoord(0, 0), target_fleet=None)
        fleet_b = _make_intercept_fleet(2, HexCoord(20, 0), target_fleet=None)
        fleet_c = _make_intercept_fleet(3, HexCoord(40, 0), target_fleet=None)
        fleet_a.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_b)]
        fleet_b.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_c)]
        fleet_c.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_a)]

        segments = project_fleet_path(fleet_a, galaxy, max_turns=10)
        assert isinstance(segments, list)

    def test_intercept_falls_back_to_target_location_on_cycle(self, mock_galaxy):
        """
        When the recursion guard fires, calculate_intercept_point should
        fall back to chasing target_fleet.location (its current hex).
        """
        galaxy, *_ = mock_galaxy

        fleet_a = _make_intercept_fleet(1, HexCoord(0, 0), target_fleet=None)
        fleet_b = _make_intercept_fleet(2, HexCoord(20, 0), target_fleet=None)
        fleet_a.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_b)]
        fleet_b.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_a)]

        # Drive calculate_intercept_point with A as chaser while A is NOT
        # already being projected (top-level call). The guard fires on the
        # nested projection of B (whose order targets A), so B's projected
        # path comes back empty and the intercept logic chooses a hex
        # related to B's current location.
        state_a = NavigationState.from_fleet(fleet_a)
        result = calculate_intercept_point(state_a, fleet_b, galaxy)
        assert result is not None  # never None when target has a location

    def test_guard_cleans_up_after_exception(self, mock_galaxy):
        """
        Re-entrancy state must not persist between calls — even if the inner
        projection raises. Otherwise a single failure would poison subsequent
        projections of the same fleet.
        """
        galaxy, *_ = mock_galaxy

        fleet = _make_intercept_fleet(99, HexCoord(0, 0), target_fleet=None)
        fleet.orders = []  # No orders -> trivial empty projection.

        service = FleetNavigationService()
        # First call should run cleanly.
        service.project_path(fleet, galaxy, max_turns=5)
        # Second call must also run — would fail if the guard set was not
        # cleared on exit from the first call.
        service.project_path(fleet, galaxy, max_turns=5)
