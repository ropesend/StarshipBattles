# Phase 1: Fix ModifierService Anti-Pattern

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-18 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace direct `RegistryManager.instance().modifiers` calls with `get_modifier_registry()` utility function

---

## Tasks

### Task 1.1: Update ModifierService imports [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py -v`

- [ ] Remove import: `from game.core.registry import RegistryManager` (line 5)
- [ ] Add import: `from game.core.registry import get_modifier_registry` (line 5)
- [ ] Verify: File compiles without import errors

**Notes:**

---

### Task 1.2: Replace anti-pattern in is_modifier_allowed() [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py::TestIsModifierAllowed -v`

- [ ] Line 17: Replace `RegistryManager.instance().modifiers` with `get_modifier_registry()`
  ```python
  # BEFORE:
  if mod_id not in RegistryManager.instance().modifiers:
  # AFTER:
  if mod_id not in get_modifier_registry():
  ```
- [ ] Line 20: Replace `RegistryManager.instance().modifiers[mod_id]` with `get_modifier_registry()[mod_id]`
  ```python
  # BEFORE:
  mod_def = RegistryManager.instance().modifiers[mod_id]
  # AFTER:
  mod_def = get_modifier_registry()[mod_id]
  ```
- [ ] Verify: Run TestIsModifierAllowed tests - all pass

**Notes:**

---

### Task 1.3: Replace anti-pattern in get_initial_value() [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py::TestGetInitialValue -v`

- [ ] Line 108: Replace `RegistryManager.instance().modifiers.get(mod_id)` with `get_modifier_registry().get(mod_id)`
  ```python
  # BEFORE:
  mod_def = RegistryManager.instance().modifiers.get(mod_id)
  # AFTER:
  mod_def = get_modifier_registry().get(mod_id)
  ```
- [ ] Verify: Run TestGetInitialValue tests - all pass

**Notes:**

---

### Task 1.4: Replace anti-pattern in get_local_min_max() [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py::TestGetLocalMinMax -v`

- [ ] Line 155: Replace `RegistryManager.instance().modifiers.get(mod_id)` with `get_modifier_registry().get(mod_id)`
  ```python
  # BEFORE:
  mod_def = RegistryManager.instance().modifiers.get(mod_id)
  # AFTER:
  mod_def = get_modifier_registry().get(mod_id)
  ```
- [ ] Verify: Run TestGetLocalMinMax tests - all pass

**Notes:**

---

### Task 1.5: Run Full ModifierService Test Suite [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/services/test_modifier_service.py -v`

- [ ] Run all ModifierService tests
- [ ] All 30+ tests pass
- [ ] No new warnings introduced

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests: `pytest tests/unit/services/test_modifier_service.py` - all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
