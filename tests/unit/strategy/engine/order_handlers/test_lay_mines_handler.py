"""PROJ-FMS-B Phase 1 — LayMinesOrderHandler tests.

Covers:
- Insufficient mines -> OrderExecutionResult(success=False).
- Successful lay -> mines popped from carrier, mine_group created at hex.
- Multiple lay actions extend the same mine_group (one group, count grows).
- Scatter coords populated and deterministic for same seed.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.lay_mines import (
    LayMinesOrderHandler,
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
        bay: list[CarriedVehicle] = []
        pods: list[DropPod] = []
        for item in self.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is not None:
                bay.append(cv)
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


def _make_mine_dict(design_id: str, damage: float = 50.0):
    return {
        "design_id": design_id,
        "design_data": {
            "name": design_id,
            "layers": {
                "CORE": {
                    "components": [
                        {
                            "id": "warhead",
                            "abilities": {"Warhead": {"damage": damage}},
                        },
                    ],
                },
            },
        },
        "vehicle_type": "mine",
        "mass": 5.0,
        "current_hp": 30,
    }


@pytest.fixture
def setup_empire_and_fleet():
    """Return (empire, fleet, carrier) with 5 mines loaded."""
    hex_c = HexCoord(0, 0)
    carrier = _StubShipInstance("carrier_1", owner_id=42)
    for _ in range(5):
        carrier.carried_items.append(_make_mine_dict("mine_warhead_small"))

    fleet = Fleet(
        fleet_id=1, owner_id=42, location=hex_c, speed=5.0,
        group_kind="fleet",
    )
    fleet.ships.append(carrier)

    empire = SimpleNamespace(
        id=42, name="E42", fleets=[fleet],
    )
    galaxy = SimpleNamespace(current_turn=1)
    return empire, fleet, carrier, galaxy


def test_supported_order_types_only_lay_mines():
    handler = LayMinesOrderHandler()
    assert handler.supported_order_types == (OrderType.LAY_MINES,)


def test_lay_mines_creates_mine_group(setup_empire_and_fleet):
    empire, fleet, carrier, galaxy = setup_empire_and_fleet
    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 3,
        "target_hex": fleet.location,
    }))

    handler = LayMinesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success
    assert len(carrier.carried_items) == 2  # 5 - 3

    mine_groups = [
        f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "mine_group"
    ]
    assert len(mine_groups) == 1
    mg = mine_groups[0]
    assert mg.location == fleet.location
    assert mg.owner_id == empire.id
    assert len(mg.ships[0].carried_items) == 3
    # Scatter coords populated.
    assert len(mg.mine_positions) == 3
    assert mg.scatter_seed is not None
    # Defaults from balance file.
    assert mg.sensitivity == "MED"
    assert mg.expected_hit_chance_threshold == pytest.approx(0.30)


def test_insufficient_mines_fails_cleanly(setup_empire_and_fleet):
    empire, fleet, carrier, galaxy = setup_empire_and_fleet
    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 10,  # only 5 available
        "target_hex": fleet.location,
    }))

    handler = LayMinesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success
    assert "insufficient" in result.message.lower()
    # No partial consumption.
    assert len(carrier.carried_items) == 5
    # No mine_group created.
    mine_groups = [
        f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "mine_group"
    ]
    assert mine_groups == []


def test_same_hex_lays_do_not_auto_merge(setup_empire_and_fleet):
    """PROJ-FMS-B audit Fix 4: same-hex lays by the same owner must NOT
    auto-merge into a single mine_group. The shared design says
    "Multiple groups per owner per hex permitted; no auto-merge"; the
    Phase 1 checklist agrees. Pre-fix the order handler returned the
    first matching mine_group at the hex, silently coalescing.
    """
    empire, fleet, carrier, galaxy = setup_empire_and_fleet
    handler = LayMinesOrderHandler()

    # Lay 2 mines in the first action.
    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 2,
        "target_hex": fleet.location,
    }))
    handler.execute_action_order(fleet, empire, galaxy)

    # Then lay 2 more in the same hex.
    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 2,
        "target_hex": fleet.location,
    }))
    handler.execute_action_order(fleet, empire, galaxy)

    mine_groups = [
        f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "mine_group"
    ]
    # Two separate lay actions => two distinct mine_groups (no auto-merge).
    assert len(mine_groups) == 2
    counts = sorted(len(mg.ships[0].carried_items) for mg in mine_groups)
    assert counts == [2, 2]


def test_three_separate_lays_at_same_hex_produce_three_groups(setup_empire_and_fleet):
    """PROJ-FMS-B audit Fix 4 regression: three IssueLayMinesCommand
    invocations at the same hex by the same owner produce three separate
    ``mine_group`` Fleets.
    """
    empire, fleet, carrier, galaxy = setup_empire_and_fleet
    handler = LayMinesOrderHandler()

    for _ in range(3):
        fleet.add_order(Order(OrderType.LAY_MINES, target={
            "ship_instance_id": carrier.instance_id,
            "mine_design_id": "mine_warhead_small",
            "count": 1,
            "target_hex": fleet.location,
        }))
        handler.execute_action_order(fleet, empire, galaxy)

    mine_groups = [
        f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "mine_group"
    ]
    assert len(mine_groups) == 3
    # Each group must have a unique fleet_id.
    assert len({mg.id for mg in mine_groups}) == 3


def test_scatter_seed_is_deterministic(setup_empire_and_fleet):
    empire, fleet, carrier, galaxy = setup_empire_and_fleet
    handler = LayMinesOrderHandler()
    fleet.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 3,
        "target_hex": fleet.location,
    }))
    handler.execute_action_order(fleet, empire, galaxy)
    mg1 = [f for f in empire.fleets if getattr(f, "group_kind", "fleet") == "mine_group"][0]
    positions_run_1 = list(mg1.mine_positions)

    # Build a fresh empire with identical inputs — same seed → same positions.
    hex_c = HexCoord(0, 0)
    carrier2 = _StubShipInstance("carrier_2", owner_id=42)
    for _ in range(5):
        carrier2.carried_items.append(_make_mine_dict("mine_warhead_small"))
    fleet2 = Fleet(fleet_id=2, owner_id=42, location=hex_c, speed=5.0)
    fleet2.ships.append(carrier2)
    empire2 = SimpleNamespace(id=42, name="E42", fleets=[fleet2])
    galaxy2 = SimpleNamespace(current_turn=1)
    fleet2.add_order(Order(OrderType.LAY_MINES, target={
        "ship_instance_id": carrier2.instance_id,
        "mine_design_id": "mine_warhead_small",
        "count": 3,
        "target_hex": hex_c,
    }))
    handler.execute_action_order(fleet2, empire2, galaxy2)
    mg2 = [f for f in empire2.fleets if getattr(f, "group_kind", "fleet") == "mine_group"][0]
    positions_run_2 = list(mg2.mine_positions)

    assert positions_run_1 == positions_run_2, "Scatter must be deterministic per seed"


def test_invalid_payload_fails_cleanly(setup_empire_and_fleet):
    empire, fleet, carrier, galaxy = setup_empire_and_fleet
    fleet.add_order(Order(OrderType.LAY_MINES, target=None))

    handler = LayMinesOrderHandler()
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert not result.success
