# Consistency Violations Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 68
- **Total Issues Found:** 19
- **Critical:** 1 | **Major:** 5 | **Minor:** 9 | **Info:** 4

## Findings

#### CRITICAL: Inconsistent Return Convention for Not-Found Scenarios
**ID:** CON-SIM-001
**Location:** `game/simulation/services/battle_service.py:274-289` vs `game/simulation/systems/battle_engine.py:615-634`
**Issue:** `BattleService.get_winner()` returns `Optional[int]` (None when no battle), while `BattleEngine.get_winner()` always returns `int` (-1 for draw, never None). This inconsistency in return semantics for the same operation at different abstraction levels creates confusion about what "no winner" means.
**Impact:** Callers must handle different return types despite calling semantically equivalent methods. This led to documented special handling in `battle_service.py:276-285`.
**Recommendation:** Either both should return Optional[int] (None = incomplete/no battle), or both should return int with -1 as a sentinel. The current documentation clarifies but doesn't eliminate the cognitive overhead.
**Effort:** Medium

#### MAJOR: Mixed Naming for Result/Error Types
**ID:** CON-SIM-002
**Location:** Multiple files in `game/simulation/services/`
**Issue:** Different naming conventions for result objects:
- `BattleServiceResult` (battle_service.py)
- `DesignResult` (vehicle_design_service.py)
- `ValidationResult` (validation/ship_validator.py)

The naming is inconsistent: "ServiceResult" vs "Result" suffix. Also, `BattleState` module has `BattleResults` (plural) which is a different concept from `BattleServiceResult`.
**Impact:** Cognitive overhead when determining which result type to use; confusion between `BattleResults` (outcome data) and `BattleServiceResult` (operation status).
**Recommendation:** Standardize to either `XxxResult` or `XxxServiceResult` for all operation result types. The current `BattleServiceResult` (renamed from `BattleResult` per PROJ-107) acknowledges this issue but the solution isn't applied consistently.
**Effort:** Medium

#### MAJOR: Inconsistent Private Member Naming
**ID:** CON-SIM-003
**Location:** Throughout `game/simulation/` module
**Issue:** Mixed use of single underscore prefix for private members:
- `Ship._cached_mass`, `Ship._registries`, `Ship._components_cache` (prefixed)
- `Ship.ship_class`, `Ship.theme_id`, `Ship.base_mass` (unprefixed but effectively private state)
- `Component._registries`, `Component._hp_ratio_dirty` (prefixed)
- `Component.abilities`, `Component.stats` (unprefixed but internal)
- `BattleEngine._ai_factory` (prefixed) vs `BattleEngine.ships`, `BattleEngine.ai_controllers` (unprefixed collections)
**Impact:** Unclear which attributes are part of public API vs implementation details.
**Recommendation:** Establish clear convention: underscore prefix for attributes not intended for external access. Apply consistently across all entity classes.
**Effort:** Complex

#### MAJOR: Inconsistent Use of TYPE_CHECKING for Import Organization
**ID:** CON-SIM-004
**Location:** Various files
**Issue:** Inconsistent patterns for type hint imports:
- Some files use `if TYPE_CHECKING:` blocks for all type-only imports (e.g., `battle_engine.py`, `design_loader.py`)
- Others import types directly even when only used for hints (e.g., `ship_stats.py` imports `Component` at runtime)
- Some use string forward references `'Ship'` while others import the type
**Impact:** Potential circular import issues; inconsistent import organization makes patterns harder to follow.
**Recommendation:** Standardize on `TYPE_CHECKING` blocks for type-only imports from same or lower layers. Use string forward references for same-module types.
**Effort:** Simple

#### MAJOR: Mixed Docstring Styles
**ID:** CON-SIM-005
**Location:** Throughout `game/simulation/` module
**Issue:** Three docstring styles in use:
1. Google-style with `Args:`, `Returns:`, `Raises:` sections (e.g., `ship_validator.py`, `battle_service.py`)
2. Simple one-liner docstrings (e.g., most abilities in `propulsion.py`, `defense.py`)
3. Extended descriptions without structured sections (e.g., `resource_manager.py` top-level docstring)

The comprehensive module docstrings (like in `battle_engine.py`, `ship_stats.py`) follow a custom format with section headers like `Battle Lifecycle:`, `Physics Constants:`.
**Impact:** Inconsistent documentation makes it harder to understand API contracts.
**Recommendation:** Adopt Google-style docstrings consistently for all public methods. Use module-level docstrings with standard sections for module documentation.
**Effort:** Complex

#### MAJOR: Dual Patterns for Querying Components/Abilities
**ID:** CON-SIM-006
**Location:** `game/simulation/entities/ship.py:586-602` vs `game/simulation/entities/ship_stat_querier.py`
**Issue:** Two patterns exist for querying ship stats:
1. Direct methods on Ship: `get_ability_total()`, `get_total_ability_value()`, `get_total_sensor_score()`, `get_total_ecm_score()`
2. Delegation to ShipStatQuerier: `ship.stat_querier.get_ability_total()`

Some methods delegate (pattern 2) while others don't exist on the querier. The Ship class has both patterns coexisting.
**Impact:** Unclear which pattern is canonical; Ship class retains some query methods rather than fully delegating.
**Recommendation:** Complete the facade pattern - Ship methods should only delegate. All query implementation should live in ShipStatQuerier.
**Effort:** Medium

#### MINOR: Inconsistent Method Verb Prefixes
**ID:** CON-SIM-007
**Location:** Various files
**Issue:** Mixed verb conventions for similar operations:
- `get_winner()` vs `get_all_ships()` vs `get_alive_ships()` (consistent `get_` prefix)
- `is_battle_over()` vs `is_retreating()` (consistent `is_` prefix)
- BUT: `calculate_ability_totals()` vs `get_ability_total()` (calculate vs get for similar aggregation)
- `find_nearest_edge()` vs `get_ship_by_name()` (find vs get for lookup operations)
- `at_map_edge()` (no prefix - reads as verb phrase rather than boolean accessor)
**Impact:** Minor cognitive overhead when remembering which verb to use.
**Recommendation:** Standardize: `get_` for retrieval, `find_` for search with criteria, `is_`/`has_` for boolean checks, `calculate_` for computation. Consider renaming `at_map_edge()` to `is_at_map_edge()`.
**Effort:** Simple

#### MINOR: Inconsistent Parameter Naming for Ship Reference
**ID:** CON-SIM-008
**Location:** Various combat and targeting files
**Issue:** Ship parameters named inconsistently:
- `ship` in most places
- `owner` in `Projectile.__init__()`, `ProjectileState.from_projectile()`
- `source_ship` in fighter launch handling
**Impact:** Minor confusion when reading across files about which parameter refers to which ship.
**Recommendation:** Use `ship` for the subject ship, `owner` for owner reference in projectiles/components, `source_ship` for launch origin. Document this convention.
**Effort:** Simple

#### MINOR: Inconsistent Boolean Naming Patterns
**ID:** CON-SIM-009
**Location:** Various entity classes
**Issue:** Boolean attributes use mixed conventions:
- `is_alive`, `is_active`, `is_operational`, `is_derelict` (verb prefix)
- `bridge_destroyed` (past participle, no prefix)
- `mass_limits_ok` (adjective suffix)
- `headless`, `isolated` in BattleConfig (bare adjectives)
**Impact:** Inconsistent reading of boolean attribute semantics.
**Recommendation:** Standardize on `is_`/`has_`/`can_` prefixes for boolean state. Consider `is_bridge_destroyed`, `are_mass_limits_ok` or `mass_limits_valid`.
**Effort:** Simple

#### MINOR: Magic Numbers in Ship/Component Initialization
**ID:** CON-SIM-010
**Location:** `game/simulation/entities/ship.py:92-96`, `game/simulation/entities/ship_stats.py:170-176`
**Issue:** Several magic numbers without named constants:
- `ship.py:92`: `max_mass_budget = class_def.get('max_mass', 1000)` - default 1000
- `ship_stats.py:170-176`: Defense score calculation uses `80.0`, `-2.5`, `20.0`, `360.0`, `180`
- `projectile.py:8`: `TURN_COMMITMENT_THRESHOLD_DEG = 45` (correctly extracted)
**Impact:** Hard to understand the significance of these values; difficult to tune consistently.
**Recommendation:** Extract all gameplay-tuning constants to `physics_constants.py` or `SimulationConstants`. Some are already there but not used consistently.
**Effort:** Simple

#### MINOR: Inconsistent Use of dataclass vs Manual Classes
**ID:** CON-SIM-011
**Location:** `game/simulation/` entity and state classes
**Issue:** Some data structures use dataclasses, others are manual classes with similar semantics:
- `BattleState`, `ShipState`, `ComponentState`, `ProjectileState` - dataclasses with `to_dict()`/`from_dict()`
- `BattleConfig`, `BattleServiceResult`, `DesignResult` - dataclasses
- `ResourceState` in `resource_manager.py` - manual class with similar pattern
- `RetreatState` - dataclass
**Impact:** Minor inconsistency; `ResourceState` could benefit from dataclass features.
**Recommendation:** Convert `ResourceState` to dataclass for consistency with other state classes.
**Effort:** Simple

#### MINOR: Inconsistent Error Handling Strategy
**ID:** CON-SIM-012
**Location:** Various service methods
**Issue:** Mixed error handling patterns:
- Services return `XxxResult(success=False, errors=[...])` (e.g., `BattleService`, `VehicleDesignService`)
- Some methods raise exceptions (e.g., `BattleController.run_headless()` raises `StateException`)
- `Projectile.__init__()` raises `ValidationException` for invalid parameters
- Some methods return `None` on failure (e.g., `create_component()`, `SimulationDesignLoader.load_ship_from_design_data()`)
**Impact:** Callers must handle multiple error reporting styles.
**Recommendation:** Document and standardize: Services use Result objects for recoverable errors; constructors raise exceptions for invalid state; None returns only for "not found" scenarios.
**Effort:** Medium

#### MINOR: Inconsistent Manager/Service/Helper Class Naming
**ID:** CON-SIM-013
**Location:** `game/simulation/` module structure
**Issue:** Mixed suffixes for helper/manager classes:
- `AbilityManager`, `ModifierManager`, `RetreatManager`, `ProjectileManager` (Manager suffix)
- `BattleService`, `ModifierService`, `VehicleDesignService` (Service suffix)
- `ShipStatsCalculator`, `DamageCalculator`, `ComponentStatsCalculator` (Calculator suffix)
- `ShipStatQuerier`, `ShipValidatorHelper` (Querier/Helper suffix)
**Impact:** Unclear semantic distinction between Manager/Service/Helper/Calculator.
**Recommendation:** Establish convention: Services are stateful orchestrators, Managers handle state for specific concerns, Calculators are stateless computation, Helpers are utility classes. Document and apply consistently.
**Effort:** Medium

#### MINOR: Inconsistent __init__.py Export Patterns
**ID:** CON-SIM-014
**Location:** `game/simulation/services/__init__.py`, `game/simulation/components/abilities/__init__.py`, `game/simulation/__init__.py`
**Issue:** Different export patterns:
- `services/__init__.py`: Simple re-exports with `__all__`
- `abilities/__init__.py`: Full registry setup, `ABILITY_REGISTRY` dict, `create_ability()` factory
- `simulation/__init__.py`: Comprehensive docstring documenting public API, organized imports

The abilities module mixes registration concerns with exports.
**Impact:** Inconsistent module boundary definitions.
**Recommendation:** Separate concerns: `__init__.py` for exports only. Move `ABILITY_REGISTRY` and `create_ability()` to a separate `registry.py` module within abilities.
**Effort:** Simple

#### INFO: Ability Classes Have Consistent Pattern
**ID:** CON-SIM-015
**Location:** `game/simulation/components/abilities/`
**Issue:** This is a POSITIVE finding - Ability classes follow a consistent pattern:
- All inherit from `Ability`
- All define `STAT_BINDINGS` class variable
- All implement `__init__(component, data)` signature
- All implement `recalculate()` for modifier application
- All implement `get_ui_rows()` for display
- All implement `get_primary_value()` for aggregation
**Impact:** Good internal consistency within abilities module.
**Recommendation:** Continue this pattern. Consider documenting it as a template for new abilities.
**Effort:** N/A

#### INFO: Validation Rules Follow Template Method Pattern
**ID:** CON-SIM-016
**Location:** `game/simulation/validation/ship_validator.py`
**Issue:** POSITIVE finding - Validation rules consistently use template method pattern:
- All extend `AdditionValidationRule` or `DesignValidationRule`
- All implement `_do_validate()` with consistent signature
- Some override `_should_validate()` for conditional execution
**Impact:** Good maintainability for validation system.
**Recommendation:** Continue this pattern. Document as example of good pattern usage.
**Effort:** N/A

#### INFO: Registry Pattern Well Implemented
**ID:** CON-SIM-017
**Location:** Throughout `game/simulation/`
**Issue:** POSITIVE finding - The registry pattern is consistently used:
- All components use `registries.components`
- All modifiers use `registries.modifiers`
- Vehicle classes from `registries.vehicle_classes`
- Strict DI with required `registries` parameter enforced in constructors
**Impact:** Good dependency injection consistency.
**Recommendation:** Continue this pattern. The PROJ-50 strict DI policy is well implemented.
**Effort:** N/A

#### INFO: Projectile State Inconsistent with Ship State Serialization
**ID:** CON-SIM-018
**Location:** `game/simulation/battle_state.py:321-468`
**Issue:** `ProjectileState` follows similar pattern to `ShipState` but lacks `to_projectile()` method parity:
- `ShipState.to_ship(registries=...)` requires registries
- `ProjectileState.to_projectile(ship_lookup)` takes a ship lookup dict instead of registries
**Impact:** Minor inconsistency in deserialization approach.
**Recommendation:** Consider whether `ProjectileState.to_projectile()` should follow similar DI pattern to `ShipState.to_ship()`.
**Effort:** Simple

#### INFO: Consistent Use of PROJ- References in Comments
**ID:** CON-SIM-019
**Location:** Throughout codebase
**Issue:** POSITIVE finding - Project references are consistently used:
- `PROJ-XX` for project IDs in comments explaining changes
- References explain why code exists, not just what it does
- Examples: `PROJ-50: Strict DI`, `PROJ-44 Phase 4:`, `PROJ-49 Phase 3:`
**Impact:** Good traceability of architectural decisions.
**Recommendation:** Continue this pattern. It aids in understanding historical context.
**Effort:** N/A

## Top 5 Priority Issues

1. **CON-SIM-001 (CRITICAL)**: Inconsistent Return Convention for Not-Found - The `get_winner()` return type inconsistency between service and engine layers creates subtle bugs when callers don't handle both conventions.

2. **CON-SIM-003 (MAJOR)**: Inconsistent Private Member Naming - Without clear public/private boundaries, maintainers may inadvertently depend on internal implementation details.

3. **CON-SIM-006 (MAJOR)**: Dual Patterns for Querying - The incomplete facade pattern in Ship class creates confusion about where query logic should live.

4. **CON-SIM-002 (MAJOR)**: Mixed Result Type Naming - The `BattleResults` vs `BattleServiceResult` confusion (acknowledged in PROJ-107 comments) continues to create cognitive overhead.

5. **CON-SIM-005 (MAJOR)**: Mixed Docstring Styles - Inconsistent documentation makes it harder for new developers to understand API contracts and follow established patterns.
