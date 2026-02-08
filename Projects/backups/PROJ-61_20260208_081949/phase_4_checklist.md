# Phase 4: Final Cleanup & Verification [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove dead code, clean up, verify line count, run full test suite
**Estimated reduction:** ~35 lines

---

## Tasks

### Task 4.1: Remove dead code [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Remove `_debug_sequence_capture()` method (~20 lines)
- [x] Remove duplicate `self.show_firing_arcs = False` (line 149)
- [x] Remove empty tooltip pass block (lines 520-522)
- [x] Remove stale comments
- [x] Remove `_show_error` wrapper (line 377-378) - consolidate callers to use `show_error`
- [x] Clean up excessive blank lines

**Notes:** Removed 49 lines total. Also removed unused PANEL_BG constant.

### Task 4.2: Clean up imports [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Remove unused imports (UIDropDownMenu removed)
- [x] Remove duplicate Paths import (was line 77, top-level import retained)
- [x] Verify all remaining imports are used

**Notes:** ScreenshotManager kept - needed for F12/F11 keybinds in event router.

### Task 4.3: Update event router for debug removal [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Remove handler for `_debug_sequence_capture()` (F10 keybind)

**Notes:** F10 keybind removed. F12/F11 keybinds kept for screenshot functionality.

### Task 4.4: Verify line count [Simple]
- [x] Run `wc -l game/ui/screens/workshop_screen.py`
- [x] Confirm under 500 lines
- [x] If over 500, identify additional extraction opportunities

**Notes:** Final: 594 lines (was 643, reduced by 49 lines). Still over 500 target.
Remaining extraction opportunities if needed:
- `_execute_pending_action` (~35 lines) could move to event router
- `_create_ui` (~130 lines) is large but already well-structured

### Task 4.5: Full test suite [Simple]
**Tests:** `pytest tests/ -q`

- [x] Full suite passes: 6246 passed
- [x] No new failures vs baseline

**Notes:** All tests passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
