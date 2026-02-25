# Phase 3: Migrate TIER 2 Production Code to TIER 1

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace all `get_default_registries()` calls in `game/` with `get_default_registry_provider()` or constructor DI. After this phase, zero production code uses the service locator pattern.

---

## Tasks

### Task 3.1: Migrate fleet_capability_calculator.py [Simple]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Replace `_get_default_component_registry()` function (lines 14-17)
- [x] Update import at top of file if `get_default_registries` was imported there
- [x] Verify: Tests pass

**Notes:** Function now uses `get_default_registry_provider().get_components()`

### Task 3.2: Migrate turn_engine.py [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -v`

- [x] Replace import (line 54): change `get_default_registries` to `get_default_registry_provider`
- [x] Replace fallback (lines 152-155): change to construct GameRegistries from provider
- [x] Verify: Tests pass

**Notes:** TurnEngine builds GameRegistries from provider when not provided via DI.

### Task 3.3: Migrate ship_instance.py [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Replace `get_default_registries()` call in `get_calculated_stats()`
- [x] Update imports accordingly
- [x] Verify: Tests pass

**Notes:** Builds GameRegistries from provider in lazy init pattern.

### Task 3.4: Migrate ship_stats.py [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [x] Replace docstring example to use new pattern
- [x] Verify: Tests pass

**Notes:** No actual code call - only docstring example was updated.

### Task 3.5: Migrate empire_economy_calculator.py [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Check if `get_default_registries()` is actually called here - only in docstring
- [x] Update docstring example
- [x] Verify: Tests pass

**Notes:** Already uses DI parameter. Updated docstring example only.

### Task 3.6: Migrate ship_factory.py [Simple]
**File:** `game/ui/services/ship_factory.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Replace `_get_registries()` fallback
- [x] Update imports
- [x] Verify: Tests pass

**Notes:** Builds GameRegistries from provider when neither explicit nor stored registries provided.

### Task 3.7: Migrate design_loader_adapter.py [Simple]
**File:** `game/ui/services/design_loader_adapter.py`
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Replace `get_default_registries()` fallback in `__init__`
- [x] Update imports to use `get_default_registry_provider, GameRegistries`
- [x] Verify: Tests pass

**Notes:** Builds GameRegistries from provider when registry_provider not provided.

### Task 3.8: Migrate planet_report_panel.py [Medium]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/ -v`

- [x] Replace `get_default_registries()` call in `compute_planet_production()`
- [x] Update imports
- [x] Verify: Tests pass

**Notes:** Builds GameRegistries from provider for registry access.

### Task 3.9: Migrate empire_panel_window.py [Simple]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -v`

- [x] Replace `get_default_registries()` call in `_build_treasury_tab()`
- [x] Update imports
- [x] Verify: Tests pass

**Notes:** Builds GameRegistries from provider for EmpireEconomyCalculator.

### Task 3.10: Migrate workshop_context.py [Medium]
**File:** `game/ui/screens/workshop_context.py`
**Tests:** `pytest tests/unit/builder/test_workshop_context_di.py -v`

- [x] Replace `__post_init__` to use provider pattern
- [x] Verify: Tests pass

**Notes:** Defensive try/except pattern preserved. Builds GameRegistries from provider.

### Task 3.11: Grep verification [Simple]
**Tests:** N/A

- [x] Run: `grep -r "get_default_registries()" game/ --include="*.py"` — only matches `game/core/registry.py` (definition + docstring)
- [x] Verify: Zero production callers outside registry.py

**Notes:** All production code now uses get_default_registry_provider()

### Task 3.12: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: 11972 passed, 1 skipped
- [x] Verify no regressions

**Notes:** All tests passing

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
