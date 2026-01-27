# Phase 1: Fix ModifierService Anti-Pattern

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-18 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace direct `RegistryManager.instance().modifiers` calls with `get_modifier_registry()` utility function

---

## Tasks

### Task 1.1: Update ModifierService imports [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py -v`

- [x] Remove import: `from game.core.registry import RegistryManager` (line 5)
- [x] Add import: `from game.core.registry import get_modifier_registry` (line 5)
- [x] Verify: File compiles without import errors

**Notes:** Replaced RegistryManager import with get_modifier_registry utility function.

---

### Task 1.2: Replace anti-pattern in is_modifier_allowed() [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py::TestIsModifierAllowed -v`

- [x] Line 17: Replace `RegistryManager.instance().modifiers` with `get_modifier_registry()`
  ```python
  # BEFORE:
  if mod_id not in RegistryManager.instance().modifiers:
  # AFTER:
  if mod_id not in get_modifier_registry():
  ```
- [x] Line 20: Replace `RegistryManager.instance().modifiers[mod_id]` with `get_modifier_registry()[mod_id]`
  ```python
  # BEFORE:
  mod_def = RegistryManager.instance().modifiers[mod_id]
  # AFTER:
  mod_def = get_modifier_registry()[mod_id]
  ```
- [x] Verify: Run TestIsModifierAllowed tests - all pass

**Notes:** Both occurrences replaced. All 7 TestIsModifierAllowed tests pass.

---

### Task 1.3: Replace anti-pattern in get_initial_value() [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py::TestGetInitialValue -v`

- [x] Line 108: Replace `RegistryManager.instance().modifiers.get(mod_id)` with `get_modifier_registry().get(mod_id)`
  ```python
  # BEFORE:
  mod_def = RegistryManager.instance().modifiers.get(mod_id)
  # AFTER:
  mod_def = get_modifier_registry().get(mod_id)
  ```
- [x] Verify: Run TestGetInitialValue tests - all pass

**Notes:** Replaced. All 7 TestGetInitialValue tests pass.

---

### Task 1.4: Replace anti-pattern in get_local_min_max() [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service.py::TestGetLocalMinMax -v`

- [x] Line 155: Replace `RegistryManager.instance().modifiers.get(mod_id)` with `get_modifier_registry().get(mod_id)`
  ```python
  # BEFORE:
  mod_def = RegistryManager.instance().modifiers.get(mod_id)
  # AFTER:
  mod_def = get_modifier_registry().get(mod_id)
  ```
- [x] Verify: Run TestGetLocalMinMax tests - all pass

**Notes:** Replaced. All 6 TestGetLocalMinMax tests pass.

---

### Task 1.5: Run Full ModifierService Test Suite [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/services/test_modifier_service.py -v`

- [x] Run all ModifierService tests
- [x] All 30+ tests pass
- [x] No new warnings introduced

**Notes:** All 33 tests pass. No warnings.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests: `pytest tests/unit/services/test_modifier_service.py` - all pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
