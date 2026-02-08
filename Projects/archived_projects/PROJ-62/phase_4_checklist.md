# Phase 4: Simplify Main Window & Final Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-62 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Simplify `update()`, remove dead code, verify <500 lines

---

## Tasks

### Task 4.1: Simplify `update()` method [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/`

- [x] Extract toggle handling helpers to reduce `update()` line count:
  - Created `_handle_filter_toggles(self, filter_dict, btn_all, btn_none, ui_key)` - unified handler for type + owner toggles
  - Created `_handle_slider_sync(self)` helper for slider-text synchronization
  - Created `_handle_preset_changes(self)` helper for preset dropdown + save logic
  - Created `_handle_column_toggles(self)` helper for column visibility
- [x] `update()` now ~30 lines calling helpers + column_mgr + renderer
- [x] Verify all button press/toggle logic still works correctly

### Task 4.2: Remove dead code and cleanup [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/`

- [x] Remove `self.filter_name = ""` - unused, txt_name_filter.get_text() used directly
- [x] Remove debug-related code (`self._debug_next_click` and all F9 debug blocks in `process_event()`)
- [x] Clean up redundant comments ("# PROJ-54" markers removed)
- [x] Remove unused imports after all extractions (UILabel, UIScrollingContainer, UITextEntryLine, UIHorizontalSlider)

### Task 4.3: Final line count verification [Simple]
**Tests:** `pytest tests/`

- [x] Count lines in `planet_list_window.py` - 490 lines (under 500)
- [x] Run full test suite: 6246 tests passed
- [x] Update `docs/refactoring/LARGE_FILE_SPLIT_PLAN.md` to mark planet_list_window.py as COMPLETE

### Task 4.4: Update project documentation [Simple]

- [x] Update plan.md Current State to "Complete"
- [x] Update plan.md Quick Status table - all phases "Complete"

**Notes:**
- Consolidated type and owner toggle handlers into unified `_handle_filter_toggles()` method
- Condensed slider sync with inner loop for min/max handling
- Compacted UI container initialization for readability

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete"
- [x] Final line count of `planet_list_window.py`: 490 lines
