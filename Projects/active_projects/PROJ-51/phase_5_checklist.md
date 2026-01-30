# Phase 5: Verification & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full verification and documentation of changes
**Priority:** Required

---

## Tasks

### Task 5.1: Full Test Suite [Simple]
**Tests:** `pytest tests/`

- [ ] Run full test suite: `pytest tests/`
- [ ] Verify test count matches baseline (5734 passed, 3 skipped)
- [ ] Document any new failures (should be none from our changes)
- [ ] Note: Pre-existing failures in `tests/repro_issues/` are expected

**Notes:** [Filled during implementation]

### Task 5.2: Manual Verification [Medium]
**Tests:** Manual gameplay testing

- [ ] Launch game: `python main.py`
- [ ] Enter Battle Mode:
  - [ ] Verify BattleScreen loads correctly
  - [ ] Verify keyboard shortcuts work (Space=pause, O=overlay, etc.)
  - [ ] Verify BattleInputHandler is handling input
- [ ] Enter Strategy Mode:
  - [ ] Verify StrategyScreen loads correctly
  - [ ] Verify UI panels render correctly (StrategyUI)
  - [ ] Verify keyboard shortcuts work (M=move, J=join, etc.)
- [ ] Open Test Lab:
  - [ ] Verify TestLabScreen loads correctly
  - [ ] Run a test scenario
- [ ] Open Ship Design:
  - [ ] Verify ShipDesignValidator is working
  - [ ] Try adding/removing components

**Notes:** [Filled during implementation]

### Task 5.3: Documentation Updates [Simple]
**Files:** Project documentation

- [ ] Check for any hardcoded references to old paths in:
  - `Projects/` documentation files
  - `CLAUDE.md` or `WORKER.md`
  - Any README files
- [ ] Update references if found
- [ ] Add note to design.md about UI-007 decision:
  > "Event handling uses dual convention: `process_event` for pygame_gui UIWindow subclasses, `handle_event` for custom screens. This is intentional architecture."

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passing
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Mark plan.md Verification checkboxes as complete
