# Phase 1: Validation Helper Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 1`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/core/test_validation_helpers.py -v`

## Task 1.1: Create deserialization validation helper module [Medium]
**File:** `game/core/validation_helpers.py` (NEW)
**Tests:** `pytest tests/unit/core/test_validation_helpers.py`

- [x] Create `game/core/validation_helpers.py`
- [x] Implement `require_keys(data: dict, keys: list[str], context: str) -> None`
  - Checks all keys exist in data
  - Raises PersistenceException with code=ErrorCode.CORRUPT_DATA.value
  - Context dict includes: missing_keys list, source string
- [x] Implement `validate_enum(value: str, enum_class: type, field_name: str, context: str)`
  - Returns enum member on success
  - Catches KeyError and ValueError from enum lookup
  - Raises PersistenceException with valid_values in context
- [x] Implement `validate_positive(value, field_name: str, context: str) -> None`
  - Raises PersistenceException if value <= 0
  - Context includes field_name, value, expected="positive"
- [x] Implement `validate_non_negative(value, field_name: str, context: str) -> None`
  - Raises PersistenceException if value < 0
  - Context includes field_name, value, expected="non-negative"
- [x] Implement `validate_range(value, min_val, max_val, field_name: str, context: str) -> None`
  - Raises PersistenceException if value outside [min_val, max_val]
  - Context includes field_name, value, min, max
- [x] Implement `safe_from_dict(from_dict_fn, data: dict, context: str)`
  - Wraps a from_dict call
  - Catches (KeyError, TypeError, ValueError)
  - Raises PersistenceException with `from e` chaining
  - Context includes: error string, source context
- [x] Add imports: `from game.core.exceptions import PersistenceException` and `from game.core.error_codes import ErrorCode`
- [x] Add `__all__` exports for all 6 helpers

**Notes:** All 6 helpers implemented with full docstrings and type hints.

## Task 1.2: Write tests for validation helpers [Simple]
**File:** `tests/unit/core/test_validation_helpers.py` (NEW)
**Tests:** `pytest tests/unit/core/test_validation_helpers.py -v`

- [x] Test `require_keys` — all keys present → no exception
- [x] Test `require_keys` — missing one key → PersistenceException, 'missing_keys' in context
- [x] Test `require_keys` — missing multiple keys → all missing listed
- [x] Test `require_keys` — empty dict → all keys listed as missing
- [x] Test `validate_enum` — valid enum name → returns correct member
- [x] Test `validate_enum` — invalid name → PersistenceException, 'valid_values' in context
- [x] Test `validate_positive` — positive value (1, 0.5, 100) → passes
- [x] Test `validate_positive` — zero → PersistenceException
- [x] Test `validate_positive` — negative → PersistenceException
- [x] Test `validate_non_negative` — zero → passes
- [x] Test `validate_non_negative` — positive → passes
- [x] Test `validate_non_negative` — negative → PersistenceException
- [x] Test `validate_range` — value in range → passes
- [x] Test `validate_range` — below min → PersistenceException with min/max in context
- [x] Test `validate_range` — above max → PersistenceException with min/max in context
- [x] Test `safe_from_dict` — successful call → returns result
- [x] Test `safe_from_dict` — KeyError from inner → PersistenceException with `__cause__` set (from e)
- [x] Test `safe_from_dict` — TypeError from inner → PersistenceException with `__cause__` set

**Notes:** 21 tests total covering all helpers with positive and negative cases.

## Phase 1 Completion
- [x] All tasks above checked
- [x] `pytest tests/unit/core/test_validation_helpers.py -v` — all pass (21 passed)
- [x] `pytest tests/ -n 12` — no regressions (11993 passed, 1 skipped)
