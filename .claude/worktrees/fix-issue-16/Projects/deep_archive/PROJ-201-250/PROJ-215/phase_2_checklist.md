# Phase 2: Enrich Event Location Data at Creation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `system_name` and `local_hex` fields to all event creation sites so the new columns have data.

---

## Tasks

### Task 2.1: Enrich production events (planet-based) [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine.py`

- [x] In `_spawn_complex()` (lines 560-577): Add `system_name=parent_sys.name` and `local_hex=[planet.location.q, planet.location.r]` to `log_event()`
- [x] In `_spawn_ship()` (lines 596-647): Same — add `system_name` and `local_hex` to `log_event()` (line 637)
- [x] In `_spawn_fleet_ship()`: Add `system_name=""` and `local_hex=None` (fleet in deep space)
- [x] In `_spawn_fleet_complex()`: Add system/local hex if galaxy available

**Notes:** Added defensive hasattr() checks for mock compatibility in tests.

### Task 2.2: Enrich combat events [Simple]
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_engine.py`

- [x] In RNG combat event (lines 206-214): Look up system from fleet location using `self._galaxy.get_system_at_location()`, add `system_name=system_name`
- [x] In simulated combat event (lines 267-275): Same system lookup, add `system_name=system_name`

**Notes:** Combat events don't have a specific planet, so no `location_name` or `local_hex`. Added defensive hasattr() checks.

### Task 2.3: Enrich colonization events [Simple]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_order_processor.py`

- [x] In `_execute_colonize_order()` (lines 220-230): Add system lookup and `system_name=system_name, local_hex=local_hex` to `log_event()`
- [x] Verify the `galaxy` parameter is accessible in this method

**Notes:** Added defensive hasattr() checks for both galaxy and planet.location.

### Task 2.4: Add tests for enriched event data [Medium]
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] Add test verifying production events include `system_name` in details
- [x] Add test verifying production events include `local_hex` in details
- [x] Add test verifying combat events include `system_name` in details
- [x] Add test verifying colonization events include `system_name` and `local_hex` in details
- [x] Run full test suite: `pytest tests/ -n 12`

**Notes:** Added 8 new tests in `tests/unit/strategy/test_engine_event_emission.py` covering all event types and edge cases.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
