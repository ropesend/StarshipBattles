# Phase 5: Strategy Layer - Save/Load & Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix error handling in save/load system and strategy services.

---

## Tasks

### Task 5.1: Update save_game_service.py Error Handling [Complex]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/test_save_game_service.py`

- [ ] Fix ERR-06: lines 109-111, 173-176 - Categorize exceptions with specific error codes
- [ ] Fix ERR-006: Add `raise from e` for exception chaining
- [ ] Replace bare `except Exception:` at line 441 with specific types
- [ ] Use `PersistenceException` for save/load failures
- [ ] Add error codes distinguishing disk full vs permission denied vs corrupt data
- [ ] Include save path, turn number in all error messages
- [ ] Verify: Tests pass

**Notes:**

---

### Task 5.2: Update design_library.py Error Handling [Medium]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/test_design_library.py`

- [ ] Replace generic `Exception` catches with specific types
- [ ] Add `raise from e` for exception chaining
- [ ] Use `PersistenceException` for file operations
- [ ] Add design ID context to all error messages
- [ ] Verify: Tests pass

**Notes:**

---

### Task 5.3: Update game_session.py Exception Context [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/test_game_session.py`

- [ ] Update `from_dict()` to include field names in error messages
- [ ] Wrap `KeyError` with `PersistenceException` and context
- [ ] Add session/turn context to reconstruction errors
- [ ] Verify: Tests pass

**Notes:**

---

### Task 5.4: Update persistence.py Error Handling [Simple]
**File:** `game/simulation/systems/persistence.py`
**Tests:** `pytest tests/unit/simulation/test_persistence.py`

- [ ] Replace generic `Exception` catches with specific types
- [ ] Use `PersistenceException` for file operations
- [ ] Add file path context to all errors
- [ ] Verify: Tests pass

**Notes:**

---

### Task 5.5: Update retreat_manager.py Error Handling [Simple]
**File:** `game/simulation/managers/retreat_manager.py`
**Tests:** `pytest tests/unit/simulation/test_retreat_manager.py`

- [ ] Replace generic `Exception` catches with specific types
- [ ] Add context to error messages
- [ ] Verify: Tests pass

**Notes:**

---

### Task 5.6: Update race_library.py Error Handling [Simple]
**File:** `game/strategy/systems/race_library.py`
**Tests:** `pytest tests/unit/strategy/test_race_library.py`

- [ ] Replace generic `Exception` catches with specific types
- [ ] Add race ID context to error messages
- [ ] Verify: Tests pass

**Notes:**

---

### Task 5.7: Update Strategy Validation with Error Codes [Simple]
**File:** `game/strategy/validation/base.py` and subclasses
**Tests:** `pytest tests/unit/strategy/validation/`

- [ ] Update validation rules to use `ErrorCode` enum
- [ ] Add error codes to all `ValidationResult.add_error()` calls
- [ ] Verify: Tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/strategy/`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Save game, verify success
- [ ] Load game, verify success
- [ ] Corrupt a save file, verify specific error message
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
