# Phase 1: Data Model — FleetOrder.execution_progress + OrderType.WARP [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `execution_progress` tracking to `FleetOrder`, add `WARP` to `OrderType`, and update serialization. No behavior changes.

---

## Tasks

### Task 1.1: Add WARP to OrderType [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "order"` after changes

- [x] Add `WARP = auto()` to `OrderType` enum (after MOVE, line ~20)
- [x] WARP target will be a HexCoord (the warp point hex to enter)

**Notes:**

### Task 1.2: Add execution_progress to FleetOrder [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet"` after changes

- [x] Add `self.execution_progress: int = 0` to `FleetOrder.__init__()` (line 38)
- [x] Update `FleetOrder.__repr__()` to include `execution_progress` when > 0
- [x] Update `FleetOrder.to_dict()` to serialize `execution_progress` (only when > 0 to keep saves clean)

**Notes:**

### Task 1.3: Update Fleet deserialization [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and (serial or dict or save or load)"` after changes

- [x] In `Fleet.from_dict()`, restore `execution_progress` from order data dict (default 0)
- [x] Handle both old saves (no field) and new saves (field present)

**Notes:**

### Task 1.4: Write unit tests for serialization round-trip [Simple]
**File:** `tests/unit/strategy/test_fleet_order_serialization.py` (new or extend existing)
**Tests:** `pytest tests/unit/strategy/test_fleet_order_serialization.py`

- [x] Test FleetOrder with execution_progress=0 round-trips correctly
- [x] Test FleetOrder with execution_progress=3 round-trips correctly
- [x] Test FleetOrder with WARP order type round-trips correctly
- [x] Test backward compat: old save data without execution_progress loads with default 0

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ --testmon` passes
- [x] No behavior changes — existing tests still pass without modification
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
