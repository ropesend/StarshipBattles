# Audit Report: Ship and Physics Unit Tests

## Executive Summary
This audit covers unit tests related to ship core functionality, physics, and resource management. The majority of tests have been updated to use the new `create_component` factory and ability-based logic. However, `test_ship_stats.py` contains significant legacy patterns, including direct instantiation of legacy component subclasses (`Engine`, `Thruster`, `Shield`) and assertions on legacy attributes which are scheduled for removal.

## Findings by File

### 1. `unit_tests/test_ship_stats.py` (High Priority)
This file was explicitly designed as a "baseline" pre-refactor and contains the most legacy debt.

*   **Legacy Class Instantiation**
    *   **Location**: Lines 36-44 (Imports), Lines 114, 137, 176, 205, 234.
    *   **Pattern**: Imports and uses `Engine`, `Thruster`, `Shield`, `ShieldRegenerator` classes directly.
    *   **Issue**: These classes are deprecated. Logic should rely on `Component` with `Ability` instances.
    *   **Blocks Removal**: **YES**
    *   **Fix**: Update tests to use `create_component` with data definitions that include abilities, or manually construct `Component` and add `Ability` instances if specific isolation is needed.

*   **Legacy Attribute in Data Definitions**
    *   **Location**: Lines 109, 135, 158, 203.
    *   **Pattern**: Defining `thrust_force`, `turn_speed`, `shield_projection` as root keys in component data dicts.
    *   **Issue**: These are now ability properties. The loader shims them currently, but tests should define them in `abilities` dict.
    *   **Blocks Removal**: **NO** (Shim handles it), but **YES** for final cleanup.
    *   **Fix**: Move these values into the `abilities` dictionary in the test data setup.

*   **Direct Legacy Attribute Assertions**
    *   **Location**: Line 208 `self.assertEqual(engine.thrust_force, 2000)`
    *   **Pattern**: Accessing `c.thrust_force` directly.
    *   **Issue**: This validates the *shim*, not the new system.
    *   **Blocks Removal**: **YES**
    *   **Fix**: Remove explicit legacy attribute tests. Verify `engine.get_ability("CombatPropulsion").thrust_force` instead.

### 2. `unit_tests/test_ship_physics_mixin.py`
*   **Status**: **Mostly Clean**
*   **Notes**:
    *   Uses `create_component('standard_engine')` which is good.
    *   Tests `ship.turn_speed` (Line 151). This is acceptable as `Ship` aggregates ability values into this property for the physics engine.
    *   **Fix**: None required, assuming `standard_engine` definition in `components.json` is up to date (which Phase 6 ensured).

### 3. `unit_tests/test_ship.py`
*   **Status**: **Clean**
*   **Notes**:
    *   Uses `create_component`.
    *   Tests generic `LayerType` and `Component` logic.
    *   Legacy `Railgun` class is not instantiated directly; usage `create_component('railgun')` is correct.

### 4. `unit_tests/test_physics.py`
*   **Status**: **Clean**
*   **Notes**:
    *   Tests `PhysicsBody` primitive. No dependency on Component system.

### 5. `unit_tests/test_resources.py` & `unit_tests/test_ship_resources.py`
*   **Status**: **Clean**
*   **Notes**:
    *   `test_resources.py` tests `ResourceConsumption` ability directly.
    *   `test_ship_resources.py` uses `create_component` and verifies status flags.

## Summary of Actions Required

1.  **Refactor `test_ship_stats.py`**:
    *   Remove imports of `Engine`, `Thruster`, `Shield`.
    *   Replace `self.Engine(data)` with `create_component` or generic `Component`.
    *   Update test data dictionaries to put values inside `abilities` key.
    *   Remove assertions checking legacy root attributes (`engine.thrust_force`) and focus on `ship.total_thrust` or `ability.thrust_force`.

2.  **Verify Data Definitions**:
    *   Ensure any inline JSON/Dict data in other tests uses `abilities` structure if they are ever updated, though current usage in `test_ship_stats.py` is the primary offender.
