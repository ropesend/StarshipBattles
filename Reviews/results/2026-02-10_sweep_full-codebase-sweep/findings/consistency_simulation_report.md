# Consistency Violations Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 72
- **Total Issues Found:** 20
- **Critical:** 3 | **Major:** 7 | **Minor:** 5 | **Info:** 5

## Findings

#### CRITICAL: Inconsistent Result Type Naming (BattleResults vs BattleResult)
**ID:** CON-SIM-001
**Location:** `game/simulation/battle_state.py:645` (BattleResults plural) AND `game/simulation/services/battle_service.py:20` (BattleResult singular)
**Issue:** Two different result classes with inconsistent naming for similar concepts.
**Impact:** API consumers must remember two different conventions. Risk of using wrong type.
**Recommendation:** Rename BattleResult to BattleServiceResult to differentiate purpose.
**Effort:** Complex

#### CRITICAL: Inconsistent get_winner() Return Type
**ID:** CON-SIM-002
**Location:** `game/simulation/systems/battle_engine.py:655` (returns int) AND `game/simulation/services/battle_service.py:262` (returns Optional[int])
**Issue:** Same method name returns different types. BattleEngine assumes valid state, BattleService handles None.
**Impact:** Silent type inconsistency could cause crashes if service layer returns None when caller expects int.
**Recommendation:** Standardize both to Optional[int].
**Effort:** Medium

#### CRITICAL: Missing Return Type Hints on Key Methods
**ID:** CON-SIM-003
**Location:** `game/simulation/entities/ship_stats.py:65-533` (20+ methods), `game/simulation/components/abilities/weapons.py:151,181,214`, `game/simulation/entities/combat_endurance.py:9,138`
**Issue:** Core stat calculation and ability methods lack return type hints despite being high-impact APIs.
**Impact:** Type checkers cannot verify correctness. Increases regression risk.
**Recommendation:** Add comprehensive return type hints to all public methods (~50 locations).
**Effort:** Medium

#### MAJOR: Inconsistent Optional vs Empty Collection Return Pattern
**ID:** CON-SIM-004
**Location:** `game/simulation/systems/resource_manager.py:114-200`, `game/simulation/projectile_manager.py:18`, `game/simulation/services/battle_service.py:306,321`
**Issue:** Similar "get collection" methods use different patterns: Optional vs empty lists.
**Impact:** Callers must remember which methods are nullable.
**Recommendation:** Prefer empty collections over Optional for collection returns.
**Effort:** Medium

#### MAJOR: Inconsistent Error Handling Exception Types
**ID:** CON-SIM-005
**Location:** `game/simulation/battle_controller.py:612,622` (ValueError), `game/simulation/managers/battle_state_manager.py:50,79` (RuntimeError), `game/simulation/combat/battle_mode_handler.py:226,301` (ValueError)
**Issue:** Similar validation failures raise different exception types with no documented reason.
**Impact:** Callers cannot reliably catch specific error types.
**Recommendation:** Define exception hierarchy: ValueError for data, RuntimeError for state violations.
**Effort:** Medium

#### MAJOR: Ability Class Method Naming Inconsistency
**ID:** CON-SIM-006
**Location:** Ability subclasses across game/simulation/components/abilities/
**Issue:** WeaponAbility adds recalculate() but others use sync_data(). No documented pattern for which lifecycle method to use.
**Impact:** Polymorphic code cannot reliably call methods on Ability instances.
**Recommendation:** Define clear lifecycle methods in base Ability class.
**Effort:** Complex

#### MAJOR: Inconsistent Docstring Patterns in Manager/Service Classes
**ID:** CON-SIM-007
**Location:** modifier_manager.py, component_health_manager.py, component_resource_manager.py, retreat_manager.py
**Issue:** Manager classes have inconsistent purposes: some are pure utility namespaces (static), others are instance managers. No clear pattern.
**Impact:** New code doesn't know whether to instantiate managers or call static methods.
**Recommendation:** Rename to clarify: *Manager = instance, *Utils = static namespace.
**Effort:** Medium

#### MAJOR: Inconsistent Type Hints for Data Parameters
**ID:** CON-SIM-008
**Location:** Ability classes, Component class, various methods accepting `data` parameter
**Issue:** data parameter sometimes typed as Dict[str, Any], sometimes untyped. No validation that data matches expected schema.
**Impact:** Runtime errors from malformed data not caught early.
**Recommendation:** Create typed dataclasses for data structures.
**Effort:** Complex

#### MAJOR: Inconsistent Lazy Initialization Patterns
**ID:** CON-SIM-009
**Location:** ship_stat_querier.py:45-50, component.py:440-451, ship.py:82-87, battle_controller.py:101-104
**Issue:** Different lazy init patterns: inline checks, factory pattern, thread-safe singletons. Thread-safety varies by location.
**Impact:** Inconsistent object lifecycle. Hard to predict creation timing.
**Recommendation:** Define single lazy init pattern (e.g., @cached_property).
**Effort:** Medium

#### MAJOR: Inconsistent Facade Pattern on Ship Class
**ID:** CON-SIM-010
**Location:** `game/simulation/entities/ship.py`
**Issue:** Some extracted classes have public facade methods, others don't. No consistent naming for facade methods. ShipStatQuerier and ShipValidatorHelper inconsistently exposed.
**Impact:** Callers uncertain which class to use for functionality.
**Recommendation:** Document facade pattern. Expose all extracted classes via Ship properties.
**Effort:** Medium

#### MAJOR: Inconsistent to_dict/from_dict Implementation
**ID:** CON-SIM-011
**Location:** battle_state.py (comprehensive), abilities/base.py (none), layer_data.py (limited)
**Issue:** Serialization patterns differ across classes. Some have full to_dict/from_dict, others none.
**Impact:** Cannot reliably serialize all objects.
**Recommendation:** Implement to_dict/from_dict on all persistent entities.
**Effort:** Medium

#### MINOR: Parameter Naming Inconsistency
**ID:** CON-SIM-012
**Location:** Resource methods use `name`, ship methods use `ship_id`, component methods use `mod_id`
**Issue:** ID parameter names vary without pattern.
**Impact:** Low - IDE handles it, but inconsistent API style.
**Recommendation:** Use _id suffix for all IDs, name only for display names.
**Effort:** Simple

#### MINOR: Docstring Completeness Varies
**ID:** CON-SIM-013
**Location:** damage_calculator.py (excellent), retreat_manager.py (sparse), ship_physics.py (none)
**Issue:** Docstring quality varies significantly across files.
**Impact:** Inconsistent comprehension difficulty.
**Recommendation:** Enforce docstring format with linting.
**Effort:** Simple

#### MINOR: Inconsistent Method Ordering in Classes
**ID:** CON-SIM-014
**Location:** ship.py properties scattered throughout
**Issue:** No consistent method organization pattern.
**Impact:** Harder to navigate large classes.
**Recommendation:** Adopt standard: __init__, properties, public methods, private methods.
**Effort:** Simple

#### MINOR: Inconsistent Default Parameter Values
**ID:** CON-SIM-015
**Location:** component.py:346, design_loader.py (hardcoded paths)
**Issue:** Default values vary: None, empty objects, literal values without consistent convention.
**Impact:** Hard to predict what None means.
**Recommendation:** Use None for optional, factory functions for mutable defaults.
**Effort:** Simple

#### MINOR: Missing Module-Level Constants
**ID:** CON-SIM-016
**Location:** Multiple files using magic numbers (0.01 for TICK_RATE, string keys 'fuel', 'energy')
**Issue:** Repeated literals instead of named constants.
**Impact:** Fragile if resource types expand.
**Recommendation:** Define constants in game/core/constants.py.
**Effort:** Simple

#### INFO: Unused Imports in Several Files
**ID:** CON-SIM-017
**Location:** damage_calculator.py, several ability files
**Issue:** Some modules import more than they use (common after refactoring).
**Impact:** Negligible.
**Recommendation:** Run flake8 F401 cleanup.
**Effort:** Simple

#### INFO: Inconsistent Test Data Naming
**ID:** CON-SIM-018
**Location:** Test fixtures use ship_data vs ship_dict vs data inconsistently
**Issue:** Test setup code naming varies.
**Impact:** Low - slows test development.
**Recommendation:** Establish test naming convention.
**Effort:** Simple

#### INFO: Docstring Cross-Reference Format
**ID:** CON-SIM-019
**Location:** Various docstrings
**Issue:** Some reference classes as Ship, others as 'Ship', others with full module path.
**Impact:** Low - affects documentation generation.
**Recommendation:** Standardize format.
**Effort:** Simple

#### INFO: Inconsistent Comment Style
**ID:** CON-SIM-020
**Location:** Various files
**Issue:** Mixed comment prefixes (PROJ-XX:, NOTE:, INTENTIONAL:, FIXME:).
**Impact:** Low - makes searching harder.
**Recommendation:** Standardize comment prefixes.
**Effort:** Simple

## Top 5 Priority Issues
1. **CON-SIM-001**: BattleResults vs BattleResult naming - API confusion
2. **CON-SIM-002**: get_winner() return type mismatch - risk of unhandled None
3. **CON-SIM-003**: Missing return type hints - blocks static analysis
4. **CON-SIM-006**: Ability lifecycle method inconsistency - breaks polymorphism
5. **CON-SIM-009**: Lazy initialization pattern inconsistency - thread safety concerns
