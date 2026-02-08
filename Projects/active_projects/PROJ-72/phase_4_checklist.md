# Phase 4: Testing & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-72 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Run automated tests and verify all functionality manually

---

## Tasks

### Task 4.1: Automated test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass (baseline: 6246+)
- [ ] No regressions from button rename or new imports

### Task 4.2: Manual verification [Simple]

- [ ] Launch game, start a quickstart or load a save
- [ ] Verify "Menu" button appears in top bar where "Save Game" was
- [ ] Verify "End Turn" button is still in correct position
- [ ] Click "Menu" → dropdown panel appears below button with 6 options
- [ ] Click "Menu" again → panel closes (toggle behavior)
- [ ] Click outside panel → panel closes
- [ ] Press Escape with panel open → panel closes
- [ ] Click "Save Game" in menu → game saves, confirmation shown
- [ ] Click "Load Game" → SaveSelectionWindow opens, can browse saves
- [ ] Select a save and load → game reloads correctly
- [ ] Click "Settings" → "Coming Soon" message window appears
- [ ] Click "Controls" → "Coming Soon" message window appears
- [ ] Click "Quit to Menu" → confirmation dialog appears
  - Click "No" / close → stays in strategy
  - Click "Yes" → returns to main menu
- [ ] Click "Quit Game" → application exits cleanly
- [ ] Verify no visual overlap between panel and sidebar/map

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
