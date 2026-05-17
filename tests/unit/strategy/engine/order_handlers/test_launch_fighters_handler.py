"""PROJ-FMS-C Phase 1 — LaunchFightersOrderHandler tests.

Covers:
- Insufficient fighters -> OrderExecutionResult(success=False).
- Successful launch -> fighters popped from carrier, fighter_group created at hex.
- HP from CarriedVehicle.current_hp carries through to deployed wing.
- Multiple lays at the same hex do NOT auto-merge.
- Mixed-design groups supported.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.launch_fighters import (
    LaunchFightersOrderHandler,
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


def _make_fighter_dict(design_id: str, hp: int = 80, mass: float = 20.0):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "vehicle_class": "Fighter (Small)",
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
        "vehicle_type": "fighter",
        "mass": mass,
        "current_hp": hp,
    }


@pytest.fixture
def setup_carrier_with_fighters():
    """Empire/fleet/carrier with 6 fighters of one design + 1 of another."""
    hex_c = HexCoord(0, 0)
    carrier = _StubShipInstance("carrier_1", owner_id=42)
    for i in range(6):
        carrier.carried_items.append(_make_fighter_dict("fighter_alpha", hp=80 - i))
    carrier.carried_items.append(_make_fighter_dict("fighter_bravo", hp=60))

    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    empire = SimpleNamespace(id=42, name="E42", fleets=[fleet])
    galaxy = SimpleNamespace(current_turn=1)
    return empire, fleet, carrier, galaxy


def test_supported_order_types_only_launch_fighters():
    handler = LaunchFightersOrderHandler()
    assert handler.supported_order_types == (OrderType.LAUNCH_FIGHTERS,)


def test_launch_creates_fighter_group(setup_carrier_with_fighters):
    empire, fleet, carrier, galaxy = setup_carrier_with_fighters
    fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "fighter_alpha",
        "count": 4,
        "target_hex": fleet.location,
    }))

    handler = LaunchFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    # 6 alpha + 1 bravo total. 4 alpha launched -> 2 alpha + 1 bravo remain.
    assert len(carrier.carried_items) == 3

    fighter_groups = [
        f for f in empire.fleets
        if getattr(f, "group_kind", "fleet") == "fighter_group"
    ]
    assert len(fighter_groups) == 1
    fg = fighter_groups[0]
    assert fg.location == fleet.location
    assert fg.owner_id == empire.id
    # 4 fighter ShipInstances deployed into the group.
    assert len(fg.ships) == 4
    for ship in fg.ships:
        assert ship.design_id == "fighter_alpha"
        # HP preserved from CarriedVehicle.current_hp.
        assert ship.current_hp > 0


def test_hp_carries_through_launch(setup_carrier_with_fighters):
    empire, fleet, carrier, galaxy = setup_carrier_with_fighters
    # The first 4 fighters have hp values [80, 79, 78, 77].
    fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "fighter_alpha",
        "count": 4,
        "target_hex": fleet.location,
    }))
    handler = LaunchFightersOrderHandler()
    handler.execute_action_order(fleet, empire, galaxy)

    fg = [f for f in empire.fleets if f.group_kind == "fighter_group"][0]
    hps = sorted(ship.current_hp for ship in fg.ships)
    assert hps == [77, 78, 79, 80]


def test_insufficient_fighters_fails_cleanly(setup_carrier_with_fighters):
    empire, fleet, carrier, galaxy = setup_carrier_with_fighters
    fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "fighter_alpha",
        "count": 10,  # only 6 alpha available
        "target_hex": fleet.location,
    }))

    handler = LaunchFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success
    assert "insufficient" in result.message.lower()
    # No partial consumption.
    assert len(carrier.carried_items) == 7
    fighter_groups = [
        f for f in empire.fleets if f.group_kind == "fighter_group"
    ]
    assert fighter_groups == []


def test_same_hex_launches_do_not_auto_merge(setup_carrier_with_fighters):
    """Multiple launch actions at the same hex produce separate fighter_groups.

    Mirrors PROJ-FMS-B mine_group "no auto-merge" rule. Players can recover
    individual groups via the strategic recovery action.
    """
    empire, fleet, carrier, galaxy = setup_carrier_with_fighters
    handler = LaunchFightersOrderHandler()

    for _ in range(2):
        fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
            "ship_instance_id": carrier.instance_id,
            "fighter_design_id": "fighter_alpha",
            "count": 2,
            "target_hex": fleet.location,
        }))
        handler.execute_action_order(fleet, empire, galaxy)

    fighter_groups = [
        f for f in empire.fleets if f.group_kind == "fighter_group"
    ]
    assert len(fighter_groups) == 2
    counts = sorted(len(fg.ships) for fg in fighter_groups)
    assert counts == [2, 2]


def test_mixed_design_launch_with_design_filter(setup_carrier_with_fighters):
    """Specifying fighter_design_id picks only matching CarriedVehicles."""
    empire, fleet, carrier, galaxy = setup_carrier_with_fighters
    fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "fighter_bravo",  # only one available
        "count": 1,
        "target_hex": fleet.location,
    }))
    handler = LaunchFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success

    fg = [f for f in empire.fleets if f.group_kind == "fighter_group"][0]
    assert len(fg.ships) == 1
    assert fg.ships[0].design_id == "fighter_bravo"


def test_invalid_payload_fails_cleanly(setup_carrier_with_fighters):
    empire, fleet, carrier, galaxy = setup_carrier_with_fighters
    fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target=None))

    handler = LaunchFightersOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success


def test_launched_fighters_tagged_with_launched_in_battle_id_none(
    setup_carrier_with_fighters,
):
    """Strategic-launch fighters do NOT carry a launched_in_battle_id tag.

    The tag is set only by tactical launches (Phase 1 tactical path). It
    drives the end-of-battle reboard policy (Phase 3): pre-existing
    strategic-launch fighters stay in their fighter_group unless
    explicitly recovered.
    """
    empire, fleet, carrier, galaxy = setup_carrier_with_fighters
    fleet.add_order(Order(OrderType.LAUNCH_FIGHTERS, target={
        "ship_instance_id": carrier.instance_id,
        "fighter_design_id": "fighter_alpha",
        "count": 2,
        "target_hex": fleet.location,
    }))
    handler = LaunchFightersOrderHandler()
    handler.execute_action_order(fleet, empire, galaxy)
    fg = [f for f in empire.fleets if f.group_kind == "fighter_group"][0]
    for ship in fg.ships:
        # None or absence both are acceptable: this is a strategic launch.
        assert getattr(ship, "launched_in_battle_id", None) is None
