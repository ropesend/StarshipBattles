# Agent 2: Strategy Tests Analysis

## Summary
- Files analyzed: 154 test files (~48,400 lines)
- Removal candidates found: 14
- HIGH confidence: 5
- MEDIUM confidence: 6
- LOW confidence: 3

---

## HIGH Confidence Removal Candidates
(Tests almost certainly safe to remove -- clear duplicates or trivially useless)

### 1. test_engines_contracts.py (DUPLICATE of test_engine_interfaces.py)
- **Location:** `tests/unit/strategy/interfaces/test_engines_contracts.py`
- **Category:** Duplicate
- **Reason:** This file (PROJ-110) is a near-complete duplicate of `test_engine_interfaces.py` (PROJ-43). Both files test the exact same engine interfaces (IMovementEngine, IProductionEngine, IOrderProcessor, IConflictEngine, IResourceEngine, IMaintenanceEngine) with the exact same patterns: is-abstract, cannot-instantiate, has-abstract-method, concrete-implementation-works. The contracts file adds coverage for IPopulationEngine, IResupplyEngine, and IHarvestingEngine that could be merged into the original file if needed. The core overlap is ~80% of the content.
- **Lines:** ~378 lines removable (merge ~50 lines of unique tests into `test_engine_interfaces.py`)
- **Action:** Merge the 3 unique interface tests (IPopulationEngine, IResupplyEngine, IHarvestingEngine) into `test_engine_interfaces.py`, then delete `test_engines_contracts.py`.

### 2. test_fleet_resource_aggregator.py in data/ (DUPLICATE of root-level)
- **Location:** `tests/unit/strategy/data/test_fleet_resource_aggregator.py`
- **Category:** Duplicate
- **Reason:** Both `data/test_fleet_resource_aggregator.py` (748 lines, PROJ-119) and root-level `test_fleet_resource_aggregator.py` (195 lines, PROJ-87) test `FleetResourceAggregator` from `game.strategy.data.fleet_resource_aggregator`. They test overlapping behaviors: movement costs, warp costs, fuel endurance, cargo operations, empty fleet edge cases. The data/ version is more comprehensive with better structure and edge case coverage.
- **Lines:** ~195 lines removable (delete root-level `test_fleet_resource_aggregator.py`)
- **Action:** Delete `tests/unit/strategy/test_fleet_resource_aggregator.py` -- the `data/` version is the superset.

### 3. test_fleet_battle_adapter.py in data/ (DUPLICATE of root-level)
- **Location:** `tests/unit/strategy/data/test_fleet_battle_adapter.py`
- **Category:** Duplicate
- **Reason:** Both `data/test_fleet_battle_adapter.py` (303 lines, PROJ-119) and root-level `test_fleet_battle_adapter.py` (225 lines, PROJ-87) test `FleetBattleAdapter`. They test overlapping scenarios: `to_battle_ships` (empty, combat-capable, skip non-combat, team positions), `_default_formation_positions` (team 0 left, team 1 right, spacing), `update_from_battle_results` (destroyed ships, survivors, speed recalculation). The root-level version also tests Fleet delegation which is unique. One should be kept.
- **Lines:** ~303 lines removable (delete `data/test_fleet_battle_adapter.py` -- the root-level version tests delegation too)
- **Action:** Delete `tests/unit/strategy/data/test_fleet_battle_adapter.py`. The root-level version covers the same scenarios plus Fleet delegation.

### 4. test_conflict_core.py (TRIVIAL -- existence checks only)
- **Location:** `tests/unit/strategy/conflict_resolution/test_conflict_core.py`
- **Category:** Trivially obvious / Scaffold
- **Reason:** Contains only 2 tests that check `import game.strategy.engine.conflict_resolution_engine` and `ConflictResolutionEngine is not None`. These import-existence checks are completely subsumed by the thorough tests in `test_core.py` and `test_battle_resolver_integration.py` in the same directory, which actually instantiate and exercise the engine.
- **Lines:** ~22 lines

### 5. test_simulation_adapter_edge_cases.py (TRIVIAL -- existence checks only)
- **Location:** `tests/unit/strategy/adapters/test_simulation_adapter_edge_cases.py`
- **Category:** Trivially obvious / Scaffold
- **Reason:** Contains only 3 tests verifying module/class/protocol can be imported and are `not None`. All of these are completely subsumed by the comprehensive `test_simulation_adapter.py` (384 lines) which imports, instantiates, and extensively tests the same classes.
- **Lines:** ~26 lines

---

## MEDIUM Confidence Removal Candidates
(Likely safe to remove, but verify before acting)

### 6. test_build_queue_source_errors.py (TRIVIAL -- existence checks only)
- **Location:** `tests/unit/strategy/data/test_build_queue_source_errors.py`
- **Category:** Trivially obvious / Scaffold
- **Reason:** Despite the name suggesting error path testing, this file contains only 3 tests: module exists, class exists, class has `queue_id` field. These are pure existence/introspection checks that add no value beyond what `test_build_queue_source.py` already covers by actually constructing and using `BuildQueueSource` objects.
- **Lines:** ~28 lines

### 7. test_ship_display_formatter_edge_cases.py (TRIVIAL -- existence checks only)
- **Location:** `tests/unit/strategy/test_ship_display_formatter_edge_cases.py`
- **Category:** Trivially obvious / Scaffold
- **Reason:** Contains only 3 tests: module exists, class exists, has `format_display_id` method. Despite being named "edge cases", this file tests zero edge cases. The companion `test_ship_display_formatter.py` thoroughly exercises the actual class. This looks like a scaffold file that was never populated.
- **Lines:** ~27 lines

### 8. test_fleet_order_transfer.py (PARTIAL DUPLICATE of test_transfer_order.py)
- **Location:** `tests/unit/strategy/engine/test_fleet_order_transfer.py`
- **Category:** Duplicate (partial)
- **Reason:** Both `test_fleet_order_transfer.py` (PROJ-119, 383 lines) and `test_transfer_order.py` (PROJ-68, 489 lines) test `FleetOrderProcessor.process_transfer()` and related `_execute_load`/`_execute_unload` methods. Significant overlap in: load passengers from colony, unload passengers, partial amounts, species-specific transfers. The PROJ-68 file additionally tests serialization and command dispatch. One should be consolidated.
- **Lines:** ~383 lines removable (consolidate into `test_transfer_order.py`)
- **Action:** Merge any unique tests from `test_fleet_order_transfer.py` into `test_transfer_order.py`, then delete the former.

### 9. test_fleet_report_filters.py (MISPLACED -- tests UI code)
- **Location:** `tests/unit/strategy/test_fleet_report_filters.py`
- **Category:** Misplaced test file
- **Reason:** This 931-line test file is placed in `tests/unit/strategy/` but it imports and tests `game.ui.screens.fleet_report_filters` and `game.ui.screens.fleet_report_view_model` -- these are UI layer modules. The file should be relocated to `tests/unit/ui/screens/` to match the module it tests. This is not a removal candidate per se, but a relocation candidate.
- **Lines:** ~931 lines (relocate, not remove)

### 10. test_hex_math.py (DUPLICATE -- tests core module from wrong location)
- **Location:** `tests/unit/strategy/test_hex_math.py`
- **Category:** Duplicate / Misplaced
- **Reason:** Tests `game.core.hex_math` (a core module) but is placed in `tests/unit/strategy/`. A more comprehensive version exists at `tests/unit/core/test_hex_math_core.py` (658 lines, 68 tests vs 298 lines, 34 tests). The strategy version tests a subset of what the core version covers.
- **Lines:** ~298 lines removable if core version covers all scenarios
- **Action:** Verify that all 34 tests in the strategy version have equivalents in the core version, then delete the strategy copy.

### 11. test_production_repro.py (REPRO/SCAFFOLD test)
- **Location:** `tests/unit/strategy/engine/test_production_repro.py`
- **Category:** Scaffold / Repro test
- **Reason:** The file name "repro" and test names like `test_repro_integer_rounding_logic` and `test_repro_drag_and_drop_1_turn_bug` strongly suggest this was a reproduction test created during debugging. These tests verify specific bug-fix scenarios that should be part of the proper `test_production_engine` test suite, not kept as separate repro files. The `production_engine/` subdirectory has 7 test files (2185 lines) with comprehensive coverage.
- **Lines:** ~133 lines
- **Action:** Verify the specific scenarios are covered by the production_engine test suite, then remove.

---

## LOW Confidence Removal Candidates
(Worth investigating but may have value)

### 12. test_battle_resolver.py (OVER-TESTED interface)
- **Location:** `tests/unit/strategy/interfaces/test_battle_resolver.py`
- **Category:** Over-tested interface
- **Reason:** Contains 180 lines testing `IBattleResolver` and `BattleResult` with patterns like "is importable", "is dataclass", "has field", "is abstract", "cannot instantiate", "concrete implementation works". While interface contract tests have some value, this level of detail for a simple ABC + dataclass is excessive. The `SimulationBattleResolver` and `ConflictResolutionEngine` tests already exercise this interface through real implementations.
- **Lines:** ~180 lines
- **Note:** These are part of PROJ-11 TDD scaffolding. If the team values contract tests as living documentation, keep them. If not, they add maintenance burden without catching real bugs.

### 13. test_engine_event_emission.py (POTENTIAL OVERLAP with test_game_session_events.py)
- **Location:** `tests/unit/strategy/test_engine_event_emission.py`
- **Category:** Potential overlap
- **Reason:** Both `test_engine_event_emission.py` (696 lines, PROJ-77 Phase 3) and `test_game_session_events.py` (250 lines, PROJ-77 Phase 2) test event-related functionality. However, they test at different levels: `test_game_session_events.py` tests GameSession's EventLog integration, while `test_engine_event_emission.py` tests that individual engines (ProductionEngine, FleetOrderProcessor, ConflictResolutionEngine) emit events. These are complementary, not duplicate. Keeping both is reasonable.
- **Lines:** N/A (recommend keeping both, just noting the relationship)

### 14. test_production_refactor.py (LEGACY VERIFICATION test)
- **Location:** `tests/unit/strategy/engine/test_production_refactor.py`
- **Category:** Partial scaffold / legacy verification
- **Reason:** The `test_legacy_cleanup` method (line 128-133) checks that old `_process_base_queue` and `_process_facility_queues` methods no longer exist on `ProductionEngine`. This is a one-time verification test from a refactoring effort. The dynamic consumption and carry-over tests (lines 27-126) test actual production behavior and are valuable. Consider removing only the `test_legacy_cleanup` test method.
- **Lines:** ~6 lines removable (just the `test_legacy_cleanup` method)

---

## Summary by Impact

| Category | Files | Lines Removable |
|----------|-------|-----------------|
| Clear duplicates (HIGH) | 5 | ~924 |
| Scaffold/trivial (MEDIUM) | 3 | ~77 |
| Partial duplicates (MEDIUM) | 1 | ~383 |
| Misplaced tests (MEDIUM) | 2 | ~1,229 (relocate) |
| Repro tests (MEDIUM) | 1 | ~133 |
| Over-tested (LOW) | 1 | ~180 |
| Legacy checks (LOW) | 1 | ~6 |
| **Total removable** | **10** | **~1,703 lines** |
| **Total relocatable** | **2** | **~1,229 lines** |

## Notable Observations

1. **No dead imports found.** All `game.*` imports in the 154 test files resolve to existing modules. The codebase is well-maintained in this regard.

2. **No skipped or xfail tests.** Zero `@pytest.mark.skip` or `@pytest.mark.xfail` decorators were found across the entire strategy test suite.

3. **No save-game migration tests.** The save_game_service tests test save/load operations and error handling, but do not contain old format migration code. This aligns with the project policy that save files are disposable.

4. **Consistent duplicate pattern.** The duplicates follow a pattern: PROJ-87 (extraction) created root-level tests, then PROJ-119 (test coverage gaps) created more thorough versions in subdirectories without removing the originals. A cleanup pass consolidating these would eliminate ~900 lines of pure duplication.

5. **Scaffold test anti-pattern.** Several "_edge_cases" or "_errors" files contain only import/existence checks (3 tests, ~25 lines each). These appear to be TDD scaffolds that were created to establish the test file, but the actual edge case tests were either never written or were written elsewhere. They should be deleted.
