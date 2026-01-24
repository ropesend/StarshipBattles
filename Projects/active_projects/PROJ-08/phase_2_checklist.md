# Phase 2: ShipStatsService Generic Refactor

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-08 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace hardcoded resource handling with generic dict accumulation

---

## Tasks

### Task 2.1: Fix Uninitialized Variable Bug [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [x] Add missing initializations for storage and cost variables

**Notes:** Fixed by refactoring to generic dicts - variables no longer needed

### Task 2.2: Refactor to Generic Dict Accumulators [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [x] Replace specific accumulators with `resource_storage`, `resource_consumption_per_hex`, `resource_consumption_per_turn` dicts
- [x] Remove if-elif chains, replace with generic iteration

**Notes:** Lines 76-81 initialize generic dicts, lines 162-179 handle resource storage generically

### Task 2.3: Add Component Toggles Parameter [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [x] Add `component_toggles: Optional[Dict[str, bool]] = None` parameter
- [x] Add default handling
- [x] Add toggle check in component loop

**Notes:** Line 44 adds parameter, lines 70-71 default, lines 138-143 toggle check

### Task 2.4: Add New Trigger Types [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [x] Add trigger handling for `strategic_per_hex`, `per_turn`, and `warp_jump`

**Notes:** Lines 186-203 handle all three trigger types

### Task 2.5: Update Return Structure [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [x] Update return dict to include new generic fields AND legacy fields

**Notes:** Lines 236-253 return both generic and legacy fields

### Task 2.6: Update Fallback Logic [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py`

- [x] Update fallback return to include new fields

**Notes:** Lines 88-130 handle fallback with all generic fields

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
