# Phase 5: Navigation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Enable row click to navigate to hex build screen

---

## Tasks

### Task 5.1: Implement row click handler [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** Manual test - click row navigates

- [ ] Track clicked row index from mouse position
- [ ] Get corresponding `BuildQueueSource`
- [ ] Get hex coordinate for source:
  - Planet: `galaxy.get_system_of_planet(planet).global_location + planet.location`
  - Fleet: `fleet.location`
- [ ] Call `on_navigate_to_hex(hex_coord)` callback
- [ ] Close window on navigation

**Notes:**

---

### Task 5.2: Wire up navigation callback [Simple]

**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual test - full navigation flow

- [ ] Add `on_navigate_to_hex_build(hex_coord)` callback method
- [ ] Close empire build queue window
- [ ] Open `BuildQueueScreen` for the specified hex
- [ ] Pass galaxy, empire, hex_coord to BuildQueueScreen

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Manual test: Click row opens hex build screen
- [ ] Manual test: Correct hex is selected
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
