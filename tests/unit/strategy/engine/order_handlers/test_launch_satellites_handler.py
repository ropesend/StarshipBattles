"""PROJ-FMS-D Phase 1 — LaunchSatellitesOrderHandler tests.

Mirrors the PROJ-FMS-C ``test_launch_fighters_handler.py`` shape:
- Insufficient satellites -> OrderExecutionResult(success=False).
- Successful launch -> satellites popped, satellite_group created.
- HP from CarriedVehicle.current_hp carries through to deployed group.
- Same-hex launches do NOT auto-merge.
- Mixed-design groups supported via filter.
- A fighter-only carrier carrying no satellites cannot launch — gates
  via vehicle_type filter inside the handler.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.launch_satellites import (
    LaunchSatellitesOrderHandler,
)


class _StubShipInstance:
    """Minimal stand-in for a ShipInstance carrier.

    Mirrors :class:`ShipInstance`'s PROJ-431 typed bay surface: the
    ``bay_inventory`` property is a fresh projection over
    ``self.carried_items``; ``set_bay_inventory`` writes back through
    ``carried_items`` so legacy assertions on the dict list still work.
    """

    def __init__(self, instance_id: str, owner_id: int = 0):
        self.instance_id = instance_id
        self.design_id = "stub_design"
        self.owner_id = owner_id
        self.name = instance_id
        self.design_data = {}
        self.current_hp = 100
        self.is_alive = True
        self.is_derelict = False
        self.carried_items: list[dict] = []

    @property
    def bay_inventory(self) -> BayInventory:
        # PROJ-431 Phase 1f: from_any deleted; explicit shape probe.
        from game.strategy.data.carried_vehicle import VALID_VEHICLE_TYPES
        bay: list[CarriedVehicle] = []
        pods: list[DropPod] = []
        for item in self.carried_items:
            if isinstance(item, CarriedVehicle):
                bay.append(item)
            elif isinstance(item, dict) and str(
                item.get("vehicle_type", "")
            ).lower() in VALID_VEHICLE_TYPES:
                bay.append(CarriedVehicle.from_dict(item))
            elif isinstance(item, dict):
                pods.append(DropPod.from_dict(item))
        return BayInventory(bay=bay, pods=pods)

    def set_bay_inventory(self, bay_inventory: BayInventory) -> None:
        new_items: list = []
        for cv in bay_inventory.bay:
            new_items.append(cv.to_dict())
        for pod in bay_inventory.pods:
            entry = {
                "design_id": pod.design_id,
                "design_data": pod.design_data,
                "mass": pod.mass,
            }
            entry.update(pod.payload)
            new_items.append(entry)
        self.carried_items = new_items


def _make_satellite_dict(design_id: str, hp: int = 80, mass: float = 30.0):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "vehicle_class": "Satellite",
            "layers": {
                "CORE": {
                    "components": [
                        {
                            "id": "stub_hull",
                            "abilities": {"StructuralIntegrity": True},
                        },
                    ],
                },
            },
        },
        "vehicle_type": "satellite",
        "mass": mass,
        "current_hp": hp,
    }


def _make_fighter_dict(design_id: str, hp: int = 80, mass: float = 20.0):
    return {
        "design_id": design_id,
        "design_data": {"name": design_id, "vehicle_class": "Fighter (Small)"},
        "vehicle_type": "fighter",
        "mass": mass,
        "current_hp": hp,
    }


@pytest.fixture
def setup_carrier_with_satellites():
    """Empire/fleet/carrier with 5 satellites of one design + 1 of another + 2 fighters."""
    hex_c = HexCoord(0, 0)
    carrier = _StubShipInstance("carrier_1", owner_id=42)
    for i in range(5):
        carrier.carried_items.append(_make_satellite_dict("sat_alpha", hp=80 - i))
    carrier.carried_items.append(_make_satellite_dict("sat_bravo", hp=60))
    # Fighter entries that must NOT be touched by the satellite handler.
    carrier.carried_items.append(_make_fighter_dict("fighter_alpha"))
    carrier.carried_items.append(_make_fighter_dict("fighter_alpha"))

    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0
    )
    fleet.ships.append(carrier)
    empire = SimpleNamespace(
        id=42, name="E42", fleets=[fleet], deployed_groups=[],
    )
    empire.deployed_groups_of = lambda cls, _emp=empire: [
        g for g in _emp.deployed_groups if isinstance(g, cls)
    ]
    galaxy = SimpleNamespace(current_turn=1)
    return empire, fleet, carrier, galaxy


def test_supported_order_types_only_launch_satellites():
    handler = LaunchSatellitesOrderHandler()
    assert handler.supported_order_types == (OrderType.LAUNCH_SATELLITES,)


def test_launch_creates_satellite_group(setup_carrier_with_satellites):
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 3,
        "target_hex": fleet.location,
    }))
    handler = LaunchSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    # Started with 5 alpha + 1 bravo + 2 fighters = 8. 3 alpha launched -> 5 remain.
    assert len(carrier.carried_items) == 5
    from game.strategy.data.deployed_group import SatelliteConstellation
    sat_groups = empire.deployed_groups_of(SatelliteConstellation)
    assert len(sat_groups) == 1
    sg = sat_groups[0]
    assert sg.location == fleet.location
    assert sg.owner_id == empire.id
    assert len(sg.ships) == 3
    for ship in sg.ships:
        assert ship.design_id == "sat_alpha"


def test_hp_carries_through_launch(setup_carrier_with_satellites):
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    # First 3 sat_alpha have hp = [80, 79, 78].
    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 3,
        "target_hex": fleet.location,
    }))
    handler = LaunchSatellitesOrderHandler()
    handler.execute_action_order(fleet, empire, galaxy)
    from game.strategy.data.deployed_group import SatelliteConstellation
    sg = empire.deployed_groups_of(SatelliteConstellation)[0]
    hps = sorted(ship.current_hp for ship in sg.ships)
    assert hps == [78, 79, 80]


def test_insufficient_satellites_fails_cleanly(setup_carrier_with_satellites):
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 10,  # only 5 alpha available
        "target_hex": fleet.location,
    }))
    handler = LaunchSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success
    assert "insufficient" in result.message.lower()
    # No partial consumption.
    assert len(carrier.carried_items) == 8
    from game.strategy.data.deployed_group import SatelliteConstellation
    sat_groups = empire.deployed_groups_of(SatelliteConstellation)
    assert sat_groups == []


def test_same_hex_launches_do_not_auto_merge(setup_carrier_with_satellites):
    """Two consecutive launches at the same hex produce TWO satellite_groups."""
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    handler = LaunchSatellitesOrderHandler()
    for _ in range(2):
        fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
            "ship_instance_id": carrier.instance_id,
            "satellite_design_id": "sat_alpha",
            "count": 2,
            "target_hex": fleet.location,
        }))
        handler.execute_action_order(fleet, empire, galaxy)

    from game.strategy.data.deployed_group import SatelliteConstellation
    sat_groups = empire.deployed_groups_of(SatelliteConstellation)
    assert len(sat_groups) == 2
    assert sorted(len(g.ships) for g in sat_groups) == [2, 2]


def test_handler_ignores_fighter_carried_items(setup_carrier_with_satellites):
    """auto launch picks only satellite-type CVs, never fighter CVs."""
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    # 6 satellites total; ask for all via "auto".
    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "auto",
        "count": 6,
        "target_hex": fleet.location,
    }))
    handler = LaunchSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    # 6 satellites popped; 2 fighter entries remain in carrier.
    assert len(carrier.carried_items) == 2
    for item in carrier.carried_items:
        assert item["vehicle_type"] == "fighter"


def test_satellite_group_uses_300000_id_namespace(setup_carrier_with_satellites):
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 2,
        "target_hex": fleet.location,
    }))
    LaunchSatellitesOrderHandler().execute_action_order(fleet, empire, galaxy)
    from game.strategy.data.deployed_group import SatelliteConstellation
    sg = empire.deployed_groups_of(SatelliteConstellation)[0]
    assert sg.id >= 300000


def test_invalid_payload_fails_cleanly(setup_carrier_with_satellites):
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target=None))
    handler = LaunchSatellitesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success


def test_launched_satellites_have_no_launched_in_battle_id_tag(
    setup_carrier_with_satellites,
):
    """Strategic-launch satellites do NOT carry a launched_in_battle_id tag.

    Mirrors the equivalent invariant for fighters. The tag is set only
    by tactical launches and drives reboard policy.
    """
    empire, fleet, carrier, galaxy = setup_carrier_with_satellites
    fleet.add_order(Order(OrderType.LAUNCH_SATELLITES, target={
        "ship_instance_id": carrier.instance_id,
        "satellite_design_id": "sat_alpha",
        "count": 2,
        "target_hex": fleet.location,
    }))
    LaunchSatellitesOrderHandler().execute_action_order(fleet, empire, galaxy)
    from game.strategy.data.deployed_group import SatelliteConstellation
    sg = empire.deployed_groups_of(SatelliteConstellation)[0]
    for ship in sg.ships:
        assert getattr(ship, "launched_in_battle_id", None) is None
