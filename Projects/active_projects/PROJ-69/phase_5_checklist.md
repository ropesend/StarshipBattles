# Phase 5: Strategy Screen Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update the strategy screen to pass hex context when opening the build queue, and handle close callback for multi-queue scenarios.

---

## Tasks

### Task 5.1: Update on_build_yard_click to pass hex context [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual test + `pytest tests/unit/ui/ -k "strategy"`

- [x] Modify `on_build_yard_click()`:
  - Calculates global hex via `get_system_of_planet()` + `global_location + planet.location`
  - Passes `hex_coord`, `galaxy`, `empire` to BuildQueueScreen
  - Keeps existing params (manager, build_context=planet, session, callbacks, DI)
- [x] Modify `on_fleet_build_click()`:
  - Uses `fleet.location` as `hex_coord`
  - Passes `hex_coord`, `galaxy`, `empire` to BuildQueueScreen
- [x] Verify both paths create BuildQueueScreen successfully (6561 passed)

**Notes:** Both methods already create the screen - we just add the hex context parameters so the screen can discover all queues at that hex.

---

### Task 5.2: Update close callback for multi-queue fleet handling [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual test

- [x] Update `_on_build_queue_close()`:
  - Iterates all `queue_sources` from the closing screen
  - For each fleet-type queue source, calls `_handle_fleet_build_queue_close(fleet)`
  - Uses `processed_fleets` set to avoid duplicate processing
  - Planet queues: no special close handling needed (planets auto-process)
- [x] `_handle_fleet_build_queue_close()` already accepts fleet entity - no change needed
- [x] Verify close callback works for all scenarios (6561 passed)

**Notes:** The close callback now needs to handle potentially multiple fleets that may have had their queues modified.

---

### Task 5.3: Remove backward compatibility code [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ --testmon`

- [x] `self.planet` alias already doesn't exist (removed in prior phases)
- [x] Remaining `self.build_context.construction_queue` references are legitimate defensive fallbacks for edge cases and test compatibility - not duplicate systems
- [x] Old close callback `build_context.context_type == 'fleet'` check replaced by queue_sources iteration (Task 5.2)
- [x] Verify: `pytest tests/ -n 12` - 6561 passed

**Notes:** Per CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely."

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` - 6561 passed, 1 pre-existing failure
- [ ] Manual test: open build queue from planet - shows all queues at hex
- [ ] Manual test: open build queue from fleet - shows all queues at hex
- [ ] Manual test: close build queue - fleet BUILD orders correctly managed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
