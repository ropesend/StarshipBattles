# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy (`game/strategy/`)
- **Files Scanned:** 95
- **Total Issues Found:** 11
- **Critical:** 0 | **Major:** 5 | **Minor:** 4 | **Info:** 2

## Findings

#### MAJOR: Mission Command Handler Duplication
**ID:** DUP-STR-001
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

#### MAJOR: Direct vs Mission Command Validation Asymmetry
**ID:** DUP-STR-002
**Location:** `game/strategy/engine/superweapon_command_handlers.py:27-176` (direct handlers) vs `game/strategy/engine/superweapon_command_handlers.py:182-393` (mission handlers)
**Issue:** Direct command handlers (ImplodePlanetCommandHandler, etc.) call validation via `SuperweaponValidator.validate_*()`, but the corresponding mission handlers skip validation entirely. They trust the path check is sufficient validation.
**Impact:** Semantic duplication of validation intent. Mission handlers may queue invalid orders that fail later during turn execution.
**Recommendation:** Mission handlers should also validate the final action will be valid at the destination, or document why validation is deferred.
**Effort:** Medium

#### MAJOR: `to_dict` / `from_dict` Boilerplate Pattern
**ID:** DUP-STR-003
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

#### MAJOR: Fleet Resolution Pattern in Command Handlers
**ID:** DUP-STR-004
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

#### MAJOR: ColonizeValidator Colony Pod Iteration Pattern
**ID:** DUP-STR-005
**Location:** `game/strategy/validation/colonize_validator.py:100-174`
**Issue:** Three methods duplicate nearly identical component iteration logic:
- `find_ship_with_colony_pod()` - iterates ships/components looking for ColonizePlanet ability
- `get_available_colony_pods()` - iterates ships/components counting ColonizePlanet ability
- `get_committed_colony_pods()` - iterates orders counting committed pods

The first two methods share ~25 lines of duplicate component iteration with ability data extraction (handling both string and dict formats).
**Impact:** The ability data format handling (`isinstance(ability_data, str)` vs dict) is duplicated and could diverge.
**Recommendation:** Extract `_extract_colony_pod_planet_type(ability_data) -> str` helper. Consider using `component_inspector.iterate_design_components()` consistently.
**Effort:** Simple

#### MINOR: Gaussian Factor Calculation Pattern
**ID:** DUP-STR-006
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

#### MINOR: Path Start Hex Determination Logic
**ID:** DUP-STR-007
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

#### MINOR: Ship Ability Check Wrappers
**ID:** DUP-STR-008
**Location:**
- `game/strategy/data/fleet_capability_calculator.py:172-186` (`_ship_has_ability` method)
- `game/strategy/validation/superweapon_validator.py:17-33` (`find_ship_with_ability` method)
**Issue:** Both classes wrap `component_inspector.ship_has_ability()` and `find_ship_with_ability()` functions with near-identical thin wrappers that just call the canonical implementation.
**Impact:** Low. The wrappers exist for API convenience and are thin delegators.
**Recommendation:** Consider deprecating wrappers in favor of direct calls to `component_inspector` functions, or document them as intentional API facades.
**Effort:** Simple

#### MINOR: Resource Dictionary Accumulation Pattern
**ID:** DUP-STR-009
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

#### INFO: Validated Design Component Iteration
**ID:** DUP-STR-010
**Location:**
- `game/strategy/services/component_inspector.py:41-89` (canonical implementation)
- `game/strategy/services/ship_stats_calculator.py:366-401` (`_iterate_design_components` method)
**Issue:** `ShipStatsCalculator._iterate_design_components()` is a near-duplicate of `component_inspector.iterate_design_components()`. The calculator version returns `(layer_name, comp_entry, comp_def)` while the inspector returns `(comp_entry, comp_def, abilities)`.
**Impact:** The two implementations serve slightly different purposes (stats calculation vs ability lookup), but share ~80% of their logic.
**Recommendation:** This is a known pattern - the calculator predates the inspector consolidation (PROJ-108). Consider unifying when ShipStatsCalculator is next refactored. Document the relationship.
**Effort:** Medium

#### INFO: Well-Consolidated Component Inspector
**ID:** DUP-STR-011
**Location:** `game/strategy/services/component_inspector.py:1-164`
**Issue:** This file represents GOOD consolidation. Previous duplication in ColonizeValidator and SuperweaponValidator was extracted into canonical functions (`iterate_design_components`, `ship_has_ability`, `find_ship_with_ability`, `count_ability`).
**Impact:** Positive. This is the canonical location for component ability inspection.
**Recommendation:** Continue using this module for new ability queries. Consider migrating `ShipStatsCalculator._iterate_design_components()` to use this.
**Effort:** N/A (observation)

## Top 5 Priority Issues

1. **DUP-STR-001 (MAJOR): Mission Command Handler Duplication** - 5 handlers share 20-line patterns that should be extracted to a helper. Most impactful consolidation opportunity in terms of lines saved.

2. **DUP-STR-003 (MAJOR): to_dict/from_dict Boilerplate** - ~400+ lines of manual serialization across 10+ classes. Adopting a serialization strategy would eliminate a major source of maintenance bugs.

3. **DUP-STR-004 (MAJOR): Fleet Resolution Pattern** - 18 repetitions of fleet resolution boilerplate. Simple decorator or helper would clean this up.

4. **DUP-STR-005 (MAJOR): ColonizeValidator Pod Iteration** - Ability data format handling duplicated in 2 methods. Extract shared helper to ensure consistent handling.

5. **DUP-STR-007 (MINOR): Path Start Hex Determination** - 6 repetitions of effective location calculation. Simple extraction to Fleet method.
