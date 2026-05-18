"""PROJ-FMS-D Phase 3 — cross-type isolation tests.

Pins the design's "separate ability gates per unit type" contract:

- A carrier with ``RecoverFightersAbility`` but NO satellite bay /
  ``RecoverSatellitesAbility`` cannot recover satellites — the
  RecoverSatellitesOrderHandler refuses to load CVs into the carrier
  even though the order is queued.
- A carrier with only fighter bay rejects satellite CVs (and vice versa).
- A carrier with both ability sets + universal bay handles both.
- The command-handler ability gating sits at a different layer (action-
  time resolver via ``ORDER_TO_ABILITY_MAP``); the test for that lives
  in :mod:`tests.unit.strategy.engine.test_command_registry_contract`.
  Here we drive only the order-handler-side behavior.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import FighterWing, SatelliteConstellation
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_handlers.launch_satellites import (
    LaunchSatellitesOrderHandler,
)
from game.strategy.engine.order_handlers.launch_fighters import (
    LaunchFightersOrderHandler,
)
from game.strategy.engine.order_handlers.recover_fighters import (
    RecoverFightersOrderHandler,
)
from game.strategy.engine.order_handlers.recover_satellites import (
    RecoverSatellitesOrderHandler,
)


class _StubCargoMgr:
    """Bay stub that gates on a tuple of accepted vehicle types."""

    def __init__(self, carrier, *, capacity: int = 10,
                 accepts: tuple[str, ...] = ("fighter", "satellite")):
        self._carrier = carrier
        self._capacity = capacity
        self._accepts = accepts

    def load_vehicle(self, cv) -> bool:
        # PROJ-436 Phase 9: load into the typed BayInventory.bay slot.
        if len(self._carrier.bay_inventory.bay) >= self._capacity:
            return False
        if cv.vehicle_type not in self._accepts:
            return False
        self._carrier.bay_inventory.bay.append(cv)
        return True


def _make_carrier(instance_id: str, owner_id: int, *,
                   capacity: int = 10,
                   accepts: tuple[str, ...] = ("fighter", "satellite")):
    carrier = ShipInstance(
        instance_id=instance_id,
        design_id="carrier_design",
        name=instance_id,
        owner_id=owner_id,
        design_data={},
        current_hp=200,
    )
    carrier._cargo_mgr = _StubCargoMgr(
        carrier, capacity=capacity, accepts=accepts,
    )
    return carrier


def _fighter_dict(design_id: str = "fighter_alpha", hp: int = 70):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id, "vehicle_class": "Fighter (Small)",
            "vehicle_type": "Fighter",
        },
        "vehicle_type": "fighter",
        "mass": 20.0,
        "current_hp": hp,
    }


def _satellite_dict(design_id: str = "sat_alpha", hp: int = 60):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id, "vehicle_class": "Satellite (Small)",
            "vehicle_type": "Satellite",
        },
        "vehicle_type": "satellite",
        "mass": 30.0,
        "current_hp": hp,
    }


def _deployed_satellite(instance_id: str, hp: int = 60) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="sat_alpha",
        name=instance_id,
        owner_id=42,
        design_data={
            "name": "sat_alpha", "vehicle_class": "Satellite (Small)",
            "vehicle_type": "Satellite", "mass": 30.0,
        },
        current_hp=hp,
    )


def _deployed_fighter(instance_id: str, hp: int = 70) -> ShipInstance:
    return ShipInstance(
        instance_id=instance_id,
        design_id="fighter_alpha",
        name=instance_id,
        owner_id=42,
        design_data={
            "name": "fighter_alpha", "vehicle_class": "Fighter (Small)",
            "vehicle_type": "Fighter", "mass": 20.0,
        },
        current_hp=hp,
    )


def test_fighter_only_bay_cannot_recover_satellites():
    """Carrier accepts fighters only → satellite recovery fails."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", owner_id=42, capacity=10, accepts=("fighter",),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)
    sg = SatelliteConstellation(group_id=300001, owner_id=42, location=hex_c)
    for i in range(3):
        sg.ships.append(_deployed_satellite(f"sat_{i}"))

    empire = SimpleNamespace(id=42, name="E42", fleets=[fleet], deployed_groups=[sg])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    result = RecoverSatellitesOrderHandler().execute_action_order(
        fleet, empire, galaxy,
    )
    assert not result.success
    assert len(carrier.bay_inventory.bay) == 0
    assert len(sg.ships) == 3
    assert sg in empire.deployed_groups


def test_satellite_only_bay_cannot_recover_fighters():
    """Carrier accepts satellites only → fighter recovery fails."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", owner_id=42, capacity=10, accepts=("satellite",),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)
    fg = FighterWing(group_id=200001, owner_id=42, location=hex_c)
    for i in range(3):
        fg.ships.append(_deployed_fighter(f"fighter_{i}"))

    empire = SimpleNamespace(id=42, name="E42", fleets=[fleet], deployed_groups=[fg])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": None,
    }))
    result = RecoverFightersOrderHandler().execute_action_order(
        fleet, empire, galaxy,
    )
    assert not result.success
    assert len(carrier.bay_inventory.bay) == 0
    assert len(fg.ships) == 3
    assert fg in empire.deployed_groups


def test_mixed_bay_carrier_isolates_per_type_capacity(fresh_registries):
    """PROJ-FMS-D audit Fix 2: real mixed-bay carrier isolates capacity.

    A carrier whose design has one fighter-only bay (capacity 250) plus
    one satellite-only bay (capacity 300) must not allow either vehicle
    type to consume the OTHER bay's capacity even though the ship-wide
    aggregate has room.

    Pre-fix bug: the cargo manager unioned every bay's ``allowed_types``
    and used the aggregate ``bay_capacity_mass`` for capacity gating,
    so 550 mass of fighters could be loaded onto a carrier whose
    fighter-only bay was only 250.
    """
    from game.core.constants import LayerType
    from game.simulation.components.component_loader import create_component
    from game.simulation.entities.ship import Ship
    from game.simulation.entities.ship_serialization import ShipSerializer

    # Build a real ShipInstance carrier with one fighter-only bay +
    # one satellite-only bay (no universal bays).
    ship = Ship(
        "MixedBay Carrier", 0, 0, (255, 255, 255),
        ship_class="Cruiser", registries=fresh_registries,
    )
    for comp_id, layer in (
        ("bridge", LayerType.CORE),
        ("crew_quarters", LayerType.INNER),
        ("life_support", LayerType.INNER),
        ("generator", LayerType.INNER),
        ("fighter_bay", LayerType.INNER),  # 250, fighter-only
        ("satellite_bay", LayerType.INNER),  # 300, satellite-only
    ):
        comp = create_component(comp_id, registries=fresh_registries)
        assert comp is not None, comp_id
        assert ship.add_component(comp, layer), comp_id
    design_data = ShipSerializer.to_dict(ship)

    carrier = ShipInstance(
        instance_id="mixed_carrier", design_id="mixed_carrier_design",
        name="MixedBay Carrier", owner_id=42,
        design_data=design_data,
    )
    carrier.set_registries(fresh_registries)

    # Fighter fits in the fighter-only bay.
    fighter = CarriedVehicle(
        design_id="f1", design_data={"name": "f1"},
        vehicle_type="fighter", mass=200.0, current_hp=50,
    )
    assert carrier._cargo_mgr.load_vehicle(fighter)

    # Satellite fits in the satellite-only bay.
    sat = CarriedVehicle(
        design_id="s1", design_data={"name": "s1"},
        vehicle_type="satellite", mass=300.0, current_hp=50,
    )
    assert carrier._cargo_mgr.load_vehicle(sat)

    # Now the satellite bay is full (300/300). A 100-mass satellite
    # must NOT consume the 50 free in the fighter-only bay (even though
    # the ship still has 50 mass of aggregate capacity left).
    extra_sat = CarriedVehicle(
        design_id="s2", design_data={"name": "s2"},
        vehicle_type="satellite", mass=50.0, current_hp=50,
    )
    assert carrier._cargo_mgr.load_vehicle(extra_sat) is False, (
        "Audit Fix 2: satellite must NOT spill into fighter-only bay "
        "even when aggregate ship capacity has room."
    )

    # Symmetric: another 100-mass fighter must not consume the satellite
    # bay's space.
    extra_fighter = CarriedVehicle(
        design_id="f2", design_data={"name": "f2"},
        vehicle_type="fighter", mass=100.0, current_hp=50,
    )
    assert carrier._cargo_mgr.load_vehicle(extra_fighter) is False, (
        "Audit Fix 2: fighter must NOT spill into satellite-only bay "
        "even when aggregate ship capacity has room."
    )


def test_universal_bay_handles_both_types():
    """A bay accepting both fighters and satellites recovers either."""
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", owner_id=42, capacity=10,
        accepts=("fighter", "satellite"),
    )
    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)

    fg = FighterWing(group_id=200001, owner_id=42, location=hex_c)
    fg.ships.append(_deployed_fighter("fighter_0"))

    sg = SatelliteConstellation(group_id=300001, owner_id=42, location=hex_c)
    sg.ships.append(_deployed_satellite("sat_0"))

    empire = SimpleNamespace(id=42, name="E42", fleets=[fleet], deployed_groups=[fg, sg])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    # Recover fighter.
    fleet.add_order(Order(OrderType.RECOVER_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_group_id": fg.id,
        "count": None,
    }))
    r1 = RecoverFightersOrderHandler().execute_action_order(
        fleet, empire, galaxy,
    )
    assert r1.success

    # Recover satellite.
    fleet.add_order(Order(OrderType.RECOVER_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_group_id": sg.id,
        "count": None,
    }))
    r2 = RecoverSatellitesOrderHandler().execute_action_order(
        fleet, empire, galaxy,
    )
    assert r2.success

    assert len(carrier.bay_inventory.bay) == 2
    types_loaded = {item.vehicle_type for item in carrier.bay_inventory.bay}
    assert types_loaded == {"fighter", "satellite"}


def test_launch_handlers_filter_by_vehicle_type():
    """The launch handlers pop only matching vehicle_type CVs.

    A carrier with mixed fighter + satellite cargo: a LAUNCH_SATELLITES
    order pops only satellites; a LAUNCH_FIGHTERS order pops only
    fighters.
    """
    hex_c = HexCoord(0, 0)
    carrier = _make_carrier(
        "carrier_1", owner_id=42, capacity=10,
        accepts=("fighter", "satellite"),
    )
    # 2 fighters + 2 satellites.
    for _ in range(2):
        carrier.bay_inventory.bay.append(CarriedVehicle.from_dict(_fighter_dict()))
    for _ in range(2):
        carrier.bay_inventory.bay.append(CarriedVehicle.from_dict(_satellite_dict()))

    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)
    empire = SimpleNamespace(id=42, name="E42", fleets=[fleet], deployed_groups=[])
    empire.deployed_groups_of = lambda cls, _e=empire: [g for g in _e.deployed_groups if isinstance(g, cls)]
    galaxy = SimpleNamespace(current_turn=1)

    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "auto",
        "count": 2,
        "target_hex": hex_c,
    }))
    LaunchSatellitesOrderHandler().execute_action_order(
        fleet, empire, galaxy,
    )

    # 2 fighters remain in the bay; 2 satellites are in a satellite_group.
    assert len(carrier.bay_inventory.bay) == 2
    assert all(item.vehicle_type == "fighter" for item in carrier.bay_inventory.bay)
    sg = empire.deployed_groups_of(SatelliteConstellation)[0]
    assert len(sg.ships) == 2

    # Now launch the fighters — they go into a fighter_group.
    fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "auto",
        "count": 2,
        "target_hex": hex_c,
    }))
    LaunchFightersOrderHandler().execute_action_order(
        fleet, empire, galaxy,
    )
    assert len(carrier.bay_inventory.bay) == 0
    fg = empire.deployed_groups_of(FighterWing)[0]
    assert len(fg.ships) == 2
