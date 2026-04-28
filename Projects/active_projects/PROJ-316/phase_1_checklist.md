# Phase 1: Paperwork sweep — checklists + docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-316 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make PROJ-313 audit-ready and bring docs into agreement
with code. Closes audit findings P1.1 (audit-readiness) and P2.5 (doc
accuracy), plus the documentation half of P1.2 (Phase 8 deviation).
No production code changes in this phase.

---

## Tasks

### Task 1.1: Update PROJ-313 phase checklists to reflect actual state [Simple]
**File:** `Projects/active_projects/PROJ-313/phase_1_checklist.md` … `phase_8_checklist.md`
**Tests:** `python Projects/scripts/validate_audit_ready.py PROJ-313`

- [ ] Phase 1 checklist: change `**Status:** Not Started` → `**Status:** Complete`. Walk task list, check off `[ ]` → `[x]` for each task that was done in PROJ-313.
- [ ] Phase 2 checklist: same pattern.
- [ ] Phase 3 checklist: same pattern.
- [ ] Phase 4 checklist: same pattern.
- [ ] Phase 5 checklist: same pattern.
- [ ] Phase 6 checklist: same pattern.
- [ ] Phase 7 checklist: same. Add a note that the click-blocking test was inadequate and is being replaced in PROJ-316 Phase 3.
- [ ] Phase 8 checklist: leave the demolition tasks unchecked. Add `**Deferred:**` notes to each, and add a "Scope Deviation" section at the bottom of the file pointing to `Projects/active_projects/PROJ-313/plan.md` Current State paragraph.

**Notes:** Don't fabricate task completions — only check boxes that genuinely correspond to completed work.

---

### Task 1.2: Update PROJ-313 plan.md Goals section [Simple]
**File:** `Projects/active_projects/PROJ-313/plan.md`
**Tests:** N/A (text-only)

- [ ] Find the Goals section.
- [ ] For "Delete `_handle_window_close`" goal — append `[deferred — see Current State scope deviation]`.
- [ ] For "Replace the false-negative-prone `TestModalSlotCleanupContract` test" goal — append `[partially deferred — new structural test added at tests/unit/ui/screens/test_strategy_modal_window.py; legacy test retained as regression for the still-active slot-cleanup pathway]`.
- [ ] Bump `Last verified:` blockquote on plan.md.

**Notes:**

---

### Task 1.3: Fix `docs/02_PATTERNS.md` Pattern #31 accuracy [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual re-read; cross-reference every claim against code.

- [ ] Adopter count line: change "21 windows" → "20 windows". Verify by counting names listed in the line — should be 20.
- [ ] "Both methods are one-liners" sentence: replace with `"Both methods walk iter_live_modals() for modal-tracking; has_modal_open() additionally checks menu_panel and build_queue_screen (pre-modal-tracking concerns retained from before PROJ-313)."`
- [ ] "Replaces the source-string-matching test" sentence: replace with `"Augments the legacy TestModalSlotCleanupContract (kept as a regression for the slot-cleanup pathway that still operates for caller-convenience pointers — see Migration notes). The new structural invariant test is at tests/unit/ui/screens/test_strategy_modal_window.py."`
- [ ] Bump `Last verified:` blockquote at the top of `docs/02_PATTERNS.md`.

**Notes:** Do not change the substance of Pattern #31 — only correct the inaccurate factual claims.

---

### Task 1.4: Pattern #30 SUPERSEDED banner clarification [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual re-read.

- [ ] Read the existing SUPERSEDED banner on Pattern #30.
- [ ] Confirm or amend so it says explicitly: the `on_close_callback` registrar mechanism is **still active** for slot-cleanup of caller-convenience pointers (see Migration notes section at the end of Pattern #31). What was superseded is the use of these slots as the modal-tracking contract — modal tracking is now structural via Pattern #31.

**Notes:**

---

### Task 1.5: Re-run audit script until green [Simple]
**Command:** `python Projects/scripts/validate_audit_ready.py PROJ-313`

- [ ] Run the script. Capture the output.
- [ ] List each error. Most should be resolved by Task 1.1.
- [ ] Address each remaining error. Iterate.
- [ ] Acceptance: exit code 0 (no errors). Warnings tolerable but document any in `decisions.md`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-313` exits 0
- [ ] `pytest tests/unit/ui/screens/` no regression
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2)
