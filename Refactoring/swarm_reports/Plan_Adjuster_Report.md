# Plan Adjuster Report
**Date:** 2026-01-04
**Phase:** 1 (Stabilization) -> 2 (Adaptation)
**Focus:** General Analysis

## Executive Summary
The refactoring effort is currently transitioning from **Phase 1 (Stabilization)** to **Phase 2 (Adaptation)**. The core infrastructure (`RegistryManager`) and strict isolation rules (`conftest.py`) are in place. However, the legacy test suite structure (`setUpClass`) is fundamentally incompatible with the new isolation enforcement, leading to widespread failures in unmigrated tests.

## Key Findings

### 1. The `setUpClass` Conflict (Root Cause of 200+ Failures)
The majority of unit tests (`tests/repro_issues/*`, `tests/unit/*`) rely on `setUpClass` to initialize global state (loading components, ship data) **once** per test class.
*   **Mechanism:** `setUpClass` runs -> global registries populated.
*   **Conflict:** The new `autouse=True` fixture `reset_game_state` in `tests/conftest.py` runs **before every test method**.
*   **Result:** `reset_game_state` calls `RegistryManager.instance().clear()`, wiping the state populated by `setUpClass`. Tests execute with empty registries and fail immediately.

**Evidence:**
*   `tests/unit/test_combat.py` uses `setUpClass` to call `load_components`. This file is currently failing (or will fail) under the new harness.
*   `tests/unit/test_components.py` was successfully refactored to use `setUp`, resolving the issue for that file.

### 2. RegistryManager Implementation
The `RegistryManager` in `game/core/registry.py` is correctly implemented as a Singleton with `clear()` methods. It successfully decouples the global dictionaries from the module scope, allowing for the strict resets we require.

### 3. Performance Risk in Phase 2
Moving from `setUpClass` (load once per class) to `setUp` (load once per test) involves repeated file I/O (parsing JSONs).
*   **Current State:** `test_components.py` re-parses JSONs for every single test method.
*   **Risk:** This will significantly increase test suite runtime (potentially 10x-100x slower for IO-bound tests).
*   **Mitigation:** The "Session Cache" plan (Phase 3) should likely be pulled forward or integrated into Phase 2 if performance degrades too severely.

## Recommendations

### Immediate Actions (Phase 2)
1.  **Proceed with Bulk Migration:** convert `setUpClass` to `setUp` in all unit tests. This is the correct correctness fix.
2.  **Verify `test_combat.py`:** Use `test_combat.py` as the first candidate for migration, as it heavily relies on the failing pattern.

### Strategic Adjustments
1.  **Accelerate Caching Strategy:** Instead of waiting for Phase 3, consider implementing a simple `lru_cache` or module-level cache for `load_components` and `load_modifiers` immediately.
    *   *Concept:* `load_components` checks a private `_cache`. If present, it deep-copies to `RegistryManager`. If not, it loads from disk to `_cache` then copies.
    *   This mitigates the IO penalty of changing `setUpClass` -> `setUp` without requiring complex test harness changes.

## Phase Status Update
*   **Phase 1:** Complete. Core structural changes are live.
*   **Phase 2:** critical. The test suite is currently broken by design (correct infrastructure, incorrect consumers).

**Verdict:** The plan is sound, but the performance impact of the `setUp` migration requires proactive handling (Caching) to avoid a slow feedback loop.
