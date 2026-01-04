# Infrastructure Engineer Report: Registry Management & Core Migration

## 1. Executive Summary
The codebase currently relies heavily on **Module-Level Mutable Globals** for its core registries (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`). This architectural pattern is the primary source of **state pollution** in the test suite, as these dictionaries persist across test boundaries unless explicitly cleared. Furthermore, the extensive use of **Local Imports** (imports inside functions) to avoid circular dependencies indicates a fragile initialization order that complicates the migration to a strictly typed, dependency-injected system.

## 2. Analysis: `game/simulation/components/component.py`

### 2.1 Global/Module-Level State (CRITICAL)
The following global dictionaries are defined at the module level:
- `MODIFIER_REGISTRY = {}` (Line 40)
- `COMPONENT_REGISTRY = {}` (Line 414)

Methods like `load_modifiers` and `load_components` mutate these globals directly.
- **Risk:** Tests running in parallel or sequentially without teardown will share these registries. If a test modifies a component definition, it pollutes subsequent tests.
- **Migration Impact:** These must be encapsulated into a `RegistryManager` class.

### 2.2 Circular Import Workarounds
The code uses deferred imports to bypass circular dependency issues:
- `from game.simulation.systems.resource_manager import ABILITY_REGISTRY` is imported inside `__init__`, `_instantiate_abilities`, and `get_abilities`.
- `from game.simulation.components.component import MODIFIER_REGISTRY` is imported inside `__init__` (Line 71), which is a self-module import, indicating extreme fragility in load order.

### 2.3 Legacy Type Mapping
- `COMPONENT_TYPE_MAP` (Line 423) hardcodes mappings of string types to the `Component` class.
- **Suggestion:** This mapping effectively reduces to a single class `Component`. The registry system should be data-driven rather than hardcoded in python.

## 3. Analysis: `game/simulation/entities/ship.py`

### 3.1 Global/Module-Level State (CRITICAL)
- `VEHICLE_CLASSES = {}` (Line 29) creates a distinct global registry for ship hulls.
- `SHIP_CLASSES = VEHICLE_CLASSES` (Line 30) creates an alias, doubling the reference cleanup requirement.
- `load_vehicle_classes` (Line 32) lacks safeguards against partial loading or validation during reload.

### 3.2 Singleton Misuse
- `_VALIDATOR = ShipDesignValidator()` (Line 25) creates a module-level singleton instance at import time.
- `VALIDATOR` exposes this globally.
- **Risk:** If `ShipDesignValidator` maintains any internal cache (stateful), it is a pollution vector. Even if stateless, it prevents mocking the validator for unit tests of the `Ship` class.

### 3.3 Implicit Coupling
The `Ship` class specifically relies on the global `VEHICLE_CLASSES` being pre-populated:
```python
class_def = VEHICLE_CLASSES.get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})
```
This requires that `initialize_ship_data` be called globally before any `Ship` object is instantiated, which is an external side-effect dependency.

## 4. Recommendations for Core Migration

### 4.1 Introduce `RegistryManager`
Refactor the distinct global dicts into a unified manager:
```python
class RegistryManager:
    def __init__(self):
        self.components = {}
        self.modifiers = {}
        self.vehicle_classes = {}
        self.abilities = {}
```

### 4.2 Dependency Injection
Modify `Ship` and `Component` validation logic to accept a `registry` argument, defaulting to a Proxy of the global manager (for backward compatibility) but allowing tests to inject an isolated registry.

### 4.3 Deprecate Local Imports
Once the `RegistryManager` is central, the circular dependency on `ABILITY_REGISTRY` can be resolved by passing the ability definitions via the manager at runtime, or initializing the manager in a centralized bootstrap module that handles import order.

### 4.4 Validator Lifecycle
Move `ShipDesignValidator` instantiation effectively inside the context where it is needed, or allow it to be injected into `Ship` instances, rather than relying on `_VALIDATOR`.
