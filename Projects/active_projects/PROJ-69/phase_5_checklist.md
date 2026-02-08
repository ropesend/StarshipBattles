# Phase 5: Strategy Screen Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update the strategy screen to pass hex context when opening the build queue, and handle close callback for multi-queue scenarios.

---

## Tasks

### Task 5.1: Update on_build_yard_click to pass hex context [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual test + `pytest tests/unit/ui/ -k "strategy"`

- [ ] Modify `on_build_yard_click()` (lines 358-396):
  - Calculate global hex for the selected planet:
    ```python
    parent_sys = self.session.galaxy.get_system_of_planet(planet)
    hex_coord = parent_sys.global_location + planet.location
    ```
  - Pass additional params to `BuildQueueScreen`:
    - `hex_coord=hex_coord`
    - `galaxy=self.session.galaxy`
    - `empire=self.current_empire`
  - Keep existing params (manager, build_context=planet, session, callbacks, DI)
- [ ] Modify `on_fleet_build_click()` (lines 449-487):
  - Use `fleet.location` as `hex_coord`
  - Pass additional params: `hex_coord`, `galaxy`, `empire`
- [ ] Verify both paths create BuildQueueScreen successfully

**Notes:** Both methods already create the screen - we just add the hex context parameters so the screen can discover all queues at that hex.

---

### Task 5.2: Update close callback for multi-queue fleet handling [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual test

- [ ] Update `_on_build_queue_close()` (lines 398-425):
  - Get all queue sources from the closing screen: `self.build_queue_screen.queue_sources`
  - For each fleet-type queue source:
    - If `source.construction_queue` is not empty: ensure fleet has BUILD order (same as current `_handle_fleet_build_queue_close` logic)
    - If `source.construction_queue` is empty: remove BUILD order if present
  - Planet queues: no special close handling needed (planets auto-process)
- [ ] Update `_handle_fleet_build_queue_close()` to accept a list of fleet entities or iterate queue sources
- [ ] Verify close callback works for:
  - Single planet selected
  - Single fleet selected
  - Hex with both planet and fleet

**Notes:** The close callback now needs to handle potentially multiple fleets that may have had their queues modified.

---

### Task 5.3: Remove backward compatibility code [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Remove `self.planet = build_context` alias (line 59) if no longer referenced
- [ ] Remove any remaining `self.build_context.construction_queue` direct references (replaced by `active_queue_source.construction_queue`)
- [ ] Search for and remove any other backward compat code introduced during transition
- [ ] Verify: `pytest tests/ --testmon` - all pass

**Notes:** Per CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely."

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: open build queue from planet - shows all queues at hex
- [ ] Manual test: open build queue from fleet - shows all queues at hex
- [ ] Manual test: close build queue - fleet BUILD orders correctly managed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
