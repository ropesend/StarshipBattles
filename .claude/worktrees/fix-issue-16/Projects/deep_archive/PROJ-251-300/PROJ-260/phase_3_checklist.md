# Phase 3: Extract ShipResourceManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-260 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract resource management state and logic from Ship (and partially from ShipStatsCalculator) into a new ShipResourceManager delegate. TDD: tests first, then implementation. Ship retains facade methods/properties.

**Prerequisites:** Phase 2 complete. ShipLayerManager extracted and tested.

---

## Tasks

### Task 3.1: Write Tests for ShipResourceManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_resource_manager.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_resource_manager.py -v`

- [ ] Create test file with standard fixtures (ship factory using GameRegistries)
- [ ] Follow test patterns from `test_ship_component_manager.py` and `test_ship_combat_manager.py`
- [ ] `TestResourceManagerInit`:
  - [ ] Test ResourceRegistry created on construction
  - [ ] Test `_resources_initialized` starts as False
  - [ ] Test `_prev_max_resources` starts as empty dict
  - [ ] Test `_prev_max_shields` starts as 0
- [ ] `TestGetResourceStat`:
  - [ ] Test returns attribute value when it exists (e.g., `fuel_consumption`)
  - [ ] Test returns 0.0 when attribute does not exist
  - [ ] Test various stat_type suffixes: 'consumption', 'endurance', 'potential_consumption'
  - [ ] Test resource_name + stat_type concatenation produces correct attribute name
- [ ] `TestInitializeResources`:
  - [ ] Test first-time init fills all resources to max
  - [ ] Test first-time init sets shields to max_shields
  - [ ] Test `_resources_initialized` is True after first init
  - [ ] Test subsequent init preserves current resource values
  - [ ] Test capacity increase adds delta to current values
  - [ ] Test shield capacity increase adds delta to current shields
  - [ ] Test current_shields capped when max_shields decreases
  - [ ] Test `_prev_max_resources` updated after each init call
  - [ ] Test `_prev_max_shields` updated after each init call
- [ ] `TestResourceConsumptionAttrs`:
  - [ ] Test fuel_consumption defaults to 0.0
  - [ ] Test ammo_consumption defaults to 0.0
  - [ ] Test energy_consumption defaults to 0.0
  - [ ] Test potential_* consumption attrs default to 0.0
  - [ ] Test attrs can be set and read back
- [ ] `TestShipFacadeIntegration`:
  - [ ] Test `ship.resources` returns the ResourceRegistry from the manager
  - [ ] Test `ship.get_resource_stat()` delegates to resource manager
  - [ ] Test `ship.resource_manager` is lazily initialized
- [ ] Run tests -- confirm they ALL FAIL (ShipResourceManager doesn't exist yet)

**Notes:** Exact test cases may be adjusted based on Phase 1 findings. The `initialize_resources` tests need a ship with components that provide resource storage (use the standard test fixtures).

---

### Task 3.2: Implement ShipResourceManager [Medium]
**File:** `game/simulation/entities/ship_resource_manager.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_resource_manager.py -v`

- [ ] Create `ship_resource_manager.py` with class docstring following delegate convention
- [ ] Implement `__init__(self, ship: 'Ship')`:
  - Create `self.registry = ResourceRegistry()`
  - Initialize `self._resources_initialized = False`
  - Initialize `self._prev_max_resources = {}`
  - Initialize `self._prev_max_shields = 0`
  - Initialize resource consumption attributes (fuel, ammo, energy + potential)
- [ ] Implement `get_resource_stat(resource_name, stat_type) -> float`:
  - Build attribute name from `f'{resource_name}_{stat_type}'`
  - Return `getattr(self, attr_name, 0.0)` -- check self first, then ship for compat
- [ ] Implement `initialize_resources(ship)`:
  - Move logic from `ShipStatsCalculator._initialize_resources()` here
  - Reads: `ship.max_shields`, `ship.current_shields`
  - Writes: `ship.current_shields` (shield capping)
  - Uses: `self.registry`, `self._resources_initialized`, `self._prev_max_resources`, `self._prev_max_shields`
- [ ] Run tests -- confirm they ALL PASS
- [ ] Verify: `wc -l game/simulation/entities/ship_resource_manager.py` (expect 80-130 lines)

**Notes:** The `initialize_resources()` method signature must be compatible with how ShipStatsCalculator calls it. Phase 1 caller trace determines the exact interface.

---

### Task 3.3: Wire Ship to ShipResourceManager [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_resource_manager.py tests/unit/entities/test_ship.py -v`

- [ ] Add `_resource_manager` to Ship.__init__ (lazy init)
- [ ] Add `resource_manager` property with lazy initialization
- [ ] Replace `self.resources = ResourceRegistry()` with delegation to resource_manager
- [ ] Add `resources` property that returns `self.resource_manager.registry`
- [ ] Remove `_resources_initialized`, `_prev_max_resources`, `_prev_max_shields` from Ship.__init__
- [ ] Replace `get_resource_stat()` body with delegation
- [ ] Move resource consumption attrs to resource_manager (add facade properties if needed)
- [ ] Run resource manager tests -- confirm still passing
- [ ] Run full Ship tests -- confirm no regressions: `pytest tests/unit/entities/test_ship.py -v`
- [ ] Run resource stat tests -- confirm no regressions: `pytest tests/unit/simulation/entities/test_ship_resource_stat.py -v`

**Notes:** `ship.resources` must continue to work as a direct attribute access for backward compatibility. The property approach achieves this transparently.

---

### Task 3.4: Update ShipStatsCalculator [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/systems/test_ship_stats_calculator_phases.py -v`

- [ ] Replace `ShipStatsCalculator._initialize_resources()` body:
  - Change from direct Ship attribute manipulation to `ship.resource_manager.initialize_resources(ship)`
  - Or remove `_initialize_resources()` entirely if it just delegates
- [ ] Verify ShipStatsCalculator still calls `ship.resources.reset_stats()` correctly
- [ ] Verify ShipStatsCalculator still calls `ship.resources.register_storage()` and `register_generation()` via `_apply_aggregated_stats()`
- [ ] Run stats calculator tests -- confirm no regressions
- [ ] Run combat endurance tests (if they exist): `pytest tests/ -k "combat_endurance" -v`

**Notes:** The key change is that `_initialize_resources()` no longer reaches into Ship's private attributes (`_prev_max_resources`, etc.) because those now live on the resource manager.

---

### Task 3.5: Run Broader Test Suite [Simple]
**Tests:** Multiple test directories

- [ ] Run all simulation entity tests: `pytest tests/unit/simulation/entities/ -v`
- [ ] Run all simulation system tests: `pytest tests/unit/simulation/systems/ -v`
- [ ] Run all entity tests: `pytest tests/unit/entities/ -v`
- [ ] Run combat manager tests: `pytest tests/unit/simulation/entities/test_ship_combat_manager.py -v`
- [ ] Run all strategy tests that touch resources: `pytest tests/unit/strategy/ -v`
- [ ] Fix any failures (should be zero if facade properties work correctly)
- [ ] Note Ship.py line count after this phase

**Notes:** Resource access is widespread -- the broader test suite is critical here.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ship_resource_manager.py` exists with full implementation
- [ ] `test_ship_resource_manager.py` exists with all tests passing
- [ ] Ship.py delegates resource logic to ShipResourceManager
- [ ] ShipStatsCalculator updated to use resource manager
- [ ] Zero test regressions across broader suite
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
