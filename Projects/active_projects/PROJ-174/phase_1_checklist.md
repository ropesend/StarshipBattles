# Phase 1: Complete IRegistryProvider Protocol

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `get_resources()` to IRegistryProvider, DefaultRegistryProvider, and TestRegistryProvider. Fixes MOD-CORE-006 and MOD-CORE-007.

---

## Tasks

### Task 1.1: Add get_resources() to IRegistryProvider Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py -v`

- [ ] Add `get_resources()` method after `get_vehicle_classes()` (after line 73):
  ```python
  def get_resources(self) -> Dict[str, Any]:
      """Get the resources registry dictionary."""
      ...
  ```
- [ ] Verify: IRegistryProvider protocol now has 4 methods

**Notes:**

### Task 1.2: Add get_resources() to DefaultRegistryProvider [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry_provider.py -v`

- [ ] Add `get_resources()` method after `get_vehicle_classes()` in DefaultRegistryProvider (after line 329):
  ```python
  def get_resources(self) -> Dict[str, Any]:
      """Get the resources registry dictionary from singleton."""
      return RegistryManager.instance().resources
  ```
- [ ] Verify: DefaultRegistryProvider now has 4 get methods

**Notes:**

### Task 1.3: Add resources to TestRegistryProvider [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/test_registry_provider.py -v`

- [ ] Add `resources` parameter to `__init__` signature (line 348-354):
  ```python
  def __init__(
      self,
      components: Optional[Dict[str, Any]] = None,
      modifiers: Optional[Dict[str, Any]] = None,
      vehicle_classes: Optional[Dict[str, Any]] = None,
      resources: Optional[Dict[str, Any]] = None,  # ADD
  ):
  ```
- [ ] Add `self._resources = resources if resources is not None else {}` in __init__ body
- [ ] Add `get_resources()` method after `get_vehicle_classes()`:
  ```python
  def get_resources(self) -> Dict[str, Any]:
      """Get the isolated resources registry dictionary."""
      return self._resources
  ```
- [ ] Verify: TestRegistryProvider now has 4 get methods and accepts resources param

**Notes:**

### Task 1.4: Add tests for get_resources() [Simple]
**File:** `tests/unit/core/test_registry_provider.py`
**Tests:** `pytest tests/unit/core/test_registry_provider.py -v`

- [ ] Add test: `test_default_provider_get_resources_returns_registry_data` — verify DefaultRegistryProvider.get_resources() returns RegistryManager.instance().resources
- [ ] Add test: `test_test_provider_get_resources_returns_custom_data` — verify TestRegistryProvider(resources={"foo": "bar"}).get_resources() returns {"foo": "bar"}
- [ ] Add test: `test_test_provider_get_resources_defaults_to_empty` — verify TestRegistryProvider().get_resources() returns {}
- [ ] Verify: All new tests pass

**Notes:**

### Task 1.5: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: 12,023+ passed, 0 failed
- [ ] Verify no regressions from protocol addition

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
