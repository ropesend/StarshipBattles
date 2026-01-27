# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-26 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: NC-01 - Duplicate BattleScene not removed [Simple]
**File:** `game/ui/screens/battle.py` (deleted) and `game/ui/screens/battle_scene.py` (kept)
**Tests:** `pytest tests/unit/ui/test_battle_scene.py --testmon`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (existing tests cover BattleScene)
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Deleted `game/ui/screens/battle.py` (legacy version using BattleEngine directly)
- Kept `game/ui/screens/battle_scene.py` (modern version using BattleService)
- Updated `tests/unit/verify_determinism_current.py` to import from `battle_scene.py`
- All 322 testmon-selected tests pass


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
