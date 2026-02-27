# Phase 5: Update Test Mocks & Deprecate Old API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update test files that mock/patch registry globals to use DI patterns instead. Add deprecation warnings to old API functions. Clean up module-level globals (MOD-CORE-005).

---

## Tasks

### Task 5.1: Update test_ship_loader.py mocks (10 patches) [Medium]
**File:** `tests/unit/simulation/entities/test_ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_loader.py -v`

- [x] ~~Replace all 10 `patch('game.simulation.entities.ship_loader.RegistryManager')` calls~~
  - **ANALYSIS:** Tests already migrated to DI pattern in Phase 4. Remaining RegistryManager patches are VALID for validator lifecycle testing (get_or_create_validator uses RegistryManager.instance() for validator storage).
- [x] Verify: All ship_loader tests pass

**Notes:** NO CHANGES NEEDED - Tests correctly use DI pattern for load_vehicle_classes, and RegistryManager mocks are valid for validator lifecycle testing.

### Task 5.2: Update test_builder_data_loader.py mock [Simple]
**File:** `tests/unit/builder/test_builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [x] ~~Replace `patch.object(RegistryManager.instance(), 'clear')` (line 132)~~
  - **ANALYSIS:** This is validly testing method delegation on DI-injected registry. The loader receives registries via DI and the test verifies clear() is called.
- [x] Verify: Tests pass

**Notes:** NO CHANGES NEEDED - test correctly verifies delegation behavior.

### Task 5.3: Update test_builder_warning_logic.py mocks (2 patches) [Simple]
**File:** `tests/unit/builder/test_builder_warning_logic.py`
**Tests:** `pytest tests/unit/builder/test_builder_warning_logic.py -v`

- [x] Updated fixture to inject mock_registries via DI to WorkshopContext.standalone()
- [x] Replaced RegistryManager patches with direct registry population via DI
- [x] Verify: Tests pass

**Notes:** Modified fixture and tests to use DI injection pattern.

### Task 5.4: Update test_workshop_data_loader.py mock [Simple]
**File:** `tests/unit/workshop/test_workshop_data_loader.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_data_loader.py -v`

- [x] ~~Replace `patch.object(RegistryManager.instance(), 'clear')` (line 138)~~
  - **ANALYSIS:** Same as Task 5.2 - validly tests method delegation.
- [x] Verify: Tests pass

**Notes:** NO CHANGES NEEDED - test correctly verifies delegation behavior.

### Task 5.5: Update test_compute_planet_production.py mock [Simple]
**File:** `tests/unit/ui/panels/test_compute_planet_production.py`
**Tests:** `pytest tests/unit/ui/panels/test_compute_planet_production.py -v`

- [x] Updated test to patch `get_default_registry_provider` instead of `get_default_registries`
- [x] Verify: Tests pass

**Notes:** Phase 3 migrated the function to use provider pattern.

### Task 5.6: Update test_planet_production_display.py mock [Simple]
**File:** `tests/unit/ui/screens/test_planet_production_display.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_production_display.py -v`

- [x] Updated test to patch `get_default_registry_provider` instead of `get_default_registries`
- [x] Verify: Tests pass

**Notes:** Same approach as Task 5.5.

### Task 5.7: Update test_strategy_detail_formatter.py mocks (2 patches) [Simple]
**File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py -v`

- [x] Updated tests to patch `get_default_registry_provider` instead of `get_default_registries`
- [x] Verify: Tests pass

**Notes:** Same approach as Task 5.5.

### Task 5.8: Add deprecation warnings to old API [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/registry/ -v`

- [x] Added deprecation warning to `get_default_registries()`
- [x] Added deprecation warning to `set_default_registries()`
- [x] Updated test_registry_features.py to filter DeprecationWarning
- [x] Updated conftest.py to suppress warning (composition root)
- [x] Updated app.py to suppress warning (composition root)
- [x] Updated additional test files with filterwarnings decorators:
  - test_deprecated_code_removed.py
  - test_workshop_context_di.py
  - test_design_loader_adapter.py
  - test_protocols_boundary.py
  - test_fleet_composition.py
- [x] Verify: No unexpected deprecation warnings in test output

**Notes:** conftest.py and app.py are composition roots - they legitimately call these functions. Warning suppressed there.

### Task 5.9: Update test_deprecated_code_removed.py [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py -v`

- [x] Added @pytest.mark.filterwarnings to TestNewPatternsWork class
- [x] Verify: Tests pass

**Notes:** File location was tests/regression/ not tests/refactor/.

### Task 5.10: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: 11972 passed, 1 skipped
- [x] Verify no regressions
- [x] Verify: `grep -r "get_default_registries()" game/` returns only registry.py
- [x] Verify: Only composition roots reference RegistryManager.instance() (app.py, registry_loader.py, ship_loader.py for validator)

**Notes:** Test count 11972 vs baseline 12023 - delta from earlier PROJ-175 logger cleanup.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete - Awaiting Audit"
