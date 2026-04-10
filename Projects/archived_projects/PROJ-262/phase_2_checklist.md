# Phase 2: Delete Set-Then-Assert and Over-Mocked Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-262 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete set-then-assert tests, over-mocked tests, and local-arithmetic repro files (~1,000 LOC). Some files are deleted entirely; others require surgical removal of specific test classes while preserving legitimate tests.

---

## Tasks

### Task 2.1: Delete entire files (5 files) [Simple]
**Tests:** N/A (deletion only)

These files are entirely set-then-assert, over-mocked, or local-arithmetic with no production imports.

- [ ] Read `tests/unit/ui/screens/test_workshop_screen_integration.py` (250 LOC) -- confirm all tests are set-then-assert / over-mocked
- [ ] Delete `tests/unit/ui/screens/test_workshop_screen_integration.py`
- [ ] Read `tests/unit/strategy/data/test_ship_pod_storage.py` (74 LOC) -- confirm tests mock lambdas, no real logic
- [ ] Delete `tests/unit/strategy/data/test_ship_pod_storage.py`
- [ ] Read `tests/repro_issues/test_bug_14_multi_planet_offset.py` (337 LOC) -- confirm local arithmetic only
- [ ] Delete `tests/repro_issues/test_bug_14_multi_planet_offset.py`
- [ ] Read `tests/repro_issues/test_bug_16_raw_data_button.py` (64 LOC) -- confirm local math + inspect.getsource
- [ ] Delete `tests/repro_issues/test_bug_16_raw_data_button.py`
- [ ] Read `tests/repro_issues/test_bug_17_drag_preview.py` (62 LOC) -- confirm inspect.getsource only
- [ ] Delete `tests/repro_issues/test_bug_17_drag_preview.py`
- [ ] Read `tests/repro_issues/test_crash_planet_list.py` (43 LOC) -- confirm tests local MockPlanetListWindow only
- [ ] Delete `tests/repro_issues/test_crash_planet_list.py`

**Notes:**

### Task 2.2: Surgical edit -- test_galaxy_test_screen.py [Medium]
**File:** `tests/unit/ui/screens/test_galaxy_test_screen.py` (281 LOC)
**Tests:** `pytest tests/unit/ui/screens/test_galaxy_test_screen.py -v`

- [ ] Read file and identify test classes/methods
- [ ] Delete `TestGalaxyTestScreenInit` class (set-then-assert init tests)
- [ ] Delete `TestCameraSetup::test_screen_has_camera` (attribute existence)
- [ ] Delete `TestFPSTracking` class (set-then-assert)
- [ ] Delete any import/constant assertion tests (e.g., `test_*_can_be_imported`)
- [ ] Keep RGB validation tests and any tests that call real production methods
- [ ] Run `pytest tests/unit/ui/screens/test_galaxy_test_screen.py -v` -- confirm remaining tests pass

**Notes:**

### Task 2.3: Surgical edit -- test_design_report_panel.py [Medium]
**File:** `tests/unit/ui/panels/test_design_report_panel.py` (531 LOC)
**Tests:** `pytest tests/unit/ui/panels/test_design_report_panel.py -v`

- [ ] Read file and identify test classes
- [ ] Delete `TestDesignReportPanelInit` class (~12 set-then-assert tests, lines ~48-118)
- [ ] Delete `TestShowPlaceholder` class (set-then-assert, lines ~122-203)
- [ ] Keep `TestUpdateDesign`, `TestUpdatePortrait`, `TestPanelKill`, `TestWidthRequired` (real behavioral tests)
- [ ] Run `pytest tests/unit/ui/panels/test_design_report_panel.py -v` -- confirm remaining tests pass

**Notes:** TestUpdateDesign calls real panel.update_design(ship), TestPanelKill calls real kill(). These must stay.

### Task 2.4: Surgical edit -- test_planet_report_panel.py [Medium]
**File:** `tests/unit/ui/panels/test_planet_report_panel.py` (496 LOC)
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py -v`

- [ ] Read file and identify test classes
- [ ] Delete `TestPlanetReportPanelInit` class (5 set-then-assert tests)
- [ ] Delete `TestUpdatePlanet` set-then-assert tests (e.g., test_update_planet_sets_planet, test_update_planet_sets_production_rates)
- [ ] Delete `TestComplexesList` reimplemented-logic tests (e.g., test_complexes_container_none_check, test_complex_items_is_list)
- [ ] Keep tests that call real methods with real side effects
- [ ] Run `pytest tests/unit/ui/panels/test_planet_report_panel.py -v` -- confirm remaining tests pass

**Notes:**

### Task 2.5: Surgical edit -- test_design_stats_panel.py [Medium]
**File:** `tests/unit/ui/panels/test_design_stats_panel.py` (299 LOC)
**Tests:** `pytest tests/unit/ui/panels/test_design_stats_panel.py -v`

- [ ] Read file and identify test classes
- [ ] Delete StatCalc tests (local reimplemented calculations)
- [ ] Delete Formatting tests (local string formatting, no production code)
- [ ] Delete RowsMap tests (set-then-assert)
- [ ] Delete LayerStatus tests (set-then-assert)
- [ ] Keep any tests that call real production panel methods
- [ ] Run `pytest tests/unit/ui/panels/test_design_stats_panel.py -v` -- confirm remaining tests pass

**Notes:**

### Task 2.6: Surgical edit -- test_strategy_screen.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_screen.py` (917 LOC)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

- [ ] Read file around lines 738-799
- [ ] Identify the 3 boundary tests (set-then-assert)
- [ ] Delete those 3 tests only
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_screen.py -v` -- confirm remaining tests pass

**Notes:**

### Task 2.7: Surgical edit -- test_strategy_scene.py (integration) [Simple]
**File:** `tests/integration/strategy/test_strategy_scene.py` (123 LOC)
**Tests:** `pytest tests/integration/strategy/test_strategy_scene.py -v`

- [ ] Read file and identify TestTurnManagement class and test_colonize_command_queues
- [ ] Delete `TestTurnManagement` class (2 tests, local lambdas)
- [ ] Delete `test_colonize_command_queues` (tests Fleet.add_order on mock)
- [ ] Keep any tests that exercise real integration paths
- [ ] If file becomes empty after deletions, delete the entire file
- [ ] Run `pytest tests/integration/strategy/test_strategy_scene.py -v` -- confirm remaining tests pass (or file deleted)

**Notes:**

### Task 2.8: Run test suite and verify [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite
- [ ] Confirm zero failures
- [ ] Record new test count (expect ~40-60 fewer tests than Phase 1 baseline)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
