# Test Coverage Gaps Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Production Files Scanned:** 94
- **Test Files Cross-Referenced:** 125+
- **Total Issues Found:** 23
- **Critical:** 4 | **Major:** 10 | **Minor:** 7 | **Info:** 2

## Findings

#### CRITICAL: FleetNavigationService Missing Comprehensive Unit Tests
**ID:** TCG-STR-001
**Location:** `game/strategy/services/fleet_navigation_service.py` (production) / `tests/unit/strategy/fleet_navigation/` (test gap)
**Issue:** The FleetNavigationService class (468 lines) has tests for individual navigation components (projection, data structures, destination path) but lacks comprehensive unit tests for the service class itself. Key methods like `compute_next_step()`, `calculate_fleet_next_hex()`, and path recalculation logic (`_needs_path_recalculation`) have no direct tests - only indirect coverage through integration tests. The service is the single source of truth for fleet navigation and is critical for both UI projection and turn execution.
**Impact:** Bugs in navigation calculation could cause fleet path mismatches between UI and execution, incorrect order processing, or fleet stranding.
**Recommendation:** Create `tests/unit/strategy/services/test_fleet_navigation_service.py` with tests for: NavigationState.from_fleet(), compute_next_step() with various order types, path recalculation conditions, and error handling for invalid MOVE_TO_FLEET targets.
**Effort:** Medium

#### CRITICAL: Command Handler Coverage Incomplete
**ID:** TCG-STR-002
**Location:** `game/strategy/engine/command_handlers.py` (production) / `tests/unit/strategy/test_command_handlers.py` (partial tests)
**Issue:** While test_command_handlers.py exists, review shows it focuses on ColonizeCommandHandler and MoveCommandHandler. Missing test coverage for: InterceptCommandHandler, JoinCommandHandler, ColonizeMissionCommandHandler, ClearOrdersCommandHandler, and TransferCommandHandler. These handlers execute critical game state mutations.
**Impact:** Untested command handlers may silently fail or corrupt game state when processing player orders.
**Recommendation:** Add test classes for each command handler: TestInterceptCommandHandler, TestJoinCommandHandler, TestColonizeMissionCommandHandler, TestClearOrdersCommandHandler, TestTransferCommandHandler. Include validation failure paths and edge cases.
**Effort:** Medium

#### CRITICAL: Superweapon Order Processor Missing Error Path Tests
**ID:** TCG-STR-003
**Location:** `game/strategy/engine/superweapon_order_processor.py` (production) / `tests/unit/strategy/engine/test_superweapon_order_processor.py` (test gap)
**Issue:** The superweapon tests exist but inspection shows they focus on happy-path execution. Missing tests for: validation failures (wrong ship at wrong location), partial fleet destruction during stellerate, invalid targets, and cooldown enforcement. Superweapon effects are destructive and irreversible.
**Impact:** Superweapons could execute incorrectly, destroying wrong planets/stars or bypassing validation.
**Recommendation:** Add negative test cases: test_implode_planet_no_superweapon_ship(), test_stellerate_wrong_target_type(), test_superweapon_validation_failure_paths(), test_cooldown_prevents_execution().
**Effort:** Medium

#### CRITICAL: Production Engine Tick Consumption Edge Cases
**ID:** TCG-STR-004
**Location:** `game/strategy/engine/production_engine.py` (production) / `tests/unit/strategy/production_engine/test_tick_consumption.py` (partial)
**Issue:** The test_tick_consumption.py file exists but lacks edge case tests for: queue exhaustion mid-tick, multiple items completing same tick, resource depletion preventing completion, and interactions with fleet production queues. The production engine handles complex multi-tick processing.
**Impact:** Production could complete incorrectly, skip items, or double-spawn completed items under edge conditions.
**Recommendation:** Add tests: test_multiple_completions_same_tick(), test_resource_exhaustion_mid_queue(), test_queue_empty_mid_tick(), test_fleet_and_colony_production_interaction().
**Effort:** Complex

#### MAJOR: No Unit Tests for services/ship_stats_calculator.py Methods
**ID:** TCG-STR-005
**Location:** `game/strategy/services/ship_stats_calculator.py` (production) / `tests/unit/strategy/ship_stats/` (test gap)
**Issue:** While ship_stats tests exist, they test at ShipInstance level. ShipStatsCalculator has static methods like `_get_current_hp()`, `_evaluate_value()`, `_get_ability_list()` that handle edge cases (indexed component IDs, formula strings, null values) but lack direct unit tests. The `has_warp_capability()` method (line 488-537) is particularly complex with multiple conditions.
**Impact:** Edge cases in stat calculation could cause incorrect damage effectiveness, warp capability checks, or resource storage calculations.
**Recommendation:** Create `tests/unit/strategy/services/test_ship_stats_calculator_edge_cases.py` with tests for formula evaluation, indexed HP lookups, and has_warp_capability edge conditions.
**Effort:** Simple

#### MAJOR: FleetCapabilityCalculator.can_build_type() Galaxy Interaction
**ID:** TCG-STR-006
**Location:** `game/strategy/data/fleet_capability_calculator.py:can_build_type()` (production) / `tests/unit/strategy/test_fleet_capability_calculator.py` (test gap)
**Issue:** The `can_build_type()` method has logic for complex building that requires galaxy.get_planets_at_global_hex() but tests don't verify this interaction. The galaxy=None case returns False for complex builds but is not explicitly tested.
**Impact:** Fleet spaceyard could incorrectly allow/deny complex construction at planetary locations.
**Recommendation:** Add tests: test_can_build_complex_with_planet_present(), test_can_build_complex_no_planet(), test_can_build_complex_no_galaxy_arg().
**Effort:** Simple

#### MAJOR: EmpireEconomyCalculator Missing Integration Tests
**ID:** TCG-STR-007
**Location:** `game/strategy/engine/empire_economy_calculator.py` (production) / `tests/unit/strategy/engine/test_empire_economy_calculator.py` (test gap)
**Issue:** This important calculator for empire-wide production and maintenance aggregation has only basic unit tests. Missing tests for: multiple colonies with facilities, interaction between colony and ship maintenance, resource pool and max_storage snapshot accuracy.
**Impact:** Economy reports could show incorrect production/expense totals affecting player decision-making.
**Recommendation:** Create integration-level tests with realistic empire data including multiple colonies, facilities with harvesters, and ships with maintenance costs.
**Effort:** Medium

#### MAJOR: ConflictResolutionEngine Battle Resolution Paths
**ID:** TCG-STR-008
**Location:** `game/strategy/engine/conflict_resolution_engine.py` (production) / `tests/unit/strategy/conflict_resolution/` (partial)
**Issue:** Conflict resolution tests cover core mechanics but miss: multi-empire conflicts (3+ parties), retreat/surrender scenarios, and post-battle state cleanup. The engine integrates with BattleResolver interface.
**Impact:** Complex multi-party battles could resolve incorrectly or leave orphaned game state.
**Recommendation:** Add tests: test_three_empire_conflict(), test_battle_with_retreat(), test_post_battle_fleet_cleanup().
**Effort:** Medium

#### MAJOR: GameSession Missing Order Queueing Tests
**ID:** TCG-STR-009
**Location:** `game/strategy/engine/game_session.py` (production) / `tests/unit/strategy/test_game_session.py` (partial)
**Issue:** GameSession tests exist but don't verify order queueing behavior: multiple orders same fleet, order replacement vs append, queue size limits. The session facade CQRS pattern expects orders to queue properly.
**Impact:** Player orders could be lost, overwritten, or exceed limits without proper feedback.
**Recommendation:** Add tests: test_queue_multiple_orders_same_fleet(), test_order_replacement_behavior(), test_order_queue_capacity().
**Effort:** Simple

#### MAJOR: Pathfinding Edge Cases Not Covered
**ID:** TCG-STR-010
**Location:** `game/strategy/data/pathfinding.py` (production) / `tests/unit/strategy/pathfinding/` (partial)
**Issue:** Pathfinding has good coverage but misses: very long paths (performance), paths with many warp points, recalculation during moving target intercept, and paths that become invalid mid-turn (blocked by new system).
**Impact:** Pathfinding could timeout, produce suboptimal paths, or fail silently in edge cases.
**Recommendation:** Add tests: test_very_long_path_performance(), test_path_with_multiple_warp_jumps(), test_intercept_moving_target_recalculation().
**Effort:** Medium

#### MAJOR: GameInitializer._setup_initial_scenario Edge Cases
**ID:** TCG-STR-011
**Location:** `game/strategy/engine/game_initializer.py:_setup_initial_scenario()` (production) / `tests/unit/strategy/engine/test_game_initializer.py` (partial)
**Issue:** Tests don't cover: 4+ player empire distribution, system with no planets for homeworld, race_config=None fallback path, and _adjust_homeworld_to_race with invalid planet_type.
**Impact:** Game initialization could fail or produce degenerate starting conditions for edge-case configurations.
**Recommendation:** Add tests: test_five_player_distribution(), test_system_no_planets_for_homeworld(), test_homeworld_adjustment_invalid_type().
**Effort:** Medium

#### MAJOR: SaveGameService Round-Trip Edge Cases
**ID:** TCG-STR-012
**Location:** `game/strategy/systems/save_game_service.py` (production) / `tests/unit/strategy/save_game_service/` (partial)
**Issue:** Save/load tests exist but don't verify round-trip integrity for: fleet orders with object references (target_fleet), component damage state, toggle states, and event log. Data fidelity after save/load is critical.
**Impact:** Saved games could load with missing or corrupted state.
**Recommendation:** Add round-trip tests: test_save_load_fleet_orders_with_fleet_target(), test_save_load_component_damage_state(), test_save_load_event_log_integrity().
**Effort:** Medium

#### MAJOR: Fleet.merge_with() Tests Incomplete
**ID:** TCG-STR-013
**Location:** `game/strategy/data/fleet.py:merge_with()` (production) / `tests/unit/strategy/fleet/` (partial)
**Issue:** Fleet merge tests don't verify: merging fleets with construction queues, cargo transfer during merge, resource level aggregation, and serial number preservation of merged ships.
**Impact:** Fleet merging could lose ships, cargo, or construction progress.
**Recommendation:** Add tests: test_merge_preserves_construction_queue(), test_merge_aggregates_cargo(), test_merge_preserves_ship_serials().
**Effort:** Simple

#### MINOR: ResupplyEngine Partial Resupply Tests
**ID:** TCG-STR-014
**Location:** `game/strategy/engine/resupply_engine.py` (production) / `tests/unit/strategy/engine/test_resupply_engine.py` (test gap)
**Issue:** Resupply tests don't cover partial resupply when facility has insufficient fuel to fill entire fleet.
**Impact:** Minor - UI display could show incorrect fuel transfer amounts.
**Recommendation:** Add test: test_partial_resupply_insufficient_facility_fuel().
**Effort:** Simple

#### MINOR: RegionClassifier._classify_spiral Boundary Tests
**ID:** TCG-STR-015
**Location:** `game/strategy/generation/region_classifier.py` (production) / `tests/unit/strategy/generation/test_region_classifier.py` (partial)
**Issue:** Spiral arm classification tests don't verify behavior at exact arm boundaries or with high arm_count (8+ arms).
**Impact:** Minor cosmetic - system region assignment may be inconsistent at boundaries.
**Recommendation:** Add tests: test_classify_at_exact_arm_boundary(), test_classify_eight_arm_spiral().
**Effort:** Simple

#### MINOR: QuickstartBuilder.spawn_initial_complexes Failure Path
**ID:** TCG-STR-016
**Location:** `game/strategy/quickstart_builder.py:spawn_initial_complexes()` (production) / `tests/unit/strategy/test_quickstart_builder.py` (test gap)
**Issue:** Tests don't verify behavior when design loading fails for some but not all complexes.
**Impact:** Minor - quickstart could partially succeed leaving incomplete starting setup.
**Recommendation:** Add test: test_spawn_initial_complexes_partial_design_failure().
**Effort:** Simple

#### MINOR: DesignMetadata.from_design_file with Missing Fields
**ID:** TCG-STR-017
**Location:** `game/strategy/data/design_metadata.py:from_design_file()` (production) / `tests/unit/strategy/test_design_metadata.py` (partial)
**Issue:** from_design_file() has default fallbacks for missing fields but tests don't verify all fallback paths.
**Impact:** Minor - metadata could have unexpected defaults for malformed design files.
**Recommendation:** Add test: test_from_design_file_missing_all_optional_fields().
**Effort:** Simple

#### MINOR: ShipResourceManager Edge Cases
**ID:** TCG-STR-018
**Location:** `game/strategy/data/ship_resource_manager.py` (production) / No dedicated test file
**Issue:** ShipResourceManager class has no dedicated test file. Tested indirectly via ShipInstance tests.
**Impact:** Minor - resource management edge cases may not be covered.
**Recommendation:** Create `tests/unit/strategy/data/test_ship_resource_manager.py` with direct tests.
**Effort:** Simple

#### MINOR: Planet Population Model Edge Cases
**ID:** TCG-STR-019
**Location:** `game/strategy/data/planet.py:SpeciesPopulation` (production) / `tests/unit/strategy/data/test_population_model.py` (partial)
**Issue:** Population model tests exist but don't verify: negative population handling, very large population numbers, and multi-species population interactions.
**Impact:** Minor - edge case population scenarios could behave unexpectedly.
**Recommendation:** Add tests: test_population_cannot_go_negative(), test_very_large_population(), test_multi_species_happiness_interaction().
**Effort:** Simple

#### MINOR: FleetDTO Build Validation
**ID:** TCG-STR-020
**Location:** `game/strategy/facade/dto/fleet_dto.py` (production) / `tests/unit/strategy/facade/test_fleet_dto_build.py` (partial)
**Issue:** FleetInfo.from_fleet() tests don't verify handling of fleets with no ships or fleets with None location.
**Impact:** Minor - UI could crash on degenerate fleet objects.
**Recommendation:** Add tests: test_fleet_dto_from_empty_fleet(), test_fleet_dto_from_fleet_none_location().
**Effort:** Simple

#### INFO: Component Inspector Good Coverage
**ID:** TCG-STR-021
**Location:** `game/strategy/services/component_inspector.py` (production) / `tests/unit/strategy/test_component_inspector.py` (tests)
**Issue:** ComponentInspector has excellent test coverage including edge cases for None components, missing abilities, and different data formats.
**Impact:** None - informational.
**Recommendation:** None - this module is a good example of thorough testing.
**Effort:** N/A

#### INFO: Habitability Formula Comprehensive Tests
**ID:** TCG-STR-022
**Location:** `game/strategy/formulas/habitability.py` (production) / `tests/unit/strategy/formulas/test_habitability.py` (tests)
**Issue:** Habitability scoring has excellent test coverage including edge cases (zero tolerance, extreme values), boundary conditions, and integration tests with real Planet/RaceConfig objects.
**Impact:** None - informational.
**Recommendation:** None - this module demonstrates best practices for formula testing.
**Effort:** N/A

#### MAJOR: No Tests for strategy/events/event_types.py Enums
**ID:** TCG-STR-023
**Location:** `game/strategy/events/event_types.py` (production) / No dedicated tests
**Issue:** EventType and EventCategory enums define critical event classification but have no tests verifying enum completeness, serialization, or uniqueness. Event log depends on these.
**Impact:** Event type changes could break serialization or filtering without detection.
**Recommendation:** Create `tests/unit/strategy/events/test_event_types.py` with enum completeness tests and serialization round-trip tests.
**Effort:** Simple

## Top 5 Priority Issues

1. **TCG-STR-001 (CRITICAL): FleetNavigationService Missing Comprehensive Unit Tests** - The single source of truth for fleet navigation lacks direct tests for its core methods. Risk of UI/execution mismatch is high.

2. **TCG-STR-002 (CRITICAL): Command Handler Coverage Incomplete** - 5 of 8 command handlers have no direct tests. These execute player orders and are critical for game state integrity.

3. **TCG-STR-004 (CRITICAL): Production Engine Tick Consumption Edge Cases** - Complex multi-tick processing lacks edge case tests. Production bugs are highly visible to players.

4. **TCG-STR-003 (CRITICAL): Superweapon Order Processor Missing Error Path Tests** - Destructive, irreversible game actions need thorough validation testing.

5. **TCG-STR-012 (MAJOR): SaveGameService Round-Trip Edge Cases** - Save/load data fidelity is critical for game persistence. Missing tests for object references and complex state.
