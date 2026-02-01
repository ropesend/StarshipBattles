# Phase 5: Fix Test Breakage

**Objective:** Update all test files to use modern resource patterns.

**Prerequisite:** Phase 1-4 complete (production code working)

---

## Tasks

### 5.1 Fix Unit Test - Combat Endurance
**File:** `tests/unit/combat/test_combat_endurance.py`

- [ ] Replace `abilities={'EnergyGeneration': ...}` with ResourceGeneration format
- [ ] Replace any `EnergyStorage`, `FuelStorage`, `AmmoStorage` patterns
- [ ] Update assertions that check legacy properties
- [ ] Ensure all 4+ test methods pass

### 5.2 Fix Unit Test - Ship Stats Modifiers
**File:** `tests/unit/strategy/ship_stats/test_modifiers.py`

- [ ] Replace all `abilities={'EnergyStorage': 2000}` patterns (~8 occurrences)
- [ ] Use `abilities={'ResourceStorage': [{'resource': 'energy', 'amount': 2000}]}`
- [ ] Update any assertions checking legacy ability names

### 5.3 Fix Unit Test - Ship Stats Basics
**File:** `tests/unit/strategy/ship_stats/test_basics.py`

- [ ] Replace `abilities={'FuelStorage': 10000}` patterns (~3 occurrences)
- [ ] Update fuel storage aggregation tests
- [ ] Update any legacy property assertions

### 5.4 Fix Unit Test - Ship Stats Warp
**File:** `tests/unit/strategy/ship_stats/test_warp.py`

- [ ] Replace all legacy ability patterns (~6 occurrences)
- [ ] Update warp cost tests to use `warp_resource_costs` dict
- [ ] Ensure warp capability tests still pass

### 5.5 Fix Unit Test - Abilities
**File:** `tests/unit/entities/test_abilities.py`

- [ ] Replace `create_ability("FuelStorage", ...)` patterns
- [ ] Update to create ResourceStorage directly
- [ ] Verify ability creation tests pass

### 5.6 Fix Unit Test - Ship Stats Toggles
**File:** `tests/unit/strategy/ship_stats/test_toggles.py`

- [ ] Replace legacy ability patterns
- [ ] Update toggle behavior tests

### 5.7 Fix Integration Tests - Resource System
**Files:** `tests/integration/resource_system/test_*.py`

- [ ] Update any legacy patterns in resource system integration tests
- [ ] These may already use modern patterns - verify

### 5.8 Fix Integration Tests - UI
**Files:** `tests/integration/ui/test_*.py`

- [ ] Update `test_build_queue_design_report.py` mock attributes
- [ ] Update any other UI tests with legacy patterns

### 5.9 Fix Repro Tests
**Files:** `tests/repro_issues/test_bug_*.py`

- [ ] Update `test_bug_03_validation.py` - warning message tests
- [ ] Update `test_bug_05_deep_repro.py` - legacy ability references
- [ ] Update `test_bug_08_fuel_validation.py` - FuelStorage validation
- [ ] Update `test_bug_09_endurance.py` - endurance calculations
- [ ] Update `test_bug_10_logistics_update.py` - logistics tests

### 5.10 Fix Regression Tests
**Files:** `tests/unit/regressions/test_*.py`

- [ ] Update `test_warnings.py` - "Needs Fuel Storage" tests
- [ ] Update `test_bug_regressions_2026_01.py` - any legacy patterns

### 5.11 Fix Builder Tests
**Files:** `tests/unit/builder/test_*.py`

- [ ] Update `test_builder_improvements.py` - mock attributes
- [ ] Update any legacy ability patterns

### 5.12 Fix Test Fixtures/Conftest
**Files:** Various `conftest.py` files

- [ ] Update `tests/unit/conftest.py` if needed
- [ ] Update `tests/unit/strategy/ship_stats/conftest.py`
- [ ] Update `tests/integration/resource_system/conftest.py`
- [ ] Update any MockComponent or fixture creation code

### 5.13 Fix Simulation Tests
**Files:** `simulation_tests/tests/test_*.py`

- [ ] Verify RESOURCE-* scenarios still pass (should already use modern format)
- [ ] Update any legacy patterns found
- [ ] Run full simulation test suite

### 5.14 Run Full Test Suite
- [ ] Run `pytest tests/` - ALL tests should pass
- [ ] Run `pytest simulation_tests/` - ALL tests should pass
- [ ] Document any remaining failures

---

## Common Test Fix Patterns

### Ability Dictionary
```python
# BEFORE
abilities = {'EnergyStorage': 2000}

# AFTER
abilities = {'ResourceStorage': [{'resource': 'energy', 'amount': 2000}]}
```

### Multiple Abilities
```python
# BEFORE
abilities = {
    'FuelStorage': 5000,
    'EnergyGeneration': 100
}

# AFTER
abilities = {
    'ResourceStorage': [{'resource': 'fuel', 'amount': 5000}],
    'ResourceGeneration': [{'resource': 'energy', 'amount': 100}]
}
```

### Property Assertions
```python
# BEFORE
assert ship.max_fuel == 5000

# AFTER
assert ship.resources.get_max_value('fuel') == 5000
```

### Mock Attributes
```python
# BEFORE
mock_ship.energy_generation = 50

# AFTER
# Setup proper resource registry mock or use real resources
mock_ship.resources.register_generation('energy', 50)
```

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
- `tests/integration/resource_system/test_*.py`
- Various `conftest.py` files
- Plus others as discovered

---

## Verification

After this phase:
```bash
# Full test suite should pass
pytest tests/ -v --tb=short

# Simulation tests should pass
pytest simulation_tests/ -v

# No legacy patterns in test files
grep -rn "EnergyStorage" tests/ --include="*.py" | grep -v "ResourceStorage"
grep -rn "FuelStorage" tests/ --include="*.py" | grep -v "ResourceStorage"
```

---

## Notes

- Some tests may be testing the legacy behavior specifically - these need rewriting
- Keep test names if behavior is same, just update implementation
- Add comments noting migration from legacy pattern where helpful
- Consider creating test helpers for common resource setup patterns
