# Phase 2: Tests & Polish

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-82 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update existing tests and add new tests for the resource grid panel. Run full test suite to verify no regressions.

---

## Tasks

### Task 2.1: Update existing tests [Simple]
**File:** `tests/integration/ui/test_build_queue_enhanced_planet_report.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- [ ] Fix any tests that assert resource text is in the info textbox (it no longer will be)
- [ ] Update `test_planet_report_panel_initializes` to also check `resource_panel` exists
- [ ] Verify `test_planet_portrait_dimensions` still passes (portrait position unchanged)
- [ ] Verify `test_atmosphere_graph_position` still passes (graph position unchanged, but height may differ)
- [ ] Verify `test_panel_minimum_height` and `test_get_height_required_returns_valid_height` — may need to adjust expected values due to increased minimum height
- [ ] Run all existing tests and fix any failures

**Notes:**

---

### Task 2.2: Add resource grid tests [Simple]
**File:** `tests/integration/ui/test_build_queue_enhanced_planet_report.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- [ ] Add test `test_resource_grid_exists`:
  - Create panel with planet that has resources
  - Assert `panel.resource_panel` is not None
  - Assert `panel._resource_grid_items` is not empty
- [ ] Add test `test_resource_grid_shows_all_resources`:
  - Create panel with planet that has all 5 resources
  - Assert 5 icon images exist in the grid
- [ ] Add test `test_resource_grid_with_production`:
  - Create panel with `production_rates={"Metals": 100.0, "Organics": 50.0}`
  - Verify panel accepts the parameter without error
- [ ] Add test `test_resource_grid_no_production`:
  - Create panel without production_rates (defaults to empty)
  - Verify panel creates without error
- [ ] Add test `test_resource_grid_updates_on_planet_change`:
  - Create panel, then call `update_planet(new_planet)`
  - Verify grid is refreshed (no crash, new data reflected)
- [ ] Add test `test_resource_panel_no_resources`:
  - Create panel with planet that has empty resources dict
  - Verify grid shows zeros/empty without crashing
- [ ] Add resources to `test_planet` fixture:
  ```python
  planet.resources = {
      "Metals": {"quantity": 250000, "quality": 85.0},
      "Organics": {"quantity": 120000, "quality": 72.0},
      "Vapors": {"quantity": 80000, "quality": 91.0},
      "Radioactives": {"quantity": 45000, "quality": 43.0},
      "Exotics": {"quantity": 12000, "quality": 67.0},
  }
  ```

**Notes:**

---

### Task 2.3: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests must pass (baseline: 6246)
- [ ] Fix any regressions found

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md Verification section — check all boxes
