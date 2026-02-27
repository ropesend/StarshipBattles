# Phase 1: Test Fortification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-202 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add test coverage for untested code paths BEFORE refactoring to ensure behavioral preservation.

**Test file:** `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py`

---

## Tasks

### Task 1.1: Star Color Classification Tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestStarColorClassification -v`

Create parameterized tests for star color-to-asset-key mapping (strategy_renderer.py lines 344-353).

- [ ] Create test file with imports (pytest, unittest.mock, StrategyRenderer)
- [ ] Test red star: `color = (255, 50, 50)` -> `asset_key = 'red'`
- [ ] Test blue star: `color = (50, 50, 255)` -> `asset_key = 'blue'`
- [ ] Test white star: `color = (255, 255, 255)` -> `asset_key = 'white'`
- [ ] Test orange star: `color = (255, 180, 50)` -> `asset_key = 'orange'`
- [ ] Test yellow star (default): `color = (255, 255, 100)` -> `asset_key = 'yellow'`
- [ ] Test edge case: `color = (201, 99, 50)` -> verify classification
- [ ] Verify: All 6 color tests pass

**Notes:** Use mock to capture `asset_manager.load_image` calls and verify asset_key argument.

---

### Task 1.2: Colony Marker Visibility Tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestColonyMarkerRendering -v`

Test colony marker logic (strategy_renderer.py lines 325-336).

- [ ] Test marker drawn at low zoom (0.4) with owned planet
- [ ] Test marker NOT drawn at high zoom (0.6) with owned planet
- [ ] Test marker NOT drawn when no owned planets (zoom 0.4)
- [ ] Test marker uses correct owner empire color
- [ ] Verify: All 4 colony marker tests pass

**Notes:** Mock camera.zoom and check pygame.draw.circle calls.

---

### Task 1.3: Selection Highlight Tests [Simple]
**File:** `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestStarSelectionHighlight -v`

Test selection highlight logic (strategy_renderer.py line 359).

- [ ] Test highlight drawn when system is selected
- [ ] Test highlight only on primary star in multi-star system
- [ ] Test NO highlight when different object selected
- [ ] Verify: All 3 selection tests pass

**Notes:** Set `scene.selected_object` and verify white circle outline drawn.

---

### Task 1.4: Fallback Rendering Tests [Simple]
**File:** `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestFallbackRendering -v`

Test fallback when star image missing (strategy_renderer.py lines 366-367).

- [ ] Test fallback circle drawn when `star_img` is None
- [ ] Test image rendered when `star_img` exists
- [ ] Verify: Both fallback tests pass

**Notes:** Mock `asset_manager.load_image` to return None or valid surface.

---

### Task 1.5: Star Label Tests [Simple]
**File:** `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestStarLabelRendering -v`

Test label rendering (strategy_renderer.py lines 369-373).

- [ ] Test primary star shows system name (not star name)
- [ ] Test secondary star shows star name
- [ ] Test NO labels at low zoom (0.4)
- [ ] Verify: All 3 label tests pass

**Notes:** Mock font.render and check text argument.

---

### Task 1.6: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run all new tests: `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py -v`
- [ ] Run existing renderer tests: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: All tests pass (0 failures)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] New test file has at least 15 test cases
- [ ] All tests pass (run validation script)
- [ ] Commit: `[PROJ-202] Phase 1: Add test coverage for _draw_systems`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
