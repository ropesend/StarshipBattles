# Phase 3: Fix save_game_service NameError (BUG-4) [Simple]

**Objective:** Fix `json.JSONDecodeError` reference to use the already-imported bare `JSONDecodeError`.
**Status:** Not Started

---

## Task 3.1: Fix the except clause [Simple]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/ -v`
- [ ] Read line 13 to confirm import: `from json import JSONDecodeError`
- [ ] Read line 463 to confirm the bug: `except (PermissionError, OSError, json.JSONDecodeError)`
- [ ] Change `json.JSONDecodeError` to `JSONDecodeError` on line 463
- [ ] Verify line 282 already uses bare `JSONDecodeError` (consistent usage)
- [ ] Run existing save_game_service tests — all pass
**Notes:**

## Task 3.2: Add test for the fixed error path [Simple]
**File:** `tests/unit/strategy/save_game_service/test_error_handling.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/test_error_handling.py -v`
- [ ] Write a test `test_get_save_info_handles_json_decode_error` that:
  - Mocks `load_json` to raise `JSONDecodeError`
  - Calls `get_save_info()` on the service
  - Asserts it returns `None` (graceful handling, no NameError)
- [ ] Run the test — verify it passes against the fixed code
- [ ] Verify it would FAIL against the old code (the `json.JSONDecodeError` NameError)
**Notes:**

## Phase 3 Verification
- [ ] All save_game_service tests pass
- [ ] No regressions: `pytest tests/ --testmon`
