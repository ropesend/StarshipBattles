# Phase 1: Validation Helper Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> - Run `python Projects/scripts/validate_phase.py PROJ-171 1`
> - Ensure ALL boxes below are checked
> - Run phase tests: `pytest tests/unit/core/test_validation_helpers.py -v`

## Task 1.1: Create deserialization validation helper module [Medium]
**File:** `game/core/validation_helpers.py` (NEW)
**Tests:** `pytest tests/unit/core/test_validation_helpers.py`

- [ ] Create `game/core/validation_helpers.py`
- [ ] Implement `require_keys(data: dict, keys: list[str], context: str) -> None`
  - Checks all keys exist in data
  - Raises PersistenceException with code=ErrorCode.CORRUPT_DATA.value
  - Context dict includes: missing_keys list, source string
- [ ] Implement `validate_enum(value: str, enum_class: type, field_name: str, context: str)`
  - Returns enum member on success
  - Catches KeyError and ValueError from enum lookup
  - Raises PersistenceException with valid_values in context
- [ ] Implement `validate_positive(value, field_name: str, context: str) -> None`
  - Raises PersistenceException if value <= 0
  - Context includes field_name, value, expected="positive"
- [ ] Implement `validate_non_negative(value, field_name: str, context: str) -> None`
  - Raises PersistenceException if value < 0
  - Context includes field_name, value, expected="non-negative"
- [ ] Implement `validate_range(value, min_val, max_val, field_name: str, context: str) -> None`
  - Raises PersistenceException if value outside [min_val, max_val]
  - Context includes field_name, value, min, max
- [ ] Implement `safe_from_dict(from_dict_fn, data: dict, context: str)`
  - Wraps a from_dict call
  - Catches (KeyError, TypeError, ValueError)
  - Raises PersistenceException with `from e` chaining
  - Context includes: error string, source context
- [ ] Add imports: `from game.core.exceptions import PersistenceException` and `from game.core.error_codes import ErrorCode`
- [ ] Add `__all__` exports for all 6 helpers

**Notes:**

## Task 1.2: Write tests for validation helpers [Simple]
**File:** `tests/unit/core/test_validation_helpers.py` (NEW)
**Tests:** `pytest tests/unit/core/test_validation_helpers.py -v`

- [ ] Test `require_keys` — all keys present → no exception
- [ ] Test `require_keys` — missing one key → PersistenceException, 'missing_keys' in context
- [ ] Test `require_keys` — missing multiple keys → all missing listed
- [ ] Test `require_keys` — empty dict → all keys listed as missing
- [ ] Test `validate_enum` — valid enum name → returns correct member
- [ ] Test `validate_enum` — invalid name → PersistenceException, 'valid_values' in context
- [ ] Test `validate_positive` — positive value (1, 0.5, 100) → passes
- [ ] Test `validate_positive` — zero → PersistenceException
- [ ] Test `validate_positive` — negative → PersistenceException
- [ ] Test `validate_non_negative` — zero → passes
- [ ] Test `validate_non_negative` — positive → passes
- [ ] Test `validate_non_negative` — negative → PersistenceException
- [ ] Test `validate_range` — value in range → passes
- [ ] Test `validate_range` — below min → PersistenceException with min/max in context
- [ ] Test `validate_range` — above max → PersistenceException with min/max in context
- [ ] Test `safe_from_dict` — successful call → returns result
- [ ] Test `safe_from_dict` — KeyError from inner → PersistenceException with `__cause__` set (from e)
- [ ] Test `safe_from_dict` — TypeError from inner → PersistenceException with `__cause__` set

## Phase 1 Completion
- [ ] All tasks above checked
- [ ] `pytest tests/unit/core/test_validation_helpers.py -v` — all pass
- [ ] `pytest tests/ --testmon` — no regressions
