# Phase 4: Update Tests + Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-80 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix failing tests, update assertions for new dimensions, remove dead code, run full suite.

---

## Tasks

### Task 4.1: Update test_build_queue_design_report.py [Simple]
**File:** `tests/integration/ui/test_build_queue_design_report.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_design_report.py -v`

Known assertion updates needed (panel is now 750px wide in test fixture, portrait is 730x730):
- [ ] `test_design_portrait_dimensions` (line 174): portrait already expects 730x730 at 750px panel - should pass as-is since fixture already uses 750px container
- [ ] `test_stats_container_position` (line 204): stats container y should be `730 + 20 = 750` (below 730px portrait)
- [ ] `test_no_requirements_section` (line 270): should still pass (DesignStatsPanel with show_requirements=False)
- [ ] `test_no_warnings_section` (line 279): should still pass
- [ ] `test_panel_dimensions_match_design_workshop` (line 288): already expects 750px - should pass
- [ ] `test_stat_sections_exist_after_update` (line 246): verify all section checks still work with `get_logistics_rows()` dynamic sections
- [ ] Run tests and fix any additional failures

**Notes:** The test fixture already creates the panel at 750x350, so portrait dimension tests should pass. The main change is that stats now use `get_logistics_rows()` instead of static keys, but the test assertions check for key presence which should still match.

### Task 4.2: Update test_stats_render.py if needed [Simple]
**File:** `tests/unit/ui/test_stats_render.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py -v`

- [ ] Verify `test_stats_panel_creation_and_update` passes - it checks `panel.rows_map` contains 'mass', 'max_speed', 'shield_regen', 'emissive_armor', 'targeting', 'crew_required'
- [ ] Verify `test_logistics_section` passes - it checks `panel.rows_map` contains 'max_fuel'
- [ ] If tests fail due to module reload issues with moved `StatRow`, fix import paths in test patches
- [ ] Run tests and fix any failures

**Notes:** These tests heavily mock pygame_gui elements and may need patch target updates if `StatRow` is now imported from `design_stats_panel` instead of `right_panel`.

### Task 4.3: Update test_bug_04_display.py if needed [Simple]
**File:** `tests/repro_issues/test_bug_04_display.py`
**Tests:** `pytest tests/repro_issues/test_bug_04_display.py -v`

- [ ] Run test and verify it passes
- [ ] Fix any import path issues related to `StatRow` move

**Notes:**

### Task 4.4: Update test_build_queue_formatting.py if needed [Simple]
**File:** `tests/integration/ui/test_build_queue_formatting.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_formatting.py -v`

- [ ] Run test and verify it passes
- [ ] Fix any assertions that depend on the old 400px design report width

**Notes:**

### Task 4.5: Final cleanup and dead code removal [Simple]
**Files:** Multiple
**Tests:** `pytest tests/ -n 12`

- [ ] Verify `right_panel.py` has no unused imports after refactor
- [ ] Verify `design_report_panel.py` has no unused imports after refactor
- [ ] Remove any commented-out code
- [ ] Verify `ship_detail_panel.py` is unaffected (only references DesignReportPanel in docstring)
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify baseline: 6246 tests pass

**Notes:**

### Task 4.6: Manual visual verification [Simple]
**Tests:** Manual

- [ ] Launch Design Workshop → verify two-column stats display with Requirements/Recommendations at bottom
- [ ] Verify Build Cost section now visible in Design Workshop
- [ ] Launch Build Queue from strategy map → verify two-column stats display WITHOUT Requirements/Recommendations
- [ ] Verify Build Queue design report panel is wider (750px)
- [ ] Verify Build Queue list is narrower but still functional
- [ ] Verify both panels show identical stat sections (same ordering, same section headers)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 6246 tests passing
- [ ] No dead code in modified files
- [ ] Visual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
