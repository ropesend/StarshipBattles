# Phase 1: Extract BuildQueuePortraitLoader

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-63 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract portrait/image loading logic into `game/ui/panels/build_queue_portraits.py`

---

## Tasks

### Task 1.1: Create BuildQueuePortraitLoader class [Medium]
**File:** `game/ui/panels/build_queue_portraits.py` (NEW)
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_drag_drop.py tests/repro_issues/test_bug_17_drag_preview.py`

- [ ] Create `game/ui/panels/build_queue_portraits.py` with class `BuildQueuePortraitLoader`
- [ ] Constructor: `__init__(self, design_library, session)` — stores `design_library` and `session`
- [ ] Move `_load_design_portrait(self, design, size)` method from `build_queue_screen.py` (lines 404-469)
  - Rename to `load_design_portrait(self, design, size)` (public method)
  - Keep all logic: theme lookup, regex ship class parsing, path search, pygame load, placeholder fallback
  - Move `import os` and `import re` to module-level imports
- [ ] Move `_load_queue_item_portrait(self, design_id, item_type, size)` method from `build_queue_screen.py` (lines 539-572)
  - Rename to `load_queue_item_portrait(self, design_id, item_type, size)` (public method)
  - Calls `self.load_design_portrait()` internally (no change in logic)
- [ ] Consolidate duplicated `color_map` dicts into a single module-level constant `VEHICLE_TYPE_COLORS`
  - Current duplication: lines 457-462 and lines 561-567
  - Both maps used for placeholder generation
- [ ] Add necessary imports: `pygame`, `Optional` from typing, `log_warning` from `game.core.logger`
- [ ] Verify: File is self-contained, no circular imports

### Task 1.2: Wire BuildQueuePortraitLoader into BuildQueueScreen [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_drag_drop.py`

- [ ] Add import: `from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader`
- [ ] In `__init__`, create instance: `self.portrait_loader = BuildQueuePortraitLoader(self.design_library, self.session)`
- [ ] Replace `self._load_design_portrait(design, size)` calls with `self.portrait_loader.load_design_portrait(design, size)`:
  - In `_refresh_items_list()` (line 375)
  - In `handle_event()` MOUSEBUTTONDOWN section (line 745)
- [ ] Replace `self._load_queue_item_portrait(design_id, item_type, size)` calls with `self.portrait_loader.load_queue_item_portrait(...)`:
  - In `_refresh_queue_display()` (line 503)
  - In `handle_event()` MOUSEMOTION section (line 780)
- [ ] Delete `_load_design_portrait` method (lines 404-469)
- [ ] Delete `_load_queue_item_portrait` method (lines 539-572)
- [ ] Verify: No remaining references to deleted methods

### Task 1.3: Run tests and verify [Simple]
**Tests:** `pytest tests/ -x -q`

- [ ] Run full test suite: `pytest tests/ -x -q`
- [ ] Verify 6248 tests still pass
- [ ] Verify `build_queue_screen.py` line count reduced (should be ~845 lines, down ~100)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
