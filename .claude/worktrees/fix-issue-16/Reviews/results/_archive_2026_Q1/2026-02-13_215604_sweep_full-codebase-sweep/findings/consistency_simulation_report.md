# Consistency Violations Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 69
- **Total Issues Found:** 21
- **Critical:** 2 | **Major:** 6 | **Minor:** 9 | **Info:** 4

## Findings

#### CRITICAL: Inconsistent Return Type Pattern for "Not Found" Scenarios
**ID:** CON-SIM-001
**Location:** `game/simulation/systems/battle_engine.py:352-357`, `game/simulation/entities/ship.py` (various methods)
**Issue:** `get_ship_by_name()` returns `None` on not-found, but some component lookup methods in Ship raise exceptions while others return `None`. The `get_ability()` method returns `None` on not-found, but `from_dict()` raises exceptions on missing data.
**Impact:** Callers must remember different error handling patterns for similar lookup operations. This increases cognitive load and bug potential.
**Recommendation:** Standardize to return `Optional[T]` for all lookup/query methods, and only raise exceptions for true error conditions (invalid state, invariant violations).
**Effort:** Medium

#### CRITICAL: Mixed Parameter Naming for Ship References
**ID:** CON-SIM-002
**Location:** Multiple files across `game/simulation/combat/`, `game/simulation/managers/`, `game/simulation/validation/`
**Issue:** Ship parameters use inconsistent naming: `ship` (dominant), `source_ship` (weapon_firing_system.py), `s` (battle_engine.py loops), `owner` (projectile.py). The `targeting_system.py` uses `ship` for shooter and `candidate`/`target` for targets, but `weapon_firing_system.py` uses `ship` and `target` inconsistently.
**Impact:** Makes it harder to understand method signatures at a glance, especially when refactoring or reviewing PRs.
**Recommendation:** Standardize to: `ship` for the primary actor, `target` for the combat target, `owner` for ownership relationships (projectiles), `source` for origin in events/attacks.
**Effort:** Medium

#### MAJOR: Inconsistent Ability Naming Suffix Pattern
**ID:** CON-SIM-003
**Location:** `game/simulation/components/abilities/markers.py:8`, `game/simulation/components/abilities/weapons.py:10-310`
**Issue:** Some ability classes end with `Ability` suffix (e.g., `WeaponAbility`, `ProjectileWeaponAbility`, `BeamWeaponAbility`, `SeekerWeaponAbility`, `VehicleLaunchAbility`) while others do not (e.g., `CommandAndControl`, `CombatPropulsion`, `ManeuveringThruster`, `ShieldProjection`, `CrewCapacity`).
**Impact:** Inconsistent class naming creates confusion about which classes are abilities. The registry uses string lookup by class name, making this inconsistency propagate to JSON configuration.
**Recommendation:** Adopt consistent naming: Either all ability classes have `Ability` suffix (preferred for explicitness) or none do. Given that `WeaponAbility` and `VehicleLaunchAbility` use the suffix, standardize all abilities to use it.
**Effort:** Complex (requires JSON data updates)

#### MAJOR: Docstring Format Inconsistency
**ID:** CON-SIM-004
**Location:** Multiple files across `game/simulation/`
**Issue:** Docstring formats are inconsistent: Some use Google style (`Args:`, `Returns:`), some use plain text, some have no docstrings. Examples:
- `battle_engine.py`: Google style with detailed documentation
- `targeting_system.py`: Google style
- `damage_calculator.py`: Google style
- `propulsion.py`: Minimal one-line docstrings
- `markers.py`: One-line docstrings without Args/Returns
- `crew.py`: No docstrings on `__init__` methods
**Impact:** Inconsistent documentation quality makes it harder to onboard new developers and understand APIs.
**Recommendation:** Standardize on Google-style docstrings for all public methods with Args/Returns sections. Use one-liners only for truly trivial methods.
**Effort:** Medium

#### MAJOR: Inconsistent `TYPE_CHECKING` Import Guard Usage
**ID:** CON-SIM-005
**Location:** `game/simulation/components/abilities/markers.py`, `game/simulation/components/abilities/crew.py`, `game/simulation/components/abilities/propulsion.py`
**Issue:** Most files correctly use `if TYPE_CHECKING:` guards for type-only imports to avoid circular dependencies (e.g., `battle_engine.py`, `targeting_system.py`). However, some ability files don't use this pattern despite having potential circular imports through Component references.
**Impact:** Inconsistent application of the pattern makes it unclear when it's required, potentially causing import issues as the codebase evolves.
**Recommendation:** Apply `TYPE_CHECKING` guards consistently: Use for all cross-module type hints, especially parent module references like `Component` and `Ship`.
**Effort:** Simple

#### MAJOR: Inconsistent Private Member Naming
**ID:** CON-SIM-006
**Location:** `game/simulation/components/abilities/base.py:163`, `game/simulation/systems/battle_engine.py:199`
**Issue:** Private members inconsistently use single underscore prefix:
- `_ai_factory` (battle_engine.py) - correct
- `_tags` (base.py) - correct
- `_base_damage`, `_base_range` (weapons.py) - correct
- `stack_group` (base.py:69) - public when it should be internal
- `damage_formula` (weapons.py:61) - public when it could be private
- `cooldown_timer` (weapons.py:99) - public when it could be private
**Impact:** Unclear API boundaries; difficult to know what is safe to use externally vs. implementation detail.
**Recommendation:** Prefix all internal implementation details with single underscore. Reserve public (no underscore) for intentional API surface.
**Effort:** Medium

#### MAJOR: Mixed Error Handling Patterns
**ID:** CON-SIM-007
**Location:** `game/simulation/services/design_loader.py:70-82`, `game/simulation/entities/ship_serialization.py:124-161`
**Issue:** Error handling patterns vary significantly:
- `SimulationDesignLoader.load_ship_from_design_data()`: Returns `None` on error (line 78-82)
- `ShipSerializer.from_dict()`: Raises `TypeError` on invalid input (line 141)
- `ShipDesignValidator`: Returns `ValidationResult` objects
- `BattleEngine.start()`: Raises `ValueError` on missing factory (line 269-272)
**Impact:** Callers must understand each method's error contract. Mixed patterns increase bug surface.
**Recommendation:** Establish clear conventions: Return `None`/`Optional` for "not found" cases, use `ValidationResult` for validation, raise exceptions only for programmer errors (wrong types, missing required dependencies).
**Effort:** Medium

#### MAJOR: Inconsistent Registry Access Pattern
**ID:** CON-SIM-008
**Location:** `game/simulation/components/ability_manager.py:44-48`, `game/simulation/validation/ship_validator.py:294`
**Issue:** Some code accesses `ABILITY_REGISTRY` directly from the module (ability_manager.py), while other code uses dependency-injected `registries` parameter (ship_validator.py). The validation rules correctly use DI with `registries` keyword argument, but ability instantiation bypasses this.
**Impact:** Makes testing harder, creates hidden global state dependencies, violates project DI conventions.
**Recommendation:** Inject `registries` for all registry access. The `AbilityManager.instantiate_abilities()` should accept registries parameter.
**Effort:** Medium

#### MINOR: Inconsistent Verb Prefix for Retrieval Methods
**ID:** CON-SIM-009
**Location:** Multiple files
**Issue:** Retrieval methods use inconsistent verb prefixes:
- `get_ship_by_name()` (battle_engine.py) - uses `get_`
- `find_nearest_edge()` (retreat_manager.py) - uses `find_`
- `get_ability()`, `get_abilities()` (ability_manager.py) - uses `get_`
- `find_valid_target()` (targeting_system.py) - uses `find_`
- `select_target()` (targeting_system.py) - uses `select_`
**Impact:** Minor cognitive overhead when choosing method names or searching for methods.
**Recommendation:** Standardize: `get_` for direct lookup by identifier, `find_` for search with criteria/calculation, `select_` only for operations involving choice/AI.
**Effort:** Simple

#### MINOR: Inconsistent Use of `Optional` vs Union with None
**ID:** CON-SIM-010
**Location:** `game/simulation/combat/targeting_system.py:14`, `game/simulation/systems/battle_engine.py:57`
**Issue:** Most files use `Optional[T]` for nullable types (correct), but some imports include both `Optional` and `Union` where only `Optional` is needed. Import statements vary: `from typing import Optional` vs `from typing import List, Optional, Tuple, Any`.
**Impact:** Minor inconsistency in type annotations.
**Recommendation:** Use `Optional[T]` for all nullable types. Keep imports alphabetically sorted within typing imports.
**Effort:** Simple

#### MINOR: Boolean Method Naming Inconsistency
**ID:** CON-SIM-011
**Location:** `game/simulation/systems/battle_engine.py:480`, `game/simulation/managers/retreat_manager.py:230`, `game/simulation/components/ability_manager.py:85`
**Issue:** Boolean-returning methods have inconsistent naming:
- `is_battle_over()` - uses `is_` prefix (correct)
- `is_retreating()` - uses `is_` prefix (correct)
- `has_ability()` - uses `has_` prefix (correct)
- `at_map_edge()` - missing `is_` prefix, should be `is_at_map_edge()`
- `can_fire()` - uses `can_` prefix (correct)
- `applies_to_layer()` - uses plain verb, could be `is_applicable_to_layer()`
**Impact:** Minor readability issue.
**Recommendation:** Use `is_`, `has_`, `can_`, `should_` prefixes consistently for all boolean-returning methods.
**Effort:** Simple

#### MINOR: Inconsistent Class vs Static Method Usage
**ID:** CON-SIM-012
**Location:** `game/simulation/components/ability_manager.py`, `game/simulation/components/modifier_manager.py`
**Issue:** Both `AbilityManager` and `ModifierManager` use `@staticmethod` for all methods. However, `Ability` base class uses `@classmethod` for introspection methods (`get_consumed_stats`, `get_stat_bindings_info`). The choice between static and class methods is inconsistent.
**Impact:** Minor confusion about when to use which pattern.
**Recommendation:** Use `@staticmethod` for pure utility functions that don't need class reference, `@classmethod` for factory methods or methods that need to know their class for polymorphism.
**Effort:** Simple

#### MINOR: Inconsistent Constant Definition Style
**ID:** CON-SIM-013
**Location:** `game/simulation/physics_constants.py`, `game/simulation/managers/retreat_manager.py:50`
**Issue:** Constants are defined in multiple ways:
- `physics_constants.py`: Module-level constants (UPPER_SNAKE_CASE)
- `RetreatManager.DEFAULT_EDGE_THRESHOLD`: Class-level constant (also UPPER_SNAKE_CASE, correct)
- Magic numbers still present: `0.01` in weapons.py (epsilon), `100` in various damage calculations
**Impact:** Magic numbers reduce code clarity.
**Recommendation:** Extract magic numbers to named constants. Use `physics_constants.py` or relevant module constants for simulation values.
**Effort:** Simple

#### MINOR: Import Organization Inconsistency
**ID:** CON-SIM-014
**Location:** Multiple files
**Issue:** Import organization varies:
- Some files: stdlib -> third-party -> local (correct)
- Some files: Mixed ordering
- `from game.x.y import z` style used consistently (good)
- Relative imports used correctly within packages (good)
**Impact:** Minor readability issue.
**Recommendation:** Enforce consistent import ordering with isort or similar tool.
**Effort:** Simple

#### MINOR: Inconsistent Method Ordering in Classes
**ID:** CON-SIM-015
**Location:** `game/simulation/systems/battle_engine.py`, `game/simulation/entities/ship.py`
**Issue:** Method ordering varies between classes:
- Some: `__init__` -> properties -> public methods -> private methods
- Some: `__init__` -> mixed public/private
- `BattleEngine`: properties defined mid-class instead of after `__init__`
**Impact:** Minor readability issue when navigating large classes.
**Recommendation:** Standardize method ordering: `__init__` -> `__str__`/`__repr__` -> properties -> public methods -> private methods (`_` prefix).
**Effort:** Simple

#### MINOR: Inconsistent Line Length in Docstrings
**ID:** CON-SIM-016
**Location:** Multiple files
**Issue:** Some docstrings wrap at ~80 chars, others extend to 100+. Module docstrings in `battle_engine.py` are well-formatted, but inline docstrings vary widely.
**Impact:** Minor visual inconsistency.
**Recommendation:** Configure formatter to wrap docstrings consistently at project line length (likely 100 or 120).
**Effort:** Simple

#### INFO: Natural Variation in Ability Structure
**ID:** CON-SIM-017
**Location:** `game/simulation/components/abilities/` directory
**Issue:** Abilities have structural variation based on their nature:
- Weapon abilities have `reload_time`, `damage`, `range`
- Resource abilities have `resource_type`, `amount`
- Marker abilities have no fields beyond base
This is natural variation, not an inconsistency.
**Impact:** None - this is appropriate domain modeling.
**Recommendation:** No change needed. Document this as intentional in ability design docs.
**Effort:** N/A

#### INFO: Validation Rule Template Method Pattern
**ID:** CON-SIM-018
**Location:** `game/simulation/validation/base.py`, `game/simulation/validation/ship_validator.py`
**Issue:** The validation system uses a well-implemented template method pattern with `ValidationRule`, `AdditionValidationRule`, and `DesignValidationRule` base classes. All rules correctly implement `_do_validate()`. This is good consistency.
**Impact:** Positive - clean pattern implementation.
**Recommendation:** Document this pattern as the standard for new validation rules.
**Effort:** N/A

#### INFO: Consistent Use of STAT_BINDINGS
**ID:** CON-SIM-019
**Location:** `game/simulation/components/abilities/` (all ability files)
**Issue:** All abilities consistently declare `STAT_BINDINGS` class variable, even when empty for marker abilities. The `recalculate()` method pattern is consistently applied. This is good consistency.
**Impact:** Positive - clean pattern implementation.
**Recommendation:** Document this pattern as the standard for new abilities.
**Effort:** N/A

#### INFO: Protocol Pattern for AI Controller
**ID:** CON-SIM-020
**Location:** `game/simulation/interfaces/ai_controller.py`
**Issue:** The `IAIController` and `IAIControllerFactory` protocols use `@runtime_checkable` decorator and proper Protocol inheritance. This enables clean layer separation between simulation and AI. This is good pattern usage.
**Impact:** Positive - enables proper layer boundaries.
**Recommendation:** Document this pattern for other cross-layer interfaces.
**Effort:** N/A

#### INFO: Consistent Use of TYPE_CHECKING in Core Files
**ID:** CON-SIM-021
**Location:** `game/simulation/systems/battle_engine.py`, `game/simulation/combat/*.py`
**Issue:** Core combat files consistently use `if TYPE_CHECKING:` guards for cross-module imports. This prevents circular import issues and is well-applied. Minor inconsistency in ability files noted separately.
**Impact:** Positive where applied.
**Recommendation:** Extend pattern to ability files as noted in CON-SIM-005.
**Effort:** N/A

## Top 5 Priority Issues

1. **CON-SIM-001 (CRITICAL)**: Inconsistent Return Type Pattern - Standardize lookup methods to return `Optional[T]` or raise exceptions consistently
2. **CON-SIM-002 (CRITICAL)**: Mixed Parameter Naming - Establish naming conventions for ship/target/owner parameters
3. **CON-SIM-003 (MAJOR)**: Ability Naming Suffix - Decide on consistent `Ability` suffix usage across all ability classes
4. **CON-SIM-007 (MAJOR)**: Mixed Error Handling - Document and standardize error handling patterns (None vs ValidationResult vs exceptions)
5. **CON-SIM-008 (MAJOR)**: Registry Access Pattern - Migrate `ABILITY_REGISTRY` direct access to dependency injection
