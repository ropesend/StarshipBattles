# Phase 2: Entity & UI Test Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate test_ship.py, test_ship_factory.py, test_builder_ui_sync.py away from singleton hydration pattern

These tests use a pattern where `fresh_registries` data is copied INTO the singleton via `mgr.hydrate()`. This is backwards — the tests should pass `fresh_registries` directly via DI.

---

## Tasks

### Task 2.1: Migrate test_ship.py TestShip class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py::TestShip -v`

- [ ] Lines 24-30: Remove singleton hydration from `setup_and_teardown` — delete `mgr = RegistryManager.instance()` and `mgr.hydrate(...)` calls
- [ ] Verify all test methods already pass `registries=fresh_registries` to Ship/Component constructors
- [ ] Run tests

**Notes:**

### Task 2.2: Migrate test_ship.py TestShipClassMutation class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py::TestShipClassMutation -v`

- [ ] Lines 154-160: Remove singleton hydration from `setup_and_teardown`
- [ ] Run tests

**Notes:**

### Task 2.3: Migrate test_ship.py TestShipEdgeCases class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py::TestShipEdgeCases -v`

- [ ] Lines 371-376: Remove singleton hydration from `setup_and_teardown`
- [ ] Run tests

**Notes:**

### Task 2.4: Migrate test_ship.py TestTotalDefenseScoreInitialization class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py::TestTotalDefenseScoreInitialization -v`

- [ ] Lines 405-410: Remove singleton hydration from `setup_and_teardown`
- [ ] Run tests

**Notes:**

### Task 2.5: Migrate test_ship_factory.py [Medium]
**File:** `tests/unit/ui/services/test_ship_factory.py`
**Tests:** `pytest tests/unit/ui/services/test_ship_factory.py -v`

- [ ] Lines 21-26: TestShipFactory.setup — remove `mgr = RegistryManager.instance()` and `mgr.hydrate(...)`
- [ ] Lines 176-181: TestShipFactoryStaticMethods.setup — same removal
- [ ] Lines 214-219: TestSetupFormationEdgeCases.setup — same removal
- [ ] Remove `from game.core.registry import RegistryManager` import (line 11) if no longer needed
- [ ] Run tests

**Notes:**

### Task 2.6: Migrate test_builder_ui_sync.py [Medium]
**File:** `tests/unit/builder/test_builder_ui_sync.py`
**Tests:** `pytest tests/unit/builder/test_builder_ui_sync.py -v`

- [ ] Lines 29-35: Remove `mgr = RegistryManager.instance()` and `mgr.hydrate(...)` from `setup_ui`
- [ ] Store `fresh_registries` as `self.registries` in setup for method access
- [ ] Line 108: Replace `classes = RegistryManager.instance().vehicle_classes` with `classes = self.registries.vehicle_classes`
- [ ] Line 151: Replace `RegistryManager.instance().vehicle_classes.items()` with `self.registries.vehicle_classes.items()`
- [ ] Line 195: Replace `RegistryManager.instance().vehicle_classes.get(opt_val)` with `self.registries.vehicle_classes.get(opt_val)`
- [ ] Remove `from game.core.registry import RegistryManager` import (line 12)
- [ ] Run tests

**Notes:**

### Task 2.7: Clean up imports [Simple]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -v`

- [ ] Remove `from game.core.registry import RegistryManager` import (line 13) if no longer used anywhere in the file
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/entities/ tests/unit/ui/services/ tests/unit/builder/test_builder_ui_sync.py` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
