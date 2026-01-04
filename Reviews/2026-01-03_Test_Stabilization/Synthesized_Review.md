# Synthesized Code Review: Test Stabilization (Refactor Phase 1)

## Executive Summary
**Status: APPROVED WITH MODIFICATIONS**

The swarm has reached a consensus that the transition to `RegistryManager` is critical for eliminating state pollution. However, the initial plan lacked specific defenses against **Stale Reference Hazards** and **Data Starvation**. This synthesized plan incorporates a **Proxy Pattern** for backward compatibility and a **Mandatory Re-hydration** strategy for the test runner.

---

## Action Plan

### 1. Registry Infrastructure (Structural Fix)
- **[NEW] `game/core/registry_proxy.py`**: Implement a `RegistryProxy` (inheriting from `collections.abc.MutableMapping`) that dynamically delegates all lookups to the `RegistryManager`. This prevents "reference detaching" when registries are cleared/reset.
- **[NEW] `game/core/registry.py`**:
    - Implement the `RegistryManager` singleton.
    - Add a `register_registry(name, dict_instance, loader_func)` method.
    - Implement `.reset()`, which calls `.clear()` then invokes all registered `loader_func` targets.

### 2. Core Refactoring (Simulation Layer)
- **[MODIFY] `game/simulation/components/component.py`**:
    - Replace `COMPONENT_REGISTRY = {}` with `COMPONENT_REGISTRY = RegistryProxy("components")`.
    - Replace `MODIFIER_REGISTRY = {}` with `MODIFIER_REGISTRY = RegistryProxy("modifiers")`.
    - Update `load_components` to clear effectively or delegate to the Manager.
- **[MODIFY] `game/simulation/entities/ship.py`**: 
    - Replace `VEHICLE_CLASSES = {}` with `VEHICLE_CLASSES = RegistryProxy("vehicle_classes")`.
- **[MODIFY] `game/simulation/ship_validator.py`**: 
    - Add a `reset()` method to the `ShipDesignValidator` class to clear custom rules. Register it with `RegistryManager`.

### 3. Test Harness (Enforcement)
- **[NEW] `tests/conftest.py`**:
    - Implement an `autouse=True` fixture that calls `RegistryManager.instance().reset()` before every test.
- **[NEW] `tests/repro_issues/test_sequence_hazard.py`**:
    - "Canary" test: Test A writes to the manager; Test B asserts the manager is fresh.

---

## Adjudication Notes

### On Reference Handling:
**Challenge**: How to support `from component import COMPONENT_REGISTRY` without breaking when the internal dict is cleared?
**Decision**: Adopted the **Proxy Pattern** suggested by the Core Architect. This is superior to `__getattr__` or global rebinding because it works with existing import semantics and prevents "Stale References".

### On "Clear" vs "Reset":
**Challenge**: `clear()` leaves registries empty, causing crashes in tests expecting standard game data.
**Decision**: Standardized on a **`reset()` protocol** (Clear + Reload). The `RegistryManager` will track "Loader Callables" to perform re-hydration automatically.

### On Scope Expansion:
**Decision**: Included `MODIFIER_REGISTRY` and `ShipDesignValidator` state in the manager's scope as identified by the Context Specialist. These are confirmed pollution vectors.
