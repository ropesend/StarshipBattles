"""PROJ-FMS-B Phase 4 — MineGroupService tests."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.services.mine_group_service import MineGroupService


def _mine_cv(design_id: str) -> CarriedVehicle:
    return CarriedVehicle(
        design_id=design_id,
        design_data={"name": design_id, "layers": {}},
        vehicle_type="mine",
        mass=5.0,
        current_hp=30,
    )


class _StubCarrier:
    """Minimal carrier stub exposing the typed BayInventory surface."""

    def __init__(self, mines: list[CarriedVehicle]) -> None:
        self.instance_id = "carrier"
        self._bay_inventory = BayInventory(bay=list(mines))

    @property
    def bay_inventory(self) -> BayInventory:
        return BayInventory(
            bay=list(self._bay_inventory.bay),
            pods=list(self._bay_inventory.pods),
        )

    def set_bay_inventory(self, bay_inventory: BayInventory) -> None:
        self._bay_inventory = BayInventory(
            bay=list(bay_inventory.bay),
            pods=list(bay_inventory.pods),
        )


def _make_mine_group(empire_id: int = 1, designs=None) -> Fleet:
    hex_c = HexCoord(0, 0)
    fleet = Fleet(
        fleet_id=42, owner_id=empire_id, location=hex_c, speed=0.0,
        group_kind="mine_group",
    )
    carrier = _StubCarrier([_mine_cv(d) for d in (designs or [])])
    fleet.ships.append(carrier)
    return fleet


def test_set_sensitivity_accepts_valid_labels():
    svc = MineGroupService()
    mg = _make_mine_group()
    for label in ("LOW", "med", "High"):
        result = svc.set_sensitivity(mg, label)
        assert result.is_valid
    assert mg.sensitivity == "HIGH"


def test_set_sensitivity_rejects_invalid_label():
    svc = MineGroupService()
    mg = _make_mine_group()
    result = svc.set_sensitivity(mg, "EXTREME")
    assert not result.is_valid
    assert mg.sensitivity == "MED"  # default unchanged


def test_set_sensitivity_rejects_non_mine_group():
    svc = MineGroupService()
    f = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0), group_kind="fleet")
    result = svc.set_sensitivity(f, "HIGH")
    assert not result.is_valid


def test_set_threshold_in_range():
    svc = MineGroupService()
    mg = _make_mine_group()
    result = svc.set_threshold(mg, 0.75)
    assert result.is_valid
    assert mg.expected_hit_chance_threshold == pytest.approx(0.75)


def test_set_threshold_out_of_range():
    svc = MineGroupService()
    mg = _make_mine_group()
    for v in (-0.1, 1.1):
        result = svc.set_threshold(mg, v)
        assert not result.is_valid


def test_get_mine_counts_by_design():
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "a", "b"])
    counts = svc.get_mine_counts_by_design(mg)
    assert counts == {"a": 2, "b": 1}


def test_self_destruct_partial():
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "a", "a", "b"])
    empire = SimpleNamespace(fleets=[mg])
    result = svc.self_destruct(mg, empire, selections={"a": 2})
    assert result.is_valid
    counts = svc.get_mine_counts_by_design(mg)
    assert counts == {"a": 1, "b": 1}
    # Group still present.
    assert mg in empire.fleets


def test_self_destruct_all_removes_group():
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "b"])
    empire = SimpleNamespace(fleets=[mg])
    svc.self_destruct(mg, empire, selections={"a": 1, "b": 1})
    assert mg.ships[0].bay_inventory.bay == []
    # Group pruned from empire.fleets.
    assert mg not in empire.fleets


def test_self_destruct_clamps_overcount():
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "a", "b"])
    empire = SimpleNamespace(fleets=[mg])
    svc.self_destruct(mg, empire, selections={"a": 99})  # only 2 available
    counts = svc.get_mine_counts_by_design(mg)
    assert counts == {"b": 1}


def test_self_destruct_resyncs_positions():
    """mine_positions list shrinks to match remaining inventory length."""
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "a", "a"])
    mg.mine_positions = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    empire = SimpleNamespace(fleets=[mg])
    svc.self_destruct(mg, empire, selections={"a": 2})
    assert len(mg.mine_positions) == 1
