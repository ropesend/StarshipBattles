"""Integration tests for strategy-layer combat resolution paths (BUG-126).

This file pins the post-BUG-126 contract:

* `SimulationBattleResolver` has THREE shortcut paths that bypass the
  simulator (no combat-capable ships at all, only one team has any,
  both fleet lists empty before resolver call). The first two are
  exercised here at the resolver level.
* `ConflictResolutionEngine._resolve_combat_at_hex` no longer assigns
  a winner. Surviving ships from BOTH sides remain in their fleets;
  no fleet is removed unless ALL its ships were destroyed (and that
  pruning is the `PostBattleHook`'s job, not the strategy layer's).
* Two co-located fleets re-engage on every subsequent strategy tick
  until one side is destroyed or they separate.
* `COMBAT_RESOLVED` events carry the new schema:
  `participating_fleet_ids` / `surviving_fleet_ids` /
  `destroyed_fleet_ids`. The legacy `winner_fleet_id` /
  `loser_fleet_id` keys are gone.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from unittest.mock import MagicMock

import pytest

from game.core.event_logging import EventBus
from game.core.hex_math import HexCoord
from game.strategy.engine.conflict_resolution_engine import (
    ConflictResolutionEngine,
)
from game.strategy.events import EventCategory, EventType
from game.strategy.interfaces.battle_resolver import (
    BattleResult,
    IBattleResolver,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _capture_log_event_calls():
    calls: List[Any] = []

    def _fake(event_type, **kwargs):
        calls.append((event_type, kwargs))

    return calls, EventBus(_fake)


def _empire(empire_id: int):
    emp = MagicMock()
    emp.id = empire_id
    emp.fleets = []
    emp.remove_fleet = MagicMock()
    return emp


def _fleet(fleet_id: int, owner_id: int, ship_count: int = 1, location=None):
    f = MagicMock()
    f.id = fleet_id
    f.owner_id = owner_id
    f.location = location or HexCoord(0, 0)
    f.ships = [MagicMock() for _ in range(ship_count)]
    return f


class _ScriptedResolver(IBattleResolver):
    """Returns a sequence of pre-built BattleResults — one per call.

    The resolver's job in production is to mutate `fleet.ships` via
    `PostBattleHook`. For unit-level tests we simulate that side
    effect with a `mutator` callback so the strategy engine sees the
    realistic post-battle fleet state.
    """

    def __init__(
        self,
        results: Sequence[BattleResult],
        mutator: Optional[Any] = None,
    ):
        self._results = list(results)
        self._mutator = mutator
        self.calls: List[Dict[str, Any]] = []

    def resolve_battle(
        self, fleets, modifiers=None, seed=None, registries=None,
        environmental_effects=None, empires=None,
    ):
        fleet_list = list(fleets)
        self.calls.append({
            "fleets": fleet_list,
            "seed": seed,
            "empires": empires,
        })
        if self._mutator is not None:
            self._mutator(fleet_list)
        if not self._results:
            # Default — no-op draw with all fleets retained.
            return BattleResult(
                winner=None,
                tick_count=1,
                team_survivors={
                    i: list(f.ships) for i, f in enumerate(fleet_list)
                },
            )
        return self._results.pop(0)


def _engine_with(resolver: IBattleResolver, *, event_bus=None):
    engine = ConflictResolutionEngine(
        battle_resolver=resolver,
        event_bus=event_bus,
    )
    engine._empires = []
    engine._combats_resolved = 0
    engine._fleets_destroyed = []
    return engine


# ===========================================================================
# Contract: draws no longer destroy a fleet
# ===========================================================================


class TestDrawDoesNotDestroyFleet:
    """A `winner=None` BattleResult must NOT cause any fleet removal.

    Pre-BUG-126: a survivor-count tiebreaker silently picked a 'winner'
    and the strategy layer deleted the 'loser' fleet — even though
    every ship survived. After the fix, both fleets remain.
    """

    def test_draw_with_survivors_on_both_sides_keeps_both_fleets(self):
        """The BUG-126 reproduction scenario.

        Two fleets, one with 1 ship and one with 5 ships. Battle ends
        as a draw (e.g. simulator timeout). Neither fleet should be
        removed from its empire.
        """
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=1)
        f2 = _fleet(2, owner_id=1, ship_count=5)
        emp1.fleets.append(f1)
        emp2.fleets.append(f2)

        resolver = _ScriptedResolver([
            BattleResult(
                winner=None,
                tick_count=20000,
                team_survivors={
                    0: list(f1.ships),
                    1: list(f2.ships),
                },
            ),
        ])
        engine = _engine_with(resolver)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        emp1.remove_fleet.assert_not_called()
        emp2.remove_fleet.assert_not_called()
        assert engine._fleets_destroyed == []
        assert engine._combats_resolved == 1

    def test_draw_with_one_destroyed_one_intact(self):
        """If draw-but-one-team-wiped, only the wiped fleet was
        already pruned by the hook; engine doesn't touch either."""
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=1)
        f2 = _fleet(2, owner_id=1, ship_count=2)
        emp1.fleets.append(f1)
        emp2.fleets.append(f2)

        # Simulate the hook clearing f1.ships (all destroyed).
        def _wipe_team0(fleets):
            fleets[0].ships = []

        resolver = _ScriptedResolver(
            [BattleResult(
                winner=None,  # Draw because winner detection didn't fire
                tick_count=500,
                team_survivors={0: [], 1: list(f2.ships)},
            )],
            mutator=_wipe_team0,
        )
        engine = _engine_with(resolver)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        # The strategy layer no longer removes ANY fleet — pruning of
        # empty fleets is the hook's job (mocked away here).
        emp1.remove_fleet.assert_not_called()
        emp2.remove_fleet.assert_not_called()


# ===========================================================================
# Contract: clear-victory does not destroy non-empty fleets
# ===========================================================================


class TestClearVictoryDoesNotDestroyNonEmptyFleets:
    """`BattleResult.winner=N` no longer means 'remove the other fleets'.

    Even when the resolver reports a winner, the strategy engine must
    not remove a non-empty fleet — the hook handles real destruction.
    """

    def test_winner_reported_but_loser_fleet_intact_means_no_removal(self):
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=2)
        f2 = _fleet(2, owner_id=1, ship_count=2)
        emp1.fleets.append(f1)
        emp2.fleets.append(f2)

        resolver = _ScriptedResolver([
            BattleResult(
                winner=0,
                tick_count=400,
                team_survivors={0: list(f1.ships), 1: list(f2.ships)},
            ),
        ])
        engine = _engine_with(resolver)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        emp1.remove_fleet.assert_not_called()
        emp2.remove_fleet.assert_not_called()


# ===========================================================================
# Contract: re-engagement on subsequent ticks
# ===========================================================================


# PROJ-320 Phase 4 Task 4.6: deleted `TestReEngagementOnSubsequentTick`.
# That class encoded the legacy per-tick re-engagement behaviour where
# every call to `resolve_all_conflicts` unconditionally fired combat at
# every contested hex (~100 battles per turn). PROJ-320 replaced that
# with per-fleet movement-opportunity triggering — combat fires only on
# the engaged fleets' opportunity ticks (`tick % get_tick_interval(speed)
# == 0`). The "two back-to-back resolve_all_calls each fire one battle"
# assertion is no longer meaningful — opportunity ticks are sparse.
# Round-budget semantics are now covered by `tests/integration/strategy/
# test_combat_round_budget.py` and `tests/unit/strategy/engine/
# test_conflict_round_budget.py`.


# ===========================================================================
# Contract: total wipe DOES propagate the destroyed-fleet id
# ===========================================================================


class TestTotalWipeReportsDestroyedFleet:
    """When the hook wipes a fleet to zero ships, the engine reports its
    id in `_fleets_destroyed` — for empire-level audit/event payloads.
    """

    def test_total_wipe_reports_destroyed_fleet_id(self):
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=2)
        f2 = _fleet(2, owner_id=1, ship_count=2)
        emp1.fleets = [f1]
        emp2.fleets = [f2]

        # Hook wipes team 1.
        def _wipe_team1(fleets):
            fleets[1].ships = []

        resolver = _ScriptedResolver(
            [BattleResult(
                winner=0,
                tick_count=500,
                team_survivors={0: list(f1.ships), 1: []},
            )],
            mutator=_wipe_team1,
        )
        engine = _engine_with(resolver)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert engine._fleets_destroyed == [2]

    def test_no_wipe_no_destroyed_fleet_id(self):
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=1)
        f2 = _fleet(2, owner_id=1, ship_count=1)
        emp1.fleets = [f1]
        emp2.fleets = [f2]

        resolver = _ScriptedResolver([
            BattleResult(
                winner=None, tick_count=20000,
                team_survivors={0: list(f1.ships), 1: list(f2.ships)},
            ),
        ])
        engine = _engine_with(resolver)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert engine._fleets_destroyed == []


# ===========================================================================
# Schema: COMBAT_RESOLVED event carries new column names
# ===========================================================================


class TestCombatResolvedEventSchema:
    """Hard schema migration: `participating_fleet_ids` /
    `surviving_fleet_ids` / `destroyed_fleet_ids`. No `winner_fleet_id`,
    no `loser_fleet_id` (BUG-126 hard migration per project ERADICATE
    policy).
    """

    def test_new_keys_present(self):
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=1)
        f2 = _fleet(2, owner_id=1, ship_count=2)
        emp1.fleets = [f1]
        emp2.fleets = [f2]

        def _wipe_team0(fleets):
            fleets[0].ships = []

        resolver = _ScriptedResolver(
            [BattleResult(
                winner=1,
                tick_count=300,
                team_survivors={0: [], 1: list(f2.ships)},
            )],
            mutator=_wipe_team0,
        )
        calls, bus = _capture_log_event_calls()
        engine = _engine_with(resolver, event_bus=bus)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMBAT_RESOLVED
        assert kw["category"] == EventCategory.COMBAT
        assert sorted(kw["participating_fleet_ids"]) == [1, 2]
        assert kw["surviving_fleet_ids"] == [2]
        assert kw["destroyed_fleet_ids"] == [1]

    def test_legacy_keys_absent(self):
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=1)
        f2 = _fleet(2, owner_id=1, ship_count=1)
        emp1.fleets = [f1]
        emp2.fleets = [f2]

        resolver = _ScriptedResolver([
            BattleResult(
                winner=None, tick_count=20000,
                team_survivors={0: list(f1.ships), 1: list(f2.ships)},
            ),
        ])
        calls, bus = _capture_log_event_calls()
        engine = _engine_with(resolver, event_bus=bus)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert len(calls) == 1
        _, kw = calls[0]
        assert "winner_fleet_id" not in kw
        assert "loser_fleet_id" not in kw

    def test_event_emits_for_draw(self):
        """Pre-BUG-126 the event was paired (winner vs each loser),
        so a draw with `winner_team_id is None` skipped logging
        entirely. Post-fix, every resolved combat emits exactly one
        event regardless of winner."""
        emp1 = _empire(0)
        emp2 = _empire(1)
        f1 = _fleet(1, owner_id=0, ship_count=1)
        f2 = _fleet(2, owner_id=1, ship_count=2)
        emp1.fleets = [f1]
        emp2.fleets = [f2]

        resolver = _ScriptedResolver([
            BattleResult(
                winner=None, tick_count=20000,
                team_survivors={0: list(f1.ships), 1: list(f2.ships)},
            ),
        ])
        calls, bus = _capture_log_event_calls()
        engine = _engine_with(resolver, event_bus=bus)
        engine._empires = [emp1, emp2]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert len(calls) == 1
        _, kw = calls[0]
        assert sorted(kw["participating_fleet_ids"]) == [1, 2]
        assert sorted(kw["surviving_fleet_ids"]) == [1, 2]
        assert kw["destroyed_fleet_ids"] == []

    def test_three_team_battle_emits_one_event_with_all_participants(self):
        """N-team battles report all participants in a single event,
        not N-1 winner/loser pairs."""
        emp1 = _empire(0)
        emp2 = _empire(1)
        emp3 = _empire(2)
        f1 = _fleet(11, owner_id=0, ship_count=1)
        f2 = _fleet(22, owner_id=1, ship_count=1)
        f3 = _fleet(33, owner_id=2, ship_count=1)
        emp1.fleets = [f1]; emp2.fleets = [f2]; emp3.fleets = [f3]

        def _wipe_team1_and_team2(fleets):
            fleets[1].ships = []
            fleets[2].ships = []

        resolver = _ScriptedResolver(
            [BattleResult(
                winner=0,
                tick_count=500,
                team_survivors={0: list(f1.ships), 1: [], 2: []},
            )],
            mutator=_wipe_team1_and_team2,
        )
        calls, bus = _capture_log_event_calls()
        engine = _engine_with(resolver, event_bus=bus)
        engine._empires = [emp1, emp2, emp3]

        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2), (emp3, f3)])

        assert len(calls) == 1
        _, kw = calls[0]
        assert sorted(kw["participating_fleet_ids"]) == [11, 22, 33]
        assert kw["surviving_fleet_ids"] == [11]
        assert sorted(kw["destroyed_fleet_ids"]) == [22, 33]


# ===========================================================================
# Shortcut paths in SimulationBattleResolver
# ===========================================================================


class TestSimulationBattleResolverShortcutPaths:
    """The three shortcut branches at simulation_adapter.py:116-137.

    These paths exist to skip the simulator when no real combat is
    possible — e.g. a fleet of derelicts vs an armed fleet.
    """

    def _make_resolver(self):
        from game.simulation.interfaces.ai_controller import IAIControllerFactory
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )
        ai_factory = MagicMock(spec=IAIControllerFactory)
        return SimulationBattleResolver(ai_factory=ai_factory)

    def _ship(self, *, alive=True, derelict=False):
        s = MagicMock()
        s.is_alive = alive
        s.is_derelict = derelict
        s.is_combat_capable = MagicMock(return_value=alive and not derelict)
        return s

    def _fleet_with_ships(self, fleet_id, owner_id, ships):
        f = MagicMock()
        f.id = fleet_id
        f.owner_id = owner_id
        f.ships = ships
        f.location = HexCoord(0, 0)
        return f

    def test_no_combat_capable_either_team_runs_truncated_simulator(self):
        """Issue #8: when both teams have ships but no combat-capable
        ones, the resolver no longer short-circuits — it runs a brief
        truncated simulator pass so the replay-capture pipeline records
        a real (short) replay. ``run_battle`` is patched here because
        the test fleets carry mock ships that can't be materialized."""
        from unittest.mock import patch

        from game.simulation.battle_outcome import ShipStatus

        resolver = self._make_resolver()
        f1 = self._fleet_with_ships(
            1, 0, [self._ship(alive=False), self._ship(derelict=True)],
        )
        f2 = self._fleet_with_ships(
            2, 1, [self._ship(derelict=True)],
        )

        # Mock outcome — neither team is eliminable in a no-weapons
        # battle, so the truncated run terminates at the cap. Both
        # teams still have ships at end so winner is None.
        outcome = MagicMock()
        outcome.duration_ticks = 2000
        outcome.replay_id = "trunc-replay-uuid"
        team0 = MagicMock()
        team0.team_id = 0
        team0.ships = [MagicMock(status=ShipStatus.SURVIVED)]
        team1 = MagicMock()
        team1.team_id = 1
        team1.ships = [MagicMock(status=ShipStatus.SURVIVED)]
        outcome.teams = (team0, team1)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            return_value=outcome,
        ) as mock_run:
            result = resolver.resolve_battle([f1, f2])

        mock_run.assert_called_once()
        assert result.winner is None  # Both teams alive at cap
        assert 0 < result.tick_count <= 2000
        assert result.replay_id == "trunc-replay-uuid"
        assert result.replay_unavailable_reason is None

    def test_only_one_team_combat_capable_declares_sole_survivor(self):
        """Shortcut #2: only one team has any combat-capable ships."""
        resolver = self._make_resolver()
        f1 = self._fleet_with_ships(
            1, 0, [self._ship(alive=True)],
        )
        f2 = self._fleet_with_ships(
            2, 1, [self._ship(alive=False), self._ship(derelict=True)],
        )

        # We don't care about the survivors list contents for this
        # contract test — just that the simulator was bypassed and a
        # winner was declared.
        survivor_ship = MagicMock()
        f1.ships[0].to_ship = MagicMock(return_value=survivor_ship)

        result = resolver.resolve_battle([f1, f2])

        assert result.winner == 0
        assert result.tick_count == 0
