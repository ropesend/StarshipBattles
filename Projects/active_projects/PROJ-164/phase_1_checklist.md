# Phase 1: Add Helper Method + Unit Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-164 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `_parse_primary_value()` to Ability base class and write comprehensive tests.

---

## Tasks

### Task 1.1: Add `_parse_primary_value()` to `Ability` base class [Simple]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_ability_base.py -v`

- [ ] Add static method after `_parse_scope()` (after line 110):
  ```python
  @staticmethod
  def _parse_primary_value(data, key: str = 'value', default: float = 0.0) -> float:
      """
      Parse a primary numeric value from ability data.

      Handles three input formats:
      - Primitive numeric (int/float): Returns float(data) directly
      - Dict with key: Returns float(data[key]) or default
      - Other (str, None, etc.): Returns default

      Args:
          data: Raw ability data (dict, int, float, or other)
          key: Dict key to look up (default: 'value')
          default: Fallback value if key missing (default: 0.0)

      Returns:
          Parsed float value
      """
      if isinstance(data, (int, float)):
          return float(data)
      if isinstance(data, dict):
          return float(data.get(key, default))
      return float(default)
  ```
- [ ] Verify existing tests still pass

**Notes:**

### Task 1.2: Write unit tests for `_parse_primary_value()` [Simple]
**File:** `tests/unit/simulation/components/abilities/test_ability_base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_ability_base.py -v`

- [ ] Add test class `TestParsePrimaryValue` with test cases:
  - [ ] `test_int_input` — `Ability._parse_primary_value(42)` → `42.0`
  - [ ] `test_float_input` — `Ability._parse_primary_value(3.14)` → `3.14`
  - [ ] `test_zero_int` — `Ability._parse_primary_value(0)` → `0.0`
  - [ ] `test_negative` — `Ability._parse_primary_value(-5.5)` → `-5.5`
  - [ ] `test_dict_with_value_key` — `{'value': 100}` → `100.0`
  - [ ] `test_dict_missing_key_returns_default` — `{'other': 5}` → `0.0`
  - [ ] `test_dict_custom_key` — `({'amount': 7}, key='amount')` → `7.0`
  - [ ] `test_dict_custom_default` — `({}, default=99.0)` → `99.0`
  - [ ] `test_string_returns_default` — `"hello"` → `0.0`
  - [ ] `test_none_returns_default` — `None` → `0.0`
  - [ ] `test_bool_treated_as_int` — `True` → `1.0`
  - [ ] `test_dict_with_int_value` — `{'value': 5}` → `5.0`
- [ ] Run tests, verify all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
