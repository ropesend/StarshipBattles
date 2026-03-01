# Phase 2: Enrich Event Location Data at Creation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `system_name` and `local_hex` fields to all event creation sites so the new columns have data.

---

## Tasks

### Task 2.1: Enrich production events (planet-based) [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine.py`

- [ ] In `_spawn_complex()` (lines 560-577): Add `system_name=parent_sys.name` and `local_hex=[planet.location.q, planet.location.r]` to `log_event()`
- [ ] In `_spawn_ship()` (lines 596-647): Same — add `system_name` and `local_hex` to `log_event()` (line 637)
- [ ] In `_spawn_fleet_ship()`: Add `system_name=""` and `local_hex=None` (fleet in deep space)
- [ ] In `_build_fleet_yard_complex()`: Add system/local hex if galaxy available

**Notes:**

### Task 2.2: Enrich combat events [Simple]
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_engine.py`

- [ ] In RNG combat event (lines 206-214): Look up system from fleet location using `self._galaxy.get_system_at_location()`, add `system_name=system_name`
- [ ] In simulated combat event (lines 267-275): Same system lookup, add `system_name=system_name`

**Notes:** Combat events don't have a specific planet, so no `location_name` or `local_hex`.

### Task 2.3: Enrich colonization events [Simple]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_order_processor.py`

- [ ] In `_execute_colonize_order()` (lines 220-230): Add system lookup and `system_name=system_name, local_hex=local_hex` to `log_event()`
- [ ] Verify the `galaxy` parameter is accessible in this method

**Notes:**

### Task 2.4: Add tests for enriched event data [Medium]
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] Add test verifying production events include `system_name` in details
- [ ] Add test verifying production events include `local_hex` in details
- [ ] Add test verifying combat events include `system_name` in details
- [ ] Add test verifying colonization events include `system_name` and `local_hex` in details
- [ ] Run full test suite: `pytest tests/ -n 12`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
