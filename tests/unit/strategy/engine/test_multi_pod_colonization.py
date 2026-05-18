"""Tests for multi-pod sequential colonization.

Phase 5: A ship with multiple drop pods can queue multiple COLONIZE orders
and colonize multiple planets sequentially.
"""
from unittest.mock import MagicMock
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.validation.colonize_validator import ColonizeValidator
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord


def _drop_pod(name="Colony Pod", mass=500.0):
    return {'vehicle_type': 'drop_pod', 'name': name, 'mass': mass, 'design_id': 'colony_pod'}


def _make_ship(num_pods=1):
    """PROJ-436 Phase 9: ship stub with typed ``bay_inventory.pods``.

    The legacy ``carried_items`` mirror is gone — the validator reads
    the typed pods slot directly since PROJ-431 Phase 1d.
    """
    ship = MagicMock()
    pods_data = [_drop_pod() for _ in range(num_pods)]
    ship.bay_inventory = BayInventory(
        bay=[],
        pods=[
            DropPod(
                design_id=p["design_id"],
                design_data={},
                mass=p["mass"],
                payload={"name": p["name"], "vehicle_type": "drop_pod"},
            )
            for p in pods_data
        ],
    )
    return ship


def _make_fleet(ships, orders=None):
    fleet = MagicMock()
    fleet.ships = ships
    fleet.orders = list(orders or [])
    fleet.location = HexCoord(0, 0)
    return fleet


def _make_planet(name="Planet", planet_id=1):
    planet = MagicMock()
    planet.id = planet_id
    planet.name = name
    planet.owner_id = None
    planet.location = HexCoord(0, 0)
    return planet


class TestMultiPodCounting:
    """Test that pod counting works correctly for multi-pod ships."""

    def test_ship_with_three_pods(self):
        ship = _make_ship(num_pods=3)
        fleet = _make_fleet([ship])
        assert ColonizeValidator.count_drop_pods(fleet) == 3

    def test_pods_across_multiple_ships(self):
        ship1 = _make_ship(num_pods=2)
        ship2 = _make_ship(num_pods=1)
        fleet = _make_fleet([ship1, ship2])
        assert ColonizeValidator.count_drop_pods(fleet) == 3


class TestMultiPodChainValidation:
    """Test that chain validation allows multiple colonize orders up to pod count."""

    def test_three_pods_allows_three_orders(self):
        ship = _make_ship(num_pods=3)
        fleet = _make_fleet([ship])

        # Queue 2 COLONIZE orders
        fleet.orders = [
            Order(OrderType.COLONIZE, target=_make_planet("P1", 1)),
            Order(OrderType.COLONIZE, target=_make_planet("P2", 2)),
        ]

        committed = ColonizeValidator.count_committed_colonize_orders(fleet)
        available = ColonizeValidator.count_drop_pods(fleet)

        # 2 committed, 3 available → can queue 1 more
        assert committed == 2
        assert available == 3
        assert committed < available

    def test_three_pods_rejects_fourth_order(self):
        ship = _make_ship(num_pods=3)
        fleet = _make_fleet([ship])

        # Queue 3 COLONIZE orders (= all pods)
        fleet.orders = [
            Order(OrderType.COLONIZE, target=_make_planet("P1", 1)),
            Order(OrderType.COLONIZE, target=_make_planet("P2", 2)),
            Order(OrderType.COLONIZE, target=_make_planet("P3", 3)),
        ]

        committed = ColonizeValidator.count_committed_colonize_orders(fleet)
        available = ColonizeValidator.count_drop_pods(fleet)

        # 3 committed, 3 available → cannot queue more
        assert committed == 3
        assert available == 3
        assert committed >= available

    def test_pod_consumed_allows_new_order(self):
        """After consuming a pod (colonization), a new order can be queued."""
        ship = _make_ship(num_pods=2)
        fleet = _make_fleet([ship])

        # Queue 2 orders
        fleet.orders = [
            Order(OrderType.COLONIZE, target=_make_planet("P1", 1)),
            Order(OrderType.COLONIZE, target=_make_planet("P2", 2)),
        ]
        assert ColonizeValidator.count_committed_colonize_orders(fleet) == 2
        assert ColonizeValidator.count_drop_pods(fleet) == 2

        # Simulate first colonization: remove 1 pod and 1 order.
        ship.bay_inventory = BayInventory(
            bay=list(ship.bay_inventory.bay), pods=ship.bay_inventory.pods[1:]
        )
        fleet.orders.pop(0)

        # Now: 1 pod, 1 committed order → at limit, cannot add more
        assert ColonizeValidator.count_drop_pods(fleet) == 1
        assert ColonizeValidator.count_committed_colonize_orders(fleet) == 1

        # After second colonization: 0 pods, 0 orders
        ship.bay_inventory = BayInventory(
            bay=list(ship.bay_inventory.bay), pods=ship.bay_inventory.pods[1:]
        )
        fleet.orders.pop(0)
        assert ColonizeValidator.count_drop_pods(fleet) == 0
        assert ColonizeValidator.count_committed_colonize_orders(fleet) == 0


class TestMultiPodWithDictTarget:
    """Test that multi-pod colonization works with dict targets (population/cargo amounts)."""

    def test_dict_target_colonize_orders_counted(self):
        """COLONIZE orders with dict targets should still count toward committed pods."""
        ship = _make_ship(num_pods=2)
        fleet = _make_fleet([ship])

        # Mix of plain and dict targets
        fleet.orders = [
            Order(OrderType.COLONIZE, target=_make_planet("P1", 1)),
            Order(OrderType.COLONIZE, target={
                'planet': _make_planet("P2", 2),
                'population': 500,
                'cargo': {'metals': 100},
            }),
        ]

        committed = ColonizeValidator.count_committed_colonize_orders(fleet)
        assert committed == 2
