# Phase 1: Fix Bugs & Add Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-91 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix existing bugs in resupply/get_resource_percentage, add get_resource_names() to ResourceRegistry, add IResourceHolder protocol, and un-hardcode resource name lists in bridge methods.

---

## Tasks

### Task 1.1: Add `get_resource_names()` to ResourceRegistry [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/unit/simulation/ -k resource`

- [ ] Add method to ResourceRegistry (after `set_regen_rate`, around line 195):
  ```python
  def get_resource_names(self) -> List[str]:
      """Return list of all registered resource names."""
      return list(self._resources.keys())
  ```
- [ ] Add `List` to the typing import at line 60 (already imported, verify)
- [ ] Write unit test for `get_resource_names()` in appropriate test file
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 1.2: Add IResourceHolder Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/ -k protocol`

- [ ] Add `IResourceHolder` protocol after the existing combat protocols section (after `IDamageable`, around line 286):
  ```python
  @runtime_checkable
  class IResourceHolder(Protocol):
      """Protocol for objects that hold resources accessible via ResourceRegistry.

      Used by ShipInstance bridge methods (to_ship, from_ship, update_from_ship)
      to access Ship resource state without hasattr checks.
      """
      @property
      def resources(self) -> Any: ...  # ResourceRegistry (typed as Any to avoid cross-layer import)

      @property
      def hp(self) -> int: ...

      @property
      def max_hp(self) -> int: ...

      @property
      def is_alive(self) -> bool: ...

      @property
      def is_derelict(self) -> bool: ...

      @property
      def layers(self) -> Dict[str, Any]: ...
  ```
- [ ] Add `is_resource_holder()` TypeGuard function in the TypeGuard section:
  ```python
  def is_resource_holder(obj: Any) -> TypeGuard[IResourceHolder]:
      """Check if obj implements IResourceHolder protocol."""
      return isinstance(obj, IResourceHolder)
  ```
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 1.3: Fix `resupply()` Bug [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/test_resupply_system.py`

- [ ] Fix `resupply()` (lines 828-829) — change from:
  ```python
  max_key = f'max_{resource_name}'
  max_val = self.get_calculated_stats().get(max_key, 100)
  ```
  to:
  ```python
  max_val = self.get_resource_capacity(resource_name)
  ```
  This reuses the existing `get_resource_capacity()` method which correctly accesses `resource_storage` dict.
- [ ] Add test case for resupply with non-100 capacity to verify fix
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 1.4: Fix `get_resource_percentage()` Bug [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/`

- [ ] Fix `get_resource_percentage()` (lines 239-240) — change from:
  ```python
  max_key = f'max_{resource_name}'
  max_val = self.get_calculated_stats().get(max_key, 100)
  ```
  to:
  ```python
  max_val = self.get_resource_capacity(resource_name)
  ```
- [ ] Add test case for get_resource_percentage with specific capacity to verify fix
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 1.5: Un-hardcode Resource Names in Bridge Methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/`

- [ ] Update `from_ship()` (lines 162-168) — change from:
  ```python
  if hasattr(ship, 'resources') and ship.resources:
      for name in ['fuel', 'energy', 'ammo']:
          current = ship.resources.get_value(name)
          max_val = ship.resources.get_max_value(name)
          if current < max_val:
              instance.resource_levels[name] = current
  ```
  to:
  ```python
  if ship.resources:
      for name in ship.resources.get_resource_names():
          current = ship.resources.get_value(name)
          max_val = ship.resources.get_max_value(name)
          if current < max_val:
              instance.resource_levels[name] = current
  ```
- [ ] Update `update_from_ship()` (lines 782-788) — change from:
  ```python
  if hasattr(ship, 'resources') and ship.resources:
      for name in ['fuel', 'energy', 'ammo']:
  ```
  to:
  ```python
  if ship.resources:
      for name in ship.resources.get_resource_names():
  ```
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

### Task 1.6: Un-hardcode Resource Names in BattleState [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/`

- [ ] Find the ShipState capture method that hardcodes `['fuel', 'energy', 'ammo']`
- [ ] Update to use `ship.resources.get_resource_names()` instead
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/ -n 12` — all 7353+ tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
