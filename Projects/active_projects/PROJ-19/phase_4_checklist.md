# Phase 4: Update Remaining UI Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate remaining UI files with significant duck typing

---

## Tasks

### Task 4.1: Update planet_list_window.py [Medium]
**File:** `game/ui/panels/planet_list_window.py` (15 hasattr)
**Tests:** `pytest tests/ui/ -k "planet" -v`

- [ ] Add Protocol imports at top of file
- [ ] Search file for hasattr patterns
- [ ] Replace duck typing with TypeGuard calls where appropriate
- [ ] Verify: Planet list displays correctly in game

**Notes:**

---

### Task 4.2: Update system_tree_panel.py [Simple]
**File:** `game/ui/panels/system_tree_panel.py` (12 hasattr)
**Tests:** Manual testing of system tree

- [ ] Add Protocol imports at top of file
- [ ] Search file for hasattr patterns
- [ ] Replace duck typing with TypeGuard calls where appropriate
- [ ] Verify: System tree works correctly in game

**Notes:**

---

### Task 4.3: Update fleet_report_window.py [Simple]
**File:** `game/ui/screens/fleet_report_window.py` (11 hasattr)
**Tests:** Manual testing of fleet report

- [ ] Add Protocol imports at top of file
- [ ] Search file for hasattr patterns
- [ ] Replace duck typing with TypeGuard calls where appropriate
- [ ] Verify: Fleet reports display correctly in game

**Notes:**

---

### Task 4.4: Evaluate Other High-Count Files [Simple]
**Files to review:**
- `game/ui/screens/workshop_event_router.py` (8 hasattr)
- `game/ui/screens/workshop_screen.py` (7 hasattr)
- `game/ui/screens/race_setup_screen.py` (7 hasattr)
- `game/ui/screens/build_queue_screen.py` (6 hasattr)

- [ ] Review each file for duck typing patterns
- [ ] Replace patterns that match existing Protocols
- [ ] Skip patterns that are UI-specific or lazy initialization
- [ ] Document any decisions in decisions.md

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/ui/ -v` - UI tests pass
- [ ] Run: `pytest tests/ --testmon -q` - no regressions
- [ ] Manual test: All UI panels work correctly
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
