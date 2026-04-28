# Phase 3: Documentation + closeout

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-315 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update `docs/06_UI_STYLE_GUIDE.md` with the new
read-only-component-grouping pattern. Project closeout: Work Log,
projects_index.md, Tracking dashboards.

---

## Tasks

### Task 3.1: Document the read-only-component-grouping pattern [Simple]
**File:** `docs/06_UI_STYLE_GUIDE.md`
**Tests:** Manual review.

- [x] Add a new section "Read-only component grouping (PROJ-315)"
  documenting:
  - When to use: any panel that displays per-component damage state
    in a read-only context (Fleet Report, future Battle After-Action
    Report, etc.).
  - The colour-tier rules (table from `design.md` §"Visual rendering
    rules").
  - The strikethrough convention (manual `pygame.draw.line()`
    overlay; pattern from `test_lab/dialogs.py`).
  - The auto-expand semantics (per-selection re-fire, no manual
    collapse persistence).
  - The module-level pure-function colocation precedent
    (`group_components_by_id` colocated with the panel class —
    matches `planet_report_panel.py`).
- [x] Update `Last verified:` blockquote at the top of the file:
  `> **Last verified:** YYYY-MM-DD — Added read-only component
  grouping pattern (PROJ-315).`
- [x] (Optional) If `docs/02_PATTERNS.md` already covers the
  module-level-pure-function colocation pattern, add a one-line
  cross-reference. If not, do NOT introduce a new pattern entry —
  one-off documentation in 06_UI_STYLE_GUIDE.md is sufficient.

**Notes:**

---

### Task 3.2: Project closeout [Simple]
**File:** `Projects/active_projects/PROJ-315/plan.md`, `Projects/projects_index.md`
**Tests:** None.

- [x] Update `plan.md` Current State:
  `**Active Phase:** Complete — ready for user verification`.
- [x] Update `plan.md` Audit Log if any audit cycles were performed.
- [x] Append a Work Log entry to `plan.md` summarising the change
  set: files touched, test count delta, baseline (15893 → final).
- [x] Update `Projects/projects_index.md` if PROJ-315 needs a status
  flip (the create script already added the entry; just bump status
  to "Awaiting User Verification" or similar).
- [x] Confirm the triage findings doc at
  `findings/fleet_report_component_damage_view.md` survives
  unchanged (it's the historical record).

**Notes:**

---

### Task 3.3: Final sharded run + manual verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Final full-suite run. Confirm: pre-Phase-1 baseline 15893 +
  Phase 1 (10–13) + Phase 2 (12–15) = ~15915–15921 passed, 0 failed.
  Document the exact post-PROJ-315 baseline in the work log.
- [x] Manual end-to-end verification per the checklist in
  `plan.md` §"Final Verification":
  - Healthy ship → all collapsed, neutral colour.
  - Damaged ship → correct group rows, layer auto-expand.
  - Destroyed component → red + strike, HP_DESTROYED grey.
  - Manual disable → MUTED_GREY, no strike.
  - Save/load round-trip preserves state.
- [x] Notify the user that PROJ-315 is ready for verification.

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to "Project Complete".
- [x] Run `python Projects/scripts/validate_phase.py PROJ-315 3`.
