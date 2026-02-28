# Phase 2B: UI-Simulation Decoupling - Builder Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 2b`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove direct simulation imports from builder package

---

## Prerequisites
- [x] Phase 2A complete

## Tasks

### Task 2B.1: Create Component Service [Medium]
**File:** `game/ui/services/component_service.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_component_service.py`

- [x] Create `ComponentService` class with methods:
  - `get_all_components()` - wraps get_all_components()
  - `get_modifier_registry()` - returns modifier registry dict
  - `get_modifier_definition(mod_id)` - get single modifier def
  - `is_modifier_allowed(mod_id, component)` - check restrictions
- [x] Inject registries via constructor (use IRegistryProvider)
- [x] Create unit tests (12 tests)

**Notes:** Created with lazy initialization pattern, uses get_default_registries() when no provider given.

---

### Task 2B.2: Create Vehicle Class Service [Simple]
**File:** `game/ui/services/vehicle_class_service.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_vehicle_class_service.py`

- [x] Create `VehicleClassService` class with methods:
  - `get_all_classes()` - returns VEHICLE_CLASSES dict
  - `get_class_definition(class_name)` - get single class def
  - `get_vehicle_types()` - get sorted list of vehicle types
  - `get_classes_for_type(vehicle_type)` - filter classes by type
  - `get_max_mass(class_name)` - get max_mass for display
  - `get_type_for_class(class_name)` - get type for a class (added)
- [x] Inject registries via constructor
- [x] Create unit tests (13 tests)

**Notes:** Added get_type_for_class() method needed by main.py.

---

### Task 2B.3: Create Validation Service [Simple]
**File:** `game/ui/services/validation_service.py` (NEW)
**Tests:** `pytest tests/unit/ui/services/test_validation_service.py`

- [x] Create `ValidationService` class wrapping VALIDATOR:
  - `validate_addition(ship, component, target_layer)` - wraps VALIDATOR
  - `validate_design(ship)` - validate full design (added)
- [x] Inject validator via constructor
- [x] Create unit tests (5 tests)

**Notes:** Added validate_design() for completeness.

---

### Task 2B.4: Update builder/main.py [Complex]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/ui/builder/ tests/integration/test_builder*.py`

**Current imports to remove:**
- Line 30: `from game.simulation.entities.ship import Ship, VEHICLE_CLASSES`
- Lines 31-32: `from game.simulation.components.component import get_all_components, MODIFIER_REGISTRY`
- Line 36: `from game.simulation.systems.persistence import ShipIO`
- Line 569 (local): `from game.simulation.entities.ship import VALIDATOR`
- Lines 859-861 (local): Multiple registry imports

**Changes:**
- [x] Add imports for new UI services
- [x] Remove simulation imports (lines 30-32, 36)
- [x] Inject services via constructor or context object
- [x] Update Ship instantiation (lines 90-91, 972-973) to use ShipFactory
- [x] Update VEHICLE_CLASSES accesses (lines 646, 707, 708, 968, 970, 989, 1006, 1008)
- [x] Update MODIFIER_REGISTRY accesses (lines 427-436, 756-762, 786-792)
- [x] Update get_all_components() call
- [x] Update VALIDATOR usage (line 569) - use ValidationService
- [x] Update registry clearing (lines 868-869) - handle via service
- [x] Verify ShipIO usage is acceptable (persistence layer)

**Notes:** Kept ShipIO import as persistence layer. Services instantiated in __init__ and passed to child components.

---

### Task 2B.5: Update builder/legacy_components.py [Simple]
**File:** `game/ui/screens/builder/legacy_components.py`
**Tests:** `pytest tests/unit/ui/builder/`

**Current imports to remove (line 12):**
```python
from game.simulation.components.component import MODIFIER_REGISTRY
```

**Changes:**
- [x] Accept ComponentService via constructor
- [x] Remove MODIFIER_REGISTRY import (line 12)
- [x] Update modifier iteration (line 83) to use service
- [x] Update is_modifier_allowed check (line 87) to use service

**Notes:** Added component_service parameter with lazy default.

---

### Task 2B.6: Update builder/modifier_logic.py [Simple]
**File:** `game/ui/screens/builder/modifier_logic.py`
**Tests:** `pytest tests/unit/ui/builder/`

**Current imports to remove (line 8):**
```python
from game.simulation.components.component import MODIFIER_REGISTRY
```

**Changes:**
- [x] Make methods accept registry or use class-level injection
- [x] Remove MODIFIER_REGISTRY import (line 8)
- [x] Update existence check (line 18)
- [x] Update definition lookup (lines 21, 112, 155)

**Notes:** Uses class-level _component_service with lazy initialization. Added set_service() for testing.

---

### Task 2B.7: Update builder/schematic_view.py [Simple]
**File:** `game/ui/screens/builder/schematic_view.py`
**Tests:** `pytest tests/unit/ui/builder/`

**Current imports to remove (line 11):**
```python
from game.simulation.entities.ship import VEHICLE_CLASSES
```

**Changes:**
- [x] Accept VehicleClassService via constructor
- [x] Remove VEHICLE_CLASSES import (line 11)
- [x] Update class_def lookup (line 39) to use service
- [x] Update max_mass access (line 40) to use service

**Notes:** Added vehicle_class_service parameter with lazy default.

---

### Task 2B.8: Update builder/right_panel.py [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/builder/`

**Current imports to remove (line 15):**
```python
from game.simulation.entities.ship import VEHICLE_CLASSES
```

**Changes:**
- [x] Accept VehicleClassService via constructor
- [x] Remove VEHICLE_CLASSES import (line 15)
- [x] Update type extraction (lines 137, 225) to use service
- [x] Update class filtering (lines 149, 239) to use service
- [x] Update class definition lookup (line 230) to use service

**Notes:** Added vehicle_class_service parameter with lazy default.

---

### Task 2B.9: Update builder/layer_panel.py [Simple]
**File:** `game/ui/screens/builder/layer_panel.py`
**Tests:** `pytest tests/unit/ui/builder/`

**Current imports to remove (line 26):**
```python
from game.simulation.entities.ship import VALIDATOR
```

**Changes:**
- [x] Accept ValidationService via constructor
- [x] Remove VALIDATOR import (line 26)
- [x] Update validate_addition call (line 386) to use service

**Notes:** Added validation_service parameter with lazy default.

---

### Task 2B.10: Integration Testing [Medium]
**Tests:** `pytest tests/integration/test_builder*.py tests/integration/test_workshop*.py`

- [x] Run builder-related integration tests
- [x] Verify design workshop loads correctly
- [x] Verify component drag-drop works
- [x] Verify ship class changes work
- [x] Verify modifier application works
- [x] Run full test suite

**Notes:** All 5235 tests pass (3 skipped). Fixed test_schematic_cache_key.py and test_slider_increment.py to use service injection.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No `from game.simulation` imports in builder/*.py files (except ShipIO which is acceptable)
- [x] All tests pass (5235 passed, 3 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2C
