# Phase 6: Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full regression testing and manual verification. Confirm zero duck typing remains.

---

## Tasks

### Task 6.1: Full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run: `pytest tests/ -n 12` → 12,705+ tests passing, 0 failures
- [ ] Run: `pytest simulation_tests/ -n 4` → all simulation tests passing
- [ ] Document any new warnings or skipped tests

**Notes:**

---

### Task 6.2: Duck typing audit [Simple]

- [ ] Run: `grep -rn "getattr\|hasattr" game/simulation/ | grep -v formula_system | grep -v __pycache__`
- [ ] Verify output is EMPTY (or only contains legitimate meta-programming in abilities/base.py descriptor system)
- [ ] Document any remaining instances with justification

**Notes:**

---

### Task 6.3: Manual verification [Simple]

- [ ] Launch game, enter Ship Builder — build/modify a ship design
- [ ] Start a combat simulation — verify ships fight, take damage, projectiles work
- [ ] Verify no AttributeErrors in console output
- [ ] Check targeting system works (ships acquire and engage targets)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passing
- [ ] Zero duck typing remaining (audit passed)
- [ ] Manual gameplay verification passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md Verification section — all checked
- [ ] Update plan.md Current State: "PROJ-190 Complete"
