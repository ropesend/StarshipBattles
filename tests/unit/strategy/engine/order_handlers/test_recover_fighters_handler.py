"""PROJ-FMS-C Phase 3 — RecoverFightersOrderHandler tests.

Covers:
- Recovery moves N fighters from fighter_group to carrier's bay.
- HP preserved per fighter.
- Partial recovery when bay capacity limits the count.
- Empty fighter_group is pruned from empire.fleets.
- Invalid payload / missing fighter_group fails cleanly.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_handlers.recover_fighters import (
    RecoverFightersOrderHandler,
)


class _StubCargoMgr:
    """Cargo manager stub with configurable bay capacity.

    Mimics ``ShipCargoManager.load_vehicle`` semantics: returns False
    when capacity is exceeded; otherwise appends a serialized
    CarriedVehicle dict to ``carrier.carried_items``.
    """

    def __init__(self, carrier, *, capacity: int = 999):
        self._carrier = carrier
        self._capacity = capacity

    def load_vehicle(self, cv) -> bool:
        if len(self._carrier.carried_items) >= self._capacity:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        return True


class _StubCarrier:
    """Minimal ShipInstance-like carrier."""

    def __init__(self, instance_id: str, owner_id: int, capacity: int = 999):
        self.instance_id = instance_id
        self.design_id = "stub_design"
        self.owner_id = owner_id
        self.name = instance_id
        self.design_data = {}
        self.current_hp = 100
        self.is_alive = True
        self.is_derelict = False
        self.carried_items = []
        self._registries = None
        self._cargo_mgr = _StubCargoMgr(self, capacity=capacity)


def _make_deployed_fighter(instance_id: str, hp: int = 80) -> ShipInstance:
    """Build a deployed fighter ShipInstance with explicit HP."""
    fighter = ShipInstance(
        instance_id=instance_id,
        design_id="fighter_alpha",
        name=instance_id,
        owner_id=42,
        design_data={
            "name": "fighter_alpha",
            "ship_class": "Fighter (Small)",
            "vehicle_class": "Fighter (Small)",
            "vehicle_type": "Fighter",
            "mass": 20.0,
        },
        current_hp=hp,
    )
    return fighter


@pytest.fixture
def setup_carrier_and_group():
    """Owner with a carrier (10 bay slots) and a fighter_group of 5."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=10)
    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)

    fg = Fleet(
        fleet_id=200001, owner_id=42, location=hex_c, speed=0.0,
        group_kind="fighter_group",
    )
    for i in range(5):
        fg.ships.append(_make_deployed_fighter(f"fighter_{i}", hp=80 - i * 5))

    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet, fg])
    galaxy = SimpleNamespace(current_turn=1)
    return empire, main_fleet, carrier, fg, galaxy


def test_supported_order_types():
    h = RecoverFightersOrderHandler()
    assert h.supported_order_types == (OrderType.RECOVER_FIGHTERS,)


def test_recover_all_fighters_into_bay(setup_carrier_and_group):
    empire, fleet, carrier, fg, galaxy = setup_carrier_and_group
    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": None,  # all
    }))

    handler = RecoverFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    # All 5 fighters in the carrier's bay (CarriedVehicle dicts).
    assert len(carrier.carried_items) == 5
    # Empty fighter_group pruned from empire's fleets list.
    assert fg not in empire.fleets


def test_partial_recovery_when_bay_capacity_limits(setup_carrier_and_group):
    empire, fleet, carrier, fg, galaxy = setup_carrier_and_group
    # Shrink the bay to 3 slots so only 3 of 5 can land.
    carrier._cargo_mgr = _StubCargoMgr(carrier, capacity=3)

    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": None,
    }))

    handler = RecoverFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 3
    # 2 fighters remain in the group.
    assert len(fg.ships) == 2
    # fighter_group still in empire.fleets (non-empty).
    assert fg in empire.fleets


def test_hp_preserved_through_round_trip(setup_carrier_and_group):
    empire, fleet, carrier, fg, galaxy = setup_carrier_and_group
    # Distinct HPs: 80, 75, 70, 65, 60.
    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": None,
    }))
    handler = RecoverFightersOrderHandler()
    handler.execute_action_order(fleet, empire, galaxy)

    hps = sorted(int(item["current_hp"]) for item in carrier.carried_items)
    assert hps == [60, 65, 70, 75, 80]


def test_recover_count_limit(setup_carrier_and_group):
    empire, fleet, carrier, fg, galaxy = setup_carrier_and_group
    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": 2,
    }))
    handler = RecoverFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 2
    assert len(fg.ships) == 3
    assert fg in empire.fleets


def test_missing_fighter_group_fails_cleanly(setup_carrier_and_group):
    empire, fleet, carrier, fg, galaxy = setup_carrier_and_group
    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": 999999,  # doesn't exist
        "count": None,
    }))
    handler = RecoverFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success


def test_invalid_payload_fails_cleanly(setup_carrier_and_group):
    empire, fleet, carrier, fg, galaxy = setup_carrier_and_group
    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target=None))

    handler = RecoverFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success
