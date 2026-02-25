# PROJ-195: Eradicate RegistryManager Singleton from Non-Root Code

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-195` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-195 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Production Code Cleanup | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Entity & UI Test Migration | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 2.5. Ship Internal Singleton Investigation & Fix | Not Started | [phase_2_5_checklist.md](phase_2_5_checklist.md) |
| 3. Data Loader Test Migration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Combat & Modifier Test Migration | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Core Test: Convert Impure Loader Tests to Pure | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Conftest & Infrastructure Migration | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Regression & Repro Test Migration | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Final Audit & Verification | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-02-24 22:05
**Active Phase:** Planning — Awaiting User Approval
**Last Action:** Plan finalized with all user feedback applied (Phase 2.5 added, pure function conversion for portability, count-based regression guard)
**Next Action:** User approval → Implementation begins in new session via "Continue Project"
**Blockers:** None

## Overview
Complete the DI migration by eradicating all `RegistryManager.instance()` calls from non-composition-root code. Previous projects (PROJ-50, PROJ-174, PROJ-181) successfully eliminated TIER 1 and TIER 2 patterns. This project targets the remaining ~126 TIER 3 references (direct singleton access), the vast majority in test code.

## Goals
- Remove all `RegistryManager.instance()` from production code except `game/app.py` (composition root) and `game/core/registry.py` (singleton definition)
- Remove all `RegistryManager.instance()` from tests except those that specifically test the singleton itself
- Establish `fresh_registries` / `minimal_registries` as the standard test pattern
- Ensure 12,718 tests continue to pass

## Scope
**In:**
- `game/simulation/entities/ship_loader.py` — 1 production leak
- `game/simulation/services/registry_loader.py` — 1 docstring fix
- ~20 test files with ~72 direct singleton references
- ~5 conftest.py files with fixture singleton references
- Import cleanup for files no longer needing RegistryManager

**Out:**
- `game/app.py` — Composition root (legitimate usage)
- `game/core/registry.py` — Singleton definition (required)
- `conftest.py` (root) — Test isolation fixture (legitimate)
- `tests/infrastructure/session_cache.py` — Session cache loading (legitimate)
- `tests/unit/core/registry/test_singleton_and_thread.py` — Tests singleton behavior
- `tests/unit/core/registry/test_registry_features.py` — Tests registry features
- `tests/unit/core/registry/conftest.py` — Registry test fixture
- `tests/regression/test_deprecated_code_removed.py` — Regression guards
- `tests/unit/core/test_registry_provider.py` — Tests DefaultRegistryProvider delegation
- `tests/unit/core/test_service_injection.py` — Tests DI isolation
- `tests/unit/core/test_isolation.py` — Tests isolation fixture

## Key Files
| Component | File Path |
|-----------|-----------|
| Singleton Definition | `game/core/registry.py` |
| IRegistryProvider | `game/core/protocols.py` |
| TestRegistryProvider | `game/core/registry.py:292-343` |
| Composition Root | `game/app.py` |
| Root conftest | `conftest.py` |
| DI fixtures | `tests/conftest.py` |
| Production leak | `game/simulation/entities/ship_loader.py:34` |
| Docstring fix | `game/simulation/services/registry_loader.py:13` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Production Code Cleanup [Simple]
**Objective:** Fix the only remaining production code singleton leaks
**Status:** Not Started

#### Task 1.1: Fix ship_loader.py singleton access [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/core/test_registry_manager_reload.py -v`
- [ ] Line 34: Replace `val = RegistryManager.instance().get_validator()` with call to module-level `get_validator()` function from `game.core.registry`
- [ ] Verify `get_validator()` exists in `game/core/registry.py` — if not, create a thin wrapper: `def get_validator(): return RegistryManager.instance().get_validator()`
- [ ] Remove import `from game.core.registry import RegistryManager` on line 18 (if no longer needed)
- [ ] Run tests to verify
**Notes:**

#### Task 1.2: Fix registry_loader.py docstring [Simple]
**File:** `game/simulation/services/registry_loader.py`
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`
- [ ] Lines 11-14: Update the docstring usage example to show the DI pattern instead of `manager = RegistryManager.instance()`
- [ ] Run tests to verify
**Notes:**

---

### Phase 2: Entity & UI Test Migration [Medium]
**Objective:** Migrate test_ship.py and test_ship_factory.py away from singleton hydration pattern
**Status:** Not Started

These tests use a pattern where `fresh_registries` data is copied INTO the singleton via `mgr.hydrate()`. This is backwards — the tests should pass `fresh_registries` directly via DI and not touch the singleton at all.

#### Task 2.1: Migrate test_ship.py TestShip class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -v`
- [ ] Lines 24-30: Remove `setup_and_teardown` singleton hydration — the fixture already receives `fresh_registries` which is passed via DI to Ship constructor. Ship/Component constructors accept `registries=` parameter.
- [ ] Lines 25-30: Delete `mgr = RegistryManager.instance()` and `mgr.hydrate(...)` calls
- [ ] Verify all test methods already pass `registries=fresh_registries` to Ship/Component constructors
- [ ] Remove `from game.core.registry import RegistryManager` import (line 13) if no longer needed
- [ ] Run tests
**Notes:** The Ship constructor and create_component already accept `registries=` parameter. The singleton hydration was a legacy pattern from before strict DI.

#### Task 2.2: Migrate test_ship.py TestShipClassMutation class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py::TestShipClassMutation -v`
- [ ] Lines 154-160: Remove singleton hydration from `setup_and_teardown`
- [ ] Run tests — verify Ship operations work with `fresh_registries` alone
**Notes:**

#### Task 2.3: Migrate test_ship.py TestShipEdgeCases class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py::TestShipEdgeCases -v`
- [ ] Lines 371-376: Remove singleton hydration from `setup_and_teardown`
- [ ] Run tests
**Notes:**

#### Task 2.4: Migrate test_ship.py TestTotalDefenseScoreInitialization class [Medium]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py::TestTotalDefenseScoreInitialization -v`
- [ ] Lines 405-410: Remove singleton hydration from `setup_and_teardown`
- [ ] Run tests
**Notes:**

#### Task 2.5: Migrate test_ship_factory.py [Medium]
**File:** `tests/unit/ui/services/test_ship_factory.py`
**Tests:** `pytest tests/unit/ui/services/test_ship_factory.py -v`
- [ ] Lines 21-26: TestShipFactory.setup — remove `mgr = RegistryManager.instance()` and `mgr.hydrate(...)`
- [ ] Lines 176-181: TestShipFactoryStaticMethods.setup — same removal
- [ ] Lines 214-219: TestSetupFormationEdgeCases.setup — same removal
- [ ] Remove `from game.core.registry import RegistryManager` import (line 11) if no longer needed
- [ ] Run tests
**Notes:** ShipFactory.create_from_design already accepts `registry_provider=fresh_registries` — the singleton hydration is redundant.

#### Task 2.6: Migrate test_builder_ui_sync.py [Medium]
**File:** `tests/unit/builder/test_builder_ui_sync.py`
**Tests:** `pytest tests/unit/builder/test_builder_ui_sync.py -v`
- [ ] Lines 29-35: Remove `mgr = RegistryManager.instance()` and `mgr.hydrate(...)` from `setup_ui`
- [ ] Line 108: Replace `classes = RegistryManager.instance().vehicle_classes` with `classes = fresh_registries.vehicle_classes`
- [ ] Line 151: Replace `for name, data in RegistryManager.instance().vehicle_classes.items()` with `fresh_registries.vehicle_classes.items()`
- [ ] Line 195: Replace `c_def = RegistryManager.instance().vehicle_classes.get(opt_val)` with `fresh_registries.vehicle_classes.get(opt_val)`
- [ ] Store `fresh_registries` as `self.registries` in setup for method access
- [ ] Remove `from game.core.registry import RegistryManager` import (line 12)
- [ ] Run tests
**Notes:** This test uses `fresh_registries` in setup but then reads data from singleton. Need to switch reads to use the fixture.

---

### Phase 2.5: Ship Internal Singleton Investigation & Fix [Medium]
**Objective:** Investigate and fix any Ship/Component internal methods that read from the global singleton, then fix all tests broken by Phase 2 removals
**Status:** Not Started

This phase handles the risk that internal Ship methods (`change_class()`, `_initialize_layers()`, `recalculate_stats()`, etc.) may still access `RegistryManager.instance()` under the hood, causing test failures when we remove the singleton hydration in Phase 2.

#### Task 2.5.1: Investigate Ship internal singleton access [Medium]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/components/component.py`
**Tests:** N/A — investigation only
- [ ] Search `game/simulation/entities/ship.py` for any `RegistryManager.instance()` or `get_default_registry_provider()` calls
- [ ] Search `game/simulation/components/component.py` for same
- [ ] Search `game/simulation/services/` for any service that Ship calls internally
- [ ] Document all internal singleton access points found
- [ ] For each access point, determine: does the code have a `registries=` parameter it could use instead?
**Notes:** If internal methods read from the singleton, we need to fix them to use the `registries` that was passed to the Ship constructor.

#### Task 2.5.2: Fix internal singleton access in production code [Medium]
**Files:** As identified in Task 2.5.1
**Tests:** `pytest tests/ --testmon`
- [ ] For each internal access point found, refactor to use the `registries` attribute stored on the Ship/Component instance
- [ ] Ensure no new singleton leaks are introduced
- [ ] Run tests after each fix
**Notes:** This may be empty if no internal access is found. The autouse `reset_game_state` fixture hydrates the singleton, so internal singleton reads may have been silently working.

#### Task 2.5.3: Fix all broken tests from Phase 2 [Medium]
**Tests:** `pytest tests/unit/entities/ tests/unit/ui/services/ tests/unit/builder/test_builder_ui_sync.py -v`
- [ ] Run the full test suite for Phase 2 files
- [ ] For each failure, diagnose root cause (internal singleton access vs missing DI parameter vs other)
- [ ] Fix each failure — prefer fixing the production code to propagate `registries` rather than re-adding singleton hydration
- [ ] All Phase 2 tests green
**Notes:**

---

### Phase 3: Data Loader Test Migration [Medium]
**Objective:** Migrate BuilderDataLoader and WorkshopDataLoader tests
**Status:** Not Started

These tests pass `registries=RegistryManager.instance()` to constructors. Replace with `fresh_registries`.

#### Task 3.1: Migrate test_builder_data_loader.py [Medium]
**File:** `tests/unit/builder/test_builder_data_loader.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`
- [ ] Add `fresh_registries` parameter to TestBuilderDataLoader class fixture or each test method
- [ ] Lines 60-61, 74-75, 88-89, 102-103, 114-115: Replace `registries=RegistryManager.instance()` with `registries=fresh_registries`
- [ ] Lines 127, 130: Replace `RegistryManager.instance()` in `test_clear_registries_clears_registry_manager` — this test uses `patch.object(RegistryManager.instance(), 'clear')`. Restructure to mock the registries object's clear method instead, or accept this test specifically validates singleton behavior and keep
- [ ] Lines 155, 172: Replace `registries=RegistryManager.instance()` in integration tests
- [ ] Remove `from game.core.registry import RegistryManager` import (line 14)
- [ ] Run tests
**Notes:** The `test_clear_registries_clears_registry_manager` test needs special handling — it's testing that the loader calls `RegistryManager.clear()`. This may be a legitimate singleton test or may need restructuring.

#### Task 3.2: Migrate test_workshop_data_loader.py [Medium]
**File:** `tests/unit/workshop/test_workshop_data_loader.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_data_loader.py -v`
- [ ] Add `fresh_registries` parameter to `data_loader_setup` fixture or each test
- [ ] Lines 62, 77, 92, 107, 120: Replace `registries=RegistryManager.instance()` with `registries=fresh_registries`
- [ ] Lines 133, 136: Same `patch.object` situation as builder — handle the `test_clear_registries_clears_registry_manager` test
- [ ] Lines 166, 184: Replace in integration tests
- [ ] Remove `from game.core.registry import RegistryManager` import (line 13)
- [ ] Run tests
**Notes:**

---

### Phase 4: Combat & Modifier Test Migration [Medium]
**Objective:** Migrate combat, modifier, and performance tests
**Status:** Not Started

#### Task 4.1: Migrate test_combat.py [Medium]
**File:** `tests/unit/combat/test_combat.py`
**Tests:** `pytest tests/unit/combat/test_combat.py -v`
- [ ] Lines 30-37: Replace `RegistryManager.instance().vehicle_classes["TestShip"] = {...}` with `fresh_registries.vehicle_classes["TestShip"] = {...}` (fixture already stores `self.registries = fresh_registries`)
- [ ] Lines 106-113: Same pattern in `test_bridge_destruction_kills_ship` — replace with `self.registries.vehicle_classes["TestShip"] = {...}`
- [ ] Remove `from game.core.registry import RegistryManager` import (line 30)
- [ ] Run tests
**Notes:** These tests add a "TestShip" vehicle class definition for testing. The data should go into `fresh_registries` not the singleton.

#### Task 4.2: Migrate test_formula_validation.py [Simple]
**File:** `tests/unit/modifiers/test_formula_validation.py`
**Tests:** `pytest tests/unit/modifiers/test_formula_validation.py -v`
- [ ] Lines 72-75: In `test_validate_all_modifiers_on_load`, replace `modifier_registry = RegistryManager.instance().modifiers` with using `fresh_registries.modifiers` (which is already hydrated by the autouse fixture)
- [ ] Add `fresh_registries` parameter to the test method
- [ ] Remove `from game.core.registry import RegistryManager` import (line 72 local import)
- [ ] Run tests
**Notes:** The test calls `load_modifiers()` which populates the singleton, then reads from singleton. Should read from `fresh_registries` instead since autouse fixture already hydrated it.

#### Task 4.3: Convert test_modifier_loader_v2.py to pure function [Simple]
**File:** `tests/unit/modifiers/test_modifier_loader_v2.py`
**Tests:** `pytest tests/unit/modifiers/test_modifier_loader_v2.py -v`
- [ ] Lines 95-98: Convert `test_load_modifiers_file` from impure `load_modifiers()` + singleton read to pure `load_modifiers_data()` + return value assertions
- [ ] Replace `reg = RegistryManager.instance().modifiers` / `reg.clear()` / `load_modifiers(...)` with `result = load_modifiers_data('data/modifiers.json')` and assert on `result`
- [ ] Remove `from game.core.registry import RegistryManager` import
- [ ] Run tests
**Notes:** Converting to pure functions improves portability to C#/C++/Rust where global singletons are not idiomatic.

#### Task 4.4: Migrate reproduce_scaling.py [Simple]
**File:** `tests/unit/performance/reproduce_scaling.py`
**Tests:** `pytest tests/unit/performance/reproduce_scaling.py -v`
- [ ] Lines 27, 45: Replace `registries=RegistryManager.instance()` with `registries=fresh_registries` (add fixture parameter)
- [ ] Add `fresh_registries` parameter to the test methods
- [ ] Remove `from game.core.registry import RegistryManager` import (line 6)
- [ ] Run tests
**Notes:**

---

### Phase 5: Core Test: Convert Impure Loader Tests to Pure [Medium]
**Objective:** Convert backward-compatibility loader tests from impure singleton tests to pure function tests. Keep "does not modify registry" tests as legitimate singleton guards.
**Status:** Not Started

For portability to C#/C++/Rust: the impure `load_components()`/`load_modifiers()` wrappers that populate a global singleton are Python-specific. Tests should validate the pure functions (`load_components_data()`, `load_modifiers_data()`) instead, which return data without side effects.

#### Task 5.1: Convert test_pure_loaders.py backward-compat tests [Medium]
**File:** `tests/unit/core/test_pure_loaders.py`
**Tests:** `pytest tests/unit/core/test_pure_loaders.py -v`
- [ ] Lines 55-59, 124-127, 189-192, 268-271: "does not modify registry" tests — **Keep as-is** (these are regression guards ensuring pure functions stay pure)
- [ ] Lines 328-339: `test_load_components_populates_registry` — Convert to test `load_components_data()` return value. Replace `registry = RegistryManager.instance().components` / `load_components(...)` / `assert len(registry) > 0` with `result = load_components_data(...)` / `assert len(result) > 0` / `assert "bridge" in result`
- [ ] Lines 343-355: `test_load_modifiers_populates_registry` — Same conversion using `load_modifiers_data()`
- [ ] Remove the `TestBackwardCompatibility` class name or rename to `TestLoaderPureFunctions`
- [ ] Run tests
**Notes:** The "does not modify registry" tests are the canonical guards that pure functions stay side-effect free — keep them. The "populates registry" tests are what we convert to pure.

#### Task 5.2: Migrate test_registry_manager_reload.py [Simple]
**File:** `tests/unit/core/test_registry_manager_reload.py`
**Tests:** `pytest tests/unit/core/test_registry_manager_reload.py -v`
- [ ] Line 27: `reg = RegistryManager.instance()` in `fresh_registry` fixture — This is a **legitimate singleton test** (testing `reload_registries_from_directory` which operates on the singleton). **Keep.**
- [ ] Add comment: `# PROJ-195: Legitimate — testing reload function that operates on singleton`
- [ ] Run tests
**Notes:**

---

### Phase 6: Conftest & Infrastructure Migration [Medium]
**Objective:** Migrate conftest.py files with singleton fixtures to use DI patterns
**Status:** Not Started

#### Task 6.1: Migrate tests/unit/strategy/conftest.py [Medium]
**File:** `tests/unit/strategy/conftest.py`
**Tests:** `pytest tests/unit/strategy/ -v`
- [ ] Lines 14-20: `reset_resource_registry` fixture — Replace `registry = RegistryManager.instance()` with `registry = RegistryManager.instance()` ... Actually this fixture clears `registry.resources` which is a global cleanup fixture. It operates on the singleton for isolation purposes. **Decision: Keep — this is a test isolation fixture similar to root conftest's `reset_game_state`**
- [ ] Lines 44-47: `custom_resource_registry` fixture — Replace `registry = RegistryManager.instance()` and `registry.resources.update(...)`. This loads custom resources into the singleton. Should use `fresh_registries` instead.
- [ ] Update `custom_resource_registry` to accept `fresh_registries` and populate `fresh_registries.resources` instead of singleton
- [ ] Verify all tests in `tests/unit/strategy/` that use `custom_resource_registry` work with the new pattern
- [ ] Remove `from game.core.registry import RegistryManager` import if no longer needed
- [ ] Run tests
**Notes:** Some strategy tests may depend on data being in the singleton vs fresh_registries. Need careful testing.

#### Task 6.2: Migrate tests/unit/core/resources_registry/conftest.py [Medium]
**File:** `tests/unit/core/resources_registry/conftest.py`
**Tests:** `pytest tests/unit/core/resources_registry/ -v`
- [ ] Lines 10-19: `clean_registry` fixture — This is an autouse fixture that clears and restores resources on the singleton. It's a **test isolation fixture** for resource registry tests. These tests specifically test the resource registry on the singleton.
- [ ] **Decision: Keep** — resource registry tests need singleton access to test the registry behavior.
- [ ] Add comment: `# PROJ-195: Legitimate — isolation fixture for singleton resource registry tests`
- [ ] Run tests
**Notes:**

#### Task 6.3: Migrate tests/integration/resource_system/conftest.py [Simple]
**File:** `tests/integration/resource_system/conftest.py`
**Tests:** `pytest tests/integration/resource_system/ -v`
- [ ] Lines 13-22: `loaded_registry` fixture returns `RegistryManager.instance()`. Replace with returning `fresh_registries` fixture or returning the singleton wrapped in explanation comment.
- [ ] Check all tests using `loaded_registry` — determine if they need the singleton or just need registry data
- [ ] If tests operate on loaded data: switch to `fresh_registries`
- [ ] If tests specifically test singleton loading: keep with comment
- [ ] Run tests
**Notes:**

#### Task 6.4: Migrate test_resource_pipeline.py [Simple]
**File:** `tests/integration/resource_system/test_resource_pipeline.py`
**Tests:** `pytest tests/integration/resource_system/test_resource_pipeline.py -v`
- [ ] Line 43: Replace `RegistryManager.instance().resources.update(...)` with `loaded_registry.resources.update(...)` (uses the `loaded_registry` fixture)
- [ ] Remove `from game.core.registry import RegistryManager` import (line 11)
- [ ] Run tests
**Notes:** This file uses both `loaded_registry` fixture and direct `RegistryManager.instance()`. The fixture already provides the registry.

---

### Phase 7: Regression & Repro Test Migration [Medium]
**Objective:** Migrate remaining regression and bug repro tests
**Status:** Not Started

#### Task 7.1: Migrate test_regressions.py [Medium]
**File:** `tests/unit/regressions/test_regressions.py`
**Tests:** `pytest tests/unit/regressions/test_regressions.py -v`
- [ ] Lines 36, 43, 45, 48: `test_ship_classes_update_in_place` — This test validates that `load_vehicle_classes` updates the singleton dict in-place (preserving reference identity). This is a **legitimate singleton test** — it's testing loader behavior on the singleton.
- [ ] **Decision: Keep** — add comment: `# PROJ-195: Legitimate — testing singleton dict identity preservation`
- [ ] Run tests
**Notes:**

#### Task 7.2: Migrate test_warnings.py [Simple]
**File:** `tests/unit/regressions/test_warnings.py`
**Tests:** `pytest tests/unit/regressions/test_warnings.py -v`
- [ ] Lines 16-17: Replace `RegistryManager.instance().vehicle_classes` access in `ship_with_registry` fixture with `fresh_registries.vehicle_classes`
- [ ] The fixture already receives `fresh_registries` — just use it directly
- [ ] Remove `from game.core.registry import RegistryManager` import (line 6) if no longer needed
- [ ] Run tests
**Notes:**

#### Task 7.3: Migrate test_bug_13_clear_removes_hull.py [Medium]
**File:** `tests/repro_issues/test_bug_13_clear_removes_hull.py`
**Tests:** `pytest tests/repro_issues/test_bug_13_clear_removes_hull.py -v`
- [ ] Lines 44-47: `simple_ship_registry` fixture — Replace `registry = RegistryManager.instance()` / `registry.vehicle_classes.update(classes)` / `registry.components[comp_id] = ...` with using `fresh_registries` directly
- [ ] Line 72: Replace `RegistryManager.instance().components.items()` with `fresh_registries.components`
- [ ] Remove `RegistryManager` from import on line 12 (keep `GameRegistries`)
- [ ] Run tests
**Notes:** The fixture creates a custom GameRegistries with test data. The singleton access is redundant since it already constructs registries explicitly.

---

### Phase 8: Final Audit & Verification [Simple]
**Objective:** Verify all singleton references are accounted for, run full suite
**Status:** Not Started

#### Task 8.1: Audit remaining references [Simple]
**Tests:** N/A — audit only
- [ ] Run `grep -rn "RegistryManager.instance()" game/ tests/ --include="*.py"` and verify every remaining reference is either:
  - In `game/app.py` (composition root)
  - In `game/core/registry.py` (singleton definition)
  - In `conftest.py` (root) or `tests/infrastructure/session_cache.py` (test infrastructure)
  - In `tests/unit/core/registry/` (singleton-specific tests)
  - In explicitly documented legitimate usages
- [ ] Document any remaining references with justification

#### Task 8.2: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12,718 tests pass
- [ ] No new warnings introduced
- [ ] No test isolation failures

#### Task 8.3: Create regression guard [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py -v`
- [ ] Add a new test class `TestSingletonUsageCount` with a test that counts `RegistryManager.instance()` references in `game/` and `tests/`
- [ ] Store the expected count as a constant (determined from Task 8.1 audit)
- [ ] Test asserts `actual_count <= EXPECTED_COUNT` — fails if count increases
- [ ] Include a clear failure message: "RegistryManager.instance() count increased from {expected} to {actual}. If this is legitimate, update the expected count."
- [ ] Run tests to verify guard works

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — **12,718 passed, 1 skipped** (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Verify no new `RegistryManager.instance()` references introduced

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Grep audit shows only legitimate singleton references remain
- [ ] Regression guard test passes

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 2.5 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All Phase 7 tasks checked off
- [ ] All Phase 8 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
