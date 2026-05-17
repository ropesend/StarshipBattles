"""PROJ-FMS-D Phase 2 — RecoverSatellitesOrderHandler tests."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_handlers.recover_satellites import (
    RecoverSatellitesOrderHandler,
)


class _StubCargoMgr:
    """Cargo manager stub that gates on vehicle_type AND capacity."""

    def __init__(self, carrier, *, capacity: int = 999,
                 accepts_satellite: bool = True,
                 accepts_fighter: bool = False):
        self._carrier = carrier
        self._capacity = capacity
        self._accepts_satellite = accepts_satellite
        self._accepts_fighter = accepts_fighter

    def load_vehicle(self, cv) -> bool:
        if len(self._carrier.carried_items) >= self._capacity:
            return False
        if cv.vehicle_type == "satellite" and not self._accepts_satellite:
            return False
        if cv.vehicle_type == "fighter" and not self._accepts_fighter:
            return False
        self._carrier.carried_items.append(cv.to_dict())
        return True


class _StubCarrier:
    """Minimal ShipInstance-like carrier."""

    def __init__(self, instance_id: str, owner_id: int, capacity: int = 999,
                 accepts_satellite: bool = True,
                 accepts_fighter: bool = False):
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
        self._cargo_mgr = _StubCargoMgr(
            self, capacity=capacity,
            accepts_satellite=accepts_satellite,
            accepts_fighter=accepts_fighter,
        )

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


def _make_deployed_satellite(instance_id: str, hp: int = 80) -> ShipInstance:
    sat = ShipInstance(
        instance_id=instance_id,
        design_id="sat_alpha",
        name=instance_id,
        owner_id=42,
        design_data={
            "name": "sat_alpha",
            "vehicle_class": "Satellite",
            "vehicle_type": "Satellite",
            "mass": 30.0,
        },
        current_hp=hp,
    )
    return sat


@pytest.fixture
def setup_carrier_and_satellite_group():
    """Carrier with satellite-only bay (capacity 10) + satellite_group of 5."""
    hex_c = HexCoord(0, 0)
    carrier = _StubCarrier("carrier_1", owner_id=42, capacity=10,
                            accepts_satellite=True, accepts_fighter=False)
    main_fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    main_fleet.ships.append(carrier)

    sg = Fleet(
        fleet_id=300001, owner_id=42, location=hex_c, speed=0.0,
        group_kind="satellite_group",
    )
    for i in range(5):
        sg.ships.append(_make_deployed_satellite(f"sat_{i}", hp=80 - i * 5))

    empire = SimpleNamespace(id=42, name="E42", fleets=[main_fleet, sg])
    galaxy = SimpleNamespace(current_turn=1)
    return empire, main_fleet, carrier, sg, galaxy


def test_supported_order_types():
    h = RecoverSatellitesOrderHandler()
    assert h.supported_order_types == (OrderType.RECOVER_SATELLITES,)


def test_recover_all_satellites_into_bay(setup_carrier_and_satellite_group):
    empire, fleet, carrier, sg, galaxy = setup_carrier_and_satellite_group
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    handler = RecoverSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 5
    # Empty satellite_group pruned.
    assert sg not in empire.fleets


def test_partial_recovery_when_bay_capacity_limits(setup_carrier_and_satellite_group):
    empire, fleet, carrier, sg, galaxy = setup_carrier_and_satellite_group
    carrier._cargo_mgr = _StubCargoMgr(
        carrier, capacity=3, accepts_satellite=True, accepts_fighter=False,
    )
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    handler = RecoverSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 3
    assert len(sg.ships) == 2
    assert sg in empire.fleets


def test_hp_preserved_through_round_trip(setup_carrier_and_satellite_group):
    empire, fleet, carrier, sg, galaxy = setup_carrier_and_satellite_group
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    handler = RecoverSatellitesOrderHandler()
    handler.execute_action_order(fleet, empire, galaxy)
    hps = sorted(int(item["current_hp"]) for item in carrier.carried_items)
    assert hps == [60, 65, 70, 75, 80]


def test_recover_count_limit(setup_carrier_and_satellite_group):
    empire, fleet, carrier, sg, galaxy = setup_carrier_and_satellite_group
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": 2,
    }))
    handler = RecoverSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 2
    assert len(sg.ships) == 3
    assert sg in empire.fleets


def test_missing_satellite_group_fails_cleanly(setup_carrier_and_satellite_group):
    empire, fleet, carrier, sg, galaxy = setup_carrier_and_satellite_group
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": 999999,  # doesn't exist
        "count": None,
    }))
    handler = RecoverSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success


def test_invalid_payload_fails_cleanly(setup_carrier_and_satellite_group):
    empire, fleet, carrier, sg, galaxy = setup_carrier_and_satellite_group
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target=None))
    handler = RecoverSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success


def test_carrier_with_fighter_only_bay_cannot_recover_satellites(
    setup_carrier_and_satellite_group,
):
    """Bay type-filter: a fighter-only carrier fails to load satellites.

    Closes the PROJ-FMS-D cross-type isolation contract — a ship with
    no satellite-accepting bay can't recover satellites even if it has
    the RecoverSatellitesAbility (the command-handler ability-gate is a
    separate concern; here we test the bay filter inside the handler).
    """
    empire, fleet, carrier, sg, galaxy = setup_carrier_and_satellite_group
    # Reconfigure carrier: fighter-only bay (rejects satellites).
    carrier._cargo_mgr = _StubCargoMgr(
        carrier, capacity=10, accepts_satellite=False, accepts_fighter=True,
    )
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    handler = RecoverSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success
    # Satellites still in their group; nothing loaded.
    assert len(carrier.carried_items) == 0
    assert len(sg.ships) == 5
    assert sg in empire.fleets
