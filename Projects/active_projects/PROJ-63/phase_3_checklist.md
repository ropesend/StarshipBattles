# Phase 3: Extract BuildQueueController

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-63 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract queue business logic into `game/ui/panels/build_queue_controller.py`

---

## Tasks

### Task 3.1: Create BuildQueueController class [Medium]
**File:** `game/ui/panels/build_queue_controller.py` (NEW)
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_basics.py tests/integration/ui/test_build_queue_design_report.py`

- [ ] Create `game/ui/panels/build_queue_controller.py` with class `BuildQueueController`
- [ ] Constructor: `__init__(self, planet, design_library, design_loader, design_report, on_queue_changed)`
  - `planet`: Planet object whose construction_queue is managed
  - `design_library`: for scanning/loading designs
  - `design_loader`: SimulationDesignLoader for creating ship objects
  - `design_report`: DesignReportPanel for updating display
  - `on_queue_changed()`: callback to trigger queue display refresh
- [ ] Add state: `self.selected_category = "complex"` (moved from screen)
- [ ] Move `_load_designs_by_category(self, category)` from `build_queue_screen.py` (lines 316-348)
  - Rename to `load_designs_by_category(self, category)` (public)
- [ ] Move `_set_category(self, category)` from `build_queue_screen.py` (lines 574-578)
  - Rename to `set_category(self, category)` (public)
  - Calls `on_queue_changed` callback (screen refreshes items list)
- [ ] Move `_add_to_queue(self, design_id, turns, category, index)` from `build_queue_screen.py` (lines 580-626)
  - Rename to `add_to_queue(self, design_id, turns, category, index)` (public)
  - Keep all BUG-24 diagnostic logging
  - Calls `on_queue_changed` callback after modifying queue
- [ ] Move `_refresh_design_report(self, design_id)` from `build_queue_screen.py` (lines 628-664)
  - Rename to `refresh_design_report(self, design_id)` (public)
- [ ] Add necessary imports: `log_info`, `log_warning`, `log_error`, `log_debug` from `game.core.logger`

### Task 3.2: Wire BuildQueueController into BuildQueueScreen [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_basics.py`

- [ ] Add import: `from game.ui.panels.build_queue_controller import BuildQueueController`
- [ ] In `__init__`, create instance after design_report panel is created:
  ```python
  self.controller = BuildQueueController(
      planet=self.planet,
      design_library=self.design_library,
      design_loader=self.design_loader,
      design_report=self.design_report,
      on_queue_changed=self._refresh_queue_display
  )
  ```
- [ ] Remove `self.selected_category = "complex"` from screen `__init__`
- [ ] Update `_refresh_items_list()` to call `self.controller.load_designs_by_category(self.controller.selected_category)`
- [ ] Update `handle_event()` category button handlers to call `self.controller.set_category(...)`
- [ ] Update `handle_event()` add-to-queue button to call `self.controller.add_to_queue(...)`
- [ ] Update drag handler callbacks: `on_add_to_queue=self.controller.add_to_queue`, `on_refresh_design_report=self.controller.refresh_design_report`
- [ ] Delete moved methods: `_load_designs_by_category`, `_set_category`, `_add_to_queue`, `_refresh_design_report`
- [ ] Verify: No remaining references to deleted methods

### Task 3.3: Update tests if needed [Simple]
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_basics.py -v`

- [ ] Check if any tests call `screen._add_to_queue()` directly — update to `screen.controller.add_to_queue()`
- [ ] Check if any tests access `screen.selected_category` — update to `screen.controller.selected_category`
- [ ] Check if any tests call `screen._set_category()` — update to `screen.controller.set_category()`
- [ ] Run basics tests: `pytest tests/integration/ui/build_queue_screen/test_basics.py -v`
- [ ] Run design report tests: `pytest tests/integration/ui/test_build_queue_design_report.py -v`

### Task 3.4: Run full suite [Simple]
**Tests:** `pytest tests/ -x -q`

- [ ] Run full test suite: `pytest tests/ -x -q`
- [ ] Verify 6248 tests still pass
- [ ] Verify `build_queue_screen.py` is now under 500 lines (target: ~450 lines)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
