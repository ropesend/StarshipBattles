# Phase 4: BuildQueueScreen MVVM Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract BuildQueueScreen (1,084 lines) into MVVM architecture. This file has the most dependencies (10 importers, 110 tests) so requires careful extraction with comprehensive test verification.

**Existing Extractions:** BuildQueueController, BuildQueueDragHandler, BuildQueuePortraitLoader, BuildQueueSelector already exist. This phase adds a ViewModel for state + a PanelFactory + a Renderer.

---

## Tasks

### Task 4.1: Create BuildQueueScreenViewModel [Medium]
**File:** `game/ui/screens/build_queue_screen.py` (read)
**New File:** `game/ui/screens/build_queue_viewmodel.py`
**Tests:** Write new tests in `tests/unit/ui/screens/test_build_queue_viewmodel.py`

- [ ] Read `build_queue_screen.py` fully, catalog all mutable state
- [ ] Identify state for ViewModel:
  - [ ] Queue items list
  - [ ] Selected queue index
  - [ ] Active queue source (from BuildQueueSelector)
  - [ ] Design category / filter state
  - [ ] Portrait surface reference
- [ ] Create `game/ui/screens/build_queue_viewmodel.py`:
  - [ ] `BuildQueueScreenViewModel` class
  - [ ] `BuildQueueScreenEvents` class with: `QUEUE_LOADED`, `SELECTION_CHANGED`, `DESIGN_SELECTED`, `QUEUE_REFRESHED`
  - [ ] Constructor: `__init__(self, event_bus, build_context, session, galaxy, empire)`
  - [ ] Coordinate with existing BuildQueueController
  - [ ] Methods: `load_queue()`, `select_item(index)`, `add_to_queue(design)`, `remove_from_queue(index)`
  - [ ] NO Pygame imports
- [ ] Write tests for ViewModel state management
- [ ] Run new tests: `pytest tests/unit/ui/screens/test_build_queue_viewmodel.py -v`

**Notes:**

---

### Task 4.2: Extract BuildQueuePanelFactory [Medium]
**File:** `game/ui/screens/build_queue_screen.py` (read)
**New File:** `game/ui/screens/build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py tests/integration/ui/build_queue_screen/`

- [ ] Identify all `_create_*_panel` methods (~6 methods, ~250 lines total):
  - [ ] `_create_planet_report_panel()`
  - [ ] `_create_queue_selector_panel()`
  - [ ] `_create_design_report_panel()`
  - [ ] `_create_items_list_panel()`
  - [ ] `_create_build_queue_panel()`
  - [ ] `_create_filter_panel()`
  - [ ] `_create_bottom_bar()`
- [ ] Create `game/ui/screens/build_queue_panel_factory.py`:
  - [ ] `BuildQueuePanelFactory` class
  - [ ] `create_all_panels(ui_manager, rect, viewmodel, ...) -> PanelCollection` method
  - [ ] `PanelCollection` dataclass holding references to all created panels
  - [ ] Factory creates panels but does NOT manage their state
- [ ] Update screen to use factory:
  ```python
  self.panels = BuildQueuePanelFactory.create_all_panels(self.manager, ...)
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_build_queue_screen.py tests/integration/ui/build_queue_screen/ -v`

**Notes:**

---

### Task 4.3: Extract BuildQueueRenderer [Medium]
**File:** `game/ui/screens/build_queue_screen.py` (read)
**New File:** `game/ui/screens/build_queue_renderer.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_formatting.py`

- [ ] Identify rendering/refresh methods:
  - [ ] `_refresh_items_list()` (~68 lines)
  - [ ] `_refresh_queue_display()` (~124 lines)
  - [ ] `_refresh_queue_selector()` (delegation)
  - [ ] `_apply_tooltips()`
- [ ] Create `game/ui/screens/build_queue_renderer.py`:
  - [ ] `BuildQueueRenderer` class
  - [ ] Takes panels + ViewModel data as input (not screen reference)
  - [ ] Methods: `refresh_items_list(panels, viewmodel_data)`, `refresh_queue_display(panels, queue_data)`
  - [ ] Pure rendering — no queries back to screen
- [ ] Update screen to delegate rendering to Renderer
- [ ] Run tests: `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_formatting.py -v`

**Notes:**

---

### Task 4.4: Refactor BuildQueueScreen to coordinator [Complex]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py tests/integration/ui/build_queue_screen/ -v`

- [ ] Refactor screen to use ViewModel + PanelFactory + Renderer:
  - [ ] In `__init__`: create EventBus, ViewModel, PanelFactory, Renderer
  - [ ] Subscribe to ViewModel events for refresh triggers
  - [ ] Remove panel creation code (now in Factory)
  - [ ] Remove refresh code (now in Renderer)
  - [ ] Remove queue state (now in ViewModel)
  - [ ] Keep: event routing (`handle_event`), lifecycle (`draw`, `update`), callbacks
- [ ] Verify screen public API unchanged
- [ ] Run ALL build queue tests:
  ```
  pytest tests/unit/ui/screens/test_build_queue_screen.py tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_drag_drop.py tests/integration/ui/test_build_queue_formatting.py -v
  ```
- [ ] Fix any test failures from moved methods
- [ ] Verify: BuildQueueScreen < 400 lines

**Notes:**

---

### Task 4.5: Phase 4 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `build_queue_screen.py` < 400 lines
  - [ ] `build_queue_viewmodel.py` exists, no Pygame imports
  - [ ] `build_queue_panel_factory.py` exists
  - [ ] `build_queue_renderer.py` exists
- [ ] Verify: ViewModel independently testable

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
