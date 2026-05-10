# Phase 4: Update Remaining UI Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate remaining UI files with significant duck typing

---

## Tasks

### Task 4.1: Update planet_list_window.py [Medium]
**File:** `game/ui/panels/planet_list_window.py` (15 hasattr)
**Tests:** `pytest tests/ui/ -k "planet" -v`

- [x] Add Protocol imports at top of file
- [x] Search file for hasattr patterns
- [x] Replace duck typing with TypeGuard calls where appropriate
- [x] Verify: Planet list displays correctly in game

**Notes:** Reviewed all 15 hasattr patterns - all are self attribute checks, optional display attributes, or defensive checks on known planet objects. No type discrimination patterns need Protocol replacement.

---

### Task 4.2: Update system_tree_panel.py [Simple]
**File:** `game/ui/panels/system_tree_panel.py` (12 hasattr)
**Tests:** Manual testing of system tree

- [x] Add Protocol imports at top of file
- [x] Search file for hasattr patterns
- [x] Replace duck typing with TypeGuard calls where appropriate
- [x] Verify: System tree works correctly in game

**Notes:** Replaced 7 duck typing patterns (lines 152-163) with Protocol TypeGuards: is_planet(), is_star(), is_warp_point(), is_star_system(). Remaining 5 hasattr are for UI tree item attributes.

---

### Task 4.3: Update fleet_report_window.py [Simple]
**File:** `game/ui/screens/fleet_report_window.py` (11 hasattr)
**Tests:** Manual testing of fleet report

- [x] Add Protocol imports at top of file
- [x] Search file for hasattr patterns
- [x] Replace duck typing with TypeGuard calls where appropriate
- [x] Verify: Fleet reports display correctly in game

**Notes:** Reviewed all 11 hasattr patterns - all are self attribute checks or widget method checks. No type discrimination patterns need Protocol replacement.

---

### Task 4.4: Evaluate Other High-Count Files [Simple]
**Files to review:**
- `game/ui/screens/workshop_event_router.py` (8 hasattr)
- `game/ui/screens/workshop_screen.py` (7 hasattr)
- `game/ui/screens/race_setup_screen.py` (7 hasattr)
- `game/ui/screens/build_queue_screen.py` (6 hasattr)

- [x] Review each file for duck typing patterns
- [x] Replace patterns that match existing Protocols
- [x] Skip patterns that are UI-specific or lazy initialization
- [x] Document any decisions in decisions.md

**Notes:** Reviewed all files. All hasattr patterns are GUI attribute checks or validation assertions, not type discrimination. build_queue_screen.py has 2 defensive validation checks on planet but these are redundant since IPlanet guarantees these attributes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/ui/ -v` - UI tests pass
- [x] Run: `pytest tests/ --testmon -q` - no regressions (8 tests)
- [x] Manual test: All UI panels work correctly
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
