# Phase 2: Eradicate Backward Compatibility Properties

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-180 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove all 14 backward-compat property shims from BuildQueueScreen and update every caller to use `screen.panels.*` or `screen.renderer.*` directly

---

## Tasks

### Task 2.1: Update unit test - test_build_queue_screen.py [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py -x`

- [x] Line 468: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [x] Line 470: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [x] Line 475: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [x] Line 533: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [x] Line 535: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [x] Line 540: `screen.queue_items = [MagicMock()...]` → `screen.renderer.queue_items = [MagicMock()...]`
- [x] Line 542: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [x] Run tests to verify

**Notes:** 38 tests passed

### Task 2.2: Update unit test - test_sub_window_hotkeys.py [Simple]
**File:** `tests/unit/ui/screens/test_sub_window_hotkeys.py`
**Tests:** `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py -x`

- [x] Line 125: `screen.btn_close = MagicMock()` → `screen.panels.btn_close = MagicMock()`
- [x] Lines 128-131: `screen.btn_category_*` → `screen.panels.btn_category_*` (4 lines)
- [x] Line 227: `screen.btn_close.set_tooltip` → `screen.panels.btn_close.set_tooltip`
- [x] Lines 245-248: `screen.btn_category_*.set_tooltip` → `screen.panels.btn_category_*.set_tooltip`
- [x] Check lines 218, 236 for dual-path mock wiring — simplified to direct `screen.panels.*`
- [x] Run tests to verify

**Notes:** Simplified _make_screen() to set up panels directly; removed redundant dual-path wiring from tooltip tests. 25 tests passed.

### Task 2.3: Update integration test - test_basics.py [Simple]
**File:** `tests/integration/ui/build_queue_screen/test_basics.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_basics.py -x`

- [x] Lines 136-137: `build_queue_screen.planet_report` → `build_queue_screen.panels.planet_report`
- [x] Lines 142-143: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [x] Lines 148-149: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [x] Lines 152-155: `build_queue_screen.btn_category_*` → `build_queue_screen.panels.btn_category_*`
- [x] Lines 160-161: `build_queue_screen.btn_close` → `build_queue_screen.panels.btn_close`
- [x] Update any `hasattr` checks to reference `panels.*` path
- [x] Run tests to verify

**Notes:** Also updated test_queue_display_updates to use renderer.queue_items. 15 tests passed.

### Task 2.4: Update integration test - test_build_queue_formatting.py [Simple]
**File:** `tests/integration/ui/test_build_queue_formatting.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_formatting.py -x`

- [x] Line 141-142: `build_queue_screen.planet_report` → `build_queue_screen.panels.planet_report`
- [x] Line 147: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [x] Line 163: `build_queue_screen.build_queue_panel` → `build_queue_screen.panels.build_queue_panel`
- [x] Line 179: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [x] Line 197: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [x] Line 216: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [x] Lines 233-234: `build_queue_screen.design_report` → `build_queue_screen.panels.design_report`
- [x] Run tests to verify

**Notes:** 7 tests passed

### Task 2.5: Update integration test - test_build_queue_drag_drop.py [Simple]
**File:** `tests/integration/ui/test_build_queue_drag_drop.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py -x`

- [x] Line 118: `build_queue_screen.items_scrollable` → `build_queue_screen.panels.items_scrollable`
- [x] Line 157: `build_queue_screen.build_queue_panel` → `build_queue_screen.panels.build_queue_panel`
- [x] Line 207: `build_queue_screen.queue_items` → `build_queue_screen.renderer.queue_items`
- [x] Lines 232-233: `build_queue_screen.queue_scrollable` → `build_queue_screen.panels.queue_scrollable`
- [x] Line 255: `build_queue_screen.queue_items` → `build_queue_screen.renderer.queue_items`
- [x] Run tests to verify

**Notes:** 5 tests passed

### Task 2.6: Update integration test - test_queue_selector.py [Simple]
**File:** `tests/integration/ui/build_queue_screen/test_queue_selector.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_queue_selector.py -x`

- [x] Line 374: `bq.queue_items` → `bq.renderer.queue_items`
- [x] Run tests to verify

**Notes:** 12 tests passed

### Task 2.7: Delete backward-compat properties from BuildQueueScreen [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ -n 12` (full suite — critical deletion step)

- [x] Delete section comment at lines 157-159 (`# Backward Compatibility Properties...`)
- [x] Delete all 14 property definitions at lines 161-234
- [x] Run full test suite to verify zero breakage
- [x] Grep codebase for any remaining references to deleted properties

**Notes:** Deleted 79 lines of backward-compat code. Full suite: 12358 passed, 1 skipped. No remaining references found.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (full suite)
- [x] No references to deleted properties remain in codebase
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
