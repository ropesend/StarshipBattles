# Phase 3: Cleanup and Validation Hardening

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-218 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove legacy code paths and harden validation to prevent this class of bug.

---

## Tasks

### Task 3.1: Delete `Planet.add_production()` [Simple]
**File:** `game/strategy/data/planet.py` (lines 190-203)
**Tests:** `pytest tests/integration/strategy/production/ -v`

- [ ] Delete the `add_production()` method from Planet class
- [ ] Find callers: `tests/integration/strategy/production/test_queue.py` lines 54, 64
- [ ] Update those tests to use `AddToConstructionQueueCommand` through the command handler instead
- [ ] Verify all integration tests pass

**Notes:**

### Task 3.2: Harden `ProductionEngine._validate_queue_item()` [Simple]
**File:** `game/strategy/engine/production_engine.py` (lines 336-344)
**Tests:** `pytest tests/unit/strategy/production_engine/ -v`

- [ ] Update validation to also reject empty `total_cost`:
  ```python
  if 'total_cost' not in item or not item['total_cost']:
      logger.warning(f"Queue item {design_id} has empty/missing 'total_cost' - skipping")
      return "skip"
  ```
- [ ] Add test for empty `total_cost` validation

**Notes:**

### Task 3.3: Remove Legacy Fallback in `EmpireBuildQueueWindow` [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (line 413-415)
**Tests:** `pytest tests/integration/ui/ -v`

- [ ] Evaluate the legacy fallback: `source.construction_queue.append(dict(item))`
- [ ] If all tests have session/facade injection, remove the fallback entirely
- [ ] If some tests depend on it, update those tests to provide session/facade

**Notes:**

### Task 3.4: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite with `-n 12` parallelism
- [ ] All 13,040+ tests must pass
- [ ] No new warnings introduced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
