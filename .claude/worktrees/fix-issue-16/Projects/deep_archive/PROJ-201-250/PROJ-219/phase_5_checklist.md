# Phase 5: Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove PROJ-216 diagnostic logging and finalize project

---

## Tasks

### Task 5.1: Check for PROJ-216 diagnostic logging [Simple]
**Files:** Multiple (see list below)
**Tests:** `pytest tests/ --testmon`

Check these files for PROJ-216 diagnostic logging that should be removed:
- [x] `game/ui/screens/strategy_input_handler.py` - removed all [DIAG] logging + unused logger import
- [x] `game/ui/screens/strategy_event_router.py` - removed all [DIAG] logging (KEPT click gate fix)
- [x] `game/ui/screens/strategy_click_dispatcher.py` - removed all [DIAG] logging
- [x] `game/ui/screens/strategy_fleet_ops.py` - removed all [DIAG] logging, kept functional warnings
- [x] `game/strategy/facade/strategy_session_facade.py` - removed [DIAG] logging from get_fleet_path_preview
- [x] `game/strategy/data/pathfinding.py` - removed all [DIAG] logging from find_hybrid_path

**Notes:** All functional code and PROJ-216 fix (click gate) preserved. Only verbose diagnostic logging removed.

---

### Task 5.2: Update PROJ-216 comments [Simple]
**Files:** See below
**Tests:** N/A (documentation only)

Update comments to reference PROJ-219:
- [x] `game/strategy/engine/game_session.py` - Updated fleet registration comment to reference PROJ-219
- [x] `game/strategy/data/empire.py` - Added PROJ-219 docstrings to add_fleet() and remove_fleet()

**Notes:**

---

### Task 5.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite (not --testmon)
- [x] Verify no new failures beyond baseline
- [x] Document any new warnings

**Notes:** 13167 passed, 2 skipped - matches baseline exactly.

---

### Task 5.4: Final manual verification [Simple]
**Tests:** Manual gameplay

- [x] Skipped (automated loop - manual gameplay not available)

**Notes:** Integration tests in Phase 4 cover all fleet lifecycle paths. Manual verification deferred to user.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` - no regressions beyond baseline
- [x] Manual verification deferred (automated mode)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `COMPLETE`
- [x] Update plan.md Verification section - all items checked
- [x] Ready for audit
