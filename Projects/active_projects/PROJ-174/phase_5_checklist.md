# Phase 5: Update Test Mocks & Deprecate Old API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update test files that mock/patch registry globals to use DI patterns instead. Add deprecation warnings to old API functions. Clean up module-level globals (MOD-CORE-005).

---

## Tasks

### Task 5.1: Update test_ship_loader.py mocks (10 patches) [Medium]
**File:** `tests/unit/simulation/entities/test_ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_loader.py -v`

- [ ] Replace all 10 `patch('game.simulation.entities.ship_loader.RegistryManager')` calls:
  - Line 248, 265, 279, 301, 318, 368, 379, 403, 599, 707
- [ ] For each: replace class-level RegistryManager mock with DI injection pattern:
  ```python
  # BEFORE:
  with patch('game.simulation.entities.ship_loader.RegistryManager') as MockRM:
      MockRM.instance.return_value.components = {...}
      MockRM.instance.return_value.vehicle_classes = {...}
      result = load_vehicle_classes(...)

  # AFTER: Use TestRegistryProvider or fixture injection
  provider = TestRegistryProvider(components={...}, vehicle_classes={...})
  result = load_vehicle_classes(..., registry_provider=provider)
  ```
- [ ] Verify: All ship_loader tests pass

**Notes:** This is the highest-effort task. Read each test carefully — some may need the mock for validator behavior specifically.

### Task 5.2: Update test_builder_data_loader.py mock [Simple]
**File:** `tests/unit/builder/test_builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [ ] Replace `patch.object(RegistryManager.instance(), 'clear')` (line 132) with appropriate DI pattern
- [ ] Verify: Tests pass

**Notes:**

### Task 5.3: Update test_builder_warning_logic.py mocks (2 patches) [Simple]
**File:** `tests/unit/builder/test_builder_warning_logic.py`
**Tests:** `pytest tests/unit/builder/test_builder_warning_logic.py -v`

- [ ] Replace `patch.object(RegistryManager.instance(), 'vehicle_classes', {...})` (lines 124, 145) with fixture/DI:
  ```python
  # BEFORE:
  with patch.object(RegistryManager.instance(), 'vehicle_classes', {'Station': {...}}):

  # AFTER: Populate RegistryManager.instance().vehicle_classes directly in test setup
  # OR inject via TestRegistryProvider if the code under test now accepts it
  ```
- [ ] Verify: Tests pass

**Notes:**

### Task 5.4: Update test_workshop_data_loader.py mock [Simple]
**File:** `tests/unit/workshop/test_workshop_data_loader.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_data_loader.py -v`

- [ ] Replace `patch.object(RegistryManager.instance(), 'clear')` (line 138) with appropriate DI pattern
- [ ] Verify: Tests pass

**Notes:**

### Task 5.5: Update test_compute_planet_production.py mock [Simple]
**File:** `tests/unit/ui/panels/test_compute_planet_production.py`
**Tests:** `pytest tests/unit/ui/panels/test_compute_planet_production.py -v`

- [ ] Replace `patch('game.core.registry.get_default_registries', ...)` (line 88):
  ```python
  # BEFORE:
  with patch('game.core.registry.get_default_registries', return_value=mock_registries):

  # AFTER: Since Phase 3 migrated the code to use provider, patch the provider instead:
  # OR pass registries directly via parameter if function signature was updated
  ```
- [ ] Verify: Tests pass

**Notes:** The approach depends on what Phase 3 did to planet_report_panel.py. If it now uses get_default_registry_provider(), patch that. If the function now accepts a registry param, pass directly.

### Task 5.6: Update test_planet_production_display.py mock [Simple]
**File:** `tests/unit/ui/screens/test_planet_production_display.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_production_display.py -v`

- [ ] Replace `patch('game.core.registry.get_default_registries', ...)` (line 97) — same approach as Task 5.5
- [ ] Verify: Tests pass

**Notes:**

### Task 5.7: Update test_strategy_detail_formatter.py mocks (2 patches) [Simple]
**File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py -v`

- [ ] Replace `patch('game.core.registry.get_default_registries')` (lines 282, 314) — same approach as Task 5.5
- [ ] Verify: Tests pass

**Notes:**

### Task 5.8: Add deprecation warnings to old API [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/registry/ -v`

- [ ] Add deprecation warning to `get_default_registries()` (line 98):
  ```python
  def get_default_registries() -> GameRegistries:
      """DEPRECATED: Use get_default_registry_provider() instead."""
      import warnings
      warnings.warn(
          "get_default_registries() is deprecated. Use get_default_registry_provider() instead.",
          DeprecationWarning,
          stacklevel=2
      )
      if _default_registries is None:
          raise StateException(...)
      return _default_registries
  ```
- [ ] Add deprecation warning to `set_default_registries()` (line 84):
  ```python
  def set_default_registries(registries: GameRegistries) -> None:
      """DEPRECATED: Kept for conftest.py compatibility during transition."""
      import warnings
      warnings.warn(
          "set_default_registries() is deprecated.",
          DeprecationWarning,
          stacklevel=2
      )
      global _default_registries
      _default_registries = registries
  ```
- [ ] Update test_registry_features.py to suppress DeprecationWarning in tests that directly test these functions
- [ ] Verify: No unexpected deprecation warnings in test output

**Notes:** conftest.py still calls set_default_registries(). This is expected — conftest migration is out of scope (it's the composition root). The warning helps identify any NEW callers.

### Task 5.9: Update test_deprecated_code_removed.py [Simple]
**File:** `tests/refactor/test_deprecated_code_removed.py`
**Tests:** `pytest tests/refactor/test_deprecated_code_removed.py -v`

- [ ] Check if this test asserts `get_default_registries` should exist — update assertion to note it's deprecated
- [ ] Check if this test asserts `RegistryManager` should be in __all__ — update to reflect Phase 2 removal
- [ ] Verify: Tests pass

**Notes:**

### Task 5.10: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: 12,023+ passed, 0 failed
- [ ] Verify no regressions
- [ ] Verify: `grep -r "get_default_registries()" game/` returns only registry.py
- [ ] Verify: Only composition roots reference RegistryManager.instance()

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete - Awaiting Audit"
