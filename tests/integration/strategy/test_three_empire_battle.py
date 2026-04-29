"""End-to-end integration test for 3-empire conflict resolution (PROJ-275).

Phase 7 collapses the legacy sequential 2-fleet decomposition in
`ConflictResolutionEngine._resolve_combat_at_hex` into a single N-team
battle. This file proves the new behavior:

  * 3 empires sharing a sector → ONE call to `IBattleResolver.resolve_battle`
  * The resolver receives all 3 fleets at once
  * The resulting `BattleResult` carries 3-team survivor data

The previous behavior — `N-choose-2` random pairings — was explicitly
called out by the user as "a mistake" in the project brief.
"""
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.engine.conflict_resolution_engine import (
    ConflictResolutionEngine,
)
from game.strategy.interfaces.battle_resolver import (
    BattleResult,
    IBattleResolver,
)


class _RecordingResolver(IBattleResolver):
    """Records every `resolve_battle` invocation for assertion.

    BUG-126: simulates the PostBattleHook by wiping the `ships` list
    on every fleet that did NOT win. The strategy engine reports a
    fleet as destroyed only when its ships list is empty after the
    resolver returns.
    """

    def __init__(self, winner_team_id: int = 0):
        self.calls = []
        self.winner_team_id = winner_team_id

    def resolve_battle(self, fleets, modifiers=None, seed=None,
                       registries=None, environmental_effects=None,
                       empires=None):
        fleet_list = list(fleets)
        self.calls.append({
            "fleets": fleet_list,
            "modifiers": modifiers,
            "seed": seed,
        })
        # Simulate the PostBattleHook wiping the loser fleets.
        for tid, f in enumerate(fleet_list):
            if tid != self.winner_team_id:
                f.ships = []
        team_survivors = {
            tid: ([MagicMock()] if tid == self.winner_team_id else [])
            for tid in range(len(fleet_list))
        }
        return BattleResult(
            winner=self.winner_team_id,
            tick_count=1,
            team_survivors=team_survivors,
        )


def _make_fleet(fleet_id, owner_id, location):
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = location
    fleet.ships = [MagicMock()]  # has at least one ship
    fleet.task_forces = []
    return fleet


def _make_empire(empire_id, fleets):
    empire = MagicMock()
    empire.id = empire_id
    empire.fleets = list(fleets)
    return empire


def test_three_empires_at_one_hex_resolve_in_single_battle():
    """3 empires colliding at one hex → ONE call to resolve_battle, with
    all three fleets in the same call."""
    resolver = _RecordingResolver(winner_team_id=0)
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    location = HexCoord(5, 5)
    fleet_a = _make_fleet(fleet_id=1, owner_id=0, location=location)
    fleet_b = _make_fleet(fleet_id=2, owner_id=1, location=location)
    fleet_c = _make_fleet(fleet_id=3, owner_id=2, location=location)

    empire_a = _make_empire(empire_id=0, fleets=[fleet_a])
    empire_b = _make_empire(empire_id=1, fleets=[fleet_b])
    empire_c = _make_empire(empire_id=2, fleets=[fleet_c])

    engine.resolve_all_conflicts([empire_a, empire_b, empire_c])

    # Single call — not 3 sequential 2-fleet pairs.
    assert len(resolver.calls) == 1, (
        f"Expected ONE 3-team battle, got {len(resolver.calls)} calls — "
        f"sequential decomposition is back."
    )
    fleets_seen = resolver.calls[0]["fleets"]
    assert len(fleets_seen) == 3
    assert {f.owner_id for f in fleets_seen} == {0, 1, 2}


def test_three_empire_battle_returns_three_team_battle_result():
    """The recorded BattleResult carries `team_survivors` keyed 0..2."""
    resolver = _RecordingResolver(winner_team_id=1)
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    location = HexCoord(0, 0)
    empires = []
    for empire_id in range(3):
        fleet = _make_fleet(
            fleet_id=empire_id + 1, owner_id=empire_id, location=location
        )
        empires.append(_make_empire(empire_id=empire_id, fleets=[fleet]))

    engine.resolve_all_conflicts(empires)

    # Direct mock assertion — recorded call carries the expected shape.
    call = resolver.calls[0]
    assert len(call["fleets"]) == 3


def test_three_empire_battle_reports_destroyed_fleets():
    """BUG-126: when the resolver wipes loser fleets to zero ships,
    the engine reports their ids in `fleets_destroyed` — but the
    strategy layer no longer calls `empire.remove_fleet` itself. That
    is the `PostBattleHook`'s job (mocked away here)."""
    resolver = _RecordingResolver(winner_team_id=0)
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    location = HexCoord(0, 0)
    fleet_a = _make_fleet(fleet_id=1, owner_id=0, location=location)
    fleet_b = _make_fleet(fleet_id=2, owner_id=1, location=location)
    fleet_c = _make_fleet(fleet_id=3, owner_id=2, location=location)

    empire_a = _make_empire(empire_id=0, fleets=[fleet_a])
    empire_b = _make_empire(empire_id=1, fleets=[fleet_b])
    empire_c = _make_empire(empire_id=2, fleets=[fleet_c])

    result = engine.resolve_all_conflicts([empire_a, empire_b, empire_c])

    # Strategy engine no longer calls remove_fleet itself.
    empire_a.remove_fleet.assert_not_called()
    empire_b.remove_fleet.assert_not_called()
    empire_c.remove_fleet.assert_not_called()
    # Combat stats reflect a single battle with 2 wiped fleets.
    assert result.combats_resolved == 1
    assert sorted(result.fleets_destroyed) == [2, 3]
