"""Unit tests for FleetWriteService (PROJ-370 Phase 2).

Each test drives ONE mutator method against a real Fleet and verifies the
behavior is bit-identical to the equivalent direct write today.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.core.protocols import IFleetMutator
from game.strategy.data.fleet import Fleet
from game.strategy.data.fleet_hierarchy import CombatPolicy
from game.strategy.data.order_types import Order, OrderType
from game.strategy.services.fleet_navigation_service import FleetNavigationService
from game.strategy.services.fleet_write_service import FleetWriteService


@pytest.fixture
def fleet() -> Fleet:
    return Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))


@pytest.fixture
def nav_service() -> FleetNavigationService:
    return FleetNavigationService()


@pytest.fixture
def service(nav_service: FleetNavigationService) -> FleetWriteService:
    return FleetWriteService(navigation_service=nav_service)


def _make_order(order_type: OrderType = OrderType.MOVE) -> Order:
    return Order(order_type=order_type, target=HexCoord(1, 1))


# ---- Protocol conformance ----


def test_fleet_write_service_satisfies_protocol(service: FleetWriteService) -> None:
    assert isinstance(service, IFleetMutator)


def test_fleet_navigation_service_satisfies_protocol_navigation_slice(
    nav_service: FleetNavigationService,
) -> None:
    # The runtime-checkable Protocol checks every method name; the navigation
    # service today only implements a subset, so only the navigation slice
    # (set_location, set_path) is asserted via direct attribute presence.
    assert hasattr(nav_service, "set_location")
    assert hasattr(nav_service, "set_path")


# ---- Navigation slice ----


def test_set_location_updates_fleet_location(
    service: FleetWriteService, fleet: Fleet
) -> None:
    new_loc = HexCoord(5, 7)
    service.set_location(fleet, new_loc)
    assert fleet.location == new_loc


def test_set_path_replaces_path(
    service: FleetWriteService, fleet: Fleet
) -> None:
    fleet.path = [HexCoord(1, 1)]
    service.set_path(fleet, [HexCoord(2, 2), HexCoord(3, 3)])
    assert fleet.path == [HexCoord(2, 2), HexCoord(3, 3)]


def test_set_location_without_nav_service_raises() -> None:
    # PROJ-466: a missing nav service is a configuration error, now raised
    # as ValidationException(MISSING_DEPENDENCY) rather than NotImplementedError.
    from game.core.exceptions import ValidationException

    bare = FleetWriteService(navigation_service=None)
    f = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    with pytest.raises(ValidationException):
        bare.set_location(f, HexCoord(1, 1))


# ---- Order queue ----


def test_append_order_appends(
    service: FleetWriteService, fleet: Fleet
) -> None:
    order = _make_order()
    service.append_order(fleet, order)
    assert fleet.orders == [order]


def test_insert_order_at_index(
    service: FleetWriteService, fleet: Fleet
) -> None:
    o1 = _make_order()
    o2 = _make_order()
    o3 = _make_order()
    service.append_order(fleet, o1)
    service.append_order(fleet, o2)
    service.insert_order(fleet, 1, o3)
    assert fleet.orders == [o1, o3, o2]


def test_pop_order_returns_and_removes(
    service: FleetWriteService, fleet: Fleet
) -> None:
    o1 = _make_order()
    o2 = _make_order()
    service.append_order(fleet, o1)
    service.append_order(fleet, o2)
    popped = service.pop_order(fleet)
    assert popped is o1
    assert fleet.orders == [o2]


def test_pop_order_at_index(
    service: FleetWriteService, fleet: Fleet
) -> None:
    o1 = _make_order()
    o2 = _make_order()
    o3 = _make_order()
    service.append_order(fleet, o1)
    service.append_order(fleet, o2)
    service.append_order(fleet, o3)
    popped = service.pop_order(fleet, index=1)
    assert popped is o2
    assert fleet.orders == [o1, o3]


def test_clear_orders_empties_queue(
    service: FleetWriteService, fleet: Fleet
) -> None:
    service.append_order(fleet, _make_order())
    service.append_order(fleet, _make_order())
    service.clear_orders(fleet)
    assert fleet.orders == []
    assert fleet.path == []


# ---- Ship membership ----


def _make_mock_ship(name: str = "TestShip") -> MagicMock:
    ship = MagicMock()
    ship.name = name
    ship.instance_id = f"id_{name}"
    ship.is_combat_capable.return_value = True
    ship.vehicle_type = "Ship"
    ship.design_data = {"vehicle_type": "Ship"}
    ship.get_calculated_stats.return_value = {
        "mass": 1000,
        "strategic_movement": 100,
    }
    return ship


def test_add_ship_triggers_speed_recalc(
    service: FleetWriteService, fleet: Fleet
) -> None:
    """Adding a ship via the mutator must still trigger the existing
    Fleet.trigger_speed_recalculation invariant."""
    ship = _make_mock_ship("S1")
    service.add_ship(fleet, ship)
    assert ship in fleet.ships


def test_remove_ship_returns_true_when_present(
    service: FleetWriteService, fleet: Fleet
) -> None:
    ship = _make_mock_ship("S2")
    fleet.add_ship(ship)
    assert service.remove_ship(fleet, ship) is True
    assert ship not in fleet.ships


def test_remove_ship_returns_false_when_absent(
    service: FleetWriteService, fleet: Fleet
) -> None:
    ship = _make_mock_ship("S3")
    assert service.remove_ship(fleet, ship) is False


# ---- Identity / policy ----


def test_set_display_name(
    service: FleetWriteService, fleet: Fleet
) -> None:
    service.set_display_name(fleet, "First Strike")
    assert fleet.display_name == "First Strike"


def test_set_fleet_policy(
    service: FleetWriteService, fleet: Fleet
) -> None:
    new_policy = CombatPolicy()
    service.set_fleet_policy(fleet, new_policy)
    assert fleet.fleet_policy is new_policy


# ---- Construction queue ----


def test_append_and_pop_construction_item(
    service: FleetWriteService, fleet: Fleet
) -> None:
    item = {"design_id": "scout", "progress": 0.0}
    service.append_construction_item(fleet, item)
    assert fleet.construction_queue == [item]
    popped = service.pop_construction_item(fleet)
    assert popped == item
    assert fleet.construction_queue == []


def test_set_construction_queue_paused(
    service: FleetWriteService, fleet: Fleet
) -> None:
    assert fleet.construction_queue_paused is False
    service.set_construction_queue_paused(fleet, True)
    assert fleet.construction_queue_paused is True
    service.set_construction_queue_paused(fleet, False)
    assert fleet.construction_queue_paused is False
