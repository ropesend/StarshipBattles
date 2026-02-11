# Phase 1: Restructure RaceThemeGallery as Vertical Scrollable List

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-96 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Convert RaceThemeGallery from a full-width horizontal layout to a compact vertical scrollable list, and update all associated tests.

---

## Tasks

### Task 1.1: Add `height` parameter to RaceThemeGallery constructor [Simple]
**File:** `game/ui/panels/race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [x] Add `height: int` parameter to `__init__` signature (line 32)
- [x] Store as `self.height = height`
- [x] Pass `height` to `_create_content` (line 67: add parameter)
- [x] Update `_create_content` signature (line 69) to accept `height`
- [x] Verify: Class instantiation still works (existing tests still pass with mock)

**Notes:** Verified in audit - height param at line 40, stored at line 59, passed at line 68

### Task 1.2: Remove preview label and preview panel [Simple]
**File:** `game/ui/panels/race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [x] Remove `self.theme_preview_panel` attribute (line 61)
- [x] Remove `self.theme_preview_label` attribute (line 62)
- [x] Add `self.theme_scroll: Optional[pygame_gui.elements.UIScrollingContainer] = None` instead
- [x] Remove "Select Ship Theme:" label creation in `_create_content` (lines 72-78)
- [x] Remove preview panel creation in `_create_content` (lines 81-94)
- [x] Remove `set_text` call in `on_theme_selected` (lines 182-183: the `if self.theme_preview_label:` block)
- [x] Verify: `on_theme_selected` still updates race_config and calls callback

**Notes:** Verified in audit - theme_scroll at line 63, no preview attributes found

### Task 1.3: Wrap theme buttons in UIScrollingContainer [Medium]
**File:** `game/ui/panels/race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [x] At start of `_create_content` (after removing label/preview), create `UIScrollingContainer`
- [x] Change theme button creation to use `container=self.theme_scroll` instead of `container=self.panel`
- [x] Change ship preview UIImage creation to use `container=self.theme_scroll` instead of `container=self.panel`
- [x] Adjust button positions: `x=0, y=local_y` (relative to scroll container, not panel)
- [x] After all buttons created, call `set_scrollable_area_dimensions`
- [x] Verify: Theme buttons appear inside scrollable container

**Notes:** Verified in audit - UIScrollingContainer at lines 73-79, container=self.theme_scroll at lines 91, 103, 111

### Task 1.4: Update unit tests for gallery changes [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [x] Delete `test_race_theme_gallery_has_preview_label` (line 66)
- [x] Delete `test_race_theme_gallery_has_preview_panel` (line 76)
- [x] Delete `test_on_theme_selected_updates_preview_label` (line 109)
- [x] Remove `gallery.theme_preview_label = MagicMock()` from relevant tests
- [x] Add `test_race_theme_gallery_has_scroll_container` test
- [x] Verify: All gallery tests pass

**Notes:** Verified in audit - no preview tests found, scroll_container test at line 66

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/ui/test_race_theme_gallery.py` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
