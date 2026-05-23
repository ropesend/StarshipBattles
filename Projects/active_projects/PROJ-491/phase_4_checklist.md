# Phase 4: Task 3.20 second bullet investigation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-491 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Determine whether PROJ-479 Phase 3 Task 3.20 second bullet (`_per_player_ui_state.load(...)` private-attr access at lines 1189-1231) is a real production seam gap or just test-side coupling that can be fixed with the existing public API.

**Background:** PROJ-479 deferred this with the assumption that a "public state-restore API" needs to be introduced. Codex consult flagged this as [unverified] — neither agent has read the production class. This phase resolves the question before committing to either PROJ-491 or PROJ-493 work.

---

## Tasks

### Task 4.1: Identify the production class
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py` (lines 1189-1231)
**Tests:** none — read-only

- [ ] Open `tests/unit/ui/screens/test_strategy_game_state_manager.py` at lines 1189-1231.
- [ ] Identify the import path of the class whose `_per_player_ui_state` is accessed.
- [ ] Read the production class definition.

### Task 4.2: Check for existing public restore API
**File:** the production class identified in Task 4.1
**Tests:** none — read-only

- [ ] Search for methods named `restore`, `load`, `apply_per_player_state`, `set_player_state`, etc.
- [ ] Check the docstring / public-API contract section of the class.
- [ ] Determine: does a public method exist that performs the same operation as `_per_player_ui_state.load(...)`?

### Task 4.3: Decision and routing
**File:** `plan.md` + `decisions.md`
**Tests:** none

- [ ] **If public API exists:** keep task in PROJ-491. Add a new task to Phase 1 (Task 1.20: rewrite test_strategy_game_state_manager.py lines 1189-1231 to use the public API). Document in `decisions.md`.
- [ ] **If no public API exists:** move task to PROJ-493. Add a new phase or task to PROJ-493 describing the production seam (`def restore_per_player_state(self, ...)`). Document the routing decision in BOTH this project's `decisions.md` AND PROJ-493's `decisions.md`.
- [ ] In either case, update `plan.md` Current State with the decision and the new task location.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Decision recorded in `decisions.md`
- [ ] Task routed to PROJ-491 Phase 1 OR moved to PROJ-493 with cross-references
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State

_Source: PROJ-479 Phase 3 Task 3.20 second bullet. See [findings/source_review.md](findings/source_review.md)._
