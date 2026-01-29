# Phase 6: UI Layer - Asset Manager & Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix UI layer error handling while maintaining graceful degradation.

---

## Tasks

### Task 6.1: Update asset_manager.py Error Handling [Medium]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/test_asset_manager.py`

- [ ] Fix ERR-001: lines 102-124 - Replace generic catches with specific types
- [ ] Fix ERR-003: line 29 - Replace `raise Exception()` with `StateException`
- [ ] Fix ERR-10: lines 73-82, 102-104 - Add asset load tracking and notification
- [ ] Add logging before fallback to placeholder
- [ ] Track which assets failed to load for debugging
- [ ] Verify: Tests pass

**Notes:** Keep graceful degradation but add visibility

---

### Task 6.2: Update ship_theme_manager.py Error Handling [Medium]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/unit/ui/assets/test_ship_theme_manager.py`

- [ ] Fix ERR-003: line 46 - Replace `raise Exception()` with `StateException`
- [ ] Replace generic `Exception` catches with specific types
- [ ] Add logging for theme loading failures with context
- [ ] Verify: Tests pass

**Notes:**

---

### Task 6.3: Update formation_editor.py Error Handling [Medium]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_formation_editor.py`

- [ ] Fix ERR-11: line 212 - Add specific handling for each error type
- [ ] Distinguish "file not found" vs "invalid JSON" vs "missing data"
- [ ] Provide user-friendly error messages for each case
- [ ] Verify: Tests pass

**Notes:**

---

### Task 6.4: Update builder/main.py Error Handling [Medium]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_main.py`

- [ ] Fix ERR-010: lines 48-55 - Add context managers or finally blocks
- [ ] Fix ERR-013: lines 62-64 - Standardize to custom logger
- [ ] Replace generic `Exception` catches with specific types
- [ ] Verify: Tests pass

**Notes:**

---

### Task 6.5: Update event_bus.py Error Handling [Simple]
**File:** `game/ui/screens/builder/event_bus.py` (or `ui/builder/event_bus.py`)
**Tests:** `pytest tests/unit/ui/builder/test_event_bus.py`

- [ ] Fix ERR-01 (Consistency): line 21 - Replace `print()` with `log_error()`
- [ ] Fix ERR-02 (Consistency): Always bind exception variable `as e:`
- [ ] Add event type context to error messages
- [ ] Verify: Tests pass

**Notes:**

---

### Task 6.6: Update battle_screen.py Error Handling [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen.py`

- [ ] Fix silent `except Exception: pass` at line 205
- [ ] Add logging for arc drawing failures
- [ ] Bind exception variable for context
- [ ] Verify: Tests pass

**Notes:**

---

### Task 6.7: Update build_queue_screen.py Error Handling [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] Fix ERR-07: lines 68-71 - Make validation consistent
- [ ] Fix silent `except Exception: pass` at line 870
- [ ] Add logging for screenshot notification failures
- [ ] Verify: Tests pass

**Notes:**

---

### Task 6.8: Update setup.py Error Handling [Simple]
**File:** `game/ui/screens/setup.py`
**Tests:** `pytest tests/unit/ui/screens/test_setup.py`

- [ ] Fix silent `except Exception: pass` at lines 41, 74
- [ ] Add logging for invalid ship/formation files
- [ ] Include file path in skip messages
- [ ] Verify: Tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/ui/`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Run game and verify UI works without crashes
- [ ] Verify error logs show context for failures
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
