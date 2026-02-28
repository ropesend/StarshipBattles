# Phase 4: Cargo Ability Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** New CargoStorage ability (follows ResourceStorage pattern), registered in ability system, aggregated by strategy-layer ShipStatsCalculator. Add passenger_quarters component to components.json.

**Depends on:** None (ability system is independent — can run in parallel with Phases 1-2)

---

## Tasks

### Task 4.1: CargoStorage Ability [Medium]
**New file:** `game/simulation/components/abilities/cargo.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_cargo_storage.py`

- [x] `CargoStorage(Ability)` class:
  - `layer = AbilityLayer.STRATEGIC` (cargo only relevant in strategy)
  - `STAT_BINDINGS` with `CAPACITY_MULT` -> `capacity`
  - Properties: `cargo_type: str`, `capacity: float`, `_base_capacity: float`
  - Handle dict format: `{"cargo_type": "passengers", "capacity": 5000}`
  - Handle scalar format: `5000` (defaults to cargo_type="generic")
  - `sync_data()`, `recalculate()`, `get_ui_rows()`, `get_primary_value()`

**Notes:** Followed `ResourceStorage` pattern. Used `layer = 'strategic'` string instead of enum.

---

### Task 4.2: Register Ability [Simple]
**File:** `game/simulation/components/abilities/__init__.py`

- [x] Import `CargoStorage` from `.cargo`
- [x] Add `"CargoStorage": CargoStorage` to `ABILITY_REGISTRY`
- [x] Add to `__all__`

**Notes:** Complete

---

### Task 4.3: Strategy-Layer Stats Aggregation [Medium]
**File:** `game/strategy/services/ship_stats_calculator.py`

- [x] Add `cargo_storage: Dict[str, float]` accumulator in calculation method
- [x] Aggregate `CargoStorage` abilities by `cargo_type` (sum capacities)
- [x] Include `'cargo_storage': cargo_storage` in returned stats dict

**Notes:** Added to main stats return and fallback expected_stats return

---

### Task 4.4: Passenger Quarters Component [Simple]
**File:** `data/components.json` (after colony pod components)

- [x] Add `passenger_quarters` component definition:
  ```json
  {
    "id": "passenger_quarters",
    "name": "Passenger Quarters",
    "type": "Infrastructure",
    "mass": 200, "hp": 150,
    "allowed_vehicle_types": ["Ship"],
    "abilities": {
      "CargoStorage": {"cargo_type": "passengers", "capacity": 5000},
      "LifeSupportCapacity": 5000,
      "CrewRequired": 10
    },
    "major_classification": "Infrastructure",
    "resource_cost": {"Metals": 150, "Organics": 100, "Vapors": 50}
  }
  ```

**Notes:** Added sprite_index: 230

---

### Task 4.5: Tests [Medium]
**New file:** `tests/unit/simulation/abilities/test_cargo_storage.py`

- [x] `test_cargo_storage_creation_dict_format`
- [x] `test_cargo_storage_creation_scalar_format`
- [x] `test_cargo_storage_sync_data`
- [x] `test_cargo_storage_recalculate_with_modifier`
- [x] `test_cargo_storage_ui_rows`
- [x] `test_cargo_storage_registry_creation` — via `create_ability()`
- [x] `test_ship_stats_includes_cargo_storage` — strategy calculator aggregation
- [x] `test_passenger_quarters_component_loads` — from components.json
- [x] Verify: `pytest tests/unit/simulation/abilities/test_cargo_storage.py -v` — 22 passed
- [x] Verify: `pytest tests/ -n 12` — 6465 passed (2 pre-existing bug_15 failures)

**Notes:** 22 new tests total covering all functionality

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/simulation/abilities/test_cargo_storage.py -v`
- [x] No regressions: `pytest tests/ -n 12` — 6465 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
