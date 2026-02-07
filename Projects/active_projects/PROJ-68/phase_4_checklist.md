# Phase 4: Cargo Ability Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** New CargoStorage ability (follows ResourceStorage pattern), registered in ability system, aggregated by strategy-layer ShipStatsCalculator. Add passenger_quarters component to components.json.

**Depends on:** None (ability system is independent — can run in parallel with Phases 1-2)

---

## Tasks

### Task 4.1: CargoStorage Ability [Medium]
**New file:** `game/simulation/components/abilities/cargo.py`
**Tests:** `pytest tests/unit/simulation/abilities/test_cargo_storage.py`

- [ ] `CargoStorage(Ability)` class:
  - `layer = AbilityLayer.STRATEGIC` (cargo only relevant in strategy)
  - `STAT_BINDINGS` with `CAPACITY_MULT` -> `capacity`
  - Properties: `cargo_type: str`, `capacity: float`, `_base_capacity: float`
  - Handle dict format: `{"cargo_type": "passengers", "capacity": 5000}`
  - Handle scalar format: `5000` (defaults to cargo_type="generic")
  - `sync_data()`, `recalculate()`, `get_ui_rows()`, `get_primary_value()`

**Notes:** Follow `ResourceStorage` pattern in `game/simulation/components/abilities/resources.py:151-189`

---

### Task 4.2: Register Ability [Simple]
**File:** `game/simulation/components/abilities/__init__.py`

- [ ] Import `CargoStorage` from `.cargo`
- [ ] Add `"CargoStorage": CargoStorage` to `ABILITY_REGISTRY`
- [ ] Add to `__all__`

**Notes:**

---

### Task 4.3: Strategy-Layer Stats Aggregation [Medium]
**File:** `game/strategy/services/ship_stats_calculator.py`

- [ ] Add `cargo_storage: Dict[str, float]` accumulator in calculation method
- [ ] Aggregate `CargoStorage` abilities by `cargo_type` (sum capacities)
- [ ] Include `'cargo_storage': cargo_storage` in returned stats dict

**Notes:** Follow existing resource storage aggregation pattern in same file

---

### Task 4.4: Passenger Quarters Component [Simple]
**File:** `data/components.json` (after colony pod components)

- [ ] Add `passenger_quarters` component definition:
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

**Notes:**

---

### Task 4.5: Tests [Medium]
**New file:** `tests/unit/simulation/abilities/test_cargo_storage.py`

- [ ] `test_cargo_storage_creation_dict_format`
- [ ] `test_cargo_storage_creation_scalar_format`
- [ ] `test_cargo_storage_sync_data`
- [ ] `test_cargo_storage_recalculate_with_modifier`
- [ ] `test_cargo_storage_ui_rows`
- [ ] `test_cargo_storage_registry_creation` — via `create_ability()`
- [ ] `test_ship_stats_includes_cargo_storage` — strategy calculator aggregation
- [ ] `test_passenger_quarters_component_loads` — from components.json
- [ ] Verify: `pytest tests/unit/simulation/abilities/test_cargo_storage.py -v` — all pass
- [ ] Verify: `pytest tests/ --testmon` — no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/simulation/abilities/test_cargo_storage.py -v`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
