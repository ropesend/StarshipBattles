# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy (`game/strategy/`)
- **Files Scanned:** 95
- **Total Issues Found:** 14
- **Critical:** 0 | **Major:** 7 | **Minor:** 5 | **Info:** 2

## Findings

#### MAJOR: Build Queue Source Collection - Near-Identical Functions
**ID:** DUP-STR-001
**Location:** `game/strategy/data/build_queue_source.py:144-218` AND `game/strategy/data/build_queue_source.py:221-288`
**Issue:** Functions `collect_build_queues_at_hex()` and `collect_all_build_queues_for_empire()` share ~70% identical code. Both functions:
1. Create planet base queue BuildQueueSource objects (lines 169-179 vs 241-251)
2. Create shipyard facility BuildQueueSource objects (lines 186-196 vs 258-268)
3. Create fleet space yard BuildQueueSource objects (lines 206-216 vs 276-286)

The only difference is the iteration source: one filters by hex location, the other iterates all empire assets.
**Impact:** If the BuildQueueSource construction logic needs updating (e.g., new fields, different default values), both functions must be modified in parallel. Risk of drift where one gets updated and the other is forgotten.
**Recommendation:** Extract private helper functions `_create_planet_queue_sources(planet)` and `_create_fleet_queue_sources(fleet)` that both public functions call. The hex-based function adds a location filter, the empire-wide function iterates without filtering.
**Effort:** Simple

---

#### MAJOR: Facility Shipyard Detection - Duplicated Pattern
**ID:** DUP-STR-002
**Location:** `game/strategy/data/build_queue_source.py:116-141` AND `game/strategy/data/planet.py:213-231`
**Issue:** The `_facility_is_shipyard()` helper and `Planet.has_space_shipyard` property contain nearly identical logic for detecting if a facility has a space shipyard:
- Both iterate `facility.design_data.get("layers", {}).values()`
- Both check `isinstance(layer_data, list)`
- Both check `comp.get("id") == "space_shipyard"` OR `"SpaceShipyard" in comp.get("abilities", {})`
- Both have the same `if not facility.is_operational` guard
**Impact:** Maintenance burden when shipyard detection logic changes. The pattern could also diverge subtly causing bugs where one method detects shipyards differently.
**Recommendation:** Create a single canonical function in `component_inspector.py` like `facility_has_shipyard(facility, component_registry=None)` that both locations call.
**Effort:** Simple

---

#### MAJOR: Mission Command Handler Duplication
**ID:** DUP-STR-003
**Location:** `game/strategy/engine/superweapon_command_handlers.py:182-393` (5 handlers)
**Issue:** Five mission command handlers (ImplodePlanetMission, StellerateStarMission, OpenWarpPointMission, CloseWarpPointMission, CreateDysonSphereMission) share nearly identical 20-line patterns for:
1. Resolving fleet from session
2. Determining start hex from last order
3. Calculating path via `find_hybrid_path`
4. Queueing MOVE order with path assignment logic
5. Queueing action-specific order

Each handler differs only in the final action order type and target parameters.
**Impact:** When the mission pattern changes (e.g., path handling, error codes), all 5 handlers must be updated identically. Risk of divergence is high.
**Recommendation:** Extract a `_queue_mission_with_move()` helper method that accepts the action order type and target as parameters.
**Effort:** Simple

---

#### MAJOR: `to_dict` / `from_dict` Boilerplate Pattern
**ID:** DUP-STR-004
**Location:** Multiple files including:
- `game/strategy/data/fleet.py:320-385`
- `game/strategy/data/empire.py:137-195`
- `game/strategy/data/galaxy.py:775-830`
- `game/strategy/data/planet.py:275-380`
- `game/strategy/data/race_config.py:149-243`
- `game/strategy/data/stars.py:46-110`
- `game/strategy/data/design_metadata.py:40-79`
- `game/strategy/events/event_log.py:31-100`
- `game/strategy/engine/game_config.py:74-195`
- `game/strategy/data/ship_instance.py:608-670`
**Issue:** Every data class manually implements `to_dict()` and `from_dict()` with field-by-field mapping. This is ~30-60 lines per class, totaling ~400+ lines of repetitive serialization code across 10+ classes.
**Impact:** Adding a field requires updates in 3 places (class, to_dict, from_dict). Easy to introduce bugs where field is serialized but not deserialized.
**Recommendation:** Use `dataclasses.asdict()` with custom handling for complex types, or adopt a serialization framework (e.g., `cattrs`, `marshmallow`, or custom `@serializable` decorator).
**Effort:** Complex (requires serialization strategy decision)

---

#### MAJOR: Fleet Resolution Pattern in Command Handlers
**ID:** DUP-STR-005
**Location:**
- `game/strategy/engine/command_handlers.py:75-93` (ColonizeCommandHandler)
- `game/strategy/engine/command_handlers.py:128-135` (MoveCommandHandler)
- `game/strategy/engine/command_handlers.py:175-188` (InterceptCommandHandler)
- `game/strategy/engine/command_handlers.py:201-224` (JoinCommandHandler)
- `game/strategy/engine/command_handlers.py:230-245` (ColonizeMissionCommandHandler)
- `game/strategy/engine/superweapon_command_handlers.py` (all 11 handlers)
**Issue:** Every command handler starts with the same pattern:
```python
fleet = session._get_fleet_by_id(cmd.fleet_id)
if not fleet:
    return ValidationResult(is_valid=False, errors=["Fleet not found."])
```
This 3-line block is repeated ~18 times across command handlers.
**Impact:** Mild code bloat; if error message changes, must update everywhere.
**Recommendation:** Either:
1. Create decorator `@require_fleet` that injects validated fleet
2. Add `session.resolve_fleet_or_fail(cmd.fleet_id)` returning `(fleet, error_result)`
**Effort:** Simple

---

#### MAJOR: ColonizeValidator Colony Pod Iteration Pattern
**ID:** DUP-STR-006
**Location:** `game/strategy/validation/colonize_validator.py:100-174`
**Issue:** Three methods duplicate nearly identical component iteration logic:
- `find_ship_with_colony_pod()` - iterates ships/components looking for ColonizePlanet ability
- `get_available_colony_pods()` - iterates ships/components counting ColonizePlanet ability
- `get_committed_colony_pods()` - iterates orders counting committed pods

The first two methods share ~25 lines of duplicate component iteration with ability data extraction (handling both string and dict formats).
**Impact:** The ability data format handling (`isinstance(ability_data, str)` vs dict) is duplicated and could diverge.
**Recommendation:** Extract `_extract_colony_pod_planet_type(ability_data) -> str` helper. Consider using `component_inspector.iterate_design_components()` consistently.
**Effort:** Simple

---

#### MAJOR: Component Layer Iteration Pattern - Repeated Boilerplate
**ID:** DUP-STR-007
**Location:** Multiple files (6+ occurrences):
- `game/strategy/data/build_queue_source.py:95-111`
- `game/strategy/data/build_queue_source.py:132-140`
- `game/strategy/data/planet.py:53-65`
- `game/strategy/data/planet.py:220-231`
- `game/strategy/engine/resupply_engine.py:142-154`
- `game/strategy/engine/production_engine.py:312-337`
**Issue:** The pattern of iterating over facility/design components is repeated with minor variations:
```python
for layer_data in design_data.get("layers", {}).values():
    if not isinstance(layer_data, list):
        continue
    for comp in layer_data:
        comp_id = comp.get("id") if isinstance(comp, dict) else comp
        comp_def = registry.get(comp_id)
        # ... ability-specific logic
```
Each location reimplements the same iteration boilerplate before doing something different with the abilities found.
**Impact:** When the component data structure changes, all locations need updates. Easy to introduce subtle bugs (e.g., some locations handle string-only entries, others don't).
**Recommendation:** The `iterate_design_components()` function in `component_inspector.py` was created to address this, but several locations still use raw iteration. Migrate remaining locations to use the canonical iterator.
**Effort:** Medium

---

#### MINOR: Gaussian Factor Calculation Pattern
**ID:** DUP-STR-008
**Location:** `game/strategy/formulas/habitability.py:31-114`
**Issue:** Three functions (`calculate_gravity_factor`, `calculate_temperature_factor`, `calculate_water_factor`) use identical Gaussian falloff calculation:
```python
deviation = abs(actual - ideal)
sigma = max(tolerance, MIN_VALUE)
factor = math.exp(-0.5 * (deviation / sigma) ** 2)
```
**Impact:** Low risk - these are pure math functions with clear purpose. However, the pattern could be extracted.
**Recommendation:** Consider extracting `gaussian_factor(actual, ideal, tolerance, min_sigma)` helper. However, current explicit implementation is also acceptable for clarity.
**Effort:** Simple

---

#### MINOR: Path Start Hex Determination Logic
**ID:** DUP-STR-009
**Location:**
- `game/strategy/engine/command_handlers.py:248-253` (ColonizeMissionCommandHandler)
- `game/strategy/engine/superweapon_command_handlers.py:197-202` (ImplodePlanetMission)
- `game/strategy/engine/superweapon_command_handlers.py:238-244` (StellerateStarMission)
- `game/strategy/engine/superweapon_command_handlers.py:279-285` (OpenWarpPointMission)
- `game/strategy/engine/superweapon_command_handlers.py:324-330` (CloseWarpPointMission)
- `game/strategy/engine/superweapon_command_handlers.py:365-371` (CreateDysonSphereMission)
**Issue:** Six mission handlers repeat identical 6-line pattern:
```python
start_hex = fleet.location
if fleet.orders:
    last = fleet.orders[-1]
    if last.type == OrderType.MOVE:
        start_hex = last.target
```
**Impact:** If logic changes (e.g., also check MOVE_TO_FLEET), must update 6 places.
**Recommendation:** Add `fleet.get_effective_location()` or `session.get_fleet_start_hex_for_order(fleet)` method.
**Effort:** Simple

---

#### MINOR: Ship Ability Check Wrappers
**ID:** DUP-STR-010
**Location:**
- `game/strategy/data/fleet_capability_calculator.py:172-186` (`_ship_has_ability` method)
- `game/strategy/validation/superweapon_validator.py:17-33` (`find_ship_with_ability` method)
**Issue:** Both classes wrap `component_inspector.ship_has_ability()` and `find_ship_with_ability()` functions with near-identical thin wrappers that just call the canonical implementation.
**Impact:** Low. The wrappers exist for API convenience and are thin delegators.
**Recommendation:** Consider deprecating wrappers in favor of direct calls to `component_inspector` functions, or document them as intentional API facades.
**Effort:** Simple

---

#### MINOR: Resource Dictionary Accumulation Pattern
**ID:** DUP-STR-011
**Location:** `game/strategy/services/ship_stats_calculator.py:109-269`
**Issue:** Multiple resource accumulation loops use identical `dict[key] = dict.get(key, 0) + value` pattern:
- `resource_storage` accumulation
- `cargo_storage` accumulation
- `resource_consumption_per_hex` accumulation
- `resource_consumption_per_turn` accumulation
- `warp_resource_costs` accumulation
**Impact:** Low - this is standard Python dict accumulation. Could use `collections.defaultdict(float)` for cleaner code.
**Recommendation:** Consider `defaultdict(float)` for accumulators to eliminate `.get(key, 0)` pattern.
**Effort:** Simple

---

#### MINOR: Fleet and Ship Delegation Pattern
**ID:** DUP-STR-012
**Location:**
- `game/strategy/data/fleet.py:200-250` (15+ delegation methods)
- `game/strategy/data/ship_instance.py:267-352` (10+ delegation methods)
**Issue:** Both Fleet and ShipInstance classes have many thin delegation methods forwarding to their internal managers (FleetResourceAggregator, ShipResourceManager, etc.):
```python
def get_fleet_cargo_capacity(self, cargo_type: str) -> int:
    return self._resource_agg.get_fleet_cargo_capacity(cargo_type)
```
**Impact:** Low risk - the delegation pattern is intentional for encapsulation (PROJ-87). However, creates maintenance overhead keeping signatures in sync.
**Recommendation:** This is a design choice. Consider exposing managers directly for bulk operations or using `__getattr__` delegation. However, current explicit delegation is also acceptable.
**Effort:** Medium (if changed)

---

#### INFO: Validated Design Component Iteration
**ID:** DUP-STR-013
**Location:**
- `game/strategy/services/component_inspector.py:41-89` (canonical implementation)
- `game/strategy/services/ship_stats_calculator.py:366-401` (`_iterate_design_components` method)
**Issue:** `ShipStatsCalculator._iterate_design_components()` is a near-duplicate of `component_inspector.iterate_design_components()`. The calculator version returns `(layer_name, comp_entry, comp_def)` while the inspector returns `(comp_entry, comp_def, abilities)`.
**Impact:** The two implementations serve slightly different purposes (stats calculation vs ability lookup), but share ~80% of their logic.
**Recommendation:** This is a known pattern - the calculator predates the inspector consolidation (PROJ-108). Consider unifying when ShipStatsCalculator is next refactored. Document the relationship.
**Effort:** Medium

---

#### INFO: Well-Consolidated Component Inspector
**ID:** DUP-STR-014
**Location:** `game/strategy/services/component_inspector.py:1-164`
**Issue:** This file represents GOOD consolidation. Previous duplication in ColonizeValidator and SuperweaponValidator was extracted into canonical functions (`iterate_design_components`, `ship_has_ability`, `find_ship_with_ability`, `count_ability`).
**Impact:** Positive. This is the canonical location for component ability inspection.
**Recommendation:** Continue using this module for new ability queries. Consider migrating `ShipStatsCalculator._iterate_design_components()` to use this.
**Effort:** N/A (observation)

---

## Top 5 Priority Issues

1. **DUP-STR-001 (MAJOR): Build Queue Source Collection** - Two functions with 70% identical code for collecting build queues. Simple helper extraction would eliminate ~50 lines of duplication.

2. **DUP-STR-002 (MAJOR): Facility Shipyard Detection** - Same detection logic in two places (`_facility_is_shipyard` and `Planet.has_space_shipyard`). Should be a single function in `component_inspector.py`.

3. **DUP-STR-007 (MAJOR): Component Layer Iteration** - 6+ locations with raw iteration boilerplate. The canonical `iterate_design_components()` exists but isn't used everywhere.

4. **DUP-STR-003 (MAJOR): Mission Command Handler Duplication** - 5 handlers share 20-line patterns that should be extracted to a helper.

5. **DUP-STR-005 (MAJOR): Fleet Resolution Pattern** - 18 repetitions of fleet resolution boilerplate. Simple decorator or helper would clean this up.
