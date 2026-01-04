# Test Strategist Report
**Role:** Test Strategist
**Date:** 2026-01-04
**Focus:** Test Isolation, Fixture Safety, and Hazard Verification

## 1. High-Level Verdict
**Status:** 🔴 **CRITICAL HAZARD**

The analyzed codebase (`component.py` and `ship.py`) exhibits **zero isolation** for core game data. The heavy reliance on module-level global variables (`REGISTRY` dicts) and singletons ensures that unit tests cannot run deterministically in parallel or in random orders. Any test that modifies a component definition or loads a different vehicle set will pollute the state for all subsequent tests, leading to "Heisenbugs" and false negatives.

## 2. Global State & Registry Pollution
The primary vector for test instability is the usage of module-level dictionaries as the single source of truth.

### A. Component & Modifier Registries (`component.py`)
- **Code:**
  ```python
  MODIFIER_REGISTRY = {}
  # ...
  COMPONENT_REGISTRY = {}
  ```
- **Hazard:** These dictionaries are mutated by `load_components` and `load_modifiers`. There is no mechanism to "reset" them to a pristine state between tests.
- **Impact:** A test that loads a mock modifiers file will leave those modifiers active for the next test. If the next test expects standard modifiers, it will crash or fail silently.

### B. Vehicle Classes (`ship.py`)
- **Code:**
  ```python
  VEHICLE_CLASSES: Dict[str, Any] = {}
  ```
- **Hazard:** `Ship` instances access this global directly in `__init__`:
  ```python
  class_def = VEHICLE_CLASSES.get(self.ship_class, ...)
  ```
- **Impact:** Tests cannot easily mock a `ShipClass` without modifying the global `VEHICLE_CLASSES`. If a test adds a "TestCruiser" class and fails to clean it up, that class persists.

### C. The Validator Singleton (`ship.py`)
- **Code:**
  ```python
  _VALIDATOR = ShipDesignValidator()
  # ...
  def add_component(self, ...):
      result = _VALIDATOR.validate_addition(self, component, layer_type)
  ```
- **Hazard:** The `Ship` class hardcodes a dependency on `_VALIDATOR`. If `ShipDesignValidator` maintains any internal state (caches, counters), that state leaks across tests. It also makes it impossible to assert on validation logic failure by mocking the validator, as the reference is hard-bound.

## 3. Dependency Injection & Mocking Frontiers
The code resists isolation testing due to rigid internal dependencies (Local Import Traps).

- **Circular Import Workarounds:**
  The code frequently uses local imports to avoid circular dependencies:
  ```python
  def _instantiate_abilities(self):
      from game.simulation.systems.resource_manager import ABILITY_REGISTRY, create_ability
  ```
  **analysis:** This pattern makes it extremely difficult to mock `create_ability` or `ABILITY_REGISTRY` via `unittest.mock.patch`, because the import defines the name ref at runtime inside the function scope. Tests trying to mock this at the module level often fail to catch the local import reference.

- **Hardcoded Subsystems:**
  `Ship` explicitly instantiates `ResourceRegistry` and `ShipStatsCalculator` if they aren't found. This coupling prevents testing a `Ship` with a "MockResourceRegistry" to verify simple logic without spinning up the entire resource system.

## 4. Fixture Safety Recommendations

To achieve the goal of "Context Injection" and test stabilization, the following refactoring steps are mandatory:

1.  **Registry Encapsulation:**
    Refactor `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, and `VEHICLE_CLASSES` into a `RegistryManager` class.
    *   *Goal:* The `RegistryManager` can be instantiated per-test or reset via a `tearDown` method.

2.  **Context Injection for Entities:**
    Update `Ship` and `Component` to accept a `context` or `registry_provider` object in their `__init__`, rather than reaching out to globals.
    *   *Interim Step:* Use a `RegistryProxy` singleton that can be hot-swapped in tests, maintaining the existing API surface while allowing backend redirection.

3.  **Validator Injection:**
    Allow `Ship` to accept a `validator` instance, defaulting to the standard one if none provided.
    ```python
    def __init__(self, ..., validator=None):
        self.validator = validator or _DEFAULT_VALIDATOR
    ```

4.  **Pytest Fixtures:**
    Create a `reset_registries` fixture in `conftest.py` that strictly clears all registries before *and* after every test function.

## 5. Hazard Verification Plan (Phase 1)
To confirm these hazards, we should run the **Hazard Verification Test** (`tests/verification/test_hazard_registry_pollution.py` - *to be created during execution*).

**Expected Failure Mode:**
1.  Test A: Loads specific "Hazard" data into `VEHICLE_CLASSES`.
2.  Test B: Expects default data.
3.  **Result:** Test B fails because Test A's data persisted.

This confirms the need for the `RegistryManager` refactor.
