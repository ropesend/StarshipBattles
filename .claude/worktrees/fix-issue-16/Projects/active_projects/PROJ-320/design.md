# PROJ-320: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Overview

The strategic layer's `ConflictResolutionEngine.resolve_all_conflicts(...)` is invoked by `TurnEngine` once per sub-tick (100 times per turn). Each invocation rebuilds a hex-map from `Empire.fleets` and fires a battle for any hex containing fleets from ≥2 empires. With both fleets stalemated, this produces ~100 sequential battles per contested hex per turn — visible in the event log as page after page of "Battle: 2 fleets engaged: no fleet destroyed" rows.

The user-confirmed model: combat fires once per **fleet** per **movement-opportunity tick** (`tick % get_tick_interval(fleet.speed) == 0`), gated by whether the fleet actually leaves the hex on that tick. Two fleets at speeds 6 and 4 in one hex resolve in 6 + 4 = 10 rounds, not 100. Fewer rounds, fewer event-log entries, faster turns, more semantic combat pacing.

## Initial Analysis

### Confirmed by code review (Phase A):

- **`turn_engine.py:524`** — `for tick in range(1, TICKS_PER_TURN + 1)` loop, `TICKS_PER_TURN = 100`.
- **`turn_engine.py:698`** — `self.conflict_engine.resolve_all_conflicts(empires, galaxy=galaxy)` called unconditionally every tick.
- **`conflict_resolution_engine.py:247-268`** — `_resolve_conflicts()` rebuilds `hex_map: Dict[HexCoord, List[(Empire, Fleet)]]` from scratch each call.
- **`conflict_resolution_engine.py:269-374`** — `_resolve_combat_at_hex()` filters to ONE fleet per empire (line 298-300) before invoking the battle resolver.
- **`fleet_speed_calculator.py:39-58`** — `get_tick_interval(speed) = max(1, int(100 // speed))`. Already the function we need.
- **`fleet_movement_engine.py:209-270`** — `collect_movements()` already iterates every empire's every fleet and checks `tick % interval == 0`. The exact pattern the new combat trigger needs.
- **No per-fleet "next movement tick" or "remaining moves" counter exists today** — the model is purely derivative from `tick % interval`.

### Documented as known follow-up:

`docs/systems/combat_simulation.md` §9 (BUG-126 "Performance follow-up"):

> Two stationary co-located fleets re-engage every sub-tick of every turn (up to 100 battles per turn) until one side is wiped. With weaponless fleets the simulator runs to its `absolute_max_ticks` ceiling each time — ~4.4s per battle observed in BUG-126's repro. A follow-on ticket should add an early-termination condition (e.g. "no damage dealt by either side in last N ticks → end as draw") or a tighter strategy-layer `absolute_max_ticks` ceiling.

PROJ-320 **is** that follow-on ticket.

### Pre-existing bug surfaced during review:

- **`order_processor.py::_execute_fleet_merge` (line ~86)** — when Fleet A merges into Fleet B in Phase 1 of a tick, the merged fleet's speed is **not** recalculated. With the new model dependent on accurate per-fleet movement intervals, this latent bug becomes a correctness issue and is fixed in scope (Phase 2).

## Swarm Findings Summary

Six Phase B explore agents wrote findings under `findings/`. Combined verdicts:

### Architecture (from Pattern Scout, API Contract Reviewer)

- **Implementation site:** Modify `ConflictResolutionEngine` in place. **Do not** create a new sub-engine, `TurnEngineConfig` field, or `IConflictEngine` method.
- **Trigger model:** Stay stateless. Re-derive contested-hex membership each tick from `Empire.fleets`. No "active encounter" registry, no per-fleet `last_combat_tick` field.
- **Iteration:** New trigger predicate iterates fleets in `(empire_id, fleet_id)` tuple order to preserve deterministic battle seeding (mirrors `conflict_resolution_engine.py:305`).
- **Naming:** New private helper `_should_trigger_combat_for_fleet(fleet, tick) -> bool`.

### Key Patterns to Reuse

- **Sub-engine pattern (PROJ-251):** `_validate_tick_inputs(empires)` precondition validation already in place at `conflict_resolution_engine.py:196-209` — extend to validate the new trigger inputs.
- **Phase wrapping (Pattern #19):** `_time_phase()` in `turn_engine.py:238-283` already wraps Phase 4 dispatch — no change.
- **Snapshot rollback (Pattern #20):** `TurnStateSnapshot` round-trips Fleet via `to_dict/from_dict` — since no new Fleet fields are added, no migration risk.
- **Movement-opportunity check pattern:** `fleet_movement_engine.py:237-249` (`if tick % interval == 0`) is the model.
- **Deterministic empire ordering:** `conflict_resolution_engine.py:305` (`sorted(fleets_by_empire.keys())`) is the model.

### Dependencies & Risks (from Risk Assessor)

1. **HIGH — Roster staleness within a tick.** When multiple combat rounds fire at the same hex in one tick (because two fleets' opportunity ticks coincide), the second round must re-derive the fleet roster from `Empire.fleets`, not reuse a cached `hex_map`. Otherwise destroyed fleets are still referenced. **Mitigation:** rebuild fleet list per round inside the trigger loop. Phase 4 task.
2. **HIGH — Mid-encounter fleet destruction.** Same root cause as #1.
3. **HIGH — Pre-existing fleet-merge speed-recalc gap.** `_execute_fleet_merge` doesn't call `FleetSpeedCalculator.update_fleet_speed(target)` after merging. With the new model, an incorrect post-merge speed produces wrong opportunity-tick cadence. **Mitigation:** Phase 2 fix.
4. **MEDIUM — Multi-fleet per empire batching.** Today `fleets_by_empire: Dict[int, Fleet]` keeps only the first fleet per empire (`conflict_resolution_engine.py:295-300`). Other fleets sit idle. User confirmed every fleet should fight independently. **Mitigation:** change to `Dict[int, List[Fleet]]`. Phase 3 task.
5. **MEDIUM — Speed change mid-turn from combat damage** is reactive (recomputed next tick). Acceptable; documented in `decisions.md`.

### Opportunities Discovered

- **Hex-map scan is still O(fleets) per tick** (Performance Analyst). Re-architecting it to event-driven (only re-scan when a fleet moves in Phase 3) would save another constant factor — but it is a separate optimization opportunity, **not** in scope for PROJ-320. The 10× win from PROJ-320 is sufficient.
- **`_log_combat_result` empire-id quirk** uses `min(participating_empire_ids)` for the event-log filter column — this stays correct under the new model (data flow agent verified).

### Data Flow

| Concern | PROJ-320 impact |
|---------|-----------------|
| Fleet persistent state | NONE — model is stateless |
| Save format | UNCHANGED |
| `FleetInfo` / `FleetInfoExtended` DTOs | UNCHANGED |
| `COMBAT_RESOLVED` event payload | UNCHANGED |
| `BattleResult` DTO | UNCHANGED |
| `ConflictResult` DTO | UNCHANGED — semantics preserved (count of rounds fired) |
| Replay store ring buffer | Fewer files, well below cap |

### API Contracts

| Interface | PROJ-320 impact |
|-----------|-----------------|
| `IConflictEngine.resolve_all_conflicts` | UNCHANGED |
| `IBattleResolver.resolve_battle` | UNCHANGED |
| `BattleSpec` (via `build_strategy_battle_spec`) | UNCHANGED |
| `PostBattleHook.apply_outcome_to_fleets` | Verified idempotent under multiple invocations per encounter |
| `Fleet` public API | UNCHANGED |
| `get_tick_interval` consumers | Expanded from 1 → 2 (movement engine + conflict engine) — read-only |
| Mock impls (`MockConflictEngine`, `MockResolver`, `InstantBattleResolver`) | NO updates required |

### UI Impact

- **Event Log (only affected surface):** Fewer combat rows per encounter, dramatically more readable. Empire-id filter logic unchanged.
- **No production UI code changes.** All UI is volume-agnostic.
- **Test impact MEDIUM:** Tests with hardcoded "expect N COMBAT_RESOLVED events per turn" assertions need updating.
- **Issue #8 (replay button)** is independent — neither fixed nor worsened by PROJ-320.
- **Issue #7 (tick number on Processing Turn overlay)** is independent — Phase 4 still blocks the UI synchronously.

### Performance

- **Expected speedup: ~10×** for typical contested-hex scenarios.
  - Today: 2 contested hexes × 100 ticks ≈ 200 battle invocations × ~50ms ≈ 10s/turn.
  - New: 2 contested hexes × ~10 rounds ≈ 20 battle invocations ≈ ~1s/turn.
- **New regression test in scope (Phase 5):** `tests/performance/test_contested_hex_round_budget.py` — 5 contested hexes, 3 empires, 2 fleets each, 100 turns, asserts total battles ≤ 150 (today: 500+).

## Design Decisions

See [decisions.md](decisions.md) for the locked-in design choices and their rationale.

## Phase Sequencing Rationale

1. **Phase 1 (TDD scaffolding)** writes the failing tests first per CLAUDE.md TDD rule. Establishes acceptance criteria as executable specs before any production code touches.
2. **Phase 2 (fleet-merge speed-recalc fix)** lands first because the new model depends on accurate per-fleet movement intervals. Pre-existing bug; small, isolated, testable on its own.
3. **Phase 3 (multi-fleet per empire)** is independent of the trigger rewrite — it's a correctness expansion of `_resolve_combat_at_hex`. Done before Phase 4 so Phase 4's trigger logic operates on the corrected fleet-batching shape.
4. **Phase 4 (per-fleet-tick triggering)** is the core change. Lands after Phases 2-3 unblock its preconditions.
5. **Phase 5 (performance regression test)** validates the win and gates against future regressions.
6. **Phase 6 (docs)** updates `strategy_layer.md` §3 and `combat_simulation.md` §9 (closing the BUG-126 follow-up note).
