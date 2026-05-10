# Consistency Violations Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 71
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 7 | **Minor:** 8 | **Info:** 2

## Findings

#### CRITICAL: ResourceRegistry Return Type Inconsistency for Not-Found Cases
**ID:** CON-SIM-001
**Location:** `game/simulation/systems/resource_manager.py:120-131`
**Issue:** `get_resource()` returns `Optional[ResourceState]` (None if not found), while `get_value()` and `get_max_value()` return `0.0` if resource not found. The class docstring documents "Optional[T] (None = not found)" for single-value lookups, but `get_value()` violates this by returning 0.0 - masking the difference between "resource doesn't exist" and "resource has zero value".
**Impact:** Bugs where code assumes a resource exists based on a zero return value, when the resource is actually unregistered. Different error handling paths required for same conceptual query.
**Recommendation:** Either make `get_value()` return `Optional[float]` to match convention, or explicitly document it as a convenience method that masks non-existence with a default value of 0.0.
**Effort:** Simple

#### MAJOR: Duplicate Exception Handler in design_loader.py
**ID:** CON-SIM-002
**Location:** `game/simulation/services/design_loader.py:118-133`
**Issue:** The same exception tuple `(KeyError, TypeError, ValueError, json.JSONDecodeError)` is caught in two consecutive except clauses, making the second clause unreachable dead code.
**Impact:** Unreachable code that adds confusion. If the first clause is modified, the second becomes orphaned.
**Recommendation:** Remove the duplicate except clause.
**Effort:** Simple

#### MAJOR: Magic Numbers in Projectile Guidance System
**ID:** CON-SIM-003
**Location:** `game/simulation/entities/projectile.py:161,167,179`
**Issue:** Hardcoded values `* 100`, `* 0.01`, and `45` (degrees) in `_update_guidance()` without named constants. These are conversion factors and thresholds that affect missile behavior.
**Impact:** Unclear behavior, maintenance difficulty. Developers must understand why 45 degrees is significant without context.
**Recommendation:** Extract to named constants: `TURN_RATE_CONVERSION = 100`, `FIXED_TICK_DURATION = 0.01`, `TURN_COMMITMENT_THRESHOLD_DEG = 45`. Add to `physics_constants.py`.
**Effort:** Simple

#### MAJOR: Singleton Fallback Pattern in Validation
**ID:** CON-SIM-004
**Location:** `game/simulation/entities/ship_loader.py`, `game/simulation/services/vehicle_design_service.py`, `game/simulation/entities/ship_validator_helper.py`
**Issue:** `get_or_create_validator()` uses global singleton pattern for ShipDesignValidator, bypassing the registry parameter passed to these methods. Comment acknowledges: "This method always uses the singleton-backed validator via get_or_create_validator(), regardless of the registry passed..."
**Impact:** Makes isolated testing harder. DI pattern is partially circumvented.
**Recommendation:** Complete the DI migration for validator instantiation as noted in PROJ-50 scope.
**Effort:** Complex

#### MAJOR: Inconsistent Parameter Naming - resource_name vs resource_type
**ID:** CON-SIM-005
**Location:** `game/simulation/components/abilities/resources.py:26,164,204`
**Issue:** ResourceConsumption uses `resource_name` attribute while ResourceStorage and ResourceGeneration use `resource_type` attribute for the same concept (the resource identifier string).
**Impact:** Cognitive overhead when working across resource abilities. Template code cannot be easily reused. Developers must remember which attribute name applies to which class.
**Recommendation:** Standardize on `resource_type` across all resource abilities. This matches ResourceType constants and is semantically accurate.
**Effort:** Simple

#### MAJOR: Type Hint Gaps in Physics and Combat Modules
**ID:** CON-SIM-006
**Location:** `game/simulation/entities/ship_physics.py`, `game/simulation/entities/combat_endurance.py`
**Issue:** `ship_physics.py` mixin methods (`rotate()`, `thrust_forward()`, `set_throttle()`) lack return type hints. `combat_endurance.py` functions lack parameter and return type hints entirely.
**Impact:** Reduced IDE support and static analysis effectiveness. Inconsistent with other modules that have full type coverage.
**Recommendation:** Add complete type hints to these modules. Use `-> None` for void methods, proper parameter types for functions.
**Effort:** Medium

#### MAJOR: AIControllerFactory Uses Positional Parameter Unlike Other DI Classes
**ID:** CON-SIM-007
**Location:** `game/simulation/factories/ai_factory.py:35`
**Issue:** `AIControllerFactory.__init__(self, grid: SpatialGrid)` uses positional parameter, while all other DI-style classes use keyword-only pattern: `VehicleDesignService(*, registries)`, `ModifierService(*, registries)`, `ShipDesignValidator(*, registries)`, etc.
**Impact:** Inconsistent API for dependency injection across the codebase.
**Recommendation:** Change to `AIControllerFactory(*, grid: SpatialGrid)` for consistency with other DI classes.
**Effort:** Simple

#### MAJOR: Magic Numbers in Targeting and Combat Systems
**ID:** CON-SIM-008
**Location:** `game/simulation/combat/targeting_system.py:167,213`, `game/simulation/managers/retreat_manager.py:103`
**Issue:** Hardcoded values: `* 2.0` (max range multiplier), `/ 100.0` (speed conversion), `500` (warp charge ticks). These affect game balance and are not defined as named constants.
**Impact:** Maintenance difficulty, unclear intent, scattered magic numbers affecting combat balance.
**Recommendation:** Extract to constants in appropriate modules. `TARGETING_MAX_RANGE_MULT = 2.0`, `SPEED_CONVERSION_FACTOR = 100.0`, `WARP_CHARGE_TICKS = 500`.
**Effort:** Simple

#### MINOR: Abbreviated Parameter Names in solve_lead()
**ID:** CON-SIM-009
**Location:** `game/simulation/combat/targeting_system.py`, `game/simulation/entities/ship_combat_engine.py:65`
**Issue:** Parameters use terse names: `p_speed`, `t_pos`, `t_vel` instead of descriptive names like `projectile_speed`, `target_position`, `target_velocity`.
**Impact:** Reduced readability, especially for developers unfamiliar with the targeting math.
**Recommendation:** Use descriptive parameter names: `target_pos`, `target_vel`, `projectile_speed`.
**Effort:** Simple

#### MINOR: Mixed Logging Initialization Patterns
**ID:** CON-SIM-010
**Location:** `game/simulation/services/registry_loader.py`, `game/simulation/managers/retreat_manager.py`, `game/simulation/services/vehicle_design_service.py`
**Issue:** registry_loader uses `logging.getLogger("StarshipBattles")` while other modules use `from game.core.logger import log_debug, log_info` wrapper functions.
**Impact:** Inconsistent logging configuration. Some modules bypass the centralized logger.
**Recommendation:** Standardize on `game.core.logger` wrapper functions throughout simulation module.
**Effort:** Simple

#### MINOR: STAT_BINDINGS Type Hint Inconsistency
**ID:** CON-SIM-011
**Location:** `game/simulation/components/abilities/markers.py`, `game/simulation/components/abilities/superweapons.py`
**Issue:** Marker abilities use `STAT_BINDINGS: List[AbilityStatBinding] = []` with type hint, while superweapons use `STAT_BINDINGS = []` without type hint. Base class uses no type hint.
**Impact:** Inconsistent static type checking. Some files benefit from type hints, others don't.
**Recommendation:** Standardize on `STAT_BINDINGS: List[AbilityStatBinding] = []` with explicit type hint in all ability classes.
**Effort:** Simple

#### MINOR: sync_data() Inconsistent Implementation Across Abilities
**ID:** CON-SIM-012
**Location:** `game/simulation/components/abilities/resources.py`, `game/simulation/components/abilities/crew.py`, `game/simulation/components/abilities/markers.py`
**Issue:** ResourceConsumption and ResourceStorage implement `sync_data()` to support runtime data updates, but most other abilities (CrewCapacity, LifeSupportCapacity, CrewRequired, VehicleLaunchAbility, CommandAndControl) rely on base class no-op implementation.
**Impact:** Inconsistent behavior when attempting to update ability data at runtime. Some abilities can be updated, others silently ignore updates.
**Recommendation:** Document which abilities support `sync_data()` or implement consistently across abilities with mutable state.
**Effort:** Medium

#### MINOR: Inconsistent Method Verb Conventions
**ID:** CON-SIM-013
**Location:** `game/simulation/entities/ship_stat_querier.py`, `game/simulation/entities/ability_aggregator.py`
**Issue:** `get_ability_total()` uses `get_` prefix while `calculate_ability_totals()` uses `calculate_` prefix for similar operations.
**Impact:** Inconsistent naming makes it harder to predict method names.
**Recommendation:** Standardize: use `calculate_` for computation-heavy methods that derive new values, `get_` for simple lookups/accessors.
**Effort:** Simple

#### MINOR: Missing Exports in services/__init__.py
**ID:** CON-SIM-014
**Location:** `game/simulation/services/__init__.py`
**Issue:** `SimulationDesignLoader` and `reload_registries_from_directory` are not exported in `__init__.py` despite being public APIs.
**Impact:** Users must import directly from submodules, inconsistent with other service exports.
**Recommendation:** Add to `__all__` if intended for public use.
**Effort:** Simple

#### MINOR: ability_aggregator.py Naming Convention
**ID:** CON-SIM-015
**Location:** `game/simulation/entities/ability_aggregator.py`
**Issue:** File is named `ability_aggregator.py` but other Ship extractions use `ship_` prefix: `ship_stats.py`, `ship_stat_querier.py`, `ship_validator_helper.py`, `ship_physics.py`, `ship_formation.py`, `ship_serialization.py`.
**Impact:** Inconsistent file naming within the entities module.
**Recommendation:** Consider renaming to `ship_ability_aggregator.py` for consistency with other ship-related extractions.
**Effort:** Simple

#### MINOR: PROJ Comment Format Inconsistency
**ID:** CON-SIM-016
**Location:** Various files across simulation module
**Issue:** PROJ reference formatting varies: `PROJ-XX:`, `PROJ-XX Phase N:`, `Part of PROJ-XX`. Examples: `PROJ-44: ShipCombatEngine Decomposition`, `PROJ-43 Phase 8: ...`, `Part of PROJ-44 Phase 5:`.
**Impact:** Minor inconsistency in documentation style.
**Recommendation:** Standardize on `PROJ-XX:` format for inline comments, `PROJ-XX Phase N:` for phase-specific notes.
**Effort:** Simple

#### INFO: ResourceRegistry Class Name Deviation
**ID:** CON-SIM-017
**Location:** `game/simulation/systems/resource_manager.py`
**Issue:** Class is named `ResourceRegistry` while similar management classes use `Manager` suffix: `RetreatManager`, `BattleStateManager`, `ModifierManager`.
**Impact:** Low - the name is semantically correct as it "registers" resources, but differs from peer classes.
**Recommendation:** Consider renaming to `ResourceManager` for consistency, or document that "Registry" is appropriate for this pattern.
**Effort:** Simple

#### INFO: Excellent Pattern Adherence - Facade/Delegate
**ID:** CON-SIM-018
**Location:** `game/simulation/entities/ship_combat_engine.py`, `game/simulation/battle_controller.py`
**Issue:** N/A - positive finding. ShipCombatEngine properly delegates to TargetingSystem, DamageCalculator, and WeaponFiringSystem. BattleController properly delegates to BattleService, BattleStateManager, and BattleModeHandler. This correctly follows PROJ-12 God Class Decomposition and PROJ-44 patterns.
**Impact:** Positive - demonstrates correct pattern usage.
**Recommendation:** Use as canonical examples in documentation for facade/delegate pattern.
**Effort:** N/A

## Top 5 Priority Issues

1. **CON-SIM-001 (CRITICAL)**: `ResourceRegistry` has inconsistent return conventions - `get_resource()` returns None for not-found, but `get_value()`/`get_max_value()` return 0.0. This masks bugs where code assumes a resource exists based on zero value.

2. **CON-SIM-002 (MAJOR)**: Duplicate exception handler in `design_loader.py` is dead code that should be removed.

3. **CON-SIM-003 + CON-SIM-008 (MAJOR)**: Magic numbers scattered across projectile guidance, targeting, and retreat systems. Extract to named constants for maintainability.

4. **CON-SIM-004 (MAJOR)**: Singleton fallback pattern in validation bypasses DI, making isolated testing harder. Complete DI migration per PROJ-50.

5. **CON-SIM-006 (MAJOR)**: Type hint gaps in `ship_physics.py` and `combat_endurance.py` reduce static analysis effectiveness and IDE support.
