# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 8
- **Confirmed:** 3
- **Downgraded:** 4
- **Rejected:** 1
- **Rejection Rate:** 12.5%

## Verdicts

#### Finding: TI-001
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The `isolated_registry` fixture at `simulation_tests/conftest.py:75` is indeed class-scoped, meaning all test methods in a class share the same registry state. However, this is intentional design for the simulation test infrastructure: the fixture clears registries, loads test data, yields, then cleans up. The test methods within a class are expected to share the same loaded test data and none of them mutate the registry -- they only read from it to load ships. The class scope avoids redundant data loading per method. State leakage is only a concern if a test mutates the registry, which none of the simulation tests do. This is a design choice, not a defect. Downgraded because while class scope is technically less isolated than function scope, it is deliberate and safe given the read-only usage pattern.

#### Finding: TI-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Info)
**Reason:** The `_load_ship` helper in `test_engine_physics.py:27-41` calls `get_default_registry_provider()` directly. However, this is the intended pattern post-PROJ-181: `DefaultRegistryProvider` delegates to `RegistryManager.instance()`, and the `isolated_registry` fixture (used via the `setup` autouse fixture at line 22-25) populates that singleton before tests run. The helper reads from the properly-hydrated singleton, which is exactly how the system is designed to work. This is not consuming "global state" in a harmful way -- it is reading from the registry that the isolation fixture explicitly set up.

#### Finding: TI-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Info)
**Reason:** The three test methods in `test_smoke.py:19-58` call `get_default_registry_provider()` in their test bodies, but the class has an autouse `setup` fixture (line 14-17) that requests `isolated_registry`, ensuring the singleton is properly hydrated. These tests are specifically smoke tests validating that the test infrastructure works -- they intentionally verify that `get_default_registry_provider()` returns properly loaded data. Calling the provider directly is the entire point of these tests.

#### Finding: TI-004
**Original Severity:** Major
**Verdict:** DOWNGRADED(Info)
**Reason:** The `_load_ship` method in `scenarios/base.py:356-368` calls `RegistryManager.instance()` (only for a debug log of frozen state) and `get_default_registry_provider()` to build `GameRegistries`. This is the canonical post-PROJ-181 pattern. When scenarios run under pytest, the `isolated_registry` fixture ensures the singleton is properly hydrated before `_load_ship` is called. When scenarios run in Combat Lab (visual mode), the application has already loaded production data into the singleton. The code explicitly follows the PROJ-181 provider pattern and is not a defect.

#### Finding: TI-005
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** The `simple_ship` fixture in `test_protocols_boundary.py:23-44` calls `get_default_registry_provider()` directly without requesting `fresh_registries`. However, this test file lives under `tests/unit/core/` where the root `conftest.py`'s `reset_game_state` autouse fixture runs for every test, which hydrates the `RegistryManager` singleton before each test. So `get_default_registry_provider()` will return valid data. The real issue is that it bypasses the DI-preferred `fresh_registries` pattern, coupling the test to the singleton rather than using an isolated copy. This is a genuine DI inconsistency, though the tests do work correctly due to the autouse fixture. Severity is appropriate as a consistency concern rather than a correctness bug; keeping it confirmed because the fixture genuinely should use `fresh_registries` for proper DI hygiene.

#### Finding: TI-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Tests at lines 53-72, 92-97, 110-118, and 128-145 in `test_workshop_context_di.py` deliberately test the fallback behavior where `WorkshopContext` is created without explicit registries, relying on `get_default_registry_provider()` to provide data from the hydrated singleton. These tests are intentionally validating backward-compatible fallback behavior. While they do rely on the singleton being hydrated (via the root conftest's `reset_game_state` autouse fixture), they are testing a legitimate code path. The Minor severity is appropriate -- these tests work correctly but represent a dependency on singleton state rather than explicit DI.

#### Finding: TI-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** In `test_design_loader_adapter.py:80`, the test method `test_adapter_uses_real_loader_when_none_provided` declares `fresh_registries` as a parameter but never references it in the test body. The fixture is requested solely for its side effect of ensuring registries are available. While this works (the fixture runs and hydrates the test environment), the parameter appears unused, which is confusing. The `fresh_registries` fixture provides an isolated `GameRegistries` object, but the test ignores it and relies on the singleton being hydrated (which is done by the root conftest's `reset_game_state` autouse fixture anyway). The fixture parameter is effectively a no-op. Minor severity is appropriate.

#### Finding: TI-008
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The `reset_resource_registry` fixture in `tests/unit/strategy/conftest.py:14-23` calls `RegistryManager.instance().resources.clear()` as a deliberate test isolation fixture. It clears the resource registry before and after each test that uses it, which is the standard cleanup pattern for singleton-backed state. The fixture even has a comment referencing `PROJ-195: Legitimate -- test isolation fixture that clears singleton`. This is not "mutating singleton directly" as a bug -- it is a purpose-built isolation fixture doing exactly what it should. The `custom_resource_registry` fixture (line 38) properly chains through `fresh_registries` and `reset_resource_registry` to provide full isolation. This is correct, intentional test infrastructure.
