# Test Isolation Analysis Report

**Analyst:** Test Isolation Analyst (Code Review Agent)
**Date:** 2026-02-27
**Scope:** 18 files referencing `get_default_registry_provider()` in tests and test infrastructure

---

## Summary

- **Total issues found:** 14
- **Critical:** 1
- **Major:** 4
- **Minor:** 5
- **Info:** 4

### Overall Assessment

The test suite has a well-designed isolation architecture centered on the root `conftest.py`'s `reset_game_state` fixture (autouse, function-scoped). This fixture clears and re-hydrates the `RegistryManager` singleton before every test and cleans up afterward. However, several test files consume global state via `get_default_registry_provider()` inside test code (not fixtures), creating implicit coupling to the singleton hydration lifecycle. The simulation test subsystem (`simulation_tests/`) has its own isolation strategy via a class-scoped `isolated_registry` fixture, which creates a gap in isolation granularity compared to the function-scoped root fixture.

---

## Findings

---

#### MAJOR: Simulation `isolated_registry` is class-scoped, enabling intra-class state bleed
**ID:** TI-001
**Location:** `simulation_tests/conftest.py:75-111`
**Issue:** The `isolated_registry` fixture is scoped to `class`, meaning all test methods within a class share the same registry state. If one test method mutates the registry (e.g., adds components, modifies data), subsequent test methods in that class will see those mutations.
**Impact:** Tests within the same class are not isolated from each other. A test that adds or modifies registry data will affect all subsequent tests in that class. With `pytest-xdist` parallelization, different workers could execute different subsets of methods in an order-dependent way.
**Isolation Pattern:** Setup -- loads test-specific data into the singleton, cleans up after the class (not after each method).
**Recommendation:** Change the fixture scope from `class` to `function`, or add per-method cleanup. If performance is a concern (reloading data per test is expensive), add an explicit guard that restores registry state after each method using a nested function-scoped fixture.
**Effort:** Medium

---

#### MAJOR: `test_engine_physics.py` consumes global state via `get_default_registry_provider()` in test helper
**ID:** TI-002
**Location:** `simulation_tests/tests/test_engine_physics.py:28-41`
**Issue:** The `_load_ship` helper method calls `get_default_registry_provider()` directly to get registry data. While the class has `autouse=True` on the `setup` fixture which references `isolated_registry`, the `_load_ship` method reads from the singleton, creating a tight implicit coupling. If the `isolated_registry` fixture ever fails to populate the singleton (or if a test is run in isolation without the fixture chain), the test will get stale or empty data silently.
**Impact:** Tests pass today because the `isolated_registry` fixture populates the same singleton that `get_default_registry_provider()` reads from. But this is an accidental alignment -- the test code doesn't explicitly declare its dependency on isolated data through DI. Any future refactoring that changes how `isolated_registry` works could silently break these tests without a clear error.
**Isolation Pattern:** Consume -- reads from global state that was set up by a separate fixture.
**Recommendation:** Pass the registry data explicitly from the fixture rather than calling `get_default_registry_provider()` in test code. For example, store `self.registries` from the fixture and use it in `_load_ship`. Alternatively, create a `GameRegistries` from the fixture data and pass it directly to `Ship.from_dict()`.
**Effort:** Medium

---

#### MAJOR: `test_smoke.py` calls `get_default_registry_provider()` multiple times without explicit DI
**ID:** TI-003
**Location:** `simulation_tests/tests/test_smoke.py:21-58`
**Issue:** All three test methods (`test_vehicle_classes_loaded`, `test_components_loaded`, `test_ship_creation`) call `get_default_registry_provider()` directly in test body code. The class relies on `isolated_registry` (autouse) to populate the singleton. This is the same pattern as TI-002 but across three separate test methods, each independently reading global state.
**Impact:** Same as TI-002 -- implicit coupling to singleton hydration. Additionally, `test_vehicle_classes_loaded` tests infrastructure readiness by reading from the provider, but if the provider returns empty data (fixture failure), the test failure message won't indicate the root cause (fixture setup failure vs. actual loading bug).
**Isolation Pattern:** Consume -- reads from global state set up by a class-scoped fixture.
**Recommendation:** Refactor to receive registry data via the fixture. The `isolated_registry` fixture could yield the `RegistryManager` instance or a `GameRegistries` object, and test methods could use that directly instead of calling `get_default_registry_provider()`.
**Effort:** Simple

---

#### MAJOR: `simulation_tests/scenarios/base.py` `_load_ship` uses singleton in production-like pattern
**ID:** TI-004
**Location:** `simulation_tests/scenarios/base.py:356-368`
**Issue:** The `_load_ship` method in `TestScenario` calls both `RegistryManager.instance()` (for debug logging) and `get_default_registry_provider()` (to build `GameRegistries` for `Ship.from_dict`). This base class is used by all simulation test scenarios. The method has no DI parameter for registries -- it always reads from global state.
**Impact:** All simulation scenarios inheriting from `TestScenario` are coupled to the singleton. This makes it impossible to test scenarios with custom/isolated registry data without first modifying the global singleton. For pytest, this works because `isolated_registry` populates the singleton, but for any future test that needs different data (e.g., testing a scenario with a modified component), there's no way to inject it.
**Isolation Pattern:** Consume -- reads from global singleton.
**Recommendation:** Add an optional `registries` parameter to `_load_ship()` that defaults to `get_default_registry_provider()`. This enables DI while maintaining backward compatibility. Similarly, `_create_ship_with_components` at line 482 calls `Ship.from_dict(ship_data)` without passing registries at all, relying on whatever default `Ship.from_dict` uses.
**Effort:** Medium

---

#### CRITICAL: `test_protocols_boundary.py` `simple_ship` fixture consumes global state for Ship creation
**ID:** TI-005
**Location:** `tests/unit/core/test_protocols_boundary.py:23-44`
**Issue:** The `simple_ship` fixture calls `get_default_registry_provider()` directly (line 28), constructs `GameRegistries` from it (lines 31-36), and passes it to `Ship()`. This fixture does NOT request `fresh_registries` or any other DI fixture. It relies entirely on the root conftest's `reset_game_state` autouse fixture to have hydrated the singleton before this fixture runs.

This is a **critical** issue because this is a unit test in `tests/unit/core/` -- a location where tests should be maximally isolated. The test is verifying protocol conformance (structural typing), which should not depend on production data being present in the singleton. A test data-independent approach (using `fresh_registries` or `minimal_registries`) would be more appropriate.
**Impact:** If the root conftest fixture fails or is modified, this test breaks silently. The test also implicitly tests with production data when it only needs structural conformance -- any component data will do. The coupling to global state is unnecessary for what the test validates.
**Isolation Pattern:** Consume -- reads from global state for test object construction.
**Recommendation:** Replace the direct `get_default_registry_provider()` call with the `fresh_registries` fixture. The fixture should be:
```python
@pytest.fixture
def simple_ship(self, fresh_registries):
    ship = Ship(
        name="Test Ship",
        x=0.0, y=0.0,
        color=(255, 255, 255),
        registries=fresh_registries
    )
    return ship
```
**Effort:** Simple

---

#### MINOR: `test_workshop_context_di.py` backward-compat tests rely on singleton hydration
**ID:** TI-006
**Location:** `tests/unit/builder/test_workshop_context_di.py:53-72, 92-97, 110-118, 128-145`
**Issue:** Multiple test methods (`test_constructor_with_none_uses_default_provider`, `test_constructor_without_registries_uses_default_provider`, `test_standalone_without_registries_uses_default_provider`, `test_integrated_without_registries_uses_default_provider`, `test_standalone_works_without_registries_arg`, `test_integrated_works_without_registries_arg`) all test the fallback behavior where `WorkshopContext` calls `get_default_registry_provider()` internally. They rely on the root conftest having hydrated the singleton.
**Impact:** These tests are intentionally testing the "no registries provided" fallback path, so consuming global state is part of what they verify. However, they only assert `context.registries is not None` -- they don't verify the registries contain correct data. This means they would pass even with an empty singleton. The risk is low but the pattern is worth noting: these tests validate a code path that couples production code to the singleton.
**Isolation Pattern:** Consume (intentional) -- testing the fallback path that reads from global state.
**Recommendation:** Consider patching `get_default_registry_provider` in these tests to return a known mock, rather than relying on the autouse fixture. This would make the tests truly independent and also faster (no need for full hydration). Alternatively, accept the current pattern as it does test a real integration point.
**Effort:** Simple

---

#### MINOR: `test_design_loader_adapter.py` line 80 uses `fresh_registries` correctly but comment mentions removed function
**ID:** TI-007
**Location:** `tests/unit/ui/services/test_design_loader_adapter.py:80-92`
**Issue:** The `test_adapter_uses_real_loader_when_none_provided` test correctly requests the `fresh_registries` fixture, but doesn't actually use it. The fixture is listed as a parameter (line 80) but is never referenced in the test body. The comment on line 85-87 says "No longer need set_default_registries - adapter uses get_default_registry_provider()". The `fresh_registries` fixture is present purely as a side-effect marker indicating "this test needs real data", but the test code itself doesn't inject it anywhere.
**Impact:** Low -- the test still works because the root conftest's autouse `reset_game_state` hydrates the singleton regardless. The `fresh_registries` parameter is unused overhead. If someone removes the unused parameter during cleanup, the test continues to work the same way (relying on autouse fixture).
**Isolation Pattern:** Consume (indirect) -- test relies on global state; `fresh_registries` parameter is a no-op marker.
**Recommendation:** Either remove the unused `fresh_registries` parameter (since it doesn't affect the test) or actually use it by patching the adapter to use the injected registries instead of the global provider. The current state is misleading.
**Effort:** Simple

---

#### MINOR: `tests/unit/strategy/conftest.py` `reset_resource_registry` mutates singleton directly
**ID:** TI-008
**Location:** `tests/unit/strategy/conftest.py:14-23`
**Issue:** The `reset_resource_registry` fixture calls `RegistryManager.instance().resources.clear()` directly in both setup and teardown. This mutates the singleton's resource registry. While it has proper cleanup (clear in yield teardown), it directly manipulates global state rather than working through DI.
**Impact:** Low -- the cleanup is correct (clears before and after). However, this fixture interacts with the same singleton that the root conftest's `reset_game_state` manages. Since `reset_game_state` is autouse and runs for every test, there could be ordering issues: `reset_resource_registry` clears resources, then `reset_game_state` re-hydrates them, or vice versa. The interaction depends on pytest fixture ordering.
**Isolation Pattern:** Setup -- modifies global state with cleanup.
**Recommendation:** Verify fixture ordering doesn't cause unexpected interactions. Consider using `fresh_registries` instead of mutating the singleton directly. The `custom_resource_registry` fixture (line 38) already uses `fresh_registries`, which is the preferred pattern.
**Effort:** Simple

---

#### MINOR: `tests/unit/strategy/conftest.py` `mock_component_registry` patches `get_default_registry_provider`
**ID:** TI-009
**Location:** `tests/unit/strategy/conftest.py:127-134`
**Issue:** The `mock_component_registry` fixture returns a context manager that patches `game.strategy.services.ship_stats_calculator.get_default_registry_provider`. This is the correct approach for mocking, but the patch target is module-specific (`ship_stats_calculator`) rather than the central module (`game.core.registry`). If the import structure changes, the patch will silently stop working.
**Impact:** Low -- this is actually good DI-aware testing. The patch targets the specific import location, which is correct for `unittest.mock.patch`. The concern is fragility if imports are refactored.
**Isolation Pattern:** Mock -- proper patching of the provider.
**Recommendation:** No immediate change needed. This is a well-implemented mock pattern. Document the patch target dependency for future maintainers.
**Effort:** N/A

---

#### MINOR: `tests/integration/resource_system/conftest.py` `loaded_registry` returns singleton directly
**ID:** TI-010
**Location:** `tests/integration/resource_system/conftest.py:13-28`
**Issue:** The `loaded_registry` fixture returns `RegistryManager.instance()` directly. Tests using this fixture receive a reference to the actual singleton. Any mutations they make to the registry are visible globally. The docstring acknowledges this ("Relies on reset_game_state (autouse) for isolation") and explains the rationale ("ShipInstance.get_calculated_stats() internally uses get_default_registry_provider()").
**Impact:** This is an integration test, so global state usage is more acceptable. The fixture is function-scoped (default) and cleanup is handled by the root conftest's `reset_game_state`. However, if a test using `loaded_registry` adds components to the singleton and another test in the same module runs concurrently (xdist), there could be conflicts.
**Isolation Pattern:** Setup/Consume -- returns the global singleton for modification.
**Recommendation:** For integration tests, this pattern is acceptable as documented. If xdist parallelization causes flakiness, consider isolating these tests into a serialized test group.
**Effort:** N/A (acceptable for integration tests)

---

#### INFO: Root `conftest.py` provides robust singleton isolation
**ID:** TI-011
**Location:** `conftest.py:10-117`
**Issue:** Not an issue -- this is a positive finding. The root conftest's `reset_game_state` fixture is autouse, function-scoped, and has comprehensive pre-test cleanup, hydration, and post-test cleanup. It clears the `RegistryManager`, re-hydrates from `SessionRegistryCache`, patches loaders to prevent disk I/O, and then cleans up all singletons (RegistryManager, StrategyManager, ShipThemeManager, ScreenshotManager, SpriteManager, event handler, profiler, component caches) in the teardown. The PROJ-181 comment confirms that `set_default_registries()` was removed and all consumers now use `get_default_registry_provider()` which reads from the hydrated singleton.
**Impact:** This is the foundation of test isolation for the entire suite. It works correctly.
**Isolation Pattern:** Setup -- comprehensive global state management with cleanup.
**Recommendation:** None -- this is well-designed.
**Effort:** N/A

---

#### INFO: `test_registry_provider.py` legitimately tests the provider itself
**ID:** TI-012
**Location:** `tests/unit/core/test_registry_provider.py:1-368`
**Issue:** Not an issue. This file tests `IRegistryProvider`, `DefaultRegistryProvider`, `TestRegistryProvider`, and `get_default_registry_provider()` directly. The `TestDefaultRegistryProvider` and `TestGetResourcesMethod` classes have their own `reset_registry` autouse fixture that calls `RegistryManager.reset()` before and after each test. This is the correct approach for testing the provider infrastructure.
**Impact:** None -- tests are properly isolated and test legitimate behavior.
**Isolation Pattern:** Test -- testing the provider system itself with proper per-test reset.
**Recommendation:** None.
**Effort:** N/A

---

#### INFO: `test_component_service.py` demonstrates exemplary DI pattern
**ID:** TI-013
**Location:** `tests/unit/ui/services/test_component_service.py:1-256`
**Issue:** Not an issue -- positive finding. Almost every test creates a `MagicMock()` for the registry provider and injects it into `ComponentService(registry_provider=mock_provider)`. The one test that exercises the fallback path (`test_service_uses_default_registries_when_none_provided`, line 175) properly patches `get_default_registry_provider` to verify the fallback is called, rather than relying on the real singleton.
**Impact:** None -- this is the gold standard pattern for DI testing.
**Isolation Pattern:** Mock -- proper DI via constructor injection.
**Recommendation:** Use this file as a reference implementation for other test files.
**Effort:** N/A

---

#### INFO: `test_registry_features.py` uses proper local conftest with save/restore
**ID:** TI-014
**Location:** `tests/unit/core/registry/test_registry_features.py:1-300` (with `tests/unit/core/registry/conftest.py:1-67`)
**Issue:** Not an issue -- positive finding. The local conftest provides both a `reset_registry` autouse fixture (saves/restores singleton data including instance references) and a function-scoped `registry` fixture that resets and returns a fresh instance. The `test_registry_features.py` tests all use the `registry` fixture parameter, ensuring they operate on a known-clean state.
**Impact:** None -- comprehensive isolation.
**Isolation Pattern:** Setup -- save/restore pattern with both instance and data preservation.
**Recommendation:** None.
**Effort:** N/A

---

## Pattern Analysis: Files Using `get_default_registry_provider()` by Pattern

### Pattern 1: Setup (Fixture-level global state configuration)
| File | Pattern | Isolation Quality |
|------|---------|------------------|
| `conftest.py` (root) | Hydrates singleton, comprehensive cleanup | Excellent |
| `simulation_tests/conftest.py` | Class-scoped singleton hydration | Adequate (class-level) |
| `tests/unit/strategy/conftest.py` | Clears singleton resources | Adequate |
| `tests/integration/resource_system/conftest.py` | Returns singleton reference | Adequate (integration) |

### Pattern 2: Consume (Test code reads from global state)
| File | Pattern | Risk Level |
|------|---------|------------|
| `tests/unit/core/test_protocols_boundary.py` | `simple_ship` fixture reads provider | High |
| `simulation_tests/tests/test_engine_physics.py` | `_load_ship` helper reads provider | Medium |
| `simulation_tests/tests/test_smoke.py` | Test methods read provider directly | Medium |
| `simulation_tests/scenarios/base.py` | `_load_ship` and `_create_ship_with_components` | Medium |
| `tests/unit/builder/test_workshop_context_di.py` | Tests fallback path (intentional) | Low |

### Pattern 3: Mock/Patch (Proper DI-aware testing)
| File | Pattern | Quality |
|------|---------|---------|
| `tests/unit/ui/services/test_component_service.py` | Constructor injection + patch fallback | Exemplary |
| `tests/unit/strategy/conftest.py` | `mock_component_registry` patches provider | Good |
| `tests/unit/ui/screens/test_strategy_detail_formatter.py` | Patches `get_default_registry_provider` | Good |
| `tests/unit/ui/screens/test_planet_production_display.py` | Patches `get_default_registry_provider` | Good |
| `tests/unit/ui/panels/test_compute_planet_production.py` | Patches `get_default_registry_provider` | Good |

### Pattern 4: Test (Testing the provider system itself)
| File | Pattern | Quality |
|------|---------|---------|
| `tests/unit/core/test_registry_provider.py` | Tests provider classes and factory | Correct |
| `tests/unit/core/registry/test_registry_features.py` | Tests registry features with proper fixtures | Correct |
| `tests/regression/test_deprecated_code_removed.py` | Tests provider exists (line 112-115) | Correct |

---

## Parallel Execution (pytest-xdist) Risk Assessment

| Risk | Files Affected | Description |
|------|---------------|-------------|
| **Class-scoped fixture + xdist** | `simulation_tests/` | The `isolated_registry` fixture is class-scoped. With xdist, different workers handle different test classes. Since each worker has its own process, cross-worker contamination is not possible. However, within a single worker, if multiple test classes are assigned, the class-scoped fixture could leave stale data between classes. The cleanup at line 110 (`RegistryManager.instance().clear()`) mitigates this. |
| **Singleton per-worker** | All files using singleton | Each xdist worker gets its own process, so singletons are independent per worker. The root conftest's `reset_game_state` runs per-test, providing function-level isolation within each worker. This architecture is sound. |
| **Session-scoped fixtures** | `tests/conftest.py` | `session_registries` loads data once per worker session. Since xdist workers are separate processes, this is safe. |

**Conclusion:** The parallel execution architecture is fundamentally sound due to xdist's process isolation model. The main risks are within a single worker's sequential execution, not across workers.

---

## Top 5 Priority Issues

1. **TI-005 (Critical):** `test_protocols_boundary.py` unit test consumes global state for Ship creation. This is a unit test that should use DI fixtures, not read from the singleton. Simple fix.

2. **TI-001 (Major):** `simulation_tests/conftest.py` `isolated_registry` is class-scoped. If any simulation test mutates registry data, all subsequent tests in the same class see the mutation. Medium effort to fix.

3. **TI-004 (Major):** `simulation_tests/scenarios/base.py` `_load_ship` and `_create_ship_with_components` are hardcoded to use the singleton. All ~40+ simulation scenarios inherit this coupling. Medium effort to add DI parameter.

4. **TI-002 (Major):** `test_engine_physics.py` `_load_ship` helper reads from singleton instead of using fixture-provided data. Medium effort to refactor.

5. **TI-003 (Major):** `test_smoke.py` three methods all independently call `get_default_registry_provider()`. Simple fix to pass from fixture.

---

## Recommendations Summary

### Quick Wins (Simple Effort)
- **TI-005:** Change `simple_ship` fixture in `test_protocols_boundary.py` to use `fresh_registries`
- **TI-003:** Pass registry from `isolated_registry` to test methods in `test_smoke.py`
- **TI-007:** Remove unused `fresh_registries` parameter from `test_design_loader_adapter.py`

### Medium-Term Improvements
- **TI-001:** Add per-method cleanup to `simulation_tests/conftest.py` or change to function scope
- **TI-002/TI-004:** Add optional `registries` parameter to `TestScenario._load_ship()` and `_create_ship_with_components()`
- **TI-006:** Patch `get_default_registry_provider` in workshop context backward-compat tests

### Architectural Note
The codebase is in an excellent transitional state. The DI infrastructure (`IRegistryProvider`, `TestRegistryProvider`, `fresh_registries` fixture) is fully in place. The remaining issues are test files that haven't yet been updated to use the new DI patterns. No new infrastructure is needed -- just incremental adoption of existing patterns.
