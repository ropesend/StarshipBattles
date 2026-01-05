# Test Strategist Report: Isolation & Hazard Analysis

**Focus:** Test Isolation, State Pollution, and Verification Hazards  
**Target:** `game/simulation/components/component.py` and `game/simulation/entities/ship.py`

## 1. High-Level Verdict: Critical Isolation Failure
The current codebase relies heavily on **Module-Level Mutable Global State** for its core definitions (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`). This makes unit testing inherently **non-deterministic** and **order-dependent**. One test modifying a registry will bleed side effects into all subsequent tests in the suite. Use of specific local imports to bypass circular dependencies further complicates mocking and isolation.

## 2. Critical Isolation Hazards

### A. Global Registry Pollution
The following objects are defined at the module level and mutated by "loader" functions. They act as persistent singletons across the entire test session unless explicitly reset.

*   **`COMPONENT_REGISTRY` & `MODIFIER_REGISTRY`** (`component.py`)
    *   **Hazard:** Defined as global dicts. Populated by `load_components/modifiers`.
    *   **Impact:** A test that loads a custom component for a scenario will leave that component in eggress for the next test. A test that involves "damaging" a registered component (if the registry holds references to live objects) breaks state.
    *   **Path:** `game/simulation/components/component.py` (Lines 41, 257)

*   **`VEHICLE_CLASSES`** (`ship.py`)
    *   **Hazard:** Global dictionary holding ship class definitions.
    *   **Impact:** Modifying ship class stats for a balance test persists for the duration of the process.
    *   **Path:** `game/simulation/entities/ship.py` (Line 29)

### B. Singleton Instance Persistence
*   **`_VALIDATOR`** (`ship.py`)
    *   **Hazard:** Instantiated at module level: `_VALIDATOR = ShipDesignValidator()`.
    *   **Impact:** If `ShipDesignValidator` maintains any internal cache or state (e.g., cached hull validation results), that state leaks across tests. It prevents testing "fresh" validation logic.
    *   **Path:** `game/simulation/entities/ship.py` (Line 18)

### C. Hidden Hard-Coded Dependencies (Mocking Barriers)
The code frequently uses "Lazy Local Imports" to avoid circular dependencies. This pattern hides dependencies from the class interface, making them extremely difficult to mock or inject during testing.

*   **Ability Registry Access:**
    *   `Component.get_abilities` imports `ABILITY_REGISTRY` inside the function body.
    *   `Component._instantiate_abilities` imports `create_ability` inside the loop.
    *   **Impact:** To test a component in isolation, the test harness must mock `game.simulation.components.abilities` *module*, not just pass a mock object. This couples the unit test to the file structure.
    *   **Ref:** `component.py` Line 99, 137

*   **Component Registry Access:**
    *   `Ship.from_dict` directly accesses `COMPONENT_REGISTRY`.
    *   **Impact:** Cannot hydration-test a Ship without fully hydrating the global component registry first.

## 3. Structural Verification Findings

### A. File Path Fragility
*   `load_components` and `load_vehicle_classes` rely on `os.getcwd()` or relative path fallback logic.
*   **Hazard:** Tests traversing directories (e.g. running from root vs running from `tests/`) will cause these loaders to fail or index different files, leading to "Works locally, fails in CI" behavior.

### B. "Live" Reference Leaks
*   `create_component` calls `COMPONENT_REGISTRY[id].clone()`.
*   **Hazard:** If `clone()` is shallow or imperfect, the "template" object in the registry might be mutated by a test, permanently corrupting the registry for subsequent clones. The current `Component.__init__` does a `copy.deepcopy` of data, which is safe, but the architecture relies on this specific implementation detail for safety.

## 4. Recommendations for Refactoring

1.  **Introduce `RegistryManager`:** Moving all global dicts (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`) into a unified `RegistryManager` class.
2.  **Context Injection:**
    *   Update `Ship.__init__` and `Component.__init__` to accept a `registry_context` argument.
    *   If `None`, default to the Global Manager (for backward compat), but allow tests to pass a sterile, isolated Manager.
3.  **Strict Fixture Reset:** In `conftest.py`, implement a fixture that:
    1.  Snapshots the state of all global registries.
    2.  Clears them.
    3.  Runs the test.
    4.  Restores the snapshot.
    *   *Better Approach:* Do not populate globals by default. Only populate a localized RegistryManager for the test scope.
4.  **Expose Dependencies:** Convert local imports to module-level imports where possible (using `typing.TYPE_CHECKING` for static analysis) or inject factories to break circular loops.

## 5. Confidence Score
**5/5** - The hazards are explicit and clearly identifiable in the provided source code.
