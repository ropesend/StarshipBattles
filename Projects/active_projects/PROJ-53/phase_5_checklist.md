# Phase 5: Fix Test Breakage

**Objective:** Update all test files to use modern resource patterns.

**Prerequisite:** Phase 1-4 complete (production code working)

**Status:** Complete

---

## Tasks

### 5.1 Fix Unit Test - Combat Endurance
**File:** `tests/unit/combat/test_combat_endurance.py`

- [x] Replace `abilities={'EnergyGeneration': ...}` with ResourceGeneration format
- [x] Replace any `EnergyStorage`, `FuelStorage`, `AmmoStorage` patterns
- [x] Update assertions that check legacy properties
- [x] All test methods pass

### 5.2 Fix Unit Test - Ship Stats Modifiers
**File:** `tests/unit/strategy/ship_stats/test_modifiers.py`

- [x] Replace all `abilities={'EnergyStorage': 2000}` patterns
- [x] Use `abilities={'ResourceStorage': [{'resource': 'energy', 'amount': 2000}]}`
- [x] Update any assertions checking legacy ability names

### 5.3 Fix Unit Test - Ship Stats Basics
**File:** `tests/unit/strategy/ship_stats/test_basics.py`

- [x] Replace `abilities={'FuelStorage': 10000}` patterns
- [x] Update fuel storage aggregation tests
- [x] Update any legacy property assertions

### 5.4 Fix Unit Test - Ship Stats Warp
**File:** `tests/unit/strategy/ship_stats/test_warp.py`

- [x] Replace all legacy ability patterns
- [x] Update warp cost tests to use `warp_resource_costs` dict
- [x] Ensure warp capability tests still pass

### 5.5 Fix Unit Test - Abilities
**File:** `tests/unit/entities/test_abilities.py`

- [x] Replace `create_ability("FuelStorage", ...)` patterns
- [x] Update to create ResourceStorage directly
- [x] Verify ability creation tests pass

### 5.6 Fix Unit Test - Ship Stats Toggles
**File:** `tests/unit/strategy/ship_stats/test_toggles.py`

- [x] Replace legacy ability patterns
- [x] Update toggle behavior tests

### 5.7 Fix Integration Tests - Resource System
**Files:** `tests/integration/resource_system/test_*.py`

- [x] Update any legacy patterns in resource system integration tests
- [x] Already uses modern patterns

### 5.8 Fix Integration Tests - UI
**Files:** `tests/integration/ui/test_*.py`

- [x] Update `test_build_queue_design_report.py` mock attributes
- [x] Update any other UI tests with legacy patterns

### 5.9 Fix Repro Tests
**Files:** `tests/repro_issues/test_bug_*.py`

- [x] Update `test_bug_03_validation.py` - warning message tests
- [x] Update `test_bug_05_deep_repro.py` - legacy ability references
- [x] Update `test_bug_08_fuel_validation.py` - FuelStorage validation
- [x] Update `test_bug_09_endurance.py` - endurance calculations
- [x] Update `test_bug_10_logistics_update.py` - logistics tests

### 5.10 Fix Regression Tests
**Files:** `tests/unit/regressions/test_*.py`

- [x] Update `test_warnings.py` - "Needs Fuel Storage" tests
- [x] Update `test_bug_regressions_2026_01.py` - any legacy patterns

### 5.11 Fix Builder Tests
**Files:** `tests/unit/builder/test_*.py`

- [x] Update `test_builder_improvements.py` - mock attributes
- [x] Update any legacy ability patterns

### 5.12 Fix Test Fixtures/Conftest
**Files:** Various `conftest.py` files

- [x] Update `tests/unit/conftest.py` if needed
- [x] Update `tests/unit/strategy/ship_stats/conftest.py`
- [x] Update `tests/integration/resource_system/conftest.py`
- [x] Update any MockComponent or fixture creation code

### 5.13 Fix Simulation Tests
**Files:** `simulation_tests/tests/test_*.py`

- [x] Verify RESOURCE-* scenarios still pass (already use modern format)
- [x] Run full simulation test suite

### 5.14 Run Full Test Suite
- [x] Run `pytest tests/` - ALL tests pass (5911)
- [x] Run `pytest simulation_tests/` - ALL tests pass
- [x] No remaining failures

---

## Files Modified (25+ files)
- `tests/unit/combat/test_combat_endurance.py`
- `tests/unit/strategy/ship_stats/test_modifiers.py`
- `tests/unit/strategy/ship_stats/test_basics.py`
- `tests/unit/strategy/ship_stats/test_warp.py`
- `tests/unit/strategy/ship_stats/test_toggles.py`
- `tests/unit/entities/test_abilities.py`
- `tests/unit/builder/test_builder_improvements.py`
- `tests/unit/regressions/test_warnings.py`
- `tests/unit/regressions/test_bug_regressions_2026_01.py`
- `tests/repro_issues/test_bug_03_validation.py`
- `tests/repro_issues/test_bug_05_deep_repro.py`
- `tests/repro_issues/test_bug_08_fuel_validation.py`
- `tests/repro_issues/test_bug_09_endurance.py`
- `tests/repro_issues/test_bug_10_logistics_update.py`
- `tests/integration/ui/test_build_queue_design_report.py`
- Various `conftest.py` files

---

## Notes

- All tests now use modern ResourceStorage/ResourceConsumption/ResourceGeneration patterns
- No legacy ability names remain in test files
