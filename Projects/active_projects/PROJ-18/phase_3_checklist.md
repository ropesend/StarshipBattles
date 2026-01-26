# Phase 3: Add New Registry Utility Functions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-18 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing utility functions (freeze_registry, set_validator, clear_registry) to registry.py

---

## Tasks

### Task 3.1: Add freeze_registry() utility function [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py -v`

- [ ] Add function after existing utility functions (after line 196):
  ```python
  def freeze_registry() -> None:
      """
      Freeze the registry to prevent further modifications.

      Call this after game initialization to catch accidental mutations
      during gameplay. Thread-safe.

      Note: Use RegistryManager.reset() to unfreeze (destroys instance).
      """
      RegistryManager.instance().freeze()
  ```
- [ ] Verify: Function can be imported and called

**Notes:**

---

### Task 3.2: Add set_validator() utility function [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py -v`

- [ ] Add function after freeze_registry():
  ```python
  def set_validator(validator) -> None:
      """
      Set the ship design validator.

      Args:
          validator: ShipDesignValidator instance

      Raises:
          RuntimeError: If the registry is frozen
      """
      RegistryManager.instance().set_validator(validator)
  ```
- [ ] Verify: Function can be imported and called

**Notes:**

---

### Task 3.3: Add clear_registry() utility function [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry.py -v`

- [ ] Add function after set_validator():
  ```python
  def clear_registry() -> None:
      """
      Clear all registries to empty state.

      Used by test fixtures to ensure clean state between tests.
      Preserves dict identity, only empties contents.

      Raises:
          RuntimeError: If the registry is frozen
      """
      RegistryManager.instance().clear()
  ```
- [ ] Verify: Function can be imported and called

**Notes:**

---

### Task 3.4: Update registry.py documentation [Simple]
**File:** `game/core/registry.py`
**Tests:** N/A

- [ ] Add section to module docstring explaining Tier 1 vs Tier 2 access:
  ```python
  """
  Registry Access Patterns
  ========================

  TIER 1 - Utility Functions (Raw Access):
      from game.core.registry import get_component_registry
      components = get_component_registry()

  TIER 2 - Domain Services (Computed Access):
      from game.strategy.services.ship_stats_service import ShipStatsService
      stats = ShipStatsService.calculate_ship_stats(design)

  AVOID - Direct Singleton Access:
      # DON'T DO THIS - harder to test
      RegistryManager.instance().components
  """
  ```
- [ ] Verify: Documentation is clear and helpful

**Notes:**

---

### Task 3.5: Run Registry Tests [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/core/test_registry.py -v`

- [ ] Run all registry tests
- [ ] All tests pass
- [ ] New functions work correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] freeze_registry() added and working
- [ ] set_validator() added and working
- [ ] clear_registry() added and working
- [ ] Documentation updated
- [ ] Tests: `pytest tests/unit/core/test_registry.py` - all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
