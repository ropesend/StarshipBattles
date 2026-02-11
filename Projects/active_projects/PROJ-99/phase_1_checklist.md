# Phase 1: Economy Calculator

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-99 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create a pure strategy-layer class that aggregates empire-wide production and maintenance data into a display-ready snapshot. No UI dependencies.

---

## Tasks

### Task 1.1: Create EmpireEconomySnapshot dataclass [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [x] Create new file `game/strategy/engine/empire_economy_calculator.py`
- [x] Import `dataclass`, `field`, `Dict` from typing, `PLANET_RESOURCES` from `game.core.constants`
- [x] Define `EmpireEconomySnapshot` dataclass with fields:
  - Production: `colony_production`, `ship_production`, `trade_production`, `tribute_production`, `mining_production`, `total_production` — all `Dict[str, float]` with `default_factory=dict`
  - Expenses: `tribute_expenses`, `maintenance_expenses`, `construction_expenses`, `total_expenses` — all `Dict[str, float]`
  - Treasury: `net_resources`, `current_storage`, `max_storage` — all `Dict[str, float]`
- [x] Verify: snapshot can be instantiated with no args and all fields default to empty dict

**Notes:** Test `test_empty_snapshot_defaults_to_empty_dicts` verifies instantiation.

### Task 1.2: Create EmpireEconomyCalculator class [Medium]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [x] Define `EmpireEconomyCalculator` class with `MAINTENANCE_RATE = 0.05`
- [x] Implement `calculate(self, empire) -> EmpireEconomySnapshot`:
  - Call `_aggregate_colony_production(empire)` → `colony_production`
  - Set `ship_production`, `trade_production`, `tribute_production`, `mining_production` to `{r: 0.0 for r in PLANET_RESOURCES}`
  - `total_production` = copy of `colony_production` (only source for now)
  - Call `_aggregate_maintenance(empire)` → `maintenance_expenses`
  - Set `tribute_expenses`, `construction_expenses` to zeros
  - `total_expenses` = copy of `maintenance_expenses`
  - `net_resources` = `total_production[r] - total_expenses[r]` for each r
  - `current_storage` = copy of `empire.resource_pool`
  - `max_storage` = copy of `empire.max_storage`
  - Return populated snapshot
- [x] Implement `_aggregate_colony_production(self, empire) -> Dict[str, float]`:
  - Initialize `{r: 0.0 for r in PLANET_RESOURCES}`
  - Iterate `empire.colonies` → `colony.facilities` → skip non-operational
  - Get `facility.design_data`, iterate `layers.values()`
  - Handle list-format layers only (`isinstance(layer_data, list)`)
  - For each dict component, check `abilities.ResourceHarvester`
  - Extract `resource_type` and `base_harvest_rate`
  - Get `colony.resources[resource_type]['quality']` (default 0.0)
  - Accumulate `base_rate * quality` into totals
  - Reference: `harvesting_engine.py:245-284`
- [x] Implement `_aggregate_maintenance(self, empire) -> Dict[str, float]`:
  - Initialize zeros
  - Iterate `empire.colonies` → `colony.facilities` → skip non-operational → call `_calculate_maintenance_cost(facility.design_data)`
  - Iterate `empire.fleets` → `fleet.ships` → call `_calculate_maintenance_cost(ship.design_data)`
  - Accumulate costs into totals
  - Reference: `maintenance_engine.py:56-99`
- [x] Implement `_calculate_maintenance_cost(self, design_data) -> Dict[str, float]`:
  - Sum `resource_cost` from all components across all layers
  - Handle both layer formats: dict with `components` key, and direct list
  - Multiply totals by `MAINTENANCE_RATE` (0.05)
  - Reference: `maintenance_engine.py:189-228`

**Notes:** All 4 methods implemented following existing engine patterns.

### Task 1.3: Write unit tests [Medium]
**File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py -v`

- [x] Create test file with imports
- [x] Test: empty empire (no colonies, no fleets) → all values are 0.0 for each resource
- [x] Test: single colony with one facility having `ResourceHarvester` → correct colony_production
- [x] Test: facility maintenance cost → 5% of resource_cost
- [x] Test: ship maintenance cost → 5% of resource_cost
- [x] Test: net_resources = production - expenses
- [x] Test: current_storage and max_storage copied from empire
- [x] Test: non-operational facility is skipped
- [x] Test: both layer formats (dict with `components` key AND direct list)
- [x] Run tests and verify all pass

**Notes:** 13 tests total, all passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py -v`
- [x] No pygame imports in the calculator module
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
