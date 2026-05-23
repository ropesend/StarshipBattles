# Phase 4: Doc update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Document the new reason API + save-restore log behavior.

**Precondition:** Phases 1-3 complete.

---

## Tasks

### Task 4.1: Update `docs/04_SERVICES.md` ModifierService section [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** N/A

- [ ] Add `check_allowance()` to the public API surface listing
- [ ] Note that `is_modifier_allowed()` is a bool-returning convenience wrapper
- [ ] If PROJ-489 Phase 2 already cleaned stale ModifierLogicService text at lines ~269-273, confirm; otherwise still address
- [ ] Verify code/docs consistency (CLAUDE.md)

**Notes:** [Filled during implementation]

### Task 4.2: Update `docs/05_ERROR_HANDLING.md` save-restore section [Simple]
**File:** `docs/05_ERROR_HANDLING.md`
**Tests:** N/A

- [ ] Add a brief note that battle/ship save-restore emits `logger.warning` on allow_abilities rejection, including modifier id + component id + reason
- [ ] Cross-link to `ModifierService.check_allowance()`

**Notes:** [Filled during implementation]

### Task 4.3: Update `docs/guides/modifier_system.md` rejection behavior [Simple]
**File:** `docs/guides/modifier_system.md`
**Tests:** N/A

- [ ] Confirm PROJ-489 Phase 2 corrected the "only type restrictions" text at lines 98, 285
- [ ] Add a one-paragraph "Diagnosing rejections" section pointing at the save-restore log warning and `check_allowance()` reasons

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Docs match code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Awaiting audit"
