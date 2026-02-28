# Validation Review 4: Remaining/Integration + Cross-Cutting Findings

## Summary
- Findings reviewed: 25+ distinct claims across both files
- CONFIRMED for removal: 11
- DISPUTED (should keep): 10
- MODIFIED (partial removal only): 4

## Key Disagreements with Original Reviewers

The original reviewers had two major blind spots:

1. **Repro tests ARE collected by pytest.** Agent 7 recommended removing 4 root-level repro tests as "scaffold/repro tests" but failed to note that `unittest.TestCase` subclasses and `test_`-prefixed functions ARE collected by pytest. More critically, the claimed replacement tests do NOT cover the same bug scenarios.

2. **The "12,766 lines of old directories" claim is misleading.** While the new files are larger, the old files use real game objects (integration-style) while new files use MagicMock (unit-style). These test different code paths and are complementary, not redundant. Blanket deletion would lose integration coverage.

---

## Agent 7 Findings: Detailed Validation

### Finding #1: tests/trace_cargo.py
- **Original claim:** Debugging script, not a test, no test functions
- **Verdict:** CONFIRMED
- **Evidence:** File contains no `test_` prefixed functions, no assertions, no test classes. Pure diagnostic tracing script that reads JSON and prints cargo info.
- **Unique tests that would be lost:** None
- **Risk of removal:** None

### Finding #2: tests/repro_colonize_population.py
- **Original claim:** Repro test, colonization logic covered by integration tests
- **Verdict:** DISPUTED - KEEP
- **Evidence:** This file IS collected by pytest (it's a `unittest.TestCase` subclass: `TestColonizePopulation`). It tests `FleetOrderProcessor._transfer_founding_population()` with zero passengers. The claimed replacements in `tests/integration/colonization/` do NOT test `_transfer_founding_population` directly — they test higher-level colonization outcomes (ownership transfer, fleet consumption). No integration test verifies that zero passengers yields zero population.
- **Unique tests that would be lost:** `test_colonize_with_zero_passengers_yields_zero_pop` — direct unit test of founding population transfer with edge case (0 passengers)
- **Risk of removal:** Medium — specific bug scenario coverage lost

### Finding #3: tests/repro_facade_colonies.py
- **Original claim:** Repro test, facade queries covered by integration tests
- **Verdict:** DISPUTED - KEEP
- **Evidence:** This file IS collected by pytest (`TestFacadeColonyRetrieval(unittest.TestCase)` with 2 test methods). It tests `get_planets_at_hex` specifically for the offset-planet scenario: planet at `HexCoord(1, -1)` from system center. The claimed replacement `test_system_queries.py` tests multiple planets at offsets but does NOT explicitly test the critical boundary case of "clicking at system center returns nothing when planet is at offset."
- **Unique tests that would be lost:** `test_get_planets_at_hex_offset_planet` — the specific center-vs-offset planet click differentiation bug
- **Risk of removal:** Medium — edge case that caused the original bug not explicitly covered elsewhere

### Finding #4: tests/repro_load_cargo_bug.py
- **Original claim:** Diagnostic repro test, transfer/cargo logic covered by proper tests
- **Verdict:** DISPUTED - KEEP
- **Evidence:** This file IS collected by pytest (`TestReproLoadCargoBug(unittest.TestCase)` with 6 test methods). The claimed replacement `tests/integration/resource_system/test_fleet_operations.py` does NOT test `TransferCommandHandler` or `TransferValidator` AT ALL — it only tests warp jump resource consumption, movement resource consumption, and component toggle effects. While unit tests exist for the handler and validator separately, this repro provides integration-level coverage of the command handler → validator → execution flow.
- **Unique tests that would be lost:** 6 integration tests for the complete cargo transfer flow including error scenarios (fleet not found, planet not found, empire not found)
- **Risk of removal:** HIGH — claimed replacement is completely wrong (tests different functionality)

### Finding #5: tests/repro_warp_bug.py
- **Original claim:** Repro test with typo, warp logic covered by integration tests
- **Verdict:** DISPUTED - KEEP
- **Evidence:** This file IS collected by pytest (2 `test_` prefixed functions). It tests warp point creation with fleet at `HexCoord(1, 0)` — NOT at system center. The claimed replacement `test_warp_logic_rework.py` tests warp distance/angle/constraints but NOT fleet location requirements. The other replacement `test_superweapon_integration.py` always creates fleet at `HexCoord(0, 0)` (system center). Neither tests the specific bug: "warp point creation fails if fleet is not at system center."
- **Unique tests that would be lost:** `test_repro_warp_point_creation_failure` — the specific off-center fleet warp creation scenario
- **Risk of removal:** HIGH — the exact bug scenario is not covered by any other test

### Finding #6: tests/unit/performance/generate_test_data.py
- **Original claim:** Standalone script, not a test, has __main__ guard
- **Verdict:** CONFIRMED
- **Evidence:** File contains no `test_` functions, no test classes, no assertions. Has `__main__` guard. Helper functions `load_json_data()`, `generate_test_ships()`, `run_generation()` are utility functions, not tests.
- **Unique tests that would be lost:** None
- **Risk of removal:** None

### Finding #7: tests/unit/performance/ scripts (4 files)
- **Original claim:** profile_simulation.py, stress_test.py, strategy_tournament.py, reproduce_scaling.py are all scripts
- **Verdict:** MODIFIED — 3 confirmed, 1 disputed
- **Evidence:**
  - `profile_simulation.py` — CONFIRMED: No test functions, cProfile script with `__main__` guard. Safe to remove.
  - `stress_test.py` — CONFIRMED: No test functions, stress testing script with `__main__` guard. Safe to remove.
  - `strategy_tournament.py` — CONFIRMED: No test functions, tournament simulation with `__main__` guard. Safe to remove.
  - `reproduce_scaling.py` — **DISPUTED: This IS a legitimate pytest test file.** Contains `@pytest.fixture` `component_environment()` and class `TestComponentScaling` with 2 real test methods (`test_crew_scaling`, `test_life_support_scaling`) that verify component ability scaling with modifiers. Real assertions testing `scaled_capacity == initial_capacity * 2`. This must NOT be removed.
- **Unique tests that would be lost (if reproduce_scaling.py removed):** 2 component scaling tests with real game objects and modifiers
- **Risk of removal:** High for reproduce_scaling.py, None for the other 3

### Finding #8: tests/unit/regressions/test_crash_regressions.py
- **Original claim:** Fragile test, catches broad Exception, commented-out assertions
- **Verdict:** CONFIRMED
- **Evidence:** The test catches `UnboundLocalError` and calls `pytest.fail()`, but catches ALL other `Exception` types and silently passes (hiding other bugs). Lines 79-86 contain commented-out assertions that were never completed. Zero positive assertions — only verifies one specific exception type doesn't occur. This is a "silence the crash" anti-pattern.
- **Unique tests that would be lost:** A crash check for `WeaponsReportPanel.draw()` with zero-range weapons, but the test doesn't verify correct behavior — only that one specific exception type doesn't occur
- **Risk of removal:** Low — test provides false confidence; any other exception passes silently

### Finding #9: tests/unit/components/test_component_health_manager.py (duplicate claim)
- **Original claim:** Duplicate of test_component_health_edge_cases.py
- **Verdict:** MODIFIED — partial overlap, consolidation recommended
- **Evidence:** The two files share 2 exact duplicate test methods (`test_take_damage_exact_hp_to_zero` = `test_take_damage_exact_destruction`, `test_hp_ratio_handles_zero_max_hp` = `test_hp_ratio_zero_max_hp`). However, `test_component_health_manager.py` has 2 UNIQUE tests not in edge_cases: `test_take_damage_raises_typeerror_for_non_numeric` and `test_hp_ratio_returns_cached_ratio`. The edge_cases file has 7 unique tests. These should be consolidated, not simply deleted.
- **Unique tests that would be lost:** 2 tests (TypeError validation, cached ratio) if health_manager.py deleted without merging
- **Risk of removal:** Medium — must merge unique tests into edge_cases file first

### Finding #10: tests/unit/fixtures/test_paths.py
- **Original claim:** Trivially obvious tests
- **Verdict:** MODIFIED — partially agree
- **Evidence:** File has 15 tests across 4 test classes. The function tests (`test_returns_path_object`, `test_returns_existing_directory`, `test_contains_game_directory`) are indeed trivial — if the project root didn't exist, no test would run at all. However, the fixture tests (`TestPathFixtures`) document the contract of shared path fixtures that other tests depend on. The trivial function tests could be removed; the fixture contract tests have value.
- **Unique tests that would be lost:** Fixture contract documentation
- **Risk of removal:** Low for function tests, Medium for fixture tests

### Finding #11: tests/unit/repro_issues/test_slider_increment.py
- **Original claim:** Mislocated but legitimate
- **Verdict:** DISPUTED — KEEP in current location
- **Evidence:** This IS a legitimate regression test with real assertions (`assert click_inc == 0.1`, `assert isinstance(val_range[0], float)`). It tests ModifierControlRow slider behavior to prevent a real UI bug. The `repro_issues/` directory is a legitimate pattern for regression tests documenting specific bugs. The file has been updated across PROJ-43 and PROJ-129, demonstrating ongoing maintenance. It is NOT mislocated.
- **Unique tests that would be lost:** N/A (recommendation is keep, not remove)
- **Risk of removal:** N/A

### Finding #12: tests/unit/fixtures/ meta-tests (3 files)
- **Original claim:** Meta-tests of debatable value
- **Verdict:** DISPUTED — KEEP all three
- **Evidence:**
  - `test_battle_fixtures.py` — Tests factory functions, verifies `enable_logging` parameter, and documents fixture contracts. Real value.
  - `test_component_fixtures.py` — Documents which abilities each component type fixture provides. Factory parametrization tests.
  - `test_ship_fixtures.py` — Contains **critical** `TestShipFixtureIsolation` class (4 tests) that verifies fixtures aren't mutated across tests. This prevents subtle test pollution bugs. Also documents composition contracts.
- **Unique tests that would be lost:** Fixture isolation verification, factory parametrization testing, fixture contract documentation
- **Risk of removal:** Medium-High — especially TestShipFixtureIsolation which guards against cross-test pollution

---

## Cross-Cutting Findings: Detailed Validation

### Old Directory Tree Claim (~12,766 lines)
- **Original claim:** 4 old directories (services/, entities/, combat/, components/) are strict subsets of newer tests in simulation/
- **Verdict:** MODIFIED — the claim is technically inaccurate but directionally correct
- **Evidence from 6 spot-checked pairs:**

#### Pair 1: Battle Service (services/ → simulation/services/)
- Old: 15 test methods | New: 77 test methods
- Old classes ARE present in new file (same or equivalent names)
- New file adds 8 entirely new test classes
- **Verdict:** Old is a subset. Safe to remove.

#### Pair 2: Layer Data (entities/ → simulation/entities/)
- Old: 24 test methods | New: 64 test methods
- Old tests have equivalents in new file, though with renamed classes (`TestLayerDataAttributeAccess` → `TestLayerDataPropertyAccess`)
- New adds 4 entirely new test classes (EdgeCases, Equality, Repr, UsagePatterns)
- **Verdict:** Old is a subset. Safe to remove.

#### Pair 3: Projectile Manager (combat/ → simulation/)
- Old: 3 test methods | New: 60 test methods
- **CAUTION:** `test_projectile_movement` from old file may not have a direct mapping in new file. Agent found only 2 of 3 old tests accounted for.
- **Verdict:** Mostly safe but verify `test_projectile_movement` coverage before deletion.

#### Pair 4: Ship Formation (entities/ → simulation/entities/)
- Old: 14 test methods | New: 76 test methods
- Old tests are scattered across new file's reorganized structure
- New adds 11 entirely new test classes
- **Verdict:** Old is a subset. Safe to remove.

#### Pair 5: Component Health Manager (components/ → simulation/components/)
- Old: 9 test methods | New: 43 test methods
- Old tests map to new equivalents
- New adds 5 new test classes with 34 additional tests
- **Verdict:** Old is a subset. Safe to remove.

#### Pair 6: Combat Endurance (combat/ → simulation/entities/)
- Old: 5 test methods | New: 45 test methods
- Old tests map to new equivalents across reorganized classes
- New adds 10 new test classes
- **Verdict:** Old is a subset. Safe to remove.

**CRITICAL NUANCE:** The old files often use **real game objects** (integration-style) while new files use **MagicMock** (pure unit-style). This means the old files test actual integration behavior while new files test interface contracts with mocks. Before deleting old directories wholesale, verify that integration-level coverage isn't lost. A proper approach would be to delete file-by-file after confirming each specific pair, not wholesale directory deletion.

### Trivial Edge Case Scaffolds (4 files)
- **Original claim:** These test nothing — only import/existence checks
- **Verdict:** CONFIRMED
- **Evidence:** All 4 files read completely:
  - `test_combat_endurance_edge_cases.py` (27 lines) — One test is `pass`, other checks `hasattr(ship, 'Ship')`
  - `test_targeting_edge_cases.py` (23 lines) — Only checks modules can be imported
  - `test_projectile_edge_cases.py` (22 lines) — Only checks modules/classes exist
  - `test_ship_formation_edge_cases.py` (22 lines) — Only checks modules/classes exist
- All 4 files provide zero functional coverage. Tests pass whether code is correct or broken.
- **Additionally, 3 "borderline" files are equally worthless:**
  - `test_ship_display_formatter_edge_cases.py` — Import existence checks only
  - `test_intercept_edge_cases.py` — Import existence checks only
  - `test_simulation_adapter_edge_cases.py` — Import existence checks only
- **Risk of removal:** None — all 7 files test nothing meaningful

### MockComponent Duplication Claim (39 definitions)
- **Original claim:** MockComponent defined 39 times, should be extracted to shared fixture
- **Verdict:** DISPUTED — count is wrong and extraction would be harmful
- **Evidence:**
  - Actual count: **18 files** contain `class MockComponent` (not 39)
  - These are NOT identical duplicates — they are contextually different:
    - Ability aggregation tests: only `ability_instances` and `abilities` dict
    - Combat damage tests: inherits from real `Component`, has `take_damage()` method, `current_hp` tracking
    - Service injection tests: has `has_ability()`, `get_modifier()`, `add_modifier()` methods
    - UI selection tests: only `id` attribute
    - Bug repro tests: only `stats` and `ship` attributes
  - A shared MockComponent fixture would either be too minimal (break tests needing methods) or too bloated (add noise to minimal tests). Test isolation would be compromised.
  - **MockPlanetType IS a valid extraction candidate** — 10 identical `Enum` definitions of `ICE_DWARF = "ICE_DWARF"` across the codebase.
- **Risk of "fixing":** HIGH — extracting to shared fixture would break test isolation and couple unrelated test modules

### Empty conftest.py Files (8 files)
- **Original claim:** Empty/near-empty, can be deleted
- **Verdict:** CONFIRMED (all 8)
- **Evidence:**
  - **5 truly empty files** (docstring only, no fixtures, no imports used):
    - `tests/unit/core/math_utils/conftest.py` (3 lines, docstring only)
    - `tests/unit/ui/schematic_view/conftest.py` (2 lines, docstring only)
    - `tests/unit/ui/battle_state_viewer/conftest.py` (5 lines, docstring + unused `import pytest`)
    - `tests/unit/ui/left_panel/conftest.py` (3 lines, docstring + unused `import pytest`)
    - `tests/unit/research/tech_tree/conftest.py` (6 lines, docstring + unused `import pytest`)
  - **3 import-only dead code files** (imports with `# noqa: F401` but no tests in their directories use the imported fixtures):
    - `tests/unit/builder/conftest.py` (12 lines, imports 7 fixtures, none used by 25 tests in dir)
    - `tests/unit/systems/conftest.py` (12 lines, imports 6 fixtures, none used by 18 tests in dir)
    - `tests/unit/ai/conftest.py` (8 lines, imports 2 fixtures, none used by 16 tests in dir)
  - Cross-reference verified: no other conftest.py or test file imports FROM these conftest files.
  - Removing them will NOT break any test — pytest fixture discovery will still find fixtures from source modules.
- **Risk of removal:** None

### Hex Math Duplication
- **Original claim:** test_hex_math_core.py (658 lines) and test_hex_math.py (298 lines) overlap on 5 test classes
- **Verdict:** MODIFIED — overlap confirmed but strategy file has some unique tests
- **Evidence:**
  - Core file: 14 test classes, 58 test methods
  - Strategy file: 9 test classes, 32 test methods
  - 5 overlapping classes: TestHexDistance, TestHexRing, TestHexLerp, TestHexLinedraw, TestHexSerialization
  - TestHexLinedraw and TestHexSerialization are functionally identical across both files
  - TestHexLerp: strategy is a strict subset of core (3 vs 4 tests)
  - TestHexDistance: strategy has 2 unique tests (`test_diagonal_distance`, `test_straight_line_distance`) not in core
  - TestHexRing: strategy has `test_radius_two` (core tests 0, 1, 3 but NOT 2) and `test_ring_size_formula`
  - Strategy file also has `TestHexPixelConversion` with `test_pixel_to_hex_near_center` not in core
  - Strategy file also has `TestHexCoord` with 11 tests covering init/equality/hash/repr/arithmetic (core covers these in 5 separate classes with different granularity)
- **Safe removal approach:** Move ~4 unique strategy tests to the core file, THEN delete the strategy file. Do NOT delete without migration.
- **Risk of removal without migration:** Low but real — loss of radius-2 ring test, diagonal distance test, pixel conversion test

---

## Cross-Cutting: Old Directory Tree Spot-Checks

### Pair 1: test_battle_service.py
| Old Test Class | Old Methods | New Equivalent | New Methods |
|---|---|---|---|
| TestBattleServiceCreateBattle | 2 | TestBattleServiceCreateBattle | 6 |
| TestBattleServiceAddShip | 3 | TestBattleServiceAddShip | 6 |
| TestBattleServiceStartBattle | 3 | TestBattleServiceStartBattle | 8 |
| TestBattleServiceUpdate | 2 | TestBattleServiceUpdate | 5 |
| TestBattleServiceGetBattleState | 2 | TestBattleServiceGetBattleState | 3 |
| TestBattleServiceIsBattleOver | 1 | TestBattleServiceIsBattleOver | 3 |
| TestBattleServiceResult | 2 | TestBattleServiceResult | 5 |
| — | — | TestBattleServiceRemoveShip (NEW) | 5 |
| — | — | TestBattleServiceRunTicks (NEW) | 5 |
| — | — | TestBattleServiceGetWinner (NEW) | 4 |
| — | — | 5 more new classes | ~24 |
**Result:** Old is strict subset. All 15 old tests have equivalents in the 77-test new file.

### Pair 2: test_layer_data.py
| Old Test Class | Old Methods | New Equivalent | New Methods |
|---|---|---|---|
| TestLayerDataConstruction | 2 | TestLayerDataConstruction | 3 |
| TestLayerDataCreateHull | 5 | TestLayerDataCreateHull | 7 |
| TestLayerDataFromDefinition | 3 | TestLayerDataFromDefinition | 9 |
| TestLayerDataClear | 6 | TestLayerDataClear | 10 |
| TestLayerDataAttributeAccess | 6 | TestLayerDataPropertyAccess | 9 |
| TestLayerDataDefaultFactoryIsolation | 2 | TestLayerDataInstanceIsolation | 3 |
| — | — | TestLayerDataEdgeCases (NEW) | 13 |
| — | — | 3 more new classes | ~10 |
**Result:** Old is subset. All 24 old tests have equivalents (some renamed) in the 64-test new file.

### Pair 3: test_projectile_manager.py
| Old Method | New Equivalent |
|---|---|
| test_projectile_movement | ⚠️ No clear 1:1 mapping found |
| test_projectile_collision | TestShipCollisions (5 tests) |
| test_missile_interception | TestMissileInterception (5 tests) |
**Result:** CAUTION — 1 of 3 old tests may lack direct equivalent. Verify before deletion.

### Pair 4: test_ship_formation.py
| Old Test Class | Old Methods | New Equivalent | Coverage |
|---|---|---|---|
| TestShipFormationUnit | 9 | Split across 8 new classes | ✓ All covered |
| TestShipFormationIntegration | 6 | Split across 4 new classes | ✓ All covered |
| — | — | 11 entirely new classes | Expanded |
**Result:** Old is subset. All 14 old tests redistributed across new file's 76 tests.

### Pair 5: test_component_health_manager.py
| Old Methods (9 total) | New Equivalent |
|---|---|
| test_take_damage_reduces_current_hp | TestTakeDamage |
| test_take_damage_returns_true_when_destroyed | TestTakeDamage |
| test_take_damage_sets_status_to_damaged_below_threshold | TestTakeDamage |
| test_take_damage_raises_typeerror_for_non_numeric | TestTakeDamageEdgeCases |
| test_take_damage_exact_hp_to_zero | TestTakeDamage |
| test_reset_hp_restores_full_hp | TestResetHp |
| test_hp_ratio_returns_cached_ratio | TestHpRatio |
| test_hp_ratio_recalculates_after_damage | TestHpRatio |
| test_hp_ratio_handles_zero_max_hp | TestHpRatio |
**Result:** Old is subset. All 9 old tests have equivalents in the 43-test new file.

### Pair 6: test_combat_endurance.py
| Old Methods (5 total) | New Equivalent |
|---|---|
| test_fuel_endurance | TestFuelEnduranceCalculation |
| test_ordnance_endurance | TestAmmoEnduranceCalculation |
| test_energy_endurance_drain | TestEnergyEnduranceCalculation |
| test_energy_recharge | TestEnergyEnduranceCalculation |
| test_standard_components_defaults | TestBoundaryConditions or TestMixedComponentScenarios |
**Result:** Old is subset. All 5 old tests have equivalents in the 45-test new file.

---

## Final Consolidated Verdicts

### CONFIRMED for Removal (11 items, ~1,130 lines)

| Item | Lines | Confidence |
|---|---|---|
| `tests/trace_cargo.py` | 52 | HIGH — diagnostic script, not a test |
| `tests/unit/performance/generate_test_data.py` | 99 | HIGH — utility script, not a test |
| `tests/unit/performance/profile_simulation.py` | 210 | HIGH — profiling script, not a test |
| `tests/unit/performance/stress_test.py` | 137 | HIGH — stress script, not a test |
| `tests/unit/performance/strategy_tournament.py` | 263 | HIGH — tournament script, not a test |
| `tests/unit/regressions/test_crash_regressions.py` | 114 | HIGH — zero positive assertions, silent exception swallowing |
| `tests/unit/combat/test_combat_endurance_edge_cases.py` | 27 | HIGH — only `pass` and import checks |
| `tests/unit/combat/test_targeting_edge_cases.py` | 23 | HIGH — only import checks |
| `tests/unit/entities/test_projectile_edge_cases.py` | 22 | HIGH — only import checks |
| `tests/unit/entities/test_ship_formation_edge_cases.py` | 22 | HIGH — only import checks |
| 8 empty conftest.py files | ~51 | HIGH — zero fixtures, unused imports |

### Additional Trivial Scaffolds Safe to Remove (3 items, ~83 lines)

| Item | Lines | Confidence |
|---|---|---|
| `tests/unit/strategy/test_ship_display_formatter_edge_cases.py` | 28 | HIGH — import checks only |
| `tests/unit/strategy/pathfinding/test_intercept_edge_cases.py` | 28 | HIGH — import checks only |
| `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py` | 27 | HIGH — import checks only |

### DISPUTED — Must Keep (10 items)

| Item | Lines | Reason |
|---|---|---|
| `tests/repro_colonize_population.py` | 47 | Unique coverage of `_transfer_founding_population` with 0 passengers |
| `tests/repro_facade_colonies.py` | 93 | Unique offset-vs-center planet click scenario |
| `tests/repro_load_cargo_bug.py` | 244 | Claimed replacement tests WRONG functionality entirely |
| `tests/repro_warp_bug.py` | 78 | Unique off-center fleet warp creation scenario |
| `tests/unit/performance/reproduce_scaling.py` | 61 | Legitimate pytest test with real assertions |
| `tests/unit/repro_issues/test_slider_increment.py` | 105 | Legitimate regression test, correctly located |
| `tests/unit/fixtures/test_battle_fixtures.py` | 143 | Factory tests and fixture contract documentation |
| `tests/unit/fixtures/test_component_fixtures.py` | 115 | Ability contract documentation |
| `tests/unit/fixtures/test_ship_fixtures.py` | 196 | Critical isolation verification tests |
| MockComponent "39 definitions" extraction | N/A | Only 18 definitions, intentionally different per context |

### MODIFIED — Conditional Removal (4 items)

| Item | Condition | Lines |
|---|---|---|
| `tests/unit/components/test_component_health_manager.py` | Merge 2 unique tests into edge_cases file FIRST, then delete | 144 |
| `tests/unit/fixtures/test_paths.py` | Remove trivial function tests (8 of 15), keep fixture contract tests | ~60 of 114 |
| `tests/unit/strategy/test_hex_math.py` | Migrate ~4 unique tests to core file FIRST, then delete | 298 |
| Old directory trees (services/, combat/, entities/, components/) | Delete file-by-file after pair verification, NOT wholesale; verify `test_projectile_movement` coverage | ~12,766 |

---

## Revised Line Counts

| Category | Original Estimate | Validated Estimate |
|---|---|---|
| Confirmed safe removal | ~1,284 (Agent 7 HIGH) | ~1,213 (scripts + trivials + crash test + conftest) |
| Conditional removal (requires migration first) | — | ~13,208 (old dirs + hex math + health manager + paths) |
| Wrongly recommended for removal | ~931 (repro tests + scaling + fixtures) | 0 (kept) |

**Bottom line:** The scripts and trivial scaffolds are clearly removable. The repro tests must be kept — the original reviewers did not verify replacement coverage. The old directory claim is directionally correct but requires careful file-by-file migration, not wholesale deletion.
