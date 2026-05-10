# Phase 1: Fix Bugs & Add Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-91 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix existing bugs in resupply/get_resource_percentage, add get_resource_names() to ResourceRegistry, add IResourceHolder protocol, and un-hardcode resource name lists in bridge methods.

---

## Tasks

### Task 1.1: Add `get_resource_names()` to ResourceRegistry [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/unit/simulation/ -k resource`

- [x] Add method to ResourceRegistry (after `set_regen_rate`, around line 195):
  ```python
  def get_resource_names(self) -> List[str]:
      """Return list of all registered resource names."""
      return list(self._resources.keys())
  ```
- [x] Add `List` to the typing import at line 60 (already imported, verify)
- [x] Write unit test for `get_resource_names()` in appropriate test file
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** Added 2 tests in tests/unit/entities/test_resources.py: test_get_resource_names_empty, test_get_resource_names_returns_all_registered

### Task 1.2: Add IResourceHolder Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/ -k protocol`

- [x] Add `IResourceHolder` protocol after the existing combat protocols section (after `IDamageable`, around line 286):
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
- [x] Add `is_resource_holder()` TypeGuard function in the TypeGuard section:
  ```python
  def is_resource_holder(obj: Any) -> TypeGuard[IResourceHolder]:
      """Check if obj implements IResourceHolder protocol."""
      return isinstance(obj, IResourceHolder)
  ```
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** Added at end of protocols.py after IResourceReader section.

### Task 1.3: Fix `resupply()` Bug [Simple]
**File:** `game/strategy/data/ship_resource_manager.py` (delegated from ship_instance.py)
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/test_resupply_system.py`

- [x] Fix `resupply()` (lines 240-241) — change from:
  ```python
  max_key = f'max_{resource_name}'
  max_val = self._ship.get_calculated_stats().get(max_key, 100)
  ```
  to:
  ```python
  max_val = self.get_resource_capacity(resource_name)
  ```
  This reuses the existing `get_resource_capacity()` method which correctly accesses `resource_storage` dict.
- [x] Add test case for resupply with non-100 capacity to verify fix
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** Bug was in ShipResourceManager, not ShipInstance directly. Added 2 tests: test_resupply_uses_resource_storage_not_max_key, test_resupply_partial

### Task 1.4: Fix `get_resource_percentage()` Bug [Simple]
**File:** `game/strategy/data/ship_display_formatter.py` (delegated from ship_instance.py)
**Tests:** `pytest tests/unit/strategy/ship_instance/`

- [x] N/A - Already fixed. ShipDisplayFormatter.get_resource_percentage() correctly uses:
  ```python
  resource_storage = stats.get('resource_storage', {})
  max_val = resource_storage.get(resource_name, 0)
  ```
  The bug was fixed during PROJ-87 extraction.
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** No fix needed - PROJ-87 extraction already uses correct resource_storage lookup.

### Task 1.5: Un-hardcode Resource Names in Bridge Methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/`

- [x] Update `from_ship()` (lines 162-168) — change from:
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
- [x] Update `update_from_ship()` (lines 782-788) — change from:
  ```python
  if hasattr(ship, 'resources') and ship.resources:
      for name in ['fuel', 'energy', 'ammo']:
  ```
  to:
  ```python
  if ship.resources:
      for name in ship.resources.get_resource_names():
  ```
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** Removed both hardcoded lists and hasattr checks.

### Task 1.6: Un-hardcode Resource Names in BattleState [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/`

- [x] Find the ShipState capture method that hardcodes `['fuel', 'energy', 'ammo']`
- [x] Update to use `ship.resources.get_resource_names()` instead
- [x] Verify: `pytest tests/ --testmon` passes

**Notes:** Updated ShipState.from_ship() (line 194-197) to use get_resource_names().

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12` — 7561 tests pass (+4 new)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
