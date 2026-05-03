"""Integration tests for PROJ-320 strategic combat round-budget model.

Drives `ConflictResolutionEngine.resolve_all_conflicts` across a 100-tick
strategic turn and asserts the new round-count semantics:

  * Two stalemated fleets (speed 6 + speed 4) → exactly 10 battles per turn,
    not 100 (the legacy per-tick scan rate).
  * Three empires sharing a hex → sum-of-speeds rounds (5 + 4 + 3 = 12).
  * One fleet leaving mid-turn stops contributing rounds for that fleet's
    remaining opportunities; the other side keeps firing.
  * One empire holding TWO co-located fleets contributes both — every fleet
    fires its own movement-opportunity rounds (eliminates the silent
    one-fleet-per-empire batching at `conflict_resolution_engine.py:298-300`).

Until Phase 3 (multi-fleet-per-empire) and Phase 4 (per-fleet-tick triggering)
land, every test in this file is expected to fail. Three modes of failure
are possible depending on what's been touched:

  - `TypeError`: today's `resolve_all_conflicts(empires, galaxy=None)` does
    NOT accept `tick=` / `moved_fleet_ids=` kwargs that the new model needs.
  - Wrong call count: if the kwargs are accepted but the legacy per-tick
    scan still fires every tick, the count comes out at 100 instead of 10.
  - Multi-fleet undercount: even after Phase 3 lands, the fourth test still
    fails until Phase 4 cuts over to per-fleet triggering.

This is the documented red baseline (Phase 1 Task 1.5).
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
    """Records every `resolve_battle` invocation but never wipes ships.

    Mirrors `_RecordingResolver` from `test_three_empire_battle.py` but
    KEEPS every fleet's ships list intact between rounds, so a stalemate
    can persist for the full 100-tick turn. This is the correct fixture
    for round-count assertions: we want to count how many times combat
    fires, not how many ships died.
    """

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def resolve_battle(self, fleets, modifiers=None, seed=None,
                       registries=None, environmental_effects=None,
                       empires=None) -> BattleResult:
        fleet_list = list(fleets)
        self.calls.append({
            "fleets": fleet_list,
            "fleet_ids": [f.id for f in fleet_list],
            "owner_ids": [f.owner_id for f in fleet_list],
        })
        # Do NOT wipe any ships — both sides survive, encounter persists.
        return BattleResult(
            winner=None,
            tick_count=1,
            team_survivors={tid: [MagicMock()] for tid in range(len(fleet_list))},
        )


def _make_fleet(fleet_id: int, owner_id: int, location, speed: float):
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = location
    fleet.speed = float(speed)
    fleet.ships = [MagicMock()]
    fleet.task_forces = []
    fleet.orders = []
    return fleet


def _make_empire(empire_id: int, fleets):
    empire = MagicMock()
    empire.id = empire_id
    empire.fleets = list(fleets)
    return empire


def _run_full_turn(engine, empires, *, fleets_that_leave_at_tick=None):
    """Drive 100 ticks of `resolve_all_conflicts`.

    `fleets_that_leave_at_tick` maps `tick -> set[fleet_id]` and lets a
    test simulate "fleet X actually left the contested hex on tick N"
    without exercising the real `FleetMovementEngine`.
    """
    fleets_that_leave_at_tick = fleets_that_leave_at_tick or {}
    for tick in range(1, TICKS_PER_TURN + 1):
        moved_fleet_ids: set[int] = set(fleets_that_leave_at_tick.get(tick, set()))
        engine.resolve_all_conflicts(
            empires,
            tick=tick,
            moved_fleet_ids=moved_fleet_ids,
        )


def test_two_stalemated_fleets_resolve_in_sum_of_speeds_rounds():
    """Fleet A (speed 6) + Fleet B (speed 4) co-located, neither moves.
    Total combat rounds across 100-tick turn: 6 + 4 = 10.

    Speed 6 → tick interval 100//6 = 16 → opportunities at 16, 32, 48,
    64, 80, 96 (6 events).
    Speed 4 → tick interval 100//4 = 25 → opportunities at 25, 50, 75,
    100 (4 events).
    Union has no shared ticks; total per-fleet-trigger events = 10.
    """
    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    location = HexCoord(0, 0)
    fleet_a = _make_fleet(1, owner_id=0, location=location, speed=6)
    fleet_b = _make_fleet(2, owner_id=1, location=location, speed=4)
    empires = [
        _make_empire(0, [fleet_a]),
        _make_empire(1, [fleet_b]),
    ]

    _run_full_turn(engine, empires)

    assert len(resolver.calls) == 10, (
        f"Expected 6+4=10 combat rounds for stalemated speed-6 vs speed-4 "
        f"fleets, got {len(resolver.calls)}. The legacy per-tick scan would "
        f"produce ~100 rounds; PROJ-320 must produce 10."
    )


def test_three_team_stalemate_sums_speeds():
    """Three empires (speeds 5/4/3) co-located, none move.
    Total rounds = 5 + 4 + 3 = 12.
    """
    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    location = HexCoord(0, 0)
    empires = [
        _make_empire(0, [_make_fleet(1, 0, location, speed=5)]),
        _make_empire(1, [_make_fleet(2, 1, location, speed=4)]),
        _make_empire(2, [_make_fleet(3, 2, location, speed=3)]),
    ]

    _run_full_turn(engine, empires)

    assert len(resolver.calls) == 12, (
        f"Expected 5+4+3=12 combat rounds for three-team stalemate, "
        f"got {len(resolver.calls)}."
    )


def test_one_fleet_leaves_mid_turn_stops_contributing():
    """Fleet A (speed 5) and Fleet B (speed 5) co-located; Fleet A leaves
    on tick 60 (one of its own opportunity ticks).

    Both fleets share opportunity ticks at multiples of 20 (interval = 20).
    So opportunity ticks = {20, 40, 60, 80, 100}.

    PROJ-320 rule:
      - Tick 20: A and B both stay → 2 rounds (one per fleet)
      - Tick 40: A and B both stay → 2 rounds
      - Tick 60: A leaves (skipped). B has its own opportunity tick BUT
        hex H is no longer contested (A relocated to elsewhere before
        Phase 4 fires) → 0 rounds
      - Tick 80: A is gone, B alone at H → 0 rounds
      - Tick 100: same → 0 rounds

    Total: 2 + 2 + 0 + 0 + 0 = 4 rounds. Once a hex stops being
    contested, opportunity ticks for the remaining fleet stop firing
    combat — the trigger is per-fleet AND per-contested-hex.

    NOTE: this test simulates "A left" by both (a) marking A's id in
    `moved_fleet_ids` for tick 60 and (b) updating A's location to a
    non-contested hex from tick 60 onward, mimicking what
    `FleetMovementEngine.apply_movements` would do.
    """
    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    contested = HexCoord(0, 0)
    elsewhere = HexCoord(5, -5)
    fleet_a = _make_fleet(1, owner_id=0, location=contested, speed=5)
    fleet_b = _make_fleet(2, owner_id=1, location=contested, speed=5)
    empires = [_make_empire(0, [fleet_a]), _make_empire(1, [fleet_b])]

    # Custom turn loop: at tick 60, mark Fleet A as "moved" AND relocate it.
    for tick in range(1, TICKS_PER_TURN + 1):
        moved: set[int] = set()
        if tick == 60:
            moved = {fleet_a.id}
            fleet_a.location = elsewhere  # Phase 3 outcome, before Phase 4
        engine.resolve_all_conflicts(
            empires, tick=tick, moved_fleet_ids=moved,
        )

    assert len(resolver.calls) == 4, (
        f"Expected 4 rounds (A+B fire at ticks 20 + 40 = 4 rounds; A "
        f"leaves at tick 60 leaving B alone at the hex, so no further "
        f"combat fires), got {len(resolver.calls)}."
    )


def test_two_fleets_one_empire_both_participate_in_battle():
    """PROJ-320 Phase 3 acceptance: when Empire 0 has TWO fleets co-located
    with Empire 1's one fleet, ALL THREE fleets must reach the battle
    resolver. Pre-PROJ-320 the conflict engine kept only Empire 0's
    first fleet; the others sat idle.

    This test exercises `_resolve_combat_at_hex` directly (one tick worth
    of combat) so it's independent of the per-fleet-tick triggering work
    landing in Phase 4.
    """
    from game.strategy.engine.conflict_resolution_engine import (
        ConflictResolutionEngine,
    )

    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)
    engine._empires = []  # combat_modifier_collector skip

    location = HexCoord(0, 0)
    fleet1 = _make_fleet(101, owner_id=0, location=location, speed=5)
    fleet2 = _make_fleet(102, owner_id=0, location=location, speed=4)
    fleet3 = _make_fleet(201, owner_id=1, location=location, speed=5)
    empire_a = _make_empire(0, [fleet1, fleet2])
    empire_b = _make_empire(1, [fleet3])

    # Direct invocation of _resolve_combat_at_hex with the contested-hex roster.
    occupants = [
        (empire_a, fleet1),
        (empire_a, fleet2),
        (empire_b, fleet3),
    ]
    engine._resolve_combat_at_hex(occupants)

    assert len(resolver.calls) == 1, (
        f"Expected ONE battle resolving all three fleets, got "
        f"{len(resolver.calls)} battles."
    )
    fleet_ids_seen = sorted(resolver.calls[0]["fleet_ids"])
    assert fleet_ids_seen == [101, 102, 201], (
        f"Expected all three fleets [101, 102, 201] in the battle, got "
        f"{fleet_ids_seen}. Pre-PROJ-320, only [101, 201] would appear."
    )


def test_event_payload_includes_all_participating_fleets():
    """PROJ-320 Phase 3: the COMBAT_RESOLVED event payload's
    `participating_fleet_ids` field must list ALL fleets that fought,
    including multiple fleets per empire.
    """
    from game.strategy.engine.conflict_resolution_engine import (
        ConflictResolutionEngine,
    )

    captured_events = []

    class _RecordingBus:
        def log_event(self, event_type, **kwargs):
            captured_events.append((event_type, kwargs))

    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(
        battle_resolver=resolver, event_bus=_RecordingBus()
    )
    engine._empires = []
    # `_lookup_environmental_effects` checks `_galaxy is None` first
    # and short-circuits with None — leaving `_galaxy` unset (None) is fine.

    location = HexCoord(3, 4)
    fleet1 = _make_fleet(11, owner_id=0, location=location, speed=5)
    fleet2 = _make_fleet(12, owner_id=0, location=location, speed=5)
    fleet3 = _make_fleet(21, owner_id=1, location=location, speed=5)
    empire_a = _make_empire(0, [fleet1, fleet2])
    empire_b = _make_empire(1, [fleet3])

    occupants = [
        (empire_a, fleet1),
        (empire_a, fleet2),
        (empire_b, fleet3),
    ]
    engine._resolve_combat_at_hex(occupants)

    # Exactly one COMBAT_RESOLVED event emitted (one battle).
    combat_events = [
        e for e in captured_events
        if str(e[0]).endswith("COMBAT_RESOLVED")
    ]
    assert len(combat_events) == 1, (
        f"Expected one COMBAT_RESOLVED event, got {len(combat_events)}"
    )
    _, payload = combat_events[0]
    participating = sorted(payload["participating_fleet_ids"])
    assert participating == [11, 12, 21], (
        f"Expected participating_fleet_ids=[11, 12, 21], got {participating}. "
        f"All allied fleets must appear in the event payload."
    )


def test_empire_with_two_fleets_each_contributes_rounds():
    """Empire 0 has Fleet1 (speed 5) and Fleet2 (speed 4) co-located with
    Empire 1's Fleet3 (speed 5). Total per-fleet-trigger events:
    5 + 4 + 5 = 14 rounds.

    This case ALSO exposes the silent "one fleet per empire" batching
    bug at `conflict_resolution_engine.py:298-300`: today's code keeps
    only Fleet1 (the first encountered fleet for empire 0) and silently
    drops Fleet2 from the battle, so the count comes out wrong even
    BEFORE Phase 4's per-fleet-tick logic lands.

    Phase 3 fixes the batching; Phase 4 fixes the round count. Both are
    needed for this test to go green.
    """
    resolver = _NonDestructiveResolver()
    engine = ConflictResolutionEngine(battle_resolver=resolver)

    location = HexCoord(0, 0)
    fleet1 = _make_fleet(101, owner_id=0, location=location, speed=5)
    fleet2 = _make_fleet(102, owner_id=0, location=location, speed=4)
    fleet3 = _make_fleet(201, owner_id=1, location=location, speed=5)
    empires = [
        _make_empire(0, [fleet1, fleet2]),
        _make_empire(1, [fleet3]),
    ]

    _run_full_turn(engine, empires)

    assert len(resolver.calls) == 14, (
        f"Expected 5+4+5=14 rounds (every fleet contributes its own "
        f"opportunities), got {len(resolver.calls)}."
    )
