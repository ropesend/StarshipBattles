# Phase 1: Extract BuildQueuePortraitLoader

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-63 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract portrait/image loading logic into `game/ui/panels/build_queue_portraits.py`

---

## Tasks

### Task 1.1: Create BuildQueuePortraitLoader class [Medium]
**File:** `game/ui/panels/build_queue_portraits.py` (NEW)
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_drag_drop.py tests/repro_issues/test_bug_17_drag_preview.py`

- [x] Create `game/ui/panels/build_queue_portraits.py` with class `BuildQueuePortraitLoader`
- [x] Constructor: `__init__(self, design_library, session)` — stores `design_library` and `session`
- [x] Move `_load_design_portrait(self, design, size)` method from `build_queue_screen.py` (lines 404-469)
  - Rename to `load_design_portrait(self, design, size)` (public method)
  - Keep all logic: theme lookup, regex ship class parsing, path search, pygame load, placeholder fallback
  - Move `import os` and `import re` to module-level imports
- [x] Move `_load_queue_item_portrait(self, design_id, item_type, size)` method from `build_queue_screen.py` (lines 539-572)
  - Rename to `load_queue_item_portrait(self, design_id, item_type, size)` (public method)
  - Calls `self.load_design_portrait()` internally (no change in logic)
- [x] Consolidate duplicated `color_map` dicts into a single module-level constant `VEHICLE_TYPE_COLORS`
  - Current duplication: lines 457-462 and lines 561-567
  - Both maps used for placeholder generation
- [x] Add necessary imports: `pygame`, `Optional` from typing, `log_warning` from `game.core.logger`
- [x] Verify: File is self-contained, no circular imports

### Task 1.2: Wire BuildQueuePortraitLoader into BuildQueueScreen [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_drag_drop.py`

- [x] Add import: `from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader`
- [x] In `__init__`, create instance: `self.portrait_loader = BuildQueuePortraitLoader(self.design_library, self.session)`
- [x] Replace `self._load_design_portrait(design, size)` calls with `self.portrait_loader.load_design_portrait(design, size)`:
  - In `_refresh_items_list()` (line 375)
  - In `handle_event()` MOUSEBUTTONDOWN section (line 745)
- [x] Replace `self._load_queue_item_portrait(design_id, item_type, size)` calls with `self.portrait_loader.load_queue_item_portrait(...)`:
  - In `_refresh_queue_display()` (line 503)
  - In `handle_event()` MOUSEMOTION section (line 780)
- [x] Delete `_load_design_portrait` method (lines 404-469)
- [x] Delete `_load_queue_item_portrait` method (lines 539-572)
- [x] Verify: No remaining references to deleted methods

### Task 1.3: Run tests and verify [Simple]
**Tests:** `pytest tests/ -x -q`

- [x] Run full test suite: `pytest tests/ -x -q`
- [x] Verify 6246 tests still pass
- [x] Verify `build_queue_screen.py` line count reduced (should be ~845 lines, down ~100)
  - **Result:** 847 lines (down from 946, -99 lines)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Implementation Notes
- Updated `test_portrait_logging.py` to use `bq_screen.portrait_loader.load_design_portrait()`
  instead of the old `bq_screen._load_design_portrait()` method
- Consolidated color maps into single `VEHICLE_TYPE_COLORS` constant with lowercase keys
- Added `_create_placeholder` and `_create_type_placeholder` helper methods for cleaner code
