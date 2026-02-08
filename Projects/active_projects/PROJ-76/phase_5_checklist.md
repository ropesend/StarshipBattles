# Phase 5: Navigation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Enable row click to navigate to hex build screen

---

## Tasks

### Task 5.1: Implement row click handler [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** 12 new tests in test_empire_build_queue_window.py (85 total)

- [x] Track clicked row index from mouse position
- [x] Get corresponding `BuildQueueSource`
- [x] Get hex coordinate for source:
  - Planet: `galaxy.get_system_of_planet(planet).global_location + planet.location`
  - Fleet: `fleet.location`
- [x] Call `on_navigate_to_hex(hex_coord, source)` callback
- [x] Re-click on already-selected row triggers navigation (double-click pattern)

**Notes:**
- `get_hex_for_source(source)` resolves hex coordinate for any source type
- `navigate_to_source(source)` selects the source, resolves hex, calls callback
- process_event detects re-click on selected row and calls navigate_to_source
- Window closing on navigation is deferred to Phase 7 (strategy screen callback handles it)

---

### Task 5.2: Wire up navigation callback [Deferred to Phase 7]

**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Will be added in Phase 7

- [x] Add `on_navigate_to_hex_build(hex_coord)` callback method (implemented in Phase 7)
- [x] Close empire build queue window (implemented in Phase 7)
- [x] Open `BuildQueueScreen` for the specified hex (implemented in Phase 7)
- [x] Pass galaxy, empire, hex_coord to BuildQueueScreen (implemented in Phase 7)

**Notes:**
- Deferred to Phase 7 (Integration) since the empire build queue window
  is not yet wired into the strategy screen. Phase 7 will create the window
  and set up this callback simultaneously.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] Task 5.1 complete with 12 new tests
- [x] No regressions: `pytest tests/ --testmon` (85 passed, 2 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
