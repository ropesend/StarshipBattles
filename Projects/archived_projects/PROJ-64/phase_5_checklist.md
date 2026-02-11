# Phase 5: UI Screens Part B — Workshop, Test Lab, Strategy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-64 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Narrow exception handling in the largest/most complex screen files.
**Tests:** `pytest tests/unit/ui/ tests/integration/ -x`

---

## Tasks

### Task 5.1: ui/screens/workshop_screen.py (3 sites) [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Status:** N/A - File already clean (no exception sites)

- [x] File has no `except Exception` sites - already clean from prior refactoring
- [x] Verified: file is 595 lines, no exception sites found

**Notes:** File was refactored in PROJ-61, exception sites no longer exist.

---

### Task 5.2: ui/screens/workshop_context.py (1 site) [Simple]
**File:** `game/ui/screens/workshop_context.py`
**Status:** N/A - File already clean (no exception sites)

- [x] File has no `except Exception` sites - already clean

**Notes:** No exception sites found.

---

### Task 5.3: ui/screens/workshop_data_loader.py (1 site) [Simple]
**File:** `game/ui/screens/workshop_data_loader.py`
**Line:** 150
**Pattern:** Data loading with result-based error collection.

- [x] Line 150: Replaced `except Exception as e:` with `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:`
- [x] Added `import json` to imports
- [x] Verify: tests pass

**Notes:** Narrowed to data loading exceptions.

---

### Task 5.4: ui/screens/test_lab_screen.py (6 sites) [Medium]
**File:** `game/ui/screens/test_lab_screen.py`
**Status:** N/A - File no longer exists

- [x] File does not exist - removed in prior refactoring

**Notes:** test_lab_screen.py was removed, no sites to process.

---

### Task 5.5: ui/screens/test_lab.py (3 sites) [Simple]
**File:** `game/ui/screens/test_lab.py`
**Status:** N/A - File no longer exists

- [x] File does not exist - removed in prior refactoring

**Notes:** test_lab.py was removed, no sites to process.

---

### Task 5.6: ui/screens/strategy_screen.py (2 sites) [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Lines:** 401, 520
**Pattern:** Report refresh and planet image loading.

- [x] Line 401: Replaced `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error, AttributeError, KeyError) as e:`
- [x] Line 520: Replaced `except Exception as e:` with `except (FileNotFoundError, OSError, pygame.error, AttributeError) as e:`
- [x] Verify: tests pass

**Notes:** Both sites narrowed to asset loading exceptions.

---

### Task 5.7: ui/screens/strategy_input_handler.py (1 site) [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Line:** 520
**Pattern:** Screenshot toast notification.

- [x] Line 520: Replaced `except Exception as e:` with `except (OSError, RuntimeError, pygame.error) as e:`
- [x] Verify: tests pass

**Notes:** Narrowed to toast/window creation exceptions.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/unit/ui/ tests/integration/ -x` - 1338 passed
- [x] Grep: verify no broad catches remain in Phase 5 files - all clean
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6

## Summary
- **Sites in checklist:** 17 (across 7 files)
- **Files existing:** 3 (workshop_data_loader.py, strategy_screen.py, strategy_input_handler.py)
- **Files already clean:** 2 (workshop_screen.py, workshop_context.py)
- **Files removed:** 2 (test_lab_screen.py, test_lab.py)
- **Sites narrowed:** 4
- **Tests:** 1338 passed
