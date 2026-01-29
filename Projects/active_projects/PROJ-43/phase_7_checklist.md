# Phase 7: Strategy Deferred Import Elimination

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Restructure strategy modules to reduce deferred imports

---

## Prerequisites
- [ ] Phase 4 complete (TurnEngine DI already removes its deferred imports)

## Background

**Problem:** Deferred imports in strategy data layer:
- `game/strategy/data/fleet.py` - 4 deferred imports
- `game/strategy/data/ship_instance.py` - deferred imports

**Key Circular Chains:**
- Fleet ↔ ShipStatsService: Fleet queries ship capabilities
- Fleet ↔ FleetMobilityService: Fleet triggers speed recalculation
- ShipInstance ↔ ShipStatsService: Instance needs stats

---

## Tasks

### Task 7.1: Analyze Fleet Deferred Imports [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [ ] Line 88-89: `FleetMobilityService` in _trigger_speed_recalculation()
- [ ] Line 110-117: `ShipStatsService` in can_use_warp()
- [ ] Line 128-132: `ShipStatsService` in get_warp_limiting_ship()
- [ ] Line 573: `ShipInstance` in from_dict()
- [ ] Document why each deferred import exists
- [ ] Add to findings/phase_7_analysis.md

**Notes:**

---

### Task 7.2: Analyze ShipInstance Deferred Imports [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [ ] Identify all deferred imports
- [ ] Document why each exists
- [ ] Add to findings/phase_7_analysis.md

**Notes:**

---

### Task 7.3: Create Fleet Helper Service [Medium]
**File:** `game/strategy/services/fleet_helper_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_fleet_helper_service.py`

Create a service that wraps FleetMobilityService and ShipStatsService calls:
- [ ] Create `FleetHelperService` class:
  - `recalculate_fleet_speed(fleet)`
  - `can_use_warp(fleet)`
  - `get_warp_limiting_ship(fleet)`
- [ ] Inject ShipStatsService and FleetMobilityService via constructor
- [ ] Create unit tests

**Notes:**

---

### Task 7.4: Refactor Fleet to Accept Services [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet.py`

**Strategy:** Move service calls to methods that receive service as parameter

- [ ] Update `_trigger_speed_recalculation()` to accept service parameter
- [ ] Update `can_use_warp()` to accept service parameter
- [ ] Update `get_warp_limiting_ship()` to accept service parameter
- [ ] Update callers to pass services explicitly
- [ ] Remove deferred imports (lines 88-132)
- [ ] Run fleet tests

**Notes:**

---

### Task 7.5: Refactor Fleet Deserialization [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet.py`

**Current issue:** from_dict() imports ShipInstance

- [ ] Option A: Keep deferred import (serialization is special)
- [ ] Option B: Move import to module level with TYPE_CHECKING for hints
- [ ] Choose approach and implement
- [ ] Run serialization tests

**Notes:**

---

### Task 7.6: Refactor ShipInstance [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/data/test_ship_instance.py`

- [ ] Review deferred imports
- [ ] Move service calls to accept services as parameters
- [ ] Update callers
- [ ] Run ship instance tests

**Notes:**

---

### Task 7.7: Update Fleet Callers [Medium]
**Files:** All files that call Fleet methods with service needs
**Tests:** `pytest tests/unit/strategy/`

- [ ] Find all callers of Fleet methods that need services
- [ ] Update to pass services explicitly
- [ ] Verify no broken calls

**Notes:**

---

### Task 7.8: Integration Testing [Simple]
**Tests:** `pytest tests/integration/strategy/`

- [ ] Run strategy integration tests
- [ ] Verify fleet operations work
- [ ] Verify warp capability checks work
- [ ] Verify speed calculations work
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Fleet deferred imports reduced or eliminated
- [ ] ShipInstance deferred imports addressed
- [ ] FleetHelperService created (if needed)
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8
