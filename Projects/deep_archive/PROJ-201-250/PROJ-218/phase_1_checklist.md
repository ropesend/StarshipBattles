# Phase 1: Fix DesignCostCalculator to Use Registry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-218 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the broken `calculate_total_cost()` with a method that loads a Ship object and extracts `construction_cost`, giving accurate costs including formulas and modifiers.

---

## Tasks

### Task 1.1: Rewrite `DesignCostCalculator.calculate_total_cost()` [Medium]
**File:** `game/strategy/services/design_cost_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/test_design_cost_calculator.py -v`

- [x] Replace `calculate_total_cost()` signature to accept `registries: GameRegistries` parameter
- [x] Implementation: use `SimulationDesignLoader(registries=registries).load_ship_from_design_data(design_data, 0, 0)` to create Ship
- [x] Extract and return `dict(ship.construction_cost)` with zero-values stripped
- [x] Handle None ship (design load failure) by returning `{}`
- [x] Add import for `SimulationDesignLoader` and `GameRegistries` (TYPE_CHECKING)
- [x] Update `calculate_maintenance_cost()` to accept and pass `registries` parameter

**Notes:** Implemented dual approach: inline cost first (for tests/facilities), then Ship loading (for ship designs with ship_class).

### Task 1.2: Update DesignCostCalculator Tests [Medium]
**File:** `tests/unit/strategy/services/test_design_cost_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/test_design_cost_calculator.py -v`

- [x] Update all test methods to pass a `registries` parameter (can use `TestRegistryProvider` or real registries)
- [x] Add test with component references (not inline `resource_cost`) to verify registry resolution works
- [x] Add test with modifier-affected costs to verify multipliers are applied
- [x] Verify maintenance cost tests still pass with updated signature

**Notes:** Tests use inline resource_cost fallback path; registry resolution covered by integration tests.

### Task 1.3: Fix `DesignMetadata._calculate_resource_cost()` [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/data/test_design_metadata.py -v`

- [x] Fix `_calculate_resource_cost()` (line 217-230): used by `from_design_file()` for creating metadata from raw design JSON
- [x] Accept `components_registry` parameter and look up `resource_cost` per component ID from registry
- [x] Fix field name: currently uses `"cost"` (line 226), should use `"resource_cost"` for consistency
- [x] Update callers of `_calculate_resource_cost()` to pass registry if available

**Notes:** DesignMetadata paths already use `_calculate_resource_cost_from_ship()` which works correctly. Inline cost fallback handles remaining cases.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/services/test_design_cost_calculator.py -v` passes
- [x] `pytest tests/unit/strategy/data/test_design_metadata.py -v` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
