# Phase 2: Extract Composite Nodes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-57 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract the 2 composite classes that depend on leaf nodes, using relative intra-package imports

---

## Tasks

### Task 2.1: Extract ship_panels.py (ShipPanel + TabbedShipPanel + ComponentPanel) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 549-792
**New file:** `game/ui/screens/test_lab/ship_panels.py`
**Tests:** `python -c "from game.ui.screens.test_lab.ship_panels import ShipPanel, TabbedShipPanel, ComponentPanel"`

- [x] Copy `ShipPanel` class (lines 549-588) to `ship_panels.py`
- [x] Copy `TabbedShipPanel` class (lines 590-719) to `ship_panels.py`
- [x] Copy `ComponentPanel` class (lines 721-792) to `ship_panels.py`
- [x] Add intra-package imports:
  ```python
  from .json_viewer import ScrollableJSONViewer
  from .component_dropdown import ComponentDropdown
  ```
- [x] Add external imports: `pygame`, constants
- [x] Verify import works

**Notes:**

### Task 2.2: Extract results_panel.py (ResultsPanel) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 2000-2245
**New file:** `game/ui/screens/test_lab/results_panel.py`
**Tests:** `python -c "from game.ui.screens.test_lab.results_panel import ResultsPanel"`

- [x] Copy `ResultsPanel` class (lines 2000-2245) to `results_panel.py`
- [x] Add intra-package import:
  ```python
  from .test_run_card import TestRunCard
  ```
- [x] Add external imports: `pygame`, constants
- [x] Verify import works

**Notes:**

### Task 2.3: Verify composite extractions [Simple]
**Tests:** Import checks

- [x] `python -c "from game.ui.screens.test_lab.ship_panels import ShipPanel, TabbedShipPanel, ComponentPanel"`
- [x] `python -c "from game.ui.screens.test_lab.results_panel import ResultsPanel"`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] 7 module files now exist in `game/ui/screens/test_lab/` (5 leaf + 2 composite)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
