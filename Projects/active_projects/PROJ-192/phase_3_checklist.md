# Phase 3: Formation + Adapter Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate duck typing in `behaviors.py` (5 instances) and `controllable.py` (4 instances).

---

## Tasks

### Task 3.1: `behaviors.py` FormationBehavior (lines 281, 334-336) [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/ -k formation`

- [ ] Import `IFormationMaster` from `game.ai.protocols`
- [ ] Type-hint `master` variable as `Optional[IFormationMaster]` after retrieval
- [ ] L281: Replace `getattr(master, 'is_derelict', False)` with `master.is_derelict`
- [ ] L334: Replace `getattr(master, 'is_thrusting', False)` with `master.is_thrusting`
- [ ] L336: Replace `getattr(master, 'max_speed', 0)` with `master.max_speed`
- [ ] L336: Replace `getattr(master, 'engine_throttle', 1.0)` with `master.engine_throttle`

**Notes:**

### Task 3.2: `controllable.py` adapter defensive defaults (lines 406, 426, 430) [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter.py`

- [ ] L406: Replace `getattr(self._ship, 'max_targets', CombatConstants.DEFAULT_MAX_TARGETS)` with `self._ship.max_targets` — Ship always sets this in `__init__` (L63)
- [ ] L426: Replace `getattr(self._ship, 'ai_strategy', 'standard_ranged')` with `self._ship.ai_strategy` — Ship always sets this (L150)
- [ ] L430: Replace `getattr(self._ship, 'vehicle_type', 'Ship')` with `self._ship.vehicle_type` — Ship always sets this (L95)

**Notes:**

### Task 3.3: `controllable.py` formation hasattr (line 472) [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py`

- [ ] L472: Replace `hasattr(master, 'formation') and hasattr(master.formation, 'members')` with direct access `master.formation.members` — Ship always has `.formation` (ShipFormation) and it always has `.members`
- [ ] Update return type hint of `get_formation_master()` from `Optional[Any]` to include IFormationMaster reference in docstring

**Notes:**

### Task 3.4: Verify [Simple]
- [ ] `pytest tests/unit/ai/ -v` — all pass
- [ ] `pytest tests/ -n 12` — 12705+ pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
