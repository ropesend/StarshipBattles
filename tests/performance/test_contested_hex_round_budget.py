"""Performance regression gate for PROJ-320 strategic combat round budget.

Pre-PROJ-320, two stationary co-located fleets fired combat once per
sub-tick of every strategic turn (`TICKS_PER_TURN = 100`), producing up
to ~100 battles per contested sector per turn — see the BUG-126
follow-up note in `docs/systems/combat_simulation.md` § 9. PROJ-320
shifted to per-fleet movement-opportunity triggering: combat fires
once per fleet per `tick % get_tick_interval(fleet.speed) == 0` tick,
gated by whether the fleet successfully left the hex on that tick.

This module locks in the combat-invocation reduction so any future
change that re-introduces the per-tick scan (or any other inflation
in dispatch count) trips the regression gate.

These are count-based assertions (not wall-clock benchmarks) — wall
time is dominated by the simulator's internal cost which lives outside
the strategy layer. The win is a multiplicative reduction in the number
of times the simulator gets invoked.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.engine.conflict_resolution_engine import (
    ConflictResolutionEngine,
)
from game.strategy.interfaces.battle_resolver import (
    BattleResult,
    IBattleResolver,
)


TICKS_PER_TURN = 100


class _NonDestructiveResolver(IBattleResolver):
    """Counts `resolve_battle` invocations; never wipes ships.

    Mirrors the helper in `tests/integration/strategy/test_combat_round_budget.py`
    — duplicated here so the perf gate has no cross-suite import.
    """

    def __init__(self) -> None:
        self.calls: list = []

    def resolve_battle(self, fleets, modifiers=None, seed=None,
                       registries=None, environmental_effects=None,
                       empires=None) -> BattleResult:
        fleet_list = list(fleets)
        self.calls.append({"fleet_count": len(fleet_list)})
        # Stalemated battle: every team retains its ships.
        return BattleResult(
            winner=None,
            tick_count=1,
            team_survivors={tid: [MagicMock()] for tid in range(len(fleet_list))},
        )


# PROJ-479 Task 5.1 (DUP-001): _make_fleet moved to tests/conftest.py.
from tests.conftest import _make_mock_fleet as _make_fleet  # noqa: E402


def _make_empire(empire_id, fleets):
    empire = MagicMock()
    empire.id = empire_id
    empire.fleets = list(fleets)
    return empire


def _run_full_turn(engine, empires) -> None:
    """Drive 100 ticks of `resolve_all_conflicts` with no movement."""
    for tick in range(1, TICKS_PER_TURN + 1):
        engine.resolve_all_conflicts(
            empires, tick=tick, moved_fleet_ids=set(),
        )


def test_two_stalemated_fleets_at_speed_5_resolve_in_10_rounds():
    """Round-budget gate: speed-5 vs speed-5 stalemate fires 10 rounds
    per turn (not 100).

    Pre-PROJ-320: 100 dispatches.
    PROJ-320: 5 opportunity ticks × 2 fleets = 10 dispatches.
    """
    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    location = HexCoord(0, 0)
    empires = [
        _make_empire(0, [_make_fleet(1, 0, location, speed=5)]),
        _make_empire(1, [_make_fleet(2, 1, location, speed=5)]),
    ]

    _run_full_turn(engine, empires)

    assert len(resolver.calls) == 10, (
        f"Expected 10 round-budget dispatches for the speed-5 vs speed-5 "
        f"stalemate (5 opportunities × 2 fleets), got {len(resolver.calls)}. "
        f"The pre-PROJ-320 per-tick scan would produce ~100."
    )


def test_five_contested_hexes_three_empires_two_fleets_each():
    """The Performance Analyst swarm-agent's recommended scenario.

    Setup: 5 contested hexes, 3 empires per hex, 2 fleets per empire,
    all at speed 5 (interval 20). Stalemate — nobody moves.

    Per hex: 6 fleets × 5 opportunity ticks each = 30 dispatches.
    Across 5 hexes: 150 dispatches per turn.

    Pre-PROJ-320: 5 hexes × 100 ticks = 500+ dispatches per turn.
    PROJ-320 ratio: ≤30% of the legacy invocation count.
    """
    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    empires = [_make_empire(eid, []) for eid in range(3)]
    fleet_id = 1
    for hex_idx in range(5):
        loc = HexCoord(hex_idx * 10, 0)
        for empire_idx, empire in enumerate(empires):
            for _ in range(2):  # 2 fleets per empire per hex
                empire.fleets.append(
                    _make_fleet(fleet_id, empire_idx, loc, speed=5)
                )
                fleet_id += 1

    _run_full_turn(engine, empires)

    assert len(resolver.calls) <= 150, (
        f"Performance regression: expected ≤150 combat dispatches for the "
        f"5-hex × 3-empire × 2-fleet scenario, got {len(resolver.calls)}. "
        f"Pre-PROJ-320 baseline was 500+. If this assertion fires, the "
        f"per-tick scan has been reintroduced or the trigger predicate is "
        f"firing when it shouldn't."
    )

    # Sanity: every dispatch is a 6-fleet (3-team-of-2) battle.
    for call in resolver.calls:
        assert call["fleet_count"] == 6, (
            f"Each dispatch should include all 6 co-located fleets; "
            f"got {call['fleet_count']}."
        )
