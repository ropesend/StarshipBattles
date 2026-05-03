# Consistency Violations Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 94
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 5 | **Minor:** 8 | **Info:** 4

## Findings

#### CRITICAL: Inconsistent Return Type for Not-Found Cases
**ID:** CON-STR-001
**Location:** Multiple files
**Issue:** Some methods return `None` for not-found cases while similar methods raise exceptions. The `Galaxy.get_planet_by_id()` returns `None`, while `RaceConfig.load()` also returns `None`, but `GameSession.from_dict()` raises `PersistenceException` for missing fields. This inconsistency in error handling patterns within the same layer can lead to bugs when callers assume one pattern but encounter another.
**Impact:** Callers may not handle `None` returns properly, leading to `AttributeError` exceptions at runtime. The mixed pattern increases cognitive load and bug risk.
**Recommendation:** Standardize on returning `None` for lookup operations (get_by_id patterns) and raising exceptions only for deserialization errors with context. Document the convention clearly.
**Effort:** Medium

#### MAJOR: Mixed Verb Prefixes for Similar Operations
**ID:** CON-STR-002
**Location:** `game/strategy/data/fleet.py`, `game/strategy/data/empire.py`, `game/strategy/data/galaxy.py`
**Issue:** Inconsistent verb prefixes for similar operations:
- `get_fleet_by_id()` vs `_get_fleet_by_id()` (Galaxy vs GameSession)
- `add_colony()` / `remove_colony()` vs `register_fleet()` / `unregister_fleet()`
- `get_system_by_name()` vs `get_system_at_location()` vs `get_system_of_object()`
The "register/unregister" pattern is used for spatial index operations while "add/remove" is used for collection operations, but `add_fleet()` on Empire doesn't use "register" terminology even though Galaxy uses it.
**Impact:** Developers must remember different naming conventions for similar operations, increasing cognitive load.
**Recommendation:** Standardize: use `add_/remove_` for collection membership, `register_/unregister_` only for spatial indexes, and `get_X_by_Y()` for lookups.
**Effort:** Medium

#### MAJOR: Inconsistent Docstring Presence and Format
**ID:** CON-STR-003
**Location:** Multiple files across `game/strategy/`
**Issue:** Docstring coverage and format varies significantly:
- `game/strategy/formulas/habitability.py` - Excellent: all public functions have detailed docstrings with Args/Returns
- `game/strategy/data/stars.py` - Poor: many methods like `_generate_mass()`, `_determine_type_and_radius()` have minimal or no docstrings
- `game/strategy/data/fleet.py` - Mixed: some methods documented, others not
- `game/strategy/engine/production_engine.py` - Good module docstring but inconsistent method coverage
**Impact:** Inconsistent documentation makes codebase harder to understand and maintain.
**Recommendation:** Establish minimum docstring requirement for all public methods (Google format with Args/Returns). Private methods should have at least a one-liner.
**Effort:** Complex (requires documentation pass across all files)

#### MAJOR: Inconsistent Constructor DI Pattern Application
**ID:** CON-STR-004
**Location:** `game/strategy/engine/` directory
**Issue:** Some engines require `GameRegistries` via constructor (strict DI) while others accept optional registries:
- `ShipStatsCalculator.__init__(registries)` - REQUIRED, raises TypeError if None (strict DI)
- `HarvestingEngine.__init__(*, registries=None)` - OPTIONAL, None acceptable
- `ProductionEngine.__init__()` - NO registries parameter at all
- `TurnEngine.__init__(registries=None)` - OPTIONAL with lazy fallback

The comment "PROJ-50: Made registries parameter required (strict DI)" in ShipStatsCalculator suggests this was intended as the standard, but it's not applied consistently.
**Impact:** Inconsistent DI patterns make testing setup unpredictable and violate the stated architectural goal of strict DI.
**Recommendation:** Apply strict DI pattern (required registries, TypeError on None) to all engine constructors per PROJ-50 intent.
**Effort:** Medium

#### MAJOR: Mixed Static Methods and Instance Methods for Utility Functions
**ID:** CON-STR-005
**Location:** `game/strategy/services/ship_stats_calculator.py`, `game/strategy/validation/colonize_validator.py`
**Issue:** Some utility classes use `@staticmethod` while others use instance methods for similar functionality:
- `ColonizeValidator.validate()` - static method, takes all dependencies as parameters
- `ColonizeValidator.find_ship_with_colony_pod()` - static method
- `ShipStatsCalculator.get_component_effectiveness()` - static method
- `ShipStatsCalculator.calculate_stats()` - instance method (needs `self._registries`)
- `HarvestingEngine._process_empire()` - instance method for similar processing

When a class has no state, all methods should be static. When it requires DI dependencies, all should be instance methods.
**Impact:** Inconsistent patterns make it unclear whether a class should be instantiated or used statically.
**Recommendation:** ColonizeValidator should either be purely static (pass registry each time) or become a service class with DI. Choose one pattern per class.
**Effort:** Medium

#### MAJOR: Inconsistent Type Hints on Module-Level Functions
**ID:** CON-STR-006
**Location:** `game/strategy/engine/harvesting_engine.py`, `game/strategy/data/stars.py`
**Issue:** Module-level helper functions have inconsistent type hint coverage:
- `get_harvester_info(comp, registries)` - Has return type `Optional[dict]` but no parameter types
- `get_harvester_from_registry(comp_id: str, registries: GameRegistries)` - Fully typed
- `StarGenerator._kelvin_to_rgb(self, temp: float)` - Has input type but not return type `tuple`
- Most functions in `habitability.py` - Fully typed with `-> float`
**Impact:** Incomplete type hints reduce IDE assistance and static analysis effectiveness.
**Recommendation:** Require type hints on all function signatures per CLAUDE.md guidelines.
**Effort:** Simple

#### MINOR: Inconsistent Private Method Naming Convention
**ID:** CON-STR-007
**Location:** `game/strategy/data/galaxy.py`, `game/strategy/services/fleet_navigation_service.py`
**Issue:** Some "private" methods use single underscore `_` while others use double underscore or no prefix:
- `Galaxy._calculate_warp_distance()` - single underscore
- `Galaxy._next_planet_id` - single underscore attribute
- `FleetNavigationService._needs_path_recalculation()` - single underscore
- `RaceConfig._ENVIRONMENT_RANGES` - single underscore for class constant
The project appears to consistently use single underscore, which is good, but some files have methods that could be private but aren't marked (e.g., helper methods in `stars.py`).
**Impact:** Minor - internal implementation detail, but consistency aids comprehension.
**Recommendation:** Continue using single underscore consistently; mark all internal helper methods as private.
**Effort:** Simple

#### MINOR: Inconsistent Import Organization
**ID:** CON-STR-008
**Location:** Multiple files
**Issue:** Import grouping varies between files:
- `fleet.py` - Mixes `from game.core...` before `from enum import...`
- `turn_engine.py` - Standard library first, then game imports
- `stars.py` - `import random` before `import math`, then `from enum...`
The convention should be: stdlib -> third-party -> local, alphabetical within groups.
**Impact:** Minor readability issue, but inconsistent with PEP8 best practices.
**Recommendation:** Use isort or ruff to standardize import ordering project-wide.
**Effort:** Simple (automated tooling available)

#### MINOR: Inconsistent Boolean Property Naming
**ID:** CON-STR-009
**Location:** `game/strategy/data/fleet.py`, `game/strategy/data/planet.py`
**Issue:** Boolean properties/methods use inconsistent prefixes:
- `fleet.is_building` - `is_` prefix
- `fleet.has_space_shipyard` - `has_` prefix (property)
- `fleet.can_use_warp()` - `can_` prefix (method)
- `ship.is_combat_capable()` - `is_` prefix (method)
- `PlanetaryFacility.is_shipyard` - `is_` prefix (property)
The pattern is mostly consistent (is_ for state, has_ for possession, can_ for capability) but the mix of properties vs methods for similar queries adds confusion.
**Impact:** Minor - naming is reasonable but property vs method choice is inconsistent.
**Recommendation:** Use properties for simple state checks, methods only when computation or external calls are needed.
**Effort:** Simple

#### MINOR: Inconsistent Error Code Usage
**ID:** CON-STR-010
**Location:** `game/strategy/validation/colonize_validator.py`, `game/strategy/engine/command_handlers.py`
**Issue:** ValidationResult error codes are used inconsistently:
- ColonizeValidator returns `error_code="NO_COLONY_POD"`, `"COLONY_POD_EXHAUSTED"`, `"NO_CANDIDATES"`
- MoveCommandHandler returns no error_code for "Target is unreachable"
- Other command handlers also don't use error codes
Only ColonizeValidator comprehensively uses error codes while other validators return human-readable errors only.
**Impact:** Client code that wants to programmatically handle specific error cases cannot do so consistently.
**Recommendation:** Add error codes to all validation failures for programmatic error handling.
**Effort:** Medium

#### MINOR: Inconsistent to_dict/from_dict Pattern Implementation
**ID:** CON-STR-011
**Location:** Multiple data classes
**Issue:** Serialization methods have varying levels of robustness:
- `Fleet.from_dict()` - Uses `.get()` with defaults for optional fields
- `Planet.from_dict()` - Uses direct key access `data['location']` without defaults
- `RaceConfig.from_dict()` - Comprehensive `.get()` with explicit defaults
- Some classes don't validate required fields during deserialization
**Impact:** Inconsistent error handling during save/load could cause confusing exceptions.
**Recommendation:** Standardize: use `.get()` with explicit defaults for optional fields, direct access for required fields, and add validation for required fields.
**Effort:** Medium

#### MINOR: Inconsistent Use of TYPE_CHECKING Block
**ID:** CON-STR-012
**Location:** Multiple files
**Issue:** Some files use `TYPE_CHECKING` imports for forward references while others don't:
- `fleet.py` - Uses `TYPE_CHECKING` for `GameRegistries`
- `stars.py` - No `TYPE_CHECKING` imports despite forward references
- `galaxy.py` - Uses `TYPE_CHECKING` for some but not all forward references
**Impact:** Minor - affects type checking tools but not runtime.
**Recommendation:** Use `TYPE_CHECKING` consistently for all forward reference imports to avoid circular import issues.
**Effort:** Simple

#### MINOR: Inconsistent Constant Naming
**ID:** CON-STR-013
**Location:** `game/strategy/data/stars.py`, `game/strategy/formulas/habitability.py`
**Issue:** Most module-level constants use UPPER_SNAKE_CASE correctly:
- `SOLAR_MASS_KG`, `SOLAR_RADIUS_M` in stars.py
- `FACTOR_WEIGHTS`, `STANDARD_GRAVITY_MS2` in habitability.py
However, some configuration data uses camelCase or mixed formats:
- `DEFAULT_ATMOSPHERE_PREFERENCES` in race_config.py (correct)
- Lists like `GOVERNMENT_TYPES`, `LEADER_TITLES` (correct)
Overall consistency is good, but magic numbers still exist in some formulas.
**Impact:** Minor - mostly consistent, some hardcoded values in formulas.
**Recommendation:** Extract remaining magic numbers (e.g., `0.8` exponent in mass-luminosity relation) to named constants.
**Effort:** Simple

#### INFO: Natural Variation in Method Signatures
**ID:** CON-STR-014
**Location:** `game/strategy/engine/` directory
**Issue:** Engine interfaces define consistent method signatures, but implementations occasionally add extra parameters:
- `IProductionEngine.process_construction_tick(tick, empires, galaxy)` vs actual implementation with `save_path`, `harvesting_engine` params
This is acceptable since the interface defines minimum contract, but could cause issues if type checking strict interface compliance.
**Impact:** Low - implementation detail, interfaces allow extension.
**Recommendation:** Document that implementations may extend interfaces with additional optional parameters.
**Effort:** None needed

#### INFO: Facade vs Direct Access Pattern Variation
**ID:** CON-STR-015
**Location:** `game/strategy/facade/strategy_session_facade.py`, `game/strategy/engine/game_session.py`
**Issue:** The facade pattern is well-implemented with StrategySessionFacade wrapping GameSession. However, internal code sometimes accesses GameSession directly (e.g., within the strategy layer), while the docstring says "UI layer should never access GameSession internals directly."
This is appropriate - the facade is for UI, internal strategy code can access session directly.
**Impact:** None - this is correct architecture, just documenting the pattern.
**Recommendation:** None - current pattern is appropriate.
**Effort:** None needed

#### INFO: Delegate Pattern Consistency
**ID:** CON-STR-016
**Location:** `game/strategy/data/fleet.py`, `game/strategy/data/ship_instance.py`
**Issue:** Both Fleet and ShipInstance use delegate pattern for separating concerns:
- Fleet uses `_resource_agg`, `_capabilities`, `_battle` delegates
- ShipInstance uses `_resource_mgr`, `_cargo_mgr`, `_display_fmt` delegates
Naming convention differs slightly (`_agg` vs `_mgr`) but pattern is consistent.
**Impact:** None - minor naming variation in internal delegates.
**Recommendation:** Consider standardizing on `_manager` suffix for all delegates, but low priority.
**Effort:** Simple if desired

#### INFO: Event System Consistency
**ID:** CON-STR-017
**Location:** `game/strategy/events/event_types.py`, usage across engines
**Issue:** EventType and EventCategory enums are well-defined and consistently used across the strategy layer:
- All production events use `EventCategory.PRODUCTION`
- All combat events use `EventCategory.COMBAT`
- Event logging via `log_event()` is consistent
This is a positive finding - the event system is well-designed.
**Impact:** None - good consistency.
**Recommendation:** Continue using this pattern as a model for other systems.
**Effort:** None needed

#### INFO: Interface Naming Convention
**ID:** CON-STR-018
**Location:** `game/strategy/interfaces/` directory
**Issue:** Interface classes consistently use `I` prefix:
- `IBattleResolver`
- `IMovementEngine`, `IProductionEngine`, `IOrderProcessor`, etc.
- `ISystemPlacementStrategy`
Protocol classes use no prefix but are runtime_checkable.
This is consistent and follows a clear convention.
**Impact:** None - good consistency.
**Recommendation:** Continue using `I` prefix for abstract base classes, Protocol for duck-typing contracts.
**Effort:** None needed

## Top 5 Priority Issues

1. **CON-STR-001 (CRITICAL)**: Inconsistent Return Type for Not-Found Cases - Mixed None/exception patterns can cause runtime errors. Should standardize on None for lookups, exceptions for deserialization.

2. **CON-STR-004 (MAJOR)**: Inconsistent Constructor DI Pattern - The strict DI pattern (PROJ-50) is only partially applied. All engines should require GameRegistries consistently.

3. **CON-STR-003 (MAJOR)**: Inconsistent Docstring Presence - Varying documentation quality across modules makes codebase harder to maintain. Establish and enforce minimum standards.

4. **CON-STR-005 (MAJOR)**: Mixed Static/Instance Methods - Classes like ColonizeValidator mix patterns. Each class should be consistently static OR service-based with DI.

5. **CON-STR-002 (MAJOR)**: Mixed Verb Prefixes - Inconsistent naming for add/remove vs register/unregister operations increases cognitive load. Standardize terminology.
