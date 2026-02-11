# Phase 2: BuildQueueSource Per-Resource Rates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Change `build_rate` from `float` to `Dict[str, float]` and update all queue discovery

---

## Tasks

### Task 2.1: Update BuildQueueSource dataclass [Simple]
**File:** `game/strategy/data/build_queue_source.py` (line 40)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Change `build_rate: float = 2000.0` to `build_rate: Dict[str, float] = field(default_factory=dict)`
- [ ] Add import for `field` from dataclasses (already imported)
- [ ] Add import for `Dict` from typing (already imported)

**Notes:**

### Task 2.2: Add production rate loader function [Simple]
**File:** `game/strategy/data/build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Add `_load_production_rates() -> Dict` function that loads `data/production_rates.json` via `load_json` with caching
- [ ] Add `get_default_production_rates(yard_type: str) -> Dict[str, float]` public function
- [ ] Yard types: `"planetary_yard"`, `"space_shipyard"`, `"fleet_space_yard"`
- [ ] Fallback: return empty dict if file missing or type unknown

**Notes:** Use `game.core.json_utils.load_json` for loading. Cache at module level.

### Task 2.3: Update `_get_facility_build_rate` → `_get_facility_production_rates` [Medium]
**File:** `game/strategy/data/build_queue_source.py` (lines 44-65)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Rename to `_get_facility_production_rates(facility) -> Dict[str, float]`
- [ ] Read `production_rates` from SpaceShipyard ability data in facility.design_data
- [ ] If found, apply `construction_speed_bonus` multiplier to all rates
- [ ] If not found, fall back to `get_default_production_rates("space_shipyard")` and apply bonus
- [ ] Return per-resource dict

**Notes:**

### Task 2.4: Update `collect_build_queues_at_hex()` [Simple]
**File:** `game/strategy/data/build_queue_source.py` (lines 96-168)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Planet base queue (line 129): `build_rate=get_default_production_rates("planetary_yard")`
- [ ] Facility queue (line 146): `build_rate=_get_facility_production_rates(facility)`
- [ ] Fleet queue (line 164): `build_rate=get_default_production_rates("fleet_space_yard")`

**Notes:**

### Task 2.5: Update `collect_all_build_queues_for_empire()` [Simple]
**File:** `game/strategy/data/build_queue_source.py` (lines 171-236)
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Planet base queue (line 199): `build_rate=get_default_production_rates("planetary_yard")`
- [ ] Facility queue (line 216): `build_rate=_get_facility_production_rates(facility)`
- [ ] Fleet queue (line 232): `build_rate=get_default_production_rates("fleet_space_yard")`

**Notes:**

### Task 2.6: Update existing build_queue_source tests [Medium]
**File:** `tests/unit/strategy/data/test_build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [ ] Update `_make_shipyard_facility` helper to include `production_rates` in SpaceShipyard data
- [ ] Update assertions: `source.build_rate == 2000.0` → `source.build_rate == {"Metals": 2000, ...}`
- [ ] Update test at line 494 (base queue rate)
- [ ] Update test at line 509 (default shipyard rate)
- [ ] Update test at line 538 (shipyard with bonus — 4500.0 → per-resource * 1.5)
- [ ] Update test at line 550 (fleet rate)
- [ ] Add new test: facility with explicit `production_rates` in design_data

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
