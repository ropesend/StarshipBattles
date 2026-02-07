# Phase 4: Simplify Main Window & Final Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-62 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Simplify `update()`, remove dead code, verify <500 lines

---

## Tasks

### Task 4.1: Simplify `update()` method [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/`

- [ ] Extract toggle handling helpers to reduce `update()` line count:
  - Create `_handle_filter_toggles(self)` helper (~25 lines) for type + owner toggle checks
  - Create `_handle_slider_sync(self)` helper (~20 lines) for slider-text synchronization
  - Create `_handle_preset_changes(self)` helper (~30 lines) for preset dropdown + save logic
- [ ] `update()` should now be ~40-50 lines calling helpers + column_mgr + renderer
- [ ] Verify all button press/toggle logic still works correctly

### Task 4.2: Remove dead code and cleanup [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/`

- [ ] Remove `self.virtual_scroll_y = 0.0` (line 146) - unused, scroll uses scroll_bar.start_percentage
- [ ] Remove `self.filter_name = ""` (line 39) - unused, txt_name_filter.get_text() used directly
- [ ] Remove debug-related code if not needed (`self._debug_next_click` and all F9 debug blocks in `process_event()`)
- [ ] Clean up redundant comments (e.g., "# PROJ-54" markers)
- [ ] Remove unused imports after all extractions

### Task 4.3: Final line count verification [Simple]
**Tests:** `pytest tests/`

- [ ] Count lines in `planet_list_window.py` - must be under 500
- [ ] If over 500, identify remaining extraction candidates
- [ ] Run full test suite: all 6248+ tests pass
- [ ] Update `docs/refactoring/LARGE_FILE_SPLIT_PLAN.md` to mark planet_list_window.py as COMPLETE

### Task 4.4: Update project documentation [Simple]

- [ ] Update plan.md Current State to "Complete"
- [ ] Update plan.md Quick Status table - all phases "Complete"

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
- [ ] Final line count of `planet_list_window.py`: ______ lines
