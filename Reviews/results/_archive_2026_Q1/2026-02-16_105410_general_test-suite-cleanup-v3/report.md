# Test Suite Cleanup Review Report v3

## Metadata
- **Date:** 2026-02-16
- **Type:** General Review (Test Suite Cleanup)
- **Scope:** Full test suite: `tests/` (~949 files, ~235K lines)
- **Agents Used:** 8 general-purpose agents writing directly to disk
- **Review ID:** 2026-02-16_105410_general_test-suite-cleanup-v3

## Executive Summary

**8 agents analyzed the entire test suite** across all directories. Every agent completed successfully and wrote findings to disk.

### Overall Numbers

| Metric | Value |
|--------|-------|
| **Total test files analyzed** | ~860 |
| **Total removal candidates** | ~85 individual items |
| **HIGH confidence removable lines** | ~8,500 |
| **MEDIUM confidence removable lines** | ~5,600 |
| **LOW confidence removable lines** | ~1,800 |
| **Cross-cutting: Old directory trees (Agent 8)** | ~12,766 additional lines |
| **Grand total potentially removable** | **~28,600 lines** |

### The Biggest Finding: Old Directory Trees Never Cleaned Up

Agent 8's cross-cutting analysis revealed the single largest issue: **4 entire old directory trees were never deleted after tests migrated to `tests/unit/simulation/`**. These contain ~12,766 lines of duplicate tests across 73 files:

| Old Directory | Files | Lines | Superseded By |
|---------------|-------|-------|---------------|
| `tests/unit/services/` | 6 | 1,307 | `tests/unit/simulation/services/` |
| `tests/unit/entities/` | ~44 | 7,740 | `tests/unit/simulation/entities/` |
| `tests/unit/combat/` | 19 | 3,136 | `tests/unit/simulation/` (various) |
| `tests/unit/components/` | 4 | 583 | `tests/unit/simulation/components/` |

The new files are consistently 1.2x-16.6x larger, confirming they are supersets of the old ones.

---

## Findings by Agent

### Agent 1: UI Tests (`tests/unit/ui/`) - 14 candidates, ~2,420 lines

**HIGH confidence (5 files, ~975 lines):**
1. `test_overlay.py` (127 lines) - Tests nothing real; all MagicMock, no game code imported
2. `test_race_validator.py` root (283 lines) - Duplicate of newer `screens/test_race_validator.py`
3. `mocks/mock_battle_ui_service.py` (256 lines) - 256-line mock never imported by any test
4. `test_slider_snap_logic.py` (96 lines) - Tests methods defined on test class itself, not game code
5. `test_config.py` (213 lines) - 30+ tests asserting static integer constants are positive

**MEDIUM confidence (5 files, ~1,145 lines):**
6. `test_battle_screen_extended.py` - 3/4 tests duplicated elsewhere
7. `screens/test_battle_screen_edge_cases.py` - ~300 duplicate lines with `test_battle_screen_simulation.py`
8. `services/test_battle_ui_service.py` - ~280 lines duplicated in subdirectory
9. `test_colors.py` - ~80 trivial lines (WHITE is white, BLACK is black)
10. `test_ui_imports.py` - Smoke tests that any other test would catch

**LOW confidence (4 files, ~300 lines):** Partial cleanup in 4 files.

---

### Agent 2: Strategy Tests (`tests/unit/strategy/`) - 14 candidates, ~1,703 removable + ~1,229 relocatable

**HIGH confidence (5 files, ~924 lines):**
1. `interfaces/test_engines_contracts.py` (378 lines) - ~80% duplicate of `test_engine_interfaces.py`
2. Root `test_fleet_resource_aggregator.py` (195 lines) - Duplicate of `data/` version
3. `data/test_fleet_battle_adapter.py` (303 lines) - Duplicate of root version
4. `conflict_resolution/test_conflict_core.py` (22 lines) - Trivial import-existence scaffold
5. `adapters/test_simulation_adapter_edge_cases.py` (26 lines) - Trivial import-existence scaffold

**MEDIUM confidence (6 files, ~1,593 lines):** More scaffolds, partial duplicate `test_fleet_order_transfer.py`, misplaced `test_fleet_report_filters.py` (931 lines testing UI code), duplicate `test_hex_math.py` (298 lines)

**Notable: Zero dead imports, zero skipped/xfail tests in entire strategy suite.**

---

### Agent 3: Simulation Tests (`tests/unit/simulation/`) - 12 items, ~2,660 lines + 19 data files

**HIGH confidence (5 items, ~1,152 lines + 19 data files):**
1. Old component test framework: `run_component_tests.py` (506 lines), `update_test_ships.py` (58 lines), `output/logs/` (7 .log files), `test_configs/` (12 .json files) - Entire custom runner superseded by simulation_tests/
2. `test_ship_stats_phase_ordering.py` (22 lines) - Trivial import-existence checks

**MEDIUM confidence (5 items, ~1,508 lines):**
3. Old framework utilities: `component_logger.py`, `component_sim_tools.py`, `log_parser.py` (~797 lines combined)
4. `test_physics_formulas.py` (731 lines) - Tests inline math, not game code
5. `ship_combat_engine/test_creation_and_lead.py` + `test_targeting.py` (252 lines) - Duplicated by `combat/test_targeting_system.py`

---

### Agent 4: Core + Entities + Data (`tests/unit/core/`, `entities/`, `data/`) - 14 candidates, ~1,300 lines

**HIGH confidence (10 files, ~696 lines to DELETE):**
1. `core/test_error_codes_coverage.py` (150 lines) - Fully duplicated by `test_error_codes.py`
2. `core/logger/test_warning.py` (56 lines) - Duplicates `test_logger.py`
3. `core/test_resource_loading.py` (185 lines) - Has class defined TWICE in same file + overlaps `test_resources.py`
4. `entities/test_ship_formation_edge_cases.py` (22 lines) - Trivial import checks only
5. `entities/test_projectile_edge_cases.py` (22 lines) - Trivial import checks only
6. `entities/test_ability_aggregator_scope.py` (37 lines) - Trivial import checks only
7. `core/test_constants.py` (40 lines) - Trivially obvious constant validation
8-10. Core edge_cases files (json_utils, validation, config) - 60-80% duplicate of primary files

**Key Pattern: "Edge Cases" file duplication** - secondary files duplicate 60-80% of primary `test_X.py` and add only a few unique tests.

---

### Agent 5: AI + Research + Combat - 17 candidates, ~3,962 lines

**HIGH confidence (7 items, ~2,065 lines):**
1. `ai/test_interface_definition.py` (259 lines) - Pure `hasattr` checks on ABC
2. `combat/test_combat_endurance_edge_cases.py` (27 lines) - Empty scaffold
3. `combat/test_targeting_edge_cases.py` (23 lines) - Import checks only
4. **4 overlapping AI behavior test files** consolidatable to 1 (save ~682 lines)
5. **2 duplicate capabilities cache files** (save ~225 lines)
6. **2 duplicate target evaluator rules files** (save ~599 lines)
7. **2 duplicate evaluation integration files** (save ~250 lines)

**MEDIUM confidence (7 items, ~1,389 lines):** 3 over-mocked research_controls files testing inline reimplementations (~569 lines), adapter test overlap (~496 lines), research tracker edge cases, tech tree validation duplication

---

### Agent 6: Refactor + Builder + Systems + Engine - 3 HIGH, 5 MEDIUM

**HIGH confidence:**
1. `builder/test_bulk_add.py` - 2 empty `pass` stub methods
2. `builder/test_ship_loading.py` - Empty `TestShipExpectedStats` class
3. `systems/test_allowed_layers_removal.py` - 5 one-time refactoring verification tests

**Key Finding:** `tests/unit/refactor/` is **NOT obsolete** - all 23 files are legitimate modifier effect system tests. Recommend renaming directory to `tests/unit/modifiers/`.

**MEDIUM:** Collision system duplication (7+ overlapping scenarios), spatial grid duplication, formula triple-duplication, misleading filenames.

---

### Agent 7: Remaining Small Dirs + Integration - 12 candidates, ~2,215 lines

**HIGH confidence (7 items, ~1,284 lines):**
1. `tests/trace_cargo.py` (52 lines) - Debugging script, not a test
2. `tests/repro_colonize_population.py` (47 lines) - Repro test
3. `tests/repro_facade_colonies.py` (93 lines) - Repro test
4. `tests/repro_load_cargo_bug.py` (244 lines) - Repro test (untracked in git)
5. `tests/repro_warp_bug.py` (78 lines) - Repro test
6. `tests/unit/performance/generate_test_data.py` (99 lines) - Script, not a test
7. 4 performance profiling scripts (671 lines) - `__main__` scripts, not pytest tests

**Integration tests (90 files, 24K lines): ALL CLEAN** - no skipped/xfail, no dead imports, no duplicates.

---

### Agent 8: Cross-Cutting Analysis - Systemic Issues

**The Most Impactful Finding:**
19 specific old-vs-new file pairs identified where old files are strict subsets of newer, larger files. See the "Old Directory Trees" section above.

**Other Cross-Cutting Issues:**
- **148 duplicate test class names** out of 3,032 total (`TestEdgeCases` appears 24 times)
- **MockComponent defined 39 times**, MockPlanetType 29 times, MockGalaxy 18 times
- **4 trivial scaffold `_edge_cases.py` files** (should be deleted)
- **9 repro/debug test files** at root level
- **60+ `pytest.skip()` calls** (test_theme_discovery.py alone has 11)
- **1 dead import** in TYPE_CHECKING block
- **8 empty conftest.py files**

---

## Prioritized Action Plan

### Phase 1: Delete Old Directory Trees (HIGH impact, ~12,766 lines)
Audit and delete `tests/unit/services/`, `tests/unit/combat/`, `tests/unit/components/`, and subset of `tests/unit/entities/` after confirming all tests are subsumed by `tests/unit/simulation/`.

### Phase 2: Delete Obvious Dead Weight (HIGH confidence, ~3,500 lines)
- All repro/debug scripts at root level (~514 lines)
- Performance scripts that aren't tests (~770 lines)
- Old component test framework in simulation/ (~1,152 lines + 19 data files)
- All trivial scaffold `_edge_cases.py` files (~170 lines)
- Unused MockBattleUIService (256 lines)
- Over-mocked tests that test nothing real (~500+ lines)

### Phase 3: Consolidate Duplicates (MEDIUM confidence, ~4,000 lines)
- AI behavior test files: 4 -> 1
- Target evaluator files: consolidate 3 pairs
- Strategy duplicates: merge root/data file pairs
- Core edge_cases files: merge unique tests into primaries, delete secondaries
- Logger subdirectory: merge into test_logger.py

### Phase 4: Structural Improvements (LOW effort)
- Rename `tests/unit/refactor/` to `tests/unit/modifiers/`
- Relocate misplaced tests (fleet_report_filters, hex_math)
- Extract shared mock classes (MockComponent x39, MockPlanetType x29)
- Delete empty conftest.py files
- Fix dead import in test_formation_flight.py
- Rename generic `TestEdgeCases` classes

---

## Agent Reports
- [Agent 1: UI Tests](findings/agent_1_ui_tests.md)
- [Agent 2: Strategy Tests](findings/agent_2_strategy_tests.md)
- [Agent 3: Simulation Tests](findings/agent_3_simulation_tests.md)
- [Agent 4: Core + Entities + Data](findings/agent_4_core_entities_data.md)
- [Agent 5: AI + Research + Combat](findings/agent_5_ai_research_combat.md)
- [Agent 6: Refactor + Builder + Systems + Engine](findings/agent_6_refactor_builder_systems_engine.md)
- [Agent 7: Remaining + Integration](findings/agent_7_remaining_integration.md)
- [Agent 8: Cross-Cutting Analysis](findings/agent_8_cross_cutting.md)
