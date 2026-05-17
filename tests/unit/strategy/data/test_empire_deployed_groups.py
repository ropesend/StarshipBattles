"""PROJ-431 Phase 2 — Empire.deployed_groups tests (RED).

``Empire`` grows a separate collection ``deployed_groups: list[DeployedGroup]``
that is NOT mixed into ``empire.fleets``. The split is the foundation
for deleting ``_split_mine_groups_from_fleets`` and dropping the
``mine_group`` discriminator from ``Fleet.group_kind``.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.deployed_group import MineGroup
from game.strategy.data.empire import Empire


def _make_empire() -> Empire:
    return Empire(empire_id=1, name="E1", color=(255, 0, 0))


def test_deployed_groups_starts_empty():
    e = _make_empire()
    assert e.deployed_groups == []


def test_add_deployed_group_sets_owner_id():
    e = _make_empire()
    mg = MineGroup(group_id=100001, owner_id=999, location=HexCoord(0, 0))
    e.add_deployed_group(mg)
    assert mg in e.deployed_groups
    # Empire takes ownership.
    assert mg.owner_id == 1


def test_add_deployed_group_dedupes():
    e = _make_empire()
    mg = MineGroup(group_id=1, owner_id=1, location=HexCoord(0, 0))
    e.add_deployed_group(mg)
    e.add_deployed_group(mg)
    assert e.deployed_groups.count(mg) == 1


def test_remove_deployed_group():
    e = _make_empire()
    mg = MineGroup(group_id=2, owner_id=1, location=HexCoord(0, 0))
    e.add_deployed_group(mg)
    assert e.remove_deployed_group(mg) is True
    assert mg not in e.deployed_groups


def test_remove_deployed_group_missing_returns_false():
    e = _make_empire()
    mg = MineGroup(group_id=3, owner_id=1, location=HexCoord(0, 0))
    assert e.remove_deployed_group(mg) is False


def test_deployed_groups_of_filters_by_type():
    e = _make_empire()
    mg1 = MineGroup(group_id=1, owner_id=1, location=HexCoord(0, 0))
    mg2 = MineGroup(group_id=2, owner_id=1, location=HexCoord(1, 0))
    e.add_deployed_group(mg1)
    e.add_deployed_group(mg2)
    mines = e.deployed_groups_of(MineGroup)
    assert mines == [mg1, mg2]


def test_deployed_groups_separate_from_fleets():
    """Adding a MineGroup never appears in ``empire.fleets``."""
    e = _make_empire()
    mg = MineGroup(group_id=1, owner_id=1, location=HexCoord(0, 0))
    e.add_deployed_group(mg)
    assert mg not in e.fleets


def test_is_eliminated_considers_deployed_groups():
    """An empire with only deployed groups is not eliminated."""
    e = _make_empire()
    mg = MineGroup(group_id=1, owner_id=1, location=HexCoord(0, 0))
    e.add_deployed_group(mg)
    assert e.is_eliminated() is False


def test_serialise_round_trips_deployed_groups():
    """Empire.to_dict / from_dict preserves ``deployed_groups``."""
    e = _make_empire()
    mg = MineGroup(group_id=100001, owner_id=1, location=HexCoord(2, -1))
    mg.sensitivity = "HIGH"
    e.add_deployed_group(mg)

    data = e.to_dict()
    restored = Empire.from_dict(data, galaxy=None)
    assert len(restored.deployed_groups) == 1
    rmg = restored.deployed_groups[0]
    assert isinstance(rmg, MineGroup)
    assert rmg.id == 100001
    assert rmg.location == HexCoord(2, -1)
    assert rmg.sensitivity == "HIGH"
