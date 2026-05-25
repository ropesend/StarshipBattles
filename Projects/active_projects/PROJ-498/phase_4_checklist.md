# Phase 4: Doc update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Document the new reason API + save-restore log behavior.

**Precondition:** Phases 1-3 complete.

---

## Tasks

### Task 4.1: Update `docs/04_SERVICES.md` ModifierService section [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** N/A

- [x] Add `check_allowance()` to the public API surface listing
- [x] Note that `is_modifier_allowed()` is a bool-returning convenience wrapper
- [x] If PROJ-489 Phase 2 already cleaned stale ModifierLogicService text at lines ~269-273, confirm; otherwise still address
- [x] Verify code/docs consistency (CLAUDE.md)

**Notes:** Expanded the Modifiers subsection of `04_SERVICES.md` with a full `check_allowance()` API listing, the locked reason set (no `ABILITY_DENIED`), and a pointer to `05_ERROR_HANDLING.md` for the save-restore log behavior. The PROJ-489 ModifierLogicService text at the old line range is still accurate and was left intact.

### Task 4.2: Update `docs/05_ERROR_HANDLING.md` save-restore section [Simple]
**File:** `docs/05_ERROR_HANDLING.md`
**Tests:** N/A

- [x] Add a brief note that battle/ship save-restore emits `logger.warning` on allow_abilities rejection, including modifier id + component id + reason
- [x] Cross-link to `ModifierService.check_allowance()`

**Notes:** Added a new "Save-Restore Modifier Rejection (PROJ-498)" subsection between the JSON/Persistence block and "Turn Engine Boundary". It cites both call sites, gives verbatim message forms, and points at `docs/04_SERVICES.md` for the API surface.

### Task 4.3: Update `docs/guides/modifier_system.md` rejection behavior [Simple]
**File:** `docs/guides/modifier_system.md`
**Tests:** N/A

- [x] Confirm PROJ-489 Phase 2 corrected the "only type restrictions" text at lines 98, 285
- [x] Add a one-paragraph "Diagnosing rejections" section pointing at the save-restore log warning and `check_allowance()` reasons

**Notes:** Verified: line 98 ("Restrictions caveat...") and line 290 in the "Important current behavior" list already correctly state that `deny_abilities`/`require_mode` are NOT enforced, per PROJ-489 Phase 2. Added `check_allowance()` + reason enum entries to the Surface listing (line ~273) and a new "Diagnosing rejections" paragraph cross-linking the save-restore warning + `check_allowance()`.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Docs match code
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Awaiting audit"
