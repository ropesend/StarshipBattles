# Phase 2: Eradicate Backward Compatibility Properties

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-180 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove all 14 backward-compat property shims from BuildQueueScreen and update every caller to use `screen.panels.*` or `screen.renderer.*` directly

---

## Tasks

### Task 2.1: Update unit test - test_build_queue_screen.py [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py -x`

- [ ] Line 468: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [ ] Line 470: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [ ] Line 475: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [ ] Line 533: `screen.queue_items = []` → `screen.renderer.queue_items = []`
- [ ] Line 535: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [ ] Line 540: `screen.queue_items = [MagicMock()...]` → `screen.renderer.queue_items = [MagicMock()...]`
- [ ] Line 542: `len(screen.queue_items)` → `len(screen.renderer.queue_items)`
- [ ] Run tests to verify

**Notes:** [Filled during implementation]

### Task 2.2: Update unit test - test_sub_window_hotkeys.py [Simple]
**File:** `tests/unit/ui/screens/test_sub_window_hotkeys.py`
**Tests:** `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py -x`

- [ ] Line 125: `screen.btn_close = MagicMock()` → `screen.panels.btn_close = MagicMock()`
- [ ] Lines 128-131: `screen.btn_category_*` → `screen.panels.btn_category_*` (4 lines)
- [ ] Line 227: `screen.btn_close.set_tooltip` → `screen.panels.btn_close.set_tooltip`
- [ ] Lines 245-248: `screen.btn_category_*.set_tooltip` → `screen.panels.btn_category_*.set_tooltip`
- [ ] Check lines 218, 236 for dual-path mock wiring — simplify to direct `screen.panels.*`
- [ ] Run tests to verify

**Notes:** [Filled during implementation]

### Task 2.3: Update integration test - test_basics.py [Simple]
**File:** `tests/integration/ui/build_queue_screen/test_basics.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_basics.py -x`

- [ ] Lines 136-137: `build_queue_screen.planet_report` → `build_queue_screen.panels.planet_report`
- [ ] Lines 142-143: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [ ] Lines 148-149: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [ ] Lines 152-155: `build_queue_screen.btn_category_*` → `build_queue_screen.panels.btn_category_*`
- [ ] Lines 160-161: `build_queue_screen.btn_close` → `build_queue_screen.panels.btn_close`
- [ ] Update any `hasattr` checks to reference `panels.*` path
- [ ] Run tests to verify

**Notes:** [Filled during implementation]

### Task 2.4: Update integration test - test_build_queue_formatting.py [Simple]
**File:** `tests/integration/ui/test_build_queue_formatting.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_formatting.py -x`

- [ ] Line 141-142: `build_queue_screen.planet_report` → `build_queue_screen.panels.planet_report`
- [ ] Line 147: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [ ] Line 163: `build_queue_screen.build_queue_panel` → `build_queue_screen.panels.build_queue_panel`
- [ ] Line 179: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [ ] Line 197: `build_queue_screen.filter_panel` → `build_queue_screen.panels.filter_panel`
- [ ] Line 216: `build_queue_screen.items_list_panel` → `build_queue_screen.panels.items_list_panel`
- [ ] Lines 233-234: `build_queue_screen.design_report` → `build_queue_screen.panels.design_report`
- [ ] Run tests to verify

**Notes:** [Filled during implementation]

### Task 2.5: Update integration test - test_build_queue_drag_drop.py [Simple]
**File:** `tests/integration/ui/test_build_queue_drag_drop.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_drag_drop.py -x`

- [ ] Line 118: `build_queue_screen.items_scrollable` → `build_queue_screen.panels.items_scrollable`
- [ ] Line 157: `build_queue_screen.build_queue_panel` → `build_queue_screen.panels.build_queue_panel`
- [ ] Line 207: `build_queue_screen.queue_items` → `build_queue_screen.renderer.queue_items`
- [ ] Lines 232-233: `build_queue_screen.queue_scrollable` → `build_queue_screen.panels.queue_scrollable`
- [ ] Line 255: `build_queue_screen.queue_items` → `build_queue_screen.renderer.queue_items`
- [ ] Run tests to verify

**Notes:** [Filled during implementation]

### Task 2.6: Update integration test - test_queue_selector.py [Simple]
**File:** `tests/integration/ui/build_queue_screen/test_queue_selector.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_queue_selector.py -x`

- [ ] Line 374: `bq.queue_items` → `bq.renderer.queue_items`
- [ ] Run tests to verify

**Notes:** [Filled during implementation]

### Task 2.7: Delete backward-compat properties from BuildQueueScreen [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ -n 12` (full suite — critical deletion step)

- [ ] Delete section comment at lines 157-159 (`# Backward Compatibility Properties...`)
- [ ] Delete all 14 property definitions at lines 161-234
- [ ] Run full test suite to verify zero breakage
- [ ] Grep codebase for any remaining references to deleted properties

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (full suite)
- [ ] No references to deleted properties remain in codebase
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
