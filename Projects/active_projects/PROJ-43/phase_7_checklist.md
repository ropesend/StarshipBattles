# Phase 7: Strategy Deferred Import Elimination

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Restructure strategy modules to reduce deferred imports

---

## Prerequisites
- [x] Phase 4 complete (TurnEngine DI already removes its deferred imports)

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

### Task 7.1: Analyze Fleet Deferred Imports [Simple] - COMPLETE
**File:** `game/strategy/data/fleet.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [x] Line 88-89: `FleetMobilityService` in _trigger_speed_recalculation()
- [x] Line 110-117: `ShipStatsService` in can_use_warp()
- [x] Line 128-132: `ShipStatsService` in get_warp_limiting_ship()
- [x] Line 573: `ShipInstance` in from_dict()
- [x] Document why each deferred import exists
- [x] Add to findings/phase_7_analysis.md

**Notes:** Analysis complete. Found 4 deferred imports:
- FleetMobilityService: Edge operation (speed recalc on ship add/remove) - KEEP
- ShipStatsService (2x): Query operations (warp capability) - KEEP
- ShipInstance: Can be moved to module level (no actual circular)

---

### Task 7.2: Analyze ShipInstance Deferred Imports [Simple] - COMPLETE
**File:** `game/strategy/data/ship_instance.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [x] Identify all deferred imports
- [x] Document why each exists
- [x] Add to findings/phase_7_analysis.md

**Notes:** Analysis complete. Found 4 deferred imports:
- Line 125: ShipSerializer in from_ship() - KEEP (cross-layer boundary)
- Line 189: ShipStatsService in get_calculated_stats() - KEEP (lazy init pattern)
- Line 597: ShipSerializer in to_ship() - KEEP (cross-layer boundary)
- Line 598: log_debug in to_ship() - Can consolidate with log_warning at module level

---

### Task 7.3: Create Fleet Helper Service [Medium] - SKIPPED
**File:** `game/strategy/services/fleet_helper_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_fleet_helper_service.py`

Create a service that wraps FleetMobilityService and ShipStatsService calls:
- [x] DECISION: Skip service creation

**Notes:** After analysis, FleetHelperService is NOT RECOMMENDED:
- Service deferred imports in Fleet are acceptable (edge operations, queries)
- Creating a wrapper adds complexity without solving the root issue
- The coupling is legitimate (fleet operations need service capabilities)
- Service calls are already class methods, not instance methods requiring DI
- See findings/phase_7_analysis.md for full rationale

---

### Task 7.4: Refactor Fleet to Accept Services [Medium] - COMPLETE (Keep Deferred)
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet.py`

**Strategy:** Document as intentional deferred imports (after analysis)

- [x] DECISION: Keep deferred imports (document as intentional)
- [x] `_trigger_speed_recalculation()` - Edge operation, acceptable
- [x] `can_use_warp()` - Query operation, acceptable
- [x] `get_warp_limiting_ship()` - Query operation, acceptable

**Notes:** After analysis, refactoring to accept services is NOT RECOMMENDED:
- These are edge/query operations, not hot paths
- Adding service parameters would require updating all callers
- The current pattern is clean and self-contained
- Will be documented as intentional in Task 7.7

---

### Task 7.5: Refactor Fleet Deserialization [Simple] - COMPLETE
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet.py`

**Current issue:** from_dict() imports ShipInstance

- [x] Option B: Move import to module level (no actual circular dependency)
- [x] Verified ship_instance.py does NOT import Fleet
- [x] Moved ShipInstance import to module level
- [x] Updated type hints to use unquoted ShipInstance
- [x] Run fleet tests: 70 passed

**Notes:** Successfully eliminated 1 deferred import. ShipInstance is now imported at
module level alongside HexCoord. No circular dependency exists since ship_instance.py
doesn't import fleet.py.

---

### Task 7.6: Refactor ShipInstance [Medium] - COMPLETE
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance_proj08.py`

- [x] Review deferred imports (3 found)
- [x] Consolidated log_debug with log_warning at module level
- [x] Added INTENTIONAL LATE IMPORT comments for cross-layer imports
- [x] Run ship instance tests: 71 passed

**Notes:** ShipInstance deferred imports are all intentional and should remain:
- ShipSerializer in from_ship() and to_ship() - Cross-layer boundary (strategy -> simulation)
- ShipStatsService in get_calculated_stats() - Lazy initialization pattern
- All documented with comments referencing ARCHITECTURE.md

---

### Task 7.7: Update Fleet Callers [Medium] - COMPLETE (No Changes Needed)
**Files:** All files that call Fleet methods with service needs
**Tests:** `pytest tests/unit/strategy/`

- [x] Decision: No callers need updating (kept deferred imports)
- [x] Verified all strategy unit tests pass: 828 passed
- [x] No broken calls

**Notes:** Since we decided to keep service deferred imports as intentional (Task 7.4),
no callers need updating. The deferred import pattern is self-contained within Fleet
and doesn't require external service passing.

---

### Task 7.8: Integration Testing [Simple] - COMPLETE
**Tests:** `pytest tests/integration/`

- [x] Run strategy integration tests: N/A (no tests/integration/strategy/ directory)
- [x] Run all integration tests: 192 passed
- [x] Verify fleet operations work: 70 fleet unit tests passed
- [x] Verify fleet combat integration: 29 passed
- [x] Run full test suite with testmon: 433 passed
- [x] Run strategy unit tests: 828 passed

**Notes:** All tests passing after Phase 7 refactoring.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Fleet deferred imports reduced: 1 eliminated (ShipInstance), 3 documented as intentional
- [x] ShipInstance deferred imports addressed: 1 eliminated (log_debug), 3 documented as intentional
- [x] FleetHelperService SKIPPED (not beneficial after analysis)
- [x] All tests pass: integration 192, fleet 70, ship_instance 71, strategy 828
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 8
