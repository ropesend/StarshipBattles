# Phase 0: Retarget / prune

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Re-grep every PROJ-480-inherited task's described pattern in the live tree before any TDD. Update phase 1-4 checklists in-place with corrected line numbers, drop NULL tasks, expand under-counted occurrences. No production-code or test edits in this phase — analysis only.

---

## Tasks

### Task 0.1: Re-grep every UI-family pending task target

- [ ] For each task in `phase_1_checklist.md`, `phase_2_checklist.md`, `phase_3_checklist.md`, `phase_4_checklist.md`, re-grep the described pattern in the target file (file paths in `manifest.md` already verified).
- [ ] Edit the task in-place if the count or line range differs from the PROJ-480 plan. PROJ-480 systematically under-counted occurrences (e.g. T4.4 plan said ~4, actual was 10; T1.23 plan said 3, actual was 4; T3.10 plan said 7, actual was 14).
- [ ] Strike-through (don't delete — preserve traceability) any task whose target pattern no longer exists in the live tree. Record reason in the task's notes line.
- [ ] Verify `tests/conftest.py` (`_make_mock_fleet`, `_assert_roundtrip_property`, `make_mock_ship_instance(has_yard=...)`) and `tests/unit/strategy/engine/conftest.py` (`make_mock_empire`, `mock_empire_factory`) helpers before any task proposes adding new ones — duplicates are out of scope.

### Task 0.2: Confirm same-file collision resolution

- [ ] Spot-check files owned by ≥2 tasks: `test_fleet_report_filters.py` (T2.16 + T3.30), `test_design_selector_window.py` (T2.19 + T3.19), `test_empire_treasury_panel.py` (T2.20 + T3.45), `test_build_queue_panel_factory.py` (T2.3 + T5.3). Decide execution order within the project (typically: T2.* extracts a fixture FIRST, then T3.* parametrize uses the fixture).
- [ ] Note the chosen order in each affected task's text. This eliminates worktree friction inside this project.

### Task 0.3: Drop or expand placeholder tasks

- [ ] Spot-check that T1.3-style "already done" tasks weren't accidentally included in this project. (T1.3 dropped at scaffold time; verify no other carry-overs have been resolved by intervening work.)
- [ ] If any task is now NULL, mark it `[~]` (struck-through) with a one-line reason and remove its action checkboxes.

### Task 0.4: Validate Phase 0 closure

- [ ] Run `python Projects/scripts/validate_phase.py PROJ-494 0`.
- [ ] Update plan.md Current State: "Phase 0 complete; phase 1-4 checklists retargeted in-place against live tree."

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
