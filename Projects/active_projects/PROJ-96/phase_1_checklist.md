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

- [ ] Add `height: int` parameter to `__init__` signature (line 32)
- [ ] Store as `self.height = height`
- [ ] Pass `height` to `_create_content` (line 67: add parameter)
- [ ] Update `_create_content` signature (line 69) to accept `height`
- [ ] Verify: Class instantiation still works (existing tests still pass with mock)

**Notes:**

### Task 1.2: Remove preview label and preview panel [Simple]
**File:** `game/ui/panels/race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [ ] Remove `self.theme_preview_panel` attribute (line 61)
- [ ] Remove `self.theme_preview_label` attribute (line 62)
- [ ] Add `self.theme_scroll: Optional[pygame_gui.elements.UIScrollingContainer] = None` instead
- [ ] Remove "Select Ship Theme:" label creation in `_create_content` (lines 72-78)
- [ ] Remove preview panel creation in `_create_content` (lines 81-94)
- [ ] Remove `set_text` call in `on_theme_selected` (lines 182-183: the `if self.theme_preview_label:` block)
- [ ] Verify: `on_theme_selected` still updates race_config and calls callback

**Notes:**

### Task 1.3: Wrap theme buttons in UIScrollingContainer [Medium]
**File:** `game/ui/panels/race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [ ] At start of `_create_content` (after removing label/preview), create `UIScrollingContainer`:
  ```python
  self.theme_scroll = pygame_gui.elements.UIScrollingContainer(
      relative_rect=pygame.Rect(x, y, width, height),
      manager=self.ui_manager,
      container=self.panel,
      allow_scroll_x=False,
      allow_scroll_y=True
  )
  ```
- [ ] Change theme button creation to use `container=self.theme_scroll` instead of `container=self.panel`
- [ ] Change ship preview UIImage creation to use `container=self.theme_scroll` instead of `container=self.panel`
- [ ] Adjust button positions: `x=0, y=local_y` (relative to scroll container, not panel)
- [ ] After all buttons created, call:
  ```python
  self.theme_scroll.set_scrollable_area_dimensions((width, total_button_height))
  ```
- [ ] Verify: Theme buttons appear inside scrollable container

**Notes:** Pattern reference: `game/ui/panels/race_portrait_gallery.py` lines 106-112

### Task 1.4: Update unit tests for gallery changes [Simple]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [ ] Delete `test_race_theme_gallery_has_preview_label` (line 66)
- [ ] Delete `test_race_theme_gallery_has_preview_panel` (line 76)
- [ ] Delete `test_on_theme_selected_updates_preview_label` (line 109)
- [ ] Remove `gallery.theme_preview_label = MagicMock()` from:
  - `test_on_theme_selected_updates_race_config` (line 102)
  - `test_on_theme_selected_calls_callback_if_provided` (line 135)
  - `test_on_theme_selected_no_callback_no_error` (line 152)
  - `test_on_theme_selected_highlights_selected_button` (line 173)
  - `test_on_theme_selected_deselects_other_buttons` (line 196)
  - `test_set_from_config_selects_configured_theme` (line 232)
  - `test_handle_button_click_returns_true_for_theme_button` (line 273)
  - `test_handle_button_click_returns_false_for_other_button` (line 294)
- [ ] Add `test_race_theme_gallery_has_scroll_container` test
- [ ] Verify: All gallery tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/ui/test_race_theme_gallery.py` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
