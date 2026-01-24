# Phase 3: Error Handling Hardening

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-10 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Improve error handling to make debugging easier and prevent silent failures
**Priority:** MAJOR

---

## Tasks

### Task 3.1: ERR-01 - Fix Bare Except in Save Selection [Simple]
**File:** `game/ui/screens/save_selection_window.py:148,171`
**Tests:** `pytest tests/unit/ui/test_save_selection_window.py`

**Issue:** Bare `except:` clauses catch all exceptions including SystemExit and KeyboardInterrupt without logging. Datetime parsing failures are silent.

**Implementation:**
- [ ] Replace `except:` with `except Exception as e:`
- [ ] Add logging: `log_error(f"Failed to parse timestamp {timestamp}: {e}")`
- [ ] Consider if ValueError is the expected exception type
- [ ] Test with malformed timestamps

**Notes:** 5-minute fix. Pattern appears twice in file.

---

### Task 3.2: ERR-02 - Fix Silent Tkinter Init Failure [Simple]
**File:** `game/simulation/systems/persistence.py:12`
**Tests:** `pytest tests/unit/simulation/test_persistence.py`

**Issue:** Bare except during Tkinter initialization. If Tkinter fails to initialize, file dialogs silently fail later with no clear error message.

**Implementation:**
- [ ] Add logging when tk_root initialization fails
- [ ] Log the specific exception for debugging
- [ ] Consider showing warning to user that file dialogs may not work
- [ ] Test on headless system (no display)

**Notes:** 10-minute fix. Improves debuggability.

---

### Task 3.3: ERR-05 - Improve Formula Eval Error Handling [Medium]
**File:** `game/simulation/formula_system.py:31`
**Tests:** `pytest tests/unit/simulation/test_formula_system.py`

**Issue:** Formula evaluation catches ANY exception and returns 0. Silent math errors lead to incorrect game balance calculations going undetected.

**Implementation:**
- [ ] Create result object with error flag instead of bare return
- [ ] Log formula errors with context (formula string, variable values)
- [ ] Return NaN or raise for invalid formulas during development
- [ ] Keep silent fallback only for production builds
- [ ] Add warning system for formula errors

**Notes:** This may be addressed by Task 1.1 (replacing eval). Coordinate with that task.

---

### Task 3.4: Audit and Fix Remaining Error Handling [Medium]
**Files:** Multiple (see ERR-06 through ERR-23 in report)
**Tests:** Various

**Issue:** Multiple instances of swallowed exceptions, missing logging, and inconsistent error handling patterns throughout the codebase.

**Implementation:**
- [ ] Review ERR-06: Silent JSON parse in setup_data_io.py
- [ ] Review ERR-07: Swallowed exception in save_game_service.py:450
- [ ] Review ERR-08: Missing error context in design_selector_window.py:404
- [ ] Review ERR-09: Inconsistent logging in component.py:628,640
- [ ] Review ERR-10: Silent ability creation failure in abilities/__init__.py:107
- [ ] For each: Add appropriate logging and error context
- [ ] Establish error handling pattern guidelines

**Notes:** This is a cleanup pass. Focus on high-impact areas first.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No bare except clauses in modified files
- [ ] All exceptions are logged with context
- [ ] Debugging is easier (errors are traceable)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
