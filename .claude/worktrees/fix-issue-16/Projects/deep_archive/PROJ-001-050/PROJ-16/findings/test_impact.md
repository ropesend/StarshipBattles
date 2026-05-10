# Test Impact Analysis - PROJ-16

**Agent Role:** Test Impact Analyst
**Date:** 2026-01-25

## Test File Counts by Re-export

| Re-export Location | Test Files Affected |
|-------------------|---------------------|
| component.py re-exports | ~141 test files |
| ship.py re-exports | ~100 test files |
| controller.py re-exports | ~40 test files |
| planet.py re-exports | ~2 test files |

## Critical Test Fixtures (Update First)

### Session-Scoped Fixtures (Highest Impact)

**tests/conftest.py:**
- Line 12: `from game.simulation.entities.ship import initialize_ship_data`
- Line 85-87: `global_ship_data` fixture - affects ALL tests
- Line 91-101: `global_ship_data_with_modifiers` fixture

**tests/fixtures/common.py:**
- Line 17-18: imports initialize_ship_data

**tests/fixtures/components.py:**
- Line 26: imports create_component, Component, LayerType
- 7 factory functions used by 141+ tests

**tests/fixtures/ships.py:**
- Line 27-28: imports Ship
- 8 fixture functions used by 100+ tests

**simulation_tests/conftest.py:**
- Lines 83-84: imports load_vehicle_classes, load_components, load_modifiers

## Mock Patches That Will Break

**CRITICAL - Must update before removing re-exports:**

`tests/repro_issues/test_bug_13_clear_removes_hull.py` (Lines 34-35):
```python
patch('game.simulation.entities.ship.get_vehicle_classes', ...)
patch('game.simulation.components.component.get_component_registry', ...)
```

These patches reference re-export paths. When re-exports are removed, these patches must be updated to canonical paths.

## Test Runner Configuration

**pytest.ini:**
- Parallel execution: `-n 4` (4 workers)
- Uses xdist for test isolation
- `reset_singletons()` fixture runs after EVERY test (autouse)

## Recommended Test Update Order

1. **Update test fixtures first** (cascading impact):
   - tests/fixtures/components.py
   - tests/fixtures/ships.py
   - tests/conftest.py
   - simulation_tests/conftest.py

2. **Update mock patches** (will break otherwise)

3. **Update individual test files** (lower impact)

4. **Run incrementally:**
   - `pytest tests/unit/fixtures/` first
   - Then `pytest tests/unit/entities/`
   - Then integration tests
