# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 89
- **Total Issues Found:** 9
- **Critical:** 0 | **Major:** 5 | **Minor:** 3 | **Info:** 1

## Findings

#### MAJOR: Duplicated Facility Component Iteration Pattern
**ID:** DUP-STR-001
**Location:**
- `game/strategy/engine/harvesting_engine.py:151-167` (EmpireStorage lookup)
- `game/strategy/engine/harvesting_engine.py:232-245` (ResourceHarvester lookup)
- `game/strategy/engine/resupply_engine.py:140-155` (ResourceGeneration lookup)
- `game/strategy/data/build_queue_source.py:93-111` (SpaceShipyard lookup)
- `game/strategy/data/planet.py:53-65` (ResourceStorage lookup - PlanetaryFacility)
- `game/strategy/data/planet.py:110-120` (SpaceShipyard check)
**Issue:** Six separate locations iterate through `facility.design_data.get("layers", {}).values()` with near-identical loop structure to extract component abilities. Each follows the pattern: iterate layers, skip non-lists, iterate components, get component ID, lookup in registry, get abilities dict, check for specific ability.
**Impact:** If the design_data format changes, all 6 locations must be updated. Bugs in component iteration could manifest differently across modules. The pattern is ~15-20 lines each.
**Recommendation:** Consolidate into `component_inspector.py` which already has `iterate_design_components()`. Create a specialized helper like `iterate_facility_abilities(facility, ability_name, registries)` that these 6 locations can use.
**Effort:** Medium

#### MAJOR: Duplicated Command Handler Pattern
**ID:** DUP-STR-002
**Location:**
- `game/strategy/engine/command_handlers.py:73-172` (Core handlers)
- `game/strategy/engine/superweapon_command_handlers.py:27-175` (Superweapon direct handlers)
- `game/strategy/engine/superweapon_command_handlers.py:222-343` (Superweapon mission handlers)
**Issue:** All command handlers follow identical structure: (1) resolve fleet via `session._get_fleet_by_id()`, (2) validate, (3) create FleetOrder, (4) add to fleet, (5) log. The direct superweapon handlers and mission handlers each repeat this ~30 line pattern 6+ times. The mission handlers also duplicate `_setup_mission_move()` logic (lines 182-219) across all 5 handlers.
**Impact:** Adding new commands requires copying the same boilerplate. Changing error handling or logging requires touching many classes.
**Recommendation:** Create a base class or decorator that handles the common resolve-validate-apply-log flow. Mission handlers could use a mixin that provides movement setup. Each handler only needs to specify: validator method, order type, and target construction.
**Effort:** Medium

#### MAJOR: Duplicated Resource Cost Calculation
**ID:** DUP-STR-003
**Location:**
- `game/strategy/engine/maintenance_engine.py:45-68` (`calculate_maintenance_cost()`)
- `game/strategy/engine/production_engine.py:58-82` (`_calculate_design_cost()`)
**Issue:** Both methods iterate through `design_data.get('layers', {}).values()` to sum up `resource_cost` from components. The maintenance engine applies a 5% rate modifier; the production engine caches the result. Core iteration logic is identical (~20 lines).
**Impact:** If component cost structure changes (e.g., nested costs, cost modifiers), both must be updated. Currently production uses `layer.get('components', [])` while maintenance handles both dict and list formats differently - potential inconsistency.
**Recommendation:** Extract shared `sum_design_resource_costs(design_data)` function that handles all layer formats. MaintenanceEngine can apply the rate multiplier on the result.
**Effort:** Simple

#### MAJOR: Duplicated Ability Lookup in Validators
**ID:** DUP-STR-004
**Location:**
- `game/strategy/validation/superweapon_validator.py:17-33` (`find_ship_with_ability()` wrapper)
- `game/strategy/services/component_inspector.py:118-136` (`find_ship_with_ability()` canonical)
- `game/strategy/data/fleet_capability_calculator.py:172-186` (`ship_has_ability()` static)
**Issue:** SuperweaponValidator.find_ship_with_ability() is a thin wrapper around component_inspector.find_ship_with_ability(). FleetCapabilityCalculator.ship_has_ability() is another wrapper around component_inspector.ship_has_ability(). These wrappers add no value - they exist only for historical reasons before component_inspector was created.
**Impact:** Cognitive overhead - developers must discover which location is canonical. The wrappers could drift from the underlying implementation.
**Recommendation:** Remove wrapper methods. Have callers use component_inspector directly. SuperweaponValidator can import and re-export if API stability is needed.
**Effort:** Simple

#### MAJOR: Duplicated Superweapon Ship Removal Pattern
**ID:** DUP-STR-005
**Location:**
- `game/strategy/engine/superweapon_order_processor.py:79-104` (IMPLODE_PLANET)
- `game/strategy/engine/superweapon_order_processor.py:252-284` (OPEN_WARP_POINT)
- `game/strategy/engine/superweapon_order_processor.py:344-359` (CLOSE_WARP_POINT)
- `game/strategy/engine/superweapon_order_processor.py:422-477` (CREATE_DYSON_SPHERE)
**Issue:** Each superweapon processor method repeats: (1) find ship with ability via validator, (2) fall back to fleet.ships[0] if no registry, (3) remove ship from fleet, (4) pop order, (5) calculate fleet_consumed, (6) log event. Pattern is ~30 lines repeated 4 times.
**Impact:** If ship removal behavior changes (e.g., triggering events, cleanup), 4 locations must be updated. Bug risk in maintaining consistency.
**Recommendation:** Extract `_consume_superweapon_ship(fleet, ability_name, registry)` helper that handles lookup, removal, and returns the ship name for logging. Each processor calls this helper.
**Effort:** Simple

#### MINOR: Duplicated to_dict/from_dict Serialization Pattern
**ID:** DUP-STR-006
**Location:**
- `game/strategy/data/fleet.py:320-415` (Fleet, FleetOrder)
- `game/strategy/data/ship_instance.py:608-662` (ShipInstance)
- `game/strategy/data/planet.py:283-397` (Planet)
- `game/strategy/data/empire.py:137-225` (Empire)
- `game/strategy/data/galaxy.py:775-836` (Galaxy, StarSystem, WarpPoint)
- `game/strategy/data/race_config.py:150-280` (RaceConfig)
**Issue:** Each domain object implements to_dict() and from_dict() with manual field serialization. While each class has unique fields, the pattern of "for each field, serialize/deserialize" is repeated. HexCoord handling (hex_to_dict/hex_from_dict) is duplicated across multiple from_dict implementations.
**Impact:** Low direct risk - each class legitimately has different fields. However, adding new fields requires remembering to update both methods. HexCoord handling could use a decorator or mixin.
**Recommendation:** Consider dataclass-based auto-serialization or a serialization mixin for common patterns. Low priority as current implementation is working.
**Effort:** Complex (would require significant refactoring)

#### MINOR: Duplicated "Fleet Not Found" Validation
**ID:** DUP-STR-007
**Location:**
- `game/strategy/engine/command_handlers.py:94,137,165,187,210,239,299,320`
- `game/strategy/engine/superweapon_command_handlers.py:34,63,88,115,139,163,228,254,279,305,330`
- `game/strategy/facade/strategy_session_facade.py:371,386,399`
**Issue:** The string "Fleet not found." appears 22+ times across command handlers and facade. Each location performs `fleet = session._get_fleet_by_id(cmd.fleet_id)` followed by `if not fleet: return ValidationResult(is_valid=False, errors=["Fleet not found."])`.
**Impact:** Minor - if error message standardization is needed, many locations must change. If lookup logic changes, each location must update.
**Recommendation:** Consider a `resolve_fleet_or_fail()` helper that returns (fleet, ValidationResult) tuple, or raises a custom exception that handlers catch.
**Effort:** Simple

#### MINOR: Duplicated Planet Lookup Pattern
**ID:** DUP-STR-008
**Location:**
- `game/strategy/facade/strategy_session_facade.py:202-215` (`_get_planet_by_id()`)
- `game/strategy/engine/game_session.py` (similar pattern)
**Issue:** Multiple places iterate through `galaxy.systems.values()` and then `system.planets` to find a planet by ID. Galaxy already has `get_planet_by_id()` O(1) lookup via `planets_by_id` registry.
**Impact:** The facade's `_get_planet_by_id()` uses O(n*m) iteration instead of O(1) registry lookup.
**Recommendation:** Use `galaxy.get_planet_by_id()` in all locations that need planet lookup by ID.
**Effort:** Simple

#### INFO: Well-Consolidated Component Inspection
**ID:** DUP-STR-009
**Location:** `game/strategy/services/component_inspector.py`
**Issue:** (Positive observation) The codebase has already consolidated component iteration into `component_inspector.py` (PROJ-108 Phase 3). ColonizeValidator, SuperweaponValidator, and FleetCapabilityCalculator all use these shared functions. This is a good example of duplication being addressed.
**Impact:** Positive - reduces future duplication risk for ability iteration.
**Recommendation:** Continue this pattern. Extend component_inspector with the facility-specific iteration helpers suggested in DUP-STR-001.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-STR-001: Duplicated Facility Component Iteration Pattern** - 6 locations with identical iteration structure. High consolidation value, medium effort. Extending the existing component_inspector pattern would be natural.

2. **DUP-STR-003: Duplicated Resource Cost Calculation** - Simple extraction that eliminates inconsistency between maintenance and production calculations. High value for effort.

3. **DUP-STR-005: Duplicated Superweapon Ship Removal Pattern** - 4 methods with 30+ lines of identical logic. Simple extraction would reduce code by ~90 lines and centralize ship consumption behavior.

4. **DUP-STR-004: Duplicated Ability Lookup Wrappers** - Dead code/wrappers that add confusion. Simple removal cleans up the codebase.

5. **DUP-STR-002: Duplicated Command Handler Pattern** - Most complex but highest long-term value. Would make adding new commands trivial and reduce boilerplate significantly.
