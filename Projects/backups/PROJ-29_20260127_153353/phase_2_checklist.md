# Phase 2: Major Issues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-29 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address major severity findings that significantly impact quality
**Priority:** High

---

## Tasks

### Task 2.1: SIM-03 - BattleController handles too many concerns [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/test_retreat_manager.py tests/unit/simulation/test_battle_state_manager.py tests/unit/simulation/test_battle_controller.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
The BattleController was mixing 4 distinct concerns:
1. Battle Setup/Configuration
2. Battle Execution
3. Retreat/Reinforcement Mechanics
4. State Serialization

**Solution implemented:**
- Created `game/simulation/managers/` package with extracted classes:
  - `RetreatManager` - Handles retreat/reinforcement mechanics (~190 lines extracted)
  - `BattleStateManager` - Handles state serialization/deserialization (~75 lines extracted)
- BattleController now delegates to these managers while maintaining backward-compatible API
- Backward compatibility properties (`_retreating_ships`, `_escaped_ships`) ensure existing code still works
- Tests updated to use new `RetreatMethod` enum instead of string method names

**Impact:**
- 31 new tests for RetreatManager
- 13 new tests for BattleStateManager
- 100 existing BattleController tests pass (with minor updates for enum usage)
- Full test suite: 4693 tests pass


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
