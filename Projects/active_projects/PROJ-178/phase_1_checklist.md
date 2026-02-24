# Phase 1: ShipInstance Validation & Docstrings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-178 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `validate_non_negative` to ShipInstance.from_dict and add missing `Raises:` docstring blocks to ShipInstance, Empire, and Fleet.

---

## Tasks

### Task 1.1: Add validate_non_negative to ShipInstance.from_dict [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_validation.py`

- [ ] Add `validate_non_negative` to import at line 21
- [ ] After `require_keys` call (line 644), add validation:
  ```python
  if data.get('current_hp') is not None:
      validate_non_negative(data['current_hp'], 'current_hp', 'ShipInstance')
  if data.get('experience') is not None:
      validate_non_negative(data['experience'], 'experience', 'ShipInstance')
  if data.get('kills') is not None:
      validate_non_negative(data['kills'], 'kills', 'ShipInstance')
  if data.get('battles_survived') is not None:
      validate_non_negative(data['battles_survived'], 'battles_survived', 'ShipInstance')
  ```
- [ ] Verify existing tests still pass

**Notes:**

### Task 1.2: Add tests for ShipInstance non-negative validation [Simple]
**File:** `tests/unit/strategy/ship_instance/test_validation.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_validation.py`

- [ ] Add parametrized test: negative `current_hp`, `experience`, `kills`, `battles_survived` each raises PersistenceException
- [ ] Add test: zero values for those fields are accepted
- [ ] Run tests — all pass

**Notes:**

### Task 1.3: Add Raises docstring to ShipInstance.from_dict [Simple]
**File:** `game/strategy/data/ship_instance.py`

- [ ] Replace one-liner docstring (line 643) with full Args/Returns/Raises docstring

**Notes:**

### Task 1.4: Add Raises docstring to Empire.from_dict [Simple]
**File:** `game/strategy/data/empire.py`

- [ ] Add `Raises: PersistenceException: If required keys missing` to existing docstring (lines 175-184)

**Notes:**

### Task 1.5: Add Raises docstring to Fleet.from_dict [Simple]
**File:** `game/strategy/data/fleet.py`

- [ ] Replace one-liner docstring (line 349) with full Args/Returns/Raises docstring

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/empire/ tests/unit/strategy/fleet/` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
