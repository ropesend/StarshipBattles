# PROJ-320 — Pattern Scout Findings

## 1. Per-Fleet-Per-Tick Iteration Patterns

`FleetMovementEngine.collect_movements()` (`fleet_movement_engine.py:209-270`) already implements the exact pattern needed: iterates all empires → all fleets, checks `tick % interval == 0`, and conditionally queues fleets for processing. The new combat trigger should mirror this iteration structure.

**Recommendation:** Could either reuse the iteration loop (couple combat trigger into Phase 2) OR run a parallel scan in Phase 4. The latter is cleaner because it lets Phase 4 use post-Phase-3 fleet locations to determine "did this fleet leave the hex this tick?"

## 2. Sub-Engine Extension vs. Modification

- `TurnEngineConfig` (`turn_engine_config.py:1-54`) already bundles 15 engine dependencies with `None`-default lazily-initialized fields.
- `IConflictEngine` protocol (`interfaces/engines.py:233-264`) defines the public contract; `ConflictResolutionEngine` (`conflict_resolution_engine.py:48-426`) implements it.
- `_validate_tick_inputs` precondition pattern in place (`conflict_resolution_engine.py:196-209`; `action_execution_engine.py:70-79`).
- `_time_phase` instrumentation (`turn_engine.py:238-283`) provides error context and timing.

**Recommendation:** **Modify existing `ConflictResolutionEngine`**, not a new sub-engine. (Note: ignore the agent's "fall back to current behavior for backward compatibility" suggestion — violates project's eradicate-shims rule.)

## 3. Event-Driven Pattern for Fleet Just-Moved

No existing "post-movement callback / hook" fires between `apply_movements()` (`fleet_movement_engine.py:339-360`) and `resolve_all_conflicts()` (`turn_engine.py:698`). The tick-loop runs phases sequentially with no inter-phase event system.

**Recommendation:** **Consult post-movement state directly**. After Phase 3 completes, fleets have updated `location` attributes. Snapshot pre-Phase-3 locations, then compute `moved_fleet_ids` after Phase 3 by comparing.

## 4. Encounter/Engagement State Pattern

No registry tracks "ongoing engagements" between ticks. `ConflictResolutionEngine._resolve_conflicts()` (`conflict_resolution_engine.py:247-267`) rebuilds `hex_map` from scratch every tick. Stateless and deterministic.

**Recommendation:** **Stay stateless**. Don't add an "active encounter" registry.

## 5. Tick-Interval Consumption & Caching

`get_tick_interval(speed)` is defined at `fleet_speed_calculator.py:39-58` and currently called only by `FleetMovementEngine.collect_movements()`. Pure function: `max(1, int(100 // speed))`.

**Recommendation:** No caching needed. Call cost is negligible (~1000 calls per turn at typical fleet count). Only cache if profiling shows a bottleneck.

## 6. Iteration Order Determinism

`ConflictResolutionEngine._resolve_combat_at_hex()` sorts empires by ID at `conflict_resolution_engine.py:305`: `empire_order: List[int] = sorted(fleets_by_empire.keys())`. This ensures deterministic battle seeding via `_battle_seed_counter`.

**Recommendation:** Iterate fleets in `(empire_id, fleet_id)` tuple order when scheduling PROJ-320 triggers. Sort by empire ID first, then fleet ID within each empire.

## 7. Round-Result Aggregation

`ConflictResolutionEngine._log_combat_result()` (`conflict_resolution_engine.py:107-194`) emits **one event per battle**, not per round.

**Recommendation:** **One event per trigger**. The existing event structure already handles multi-fleet payloads.

## 8. Naming Convention

**Recommendation:** Call the new predicate **`_should_trigger_combat_for_fleet(fleet, tick) -> bool`**. Mirrors the imperative "should/is" style of action predicates.

## 9. Anti-Patterns to Avoid

1. **Singleton anti-pattern** — Don't add a new singleton for "active encounters."
2. **Backward-compat shim for old per-tick combat** — Once PROJ-320 is live, delete the old full-scan path entirely. No fallback, no feature flag. Confirmed by CLAUDE.md.
3. **Magic numbers** — `BASE_TICKS_PER_MOVEMENT = 100` (`fleet_speed_calculator.py:36`) is a const. Reuse it.
4. **Broad `except Exception`** — Any broad catch in PROJ-320 must explain why.
5. **Public methods without return types** — Confirmed critical by CLAUDE.md; all public engine methods have return-type annotations. The new `_should_trigger_combat_for_fleet()` must annotate `-> bool`.

## Recommended Placement

**Verdict: Modify existing `ConflictResolutionEngine`, not a new sub-engine.**

1. **Phase 3 snapshot:** In `TurnEngine._process_tick`, after `apply_movements()` completes, populate `moved_fleet_ids` set.
2. **Phase 4 gate:** Pass this set to `resolve_all_conflicts(empires, galaxy, moved_fleet_ids)`. Inside, iterate fleets and call `_should_trigger_combat_for_fleet`.
3. **Why:** (a) Zero new engine/DI churn. (b) Keeps spatial collision logic in one place. (c) Deterministic iteration order already present. (d) Reuses existing precondition validation and error handling. (e) Minimal test surface.

**Cost:** ~15 lines to `ConflictResolutionEngine`, ~5 lines to `TurnEngine`. No new files, no new sub-engines, no new registries.
