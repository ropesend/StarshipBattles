# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 90
- **Total Issues Found:** 13
- **Critical:** 1 | **Major:** 5 | **Minor:** 5 | **Info:** 2

## Findings

#### CRITICAL: Design Layer Iteration Pattern Duplicated Across Multiple Engines
**ID:** DUP-STR-001
**Location:** `game/strategy/engine/harvesting_engine.py:227-245` AND `game/strategy/engine/resupply_engine.py:139-156` AND `game/strategy/engine/maintenance_engine.py:44-68` AND `game/strategy/engine/production_engine.py:71-82` AND `game/strategy/data/build_queue_source.py:93-111`
**Issue:** The pattern of iterating through `design_data.get("layers", {}).values()` to scan components for abilities is repeated in 5+ locations with near-identical structure. Each location handles slightly different ability types (ResourceHarvester, ResourceGeneration, ResourceStorage, SpaceShipyard, resource_cost) but the iteration logic is copy-pasted.
**Impact:** HIGH - Bug fixes to layer iteration (e.g., handling non-list layers) must be applied in all 5+ locations. If one is missed, subtle bugs can emerge. The code has already diverged slightly (some check `isinstance(layer_data, list)`, others check for "components" key).
**Recommendation:** Extract a generic `iterate_design_components()` function (similar to what exists in `component_inspector.py`) that yields `(layer_name, component, abilities)` tuples. All engines should use this single iterator.
**Effort:** Medium

#### MAJOR: Ability Extraction Pattern Repeated
**ID:** DUP-STR-002
**Location:** `game/strategy/engine/harvesting_engine.py:30-75` (get_harvester_info, get_harvester_from_registry) AND `game/strategy/engine/harvesting_engine.py:169-211` (_get_storage_info, _get_storage_from_registry)
**Issue:** Nearly identical helper functions exist for extracting ResourceHarvester and EmpireStorage abilities from components. Both follow the same pattern: check if dict with inline abilities, or resolve via registry lookup.
**Impact:** Maintenance burden - adding support for a new ability type requires writing yet another pair of helper functions.
**Recommendation:** Create a generic `get_ability_info(comp, ability_name, registries)` function that handles both inline and registry-based ability extraction.
**Effort:** Simple

#### MAJOR: Maintenance Cost Calculation Duplicated
**ID:** DUP-STR-003
**Location:** `game/strategy/engine/maintenance_engine.py:28-68` (calculate_maintenance_cost) AND `game/strategy/engine/empire_economy_calculator.py:222-233` (_calculate_maintenance_cost)
**Issue:** Both modules calculate maintenance costs from design_data. While EmpireEconomyCalculator correctly delegates to the shared function, the pattern of iterating layers to sum resource_cost is still duplicated in production_engine.py:58-82 (_calculate_design_cost) which does the SAME thing but without the rate multiplier.
**Impact:** Three places calculate total resource costs from components - maintenance uses rate multiplier, production does not. If the layer format changes, all three need updates.
**Recommendation:** Consolidate into a single `calculate_total_design_cost(design_data)` function, then have maintenance multiply by rate.
**Effort:** Simple

#### MAJOR: Ship Spawning Logic Duplicated Between Planet and Fleet
**ID:** DUP-STR-004
**Location:** `game/strategy/engine/production_engine.py:477-541` (_spawn_ship) AND `game/strategy/engine/production_engine.py:603-657` (_spawn_fleet_ship)
**Issue:** Both methods load design data via DesignLibrary, create ShipInstance.create(), and call increment_built_count(). The key difference is _spawn_ship creates a new Fleet while _spawn_fleet_ship adds to existing fleet. ~35 lines of near-identical code.
**Impact:** Changes to ship creation (e.g., adding crew assignment) must be applied in both places.
**Recommendation:** Extract common ship creation logic into a `_create_ship_instance()` helper, then have spawners focus only on fleet handling.
**Effort:** Simple

#### MAJOR: Complex Spawning Logic Duplicated Between Planet and Fleet
**ID:** DUP-STR-005
**Location:** `game/strategy/engine/production_engine.py:434-475` (_spawn_complex) AND `game/strategy/engine/production_engine.py:659-731` (_spawn_fleet_complex)
**Issue:** Both create PlanetaryFacility instances with identical initialization pattern. _spawn_fleet_complex has additional planet lookup logic but the facility creation is copy-pasted.
**Impact:** Changes to facility initialization must be applied in both places.
**Recommendation:** Extract `_create_facility_instance(design_id, design_data)` helper.
**Effort:** Simple

#### MAJOR: Fleet Lookup Pattern Repeated in Facade
**ID:** DUP-STR-006
**Location:** `game/strategy/facade/strategy_session_facade.py:79-104` (_get_fleet_by_id, _get_empire_by_id) AND `game/strategy/engine/game_session.py:208-247` (_get_fleet_by_id, _get_planet_by_id)
**Issue:** Both GameSession and StrategySessionFacade have their own entity lookup helpers. Facade delegates _get_fleet_by_id to session but has its own _get_empire_by_id. This creates confusion about the authoritative lookup location.
**Impact:** If lookup logic changes (e.g., O(1) registry lookup), both locations may need updates.
**Recommendation:** Facade should delegate ALL lookups to GameSession. Session should be the single source of truth for entity resolution.
**Effort:** Simple

#### MINOR: find_ship_with_ability Wrapper in SuperweaponValidator
**ID:** DUP-STR-007
**Location:** `game/strategy/validation/superweapon_validator.py:17-33` (find_ship_with_ability method)
**Issue:** SuperweaponValidator.find_ship_with_ability() is a thin wrapper that just calls _inspector_find_ship(). This adds an unnecessary layer of indirection.
**Impact:** Low - works correctly, just adds code without value.
**Recommendation:** Call component_inspector.find_ship_with_ability() directly instead of wrapping it.
**Effort:** Simple

#### MINOR: Planet/Fleet Build Capability Checks Similar
**ID:** DUP-STR-008
**Location:** `game/strategy/data/planet.py:267-287` (can_build_type) AND `game/strategy/data/fleet_capability_calculator.py:74-102` (can_build_type)
**Issue:** Both implement the same vehicle_type checking logic (ship/fighter/satellite vs complex). Planet checks has_space_shipyard, FleetCapabilityCalculator also checks shipyard status.
**Impact:** Minor - slightly different semantics but similar pattern.
**Recommendation:** Consider a shared enum or constants for vehicle types that can be built by shipyards vs planetary yards.
**Effort:** Simple

#### MINOR: Queue Tick Processing Partially Duplicated
**ID:** DUP-STR-009
**Location:** `game/strategy/engine/production_engine.py:138-172` (_process_queue_tick) AND `game/strategy/engine/production_engine.py:173-280` (_process_queue_tick_with_completion)
**Issue:** _process_queue_tick is a subset of _process_queue_tick_with_completion. The simpler method is unused and could be removed.
**Impact:** Dead code - _process_queue_tick appears to be vestigial.
**Recommendation:** Remove _process_queue_tick if it's truly unused, or refactor to have it call the more complete version.
**Effort:** Simple

#### MINOR: HexCoord Serialization Pattern Repeated
**ID:** DUP-STR-010
**Location:** `game/strategy/data/fleet.py:325-338` (to_dict location handling) AND `game/strategy/data/fleet.py:346-370` (from_dict location/path restoration)
**Issue:** HexCoord to/from dict conversion appears in multiple places with slightly different approaches. Some use hex_to_dict/hex_from_dict helpers, others do inline dict construction.
**Impact:** Minor inconsistency - could lead to bugs if HexCoord format changes.
**Recommendation:** Always use the canonical hex_to_dict/hex_from_dict from game.core.hex_math.
**Effort:** Simple

#### MINOR: collect_build_queues Pattern Duplicated
**ID:** DUP-STR-011
**Location:** `game/strategy/data/build_queue_source.py:196-227` (collect_build_queues_at_hex) AND `game/strategy/data/build_queue_source.py:230-255` (collect_all_build_queues_for_empire)
**Issue:** Both functions iterate planet sources and fleet sources with nearly identical calls to _collect_planet_sources and _collect_fleet_sources. Only the iteration scope differs.
**Impact:** Low - already factored reasonably well.
**Recommendation:** Could parameterize with optional hex filter, but current design is acceptable.
**Effort:** Complex (not recommended)

#### INFO: Consistent Delegate Pattern (Good Design)
**ID:** DUP-STR-012
**Location:** `game/strategy/data/fleet.py` AND `game/strategy/data/ship_instance.py`
**Issue:** Both Fleet and ShipInstance properly delegate to specialized managers (FleetResourceAggregator, FleetCapabilityCalculator, ShipResourceManager, ShipCargoManager). This is good design that AVOIDS duplication.
**Impact:** Positive - this pattern should be emulated elsewhere.
**Recommendation:** No action needed - document as best practice.
**Effort:** N/A

#### INFO: Well-Consolidated Component Inspector
**ID:** DUP-STR-013
**Location:** `game/strategy/services/component_inspector.py`
**Issue:** This module was created specifically to consolidate duplicated component/ability iteration patterns. It provides ship_has_ability, find_ship_with_ability, iterate_design_components, etc.
**Impact:** Positive - this shows prior consolidation effort.
**Recommendation:** Extend this pattern to cover the engine-level duplications identified in DUP-STR-001.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-STR-001 (CRITICAL):** Design layer iteration duplicated across 5+ engine files - highest bug risk, should consolidate into a single canonical iterator function.

2. **DUP-STR-003 (MAJOR):** Maintenance/production cost calculation scattered - three places calculate total resource costs from design components with slight variations.

3. **DUP-STR-004 + DUP-STR-005 (MAJOR):** Ship and complex spawning logic duplicated between planet and fleet contexts - extract common creation helpers.

4. **DUP-STR-002 (MAJOR):** Ability extraction pattern repeated for different ability types - create generic ability getter.

5. **DUP-STR-006 (MAJOR):** Entity lookup split between Facade and Session - consolidate to Session as single source of truth.
