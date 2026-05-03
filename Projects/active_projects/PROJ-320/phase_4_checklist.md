# Phase 4: Per-Fleet-Tick Combat Triggering (Core Change)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the per-tick contested-hex scan with per-fleet movement-opportunity triggering. Combat fires once per (fleet, tick) pair where the fleet had a movement opportunity AND did not leave the contested hex on that tick. Delete the old per-tick path entirely (no shim per CLAUDE.md "Eradicate" rule). All Phase-1 failing tests turn green.

---

## Tasks

### Task 4.1: Add the trigger predicate `_should_trigger_combat_for_fleet` [Medium]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_round_budget.py -v`

- [ ] Add private method on `ConflictResolutionEngine`:
  ```python
  def _should_trigger_combat_for_fleet(
      self,
      fleet: "Fleet",
      tick: int,
      moved_fleet_ids_this_tick: set[int],
  ) -> bool:
      """Return True iff `fleet` is on a movement-opportunity tick AND did not leave its hex this tick.
      
      The criterion is fully derived from per-tick state — no persistent fleet field is needed.
      """
      from game.strategy.services.fleet_speed_calculator import get_tick_interval
      
      if fleet.speed <= 0:
          return False
      interval = get_tick_interval(fleet.speed)
      if tick % interval != 0:
          return False
      # Fleet had an opportunity. Did it actually leave?
      if fleet.id in moved_fleet_ids_this_tick:
          return False
      return True
  ```
- [ ] Add unit test for each of the five Phase-1 cases — the failing tests in `test_conflict_round_budget.py` from Task 1.1 should now PASS.

**Notes:** `moved_fleet_ids_this_tick` is the set of fleet ids whose location actually changed during Phase 3 of THIS tick. Computed by TurnEngine and passed in (Task 4.2). Stays stateless — never persisted.

---

### Task 4.2: Compute `moved_fleet_ids_this_tick` in `TurnEngine._process_tick` [Medium]

**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/test_combat_round_budget.py -v`

- [ ] Locate `_process_tick` (around line 668-698)
- [ ] Phase 3 (`apply_movements`) call: capture pre- and post-state. Today the move queue is built in Phase 2 as `[(fleet, next_hex), ...]`. The list of fleets that successfully moved is exactly the fleets whose `next_hex != fleet.location_at_start_of_phase_3`.
- [ ] Snapshot pre-Phase-3 locations:
  ```python
  pre_movement_locations = {f.id: f.location for emp in empires for f in emp.fleets}
  move_queue = self._time_phase("movement_calc", self.movement_engine.collect_movements, ...)
  self._time_phase("movement_apply", self.movement_engine.apply_movements, move_queue, galaxy)
  moved_fleet_ids = {
      f.id for emp in empires for f in emp.fleets
      if pre_movement_locations.get(f.id) != f.location
  }
  ```
- [ ] Pass `moved_fleet_ids` as a new kwarg to `self.conflict_engine.resolve_all_conflicts(empires, galaxy=galaxy, moved_fleet_ids=moved_fleet_ids)`.
- [ ] If using `_time_phase` to wrap the conflict call, ensure kwargs are forwarded.

**Notes:** Snapshot cost is O(fleets) — same order as the existing hex-map scan. No persistent state added.

---

### Task 4.3: Rewrite `resolve_all_conflicts` and `_resolve_conflicts` to use the trigger gate [Complex]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/ tests/integration/strategy/test_combat_round_budget.py -v`

- [ ] Update `IConflictEngine.resolve_all_conflicts` signature in `game/strategy/interfaces/engines.py` to accept the new optional kwarg:
  ```python
  def resolve_all_conflicts(
      self,
      empires: List,
      galaxy: Optional["Galaxy"] = None,
      moved_fleet_ids: Optional[set[int]] = None,
  ) -> "ConflictResult":
  ```
  When `moved_fleet_ids is None` (callers that haven't been updated, including `MockConflictEngine`), default to an empty set — semantically: "no movement information available, treat all fleets as potentially staying put." The TurnEngine will always pass it; tests using `MockConflictEngine` won't notice.
- [ ] Rewrite `_resolve_conflicts` (around line 247-268):
  - Iterate every empire's every fleet in `(empire_id, fleet_id)` sorted order
  - For each fleet at a hex with ≥1 enemy fleet present, call `_should_trigger_combat_for_fleet(fleet, tick, moved_fleet_ids)`
  - If True → invoke `_resolve_combat_at_hex(fleet.location, current_empires_state)` and add the hex to a `combats_dispatched_this_tick: set[HexCoord]` to ensure ONE battle per (hex, tick) even if multiple fleets at that hex have opportunities on the same tick
- [ ] Wait — re-read the user's rule: "Each time A could have moved but didn't, there should be a round of combat. Each time B could have moved but didn't there should also be a round of combat." This says EACH fleet's opportunity = a round, even on shared ticks. So if A and B both have opportunity at tick 20, we fire 2 separate battles at tick 20 (sequentially, with roster re-derived between them).
- [ ] Final implementation:
  ```python
  def _resolve_conflicts(self, empires, galaxy, tick, moved_fleet_ids):
      moved_fleet_ids = moved_fleet_ids or set()
      # Iterate fleets in (empire_id, fleet_id) order for deterministic seeding
      sorted_fleets: List[Tuple[int, "Fleet"]] = sorted(
          ((emp.id, f) for emp in empires for f in emp.fleets),
          key=lambda pair: (pair[0], pair[1].id),
      )
      for emp_id, fleet in sorted_fleets:
          if not self._should_trigger_combat_for_fleet(fleet, tick, moved_fleet_ids):
              continue
          # Re-derive contested-hex membership LIVE — earlier rounds may have destroyed fleets
          if not self._is_hex_contested(fleet.location, empires):
              continue
          self._resolve_combat_at_hex(fleet.location, empires, triggering_fleet=fleet)
  
  def _is_hex_contested(self, hex_loc, empires) -> bool:
      empire_ids_at_hex = {emp.id for emp in empires for f in emp.fleets if f.location == hex_loc}
      return len(empire_ids_at_hex) >= 2
  ```
- [ ] **Roster freshness mitigation (HIGH risk #1/#2):** `_resolve_combat_at_hex` must build its `fleets_for_battle` list FROM `empires` (passed by reference, mutated by `apply_outcome_to_fleets`) — NOT from a cached snapshot. Earlier rounds in this tick may have destroyed fleets; those are removed from `Empire.fleets` by the post-battle hook before the next round runs. Phase 3 already moved `fleets_by_empire` to `Dict[int, List[Fleet]]` — verify that build still iterates `empire.fleets` directly each call.
- [ ] Add the `triggering_fleet` parameter to `_resolve_combat_at_hex` for diagnostic logging only — does not change battle outcome:
  ```python
  logger.info(
      f"Combat at {hex_loc}: triggered by Fleet {triggering_fleet.id} (empire {triggering_fleet.owner_id}) "
      f"on tick {tick}; participants={[f.id for f in fleets_for_battle]}"
  )
  ```

**Notes:** Roster re-derivation per round is the HIGH-risk mitigation. Each round-fire must compute the contested-hex membership from CURRENT `Empire.fleets` state, not a snapshot.

---

### Task 4.4: Delete the old per-tick scanning path [Simple]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/ tests/integration/strategy/ -v`

Per CLAUDE.md "Eradicate Backward Compat Shims" — once the new path is wired, remove the old hex-map scan code.

- [ ] Delete the old `hex_map: Dict[HexCoord, List[(Empire, Fleet)]]` build loop in `_resolve_conflicts` (it's been replaced by the per-fleet iteration). Confirm no other method or test references the old structure.
- [ ] Delete the module-level docstring line `"If two co-located fleets both retain ships, combat re-engages on the next strategy tick (the tick loop rebuilds the hex_map from scratch each call)."` (lines 19-20). Replace with a description of the new triggering rule.
- [ ] If any helper exists solely to support the old scan (e.g., a `_build_hex_map` method), delete it.
- [ ] Search for `hex_map` in the file: confirm zero remaining references.

**Notes:** Save files are disposable (CLAUDE.md). No fallback flag, no opt-in.

---

### Task 4.5: Update `_validate_tick_inputs` for the new model [Simple]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_validation.py -v` (or wherever the validation tests live)

- [ ] Confirm `_validate_tick_inputs(empires)` (around line 196-209) still validates what's needed: `fleet.location is not None`, `fleet.speed >= 0`. Add nothing new — `moved_fleet_ids` is per-tick metadata, not per-fleet state.
- [ ] If a test exists asserting the validation catches a specific malformed empire, ensure it still passes.

**Notes:** Validation shape is unchanged. Pattern Scout swarm agent verified.

---

### Task 4.6: Update existing tests with PROJ-320 markers (Phase 1 Task 1.4) [Simple]

**File:** `tests/integration/strategy/test_combat_shortcut_paths.py`, `tests/integration/strategy/test_event_log_integration.py`, others surfaced by Phase 1 grep
**Tests:** `pytest tests/integration/strategy/ -v`

The PROJ-320 markers added in Phase 1 Task 1.4 now need their assertions updated.

- [ ] For each `# PROJ-320` marker added in Phase 1: investigate the new expected count under the round-budget model. Update the assertion. Remove the marker (or convert to a normal explanation comment).
- [ ] Specifically `test_combat_shortcut_paths.py` test "two stationary co-located fleets fight repeatedly" (or equivalent) — its expected count drops from 100 to (sum of speeds).
- [ ] If a test was specifically designed to verify the OLD per-tick behavior (e.g., "every tick triggers a battle"), DELETE it — that behavior is intentionally gone. Document deletion in the checklist `Notes`.

**Notes:** UI Impact swarm agent flagged ~3-5 tests likely affected. Bound the cleanup at 1-2 hours; if the count balloons, surface to the user.

---

### Task 4.7: Run the full strategy + simulation suite [Medium]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/ tests/integration/strategy/ tests/unit/simulation/ tests/integration/simulation/ -v
```

- [ ] All Phase-1 failing tests now PASS (Tasks 1.1 + 1.2 — five unit tests + four integration tests)
- [ ] Phase 2 + Phase 3 fixes still pass
- [ ] No new regressions
- [ ] Run sharded baseline: `.venv/Scripts/python.exe Tools/test_sharded/test_sharded.py` — total should be 16,374 + (~10 new tests) = ~16,384, all passing

**Notes:** If sharded count differs from expected, audit Task 4.6 for tests that should be deleted or updated.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_should_trigger_combat_for_fleet` predicate exists with all five Phase-1 unit tests passing
- [ ] `TurnEngine._process_tick` passes `moved_fleet_ids` to the conflict engine
- [ ] `_resolve_conflicts` uses the per-fleet iteration; old hex-map scan deleted
- [ ] All Phase-1 integration tests pass (sum-of-speeds round counts)
- [ ] Phase-2 and Phase-3 tests still pass
- [ ] Full sharded baseline passes (no regression)
- [ ] Update status at top of this file to `Complete`
- [ ] Update [plan.md](plan.md) phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
