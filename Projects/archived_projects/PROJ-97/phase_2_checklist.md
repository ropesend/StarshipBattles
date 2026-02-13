# Phase 2: BuildQueueSource Per-Resource Rates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Change `build_rate` from `float` to `Dict[str, float]` and update all queue discovery

---

## Tasks

### Task 2.1: Update BuildQueueSource dataclass [Simple]
**File:** `game/strategy/data/build_queue_source.py` (line 40)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Change `build_rate: float = 2000.0` to `build_rate: Dict[str, float] = field(default_factory=dict)`
- [x] Add import for `field` from dataclasses (already imported)
- [x] Add import for `Dict` from typing (already imported)

**Notes:** Updated dataclass to use Dict with default_factory

### Task 2.2: Add production rate loader function [Simple]
**File:** `game/strategy/data/build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Add `_load_production_rates() -> Dict` function that loads `data/production_rates.json` via `load_json` with caching
- [x] Add `get_default_production_rates(yard_type: str) -> Dict[str, float]` public function
- [x] Yard types: `"planetary_yard"`, `"space_shipyard"`, `"fleet_space_yard"`
- [x] Fallback: return empty dict if file missing or type unknown

**Notes:** Added module-level cache, returns copy not reference

### Task 2.3: Update `_get_facility_build_rate` → `_get_facility_production_rates` [Medium]
**File:** `game/strategy/data/build_queue_source.py` (lines 44-65)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Rename to `_get_facility_production_rates(facility) -> Dict[str, float]`
- [x] Read `production_rates` from SpaceShipyard ability data in facility.design_data
- [x] If found, apply `construction_speed_bonus` multiplier to all rates
- [x] If not found, fall back to `get_default_production_rates("space_shipyard")` and apply bonus
- [x] Return per-resource dict

**Notes:** Full implementation with explicit rates support

### Task 2.4: Update `collect_build_queues_at_hex()` [Simple]
**File:** `game/strategy/data/build_queue_source.py` (lines 96-168)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Planet base queue (line 129): `build_rate=get_default_production_rates("planetary_yard")`
- [x] Facility queue (line 146): `build_rate=_get_facility_production_rates(facility)`
- [x] Fleet queue (line 164): `build_rate=get_default_production_rates("fleet_space_yard")`

**Notes:** All three queue types now use Dict rates

### Task 2.5: Update `collect_all_build_queues_for_empire()` [Simple]
**File:** `game/strategy/data/build_queue_source.py` (lines 171-236)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Planet base queue (line 199): `build_rate=get_default_production_rates("planetary_yard")`
- [x] Facility queue (line 216): `build_rate=_get_facility_production_rates(facility)`
- [x] Fleet queue (line 232): `build_rate=get_default_production_rates("fleet_space_yard")`

**Notes:** All three queue types now use Dict rates

### Task 2.6: Update existing build_queue_source tests [Medium]
**File:** `tests/unit/strategy/data/test_build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Update `_make_shipyard_facility` helper to include `production_rates` in SpaceShipyard data
- [x] Update assertions: `source.build_rate == 2000.0` → `source.build_rate == {"Metals": 2000, ...}`
- [x] Update test at line 494 (base queue rate)
- [x] Update test at line 509 (default shipyard rate)
- [x] Update test at line 538 (shipyard with bonus — 4500.0 → per-resource * 1.5)
- [x] Update test at line 550 (fleet rate)
- [x] Add new test: facility with explicit `production_rates` in design_data

**Notes:** Added 7 new tests: explicit rates, rates with bonus, 5 get_default_production_rates tests

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
