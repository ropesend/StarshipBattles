# Agent 7: Remaining Unit Dirs + Integration Tests Analysis

## Summary
- Files analyzed: 131 (41 unit test files across 14 dirs + 90 integration test files + root-level files)
- Removal candidates found: 12
- HIGH confidence: 7
- MEDIUM confidence: 3
- LOW confidence: 2

---

## HIGH Confidence Removal Candidates

### 1. tests/trace_cargo.py
- **Location:** `tests/trace_cargo.py`
- **Lines:** ~52
- **Category:** Debugging script (not a test)
- **Reason:** Not actually a test file - it's a diagnostic tracing script that reads JSON files and prints cargo storage info. No test functions or assertions. Contains hardcoded relative file paths. Should not be in the test tree at all.

### 2. tests/repro_colonize_population.py
- **Location:** `tests/repro_colonize_population.py`
- **Lines:** ~47
- **Category:** Scaffold/repro test
- **Reason:** Reproduction test using `unittest.TestCase` with `__main__` guard. Tests `FleetOrderProcessor._transfer_founding_population` with mocks and `print()` diagnostics. Temporary repro test. The colonization logic is already tested thoroughly in `tests/integration/colonization/` (5 files, covering execution, validation, edge cases, explicit orders, and planet-specific colonization).

### 3. tests/repro_facade_colonies.py
- **Location:** `tests/repro_facade_colonies.py`
- **Lines:** ~93
- **Category:** Scaffold/repro test
- **Reason:** Reproduction test for `StrategySessionFacade.get_planets_at_hex` using `unittest.TestCase` with `__main__` guard. The facade planet queries are already covered by `tests/integration/strategy/facade/test_system_queries.py` and `test_validation_queries.py`. This is a temporary diagnostic test.

### 4. tests/repro_load_cargo_bug.py
- **Location:** `tests/repro_load_cargo_bug.py`
- **Lines:** ~244
- **Category:** Scaffold/repro test
- **Reason:** Large diagnostic reproduction test for "load cargo order not appearing" bug. Contains extensive `print()` diagnostic output throughout all 6 test methods. Tests `TransferCommandHandler` and `TransferValidator` with diagnostic focus rather than assertive testing. The transfer/cargo logic is covered by proper tests in `tests/integration/resource_system/test_fleet_operations.py` and the unit-level transfer validator tests. Git status shows this is an untracked file (freshly created), which further suggests it's a temporary diagnostic.

### 5. tests/repro_warp_bug.py
- **Location:** `tests/repro_warp_bug.py`
- **Lines:** ~78
- **Category:** Scaffold/repro test
- **Reason:** Reproduction test for warp point creation failure. Contains `__main__` guard with typo (`AssertionError` instead of `AssertionError`). Has `print()` diagnostics. Test structure is informal. The warp logic is covered by `tests/integration/strategy/test_warp_logic_rework.py` and `tests/integration/strategy/test_superweapon_integration.py`.

### 6. tests/unit/performance/generate_test_data.py
- **Location:** `tests/unit/performance/generate_test_data.py`
- **Lines:** ~99
- **Category:** Standalone script (not a test)
- **Reason:** A standalone script for generating test ship design JSON files (not a pytest test). Has `__main__` guard, uses `print()` statements, no test functions. This is a data generation utility that should live in a scripts directory, not the test tree.

### 7. tests/unit/performance/profile_simulation.py, stress_test.py, strategy_tournament.py, reproduce_scaling.py
- **Location:** `tests/unit/performance/profile_simulation.py` (~210 lines), `tests/unit/performance/stress_test.py` (~137 lines), `tests/unit/performance/strategy_tournament.py` (~263 lines), `tests/unit/performance/reproduce_scaling.py` (~61 lines)
- **Lines:** ~671 total
- **Category:** Standalone profiling/stress scripts (not pytest tests)
- **Reason:** All four files are standalone scripts with `__main__` guards and `cProfile` profiling, not pytest tests. They use `print()` extensively, create pygame displays, and are designed to be run manually. They will never be collected by pytest. These are developer tools, not tests, and should be in a `tools/` or `scripts/` directory if kept at all.

---

## MEDIUM Confidence Removal Candidates

### 8. tests/unit/regressions/test_crash_regressions.py
- **Location:** `tests/unit/regressions/test_crash_regressions.py`
- **Lines:** ~114
- **Category:** Regression test (fragile/incomplete)
- **Reason:** Tests WeaponsReportPanel crash on zero-range weapons. The test methodology is weak: it catches broad `Exception` and only fails on `UnboundLocalError`, meaning the test passes even if the draw method raises `AttributeError`, `TypeError`, or any other exception. Lines 79-86 contain commented-out assertions that were never completed. The test provides very limited value as it only verifies one specific exception type doesn't occur.

### 9. tests/unit/components/test_component_health_manager.py (potential duplicate)
- **Location:** `tests/unit/components/test_component_health_manager.py`
- **Lines:** ~144
- **Category:** Duplicate tests
- **Reason:** This file tests `ComponentHealthManager` with take_damage, reset_hp, and hp_ratio. `tests/unit/components/test_component_health_edge_cases.py` (~162 lines) tests the exact same class with the exact same methods including many overlapping scenarios (damage to zero, overkill, partial damage, hp_ratio caching, zero max_hp, reset_hp). The two files should be consolidated. The edge_cases file is slightly more thorough, but both use nearly identical mock setups and test the same code paths.

### 10. tests/unit/fixtures/test_paths.py (low value)
- **Location:** `tests/unit/fixtures/test_paths.py`
- **Lines:** ~114
- **Category:** Trivially obvious tests
- **Reason:** Tests that `get_project_root()` returns a Path, that the directory exists, that it contains `game/` and `data/` directories. Also tests `get_data_dir()` and `get_assets_dir()` in the same trivial fashion ("returns a Path", "directory exists", "contains components.json"). These tests verify that the project's directory structure exists, which is a given for any test run. If the project root or data dir didn't exist, no other test would pass either. The 15 tests in this file add noise without catching real bugs.

---

## LOW Confidence Removal Candidates

### 11. tests/unit/repro_issues/test_slider_increment.py (mislocated)
- **Location:** `tests/unit/repro_issues/test_slider_increment.py`
- **Lines:** ~105
- **Category:** Mislocated test
- **Reason:** While in the `repro_issues` folder, this test has been updated across multiple projects (PROJ-43, PROJ-129) and tests real ModifierControlRow slider behavior. It is a legitimate test but lives in the wrong directory. Consider relocating to `tests/unit/workshop/` rather than removing.

### 12. tests/unit/fixtures/ (fixture validation tests - debatable value)
- **Location:** `tests/unit/fixtures/test_battle_fixtures.py` (~143 lines), `tests/unit/fixtures/test_component_fixtures.py` (~115 lines), `tests/unit/fixtures/test_ship_fixtures.py` (~196 lines)
- **Lines:** ~454 total
- **Category:** Meta-tests (tests for test fixtures)
- **Reason:** These are "tests for test infrastructure" - they verify that fixtures like `empty_ship`, `basic_ship`, `weapon_component`, `battle_engine` return proper objects with expected attributes. While having self-testing fixtures provides confidence, many of these checks are trivially obvious (e.g., `test_returns_ship_object(self, empty_ship): assert isinstance(empty_ship, Ship)`). If a fixture broke, the hundreds of tests that use it would also fail, making these meta-tests somewhat redundant. However, they do serve as documentation of what each fixture provides, so this is debatable.

---

## Directories Analyzed - No Issues Found

### tests/unit/performance/test_profiler_perf.py
- **Lines:** ~176
- **Status:** KEEP - Legitimate tests for Profiler singleton, toggling, recording, context manager, decorator, and save_history. Well-structured with proper fixtures.

### tests/unit/assets/test_asset_manager_resolutions.py
- **Lines:** ~164
- **Status:** KEEP - Legitimate tests for AssetManager planet image resolution selection. Tests folder mapping, fallback chain, caching. Real functionality being tested.

### tests/unit/validation/test_component_definitions.py
- **Lines:** ~108
- **Status:** KEEP - Data-driven validation tests for components.json. Parametrized over all components. Validates IDs, required fields, metrics, types, resource costs, abilities format.

### tests/unit/components/test_component_health_edge_cases.py
- **Lines:** ~162
- **Status:** KEEP (but see item #9 above about consolidation with test_component_health_manager.py)

### tests/unit/components/test_component_resource_manager.py
- **Lines:** ~201
- **Status:** KEEP - Solid tests for ComponentResourceManager with activation, resource consumption, formula evaluation.

### tests/unit/components/test_resource_costs.py
- **Lines:** ~80
- **Status:** KEEP - Data validation tests for resource costs in components.json plus modifier cost scaling.

### tests/unit/workshop/ (3 files)
- **Lines:** ~671 total
- **Status:** KEEP - All three files test real WorkshopContext, WorkshopDataLoader, and WorkshopViewModel. Well-structured with proper fixtures. PROJ-40/50 updated.

### tests/unit/quickstart/ (3 files)
- **Lines:** ~791 total
- **Status:** KEEP - All three files test QuickstartBuilder, quickstart design fixtures, and quickstart race fixtures. Comprehensive parametrized tests with real data validation.

### tests/unit/test_lab/ (3 files)
- **Lines:** ~814 total
- **Status:** KEEP - Tests for Combat Lab data path construction, propulsion metrics display, and visual run flow. All test real code paths with proper mocking.

### tests/unit/abilities/ (4 files)
- **Lines:** ~850 total
- **Status:** KEEP - Tests for AbilityLayer/AbilityScope enums, ColonizePlanet, StrategicMovement, and WarpJump abilities. Thorough TDD tests with proper registration checks.

### tests/unit/simulation_tests/ (3 files + scenarios/)
- **Lines:** ~1200 total
- **Status:** KEEP - Tests for PropulsionScenario results storage, resource scenario metadata, and TestMetadata end conditions. All test real framework classes.

### tests/unit/services/ (6 files)
- **Lines:** ~1300 total
- **Status:** KEEP - Tests for BattleService, ModifierService, VehicleDesignService, ShipStatsCalculator including DI variants. All test real service classes with proper fixtures.

### tests/unit/test_framework/ (7 files in services/ + 1 registry file)
- **Lines:** ~2400 total
- **Status:** KEEP - Tests for test framework registry, controller execution, controller events, metadata management, scenario data, test execution, and UI state services. All test real test framework infrastructure.

### tests/unit/regressions/test_bug_regressions_2026_01.py
- **Lines:** ~114
- **Status:** KEEP - Tests 3 specific bug fixes with real objects.

### tests/unit/regressions/test_regressions.py
- **Lines:** ~93
- **Status:** KEEP - Tests ship class reference stability, theme fallbacks, theme persistence.

### tests/unit/regressions/test_warnings.py
- **Lines:** ~119
- **Status:** KEEP - Tests fuel/ammo/energy validation warnings.

### tests/integration/ (90 files)
- **Lines:** ~24,000 total
- **Status:** KEEP (all) - All 90 integration test files were scanned for skip/xfail markers (none found), dead imports, and obvious duplication patterns. The integration tests are well-organized into subdirectories by feature area (ai_strategy, colonization, fleet_combat, gameplay_loop, quickstart, research_workflow, resource_system, save_load, strategy, ui). No skipped/xfail tests were found across the entire integration test suite. The root-level integration files (`test_formation_attack.py`, `test_formation_flight.py`, `test_complex_workflow.py`, `test_strategic_abilities.py`) are all legitimate integration tests that were properly converted from script format (PROJ-48) and updated for DI (PROJ-50).

---

## Summary Table

| # | File(s) | Lines | Confidence | Category |
|---|---------|-------|------------|----------|
| 1 | `tests/trace_cargo.py` | 52 | HIGH | Debugging script |
| 2 | `tests/repro_colonize_population.py` | 47 | HIGH | Repro test |
| 3 | `tests/repro_facade_colonies.py` | 93 | HIGH | Repro test |
| 4 | `tests/repro_load_cargo_bug.py` | 244 | HIGH | Repro test |
| 5 | `tests/repro_warp_bug.py` | 78 | HIGH | Repro test |
| 6 | `tests/unit/performance/generate_test_data.py` | 99 | HIGH | Script (not test) |
| 7 | `tests/unit/performance/{profile_simulation,stress_test,strategy_tournament,reproduce_scaling}.py` | 671 | HIGH | Scripts (not tests) |
| 8 | `tests/unit/regressions/test_crash_regressions.py` | 114 | MEDIUM | Fragile test |
| 9 | `tests/unit/components/test_component_health_manager.py` | 144 | MEDIUM | Duplicate |
| 10 | `tests/unit/fixtures/test_paths.py` | 114 | MEDIUM | Trivially obvious |
| 11 | `tests/unit/repro_issues/test_slider_increment.py` | 105 | LOW | Mislocated |
| 12 | `tests/unit/fixtures/test_{battle,component,ship}_fixtures.py` | 454 | LOW | Meta-tests |

**Total removable lines (HIGH confidence):** ~1,284
**Total removable lines (HIGH + MEDIUM):** ~1,656
**Total removable lines (all):** ~2,215
