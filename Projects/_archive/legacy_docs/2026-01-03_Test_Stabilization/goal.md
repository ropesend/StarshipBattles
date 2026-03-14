# Refactor Goal: Test Stabilization via RegistryManager

## Background
The test suite currently suffers from "State Pollution" where global registries (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`) persist data between tests. This causes sequential test failures (e.g., `pytest -n0`).

## Proposed Solution
1. **RegistryManager Singleton**: Centralize all registries in `game/core/registry.py`. Provide a `.clear()` method.
2. **Deprecate Globals**: Update `game/simulation/components/component.py` and `game/simulation/entities/ship.py` to point their global dicts to the `RegistryManager.instance()`.
3. **Automated Reset**: Add an autouse fixture in `tests/conftest.py` that calls `clear()` before/after every test.
4. **Hazard Test**: Create `tests/repro_issues/test_sequence_hazard.py` as a "canary" to verify state isolation.

## Review Focus
- **Backwards Compatibility**: Ensure that third-party code or existing tests still work if they access the global dicts directly (proxied via `RegistryManager`).
- **Completeness**: Are there other globals (e.g., `MODIFIER_REGISTRY`) that need encapsulation?
- **Robustness**: Does the `conftest.py` fixture cover all necessary state? Is the hazard test sufficiently "poisonous"?
