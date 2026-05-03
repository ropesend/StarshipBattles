# Consistency Violations Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 95
- **Total Issues Found:** 14
- **Critical:** 1 | **Major:** 4 | **Minor:** 6 | **Info:** 3

## Findings

#### CRITICAL: Inconsistent Error Handling Return Types
**ID:** CON-STR-001
**Location:** `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`, `game/strategy/validation/superweapon_validator.py`
**Issue:** ColonizeValidator.validate() returns a ValidationResult with errors list, but the error messages are inconsistent with TransferValidator. ColonizeValidator uses lowercase "required" messages while SuperweaponValidator uses proper sentences. Some validators check for None target first, others embed it in later logic.
**Impact:** Inconsistent error messages make UI/logging integration harder; validators behave differently for edge cases.
**Recommendation:** Standardize all validators to:
1. Check for None targets first with consistent message format
2. Use sentence case for all error messages ("Fleet must be at planet location" not "required")
3. Return ValidationResult consistently across all validators
**Effort:** Medium

#### MAJOR: Mixed Engine Initialization Patterns
**ID:** CON-STR-002
**Location:** `game/strategy/engine/production_engine.py:52-54`, `game/strategy/engine/resupply_engine.py:54-65`, `game/strategy/engine/harvesting_engine.py:94-101`
**Issue:** Engine classes have inconsistent constructor patterns:
- ProductionEngine: Empty __init__, no dependencies
- ResupplyEngine: Requires registries (raises TypeError if None)
- HarvestingEngine: Optional registries with keyword-only syntax
- FleetMovementEngine: Optional nav_service with lazy initialization
**Impact:** Inconsistent DI patterns create confusion about engine usage; some engines fail fast while others fail silently later.
**Recommendation:** Standardize all engines to use the HarvestingEngine pattern: keyword-only `registries` parameter that is optional with lazy initialization where needed. Document pattern in engine interface or base class.
**Effort:** Medium

#### MAJOR: Inconsistent Docstring Formats
**ID:** CON-STR-003
**Location:** Multiple files including `game/strategy/data/pathfinding.py`, `game/strategy/data/naming.py`, `game/strategy/data/planet.py`
**Issue:** Docstring styles are inconsistent across the module:
- Some use Google-style with Args/Returns sections (habitability.py, placement_strategies.py)
- Some use minimal one-line docstrings (naming.py methods)
- Some omit docstrings entirely for private methods
- Event classes in event_log.py use Attributes section while DTOs use different formats
**Impact:** Inconsistent documentation style increases cognitive load when reading code.
**Recommendation:** Standardize on Google-style docstrings with Args/Returns/Raises sections for all public methods. Private methods (_prefix) can use brief one-liners.
**Effort:** Complex

#### MAJOR: Mixed Method Verb Prefixes for Similar Operations
**ID:** CON-STR-004
**Location:** Multiple files
**Issue:** Similar retrieval operations use different verb prefixes:
- `get_` prefix: `get_system_at_hex()`, `get_planets_at_global_hex()`, `get_hp_display()`
- `find_` prefix: `find_path_deep_space()`, `find_nearest_system()`, `find_hybrid_path()`
- `calculate_` prefix: `calculate_intercept_point()`, `calculate_gravity_factor()`
- `scan_` prefix: `scan_designs()`
- `load_` prefix: `load_design_data()`
Pattern usage is mostly correct (find for search, get for retrieval, calculate for computation) but some exceptions exist.
**Impact:** Minor cognitive overhead when API discovery.
**Recommendation:** Document verb conventions:
- `get_*`: Direct retrieval from data structure (O(1) or O(log n))
- `find_*`: Search/scan operations (O(n) or pathfinding)
- `calculate_*`: Computation from inputs
- `load_*`: File/disk operations
- `scan_*`: Enumerate and filter
**Effort:** Simple

#### MAJOR: Inconsistent Use of TYPE_CHECKING Pattern
**ID:** CON-STR-005
**Location:** `game/strategy/data/pathfinding.py:8-11`, `game/strategy/services/fleet_navigation_service.py`, `game/strategy/engine/fleet_movement_engine.py:20-22`
**Issue:** TYPE_CHECKING guard usage is inconsistent:
- Some files import types inside TYPE_CHECKING block correctly
- Some files import inside function bodies instead (pathfinding.py:270, 308)
- Some files mix both approaches
**Impact:** Function-level imports for type hints create runtime overhead on every call; inconsistent patterns make code harder to maintain.
**Recommendation:** Standardize on TYPE_CHECKING block for all type-only imports. Move all such imports to module level with proper guards.
**Effort:** Simple

#### MINOR: Inconsistent Parameter Naming for Registry
**ID:** CON-STR-006
**Location:** `game/strategy/validation/superweapon_validator.py:21`, `game/strategy/services/component_inspector.py`, `game/strategy/adapters/simulation_adapter.py:46`
**Issue:** Component registry parameter naming varies:
- `component_registry: Dict[str, Any]` (validators)
- `registries: GameRegistries` (engines, adapters)
- `registry` (some internal methods)
**Impact:** API consumers must remember different parameter names for same concept.
**Recommendation:** Standardize on `registries: GameRegistries` for the full registry container, `component_registry` only when explicitly passing just the component dict.
**Effort:** Simple

#### MINOR: Inconsistent Boolean Property Naming
**ID:** CON-STR-007
**Location:** `game/strategy/data/fleet.py`, `game/strategy/data/ship_instance.py`, `game/strategy/data/planet.py`
**Issue:** Boolean properties/methods use mixed naming conventions:
- `is_` prefix: `is_building`, `is_operational`, `is_alive`, `is_derelict`
- `has_` prefix: `has_orders`, `has_space_shipyard`, `has_resources`
- `can_` prefix: `can_use_warp()`, `can_build_type()`
- No prefix: `combat_capable` (should be `is_combat_capable`)
Most usage is correct, but a few outliers exist.
**Impact:** Minor inconsistency in API.
**Recommendation:** Audit all boolean properties/methods:
- `is_*` for state queries
- `has_*` for possession/containment
- `can_*` for capability checks
**Effort:** Simple

#### MINOR: Dual Implementation of Same Logic
**ID:** CON-STR-008
**Location:** `game/strategy/engine/harvesting_engine.py:30-55` and `game/strategy/engine/harvesting_engine.py:247-273`
**Issue:** Module has both module-level functions (`get_harvester_info`, `get_harvester_from_registry`) and equivalent instance methods (`_get_harvester_info`, `_get_harvester_from_registry`). The instance methods simply delegate to the module functions.
**Impact:** Code duplication; unclear whether to use function or method.
**Recommendation:** Keep only the module-level functions (they're already used by other code). Remove the instance method wrappers or have instance methods be the canonical implementation.
**Effort:** Simple

#### MINOR: Inconsistent __init__.py Export Patterns
**ID:** CON-STR-009
**Location:** `game/strategy/__init__.py`, `game/strategy/validation/__init__.py`, `game/strategy/events/__init__.py`, `game/strategy/data/__init__.py`
**Issue:** Export patterns in __init__.py vary:
- validation/__init__.py: Imports and __all__ list
- events/__init__.py: No imports, no __all__
- data/__init__.py: No imports, no __all__
- services/__init__.py: No imports, no __all__
**Impact:** Inconsistent import ergonomics; some submodules require full path imports.
**Recommendation:** Either provide __all__ exports in all subpackages or remove from all. Recommend keeping validation pattern as the standard.
**Effort:** Simple

#### MINOR: Inconsistent Comment Style for Project References
**ID:** CON-STR-010
**Location:** Multiple files
**Issue:** PROJ-XX references in comments use varied formats:
- `PROJ-12 Phase 3:` (colon after phase)
- `PROJ-75 Phase 2-3:` (range)
- `PROJ-35:` (no phase)
- Some docstrings have extensive project history, others have none
**Impact:** Minor inconsistency in code archaeology.
**Recommendation:** Standardize on `PROJ-XX Phase N:` format. Consider limiting project references to module docstring only, not inline comments.
**Effort:** Simple

#### MINOR: Missing Type Hints on Return Types
**ID:** CON-STR-011
**Location:** `game/strategy/data/pathfinding.py:162`, `game/strategy/data/naming.py:48`
**Issue:** Some functions have partial type hints (parameters but no return type):
- `find_hybrid_path()` missing return type hint
- `get_system_name()` missing return type hint
Most functions are fully typed, but a few older functions lack return annotations.
**Impact:** Type checker cannot verify return type usage.
**Recommendation:** Add return type hints to all public functions.
**Effort:** Simple

#### INFO: Magic Numbers in Pathfinding
**ID:** CON-STR-012
**Location:** `game/strategy/data/pathfinding.py:111`, `game/strategy/data/pathfinding.py:421`
**Issue:** Magic numbers appear without named constants:
- `radius: int = 50` default in get_system_at_hex
- `max_turns=50` in calculate_intercept_point
- `0.1` tolerance for intercept synchronization
**Impact:** Values not documented; harder to tune.
**Recommendation:** Extract to named constants with documentation: `DEFAULT_SYSTEM_SEARCH_RADIUS = 50`, `MAX_INTERCEPT_PROJECTION_TURNS = 50`.
**Effort:** Simple

#### INFO: Legacy Adapter Pattern Documentation
**ID:** CON-STR-013
**Location:** `game/strategy/data/pathfinding.py:275-296`
**Issue:** _ChaserProxy class is documented as "intentional adapter pattern" with PROJ-42 review note. The pattern is valid but the class name uses leading underscore (private) while being used across module boundaries conceptually.
**Impact:** None - correctly documented as intentional.
**Recommendation:** Consider renaming to `ChaserAdapter` without underscore if it's part of the public API, or keep as-is if truly private to pathfinding module.
**Effort:** Simple

#### INFO: Event System Enums vs String Constants
**ID:** CON-STR-014
**Location:** `game/strategy/events/event_types.py`, `game/strategy/events/event_log.py`
**Issue:** EventType and EventCategory are str-based Enums (good pattern), but Event dataclass stores `event_type: str` and `category: str` instead of the enum types directly.
**Impact:** Loss of type safety when storing events.
**Recommendation:** Change Event dataclass to use `event_type: EventType` and `category: EventCategory` directly. The to_dict/from_dict methods already handle string conversion.
**Effort:** Simple

## Top 5 Priority Issues
1. **CON-STR-001 (CRITICAL)**: Inconsistent validator error handling - API contracts differ between validators, causing integration issues
2. **CON-STR-002 (MAJOR)**: Mixed engine initialization patterns - DI inconsistency makes engines harder to use correctly
3. **CON-STR-005 (MAJOR)**: Inconsistent TYPE_CHECKING usage - Function-level imports create runtime overhead
4. **CON-STR-003 (MAJOR)**: Inconsistent docstring formats - Documentation inconsistency affects maintainability
5. **CON-STR-004 (MAJOR)**: Mixed method verb prefixes - API discoverability issue
