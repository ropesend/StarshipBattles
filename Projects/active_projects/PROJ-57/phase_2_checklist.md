<<<<<<< HEAD
# Phase 2: Extract Composite Nodes
=======
# Phase 2: Enhance Validation Layer
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

<<<<<<< HEAD
**Status:** Not Started
**Objective:** Extract the 2 composite classes that depend on leaf nodes, using relative intra-package imports
=======
**Status:** Complete
**Objective:** Add pod detection and chain validation to colonization validator
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Tasks

<<<<<<< HEAD
### Task 2.1: Extract ship_panels.py (ShipPanel + TabbedShipPanel + ComponentPanel) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 549-792
**New file:** `game/ui/screens/test_lab/ship_panels.py`
**Tests:** `python -c "from game.ui.screens.test_lab.ship_panels import ShipPanel, TabbedShipPanel, ComponentPanel"`

- [ ] Copy `ShipPanel` class (lines 549-588) to `ship_panels.py`
- [ ] Copy `TabbedShipPanel` class (lines 590-719) to `ship_panels.py`
- [ ] Copy `ComponentPanel` class (lines 721-792) to `ship_panels.py`
- [ ] Add intra-package imports:
  ```python
  from .json_viewer import ScrollableJSONViewer
  from .component_dropdown import ComponentDropdown
  ```
- [ ] Add external imports: `pygame`, constants
- [ ] Verify import works

**Notes:**

### Task 2.2: Extract results_panel.py (ResultsPanel) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 2000-2245
**New file:** `game/ui/screens/test_lab/results_panel.py`
**Tests:** `python -c "from game.ui.screens.test_lab.results_panel import ResultsPanel"`

- [ ] Copy `ResultsPanel` class (lines 2000-2245) to `results_panel.py`
- [ ] Add intra-package import:
  ```python
  from .test_run_card import TestRunCard
  ```
- [ ] Add external imports: `pygame`, constants
- [ ] Verify import works

**Notes:**

### Task 2.3: Verify composite extractions [Simple]
**Tests:** Import checks

- [ ] `python -c "from game.ui.screens.test_lab.ship_panels import ShipPanel, TabbedShipPanel, ComponentPanel"`
- [ ] `python -c "from game.ui.screens.test_lab.results_panel import ResultsPanel"`

**Notes:**
=======
### Task 2.1: Add Pod Detection Methods [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [x] Add static method `find_ship_with_colony_pod(fleet, planet_type_str, component_registry)`:
  - Iterate through `fleet.ships`
  - For each ship, iterate through design_data['layers']
  - Look up component in registry and check for ColonizePlanet ability
  - If ability exists and matches planet_type_str, return ship
  - Return None if not found
- [x] Add static method `get_available_colony_pods(fleet, component_registry) -> Dict[str, int]`:
  - Initialize empty dict `pod_counts = {}`
  - Iterate fleet.ships → design_data['layers'] → component registry lookups
  - Count pods by planet type
  - Return pod_counts dict
- [x] Add static method `get_committed_colony_pods(fleet) -> Dict[str, int]`:
  - Initialize empty dict `committed = {}`
  - Iterate through `fleet.orders`
  - For COLONIZE orders with target: count `order.target.planet_type.name`
  - Return committed dict
- [x] Verify: Methods compile, no syntax errors

**Notes:** Implemented using design_data pattern consistent with ShipStatsCalculator. Used component_registry parameter for DI rather than global lookup.

---

### Task 2.2: Modify validate() Method for Pod Checking [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [x] Modified `validate(galaxy, fleet, target_planet, component_registry=None)` to accept optional registry
- [x] After existing location/ownership checks, added pod validation block:
  - Check if fleet has a matching colony pod via find_ship_with_colony_pod()
  - Return NO_COLONY_POD error if not found
- [x] Added chain limit validation block:
  - Compare available_count vs committed_count
  - Return COLONY_POD_EXHAUSTED if committed >= available
- [x] Verify: Code compiles, logic flows correctly

**Notes:** Pod validation is optional (only when component_registry is provided). Backward compatible with existing callers.

---

### Task 2.3: Update Validation Tests [Medium]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py -v`

- [x] Add test: `test_validate_requires_matching_colony_pod()` - validates NO_COLONY_POD error
- [x] Add test: `test_validate_accepts_matching_colony_pod()` - validates success with matching pod
- [x] Add test: `test_validate_no_colony_pod_at_all()` - validates NO_COLONY_POD when fleet has no pods
- [x] Add test: `test_get_available_colony_pods()` - counts available pods correctly
- [x] Add test: `test_get_available_colony_pods_multiple_same_type()` - counts multiple same-type pods
- [x] Add test: `test_get_committed_colony_pods()` - counts committed pods from orders
- [x] Add test: `test_validate_rejects_overcommitted_pods()` - validates COLONY_POD_EXHAUSTED error
- [x] Add test: `test_validate_allows_different_pod_types_independently()` - pod types tracked separately
- [x] Run tests: `pytest tests/unit/strategy/validation/test_colonize_validator.py -v` - all pass
- [x] Verify: All 22 tests pass (14 existing + 8 new), no regressions

**Notes:** Added TestColonizeValidatorColonyPods test class. All existing tests continue to pass (backward compatible).
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Phase Completion Checklist
When all tasks above are done:
<<<<<<< HEAD
- [ ] All task checkboxes above are checked
- [ ] 7 module files now exist in `game/ui/screens/test_lab/` (5 leaf + 2 composite)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
=======
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/validation/ -v` - all tests pass (22 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
