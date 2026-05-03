# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 94
- **Total Issues Found:** 9
- **Critical:** 2 | **Major:** 4 | **Minor:** 3 | **Info:** 0

## Findings

#### CRITICAL: Component Ability Extraction Loop - Identical in 3 Validators
**ID:** DUP-STR-001
**Location:** `game/strategy/validation/colonize_validator.py:15-37` AND `game/strategy/validation/superweapon_validator.py:14-36` AND `game/strategy/data/fleet_capability_calculator.py:35-44`
**Issue:** The exact same method _get_component_abilities() is implemented identically in both ColonizeValidator and SuperweaponValidator. Additionally, FleetCapabilityCalculator.ship_has_spaceyard() contains nearly identical component iteration logic. ~30 lines duplicated across 3 locations.
**Impact:** Any fix to ability extraction must be applied in 3 places. Future validators will copy-paste this again.
**Recommendation:** Extract to shared ComponentAbilityExtractor utility class in game/core/ or game/strategy/services/.
**Effort:** Medium

#### CRITICAL: Component Layer Iteration Pattern - Fragmented Across 6 Files
**ID:** DUP-STR-002
**Location:** `game/strategy/validation/colonize_validator.py:142-167` AND `game/strategy/validation/superweapon_validator.py:54-70` AND `game/strategy/data/fleet_capability_calculator.py:70-81` AND `game/strategy/data/design_metadata.py:164-171,207-215` AND `game/strategy/engine/resource_management_engine.py:119-125` AND `game/strategy/services/ship_stats_calculator.py:395-410`
**Issue:** Pattern of iterating through ship layers and extracting component entries appears in 6+ files with nearly identical structure but inconsistencies (some check isinstance(layer_components, list) while others check both list and dict formats).
**Impact:** Bug hiding risk - if a component iteration bug is discovered, it likely exists in all 6 locations.
**Recommendation:** Create ComponentIterator utility class with iterate_design_components(design_data, component_registry) method.
**Effort:** Medium

#### MAJOR: "Find Ship With Ability" Logic Duplicated in 2 Validators
**ID:** DUP-STR-003
**Location:** `game/strategy/validation/colonize_validator.py:125-167` AND `game/strategy/validation/superweapon_validator.py:39-70`
**Issue:** Both validators implement nearly identical "find first ship in fleet with ability" logic. Differ only in the ability name being searched. Both iterate through fleet ships → layers → components → abilities.
**Impact:** Two independent implementations will drift apart as features are added.
**Recommendation:** Create unified FleetAbilityFinder service. Consolidate 80 lines of near-identical code.
**Effort:** Simple

#### MAJOR: "Get Available/Committed Pods" Pattern Duplication
**ID:** DUP-STR-004
**Location:** `game/strategy/validation/colonize_validator.py:170-212` AND `game/strategy/validation/colonize_validator.py:215-238`
**Issue:** Two methods (get_available_colony_pods and get_committed_colony_pods) implement the same aggregation pattern but over different data sources. Both produce Dict[str, int] with the same structure.
**Impact:** If counting logic needs enhancement, it must be applied twice.
**Recommendation:** Create generic ResourceAggregator class or PodInventoryService with unified interface.
**Effort:** Medium

#### MAJOR: Resource Consumption Verification - Duplicated Pattern
**ID:** DUP-STR-005
**Location:** `game/strategy/data/fleet_resource_aggregator.py:47-97` AND `game/strategy/services/ship_stats_calculator.py:461-474`
**Issue:** Fleet resource aggregator has a two-phase check pattern repeated 3 times (verify all ships have sufficient resources, then consume). Same pattern in consume_movement_resources(), consume_warp_resources(), and conceptually in ship stats calculation.
**Impact:** Bug risk if someone fixes the atomic operation in one place but not others.
**Recommendation:** Extract AtomicResourceConsumption utility with verify_all_have() and consume_from_all() methods.
**Effort:** Medium

#### MAJOR: Ship Component Inspection - Nearly Identical in 3 Capability Checkers
**ID:** DUP-STR-006
**Location:** `game/strategy/data/fleet_capability_calculator.py:25-45` AND `game/strategy/data/fleet_capability_calculator.py:67-81` AND similar in colonize_validator.py and superweapon_validator.py
**Issue:** FleetCapabilityCalculator has two methods doing nearly the same thing - checking if a component exists with a specific ability. Static ship_has_spaceyard() returns boolean; property space_shipyard_count() returns count. Both iterate layers identically.
**Impact:** Each new capability check will replicate this layer iteration.
**Recommendation:** Create ShipComponentInspector utility with has_component_ability() and count_component_ability() methods.
**Effort:** Simple

#### MINOR: Distance/Location Calculation Patterns in Pathfinding
**ID:** DUP-STR-007
**Location:** `game/strategy/data/pathfinding.py:130-139` AND `game/strategy/data/pathfinding.py:141-160`
**Issue:** get_system_at_hex() and find_nearest_system() share 80% of their logic. Both iterate all systems and calculate distances with minimum tracking. ~30 lines of loop logic overlap.
**Impact:** Low-risk but maintenance burden if spatial search logic changes.
**Recommendation:** Create unified SystemLocator with find_nearest_system(hex, radius=None).
**Effort:** Simple

#### MINOR: Loader Pattern Duplication in 3 Configuration Loaders
**ID:** DUP-STR-008
**Location:** `game/strategy/generation/loaders/astrophysics_loader.py` AND `game/strategy/generation/loaders/system_blueprints_loader.py` AND `game/strategy/generation/loaders/galaxy_layouts_loader.py`
**Issue:** All three loaders follow identical pattern: optional custom path with DEFAULT_PATH fallback, load() method calling load_json_required() and _validate_schema(), getter methods. ~50 lines of duplicated boilerplate per loader.
**Impact:** Minor - loaders are isolated, unlikely to change frequently.
**Recommendation:** Create JsonConfigLoader base class with template methods.
**Effort:** Simple

#### MINOR: Density Primitive Evaluation Falloff Pattern
**ID:** DUP-STR-009
**Location:** `game/strategy/generation/density/primitives/geometric.py:89-105` and similar in radial.py, ring.py, spiral_arm.py
**Issue:** Density primitives implement similar falloff calculations for edge cases with similar exponential falloff formulas. ~20 lines of math duplicated.
**Impact:** Minor - each primitive is small.
**Recommendation:** Create DensityFalloffUtils with reusable gaussian_falloff() function.
**Effort:** Simple

## Top 5 Priority Issues
1. **DUP-STR-002: Component Layer Iteration Fragmentation** - 6+ files with inconsistent implementations, high bug risk
2. **DUP-STR-001: Component Ability Extraction** - Identical 30-line method in 3 validators
3. **DUP-STR-006: Ship Component Inspection** - Core operation duplicated, will proliferate
4. **DUP-STR-003: Find Ship With Ability** - Near-identical in 2 validators, easy consolidation
5. **DUP-STR-005: Resource Consumption Verification** - Atomic operation pattern repeated 3x
