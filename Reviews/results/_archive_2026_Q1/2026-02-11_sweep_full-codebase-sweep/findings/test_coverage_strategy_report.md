# Test Coverage Gaps Sweep: Strategy

## Summary
- **Shard:** Strategy (`game/strategy/` and all subdirectories)
- **Production Files Scanned:** 90 (excluding `__init__.py` files)
- **Test Files Cross-Referenced:** 120+ (unit + integration)
- **Total Issues Found:** 24
- **Critical:** 3 | **Major:** 10 | **Minor:** 8 | **Info:** 3

## Findings

#### CRITICAL: planet_gen.py Has No Dedicated Unit Tests
**ID:** TCG-STR-001
**Location:** `game/strategy/data/planet_gen.py` (production) / no corresponding test file
**Issue:** The `planet_gen.py` module, which handles procedural planet generation including surface conditions, atmosphere composition, resource distribution, and classification, has no dedicated unit test file. Planet generation is referenced tangentially in `tests/unit/strategy/data/test_planet_classification_logic.py` and `tests/integration/strategy/test_planet_physics.py`, but there are no direct tests for the generation functions themselves.
**Impact:** Planet generation is a core game mechanic that feeds into habitability, resource production, and colony viability. Bugs in generation logic (e.g., generating impossible surface conditions, negative resource quantities, or invalid atmosphere compositions) would cascade through the entire strategy layer and go undetected.
**Recommendation:** Create `tests/unit/strategy/data/test_planet_gen.py` with tests covering: generation of each planet type, resource distribution ranges, atmosphere composition validity, surface condition boundaries (temperature, pressure, gravity), and edge cases like zero-radius or max-radius orbits.
**Effort:** Complex

#### CRITICAL: FleetOrderProcessor Transfer Logic Has Thin Coverage
**ID:** TCG-STR-002
**Location:** `game/strategy/engine/fleet_order_processor.py` lines 246-472 / `tests/unit/strategy/engine/test_transfer_order.py`
**Issue:** The `process_transfer()`, `_execute_load()`, `_execute_unload()`, and `_transfer_founding_population()` methods in FleetOrderProcessor handle critical cargo and population transfer operations. While `test_transfer_order.py` exists, the following paths are untested: (1) species-specific loading (`species_id` parameter in `_execute_load`), (2) creating new SpeciesPopulation entries during unload when species doesn't exist on planet, (3) the fallback `try/except` blocks in `_transfer_founding_population` for mock compatibility, (4) edge case where `passengers` is not an int, (5) the `founding_pop == 0 and has_race_config` path for minimum seed population.
**Impact:** Population transfer is a core gameplay mechanic (colonization, population management). Untested edge cases in species handling could lead to population duplication, loss, or incorrect species assignments that would be very difficult to diagnose.
**Recommendation:** Add tests for: species-specific load with `species_id`, unload creating new SpeciesPopulation on planet, founding population minimum seed (100K) when no passengers but race_config exists, and negative/zero amount handling.
**Effort:** Medium

#### CRITICAL: GameSession.handle_command() Dispatch Has No Direct Unit Tests
**ID:** TCG-STR-003
**Location:** `game/strategy/engine/game_session.py` / `tests/unit/strategy/test_game_session.py`
**Issue:** The `GameSession.handle_command()` method is the central command dispatch point for ALL player actions. While individual command handlers have tests (`test_command_handlers.py`, `test_superweapon_command_handlers.py`), the `handle_command()` method itself -- which routes commands through the `CommandHandlerRegistry` -- lacks dedicated tests verifying: (1) unknown command type handling, (2) error propagation from handlers, (3) the complete command dispatch lifecycle from GameSession through registry to handler. The existing `test_game_session.py` tests session creation and fleet lookup but not command dispatch.
**Impact:** If command routing breaks (e.g., a handler isn't registered, or the registry dispatch returns unexpected results), all player commands would fail silently or with cryptic errors.
**Recommendation:** Add tests in `test_game_session.py` for `handle_command()` covering: successful dispatch of each registered command type, error result for unregistered command, and proper ValidationResult propagation.
**Effort:** Medium

#### MAJOR: FleetBattleAdapter Has Minimal Test Coverage
**ID:** TCG-STR-004
**Location:** `game/strategy/data/fleet_battle_adapter.py` / `tests/unit/strategy/test_fleet_battle_adapter.py`
**Issue:** `FleetBattleAdapter` bridges the strategy-simulation boundary for combat. While a test file exists, `to_battle_ships()` needs tests for: (1) ships that are not combat-capable being skipped, (2) formation position assignment when positions list is shorter than ship count, (3) `update_from_battle_results()` correctly removing destroyed ships and updating survivors, (4) the `_default_formation_positions()` method for team 0 vs team 1 positioning, (5) empty fleet edge case.
**Impact:** This adapter converts fleet data for battles. Incorrect conversion could lead to wrong ship counts, positions, or stats in combat, or post-battle state corruption (destroyed ships remaining, alive ships disappearing).
**Recommendation:** Expand `test_fleet_battle_adapter.py` with tests for non-combat-capable ship filtering, position overflow handling, battle result reconciliation (survivors vs destroyed), and empty fleet handling.
**Effort:** Medium

#### MAJOR: FleetResourceAggregator Lacks Atomic Operation Tests
**ID:** TCG-STR-005
**Location:** `game/strategy/data/fleet_resource_aggregator.py` / `tests/unit/strategy/test_fleet_resource_aggregator.py`
**Issue:** `FleetResourceAggregator.consume_movement_resources()` and `consume_warp_resources()` claim to be atomic (no resources consumed if any ship lacks sufficient resources). However, the atomicity guarantee is not verified in tests. Additionally, `fuel_endurance()`, `warp_jumps_remaining()`, and `get_capability_summary()` need edge-case testing for: (1) fleets with mixed fuel-consuming and non-fuel-consuming ships, (2) division-by-zero when cost_per_hex is exactly 0, (3) the `-1` return for unlimited endurance.
**Impact:** Non-atomic resource consumption could leave fleets in inconsistent states where some ships have resources consumed and others don't, causing movement desync during gameplay.
**Recommendation:** Add tests verifying: atomicity (no partial consumption on failure), mixed ship types (some with fuel, some without), zero-cost edge cases, and unlimited endurance return value.
**Effort:** Medium

#### MAJOR: QuickstartBuilder.spawn_initial_complexes() Not Tested
**ID:** TCG-STR-006
**Location:** `game/strategy/quickstart_builder.py` lines 256-299 / `tests/unit/strategy/test_quickstart_builder.py`
**Issue:** While `build_1p_config()` and `build_2p_config()` have test coverage, the `spawn_initial_complexes()` method and `copy_quickstart_designs()` method have no unit tests. These methods handle file I/O (copying design files) and game state modification (spawning facilities on home planets). `spawn_initial_complexes()` iterates empires, loads design data, and creates PlanetaryFacility objects.
**Impact:** Broken quickstart facility spawning would cause new games to start without essential infrastructure (shipyards, resource harvesters), making the game unplayable from quickstart.
**Recommendation:** Add unit tests for `spawn_initial_complexes()` with mocked DesignLibrary and GameSession, and for `copy_quickstart_designs()` with temp directories. Test error handling for missing design files and empires without colonies.
**Effort:** Medium

#### MAJOR: Superweapon Command Handlers Missing Error Path Tests
**ID:** TCG-STR-007
**Location:** `game/strategy/engine/superweapon_command_handlers.py` / `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Issue:** The 11 superweapon command handlers (6 direct + 5 mission) each follow a resolve-validate-apply pattern. The existing tests cover happy paths but lack: (1) fleet-not-found error paths for mission handlers, (2) planet-not-found error paths for ImplodePlanetMissionCommandHandler, (3) no-path-found scenarios for all mission handlers, (4) validation failure propagation (when SuperweaponValidator returns invalid).
**Impact:** Without error path tests, validation failures in superweapon commands could result in orders being created despite invalid state, leading to game crashes during turn processing.
**Recommendation:** For each mission handler, add tests for: fleet not found, target not found, path not found, and validator rejection.
**Effort:** Medium

#### MAJOR: DesignMetadata.from_design_file() and from_ship() Untested
**ID:** TCG-STR-008
**Location:** `game/strategy/data/design_metadata.py` / `tests/unit/strategy/test_design_metadata.py`
**Issue:** While `to_dict()`/`from_dict()` serialization is tested, the `from_design_file()` class method (which reads actual files and parses component data) and `from_ship()` (which extracts metadata from Ship objects) lack tests. These methods contain combat power calculation logic (`_calculate_combat_power`, `_calculate_combat_power_from_ship`) and resource cost aggregation (`_calculate_resource_cost`, `_calculate_resource_cost_from_ship`) that have no test coverage.
**Impact:** Combat power and resource cost calculations are used for sorting, filtering, and displaying designs in the UI. Incorrect values would mislead players about ship capabilities and build costs.
**Recommendation:** Add tests for: `_calculate_combat_power` with weapon/armor components, `_calculate_resource_cost` with multi-layer designs, `from_ship()` with mock Ship objects, and `embed_in_ship_data()` round-trip.
**Effort:** Medium

#### MAJOR: ColonizeValidator Chain Validation Not Thoroughly Tested
**ID:** TCG-STR-009
**Location:** `game/strategy/validation/colonize_validator.py` / `tests/unit/strategy/validation/test_colonize_validator.py`
**Issue:** The chain validation logic (PROJ-55) that prevents over-committing colony pods needs more thorough testing: (1) `get_committed_colony_pods()` counting from order queue, (2) the COLONY_POD_EXHAUSTED error code when all pods are committed, (3) interaction between `get_available_colony_pods()` and `get_committed_colony_pods()` when multiple COLONIZE orders exist for same planet type.
**Impact:** Without proper chain validation, players could queue more colonize orders than they have colony pods for, leading to failed colonization attempts and wasted turns.
**Recommendation:** Add tests for: fleet with 1 pod and 2 queued colonize orders (should fail second), fleet with mixed pod types, and committed pod counting from order queue.
**Effort:** Simple

#### MAJOR: EmpireEconomyCalculator Registry Fallback Path Has Edge Cases
**ID:** TCG-STR-010
**Location:** `game/strategy/engine/empire_economy_calculator.py` / `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Issue:** While the test file is thorough for basic scenarios, these edge cases are untested: (1) component entry as a plain string (not dict) with registry lookup, (2) registry returning None for unknown component ID, (3) component with abilities that are NOT ResourceHarvester (should be skipped), (4) negative quality values, (5) multiple harvesters on same colony for same resource type (aggregation).
**Impact:** The economy calculator drives the entire resource display in the UI. Edge cases in component lookup could cause incorrect production/maintenance displays, misleading player economic decisions.
**Recommendation:** Add tests for: string-format component entries, registry miss (unknown comp_id), non-harvester abilities being skipped, and multiple harvesters aggregating correctly.
**Effort:** Simple

#### MAJOR: TurnEngine._process_tick() Integration Not Tested End-to-End
**ID:** TCG-STR-011
**Location:** `game/strategy/engine/turn_engine.py` / `tests/unit/strategy/turn_engine/`
**Issue:** While individual phases of `_process_tick()` are tested via dependency injection (the sub-engines have their own tests), the 8-phase tick orchestration order is not verified. There are no tests confirming: (1) per-turn consumption happens before fuel generation, (2) fuel generation happens before fleet resupply, (3) construction tick happens before instant orders, (4) instant orders happen before movement, (5) movement happens before combat. Phase ordering bugs would be extremely subtle.
**Impact:** If tick phases execute in wrong order, resources could be consumed before generation, or combat could resolve before movement completes, causing incorrect game state.
**Recommendation:** Add an integration test that injects spy/recording engines and verifies the exact call order across all 8 phases of `_process_tick()`.
**Effort:** Medium

#### MAJOR: FleetCapabilityCalculator.can_build_type() Complex Proximity Not Tested
**ID:** TCG-STR-012
**Location:** `game/strategy/data/fleet_capability_calculator.py` / `tests/unit/strategy/test_fleet_capability_calculator.py`
**Issue:** `can_build_type("complex", galaxy)` requires the fleet to be at the same hex as a planet, which requires a galaxy argument. This path is likely untested since it needs a real or mock galaxy with spatial index. Additionally, `has_ability()` and `ships_with_ability()` for arbitrary ability names need testing.
**Impact:** Complex construction is a key gameplay feature. If planet proximity validation fails, players could build complexes in empty space or be incorrectly prevented from building at valid planets.
**Recommendation:** Add tests for `can_build_type("complex")` with and without galaxy, with and without planet at hex. Test `has_ability()` and `ships_with_ability()` with mock registries.
**Effort:** Simple

#### MAJOR: ShipResourceManager Missing Boundary Tests
**ID:** TCG-STR-013
**Location:** `game/strategy/data/ship_resource_manager.py` / `tests/unit/strategy/test_ship_resource_manager.py`
**Issue:** `ShipResourceManager.consume_resource()` has explicit negative amount rejection (returns False for amount < 0), but this is likely untested. Additional untested paths: (1) consuming exactly the remaining amount (should succeed and leave 0), (2) consuming from a resource type not in resource_levels dict, (3) `resupply()` when max_val is 0 (should not increase), (4) `resupply()` when already at max capacity.
**Impact:** Resource consumption is called every tick for fuel/energy. Edge cases in consumption could cause negative resources or incorrect movement blocking.
**Recommendation:** Add boundary tests for: negative consumption, exact-amount consumption, unknown resource type, and resupply at/above capacity.
**Effort:** Simple

#### MINOR: ShipDisplayFormatter.get_resource_percentage() Division by Zero
**ID:** TCG-STR-014
**Location:** `game/strategy/data/ship_display_formatter.py` line 108 / `tests/unit/strategy/test_ship_display_formatter.py`
**Issue:** `get_resource_percentage()` handles `max_val <= 0` by returning 0.0, but this edge case (resource with zero max capacity) needs a test to prevent regression. The `get_hp_display()` method when `current_hp is None` also needs verification.
**Impact:** Low -- display-only code, but division by zero in production would crash the UI.
**Recommendation:** Add edge case tests for: zero-capacity resource percentage, None current_hp display, and N/A resource display.
**Effort:** Simple

#### MINOR: ShipCargoManager.load_cargo() and unload_cargo() Zero/Negative Amount
**ID:** TCG-STR-015
**Location:** `game/strategy/data/ship_cargo_manager.py` / `tests/unit/strategy/test_ship_cargo_manager.py`
**Issue:** Both `load_cargo()` and `unload_cargo()` handle `amount <= 0` by returning 0, and `unload_cargo()` cleans up zero entries from the dict. These boundary behaviors need explicit tests to prevent regression.
**Impact:** Cargo operations affect colonization (passenger loading). Incorrect zero-handling could prevent or corrupt transfers.
**Recommendation:** Add tests for: zero amount load/unload, negative amount load/unload, and dict cleanup verification after full unload.
**Effort:** Simple

#### MINOR: SuperweaponOrderProcessor._find_system_at_location() Edge Cases
**ID:** TCG-STR-016
**Location:** `game/strategy/engine/superweapon_order_processor.py` lines 47-78
**Issue:** The `_find_system_at_location()` method searches galaxy systems by checking direct location, planet offsets, star offsets, and warp point offsets. While it is exercised indirectly through superweapon tests, there are no unit tests for the method itself, especially for: (1) fleet at a planet location (not system center), (2) fleet at a warp point location, (3) fleet at a star location, (4) fleet in deep space (no system).
**Impact:** If system lookup fails, superweapon orders would fail with "Fleet not at a star system" even when the fleet is at a planet within a system.
**Recommendation:** Add focused unit tests for `_find_system_at_location()` with each lookup path.
**Effort:** Simple

#### MINOR: EventTypes Enum and EventLog Serialization Completeness
**ID:** TCG-STR-017
**Location:** `game/strategy/events/event_types.py` / `tests/unit/strategy/events/test_event_types.py`
**Issue:** While event_types has a test file, new event types added for superweapons (PLANET_DESTROYED, STAR_DESTROYED, WARP_POINT_OPENED, WARP_POINT_CLOSED, DYSON_SPHERE_CREATED, SHIPS_SELF_DESTRUCTED) should have serialization/deserialization round-trip tests to ensure they survive save/load cycles.
**Impact:** If new event types fail serialization, turn events would be lost after save/load, losing important game history.
**Recommendation:** Add round-trip serialization tests for all superweapon event types.
**Effort:** Simple

#### MINOR: Facade DTO from_* Methods Missing Edge Case Tests
**ID:** TCG-STR-018
**Location:** `game/strategy/facade/dto/` (empire_dto.py, fleet_dto.py, planet_dto.py, system_dto.py) / `tests/unit/strategy/facade/`
**Issue:** While DTO creation from domain objects is tested in integration tests, the `from_fleet()`, `from_planet()`, `from_star_system()`, and `from_empire()` class methods lack unit tests for edge cases: (1) fleet with no ships, (2) planet with no populations, (3) system with no stars, (4) empire with no colonies or fleets.
**Impact:** DTOs are the UI's only view of game state. Missing edge case handling could cause UI crashes when displaying empty/minimal game objects.
**Recommendation:** Add unit tests for each DTO's `from_*` method with minimal/empty domain objects.
**Effort:** Simple

#### MINOR: RegionClassifier Has No Test for Ring/Bar Galaxy Types
**ID:** TCG-STR-019
**Location:** `game/strategy/generation/region_classifier.py` / `tests/unit/strategy/generation/test_region_classifier.py`
**Issue:** RegionClassifier supports spiral, cluster, ring, and bar galaxy types. The `_build_regions()` method creates different region lists for each type, but the ring and bar paths may not be tested since they are less common galaxy layouts.
**Impact:** Low -- these galaxy types may not be actively used, but if they are, incorrect classification would affect naming and region display.
**Recommendation:** Add tests for ring and bar galaxy type classification and region building.
**Effort:** Simple

#### MINOR: placement_strategies.py DensityBasedPlacementStrategy Boundary Behavior
**ID:** TCG-STR-020
**Location:** `game/strategy/generation/placement_strategies.py` / `tests/unit/strategy/generation/test_placement_strategies.py`
**Issue:** `DensityBasedPlacementStrategy` uses `min(radius, self._density_map.radius)` for effective radius. Edge cases: (1) density map radius smaller than galaxy radius, (2) all attempts failing (max_attempts reached, returns None), (3) density_threshold of 0.01 rejecting very low density areas. These boundary behaviors need explicit tests.
**Impact:** Galaxy generation could produce fewer systems than expected if density strategy rejects too many locations, or could place systems outside the intended density zones.
**Recommendation:** Add tests for: mismatched radii, exhausted attempts, and threshold rejection behavior.
**Effort:** Simple

#### MINOR: GameConfig and PlayerConfig Missing Validation Tests
**ID:** TCG-STR-021
**Location:** `game/strategy/engine/game_config.py` / `tests/unit/strategy/test_game_config.py`
**Issue:** `GameConfig` and `PlayerConfig` dataclasses are used to configure new games. While basic instantiation is tested, validation of invalid inputs is not: (1) system_count = 0, (2) negative galaxy_radius, (3) empty players list, (4) duplicate player names, (5) invalid galaxy_type string.
**Impact:** Invalid game configurations could cause crashes during galaxy initialization that are hard to trace back to the config.
**Recommendation:** Add tests for invalid config values and ensure either validation rejects them or the system handles them gracefully.
**Effort:** Simple

#### INFO: Test Organization -- Some Test Files in Non-Standard Locations
**ID:** TCG-STR-022
**Location:** Various test files
**Issue:** Some strategy test files are at the top level of `tests/unit/strategy/` (e.g., `test_fleet_speed_calculator.py`, `test_ship_cargo_manager.py`, `test_fleet_battle_adapter.py`, `test_component_inspector.py`) rather than in subdirectories matching the production code structure (`tests/unit/strategy/services/`, `tests/unit/strategy/data/`). This inconsistency makes it harder to verify coverage by directory comparison.
**Impact:** No functional impact, but increases cognitive load when auditing test coverage.
**Recommendation:** Consider reorganizing test files to mirror the production code directory structure.
**Effort:** Simple

#### INFO: Validation Module Has No __init__.py Test Package
**ID:** TCG-STR-023
**Location:** `tests/unit/strategy/validation/`
**Issue:** The `tests/unit/strategy/validation/` directory exists but has only `__init__.py` -- the actual validator test files (`test_colonize_validator.py`, `test_transfer_validator.py`, `test_superweapon_validator.py`) exist but would benefit from being listed as a proper test package with conftest shared fixtures.
**Impact:** No functional impact, but shared fixtures (mock galaxy, mock fleet, mock planet) are duplicated across validator tests.
**Recommendation:** Create a shared `conftest.py` in `tests/unit/strategy/validation/` with common fixtures.
**Effort:** Simple

#### INFO: Heavy Mock Usage in FleetOrderProcessor and SuperweaponOrderProcessor Tests
**ID:** TCG-STR-024
**Location:** `tests/unit/strategy/test_fleet_order_processor.py`, `tests/unit/strategy/engine/test_superweapon_order_processor.py`
**Issue:** Both test files use MagicMock extensively for Fleet, Galaxy, Empire, and Planet objects. While this provides isolation, it means the tests don't verify that the real Fleet/Galaxy APIs are called correctly (e.g., `fleet.pop_order()` signature, `galaxy.unregister_planet()` behavior). Any change to these APIs would not be caught by these tests.
**Impact:** API changes in Fleet or Galaxy could break order processing without test detection.
**Recommendation:** Consider adding a small number of integration tests that use real (not mocked) Fleet and Galaxy objects with the order processors, complementing the existing mock-based unit tests.
**Effort:** Medium

## Top 5 Priority Issues

1. **TCG-STR-001 (CRITICAL):** `planet_gen.py` has no dedicated unit tests -- planet generation logic feeding into habitability, resources, and classification is completely untested at the unit level.

2. **TCG-STR-002 (CRITICAL):** FleetOrderProcessor transfer logic (species-specific loading, founding population seeding, unload-to-new-species) has significant untested paths that handle critical population management mechanics.

3. **TCG-STR-003 (CRITICAL):** GameSession.handle_command() central dispatch -- the single entry point for all player commands -- lacks direct unit tests for routing, error handling, and result propagation.

4. **TCG-STR-011 (MAJOR):** TurnEngine tick phase ordering (8 phases per tick, 100 ticks per turn) is untested. Phase ordering bugs would be extremely subtle and could cause resource/movement/combat desync.

5. **TCG-STR-004 (MAJOR):** FleetBattleAdapter, the strategy-simulation bridge for combat, has minimal test coverage for ship filtering, position assignment, and post-battle state reconciliation.
