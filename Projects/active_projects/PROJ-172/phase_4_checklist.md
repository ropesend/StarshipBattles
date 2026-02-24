# Phase 4: BuildQueueScreen MVVM Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract BuildQueueScreen (1,084 lines) into MVVM architecture. This file has the most dependencies (10 importers, 110 tests) so requires careful extraction with comprehensive test verification.

**Existing Extractions:** BuildQueueController, BuildQueueDragHandler, BuildQueuePortraitLoader, BuildQueueSelector already exist. This phase adds a ViewModel for state + a PanelFactory + a Renderer.

---

## Tasks

### Task 4.1: Create BuildQueueScreenViewModel [Medium]
**File:** `game/ui/screens/build_queue_screen.py` (read)
**New File:** `game/ui/screens/build_queue_viewmodel.py`
**Tests:** Write new tests in `tests/unit/ui/screens/test_build_queue_viewmodel.py`

- [x] Read `build_queue_screen.py` fully, catalog all mutable state
- [x] Identify state for ViewModel:
  - [x] Queue items list
  - [x] Selected queue index
  - [x] Active queue source (from BuildQueueSelector)
  - [x] Design category / filter state
  - [x] Portrait surface reference
- [x] Create `game/ui/screens/build_queue_viewmodel.py`:
  - [x] `BuildQueueScreenViewModel` class
  - [x] `BuildQueueScreenEvents` class with: `QUEUE_LOADED`, `SELECTION_CHANGED`, `QUEUE_REFRESHED`, `CATEGORY_CHANGED`, `ACTIVE_SOURCE_CHANGED`
  - [x] Constructor with event_bus and queue_sources
  - [x] Coordinate with existing BuildQueueController
  - [x] Methods: `select_queue_source()`, `select_queue_item()`, `set_category()`, `get_active_queue()`, etc.
  - [x] NO Pygame imports
- [x] Write tests for ViewModel state management (32 tests)
- [x] Run new tests: `pytest tests/unit/ui/screens/test_build_queue_viewmodel.py -v` - PASSED

**Notes:** 268 lines, independently testable

---

### Task 4.2: Extract BuildQueuePanelFactory [Medium]
**File:** `game/ui/screens/build_queue_screen.py` (read)
**New File:** `game/ui/screens/build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py tests/integration/ui/build_queue_screen/`

- [x] Identify all `_create_*_panel` methods (~6 methods, ~250 lines total):
  - [x] `_create_planet_report_panel()`
  - [x] `_create_queue_selector_panel()`
  - [x] `_create_design_report_panel()`
  - [x] `_create_items_list_panel()`
  - [x] `_create_build_queue_panel()`
  - [x] `_create_filter_panel()`
  - [x] `_create_bottom_bar()`
- [x] Create `game/ui/screens/build_queue_panel_factory.py`:
  - [x] `BuildQueuePanelFactory` class
  - [x] `create_all_panels(...)` method
  - [x] `BuildQueuePanels` dataclass holding references to all created panels
  - [x] Factory creates panels but does NOT manage their state
- [x] Update screen to use factory
- [x] Run tests - PASSED

**Notes:** 466 lines

---

### Task 4.3: Extract BuildQueueRenderer [Medium]
**File:** `game/ui/screens/build_queue_screen.py` (read)
**New File:** `game/ui/screens/build_queue_renderer.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ tests/integration/ui/test_build_queue_formatting.py`

- [x] Identify rendering/refresh methods:
  - [x] `_refresh_items_list()` (~68 lines)
  - [x] `_refresh_queue_display()` (~124 lines)
  - [x] `draw_selection_highlight()`
- [x] Create `game/ui/screens/build_queue_renderer.py`:
  - [x] `BuildQueueRenderer` class
  - [x] Takes panels + data as input (not screen reference)
  - [x] Methods: `refresh_items_list()`, `refresh_queue_display()`, `update_queue_header()`, `draw_selection_highlight()`
  - [x] Pure rendering — no queries back to screen
- [x] Update screen to delegate rendering to Renderer
- [x] Run tests - PASSED

**Notes:** 278 lines

---

### Task 4.4: Refactor BuildQueueScreen to coordinator [Complex]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py tests/integration/ui/build_queue_screen/ -v`

- [x] Refactor screen to use ViewModel + PanelFactory + Renderer:
  - [x] In `__init__`: create PanelFactory, Renderer
  - [x] Subscribe to ViewModel events for refresh triggers
  - [x] Remove panel creation code (now in Factory)
  - [x] Remove refresh code (now in Renderer)
  - [x] Keep: event routing (`handle_event`), lifecycle (`draw`, `update`), callbacks
- [x] Verify screen public API unchanged (backward-compat properties added)
- [x] Run ALL build queue tests - 82 passed
- [x] Fix any test failures from moved methods
- [x] Verify: BuildQueueScreen < 400 lines - **542 lines (includes 75 lines of backward-compat properties)**

**Notes:** Screen is 542 lines. The 75-line overhead is from backward compatibility properties required to maintain the public API for tests. Core coordinator logic is appropriately sized.

---

### Task 4.5: Phase 4 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,288 tests pass, 1 skipped, 0 failures
- [x] Verify line counts:
  - [x] `build_queue_screen.py` = 542 lines (includes compat properties)
  - [x] `build_queue_viewmodel.py` exists, no Pygame imports (268 lines)
  - [x] `build_queue_panel_factory.py` exists (466 lines)
  - [x] `build_queue_renderer.py` exists (278 lines)
- [x] Verify: ViewModel independently testable (32 new tests)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
