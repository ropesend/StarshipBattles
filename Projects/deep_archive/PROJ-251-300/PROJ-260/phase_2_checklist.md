# Phase 2: Extract ShipLayerManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-260 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract layer initialization and management logic from Ship into a new ShipLayerManager delegate. TDD: tests first, then implementation. Ship retains facade methods.

**Prerequisites:** Phase 1 complete. Extraction plan finalized in `findings/phase_1_extraction_plan.md`.

---

## Tasks

### Task 2.1: Write Tests for ShipLayerManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_layer_manager.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_layer_manager.py -v`

- [ ] Create test file with standard fixtures (ship factory using GameRegistries)
- [ ] Follow test patterns from `test_ship_component_manager.py`
- [ ] `TestInitializeLayers`:
  - [ ] Test layers created from vehicle class definition (standard ship_class)
  - [ ] Test HULL layer always present with `create_hull()` defaults
  - [ ] Test fallback layer definitions when vehicle class has no 'layers' key
  - [ ] Test unknown LayerType string is skipped with warning (not error)
  - [ ] Test layer radius recalculation (area-proportional to mass capacity)
  - [ ] Test HULL layer radius is always 0.0
  - [ ] Test layers dict has correct LayerType keys for standard vehicle class
- [ ] `TestEquipDefaultHull`:
  - [ ] Test default hull component is created and added to HULL layer
  - [ ] Test hull component has correct layer_assigned and ship reference
  - [ ] Test no hull added when class_def has no 'default_hull_id'
  - [ ] Test warning logged when hull component creation fails
- [ ] `TestLayerManagerIntegration`:
  - [ ] Test `_initialize_layers()` on Ship delegates to ShipLayerManager
  - [ ] Test `_equip_default_hull()` on Ship delegates to ShipLayerManager
  - [ ] Test full init flow: Ship() creates layers and equips hull
- [ ] Run tests -- confirm they ALL FAIL (ShipLayerManager doesn't exist yet)

**Notes:** Exact test cases may be adjusted based on Phase 1 findings. If `change_class()` moves to ShipLayerManager, add tests for that too.

---

### Task 2.2: Implement ShipLayerManager [Medium]
**File:** `game/simulation/entities/ship_layer_manager.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_layer_manager.py -v`

- [ ] Create `ship_layer_manager.py` with class docstring following delegate convention
- [ ] Implement `__init__(self, ship: 'Ship')` storing ship reference
- [ ] Move `_initialize_layers()` logic from Ship to `initialize_layers()`:
  - Read vehicle class from `ship._registries.vehicle_classes`
  - Build `ship.layers` dict with LayerData instances
  - Force HULL layer via `LayerData.create_hull()`
  - Handle fallback layer definitions
  - Recalculate layer radii (area-proportional)
- [ ] Move `_equip_default_hull()` logic to `equip_default_hull(class_def)`:
  - Create hull component via `create_component()`
  - Append to HULL layer, set layer_assigned and ship reference
- [ ] If Phase 1 determined `change_class()` moves here, implement `change_class()`:
  - Save old components if migrating
  - Update ship identity attributes (ship_class, vehicle_type, max_mass_budget)
  - Call `initialize_layers()` and `equip_default_hull()`
  - Restore components if migrating
  - Call `ship.recalculate_stats()`
- [ ] Run tests -- confirm they ALL PASS
- [ ] Verify: `wc -l game/simulation/entities/ship_layer_manager.py` (expect 80-150 lines)

**Notes:** Method signatures determined by Phase 1 analysis.

---

### Task 2.3: Wire Ship to ShipLayerManager [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_layer_manager.py tests/unit/entities/test_ship.py -v`

- [ ] Add `_layer_manager` to Ship.__init__ (lazy or eager, per Phase 1 decision)
- [ ] Add `layer_manager` property with lazy initialization (if not eager)
- [ ] Replace `_initialize_layers()` body with delegation: `self.layer_manager.initialize_layers()`
- [ ] Replace `_equip_default_hull()` body with delegation: `self.layer_manager.equip_default_hull(class_def)`
- [ ] If `change_class()` moved, replace body with delegation
- [ ] Remove extracted implementation code from Ship (leave only facade methods)
- [ ] Run layer manager tests -- confirm still passing
- [ ] Run full Ship tests -- confirm no regressions: `pytest tests/unit/entities/test_ship.py -v`
- [ ] Run component manager tests -- confirm no regressions: `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`
- [ ] Run serialization tests -- confirm no regressions: `pytest tests/unit/simulation/entities/test_ship_serialization.py -v`

**Notes:** Ship must remain the public API -- `_initialize_layers()` and `_equip_default_hull()` stay as methods on Ship that delegate.

---

### Task 2.4: Run Broader Test Suite [Simple]
**Tests:** Multiple test directories

- [ ] Run all simulation entity tests: `pytest tests/unit/simulation/entities/ -v`
- [ ] Run all builder tests: `pytest tests/unit/builder/ -v`
- [ ] Run all entity tests: `pytest tests/unit/entities/ -v`
- [ ] Run stats calculator tests: `pytest tests/unit/simulation/systems/test_ship_stats_calculator_phases.py -v`
- [ ] Fix any failures (should be zero if delegation is correct)
- [ ] Note Ship.py line count after this phase

**Notes:** Record line count in findings for tracking toward <500 goal.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ship_layer_manager.py` exists with full implementation
- [ ] `test_ship_layer_manager.py` exists with all tests passing
- [ ] Ship.py delegates layer logic to ShipLayerManager
- [ ] Zero test regressions across broader suite
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
