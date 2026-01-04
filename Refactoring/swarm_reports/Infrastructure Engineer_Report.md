# Infrastructure Engineer Report

**Date:** 2026-01-04
**Focus:** Registry Encapsulation, Singleton Management, Backward Compatibility
**Target scope:** `game/simulation/components/component.py` and `game/simulation/entities/ship.py`

## 1. Executive Summary

The codebase currently relies heavily on module-level global dictionaries (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`, `ABILITY_REGISTRY`) acting as implicit singletons. This architectural pattern is the primary source of **state pollution**, **circular import hacks**, and **test isolation failures**.

The lack of strict encapsulation means that tests cannot reliably run in parallel or sequence without rigorous setup/teardown of these global variables. Furthermore, classes like `Ship` and `Component` have hard code dependencies on these globals, preventing dependency injection and modular simulation contexts.

## 2. Detailed Analysis

### 2.1 Registry Encapsulation & Singleton Management

**Issue 1: Global State Arrays (Pollution Vectors)**
The following are defined as global module-level variables:
- `game.simulation.components.component.MODIFIER_REGISTRY`
- `game.simulation.components.component.COMPONENT_REGISTRY`
- `game.simulation.entities.ship.VEHICLE_CLASSES`

**Evidence:**
- `game/simulation/components/component.py`:
  ```python
  MODIFIER_REGISTRY = {}
  ...
  COMPONENT_REGISTRY = {}
  ...
  def load_components(filepath="data/components.json"):
      global COMPONENT_REGISTRY
  ```
- `game/simulation/entities/ship.py`:
  ```python
  VEHICLE_CLASSES: Dict[str, Any] = {}
  ...
  def load_vehicle_classes(...):
      global VEHICLE_CLASSES
  ```

**Impact:**
- **Test Pollution:** Tests modifying these registries (e.g., adding a dummy component) affect subsequent tests unless manually cleared.
- **Race Conditions:** Inconceivable to run concurrent simulation contexts (e.g., a "Simulation Preview" in the UI while the game runs) because they share the same datastore.

**Issue 2: Hard-Coded Global Access (Tight Coupling)**
Classes query these globals directly rather than accepting them as dependencies.

**Evidence:**
- `Component.__init__` does a local import to access `MODIFIER_REGISTRY`.
- `Component.add_modifier` checks `if mod_id not in MODIFIER_REGISTRY`.
- `Ship.__init__` directly queries `VEHICLE_CLASSES.get(self.ship_class)`.
- `Ship.update_derelict_status` accesses `VEHICLE_CLASSES`.
- `Ship.from_dict` accesses `COMPONENT_REGISTRY` and `MODIFIER_REGISTRY`.

**Impact:**
- **Dependency Inversion Violation:** High-level entities (`Ship`) depend on specific global state implementations.
- **Mocking Difficulty:** Validating `Ship` logic requires side-loading data into global `VEHICLE_CLASSES` rather than passing a mock configuration.

### 2.2 Circular Dependencies & Import Hacks

**Issue 3: Lazy Import Workarounds**
To support the global registry pattern, methods often invoke imports locally to avoid import-time cycles.

**Evidence:**
- `Component.__init__` -> `from game.simulation.components.component import MODIFIER_REGISTRY`
- `Component.get_abilities` -> `from game.simulation.components.abilities import ABILITY_REGISTRY`
- `Component._instantiate_abilities` -> `from game.simulation.systems.resource_manager import ABILITY_REGISTRY`

**Impact:**
- **Code Smell:** Indicates that the architecture is fighting against the Python import system.
- **Performance:** Repeated imports inside tight loops (like `_instantiate_abilities` or `update`) can have overhead, though Python caches modules.
- **Fragility:** Moving files becomes high-risk as these string-based or deferred imports break easily.

### 2.3 Backward Compatibility

**Issue 4: Legacy Type Mapping**
The system creates generic `Component` objects for distinct types (`Weapon`, `Engine`) using `COMPONENT_TYPE_MAP`.

**Evidence:**
- `COMPONENT_TYPE_MAP` maps 18 keys (e.g., "Bridge", "Shield") to the single `Component` class.
- `Ship._initialize_layers` contains fallback logic for when layer definitions are missing (Lines 257-263).

**Analysis:**
This is actually a **good** pattern for data-driven design (Phase 7 Simplified), but the implementation relies on the global `COMPONENT_REGISTRY` to store the resulting instances. The backward compatibility logic itself is sound, but its storage mechanism is flawed.

## 3. Recommendations

### 3.1 Introduce `RegistryManager`
Create a unified context object that holds the registries.

```python
class RegistryManager:
    def __init__(self):
        self.components = {}
        self.modifiers = {}
        self.vehicle_classes = {}
        self.abilities = {}
        
    def load_data(self, path):
        # Implementation of loading logic here
        pass
```

### 3.2 Context Injection
Refactor `Ship` and `Component` to accept a `context` or `registry_source` argument, defaulting to a Proxy looking at the old Globals (for backward compatibility during refactor).

**Refactor Target:**
```python
# ship.py
class Ship:
    def __init__(self, ..., context=None):
        self.context = context or GlobalGameContext
        # self.context.vehicle_classes.get(...)
```

### 3.3 Strict "No Global Mutation" Policy
Tests must use a fresh `RegistryManager` instance. The `load_*` functions should return data rather than mutating globals, or be methods of the Manager.

### 3.4 Registry Proxy Pattern
To fix the circular imports without rewriting every line immediately, replace the global `MODIFIER_REGISTRY = {}` with a Proxy object that redirects to the active singleton manager. This allows `from module import MODIFIER_REGISTRY` to still work, but the underlying data is managed.

## 4. Critical Blockers identified in Code

1.  **`Ship.from_dict` Static Method:** Being static, it has no `self` context. It relies entirely on `COMPONENT_REGISTRY`. This must be changed to `Ship.from_dict(data, context)` or the registry lookup logic effectively remains global.
2.  **`Component` self-referential import:** The line `from game.simulation.components.component import MODIFIER_REGISTRY` inside `Component` methods is dangerous if we move `MODIFIER_REGISTRY` out of that file.

## 5. Conclusion

The current infrastructure is rigid and resistant to testing due to Hard-Coded Global Registries. The "Active Refactor" goal of "Test Context Injection" is strictly necessary. The immediate next step should be implementing the **RegistryProxy** to decouple the global symbols from their storage, allowing tests to inject isolated state.
