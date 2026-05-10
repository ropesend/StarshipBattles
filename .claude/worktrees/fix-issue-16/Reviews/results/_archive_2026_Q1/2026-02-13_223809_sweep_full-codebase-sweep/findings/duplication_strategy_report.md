# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 95
- **Total Issues Found:** 12
- **Critical:** 1 | **Major:** 4 | **Minor:** 5 | **Info:** 2

## Findings

#### CRITICAL: Duplicate Component Ability Extraction Pattern
**ID:** DUP-STR-001
**Location:** `game/strategy/engine/harvesting_engine.py:30-75, 169-211` AND `game/strategy/data/fleet_capability_calculator.py:14-18, 31-44, 172-186`
**Issue:** The pattern for extracting abilities from component entries (inline dict abilities vs registry lookup) is duplicated across multiple files. `HarvestingEngine` has `get_harvester_info()`, `get_harvester_from_registry()`, `_get_storage_info()`, `_get_storage_from_registry()`. `FleetCapabilityCalculator` uses `ship_has_ability()` via `component_inspector`. Each uses slightly different approaches to the same fundamental operation: "get ability X from a component entry that may be inline or require registry resolution."
**Impact:** High maintenance risk. When adding new ability types, each extraction pattern must be updated separately. Logic drift is likely - some methods handle edge cases others don't. The `_get_harvester_from_registry()` method wraps `get_harvester_from_registry()` which is redundant.
**Recommendation:** Create a unified `ComponentAbilityExtractor` service in `game/strategy/services/` with a single method: `get_ability(component_entry, ability_name, registries) -> Optional[dict]`. All ability lookups should use this single abstraction.
**Effort:** Medium

#### MAJOR: Duplicated "Find Nearest" System Patterns
**ID:** DUP-STR-002
**Location:** `game/strategy/data/pathfinding.py:107-139` AND `game/strategy/data/pathfinding.py:141-160`
**Issue:** `get_system_at_hex()` and `find_nearest_system()` share nearly identical iteration logic over `galaxy.systems.values()` with distance comparison. Both iterate all systems comparing `hex_distance()`.
**Impact:** Code duplication (~20 lines). If optimization is needed (spatial indexing), both would need updating.
**Recommendation:** Consolidate into a single `find_systems_near(galaxy, hex, max_distance=None) -> List[Tuple[StarSystem, int]]` function that returns sorted systems by distance. Both existing functions become thin wrappers.
**Effort:** Simple

#### MAJOR: Duplicated Star Generation Logic
**ID:** DUP-STR-003
**Location:** `game/strategy/data/stars.py:373-478` AND `game/strategy/data/stars.py:480-553`
**Issue:** `generate_from_blueprint()` and `_generate_random_stars()` contain substantial duplicated code for creating primary stars (~30 lines) and companion stars (~30 lines). The Star object creation, spectrum generation, location assignment, and companion iteration logic is nearly identical with minor variations for constraint handling.
**Impact:** ~60 lines of duplicate code. Bug fixes or changes to star generation logic must be applied twice.
**Recommendation:** Extract common star creation logic into helper methods:
- `_create_star(name, mass, location)` for Star object construction
- `_place_companions(primary, count, occupied_hexes)` for companion positioning
Both `generate_from_blueprint()` and `_generate_random_stars()` would call these helpers.
**Effort:** Medium

#### MAJOR: Ship Spawning Duplication in ProductionEngine
**ID:** DUP-STR-004
**Location:** `game/strategy/engine/production_engine.py:477-541` AND `game/strategy/engine/production_engine.py:603-657`
**Issue:** `_spawn_ship()` and `_spawn_fleet_ship()` have substantial overlap (~40 lines each):
- Both load design data via `DesignLibrary`
- Both create `ShipInstance.create()` with same parameters
- Both increment `times_built` counter
- Both log events with `log_event(EventType.SHIP_BUILT, ...)`
The main difference is where the ship ends up (new fleet vs existing fleet).
**Impact:** Any change to ship creation logic must be applied in two places. Risk of drift if one is updated but not the other.
**Recommendation:** Extract common ship creation logic into `_create_ship_instance(design_id, empire, save_path) -> ShipInstance`. The spawning methods become simpler: create instance, then either add to fleet or create new fleet.
**Effort:** Simple

#### MAJOR: Duplicated Complex Spawning Logic
**ID:** DUP-STR-005
**Location:** `game/strategy/engine/production_engine.py:434-475` AND `game/strategy/engine/production_engine.py:659-731`
**Issue:** `_spawn_complex()` and `_spawn_fleet_complex()` share ~30 lines of identical logic:
- Design data loading via `DesignLibrary`
- `PlanetaryFacility` creation with same parameters
- Appending to `planet.facilities`
- Logging via `log_event(EventType.COMPLEX_BUILT, ...)`
**Impact:** Same risks as DUP-STR-004. Complex creation changes require dual updates.
**Recommendation:** Extract common facility creation into `_create_facility(design_id, empire, save_path) -> PlanetaryFacility`. Spawning methods handle planet selection and logging.
**Effort:** Simple

#### MINOR: Resource Consumption Loop Pattern
**ID:** DUP-STR-006
**Location:** `game/strategy/data/fleet_resource_aggregator.py:65-97` AND `game/strategy/data/fleet_resource_aggregator.py:134-162`
**Issue:** `consume_movement_resources()` and `consume_warp_resources()` follow identical two-phase patterns:
1. Verify all ships have enough (atomic check)
2. Consume from all ships
The loop structure is nearly identical with different cost accessor methods.
**Impact:** ~15 lines duplicated per method. Low risk since both are stable.
**Recommendation:** Extract generic `_atomic_consume_fleet_resources(ships, cost_accessor, multiplier=1)` method.
**Effort:** Simple

#### MINOR: has_resources/consume Pattern in FleetResourceAggregator
**ID:** DUP-STR-007
**Location:** `game/strategy/data/fleet_resource_aggregator.py:47-63` AND `game/strategy/data/fleet_resource_aggregator.py:115-132`
**Issue:** `has_resources_for_movement()` and `has_resources_for_warp()` are nearly identical:
- Same iteration over combat-capable ships
- Same resource checking pattern
- Only differ in which cost accessor is used
**Impact:** ~12 lines duplicated. Low impact since these are simple checks.
**Recommendation:** Extract `_has_resources_for_operation(cost_accessor) -> bool` helper.
**Effort:** Simple

#### MINOR: Duplicate Fleet-Like Proxy Pattern
**ID:** DUP-STR-008
**Location:** `game/strategy/data/pathfinding.py:275-296` AND `game/strategy/services/fleet_navigation_service.py:173-177`
**Issue:** Both files create "fleet-like" objects for pathfinding:
- `pathfinding.py` has `_ChaserProxy` class with `can_use_warp()` method
- `fleet_navigation_service.py` creates anonymous `fleet_like` object with same pattern
Both exist solely to pass warp capability to `find_hybrid_path()`.
**Impact:** Code duplication and concept fragmentation. The adapter pattern is documented in pathfinding.py but not in fleet_navigation_service.py.
**Recommendation:** Use `_ChaserProxy` from pathfinding.py in fleet_navigation_service.py, or extract to shared location. Consider making `find_hybrid_path()` accept `can_warp: bool` directly instead of requiring fleet-like object.
**Effort:** Simple

#### MINOR: Serialization to_dict/from_dict Pattern Repetition
**ID:** DUP-STR-009
**Location:** `game/strategy/data/stars.py:48-75, 107-138` AND `game/strategy/data/planet.py` (multiple locations)
**Issue:** `Spectrum.to_dict()/from_dict()` and `Star.to_dict()/from_dict()` follow the same manual field-by-field serialization pattern. Similar patterns exist in `Planet`, `Fleet`, `Empire`, etc. Each manually maps fields to dict and back.
**Impact:** Verbose boilerplate code. Adding new fields requires updating both methods. However, this is a common Python pattern without easy generic solutions.
**Recommendation:** Consider using `dataclasses.asdict()` where applicable, or a mixin class with generic serialization. Alternatively, accept this as standard Python serialization pattern.
**Effort:** Complex (architectural change)

#### MINOR: Layer Iteration Pattern
**ID:** DUP-STR-010
**Location:** `game/strategy/engine/harvesting_engine.py:156-167, 234-245` AND `game/strategy/engine/production_engine.py:75-82` AND `game/strategy/services/ship_stats_calculator.py:128-149`
**Issue:** The pattern `for layer_data in design_data.get('layers', {}).values(): if isinstance(layer_data, list): for comp in layer_data:` appears in multiple places for iterating design components.
**Impact:** ~5-6 lines repeated in 4+ locations. Minor verbosity.
**Recommendation:** Extract utility function `iterate_design_components(design_data) -> Iterator[dict]` in `game/core/` or `game/strategy/services/`.
**Effort:** Simple

#### INFO: Similar DTO from_X Factory Methods
**ID:** DUP-STR-011
**Location:** `game/strategy/facade/dto/fleet_dto.py:91-177` AND `game/strategy/facade/dto/planet_dto.py:44-72`
**Issue:** `FleetInfo.from_fleet()` and `PlanetInfo.from_planet()` follow similar structural patterns for creating DTOs from domain objects. This is expected DTO pattern, not problematic duplication.
**Impact:** None - this is appropriate use of factory methods. Each DTO has unique field mappings.
**Recommendation:** No action needed. This is proper DTO design.
**Effort:** N/A

#### INFO: NavigationState Pattern
**ID:** DUP-STR-012
**Location:** `game/strategy/services/fleet_navigation_service.py:32-63`
**Issue:** `NavigationState.from_fleet()` duplicates some structure from `FleetInfo.from_fleet()` in extracting fleet properties. However, these serve different purposes (navigation calculation vs UI display).
**Impact:** None - appropriate separation of concerns. NavigationState is for pure calculation, FleetInfo is for UI.
**Recommendation:** No action needed. Different purposes justify separate implementations.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-STR-001 (CRITICAL):** Component Ability Extraction - Create unified `ComponentAbilityExtractor` service. Most impactful because it affects how new abilities are added across the codebase and has active divergence risk.

2. **DUP-STR-004 (MAJOR):** Ship Spawning Duplication - Extract `_create_ship_instance()` helper in ProductionEngine. Simple fix with clear consolidation benefit.

3. **DUP-STR-005 (MAJOR):** Complex Spawning Duplication - Extract `_create_facility()` helper in ProductionEngine. Can be done alongside DUP-STR-004.

4. **DUP-STR-003 (MAJOR):** Star Generation - Extract common star creation helpers. Medium effort but affects procedural generation quality.

5. **DUP-STR-002 (MAJOR):** Find Nearest System - Consolidate distance iteration. Simple fix that improves pathfinding maintainability.
