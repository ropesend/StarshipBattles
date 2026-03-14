# Core_Architect Report: Registry Encapsulation and Backward Compatibility

## High-Level Verdict
**APPROVE WITH CAUTION**

The proposal to centralize registries via `RegistryManager` is architecturally sound and necessary for test stabilization. However, the "Backwards Compatibility" requirement creates a significant **Stale Reference Hazard**. Simply pointing the existing global variables to the singleton *once* is insufficient if the underlying data structures are replaced during `clear()` or re-initialization.

## Critical Issues (blocking)

### 1. Stale Reference Hazard in Global Exports
Files that perform `from game.simulation.components.component import COMPONENT_REGISTRY` bind a reference to the specific dictionary object at import time. 
- **The Hazard**: If `RegistryManager.clear()` replaces the dictionary instance (e.g., `self.components = {}`), all external modules holding the old reference will effectively be "detached" from the registry, continuing to see stale or empty data while the system uses the new one.
- **Blocking Requirement**: The global variables (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`) must be converted to **Proxy Objects** (e.g., inheriting from `collections.abc.MutableMapping`) that dynamically delegate to `RegistryManager.instance().get_registry(...)`. They cannot simply be aliases to a dictionary.

### 2. 'load_components' Global Variable Shadowing
In `game/simulation/components/component.py`:
```python
def load_components(filepath="data/components.json"):
    global COMPONENT_REGISTRY
    # ...
```
If `COMPONENT_REGISTRY` becomes a proxy object or a property, using the `global` keyword and potentially assigning to it (even accidentally) could overwrite the proxy with a raw dict, breaking the singleton link. The loading logic should be moved *into* the `RegistryManager`, and the legacy `load_components` function should just call `RegistryManager.instance().load_components()`.

## Questions (ambiguities)

1. **Wait-state behavior?**: If `RegistryManager` is cleared, and a static module attempts to access a registry before it is retrace-hydrated (e.g., during import side-effects), should it raise an error or return an empty dict? (Fail-fast vs. Resilience).
2. **`module.__getattr__` availability**: Is the target python version >= 3.7? If so, we can use [PEP 562](https://peps.python.org/pep-0562/) (`def __getattr__(name)`) at the module level in `component.py` to intercept access to `COMPONENT_REGISTRY` and redirect it to the Manager dynamically, avoiding the need for a complex Proxy class.

## Code Suggestions (diffs)

### Mitigation for Stale References (Proxy Pattern)
Do not expose the raw dict. Use a proxy explicitly.

```python
# game/core/registry_proxy.py (New utility)
from collections.abc import MutableMapping

class RegistryProxy(MutableMapping):
    def __init__(self, registry_type):
        self.registry_type = registry_type

    @property
    def _target(self):
        # Dynamic lookup every time
        from game.core.registry import RegistryManager
        return RegistryManager.instance().get(self.registry_type)

    def __getitem__(self, key): return self._target[key]
    def __setitem__(self, key, value): self._target[key] = value
    def __delitem__(self, key): del self._target[key]
    def __iter__(self): return iter(self._target)
    def __len__(self): return len(self._target)
    def __repr__(self): return repr(self._target)
```

### Refactoring `component.py`
Redirect globals to the proxy.

```python
# game/simulation/components/component.py

# ... imports ...

# REPLACE global dicts with Proxies
# COMPONENT_REGISTRY = {} 
# MODIFIER_REGISTRY = {}
from game.core.registry_proxy import RegistryProxy
COMPONENT_REGISTRY = RegistryProxy("components")
MODIFIER_REGISTRY = RegistryProxy("modifiers")

# ...

def load_components(filepath="data/components.json"):
    # REMOVE global keyword, use the Proxy
    # global COMPONENT_REGISTRY 
    
    # Ideally, delegate entirely:
    # RegistryManager.instance().load_components(filepath)
    
    # But for minimal diff, just ensure we write to the proxy:
    # ... (existing json loading) ...
    for comp_def in data['components']:
         # ... creation logic ...
         COMPONENT_REGISTRY[comp_def['id']] = obj # Writes through proxy to Singleton
```

### Refactoring `ship.py`
Similarly for Vehicle Classes.

```python
# game/simulation/entities/ship.py

# VEHICLE_CLASSES: Dict[str, Any] = {}
from game.core.registry_proxy import RegistryProxy
VEHICLE_CLASSES = RegistryProxy("vehicle_classes")
SHIP_CLASSES = VEHICLE_CLASSES # Alias still works
```
