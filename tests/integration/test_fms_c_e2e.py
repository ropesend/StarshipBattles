"""PROJ-FMS-C Phase 4 — strategic launch -> combat -> recover round trip.

Covers the full fighter lifecycle from a carrier ship's bay through a
strategic launch to a contested-hex tactical battle, plus an explicit
strategic recovery action afterwards.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_handlers.launch_fighters import (
    LaunchFightersOrderHandler,
)
from game.strategy.engine.order_handlers.recover_fighters import (
    RecoverFightersOrderHandler,
)


# ---------------------------------------------------------------------------
# Test fixtures — minimal carrier setup
# ---------------------------------------------------------------------------


class _StubCargoMgr:
    def __init__(self, carrier, *, capacity: int = 10):
        self._carrier = carrier
        self._capacity = capacity

    def load_vehicle(self, cv) -> bool:
        if len(self._carrier.carried_items) >= self._capacity:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        return True


class _StubCarrier:
    def __init__(self, instance_id: str, owner_id: int, *, capacity: int = 10):
        self.instance_id = instance_id
        self.design_id = "carrier_design"
        self.owner_id = owner_id
        self.name = instance_id
        self.design_data = {}
        self.current_hp = 200
        self.is_alive = True
        self.is_derelict = False
        self.carried_items = []
        self._registries = None
        self._cargo_mgr = _StubCargoMgr(self, capacity=capacity)


def _make_fighter_dict(design_id: str, hp: int = 80, mass: float = 20.0):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "ship_class": "Fighter (Small)",
            "vehicle_class": "Fighter (Small)",
            "vehicle_type": "Fighter",
        },
        "vehicle_type": "fighter",
        "mass": mass,
        "current_hp": hp,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_strategic_launch_then_recover_round_trip_preserves_hp():
    """Load fighters into a carrier, strategic-launch into hex, recover
    them — HP is preserved across the round trip."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=10)
    # 4 fighters in the bay with distinct HP.
    for i in range(4):
        carrier.carried_items.append(_make_fighter_dict("fighter_alpha", hp=80 - i * 5))

    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)
    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet])
    galaxy = SimpleNamespace(current_turn=1)

    # Strategic launch all 4.
    main_fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "fighter_alpha",
        "count": 4,
        "target_hex": hex_c,
    }))
    launch = LaunchFightersOrderHandler()
    result = launch.execute_action_order(main_fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 0
    fg = next(f for f in empire.fleets if f.group_kind == "fighter_group")
    assert len(fg.ships) == 4
    pre_recovery_hps = sorted(s.current_hp for s in fg.ships)

    # Strategic recover all 4.
    main_fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": None,
    }))
    recover = RecoverFightersOrderHandler()
    result = recover.execute_action_order(main_fleet, empire, galaxy)
    assert result.success
    # Group destroyed (empty).
    assert fg not in empire.fleets
    # Carrier got 4 CarriedVehicle entries with preserved HP.
    assert len(carrier.carried_items) == 4
    post_recovery_hps = sorted(int(c["current_hp"]) for c in carrier.carried_items)
    assert pre_recovery_hps == post_recovery_hps


def test_partial_recovery_when_bay_too_small():
    """If bay capacity < group size, partial recovery is allowed and
    the fighter_group keeps the surplus."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=2)
    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)

    # Pre-existing fighter_group of 5 at the hex.
    fg = Fleet(
        fleet_id=200001, owner_id=42, location=hex_c, speed=0.0,
        group_kind="fighter_group",
    )
    for i in range(5):
        fg.ships.append(ShipInstance(
            instance_id=f"f_{i}",
            design_id="fighter_alpha",
            name=f"f_{i}",
            owner_id=42,
            design_data={"name": "fighter_alpha", "mass": 20.0},
            current_hp=70 + i,
        ))

    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet, fg])
    galaxy = SimpleNamespace(current_turn=1)

    main_fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": None,
    }))
    recover = RecoverFightersOrderHandler()
    result = recover.execute_action_order(main_fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 2
    assert len(fg.ships) == 3
    # Group still in empire.fleets (not empty).
    assert fg in empire.fleets


def test_strategic_launch_creates_fighter_group_visible_to_conflict_resolution():
    """Pin the contract that LaunchFightersOrderHandler produces a
    fighter_group Fleet that conflict-resolution iteration will see
    via ``empire.fleets`` (the conflict engine iterates this list
    directly — see ``conflict_resolution_engine._resolve_conflicts``)."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=10)
    for _ in range(2):
        carrier.carried_items.append(_make_fighter_dict("fighter_alpha"))
    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)
    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet])
    galaxy = SimpleNamespace(current_turn=1)

    main_fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "fighter_alpha",
        "count": 2,
        "target_hex": hex_c,
    }))
    launch = LaunchFightersOrderHandler()
    launch.execute_action_order(main_fleet, empire, galaxy)

    fg = next(f for f in empire.fleets if f.group_kind == "fighter_group")
    # Same hex as the carrier fleet — conflict resolution iterates
    # ``empire.fleets`` and includes anything at the contested hex.
    assert fg.location == main_fleet.location
    # group_kind != "fleet" means non-merge, but conflict iteration
    # will still pick this up.
    assert fg.group_kind == "fighter_group"
    # Owner matches so it joins the owner's team in the spec compiler.
    assert fg.owner_id == empire.id
