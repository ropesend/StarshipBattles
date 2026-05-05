# Phase 4: Image generation tool + asset prep

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-314 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add the portrait-regeneration tool and prepare existing assets for schema migration.

---

## Tasks

### Task 4.1: Add regeneration CLI and prompt builder [Medium]
**Files:** `Tools/regenerate_ship_portraits/cli.py`, `Tools/regenerate_ship_portraits/prompts.py`
**Tests:** `pytest tests/unit/tools/test_regenerate_ship_portraits.py`

- [x] Add CLI for generating missing portraits with the image provider.
- [x] Add prompt construction from theme description and ship class.
- [x] Add dry-run, force, class filter, theme filter, and last-run manifest support.

**Notes:** Shipped via commit d000acc5a (PROJ-314 Phase 4). AI portrait generation deferred; user runs CLI with their `OPENAI_API_KEY`.

### Task 4.2: Add ship-theme audit script [Simple]
**File:** `Tools/regenerate_ship_portraits/audit.py`
**Tests:** `pytest tests/unit/tools/test_regenerate_ship_portraits.py`

- [x] Add schema coverage audit.
- [x] Add casing audit.
- [x] Add size audit.
- [x] Add human and JSON output modes.

**Notes:** Shipped via commit d000acc5a (PROJ-314 Phase 4).

### Task 4.3: Normalize existing asset filenames [Medium]
**Files:** `assets/ShipThemes/`
**Tests:** `python -m Tools.regenerate_ship_portraits.audit`

- [x] Convert relevant JPG portrait assets to PNG.
- [x] Normalize filenames to lowercase_with_underscores.
- [x] Fix Atlantians heavy-cruiser filename typo.
- [x] Fix Thoraliens superdreadnought path mismatch.

**Notes:** Shipped via commit d000acc5a (PROJ-314 Phase 4).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] CLI exists
- [x] Audit script exists
- [x] Asset filenames normalized for schema migration
- [x] Commit: `feat(PROJ-314 Phase 4): regenerate_ship_portraits/ tool + asset prep`
