# Phase 3: Update Tests and Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-166 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all theme gallery tests for the new BaseGallery-based API, and run full test suite to confirm zero regressions.

---

## Tasks

### Task 3.1: Update theme gallery test imports and fixtures [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** Tests will pass incrementally as each test class is updated

- [x] Update module docstring to note PROJ-166 refactoring
- [x] No fixture changes needed (mock_race_config, mock_ui_manager, mock_panel are fine)

**Notes:**

### Task 3.2: Update TestRaceThemeGalleryCreation tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestRaceThemeGalleryCreation -v`

- [x] `test_race_theme_gallery_has_button_list` - Updated to use asset_buttons
- [x] `test_race_theme_gallery_has_scroll_container` - Updated to use scroll_container

**Notes:** Updated in Phase 2

### Task 3.3: Update TestThemeSelection tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestThemeSelection -v`

- [x] All tests updated to use on_asset_selected and asset_buttons

**Notes:** Updated in Phase 2

### Task 3.4: Update TestButtonHighlighting tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestButtonHighlighting -v`

- [x] All tests updated to use on_asset_selected and asset_buttons

**Notes:** Updated in Phase 2

### Task 3.5: Update TestConfigurationBinding tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestConfigurationBinding -v`

- [x] All tests updated to use on_asset_selected

**Notes:** Updated in Phase 2

### Task 3.6: Update TestButtonClickHandling tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestButtonClickHandling -v`

- [x] All tests updated to use asset_buttons with 2-tuple structure

**Notes:** Updated in Phase 2

### Task 3.7: Run all gallery tests together [Simple]
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py tests/unit/ui/test_race_flag_gallery.py tests/unit/ui/test_race_theme_gallery.py -v`

- [x] All portrait gallery tests pass (18 tests)
- [x] All flag gallery tests pass (12 tests)
- [x] All theme gallery tests pass (13 tests)

**Notes:** 43 total gallery tests passing

### Task 3.8: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12 -q`

- [x] All tests pass: 12016 passed, 1 skipped
- [x] No regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All 13 theme gallery tests pass with updated API
- [x] Full test suite passes (12016 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `Complete`
