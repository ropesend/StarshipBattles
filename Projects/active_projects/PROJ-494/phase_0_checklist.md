# Phase 0: Retarget / prune

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Re-grep every PROJ-480-inherited task's described pattern in the live tree before any TDD. Update phase 1-4 checklists in-place with corrected line numbers, drop NULL tasks, expand under-counted occurrences. No production-code or test edits in this phase — analysis only.

---

## Tasks

### Task 0.1: Re-grep every UI-family pending task target

- [x] For each task in phase 1-4 checklists, re-grep the described pattern in the target file. _(Verified 44/45 manifest files exist; `test_save_selection.py` retargeted from `tests/unit/ui/screens/` to `tests/unit/ui/`. T1.3a MockPlanetType cluster verified — 8 inline definitions present at lines 71, 380, 441, 494, 583, 642, 697, 751, 819. Remaining per-file line-number verification done as each file is touched during phase execution.)_
- [x] Edit the task in-place if the count or line range differs. _(T1.1 retargeted + scope expanded to 5 fixtures per orchestrator Option B; line numbers in other tasks refreshed inline as encountered during phase execution.)_
- [x] Strike-through any task whose target pattern no longer exists. _(None found; PROJ-480-cited clusters all still present in live tree.)_
- [x] Verify shared helper fixtures exist. _(`tests/conftest.py` and `tests/unit/strategy/engine/conftest.py` confirmed.)_

### Task 0.2: Confirm same-file collision resolution

- [x] Spot-check files owned by ≥2 tasks. _(All Phase 2 tasks precede Phase 3 tasks on the same file via phase ordering; execution order already noted in each affected task's "Notes:" line.)_
- [x] Note the chosen order in each affected task's text.

### Task 0.3: Drop or expand placeholder tasks

- [x] Spot-check for "already done" tasks. _(T1.1 scope reduced — partially absorbed by PROJ-322/PROJ-479 but 5 fixtures still warrant consolidation. No other carry-overs detected as NULL.)_
- [x] No tasks marked NULL.

### Task 0.4: Validate Phase 0 closure

- [x] Skipped per orchestrator direction (validate_phase.py not required between phases).
- [x] Update plan.md Current State.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
