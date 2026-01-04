# Dependency Analyst Report
**Focus:** Infrastructure & Core Refactoring
**Date:** 2026-01-03

## 1. Executive Summary
The `game/simulation` core infrastructure suffers from **Critical State Pollution Hazards** due to the use of module-level global variables for component and modifier registries. This architecture prevents reliable parallel testing and introduces "spooky action at a distance" where one test's teardown (clearing a global registry) can corrupt the state of another test or the running application.

Additionally, **Circular Dependencies** are rampant between `component.py`, `modifiers.py`, and `resource_manager.py`, currently managed via fragile function-level imports.

## 2. Critical Infrastructure Issues

### 2.1 Global Registry Pollution (High Severity)
**Violation:** Global Mutable State
**Location:** `game/simulation/components/component.py`

```python
# component.py:449
COMPONENT_REGISTRY = {} 

# component.py:510
MODIFIER_REGISTRY = {}
```

**Impact:**
- **Test Isolation Failure:** Tests that load components mutate this global state. `builder_screen.py` explicitly calls `COMPONENT_REGISTRY.clear()`, which is a "scorched earth" tactic that breaks concurrent execution or persistent environments.
- **Race Conditions:** In any threaded context, unrestricted access to these globals will cause corruption.
- **Hidden Dependencies:** Functions rely on these globals being populated "at some point" before execution, leading to `KeyError` crashes if the specific loading sequence wasn't followed (e.g., `load_components()` not called).

### 2.2 Circular Dependency Spaghetti (Medium Severity)
**Violation:** Tight Coupling / Import Cycles
**Location:** `component.py`, `abilities.py`, `resource_manager.py`

The codebase relies on function-level imports to bypass circular dependency errors at import time:
- `component.py` imports `ABILITY_REGISTRY` inside methods.
- `component.py` imports `MODIFIER_REGISTRY` (from itself!) inside methods to handle scope issues.
- `resource_manager.py` imports `ABILITY_REGISTRY`.

**Impact:**
- **Fragility:** Moving code breaks these delicate import chains easily.
- **Performance:** Repeated import calls inside tight loops (like `update()`) add unnecessary overhead, though Python caches them, the pattern indicates design failure.

## 3. Analysis Findings

| Component | Issue | Risk | Recommendation |
| :--- | :--- | :--- | :--- |
| `component.py` | `COMPONENT_REGISTRY` Global | Critical | **Refactor to Dependency Injection.** Pass a `Registry` instance to Component Factories/Loaders. |
| `component.py` | `MODIFIER_REGISTRY` Global | Critical | Move to `RegistryManager`. |
| `builder_screen.py` | Direct Registry Clearing | High | Remove direct access. Use `RegistryManager.reset()` or scoped test fixtures. |
| `abilities.py` | `ABILITY_REGISTRY` (Dict) | Low | This is stateless (Factory Pattern), which is acceptable, but should ideally be wrapped in a Service. |

## 4. Recommendations for Core Refactoring

### Phase 1: Registry Encapsulation (Immediate)
Identify all usage of `COMPONENT_REGISTRY` and wrap it in a Singleton `RegistryManager` (as a stopgap) that locks access and provides controlled `reset()` methods for testing.

**Proposed Interface:**
```python
class RegistryManager:
    _instance = None
    def __init__(self):
        self.components = {}
        self.modifiers = {}
    
    @classmethod
    def get(cls):
        if not cls._instance: cls._instance = RegistryManager()
        return cls._instance
```

### Phase 2: Dependency Injection (Long Term)
Remove the global `RegistryManager` usage from `Component` class methods. Instead, pass the context (including registries) into `update()` or `instantiate()` methods.

### Phase 3: Consolidation
Move all Registry definitions (`ABILITY_REGISTRY`, `COMPONENT_REGISTRY`, etc.) to a dedicated `game.core.registries` module to break circular dependency chains in `component.py` and `resource_manager.py`.

## 5. Conclusion
The current infrastructure is "brittle" due to global state. Refactoring to a **Registry Service Pattern** is the highest priority instruction to stabilize the Test Suite and prevent "State Pollution" regressions.
