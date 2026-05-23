# Phase 0: Retarget / prune

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-496 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Re-grep every PROJ-480-inherited task's described pattern in the live tree before any TDD. Update phase 1-2 checklists in-place with corrected line numbers, drop NULL tasks, expand under-counted occurrences. No production-code or test edits in this phase — analysis only.

---

## Tasks

### Task 0.1: Re-grep every risky/integration pending task target

- [ ] For each task in `phase_1_checklist.md` and `phase_2_checklist.md`, re-grep the described pattern in the target file.
- [ ] Edit the task in-place if the count or line range differs from the PROJ-480 plan.
- [ ] Strike-through (don't delete) any task whose target pattern no longer exists.

### Task 0.2: Confirm T5.14 re-pending evidence is still valid

- [ ] Re-read `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:219-288` and confirm both `inspect.getsource(...)` guard and AST-parsing guard are still present (PROJ-480 audit_verification.md F1 evidence as of 2026-05-23).
- [ ] If PROJ-479's Task 3.21 (NEEDS_REWORK) has since landed, mark T5.14 in Phase 1 as resolved and update the task notes accordingly.

### Task 0.3: Confirm same-file collision plan for turn_engine_lazy_properties

- [ ] Phase 1 owns BOTH PROJ-480 T3.29 (parametrize 18 isinstance) and T5.14 (guard split) for `test_turn_engine_lazy_properties.py`. Confirm Phase 1 sequencing: T3.29 → T5.14.

### Task 0.4: Confirm risky-file boundary with PROJ-494/PROJ-495

- [ ] Verify none of PROJ-496's files (per `manifest.md`) appear in PROJ-494/495 manifests. Spot-check by reading the three manifest.md files.

### Task 0.5: Validate Phase 0 closure

- [ ] Run `python Projects/scripts/validate_phase.py PROJ-496 0`.
- [ ] Update plan.md Current State.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
