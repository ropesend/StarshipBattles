# Phase 6: UI Layer - Asset Manager & Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix UI layer error handling while maintaining graceful degradation.

---

## Tasks

### Task 6.1: Update asset_manager.py Error Handling [Medium]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/test_asset_manager.py`

- [x] Fix ERR-001: lines 102-124 - Replace generic catches with specific types
- [x] Fix ERR-003: line 29 - Replace `raise Exception()` with `StateException`
- [x] Fix ERR-10: lines 73-82, 102-104 - Add asset load tracking and notification
- [x] Add logging before fallback to placeholder
- [x] Track which assets failed to load for debugging
- [x] Verify: Tests pass

**Notes:** Replaced generic Exception with FileNotFoundError and pygame.error

---

### Task 6.2: Update ship_theme_manager.py Error Handling [Medium]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/unit/ui/assets/test_ship_theme_manager.py`

- [x] Fix ERR-003: line 46 - Replace `raise Exception()` with `StateException`
- [x] Replace generic `Exception` catches with specific types
- [x] Add logging for theme loading failures with context
- [x] Verify: Tests pass

**Notes:** StateException for singleton, FileNotFoundError/pygame.error for image loading

---

### Task 6.3: Update formation_editor.py Error Handling [Medium]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_formation_editor.py`

- [x] Fix ERR-11: line 212 - Add specific handling for each error type
- [x] Distinguish "file not found" vs "invalid JSON" vs "missing data"
- [x] Provide user-friendly error messages for each case
- [x] Verify: Tests pass

**Notes:** Added log_error/log_info, distinguished FileNotFoundError/JSONDecodeError/KeyError/ValueError

---

### Task 6.4: Update builder/main.py Error Handling [Medium]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_main.py`

- [x] Fix ERR-010: lines 48-55 - Add context managers or finally blocks
- [x] Fix ERR-013: lines 62-64 - Standardize to custom logger
- [x] Replace generic `Exception` catches with specific types
- [x] Verify: Tests pass

**Notes:** _reload_data() now catches OSError/JSONDecodeError/KeyError/ValueError/TypeError

---

### Task 6.5: Update event_bus.py Error Handling [Simple]
**File:** `game/ui/screens/builder/event_bus.py` (or `ui/builder/event_bus.py`)
**Tests:** `pytest tests/unit/ui/builder/test_event_bus.py`

- [x] Fix ERR-01 (Consistency): line 21 - Replace `print()` with `log_error()`
- [x] Fix ERR-02 (Consistency): Always bind exception variable `as e:`
- [x] Add event type context to error messages
- [x] Verify: Tests pass

**Notes:** Added log_error with callback name and event type context

---

### Task 6.6: Update battle_screen.py Error Handling [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen.py`

- [x] Fix silent `except Exception: pass` at line 205
- [x] Add logging for arc drawing failures
- [x] Bind exception variable for context
- [x] Verify: Tests pass

**Notes:** Now catches ValueError/pygame.error with log_debug message

---

### Task 6.7: Update build_queue_screen.py Error Handling [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [x] Fix ERR-07: lines 68-71 - Make validation consistent
- [x] Fix silent `except Exception: pass` at line 870
- [x] Add logging for screenshot notification failures
- [x] Verify: Tests pass

**Notes:** _show_screenshot_toast() now catches AttributeError/pygame.error with log_debug

---

### Task 6.8: Update setup.py Error Handling [Simple]
**File:** `game/ui/screens/setup.py`
**Tests:** `pytest tests/unit/ui/screens/test_setup.py`

- [x] Fix silent `except Exception: pass` at lines 41, 74
- [x] Add logging for invalid ship/formation files
- [x] Include file path in skip messages
- [x] Verify: Tests pass

**Notes:** All scan/load/save functions now use specific exception types with log_warning/log_error

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/ui/`
- [x] No regressions: `pytest tests/ --testmon`
- [x] Run game and verify UI works without crashes
- [x] Verify error logs show context for failures
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
