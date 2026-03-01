# Phase 5: Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove PROJ-216 diagnostic logging and finalize project

---

## Tasks

### Task 5.1: Check for PROJ-216 diagnostic logging [Simple]
**Files:** Multiple (see list below)
**Tests:** `pytest tests/ --testmon`

Check these files for PROJ-216 diagnostic logging that should be removed:
- [ ] `game/ui/screens/strategy_input_handler.py` - check for debug logging
- [ ] `game/ui/screens/strategy_event_router.py` - check for debug logging (note: KEEP the click gate fix)
- [ ] `game/ui/screens/strategy_click_dispatcher.py` - check for debug logging
- [ ] `game/ui/screens/strategy_fleet_ops.py` - check for debug logging
- [ ] `game/strategy/facade/strategy_session_facade.py` - check for debug logging
- [ ] `game/strategy/data/pathfinding.py` - check for debug logging

For each file:
- Keep functional code changes from PROJ-216
- Remove any verbose diagnostic logging that was added for debugging
- Leave appropriate info/warning level logs

**Notes:**

---

### Task 5.2: Update PROJ-216 comments [Simple]
**Files:** See below
**Tests:** N/A (documentation only)

Update comments to reference PROJ-219:
- [ ] `game/strategy/engine/game_session.py` - Update comment on fleet registration loop to reference PROJ-219
- [ ] `game/strategy/data/empire.py` - Add docstring mentioning PROJ-219 auto-registration

**Notes:**

---

### Task 5.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite (not --testmon)
- [ ] Verify no new failures beyond the 42 baseline
- [ ] Document any new warnings

**Notes:**

---

### Task 5.4: Final manual verification [Simple]
**Tests:** Manual gameplay

- [ ] Start new game, build ship at colony → fleet appears in galaxy registry
- [ ] Split fleet → both fleets queryable via `get_fleet_by_id()`
- [ ] Merge fleet (JOIN_FLEET) → merged fleet removed from registry
- [ ] Save and load game → all fleets work correctly
- [ ] Verify no crashes or obvious issues

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` - no regressions beyond baseline
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `COMPLETE`
- [ ] Update plan.md Verification section - all items checked
- [ ] Ready for audit
