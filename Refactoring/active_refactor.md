# Active Refactor: Test Stabilization and Registry Encapsulation

**Goal:** Eliminate "State Pollution" in the test suite by encapsulating global registries (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`) into a `RegistryManager` and enforcing strict state resets.
**Status:** Planning / Phase 1 Execution
**Start Date:** 2026-01-04

## Migration Map (The Constitution)

| Concept | Old Pattern (Deprecated) | New Pattern (Enforced) |
| :--- | :--- | :--- |
| **Component Registry** | `game.simulation.components.component.COMPONENT_REGISTRY` | `RegistryManager.instance().components` |
| **Modifier Registry** | `game.simulation.components.component.MODIFIER_REGISTRY` | `RegistryManager.instance().modifiers` |
| **Vehicle Classes** | `game.simulation.entities.ship.VEHICLE_CLASSES` | `RegistryManager.instance().vehicle_classes` |
| **Access Pattern** | Direct Global Access / `global` keyword | `RegistryManager.instance()` or Context Injection |
| **Test Cleanup** | Manual `clear()` or None (Pollution) | Autouse `reset_game_state` fixture |

## Test Triage Table

| Test File | Status | Notes |
| :--- | :--- | :--- |
| `tests/repro_issues/test_sequence_hazard.py` | [PENDING] | **New Canary Test**. Must fail before fix, pass after. |
| `tests/unit/` | [PENDING] | Regression suite. |

## Phased Schedule

### Phase 1: Infrastructure & Hazard Verification
**Objective:** Establish the `RegistryManager` and prove pollution exists.
1. [ ] **Create Canary Test:** `tests/repro_issues/test_sequence_hazard.py` to demonstrate pollution.
2. [ ] **Create Manager:** `game/core/registry.py` implementing `RegistryManager` singleton.
3. [ ] **Refactor Core:**
    *   Update `component.py` to use `RegistryManager`.
    *   Update `ship.py` to use `RegistryManager`.
4. [ ] **Enforce Cleanup:** Create/Update `tests/conftest.py` with `reset_game_state` fixture.
5. [ ] **Verify:** Run Canary Test and Unit Tests.

### Phase 2: Component Decoupling (TBD)
*   Refactor Component classes to remove local import hacks.
*   Implement full Dependency Injection for `Ship`.
