# Phase 2: Per-resource grid expansion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-289 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rewrite the resource grid on the planet report panel from the current stockpile (current/max) layout to a 4-column projection grid (Harvest / Upkeep / Yard / Net). Retain the stockpile summary as a compact row below the grid.

---

## Tasks

### Task 2.1: Write failing tests for 4-column grid [Medium]
**File:** `tests/unit/ui/panels/test_planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py::TestResourceGrid4Column`

- [ ] Test: grid has header row with 5 cells (Resource label + 4 column headers).
- [ ] Test: grid has one data row per resource in `view.resource_projections`.
- [ ] Test: harvest cell uses `format_signed_float(proj.harvest, 1)`.
- [ ] Test: upkeep cell is `-proj.upkeep` (negative sign because it's a drain).
- [ ] Test: yard cell is `-proj.yard` (same reasoning).
- [ ] Test: net cell is `proj.net` (already signed).
- [ ] Test: net cell color is green when net > 0, red when < 0, default when 0.
- [ ] Test: non-food resource (no upkeep) shows "0.0" in upkeep column.
- [ ] Test: view=None fallback renders the legacy stockpile grid.

**Notes:**

### Task 2.2: Rewrite `_build_resource_grid` + `_update_resource_grid` [Complex]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [ ] Rename the existing stockpile grid builder → `_build_stockpile_summary_row` (becomes a compact single-line display below the projection grid).
- [ ] Build new `_build_projection_grid` method that constructs:
  - Header row: Resource / Harvest / Upkeep / Yard / Net.
  - Data rows from `view.resource_projections`.
  - Uses `UILabel` cells with consistent column widths.
- [ ] Update `_update_resource_grid` to receive the view, populate projection grid cells, apply color to net cells.
- [ ] Retain stockpile summary row below the projection grid (e.g. "Stockpile: Metals 4523/10000  Organics 890/5000  ...").

**Notes:**

### Task 2.3: Visual layout calibration [Medium]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** Manual smoke

- [ ] Grid size: confirm 5 columns × (1 + N resources) rows fit in the panel's right-hand area without overlapping the complexes list.
- [ ] If vertical space is tight, consider placing the projection grid ABOVE the stockpile summary vs the existing layout.
- [ ] Font size + column widths tuned for readability at 2560px minimum resolution (per CLAUDE.md display target).

**Notes:**

### Task 2.4: Color the net column [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [ ] Import green/red color constants from `game/ui/colors.py` (or add if missing).
- [ ] Apply color via UILabel HTML or `.set_text_colour()` depending on pygame_gui version in use.
- [ ] Test: spy on color-apply calls; verify correct color per sign.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3: docs + cleanup)
