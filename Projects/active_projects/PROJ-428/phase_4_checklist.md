# Phase 4: Extract the movement-only collaborator

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-428 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/turn_engine.py`
- `game/strategy/engine/turn_phase_registry.py`
- `game/strategy/engine/movement_phase_collaborator.py`
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
- `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`

**Objective:** Extract movement-specific snapshot/diff/minefield/pruning
work from `_capture_move_queue` and `_derive_moved_fleet_ids` into a single
`MovementPhaseCollaborator` owned by `TurnEngine`. Preserve all behavior
and the existing call contracts.

---

## Tasks

### Task 4.1: Red tests for `MovementPhaseCollaborator.snapshot_before` [Medium]
**File:** `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`

- [ ] Add a failing test that calls `snapshot_before(ctx, result)` and
      asserts both `move_queue` and `pre_movement_locations` are stored on
      the context with the existing semantics.
- [ ] Confirm the test fails because the collaborator does not yet exist.

**Notes:**

### Task 4.2: Red tests for `MovementPhaseCollaborator.resolve_after` [Complex]
**File:** `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`

- [ ] Add a failing test that confirms `resolve_after` derives
      `moved_fleet_ids` from the diff.
- [ ] Add a failing test that confirms `resolve_after` flips
      `_booster_dirty` only for empires whose fleets moved.
- [ ] Add a failing test that confirms `resolve_after` invokes
      `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)`
      for each moved fleet.
- [ ] Add a failing test that confirms emptied fleets are removed from
      the owning empire.
- [ ] Confirm all four tests fail for the intended reason.

**Notes:**

### Task 4.3: Implement `MovementPhaseCollaborator` [Complex]
**File:** `game/strategy/engine/movement_phase_collaborator.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`

- [ ] Create the new module with public methods
      `snapshot_before(ctx, result)` and `resolve_after(engine, ctx)`.
- [ ] Add private split: `_diff_moved_fleets`,
      `_mark_boosters_dirty`, `_resolve_minefields`,
      `_prune_destroyed_fleet_contents`.
- [ ] Keep the broad-except around minefield resolution exactly intact
      (same exception class, same swallowed scope).
- [ ] Preserve `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)`
      call contract byte-for-byte.
- [ ] Verify all Task 4.1 / 4.2 red tests now pass.

**Notes:**

### Task 4.4: Wire `TurnEngine` to own and dispatch the collaborator [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`

- [ ] Construct or lazily create the collaborator on `TurnEngine`.
- [ ] Expose two thin engine entry points (or pass the collaborator
      directly) for the `movement_calc` and `movement_apply` hooks.
- [ ] Confirm the Phase 1 characterization suite is still green.

**Notes:**

### Task 4.5: Repoint registry hooks and delete the old helpers [Medium]
**File:** `game/strategy/engine/turn_phase_registry.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [ ] Repoint the `movement_calc` hook at the new collaborator path.
- [ ] Repoint the `movement_apply` hook at the new collaborator path.
- [ ] Delete `_capture_move_queue` from `turn_phase_registry.py`.
- [ ] Delete `_derive_moved_fleet_ids` from `turn_phase_registry.py`.
- [ ] Remove any `MinefieldResolver` import from `turn_phase_registry.py`.
- [ ] Verify focused turn-engine suite is green.

**Notes:**

### Task 4.6: FMS-B regression gate [Medium]
**File:** `tests/integration/test_fms_b_e2e.py`, `tests/integration/test_fms_b_statistical_balance.py`
**Tests:** `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_b_statistical_balance.py -x`

- [ ] Run both FMS-B integration tests; confirm green.
- [ ] If statistical balance fluctuates within its existing tolerance
      band, document the run in `findings/` (do not loosen tolerances).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/turn_engine/ -x` is green
- [ ] `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_b_statistical_balance.py -x` is green
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
