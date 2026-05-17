"""PROJ-FMS-D Phase 3 — strategic launch -> recover round trip for satellites.

Mirrors :mod:`test_fms_c_e2e` but operates on satellites + the new
PROJ-FMS-D handlers / ability gates.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import SatelliteConstellation
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_handlers.launch_satellites import (
    LaunchSatellitesOrderHandler,
)
from game.strategy.engine.order_handlers.recover_satellites import (
    RecoverSatellitesOrderHandler,
)


class _StubCargoMgr:
    def __init__(self, carrier, *, capacity: int = 10,
                 accepts: tuple[str, ...] = ("satellite", "fighter")):
        self._carrier = carrier
        self._capacity = capacity
        self._accepts = accepts

    def load_vehicle(self, cv) -> bool:
        if len(self._carrier.carried_items) >= self._capacity:
            return False
        if cv.vehicle_type not in self._accepts:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        return True


class _StubCarrier:
    def __init__(self, instance_id: str, owner_id: int, *,
                 capacity: int = 10,
                 accepts: tuple[str, ...] = ("satellite", "fighter")):
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
        self._cargo_mgr = _StubCargoMgr(self, capacity=capacity, accepts=accepts)

    # PROJ-431 Phase 1f: production callers read carried inventory via
    # the typed BayInventory. Derive it from the raw ``carried_items``
    # list so existing tests keep working.
    @property
    def bay_inventory(self):
        from game.strategy.data.bay_inventory import BayInventory, DropPod
        from game.strategy.data.carried_vehicle import (
            VALID_VEHICLE_TYPES, CarriedVehicle,
        )
        bay = []
        pods = []
        for item in self.carried_items:
            if isinstance(item, CarriedVehicle):
                bay.append(item)
            elif isinstance(item, dict) and str(
                item.get("vehicle_type", "")
            ).lower() in VALID_VEHICLE_TYPES:
                bay.append(CarriedVehicle.from_dict(item))
            elif isinstance(item, dict):
                pods.append(DropPod(
                    design_id=str(item.get("design_id", "")),
                    design_data=dict(item.get("design_data", {})),
                    mass=float(item.get("mass", 0.0)),
                    payload={
                        k: v for k, v in item.items()
                        if k not in {"design_id", "design_data", "mass"}
                    },
                ))
        return BayInventory(bay=bay, pods=pods)

    def set_bay_inventory(self, bi) -> None:
        new_items = [cv.to_dict() for cv in bi.bay]
        for pod in bi.pods:
            entry = {
                "design_id": pod.design_id,
                "design_data": pod.design_data,
                "mass": pod.mass,
            }
            entry.update(pod.payload)
            new_items.append(entry)
        self.carried_items = new_items


def _make_satellite_dict(design_id: str, hp: int = 60, mass: float = 30.0):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "ship_class": "Satellite",
            "vehicle_class": "Satellite",
            "vehicle_type": "Satellite",
        },
        "vehicle_type": "satellite",
        "mass": mass,
        "current_hp": hp,
    }


def test_strategic_launch_then_recover_round_trip_preserves_hp():
    """Load 4 satellites in a carrier, strategic-launch, recover all.

    HP is preserved across the round trip.
    """
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=10)
    for i in range(4):
        carrier.carried_items.append(
            _make_satellite_dict("sat_alpha", hp=80 - i * 5),
        )

    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)
    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet], deployed_groups=[])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    # Strategic launch all 4 satellites.
    main_fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 4,
        "target_hex": hex_c,
    }))
    launch = LaunchSatellitesOrderHandler()
    result = launch.execute_action_order(main_fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 0
    sg = empire.deployed_groups_of(SatelliteConstellation)[0]
    assert len(sg.ships) == 4
    pre_recovery_hps = sorted(s.current_hp for s in sg.ships)

    # Strategic recover all 4.
    main_fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    recover = RecoverSatellitesOrderHandler()
    result = recover.execute_action_order(main_fleet, empire, galaxy)
    assert result.success
    assert sg not in empire.fleets  # empty group pruned
    post_recovery_hps = sorted(
        int(item["current_hp"]) for item in carrier.carried_items
    )
    assert post_recovery_hps == pre_recovery_hps


def test_partial_recovery_leaves_overflow_in_satellite_group():
    """Capacity-limited recovery: 2 of 3 land, 1 remains in the group."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=2)
    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)

    sg = SatelliteConstellation(group_id=300042, owner_id=42, location=hex_c)
    for i in range(3):
        sg.ships.append(ShipInstance(
            instance_id=f"sat_{i}",
            design_id="sat_alpha",
            name=f"sat_{i}",
            owner_id=42,
            design_data={"name": "sat_alpha", "mass": 30.0},
            current_hp=70 - i * 5,
        ))

    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet], deployed_groups=[sg])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    main_fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    recover = RecoverSatellitesOrderHandler()
    result = recover.execute_action_order(main_fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 2
    assert len(sg.ships) == 1
    assert sg in empire.deployed_groups


def test_satellite_group_id_namespace_distinct_from_fighter_group():
    """Strategic-launched satellite_group uses 300000+; not 200000+."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=10)
    carrier.carried_items.append(_make_satellite_dict("sat_alpha"))

    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)
    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet], deployed_groups=[])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    main_fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 1,
        "target_hex": hex_c,
    }))
    LaunchSatellitesOrderHandler().execute_action_order(
        main_fleet, empire, galaxy,
    )
    sg = empire.deployed_groups_of(SatelliteConstellation)[0]
    assert sg.id >= 300000
    assert sg.id < 400000


def test_launched_satellite_group_satellites_have_no_battle_tag():
    """Strategic launches do not set ``launched_in_battle_id``."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=10)
    carrier.carried_items.append(_make_satellite_dict("sat_alpha"))

    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)
    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet], deployed_groups=[])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    main_fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 1,
        "target_hex": hex_c,
    }))
    LaunchSatellitesOrderHandler().execute_action_order(
        main_fleet, empire, galaxy,
    )
    sg = empire.deployed_groups_of(SatelliteConstellation)[0]
    for ship in sg.ships:
        assert getattr(ship, "launched_in_battle_id", None) is None
