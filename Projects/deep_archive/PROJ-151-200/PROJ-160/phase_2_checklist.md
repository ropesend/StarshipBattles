# Phase 2: Refactor Command Handlers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-160 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace system iteration with new method in command handlers

---

## Tasks

### Task 2.1: Refactor ColonizeCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestColonizeCommandHandler -v`

- [x] Replace lines 121-125 with single call to `session.galaxy.get_planet_global_hex(target_planet)`

**Notes:** Reduced 5 lines to 1 line at command_handlers.py:121

---

### Task 2.2: Refactor TransferCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestTransferCommandHandler -v`

- [x] Replace lines 417-421 with single call to `session.galaxy.get_planet_global_hex(planet)`

**Notes:** Reduced 5 lines to 1 line at command_handlers.py:411

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Code compiles without errors
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

**Note:** Tests may fail until Phase 3 updates the mocks.
