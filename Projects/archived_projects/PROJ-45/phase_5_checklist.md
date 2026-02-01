# Phase 5: Strategy Layer - Save/Load & Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix error handling in save/load system and strategy services.

---

## Tasks

### Task 5.1: Update save_game_service.py Error Handling [Complex]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/test_save_game_service.py`

- [x] Fix ERR-06: lines 109-111, 173-176 - Categorize exceptions with specific error codes
- [x] Fix ERR-006: Add `raise from e` for exception chaining
- [x] Replace bare `except Exception:` at line 441 with specific types
- [x] Use `PersistenceException` for save/load failures
- [x] Add error codes distinguishing disk full vs permission denied vs corrupt data
- [x] Include save path, turn number in all error messages
- [x] Verify: Tests pass (27 passed)

**Notes:**

---

### Task 5.2: Update design_library.py Error Handling [Medium]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/test_design_library.py`

- [x] Replace generic `Exception` catches with specific types
- [x] Add `raise from e` for exception chaining
- [x] Use `PersistenceException` for file operations
- [x] Add design ID context to all error messages
- [x] Verify: Tests pass (24 passed)

**Notes:** Updated 7 exception handlers with specific types (json.JSONDecodeError, PermissionError, OSError, KeyError, TypeError, ValueError)

---

### Task 5.3: Update game_session.py Exception Context [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/test_game_session.py`

- [x] Update `from_dict()` to include field names in error messages
- [x] Wrap `KeyError` with `PersistenceException` and context
- [x] Add session/turn context to reconstruction errors
- [x] Verify: Tests pass (12 passed)

**Notes:** Wrapped KeyError in PersistenceException with error codes P001/P002/P003 for config/galaxy/empires

---

### Task 5.4: Update persistence.py Error Handling [Simple]
**File:** `game/simulation/systems/persistence.py`
**Tests:** `pytest tests/unit/simulation/test_persistence.py`

- [x] Replace generic `Exception` catches with specific types
- [x] Use `PersistenceException` for file operations
- [x] Add file path context to all errors
- [x] Verify: Tests pass

**Notes:** Updated ShipIO save/load with json.JSONDecodeError, PermissionError, OSError, KeyError, TypeError, ValueError

---

### Task 5.5: Update retreat_manager.py Error Handling [Simple]
**File:** `game/simulation/managers/retreat_manager.py`
**Tests:** `pytest tests/unit/simulation/test_retreat_manager.py`

- [x] Replace generic `Exception` catches with specific types
- [x] Add context to error messages
- [x] Verify: Tests pass (31 passed)

**Notes:** N/A - retreat_manager.py has no generic exception handlers

---

### Task 5.6: Update race_library.py Error Handling [Simple]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/unit/strategy/test_race_library.py`

- [x] Replace generic `Exception` catches with specific types
- [x] Add race ID context to error messages
- [x] Verify: Tests pass

**Notes:** Updated 6 exception handlers with json.JSONDecodeError, PermissionError, OSError, KeyError, TypeError, ValueError

---

### Task 5.7: Update Strategy Validation with Error Codes [Simple]
**File:** `game/strategy/validation/base.py` and subclasses
**Tests:** `pytest tests/unit/strategy/validation/`

- [x] Update validation rules to use `ErrorCode` enum
- [x] Add error codes to all `ValidationResult.add_error()` calls
- [x] Verify: Tests pass

**Notes:** Already implemented - ColonizeValidator uses error codes (NO_CANDIDATES, ALREADY_OWNED, WRONG_LOCATION)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/` (838 passed)
- [x] No regressions: `pytest tests/` (5781 passed, 3 skipped)
- [x] Save game, verify success (tested via unit tests)
- [x] Load game, verify success (tested via unit tests)
- [x] Corrupt a save file, verify specific error message (tested via unit tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
