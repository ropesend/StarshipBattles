# Context Specialist Report: Registry & State Analysis

**Role:** Context_Specialist
**Focus:** Identifying all pollutable singletons and ensuring schema consistency.

## High-Level Verdict
**APPROVE with Critical Additions.**
The proposed `RegistryManager` is essential. The current codebase uses module-level dictionaries that are mutated by loading functions. Crucially, some loading functions (`load_components`, `load_modifiers`) do **not** clear the registry before loading, meaning any test that adds a test-specific item permanently pollutes the registry for the process lifetime.

## Critical Issues (Blocking)

### 1. Cumulative Pollution in `load_components` and `load_modifiers`
Unlike `load_vehicle_classes`, which calls `.clear()` before updating, `load_components` and `load_modifiers` merely set keys.
*   **Location:** `game/simulation/components/component.py`
*   **Risk:** Tests that register mock components (e.g. `COMPONENT_REGISTRY['test_comp'] = ...`) or load custom internal data will leave artifacts that persist across all subsequent tests.
*   **Requirement:** The `RegistryManager` must not only clear but ideally **reset** these to a known base state, or the `conftest` fixture must strictly handle re-loading.

### 2. Identifying all Pollutable State
The following globals must be managed by `RegistryManager`:

| Registry | Location | Mutable? | Loader Function | Danger Level |
| :--- | :--- | :--- | :--- | :--- |
| `COMPONENT_REGISTRY` | `game/simulation/components/component.py` | Yes | `load_components` | **CRIT** (No Clear) |
| `MODIFIER_REGISTRY` | `game/simulation/components/component.py` | Yes | `load_modifiers` | **CRIT** (No Clear) |
| `VEHICLE_CLASSES` | `game/simulation/entities/ship.py` | Yes | `load_vehicle_classes` | HIGH (Clears first) |
| `SHIP_CLASSES` | `game/simulation/entities/ship.py` | Yes | (Alias) | LOW |
| `_VALIDATOR` | `ship_validator.py` | Yes* | N/A | MED (Rules list) |
| `ABILITY_REGISTRY` | `game/simulation/components/abilities.py`| Yes* | Static Init | MED (Monkeypatching) |

* *Validator*: The `ShipDesignValidator` is a singleton instance (`_VALIDATOR`) instantiated at module level. While its logic is mostly stateless, it holds `addition_rules` and `design_rules` lists. If a test modifies these lists (e.g. adding a mock validation rule), checking validity in later tests will yield incorrect results.

### 3. Registry Identity vs Reference Holding
Several modules likely import these registries directly (e.g., `from component import COMPONENT_REGISTRY`).
*   If `RegistryManager` replaces the dictionary object (`component.COMPONENT_REGISTRY = {}`), modules holding the old reference will be desynchronized.
*   **Constraint:** `RegistryManager` must operate by `clearing` the existing dictionary objects, not rebinding them, OR all call sites must be updated to use accessors.

## Questions (Ambiguities)

1.  **Validator Reset:** Should `RegistryManager` also track singleton instances like `_VALIDATOR`?
    *   *Recommendation:* Yes. Add a `reset()` method to the validator or allow `RegistryManager` to re-instantiate it.
2.  **Default Data State:** clearly `.clear()` is destructive. Does the `Autouse Fixture` described in the goal imply "Clear and Leave Empty" or "Reset to Default Game Data"?
    *   *Context:* Most tests expect standard components (e.g. "Bridge") to exist.
    *   *Recommendation:* The fixture must be `Reset to Defaults`. `RegistryManager` should have a `load_defaults()` method that calls the `load_*` functions.

## Code Suggestions

### Diff 1: Add Clear to Component Loader
`game/simulation/components/component.py`
```diff
def load_components(filepath="data/components.json"):
    global COMPONENT_REGISTRY
    import os
    
+   # Prevent cumulative pollution
+   COMPONENT_REGISTRY.clear()

    # Try absolute path based on this file if CWD fails
    if not os.path.exists(filepath):
```

### Diff 2: RegistryManager Schema (Draft)
`game/core/registry.py`
```python
class RegistryManager:
    _instance = None
    
    def __init__(self):
        self._registries = []
        self._loaders = []

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_registry(self, name: str, registry_dict: dict, loader_func=None):
        """
        Register a dictionary to be managed.
        registry_dict: The actual global dictionary object (passed by ref).
        loader_func: Optional callable to reload default data.
        """
        self._registries.append((name, registry_dict, loader_func))

    def clear(self):
        """Clear all registries."""
        for name, reg, _ in self._registries:
            reg.clear()
            
    def reset(self):
        """Clear and Reload Defaults."""
        self.clear()
        for name, _, loader in self._registries:
            if loader:
                loader()
```

### Diff 3: Integration Point
`game/simulation/components/component.py`
```python
# ... bottom of file ...
from game.core.registry import RegistryManager
RegistryManager.instance().register_registry("components", COMPONENT_REGISTRY, load_components)
RegistryManager.instance().register_registry("modifiers", MODIFIER_REGISTRY, load_modifiers)
```
