# Phase 3: Formation + Adapter Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate duck typing in `behaviors.py` (5 instances) and `controllable.py` (4 instances).

---

## Tasks

### Task 3.1: `behaviors.py` FormationBehavior (lines 281, 334-336) [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/ -k formation`

- [x] Import `IFormationMaster` from `game.ai.protocols`
- [x] Type-hint `master` variable as `Optional[IFormationMaster]` after retrieval
- [x] L281: Replace `getattr(master, 'is_derelict', False)` with `master.is_derelict`
- [x] L334: Replace `getattr(master, 'is_thrusting', False)` with `master.is_thrusting`
- [x] L336: Replace `getattr(master, 'max_speed', 0)` with `master.max_speed`
- [x] L336: Replace `getattr(master, 'engine_throttle', 1.0)` with `master.engine_throttle`

**Notes:** Renamed local variable to `formation_master` and updated all subsequent usages.

### Task 3.2: `controllable.py` adapter defensive defaults (lines 406, 426, 430) [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter.py`

- [x] L406: Replace `getattr(self._ship, 'max_targets', CombatConstants.DEFAULT_MAX_TARGETS)` with `self._ship.max_targets` — Ship always sets this in `__init__` (L63)
- [x] L426: Replace `getattr(self._ship, 'ai_strategy', 'standard_ranged')` with `self._ship.ai_strategy` — Ship always sets this (L150)
- [x] L430: Replace `getattr(self._ship, 'vehicle_type', 'Ship')` with `self._ship.vehicle_type` — Ship always sets this (L95)

**Notes:** Ship always has these attributes. Deleted 3 obsolete tests that tested impossible fallback scenarios.

### Task 3.3: `controllable.py` formation hasattr (line 472) [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py`

- [x] L472: Replace `hasattr(master, 'formation') and hasattr(master.formation, 'members')` with direct access `master.formation.members` — Ship always has `.formation` (ShipFormation) and it always has `.members`
- [x] Update return type hint of `get_formation_master()` from `Optional[Any]` to include IFormationMaster reference in docstring

**Notes:** Added docstring explaining Ship always has .formation (ShipFormation) with .members.

### Task 3.4: Verify [Simple]
- [x] `pytest tests/unit/ai/ -v` — all pass
- [x] `pytest tests/ -n 12` — 12706 passed, 1 skipped

**Notes:** Deleted 4 obsolete tests total:
- 3 from test_controllable_adapter_edge_cases.py (test_get_ai_strategy_missing, test_get_vehicle_type_missing, test_get_max_targets_missing)
- 1 from test_response.py (test_default_strategy_if_not_set)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
