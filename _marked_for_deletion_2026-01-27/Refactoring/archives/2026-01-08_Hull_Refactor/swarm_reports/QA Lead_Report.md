# QA Lead Report: Phase 2 Hull Refactor

**Role:** QA Lead
**Focus:** Verification Plan & Test Coverage
**Phase:** 2 (Ship.py Core Logic Refactor)

## 1. Executive Summary

The verification environment for Phase 2 is currently in a fragmented state. While foundational infrastructure like `RegistryManager` and `SessionRegistryCache` exists, critical unit tests and the test orchestration layer (`conftest.py`) are either missing or misplaced. The primary focus of this phase's verification must be the **restoration of test isolation** and the implementation of **unified hull-stat verification**.

## 2. Identified Issues & Gaps

### 2.1 Critical Missing Files
The following files, required for Phase 2 verification, are missing from the `tests/` directory:
- `tests/conftest.py`: (Found in root `C:\Dev\Starship Battles\conftest.py` but flagged as missing for the `tests/` package context). This file is essential for preventing state pollution between tests.
- `tests/unit/entities/test_ship_core.py`: Missing coverage for the new unified Ship/Hull logic.
- `tests/unit/ui/test_builder_inventory.py`: Missing coverage for the UI data sourcing from the new ability system.

### 2.2 Test Isolation & State Pollution
Existing tests (e.g., `tests/unit/entities/test_ship.py`) rely on manual `setUp()` initialization:
```python
def setUp(self):
    initialize_ship_data() 
    load_components("data/components.json")
```
> [!WARNING]
> This pattern bypasses the `RegistryManager.clear()`/`hydrate()` logic defined in the root `conftest.py`. This leads to:
> 1.  **Redundant Disk I/O**: Constant reloading of JSON data.
> 2.  **State Leakage**: Registry modifications in one test affecting others.

### 2.3 Verification Strategy for Phase 2 (Hull Refactor)
Phase 2 aims to unify Ship stats under the V2 Ability System. verification must focus on:
- **Hull Component as Source of Truth**: Ensuring `Ship` base mass and base HP are derived purely from the special `Hull` component rather than legacy attributes in `ship_class` definitions.
- **Ability Aggregation**: Validating that all resources (Fuel, Energy, Ammo) are correctly aggregated via `ShipStatsCalculator` from V2 ability instances.

## 3. Recommended Actions

1.  **Re-establish `tests/conftest.py`**: Ensure the `reset_game_state` fixture is active and enforced across all unit tests.
2.  **Implement `test_ship_core.py`**: Create a focused unit test for the `Ship` class that mocks the `Hull` component to verify stat derivation without loading full dependency chains.
3.  **Audit `RegistryManager` Usage**: Ensure the Core Engineer replaces any remaining direct registry access with the `get_registry_...` utility functions to maintain mockability.

## 4. Test Coverage Checklist

- [ ] `Ship` initialization correctly creates a dummy/default `Hull` component if none exists.
- [ ] `Ship.mass` equals `Hull.mass` + all other components.
- [ ] `Ship.hp` equals `Hull.hp` + all other components.
- [ ] `RegistryManager` is correctly cleared after test execution (verified via `conftest.py`).
