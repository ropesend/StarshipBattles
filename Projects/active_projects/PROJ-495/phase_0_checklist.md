# Phase 0: Retarget / prune

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Re-grep every PROJ-480-inherited task's described pattern in the live tree before any TDD. Update phase 1-4 checklists in-place with corrected line numbers, drop NULL tasks, expand under-counted occurrences. No production-code or test edits in this phase — analysis only.

---

## Tasks

### Task 0.1: Re-grep every core-mechanical pending task target

- [ ] For each task in `phase_1_checklist.md`, `phase_2_checklist.md`, `phase_3_checklist.md`, `phase_4_checklist.md`, re-grep the described pattern in the target file (file paths in `manifest.md` already verified).
- [ ] Edit the task in-place if the count or line range differs from the PROJ-480 plan.
- [ ] Strike-through (don't delete — preserve traceability) any task whose target pattern no longer exists in the live tree.
- [ ] Verify `tests/conftest.py` and `tests/unit/strategy/engine/conftest.py` helpers before any task proposes adding new ones — duplicates are out of scope.

### Task 0.2: Confirm no same-file collisions inside this project

- [ ] No same-file pairs are currently expected in PROJ-495 (Codex's collision list was UI-heavy). Verify by scanning `manifest.md` for duplicate file paths.
- [ ] If a collision is found post-scaffold, decide execution order (typically Phase 2 fixture/helper extraction → Phase 3 parametrize uses the fixture).

### Task 0.3: Confirm risky-file boundary with PROJ-496

- [ ] Verify none of the explicitly risky files (`test_turn_engine_lazy_properties.py`, `test_persistence_adapter.py`, `test_battle_engine_tick.py`, `test_colony_output.py`, `test_generation.py` atmosphere, `test_bug_regressions_2026_01.py`, `test_generator_crew_requirement_design.py`) leaked into PROJ-495's manifest. They live in PROJ-496.

### Task 0.4: Validate Phase 0 closure

- [ ] Run `python Projects/scripts/validate_phase.py PROJ-495 0`.
- [ ] Update plan.md Current State: "Phase 0 complete; phase 1-4 checklists retargeted in-place against live tree."

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
