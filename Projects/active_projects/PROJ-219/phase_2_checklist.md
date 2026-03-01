# Phase 2: Wire Up Galaxy References

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Ensure Empire instances have galaxy reference set after construction/deserialization

---

## Tasks

### Task 2.1: Update GameInitializer [Simple]
**File:** `game/strategy/engine/game_initializer.py`
**Tests:** `pytest tests/integration/strategy/test_game_initializer.py`

- [ ] In `initialize()` method, after line 53 (after `_setup_initial_scenario`), add:
  ```python
  # PROJ-219: Set galaxy back-references for auto-registration
  for empire in empires:
      empire.set_galaxy(galaxy)
  ```
- [ ] Verify: Empires created via GameInitializer have `_galaxy` set

**Notes:** Insert the loop before `return galaxy, empires` (line 55).

---

### Task 2.2: Update GameSession.from_dict [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/integration/save_load/`

- [ ] After empire deserialization (line 349, after exception block), before fleet registration loop (line 353), add:
  ```python
  # PROJ-219: Set galaxy back-references for auto-registration
  for empire in session.empires:
      empire.set_galaxy(session.galaxy)
  ```
- [ ] Keep the existing fleet registration loop (lines 353-357) - deserialized fleets need explicit registration
- [ ] Verify: Save/load round-trip still works
- [ ] Verify: Loaded empires have `_galaxy` set for future operations

**Notes:**

---

### Task 2.3: Add integration test for wiring [Simple]
**File:** `tests/integration/strategy/test_fleet_registration_wiring.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_wiring.py`

Create tests verifying galaxy wiring:
- [ ] `test_game_initializer_sets_galaxy_on_empires`
- [ ] `test_game_session_from_dict_sets_galaxy_on_empires`
- [ ] `test_new_fleet_after_load_registers_automatically`

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/integration/save_load/` - all pass
- [ ] Run `pytest tests/ --testmon` - no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
