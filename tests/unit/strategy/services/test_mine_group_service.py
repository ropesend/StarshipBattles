"""PROJ-FMS-B Phase 4 + PROJ-431 Phase 2 — MineGroupService tests."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.deployed_group import MineGroup
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


def _make_mine_group(empire_id: int = 1, designs=None) -> MineGroup:
    hex_c = HexCoord(0, 0)
    mg = MineGroup(group_id=42, owner_id=empire_id, location=hex_c)
    mg.mines = [_mine_cv(d) for d in (designs or [])]
    return mg


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
    # A real Fleet is structurally not a MineGroup — the typed check rejects it.
    f = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
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
    empire = SimpleNamespace(fleets=[], deployed_groups=[mg])
    result = svc.self_destruct(mg, empire, selections={"a": 2})
    assert result.is_valid
    counts = svc.get_mine_counts_by_design(mg)
    assert counts == {"a": 1, "b": 1}
    # Group still present.
    assert mg in empire.deployed_groups


def test_self_destruct_all_removes_group():
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "b"])
    empire = SimpleNamespace(fleets=[], deployed_groups=[mg])
    svc.self_destruct(mg, empire, selections={"a": 1, "b": 1})
    assert mg.mines == []
    # Group pruned from empire.deployed_groups.
    assert mg not in empire.deployed_groups


def test_self_destruct_clamps_overcount():
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "a", "b"])
    empire = SimpleNamespace(fleets=[], deployed_groups=[mg])
    svc.self_destruct(mg, empire, selections={"a": 99})  # only 2 available
    counts = svc.get_mine_counts_by_design(mg)
    assert counts == {"b": 1}


def test_self_destruct_resyncs_positions():
    """mine_positions list shrinks to match remaining inventory length."""
    svc = MineGroupService()
    mg = _make_mine_group(designs=["a", "a", "a"])
    mg.mine_positions = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    empire = SimpleNamespace(fleets=[], deployed_groups=[mg])
    svc.self_destruct(mg, empire, selections={"a": 2})
    assert len(mg.mine_positions) == 1
