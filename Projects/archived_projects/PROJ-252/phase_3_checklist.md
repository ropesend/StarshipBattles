# Phase 3: Eliminate Global Registry from Simulation

**Objective:** Remove all `get_default_registry_provider()` calls from `game/simulation/` code and replace with dependency injection from the Ship's existing registries.

**Key Principle:** Simulation-domain code must never call global lookup functions. Registries are injected via constructors, matching the documented strict-DI contract in `docs/02_PATTERNS.md:202`.

---

## Background

`ShipComponentManager` and `ShipValidatorHelper` call `get_default_registry_provider()` inside simulation-domain code at 6+ call sites. This violates the strict-DI contract documented in `02_PATTERNS.md`. The Ship class already holds `_registries` and enforces it via constructor validation — but its delegates bypass this by calling the global.

Note: `ship_component_manager.py` already has a `# PROJ-211` comment acknowledging this debt.

## Design

1. `ShipComponentManager.__init__` already receives `Ship` — extract `self._registries = ship._registries`
2. Replace all `get_default_registry_provider()` calls in `ShipComponentManager` with `self._registries`
3. `ShipValidatorHelper` — accept `registries` in constructor, store, use in all methods
4. Grep for any remaining `get_default_registry_provider` in `game/simulation/` and migrate

---

## Checklist

### Discovery
- [ ] Grep `game/simulation/` for all `get_default_registry_provider` calls — confirm complete list
- [ ] Verify Ship class holds `_registries` and can provide them to delegates
- [ ] Check `ShipComponentManager.__init__` signature — confirm Ship is already passed
- [ ] Check `ShipValidatorHelper.__init__` signature — determine what's currently passed

### Tests First (TDD)
- [ ] Write test: `ShipComponentManager.add_component()` works without any default registry provider set
- [ ] Write test: `ShipComponentManager.add_components_bulk()` works without any default registry provider set
- [ ] Write test: `ShipValidatorHelper.check_validity()` works without any default registry provider set
- [ ] Write test: importing `game.simulation.entities.ship_component_manager` does not require a default provider
- [ ] Run tests — confirm they fail (current code calls global and will crash without it)

### Implementation
- [ ] Update `ShipComponentManager.__init__` to extract registries from Ship: `self._registries = ship._registries`
- [ ] Replace `get_default_registry_provider()` at line ~96 in `add_component()` with `self._registries`
- [ ] Replace `get_default_registry_provider()` at line ~137 in `add_components_bulk()` with `self._registries`
- [ ] Replace any other `get_default_registry_provider()` calls in `ShipComponentManager`
- [ ] Update `ShipValidatorHelper.__init__` to accept `registries` parameter
- [ ] Replace `get_default_registry_provider()` calls at lines ~44, ~55, ~64 in `ShipValidatorHelper`
- [ ] Remove unused `get_default_registry_provider` imports from both files
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python Tools/test_sharded/test_sharded.py`) — no regressions
- [ ] Run simulation tests (`python -m simulation_tests.run_tests`) — all pass
- [ ] Grep `game/simulation/` for `get_default_registry_provider` — should return zero results
- [ ] Remove `# PROJ-211` comment if present (debt is now paid)
