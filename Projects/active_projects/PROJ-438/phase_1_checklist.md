# Phase 1: Canonical graph restoration path

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove duplicated graph-repair knowledge between save-load and rollback restore paths by introducing one canonical restoration path or restoration collaborator.

---

## Tasks

### Task 1.1: [Task list to be authored at phase start]
**File:** `game/strategy/engine/session/persistence_adapter.py` / `game/strategy/engine/turn_state_snapshot.py`
**Tests:** `pytest tests/unit/strategy/engine/session/test_bootstrap.py tests/unit/strategy/engine/test_restore_path_parity.py`

- [ ] Author detailed subtasks at phase start after re-reading predecessor state.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
