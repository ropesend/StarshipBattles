"""PROJ-431 Phase 5 (Finding 1) — deployed groups trigger combat without fleets.

Codex-consult-driven fix: ``ConflictResolutionEngine._resolve_conflicts``
previously only iterated ``empire.fleets`` for combat triggers, snapshotting
fleet pairs as the sole conflict source. ``FighterWing`` and
``SatelliteConstellation`` instances on ``empire.deployed_groups`` were only
added to the occupant list AFTER a fleet trigger existed at that hex.

Result before the fix: two opposing FighterWings (or SatelliteConstellations)
at the same hex with no real fleet present never battle. They just sit there.

This test creates two opposing deployed groups at a contested hex with NO
fleets at all and asserts the battle resolver is invoked. The contested
participants must include both deployed groups.

Mines (``MineGroup``) are NOT combat-capable triggers — they resolve via
``TacticalMineResolver`` inside an existing battle, not as battle initiators.
That is consistent with ``_combat_participating_groups``'s filter that already
excludes ``MineGroup`` from the occupants list.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.deployed_group import (
    FighterWing,
    MineGroup,
    SatelliteConstellation,
)
from game.strategy.engine.conflict_resolution_engine import (
    ConflictResolutionEngine,
)
from game.strategy.interfaces.battle_resolver import BattleResult


def _make_empire(empire_id: int):
    """Empire-like stub with a `.fleets` list and `.deployed_groups` list."""
    emp = MagicMock()
    emp.id = empire_id
    emp.fleets = []
    emp.deployed_groups = []
    return emp


def _make_resolver():
    resolver = MagicMock()
    resolver.resolve_battle.return_value = BattleResult(
        winner=0,
        tick_count=1,
        team_survivors={0: [MagicMock()], 1: []},
        replay_id=None,
    )
    return resolver


def _make_fighter_wing(group_id: int, owner_id: int, location: HexCoord) -> FighterWing:
    wing = FighterWing(group_id=group_id, owner_id=owner_id, location=location)
    # One materialised ship so it isn't pruned as empty.
    ship = MagicMock()
    ship.is_alive = True
    wing.ships.append(ship)
    return wing


def test_two_opposing_fighter_wings_with_no_fleets_trigger_combat():
    """Finding 1 (MAJOR): two opposing FighterWings at the same hex with no
    fleets must engage. Previously the conflict trigger only iterated fleets,
    so this scenario silently produced no combat."""
    hex_c = HexCoord(0, 0)

    emp_a = _make_empire(empire_id=1)
    emp_b = _make_empire(empire_id=2)

    wing_a = _make_fighter_wing(group_id=1001, owner_id=1, location=hex_c)
    wing_b = _make_fighter_wing(group_id=1002, owner_id=2, location=hex_c)
    emp_a.deployed_groups.append(wing_a)
    emp_b.deployed_groups.append(wing_b)

    resolver = _make_resolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)
    engine._empires = [emp_a, emp_b]

    # `tick=1`: any combat fires on this opportunity since deployed groups have
    # no speed-based gating. The exact tick number is incidental — what matters
    # is that the deployed-group trigger fires at all.
    engine.resolve_all_conflicts(
        [emp_a, emp_b],
        galaxy=None,
        tick=1,
        moved_fleet_ids=set(),
    )

    assert resolver.resolve_battle.called, (
        "Battle resolver was not invoked: two opposing FighterWings at "
        "the same hex with no fleets did not trigger combat. The conflict "
        "engine is still fleet-only on the trigger side."
    )


def test_opposing_satellite_constellations_with_no_fleets_trigger_combat():
    """Symmetric case: SatelliteConstellation must also drive triggers."""
    hex_c = HexCoord(2, -1)

    emp_a = _make_empire(empire_id=1)
    emp_b = _make_empire(empire_id=2)

    sat_a = SatelliteConstellation(
        group_id=2001, owner_id=1, location=hex_c,
    )
    sat_a.ships.append(MagicMock(is_alive=True))
    sat_b = SatelliteConstellation(
        group_id=2002, owner_id=2, location=hex_c,
    )
    sat_b.ships.append(MagicMock(is_alive=True))
    emp_a.deployed_groups.append(sat_a)
    emp_b.deployed_groups.append(sat_b)

    resolver = _make_resolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)
    engine._empires = [emp_a, emp_b]

    engine.resolve_all_conflicts(
        [emp_a, emp_b],
        galaxy=None,
        tick=1,
        moved_fleet_ids=set(),
    )

    assert resolver.resolve_battle.called


def test_lone_mine_group_does_not_trigger_combat():
    """``MineGroup`` is not a combat trigger — mines detonate inside an
    existing battle via ``TacticalMineResolver``. Two opposing mine groups
    at a hex (with no fleets, no fighter wings, no satellites) must NOT
    cause battle resolution."""
    hex_c = HexCoord(0, 0)

    emp_a = _make_empire(empire_id=1)
    emp_b = _make_empire(empire_id=2)

    mg_a = MineGroup(group_id=3001, owner_id=1, location=hex_c)
    mg_b = MineGroup(group_id=3002, owner_id=2, location=hex_c)
    emp_a.deployed_groups.append(mg_a)
    emp_b.deployed_groups.append(mg_b)

    resolver = _make_resolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)
    engine._empires = [emp_a, emp_b]

    engine.resolve_all_conflicts(
        [emp_a, emp_b],
        galaxy=None,
        tick=1,
        moved_fleet_ids=set(),
    )

    assert not resolver.resolve_battle.called, (
        "Mine groups must not trigger combat on their own. They resolve "
        "inside an existing battle via TacticalMineResolver."
    )
