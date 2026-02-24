# Phase 3: Update Tests and Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-166 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all theme gallery tests for the new BaseGallery-based API, and run full test suite to confirm zero regressions.

---

## Tasks

### Task 3.1: Update theme gallery test imports and fixtures [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** Tests will pass incrementally as each test class is updated

- [ ] Update module docstring to note PROJ-166 refactoring
- [ ] No fixture changes needed (mock_race_config, mock_ui_manager, mock_panel are fine)

**Notes:**

### Task 3.2: Update TestRaceThemeGalleryCreation tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestRaceThemeGalleryCreation -v`

- [ ] `test_race_theme_gallery_has_button_list` (lines 55-64):
  - Change `gallery.theme_buttons = []` → `gallery.asset_buttons = []` (line 61)
  - Change `assert hasattr(gallery, 'theme_buttons')` → `assert hasattr(gallery, 'asset_buttons')` (line 63)
  - Change `isinstance(gallery.theme_buttons, list)` → `isinstance(gallery.asset_buttons, list)` (line 64)
- [ ] `test_race_theme_gallery_has_scroll_container` (lines 66-74):
  - Change `gallery.theme_scroll = None` → `gallery.scroll_container = None` (line 72)
  - Change `assert hasattr(gallery, 'theme_scroll')` → `assert hasattr(gallery, 'scroll_container')` (line 74)

**Notes:**

### Task 3.3: Update TestThemeSelection tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestThemeSelection -v`

- [ ] `test_on_theme_selected_updates_race_config` (lines 84-96):
  - Change `gallery.theme_buttons = []` → `gallery.asset_buttons = []` (line 91)
  - Change `gallery.on_theme_selected("terran")` → `gallery.on_asset_selected("terran")` (line 94)
- [ ] `test_on_theme_selected_calls_callback_if_provided` (lines 98-112):
  - Change `gallery.theme_buttons = []` → `gallery.asset_buttons = []` (line 105)
  - Change `gallery.on_theme_selected("terran")` → `gallery.on_asset_selected("terran")` (line 110)
- [ ] `test_on_theme_selected_no_callback_no_error` (lines 114-125):
  - Change `gallery.theme_buttons = []` → `gallery.asset_buttons = []` (line 121)
  - Change `gallery.on_theme_selected("terran")` → `gallery.on_asset_selected("terran")` (line 125)
- [ ] All three tests: also need to set `gallery._asset_loader = MagicMock()` and `gallery.preview_panel = None` since BaseGallery now provides `on_asset_selected` which calls `_update_preview` → but RaceThemeGallery overrides `_update_preview` as no-op so these may not be strictly needed. Add if tests fail.

**Notes:**

### Task 3.4: Update TestButtonHighlighting tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestButtonHighlighting -v`

- [ ] `test_on_theme_selected_highlights_selected_button` (lines 135-155):
  - Change `gallery.theme_buttons` → `gallery.asset_buttons` (line 147)
  - Change tuple structure from `(btn1, "terran")` to `(btn1, "terran")` — **already 2-tuples! No structure change needed** after Phase 1 normalization
  - Change `gallery.on_theme_selected("terran")` → `gallery.on_asset_selected("terran")` (line 152)
  - Add `gallery._asset_loader = MagicMock()` and `gallery.preview_panel = None` if needed
- [ ] `test_on_theme_selected_deselects_other_buttons` (lines 157-180):
  - Same changes: `theme_buttons` → `asset_buttons`, `on_theme_selected` → `on_asset_selected`

**Notes:**

### Task 3.5: Update TestConfigurationBinding tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestConfigurationBinding -v`

- [ ] `test_set_from_config_selects_configured_theme` (lines 190-206):
  - Change `gallery.theme_buttons = []` → `gallery.asset_buttons = []` (line 198)
  - Change `gallery.on_theme_selected = MagicMock()` → `gallery.on_asset_selected = MagicMock()` (line 202)
  - Change assertion `gallery.on_theme_selected.assert_called_once_with("terran")` → `gallery.on_asset_selected.assert_called_once_with("terran")` (line 206)
- [ ] `test_set_from_config_no_theme_id_no_selection` (lines 208-222):
  - Change `gallery.on_theme_selected = MagicMock()` → `gallery.on_asset_selected = MagicMock()` (line 218)
  - Change `gallery.on_theme_selected.assert_not_called()` → `gallery.on_asset_selected.assert_not_called()` (line 222)

**Notes:**

### Task 3.6: Update TestButtonClickHandling tests [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py::TestButtonClickHandling -v`

- [ ] `test_handle_button_click_returns_true_for_theme_button` (lines 232-250):
  - Change `gallery.theme_buttons` → `gallery.asset_buttons` (line 243)
  - Tuple structure is already 2-tuple after Phase 1
- [ ] `test_handle_button_click_returns_false_for_other_button` (lines 252-271):
  - Change `gallery.theme_buttons` → `gallery.asset_buttons` (line 264)
  - Tuple structure is already 2-tuple after Phase 1
- [ ] Both tests need to mock `on_asset_selected` or set up enough state for it to run (since `handle_button_click` calls `on_asset_selected`). Add `gallery._set_selection = MagicMock()` or mock `on_asset_selected` directly.

**Notes:**

### Task 3.7: Run all gallery tests together [Simple]
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py tests/unit/ui/test_race_flag_gallery.py tests/unit/ui/test_race_theme_gallery.py -v`

- [ ] All portrait gallery tests pass
- [ ] All flag gallery tests pass
- [ ] All theme gallery tests pass (12 tests)

**Notes:**

### Task 3.8: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12 -q`

- [ ] All tests pass (baseline: 11994 passed, 1 skipped)
- [ ] No regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 12 theme gallery tests pass with updated API
- [ ] Full test suite passes (11994+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
