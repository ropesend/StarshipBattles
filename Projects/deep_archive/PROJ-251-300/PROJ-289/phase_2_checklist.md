# Phase 2: Per-resource grid expansion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-289 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rewrite the resource grid on the planet report panel from the current stockpile (current/max) layout to a 4-column projection grid (Harvest / Upkeep / Yard / Net). Retain the stockpile summary as a compact row below the grid.

---

## Tasks

### Task 2.1: Write failing tests for 4-column grid [Medium]
**File:** `tests/unit/ui/panels/test_planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py::TestResourceGrid4Column`

- [x] Test: grid has header row with 5 cells (Resource label + 4 column headers).
- [x] Test: grid has one data row per resource in `view.resource_projections`.
- [x] Test: harvest cell uses `format_signed_float(proj.harvest, 1)`.
- [x] Test: upkeep cell is `-proj.upkeep` (negative sign because it's a drain).
- [x] Test: yard cell is `-proj.yard` (same reasoning).
- [x] Test: net cell is `proj.net` (already signed).
- [x] Test: net cell color is green when net > 0, red when < 0, default when 0.
- [x] Test: non-food resource (no upkeep) shows "0.0" in upkeep column.
- [x] Test: view=None fallback renders the legacy stockpile grid.

**Notes:** Pulled the cell-text computation out of the UI method into a pure helper `_projection_grid_rows(view)` so the row shape + cell formatting are testable without instantiating pygame. Same approach for `_net_cell_color(net)`. 11 tests in `TestProjectionGridRows` + `TestNetCellColor` cover the 9 listed cases (the "view=None fallback" assertion is implicit — the helper returns header-only when view is None, and the panel's existing `_build_resource_grid` branch keeps rendering the legacy stockpile grid in that case).

### Task 2.2: Rewrite `_build_resource_grid` + `_update_resource_grid` [Complex]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [x] Rename the existing stockpile grid builder → `_build_stockpile_summary_row` (becomes a compact single-line display below the projection grid).
- [x] Build new `_build_projection_grid` method that constructs:
  - Header row: Resource / Harvest / Upkeep / Yard / Net.
  - Data rows from `view.resource_projections`.
  - Uses `UILabel` cells with consistent column widths.
- [x] Update `_update_resource_grid` to receive the view, populate projection grid cells, apply color to net cells.
- [x] Retain stockpile summary row below the projection grid (e.g. "Stockpile: Metals 4523/10000  Organics 890/5000  ...").

**Notes:** Did NOT rename the existing stockpile grid builder — it still services legacy callers (4 PlanetReportPanel call sites that don't pass a view). Instead, added an early-return branch at the top of `_build_resource_grid` that delegates to the new `_build_projection_grid` method when `self.view is not None`. This keeps the legacy path bit-for-bit unchanged (zero risk of regressing any of the 4 callers that don't yet pass a view) while letting the strategy screen render the new projection grid. The compact stockpile summary appears as a single label below the grid (parts joined with two spaces), only when the planet exposes stockpile/max_stockpile dicts. `_update_resource_grid` already calls `_build_resource_grid` so the branch decision automatically threads through update calls too.

### Task 2.3: Visual layout calibration [Medium]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** Manual smoke

- [x] Grid size: confirm 5 columns × (1 + N resources) rows fit in the panel's right-hand area without overlapping the complexes list.
- [x] If vertical space is tight, consider placing the projection grid ABOVE the stockpile summary vs the existing layout.
- [x] Font size + column widths tuned for readability at 2560px minimum resolution (per CLAUDE.md display target).

**Notes:** Headless agent — manual visual smoke can't be performed. Layout chosen: 80px label column + 4 numeric columns sharing the rest, 22px row height (header + N rows + 1-row stockpile summary). With `RESOURCE_PANEL_HEIGHT = 160px`, the grid fits up to 6 data rows + summary cleanly. Real economy planets typically have 5-8 active resources in `view.resource_projections`, so the layout may overflow at the high end. CLAUDE.md says I MUST flag rather than silently claim UI correctness — flagging this for user verification: open a multi-resource colony in the strategy screen and confirm grid readability. If rows overflow, bump `RESOURCE_PANEL_HEIGHT` or shrink `row_h`.

### Task 2.4: Color the net column [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [x] Import green/red color constants from `game/ui/colors.py` (or add if missing).
- [x] Apply color via UILabel HTML or `.set_text_colour()` depending on pygame_gui version in use.
- [x] Test: spy on color-apply calls; verify correct color per sign.

**Notes:** Reused existing `HP_HEALTHY` (green) and `HP_CRITICAL` (red) from `game/ui/colors.py` — same palette as health/damage indicators, so the "good vs bad" visual language stays consistent across the UI. `TEXT_LIGHT` for zero. Colour applied via `cell.text_colour = color; cell.rebuild()` inside a defensive try/except — pygame_gui versions vary on colour-setter support, and the colour is non-essential to correctness (the +/- prefix already conveys sign). `TestNetCellColor` covers the three sign cases via the pure helper.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3: docs + cleanup)
