# Test Strategist Report: Verification & Test Harness

**Status:** 🔴 **CRITICAL GAPS IDENTIFIED**
**Focus:** Verification Infrastructure, Test Isolation, State Management

## 1. High-Level Verdict
The current test harness is **unsustainable** for a growing codebase. The extensive use of global dictionaries (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`) combined with the absence of a centralized reset mechanism (`conftest.py`) guarantees **State Pollution**.

The "flaky" tests reported (e.g., `test_bug_12` failing only when run in suite) are a direct symptom of this architecture. Without immediate intervention, regression testing will become impossible as side effects accumulate across test cases.

## 2. Critical Issues Identified

### A. Lack of Test Lifecycle Management (The "Pollution Root")
- **Issue:** There is no `tests/conftest.py`.
- **Impact:** `pytest` has no central hook to reset state between tests.
- **Evidence:** `tests` directory contains 180+ tests but lacks the standard configuration file for fixtures.
- **Consequence:** State mutations (e.g., loading a custom ship class in Test A) persist into Test B, causing false failures or false positives.

### B. Unprotected Global Registries
- **Issue:** Core systems use raw dictionary assignment:
    - `game/simulation/components/component.py`: `COMPONENT_REGISTRY = {}`
    - `game/simulation/entities/ship.py`: `VEHICLE_CLASSES = {}`
- **Impact:** Any module can overwrite keys or clear these dicts. A test that mocks a component often inadvertently modifies the "production" registry for subsequent tests.
- **Risk:** **High**. Use of `global` keyword in `load_components` and `load_vehicle_classes` makes it easy to accidentally wipe data or inject mock data that persists.

### C. Missing "Re-hydration" Loop
- **Issue:** Even if we implement `RegistryManager.clear()`, the game systems rely on data being present at import time or initialization time.
- **Impact:** Clearing registries without immediate reloading ("re-hydration") will cause "Data Starvation" crashes (e.g., `KeyError: 'Escort'` when trying to spawn a ship).
- **Recommendation:** usage of `custom_registry.reset()` must automatically trigger `loader_func` execution.

## 3. Strategic Recommendations (The Protocol)

### Phase 1: Infrastructure (The Harness)
1.  **Create `tests/conftest.py`:**
    - Must include an `autouse=True` fixture.
    - Must call `RegistryManager.reset()` (not just clear).
2.  **Implement `RegistryManager` & `RegistryProxy`:**
    - **Proxy Pattern** is essential to avoid breaking imports. `from component import COMPONENT_REGISTRY` must continue to work, but `COMPONENT_REGISTRY` must be a proxy object, not a dict.

### Phase 2: Verification
1.  **Canary Testing:**
    - Create `tests/repro_issues/test_state_isolation.py`.
    - **Test:** Verify that modifying a registry in one test does not affect a subsequent test.
2.  **Legacy Suite Stabilization:**
    - Run the full suite (`pytest`) to confirm `test_bug_12` and `test_bug_10` no longer fail due to pollution.

## 4. Code Directives (For Swarm)

**To Dependency Analyst:**
- Ensure `registry_proxy.py` mimics `MutableMapping` perfectly to satisfy type checkers and legacy code usage.

**To Refactor Agent:**
- **DO NOT** simply replace `COMPONENT_REGISTRY = {}` with `RegistryManager.instance()`. This breaks `from X import Y` patterns. Use the Proxy.

## 5. Summary of Required Changes
| Component | Current State | Required State |
| :--- | :--- | :--- |
| **Harness** | None (`pytest.ini` only) | `tests/conftest.py` with global reset fixture |
| **Registries** | `Global Dict` | `RegistryProxy` pointing to `RegistryManager` |
| **Lifecycle** | Manual Load | Automated Reset & Reload (Re-hydration) |

---
**Signed:** Test Strategist Agent
