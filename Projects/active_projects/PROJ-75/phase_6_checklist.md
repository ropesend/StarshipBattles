# Phase 6: Integration & UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire everything together and display to player

---

## Tasks

### Task 6.1: Write end-to-end integration tests [Medium]
**File:** `tests/integration/strategy/test_economy_e2e.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_economy_e2e.py -v`

- [ ] Create test file with TestEconomyE2E class
- [ ] Test: full turn cycle with harvesting -> maintenance -> production
- [ ] Test: empire starts with resources, harvests more
- [ ] Test: build ship with resource consumption
- [ ] Test: ship requires maintenance payment
- [ ] Test: resource depletion causes build pause
- [ ] Test: maintenance failure causes scuttling
- [ ] Test: save/load preserves all economy state

**Notes:**

---

### Task 6.2: Update build queue UI to show costs [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual - start game and view build queue

- [ ] Display resource costs when selecting design
- [ ] Show current empire resources
- [ ] Color-code insufficient resources (red)
- [ ] Show build progress with resources consumed
- [ ] Show estimated completion time

**Notes:**

---

### Task 6.3: Update strategy UI to show empire resources [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual - start game and view strategy map

- [ ] Add empire resource display panel
- [ ] Show current / max for each resource type
- [ ] Color-code based on storage percentage
- [ ] Update display each turn

**Notes:**

---

### Task 6.4: Add scuttle notifications [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual - trigger scuttle and verify notification

- [ ] Display scuttle events to player
- [ ] Show what was scuttled and why
- [ ] Clear notification on acknowledgment

**Notes:**

---

### Task 6.5: Final verification [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite - all pass
- [ ] Manual playtest: Start new game
- [ ] Build harvesting complex, verify resources accumulate
- [ ] Queue ship build, verify proportional consumption
- [ ] Let resources deplete, verify build pauses
- [ ] Let maintenance fail, verify scuttling
- [ ] Save and reload, verify state preserved

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Run audit: `python Projects/scripts/audit_project.py PROJ-75`
