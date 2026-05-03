# Agent 8: Cross-Cutting Analysis

## Summary

Cross-cutting analysis of the entire test suite (769 test files, 3,032 test classes) reveals significant systemic issues:

| Category | Count | Severity |
|----------|-------|----------|
| Duplicate test class names | 148 (across 3,032 classes) | Medium |
| `TestEdgeCases` generic name usage | 24 classes | Medium |
| Old-vs-new directory duplication pairs | 19 file pairs identified | **High** |
| Entire old directories to audit/delete | 4 directories (~12,766 lines) | **High** |
| Repeated mock class definitions | 39x `MockComponent`, 29x `MockPlanetType`, 18x `MockGalaxy` | Medium |
| Trivial edge_cases scaffolds | 4 files (+ 3 borderline) | Low |
| Repro/debug test files | 9 files (5 at root level) | Low |
| `pytest.skip()` calls | 60+ instances | Low |
| Empty conftest.py files | 8 files | Low |
| Dead TYPE_CHECKING import | 1 instance | Low |

**Estimated waste:** ~12,766 lines across 73 test files in old directories (tests/unit/services, tests/unit/entities, tests/unit/combat, tests/unit/components) that have been superseded by tests in tests/unit/simulation/. These old files run duplicate tests, inflating test count and execution time without adding coverage.

---

## 1. Skipped/XFail Tests

### pytest.skip() Calls (Conditional Skips)

Total: 60+ instances of `pytest.skip()` across the test suite. **No `@pytest.mark.skip` or `@pytest.mark.xfail` decorators** were found, and no `unittest.skip` usage.

#### By Category:

**Repro/Bug Tests (conditional feature checks):**
- `tests/repro_issues/test_bug_15_screenshot_strategy.py:124,152` - "capture_strategy_layer() not implemented yet"

**Registry/Data Availability Guards (largest category):**
- `tests/unit/combat/test_multitarget.py:89,102,129` - "multiplex_tracking component not defined"
- `tests/unit/data/test_data_validation.py:281` - "modifiers.json not found"
- `tests/unit/builder/test_builder_ui_sync.py:174` - "No vehicle classes found to test type filtering."
- `tests/unit/entities/test_modifier_defaults_robustness.py:34,63` - "Railgun not found" / "PDC not found"
- `tests/unit/entities/test_modifier_propagation.py:77` - "simple_size_mount not found"
- `tests/unit/core/resources_registry/test_integration.py:274` - "data/resources.json not found"
- `tests/unit/refactor/test_pipeline_unification.py:24,41,48,69,122,128` - Various component/ability not found (6 skips)
- `tests/unit/refactor/test_multi_ability_effects.py:195,199,238,242,279,283` - Various (6 skips)
- `tests/unit/systems/test_allowed_layers_removal.py:85,108,130` - Component not in registry
- `tests/unit/simulation/test_component_decoupling.py:113,133,161` - "standard_engine doesn't have ResourceConsumption ability"
- `tests/unit/quickstart/test_quickstart_designs.py:105` - design has no expected_stats

**File System Guards:**
- `tests/unit/ui/test_theme_discovery.py:36,275,279,295,299,335,339,356,360,412,416` - **11 instances in one file!**
- `tests/unit/ui/test_sprites.py:35,279` - Components directory not found

**Snapshot Baseline Creation (auto-skip on first run):**
- `tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py` - 13 instances
- `tests/regression/modifier_ability_snapshots/test_utility_modifiers.py` - 8 instances

**Integration Test Data Guards:**
- `tests/integration/test_formation_flight.py:207` - "No ship designs available"
- `tests/integration/test_formation_attack.py:163` - "No ship designs available"
- `tests/integration/gameplay_loop/test_turn_execution.py:147` - "No colony available"
- `tests/integration/gameplay_loop/test_fleet_operations.py:70` - "No player empire"
- `tests/integration/gameplay_loop/test_commands_colonization.py:54,77,221,257` - Various (4 skips)
- `tests/integration/research_workflow/test_workflow.py:182` - "Tech tree JSON not found"
- `tests/integration/save_load/test_resupply_persistence.py:233,282` - No colonies/fleets
- `tests/integration/fleet_combat/test_component_destruction_cascade.py:249` - Component not available
- `tests/integration/fleet_combat/test_combat_resource_consumption.py:168` - Components lack abilities
- `tests/integration/strategy/facade/test_facade_integration.py:145,168,208,304,325` - Various (5 skips)

### Analysis
- `test_theme_discovery.py` alone has 11 `pytest.skip()` calls guarding against missing theme files. Either fixtures should guarantee the data exists, or these should be `skipIf` decorators.
- Snapshot tests use `pytest.skip()` for baseline creation (21 instances) -- intentional but unusual.
- Many registry/component guard skips could be replaced with proper fixtures.

---

## 2. Repro/Reproduction Tests

Found 9 repro/debug test files:

| File | Location | Notes |
|------|----------|-------|
| `tests/repro_load_cargo_bug.py` | Root tests/ | Untracked in git |
| `tests/repro_warp_bug.py` | Root tests/ | Tracked |
| `tests/repro_colonize_population.py` | Root tests/ | Tracked |
| `tests/repro_facade_colonies.py` | Root tests/ | Tracked |
| `tests/trace_cargo.py` | Root tests/ | Untracked, debug script |
| `tests/repro_issues/test_bug_05_deep_repro.py` | repro_issues/ | In dedicated dir |
| `tests/repro_issues/test_bug_15_screenshot_strategy.py` | repro_issues/ | Has pytest.skip() |
| `tests/unit/strategy/engine/test_production_repro.py` | unit tests | Mixed into unit tests |
| `tests/unit/performance/reproduce_scaling.py` | performance | Performance repro |

Additionally, `tests/repro_issues/` contains 27 total bug reproduction test files (test_bug_01 through test_bug_27). While the directory is organized, the question is whether these should all remain or be consolidated/promoted to regression tests.

**Recommendation:** Root-level repro files should be deleted or moved to `tests/repro_issues/`. `test_production_repro.py` in unit tests should be evaluated for promotion to a proper regression test.

---

## 3. Duplicate Test Class Names

**Total test classes:** 3,032
**Unique class names:** 2,838
**Duplicate class names:** 148

### Most Severe: `TestEdgeCases` - 24 occurrences

The generic name "TestEdgeCases" appears in 24 different files. While pytest resolves by module path, this makes test output confusing and searching difficult.

**All 24 files:**
1. `tests/integration/colonization/test_planet_specific_colonization.py`
2. `tests/integration/research_workflow/test_persistence.py`
3. `tests/integration/strategy/test_fleet_navigation_consistency.py`
4. `tests/unit/ai/formation_prediction/test_formation_behavior.py`
5. `tests/unit/ai/target_evaluator/test_evaluation_integration.py`
6. `tests/unit/core/test_resources.py`
7. `tests/unit/core/logger/test_singleton.py`
8. `tests/unit/core/profiling/test_persistence.py`
9. `tests/unit/core/registry/test_registry_features.py`
10. `tests/unit/core/resources_registry/test_loading.py`
11. `tests/unit/research/tech_tree/test_validation.py`
12. `tests/unit/simulation/test_projectile_manager.py`
13. `tests/unit/simulation/entities/test_ship_serialization.py`
14. `tests/unit/simulation/services/test_modifier_service.py`
15. `tests/unit/simulation/systems/test_battle_engine_tick.py`
16. `tests/unit/simulation/systems/test_tech_preset_loader.py`
17. `tests/unit/strategy/data/test_fleet_battle_adapter.py`
18. `tests/unit/strategy/engine/test_population_engine.py`
19. `tests/unit/strategy/fleet/test_warp_resources.py`
20. `tests/unit/strategy/formulas/test_habitability.py`
21. `tests/unit/strategy/generation/test_region_classifier.py`
22. `tests/unit/strategy/ship_instance/test_serialization.py`
23. `tests/unit/ui/screens/test_strategy_input_handler_core.py`
24. `tests/unit/ui/screens/test_strategy_screen.py`

### Fully Duplicated Test Suites: Old Location vs New

The following test file pairs exist where the old file is a **strict subset** of the new file (the new file is always 1.2x-16.6x larger):

| Old File (smaller) | New File (larger) | Ratio |
|---------------------|-------------------|-------|
| `tests/unit/services/test_battle_service.py` (7.7KB) | `tests/unit/simulation/services/test_battle_service.py` (34KB) | 4.5x |
| `tests/unit/services/test_modifier_service.py` (14KB) | `tests/unit/simulation/services/test_modifier_service.py` (38KB) | 2.6x |
| `tests/unit/services/test_vehicle_design_service.py` (11KB) | `tests/unit/simulation/services/test_vehicle_design_service.py` (39KB) | 3.4x |
| `tests/unit/entities/test_layer_data.py` (7.8KB) | `tests/unit/simulation/entities/test_layer_data.py` (21KB) | 2.7x |
| `tests/unit/combat/test_projectiles.py` (10KB) | `tests/unit/simulation/entities/test_projectile.py` (23KB) | 2.3x |
| `tests/unit/entities/test_ship_serialization.py` (8.7KB) | `tests/unit/simulation/entities/test_ship_serialization.py` (33KB) | 3.8x |
| `tests/unit/entities/test_ship_formation.py` (7.9KB) | `tests/unit/simulation/entities/test_ship_formation.py` (37KB) | 4.7x |
| `tests/unit/combat/test_projectile_manager.py` (3.3KB) | `tests/unit/simulation/test_projectile_manager.py` (55KB) | 16.6x |
| `tests/unit/components/test_component_health_manager.py` (5.6KB) | `tests/unit/simulation/components/test_component_health_manager.py` (15KB) | 2.7x |
| `tests/unit/components/test_component_resource_manager.py` (8.8KB) | `tests/unit/simulation/components/test_component_resource_manager.py` (26KB) | 3.0x |
| `tests/unit/combat/test_combat_endurance.py` (13KB) | `tests/unit/simulation/entities/test_combat_endurance.py` (38KB) | 2.9x |
| `tests/unit/entities/test_modifiers.py` (5.8KB) | `tests/unit/simulation/components/test_modifiers.py` (9.9KB) | 1.7x |
| `tests/unit/refactor/test_modifier_introspection.py` (15KB) | `tests/unit/simulation/components/test_modifier_introspection.py` (26KB) | 1.7x |
| `tests/unit/test_screenshot_manager.py` (2.8KB) | `tests/unit/ui/services/test_screenshot_manager.py` (25KB) | 8.8x |
| `tests/unit/ui/test_rendering_logic.py` (9.5KB) | `tests/unit/ui/schematic_view/test_rendering_logic.py` (12KB) | 1.3x |
| `tests/unit/ui/test_race_validator.py` (9.9KB) | `tests/unit/ui/screens/test_race_validator.py` (12KB) | 1.2x |
| `tests/unit/strategy/test_fleet_battle_adapter.py` (8.4KB) | `tests/unit/strategy/data/test_fleet_battle_adapter.py` (11KB) | 1.3x |
| `tests/unit/strategy/test_fleet_resource_aggregator.py` (8.6KB) | `tests/unit/strategy/data/test_fleet_resource_aggregator.py` (31KB) | 3.6x |
| `tests/unit/strategy/test_quickstart_builder.py` (16KB) | `tests/unit/quickstart/test_quickstart_builder.py` (16KB) | 1.0x |

### 4 Entire Old Directories That Should Be Audited for Deletion

These directories appear to contain older versions of tests that have been superseded:

| Directory | Files | Lines | Newer Location |
|-----------|-------|-------|----------------|
| `tests/unit/services/` | 6 test files | 1,307 | `tests/unit/simulation/services/` |
| `tests/unit/entities/` | 44 test files | 7,740 | `tests/unit/simulation/entities/` |
| `tests/unit/combat/` | 19 test files | 3,136 | `tests/unit/simulation/` (various) |
| `tests/unit/components/` | 4 test files | 583 | `tests/unit/simulation/components/` |
| **Total** | **73 files** | **12,766 lines** | |

### Other Notable Duplicates (4 occurrences each)

- `TestComputePlanetProduction` (4x): across 4 different UI test files
- `TestLoadResourcesData` (4x): including 2 in the same file (`test_resource_loading.py`)
- `TestPanelKill` (4x): across 4 panel test files

### 3-Way Duplicates (17 classes with 3 occurrences)
`TestButtonHighlighting`, `TestConfigurationBinding`, `TestBackwardCompatibility`, `TestLeadCalculation`, `TestShieldRegeneration`, `TestSingletonBehavior`, `TestStrictDIEnforcement`, `TestTargetSelection`, `TestThreadSafety`, `TestValueFormatting`, `TestNavigationStep`, `TestCloseCallback`, `TestProcessEvent`, `TestHelperFunctions`, `TestHasWarpCapability`, `TestHandleResize`, `TestModifierStacking`

---

## 4. Edge Cases Scaffold Files

**Total `*_edge_cases.py` files:** 29

### Trivial Scaffolds (4 files) -- SHOULD BE DELETED

These contain only import/existence checks with no real test logic:

1. **`tests/unit/combat/test_combat_endurance_edge_cases.py`** (26 lines, 2 tests, 1 assert)
   - One test just checks `hasattr(ship, 'Ship')`, other is `pass`
2. **`tests/unit/combat/test_targeting_edge_cases.py`** (22 lines, 2 tests, 2 asserts)
   - Only checks that modules can be imported
3. **`tests/unit/entities/test_projectile_edge_cases.py`** (21 lines, 2 tests, 2 asserts)
   - Only checks that modules/classes exist
4. **`tests/unit/entities/test_ship_formation_edge_cases.py`** (21 lines, 2 tests, 2 asserts)
   - Only checks that modules/classes exist

### Borderline Small (3 files) -- Worth Reviewing

5. **`tests/unit/strategy/test_ship_display_formatter_edge_cases.py`** (27 lines, 3 tests, 3 asserts)
6. **`tests/unit/strategy/pathfinding/test_intercept_edge_cases.py`** (27 lines, 3 tests, 4 asserts)
7. **`tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py`** (26 lines, 3 tests, 3 asserts)

### Substantial Edge Case Files (22 files) -- KEEP
The remaining 22 files contain meaningful test logic (100-711 lines, 8-38 tests, 10-65 asserts each).

### Statistics
- Trivial scaffolds: 4/29 (14%)
- Borderline small: 3/29 (10%)
- Substantial: 22/29 (76%)

---

## 5. Dead Imports

### Confirmed Dead Imports

1. **`tests/integration/test_formation_flight.py:24`** - `from game.core.registries.game_registries import GameRegistries`
   - Module `game/core/registries/` does not exist (the directory was removed)
   - This is inside a `TYPE_CHECKING` block so it doesn't fail at runtime, but it's a stale reference
   - The correct import is `from game.core.registry import GameRegistries`

2. **`tests/refactor/test_deprecated_code_removed.py:16`** - `from game.strategy.engine.fleet_movement import FleetMovementSimulator`
   - This is **intentional** -- the test verifies the module stays removed by asserting `ImportError`

### No Other Dead Imports Found
All other `from game.xxx import` statements in test files resolve to existing modules. The codebase is in good shape regarding import validity.

---

## 6. Abandoned Test Infrastructure

### Empty/Near-Empty conftest.py Files (8 files)

These conftest files have no fixtures and minimal content:

| File | Content |
|------|---------|
| `tests/unit/core/math_utils/conftest.py` | Single docstring comment |
| `tests/unit/ui/schematic_view/conftest.py` | Single docstring comment |
| `tests/unit/ui/battle_state_viewer/conftest.py` | Docstring only |
| `tests/unit/ui/left_panel/conftest.py` | Docstring only |
| `tests/unit/research/tech_tree/conftest.py` | Docstring only |
| `tests/unit/builder/conftest.py` | Minor setup, no fixtures |
| `tests/unit/systems/conftest.py` | Minor setup, no fixtures |
| `tests/unit/ai/conftest.py` | Fixture re-exports only |

**Recommendation:** Empty conftest files with just docstrings can be deleted.

### Massively Duplicated Mock Classes

The following mock/fake/stub classes are redefined across many files instead of being shared:

| Mock Class | Definitions | Recommendation |
|------------|-------------|----------------|
| `MockComponent` | **39 definitions** | Extract to shared fixture |
| `MockPlanetType` | **29 definitions** | Extract to shared fixture |
| `MockGalaxy` | **18 definitions** | Extract to shared fixture |
| `MockPlanet` | 8 definitions | Extract to shared fixture |
| `MockShip` | 8 definitions | Extract to shared fixture |
| `MockSession` | 7 definitions | Extract to shared fixture |
| `MockSystem` | 6 definitions | Extract to shared fixture |
| `MockAbility` | 6 definitions | Extract to shared fixture |
| `MockGameSession` | 5 definitions | Extract to shared fixture |
| `MockEmpire` | 4 definitions | Extract to shared fixture |

`MockComponent` alone is defined **39 separate times** across the test suite. While some of these may differ slightly, the majority are likely identical or near-identical mock objects.

`MockPlanetType(Enum)` is particularly egregious at 29 copies, with 10 copies in `test_colonization_facade.py` and 10 in `test_colonize_validator.py`. This should be a single shared fixture.

### `tests/unit/refactor/` Directory (23 files)

This directory contains tests written during specific refactoring projects. While the test names contain "refactor" in the path, the tests themselves validate current behavior (abilities, modifiers, formulas). Some files overlap with `tests/unit/simulation/`:

- `test_modifier_introspection.py` (15KB) duplicated in `tests/unit/simulation/components/test_modifier_introspection.py` (26KB)
- `test_ability_introspection.py` duplicated in `tests/unit/simulation/components/abilities/test_ability_base.py`
- `test_stat_key.py` duplicated in `tests/unit/simulation/components/abilities/test_stat_keys.py`

**Recommendation:** Audit `tests/unit/refactor/` -- tests that have been absorbed into `tests/unit/simulation/` should be deleted.

---

## 7. Cross-Directory Duplication Patterns

### Pattern 1: Old Flat Structure vs New Hierarchical Structure

The test suite went through a restructuring where tests moved from flat directories to a hierarchical `tests/unit/simulation/` structure. **The old directories were never cleaned up**, resulting in:

```
OLD (smaller, subset)              NEW (larger, superset)
tests/unit/services/          -->  tests/unit/simulation/services/
tests/unit/entities/          -->  tests/unit/simulation/entities/
tests/unit/combat/            -->  tests/unit/simulation/ (various)
tests/unit/components/        -->  tests/unit/simulation/components/
tests/unit/refactor/          -->  tests/unit/simulation/ (various)
```

**Impact:** ~12,766 lines of duplicate tests running in CI, inflating test count (~7,353 baseline) by an estimated 200-400 tests.

### Pattern 2: Same-File Basename in Different Directories

43 test files share the same basename across different directories. Most are legitimate (e.g., `test_basics.py` in 7 directories is fine because they test different modules). However, these are problematic duplications:

| Basename | Old Location | New Location | Old Size | New Size |
|----------|-------------|-------------|----------|----------|
| `test_battle_service.py` | `unit/services/` | `unit/simulation/services/` | 7.7KB | 34KB |
| `test_modifier_service.py` | `unit/services/` | `unit/simulation/services/` | 14KB | 38KB |
| `test_vehicle_design_service.py` | `unit/services/` | `unit/simulation/services/` | 11KB | 39KB |
| `test_layer_data.py` | `unit/entities/` | `unit/simulation/entities/` | 7.8KB | 21KB |
| `test_ship_serialization.py` | `unit/entities/` | `unit/simulation/entities/` | 8.7KB | 33KB |
| `test_ship_formation.py` | `unit/entities/` | `unit/simulation/entities/` | 7.9KB | 37KB |
| `test_projectile_manager.py` | `unit/combat/` | `unit/simulation/` | 3.3KB | 55KB |
| `test_component_health_manager.py` | `unit/components/` | `unit/simulation/components/` | 5.6KB | 15KB |
| `test_component_resource_manager.py` | `unit/components/` | `unit/simulation/components/` | 8.8KB | 26KB |
| `test_combat_endurance.py` | `unit/combat/` | `unit/simulation/entities/` | 13KB | 38KB |
| `test_modifier_introspection.py` | `unit/refactor/` | `unit/simulation/components/` | 15KB | 26KB |

### Pattern 3: Strategy Test Migration

Similarly, some strategy tests have both old and new locations:

| Old | New |
|-----|-----|
| `tests/unit/strategy/test_fleet_battle_adapter.py` | `tests/unit/strategy/data/test_fleet_battle_adapter.py` |
| `tests/unit/strategy/test_fleet_resource_aggregator.py` | `tests/unit/strategy/data/test_fleet_resource_aggregator.py` |
| `tests/unit/strategy/test_quickstart_builder.py` | `tests/unit/quickstart/test_quickstart_builder.py` |

### Pattern 4: Hex Math Tests (Pure Duplication)

`tests/unit/core/test_hex_math_core.py` (658 lines) and `tests/unit/strategy/test_hex_math.py` (298 lines) both test `game.core.hex_math` with overlapping test class names:
- `TestHexDistance`, `TestHexLerp`, `TestHexLinedraw`, `TestHexRing`, `TestHexSerialization`

The strategy one is smaller and appears to be a predecessor. Only one should exist.

---

## Systemic Recommendations

### Priority 1: Delete Old Directory Trees (HIGH IMPACT)

**Action:** Audit and delete the following directories after confirming their tests are fully subsumed by the newer location:

1. `tests/unit/services/` (6 files, 1,307 lines) -- superseded by `tests/unit/simulation/services/`
2. `tests/unit/components/` (4 files, 583 lines) -- superseded by `tests/unit/simulation/components/`
3. `tests/unit/combat/` (19 files, 3,136 lines) -- superseded by `tests/unit/simulation/` (various)
4. Individual files in `tests/unit/entities/` that duplicate `tests/unit/simulation/entities/`
5. Individual files in `tests/unit/refactor/` that duplicate `tests/unit/simulation/`

**Estimated savings:** ~12,000+ lines, ~200-400 duplicate tests removed from CI

### Priority 2: Consolidate Duplicate Mock Classes (MEDIUM IMPACT)

Create shared mock fixtures in `tests/fixtures/` or appropriate `conftest.py` files for:
- `MockComponent` (39 definitions)
- `MockPlanetType` (29 definitions)
- `MockGalaxy` (18 definitions)

### Priority 3: Delete Trivial Scaffolds (LOW EFFORT)

Delete the 4 trivial edge_cases scaffold files that test nothing:
- `tests/unit/combat/test_combat_endurance_edge_cases.py`
- `tests/unit/combat/test_targeting_edge_cases.py`
- `tests/unit/entities/test_projectile_edge_cases.py`
- `tests/unit/entities/test_ship_formation_edge_cases.py`

### Priority 4: Clean Up Repro Files (LOW EFFORT)

- Delete or move root-level repro files to `tests/repro_issues/`
- Evaluate `tests/unit/strategy/engine/test_production_repro.py` for promotion

### Priority 5: Rename `TestEdgeCases` Classes (MEDIUM EFFORT)

Rename all 24 `TestEdgeCases` classes to include the module/component name (e.g., `TestProjectileManagerEdgeCases`, `TestShipSerializationEdgeCases`).

### Priority 6: Fix Dead Import (LOW EFFORT)

Fix `tests/integration/test_formation_flight.py:24`: change `from game.core.registries.game_registries import GameRegistries` to `from game.core.registry import GameRegistries` inside the `TYPE_CHECKING` block.

### Priority 7: Clean Up Empty conftest.py Files (LOW EFFORT)

Delete 4-5 conftest files that contain nothing but a docstring.

### Priority 8: Reduce pytest.skip() Usage (LONG TERM)

Replace conditional `pytest.skip()` calls with proper fixture guarantees where possible, especially in `test_theme_discovery.py` (11 skips).
