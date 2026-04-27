# Phase 1: Backfill timestamps to 21 docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-307 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `> **Last verified:** YYYY-MM-DD` to each of the 21 doc files lacking it. Use the file's most recent meaningful commit date as the backfill baseline.

---

## Tasks

### Task 1.1: Get the per-file last-commit dates [Simple]
**File:** None — investigation step
**Tests:** None.

- [ ] For each of the 21 docs, run `git log -1 --format=%cs -- <path>` to get its most recent commit date
- [ ] Record the dates in a temporary table (can be inline in implementation notes — no formal artifact required)

**Notes:** [Filled with the 21 dates]

---

### Task 1.2: Add timestamp to top-level docs [Simple]
**File:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/04_SERVICES.md`, `docs/05_ERROR_HANDLING.md`, `docs/06_UI_STYLE_GUIDE.md` (6 files)
**Tests:** Manual grep verification

For each file:
- [ ] Read the H1 (line 1) — confirm format
- [ ] Insert blockquote line directly after H1: `> **Last verified:** <date from Task 1.1>`
- [ ] If you're confident about the doc's recent state (e.g., 02_PATTERNS.md was just updated for PROJ-297's pattern-count fix), add an optional summary: `> **Last verified:** 2026-04-26 — Pattern count corrected to 27 in PROJ-297`
- [ ] Otherwise leave summary blank (the date alone is fine for backfill)

Files:
- [ ] `docs/01_ARCHITECTURE.md`
- [ ] `docs/02_PATTERNS.md`
- [ ] `docs/03_CONVENTIONS.md`
- [ ] `docs/04_SERVICES.md`
- [ ] `docs/05_ERROR_HANDLING.md`
- [ ] `docs/06_UI_STYLE_GUIDE.md`

**Notes:**

---

### Task 1.3: Add timestamp to guide docs [Simple]
**File:** `docs/guides/*.md` (7 files)
**Tests:** Manual grep verification

- [ ] `docs/guides/adding_abilities.md`
- [ ] `docs/guides/adding_modifiers.md`
- [ ] `docs/guides/component_system.md`
- [ ] `docs/guides/modifier_system.md`
- [ ] `docs/guides/qs_complex_design.md`
- [ ] `docs/guides/simulation_testing.md`
- [ ] `docs/guides/testing_infrastructure.md`

**Notes:**

---

### Task 1.4: Add timestamp to system docs [Simple]
**File:** `docs/systems/*.md` (8 files)
**Tests:** Manual grep verification

- [ ] `docs/systems/ability_reference.md`
- [ ] `docs/systems/ai_system.md`
- [ ] `docs/systems/combat_simulation.md`
- [ ] `docs/systems/orders_system.md`
- [ ] `docs/systems/production_system.md`
- [ ] `docs/systems/research_system.md`
- [ ] `docs/systems/resource_system.md`
- [ ] `docs/systems/strategy_layer.md`

**Notes:**

---

### Task 1.5: Verification [Simple]
**File:** All of `docs/`
**Tests:** Manual grep verification

- [ ] `grep -L "Last verified" docs/*.md docs/guides/*.md docs/systems/*.md` — should return ZERO files (every doc has the marker)
- [ ] `grep -c "Last verified" docs/*.md docs/guides/*.md docs/systems/*.md` — every line should report 1 (no doc has duplicate markers)
- [ ] Spot-check 3 files visually — the blockquote should appear directly under the H1, render as a callout in markdown previewers

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `grep -L "Last verified" docs/*.md docs/guides/*.md docs/systems/*.md` returns zero files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2)
