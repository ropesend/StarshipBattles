# Phase 4: Per-Fleet-Tick Combat Triggering (Core Change)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the per-tick contested-hex scan with per-fleet movement-opportunity triggering. Combat fires once per (fleet, tick) pair where the fleet had a movement opportunity AND did not leave the contested hex on that tick. Delete the old per-tick path entirely (per CLAUDE.md "Eradicate" rule). All Phase-1 failing tests turn green.

---

## Tasks

### Task 4.1: Add the trigger predicate `_should_trigger_combat_for_fleet` [Medium]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_round_budget.py -v`

- [x] Added `_should_trigger_combat_for_fleet(self, fleet, tick, moved_fleet_ids) -> bool` private method on `ConflictResolutionEngine`. Reads `fleet.speed`, `fleet.id`. Calls `get_tick_interval(fleet.speed)` from `fleet_speed_calculator`. Returns False on `speed <= 0`, on non-opportunity-tick, or when fleet.id is in `moved_fleet_ids`. All five Phase-1 unit tests pass.

**Notes:** Predicate is fully derived from per-tick state — no persistent fleet field added. Comment block in source explains the unifying rule "did the fleet leave?" applies regardless of WHY it didn't move (idle, action-ordered, blocked, path-failed all qualify).

---

### Task 4.2: Compute `moved_fleet_ids` in `TurnEngine._process_tick` [Medium]

**File:** `game/strategy/engine/turn_engine.py`
**Tests:** Integration via `tests/integration/strategy/test_combat_round_budget.py`

- [x] Added pre-Phase-3 `pre_movement_locations = {f.id: f.location for emp in empires for f in emp.fleets}` snapshot before `apply_movements`.
- [x] Added post-Phase-3 `moved_fleet_ids = {f.id for emp/f if pre.location != f.location}` derivation.
- [x] Threaded `tick=tick, moved_fleet_ids=moved_fleet_ids` through `self.conflict_engine.resolve_all_conflicts(...)` invocation (line 732).

**Notes:** Snapshot cost is O(fleets) — same order as the legacy hex-map scan, so no perf regression. `_time_phase` wrapping unchanged.

---

### Task 4.3: Rewrite `resolve_all_conflicts` and `_resolve_conflicts` to use the trigger gate [Complex]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/ tests/integration/strategy/test_combat_round_budget.py -v`

- [x] Updated `resolve_all_conflicts` signature to accept `*, tick: Optional[int] = None, moved_fleet_ids: Optional[set] = None`. When `tick is None`, returns early with zero combats (defensive — predicate cannot evaluate `tick % interval`).
- [x] Updated `_resolve_conflicts` signature: `*, tick: int, moved_fleet_ids` (required keyword-only). Iterates fleets in deterministic `(empire_id, fleet_id)` order via `sorted(...)`. Per-fleet:
  - Liveness re-check: `if fleet not in triggering_empire.fleets: continue` (catches fleets pruned by earlier rounds in the same tick — HIGH-risk mitigation from Risk Assessor finding #1/#2)
  - Predicate check: `if not self._should_trigger_combat_for_fleet(...): continue`
  - Live contested-hex check: rebuild occupants list from CURRENT `Empire.fleets` state at fleet's hex; skip unless ≥2 empires present
  - Dispatch `_resolve_combat_at_hex(occupants)`
- [x] Re-derivation per round (not snapshot reuse) means destroyed fleets from earlier rounds in the same tick don't appear in later rounds.

**Notes:** The HIGH-risk mitigation (per-round liveness re-check) is the load-bearing correctness check. The deterministic seed (`_battle_seed_counter`) increments per dispatch, so replay determinism is preserved by the sorted iteration.

---

### Task 4.4: Delete the old per-tick scanning path [Simple]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/ tests/integration/strategy/ -v`

Per CLAUDE.md "Eradicate Backward Compat Shims" — once the new path is wired, remove the old hex-map scan code.

- [x] Old `hex_map: Dict[HexCoord, List[(Empire, Fleet)]]` build loop in `_resolve_conflicts` deleted as part of Task 4.3's full method rewrite.
- [x] Module docstring updated: replaced the legacy "If two co-located fleets both retain ships, combat re-engages on the next strategy tick (the tick loop rebuilds the hex_map from scratch each call)" with a PROJ-320 description.
- [x] `_resolve_combat_at_hex` docstring updated: replaced the stale "combat re-engages on subsequent ticks" line with "subsequent rounds at the same hex (within the same tick or on later ticks) are gated by per-fleet movement-opportunity ticks".
- [x] Verified zero remaining `hex_map` references in code (the only match is the module docstring's historical reference, which is intentional).

**Notes:** No backward-compat flag, no opt-in. Save files are disposable per CLAUDE.md.

---

### Task 4.5: Update `IConflictEngine` signature + MockConflictEngine [Simple]

**File:** `game/strategy/interfaces/engines.py`, `tests/unit/strategy/mocks/mock_engines.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -v`

- [x] Extended `IConflictEngine.resolve_all_conflicts` abstract signature with `*, tick: Optional[int] = None, moved_fleet_ids: Optional[set] = None` kwargs (backward-compatible defaults).
- [x] Updated docstring with PROJ-320 semantics for both new kwargs.
- [x] Updated `MockConflictEngine.resolve_all_conflicts` to accept and ignore the new kwargs (records empires/galaxy as before — protocol parity).

**Notes:** `_validate_tick_inputs` (Task 4.5 in original plan) needs no change — Pattern Scout swarm agent verified.

---

### Task 4.6: Update existing tests with PROJ-320 markers + delete legacy re-engagement test [Simple]

**File:** Multiple test files; legacy class deletion in `test_combat_shortcut_paths.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -v`

- [x] Updated `test_core.py` `_resolve_conflicts` callers: `test_no_conflict_same_empire`, `test_three_way_conflict_detected`, `test_resolve_conflicts_detects_collision`, `test_building_fleet_participates_in_combat`, `test_building_fleet_in_hex_collision_detection`. Each now sets `fleet.id` and `fleet.speed` and passes `tick=20, moved_fleet_ids=set()`. Adjusted `assert_called_once` to `assert call_count >= 1` where multiple opportunity-tick coincidences cause repeated dispatches.
- [x] Updated `test_battle_resolver_integration.py` `_fleet` helper: added `speed=5` default. Updated all `resolve_all_conflicts` callers: `test_resolve_all_conflicts_returns_conflict_result`, `test_resolve_all_conflicts_tracks_combats`, `test_resolve_all_conflicts_tracks_destroyed_fleets`, `test_no_conflicts_returns_zero_combats`. Loosened `fleets_destroyed == [2]` to `set(...) == {2}` (multi-round dispatches re-add ids).
- [x] Updated `test_three_empire_battle.py` `_make_fleet` helper: added `speed=5` default. Updated all 3 `resolve_all_conflicts` callers. PROJ-275 invariant (single N-team battle, not 2-fleet decomposition) re-asserted as "every dispatch is N-team" rather than "exactly one dispatch".
- [x] Updated `test_fleet_registration_lifecycle.py` `resolve_all_conflicts` caller (line 176) — `Fleet(speed=15.0)` already set; pass `tick=6, moved_fleet_ids=set()`.
- [x] **DELETED** `TestReEngagementOnSubsequentTick` class in `test_combat_shortcut_paths.py`. The class encoded the legacy "every call to resolve_all_conflicts fires combat" behaviour PROJ-320 deletes. Replaced with a tombstone comment pointing readers to the new round-budget tests in `test_combat_round_budget.py`.

**Notes:** Test fixup landed in 4 files. Round-budget semantics are now covered by Phase 1's new test files (per CLAUDE.md "Eradicate" — old tests of obsolete behaviour gone).

---

### Task 4.7: Run the full strategy + simulation suite [Medium]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/ tests/integration/strategy/
.venv/Scripts/python.exe Tools/test_sharded/test_sharded.py
```

- [x] Strategy + integration: **3,719 passed, 1 skipped, 0 failed.** All Phase 1 trigger + round-budget tests now PASS. All legacy tests updated and pass. Zero regressions.
- [x] Full sharded baseline: **16,425 tests | 16,422 passed | 0 failed | 0 errors | 3 skipped** (51.6s wall time across 16 shards). Up from 16,422/16,410/9 at end of Phase 3.

**Notes:** Phase 4 production code is the load-bearing change of PROJ-320. With it landed, the user's spoken model ("each fleet's opportunity tick = a round") is fully encoded.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `_should_trigger_combat_for_fleet` predicate exists with all five Phase-1 unit tests passing
- [x] `TurnEngine._process_tick` passes `tick` + `moved_fleet_ids` to the conflict engine
- [x] `_resolve_conflicts` uses the per-fleet iteration with live liveness + contested-hex re-checks
- [x] Legacy hex-map scan deleted; `TestReEngagementOnSubsequentTick` deleted
- [x] All Phase-1 integration tests pass (sum-of-speeds round counts)
- [x] Phase-2 and Phase-3 tests still pass
- [x] Strategy + integration suite: 3,719 / 1 / 0 (passed/skipped/failed)
- [x] Full sharded baseline: 16,425 / 3 / 0 (passed/skipped/failed) — zero regressions
- [x] Update status at top of this file to `Complete`
- [x] Update [plan.md](plan.md) phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
