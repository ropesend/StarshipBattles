# Phase 2: Update Stats, Combat, Validation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Convert the simulation layer — stats calculation, damage calculator, ship validator, vehicle design service — from dict access to LayerData attribute access.

---

## Tasks

### Task 2.1: Update ShipStatsCalculator [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py tests/unit/simulation/systems/test_ship_stats_calculator_phases.py -x`

- [x] Add import: `from game.simulation.entities.layer_data import LayerData`
- [x] Line ~83-85: Mass calculation loop — `layer_data['components']` → `.components`, `layer_data['mass'] = l_mass` → `.mass = l_mass`
- [x] Line ~117-118: Armor HP pool reset — `ship.layers[LayerType.ARMOR]['max_hp_pool'] = 0` → `.max_hp_pool = 0`
- [x] Line ~276: Armor HP pool accumulation — `ship.layers[LayerType.ARMOR]['max_hp_pool'] += comp.max_hp` → `.max_hp_pool += comp.max_hp`
- [x] Lines ~410-413: HP pool initialization — `ship.layers[LayerType.ARMOR]['hp_pool']` → `.hp_pool`, `['max_hp_pool']` → `.max_hp_pool`
- [x] Line ~441: Any `.get()` calls → direct attribute access
- [x] Search entire file for any remaining `['` string-key access patterns and convert
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 2.2: Update DamageCalculator [Simple]
**File:** `game/simulation/combat/damage_calculator.py`
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator.py tests/unit/combat/ -x`

- [x] Sort lambda: `x[1]['radius_pct']` → `x[1].radius_pct`
- [x] Component access: `layer['components']` → `layer.components`
- [x] Search entire file for any remaining dict-style layer access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 2.3: Update ShipValidator [Simple]
**File:** `game/simulation/validation/ship_validator.py`
**Tests:** `pytest tests/unit/simulation/test_layer_restriction_rule_refactor.py tests/unit/systems/test_layer_restrictions_refactor.py tests/unit/systems/test_mount_validation.py -x`

- [x] `layer_data['components']` → `layer_data.components`
- [x] Search entire file for any remaining dict-style layer access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 2.4: Update VehicleDesignService [Simple]
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/ -k "design" -x`

- [x] Any `.get()` layer access → attribute access
- [x] Any `['key']` layer access → `.key` attribute access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 2.5: Incremental test run [Simple]
**Tests:** `pytest tests/unit/entities/ tests/unit/combat/ tests/unit/simulation/ -x`

- [x] Run combined test suite for Phase 2 scope
- [x] Fix any failures discovered
- [x] Verify all pass

**Notes:** 157 tests passed during Phase 2-7 verification.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
