# Consistency Violations Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 70
- **Total Issues Found:** 17
- **Critical:** 0 | **Major:** 5 | **Minor:** 9 | **Info:** 3

## Findings

#### MAJOR: Mixed return conventions for "not found" scenarios
**ID:** CON-SIM-001
**Location:** `game/simulation/systems/resource_manager.py:120-126`, `game/simulation/components/modifier_manager.py:109-126`
**Issue:** Inconsistent return conventions across the module. `ResourceRegistry.get_resource()` returns `Optional[ResourceState]` (None on not-found), while some similar lookup methods return default values directly. `get_value()` returns 0.0 for missing resources without indicating absence.
**Impact:** Cognitive overhead distinguishing between "resource not registered" vs "resource is at 0". Callers must remember which methods use which convention.
**Recommendation:** Adopt consistent Optional[T] return type for lookups. Add `has_resource(name)` for explicit existence checks, or document the "0.0 = missing" convention explicitly.
**Effort:** Medium

#### MAJOR: Inconsistent docstring format across modules
**ID:** CON-SIM-002
**Location:** Multiple files throughout `game/simulation/`
**Issue:** Docstring styles are inconsistent:
- Some use Google-style with Args/Returns sections (`retreat_manager.py`, `battle_service.py`)
- Some use brief single-line docstrings (`ship_physics.py`, `crew.py`)
- Some have no docstrings on public methods (`ability_aggregator.py:_aggregate_ability_groups`)
**Impact:** Inconsistent API documentation makes codebase harder to navigate. IDE tooling shows inconsistent help.
**Recommendation:** Standardize on Google-style docstrings for all public APIs (Args, Returns, Raises sections). Private methods can use brief docstrings.
**Effort:** Medium

#### MAJOR: Inconsistent use of is_ vs has_ boolean method prefixes
**ID:** CON-SIM-003
**Location:** `game/simulation/components/component.py`, `game/simulation/entities/ship.py`
**Issue:** Boolean checking methods use inconsistent prefixes:
- `is_operational`, `is_active`, `is_alive` (state properties)
- `has_ability()`, `has_pdc_ability()` (capability checks)
- But `applies_to_layer()` (returns bool, no prefix)
- And `can_afford_activation()`, `can_fire()` (capability checks with `can_` prefix)
**Impact:** Users must guess which prefix to use for new methods. Three different conventions (is_, has_, can_) overlap in meaning.
**Recommendation:** Establish convention: `is_` for state, `has_` for presence checks, `can_` for capability/permission checks. Document in CLAUDE.md.
**Effort:** Simple

#### MAJOR: Parameter ordering inconsistency for ship/component methods
**ID:** CON-SIM-004
**Location:** `game/simulation/combat/targeting_system.py`, `game/simulation/combat/weapon_firing_system.py`
**Issue:** Methods receiving both `ship` and `component` parameters vary in order:
- `_process_weapon_fire(ship, comp, context)` - ship first
- `calculate_firing_solution(ship, comp, target)` - ship first
- But `DamageCalculator._damage_layer(ship, layer_type, damage)` - ship first, no comp
The pattern is mostly consistent (ship first), but `Component.recalculate_stats(context)` receives ship via `self.ship` reference.
**Impact:** Minor confusion when calling APIs. Some methods expect ship as explicit param, others access via self reference.
**Recommendation:** For module-level functions: ship first, then component, then other params. Document in CLAUDE.md.
**Effort:** Simple

#### MAJOR: Facade pattern inconsistently applied in decomposed classes
**ID:** CON-SIM-005
**Location:** `game/simulation/entities/ship.py`, `game/simulation/components/component.py`
**Issue:** God class decomposition (PROJ-12, PROJ-88) extracts logic to helper classes but applies facade pattern inconsistently:
- `Component` has facade methods like `take_damage()` that delegate to `health_manager.take_damage()`
- `Component` also exposes direct access to `resource_manager` property
- `Ship` similarly mixes facade methods with direct sub-manager access
Some callers use `component.take_damage()`, others could access `component.health_manager.take_damage()`.
**Impact:** Two access patterns exist for the same operations, making it unclear which is preferred.
**Recommendation:** Prefer complete facades - all public operations should go through the main class. Make sub-managers private (`_health_manager`) or document that direct access is acceptable.
**Effort:** Medium

#### MINOR: Inconsistent private member naming with underscore prefix
**ID:** CON-SIM-006
**Location:** `game/simulation/entities/ship.py`, `game/simulation/components/component.py`
**Issue:** Some private members use underscore prefix, others don't:
- `_registries`, `_hp_ratio_dirty`, `_cached_hp_ratio` (underscore)
- `stats`, `modifiers`, `ability_instances` (no underscore, but internal)
- `_resource_mgr`, `_health_mgr` (underscore for lazy-init managers)
**Impact:** Unclear which attributes are part of public API vs internal implementation.
**Recommendation:** Use underscore prefix for all non-public attributes. Document public attributes in class docstring.
**Effort:** Medium

#### MINOR: Logger initialization patterns vary
**ID:** CON-SIM-007
**Location:** `game/simulation/components/modifiers.py:10-11`, vs other files
**Issue:** Most files use `from game.core.logger import log_warning, log_error` (function imports), but `modifiers.py` uses `import logging; logger = logging.getLogger(__name__)`.
**Impact:** Two logging patterns in the same codebase. The `game.core.logger` functions provide centralized configuration.
**Recommendation:** Standardize on `game.core.logger` function imports (`log_debug`, `log_info`, `log_warning`, `log_error`).
**Effort:** Simple

#### MINOR: Inconsistent exception handling patterns
**ID:** CON-SIM-008
**Location:** `game/simulation/services/design_loader.py:70-82`, `game/simulation/entities/ship_serialization.py:103-107`
**Issue:** Error handling varies:
- Some methods catch specific exceptions and return None/False with error message
- Some catch broad `Exception` and re-raise after logging
- Some use `ValidationException` from core, others raise standard exceptions
**Impact:** Callers must handle different error patterns from similar operations.
**Recommendation:** Establish pattern: Use specific exceptions, let them propagate for callers to catch. Only catch-and-wrap when adding context. Return Optional types for "not found" scenarios (not for errors).
**Effort:** Medium

#### MINOR: Ability class naming suffix inconsistency
**ID:** CON-SIM-009
**Location:** `game/simulation/components/abilities/`
**Issue:** Ability classes use inconsistent naming:
- `WeaponAbility`, `ProjectileWeaponAbility` - `Ability` suffix
- `ResourceConsumption`, `ResourceStorage` - no suffix
- `CombatPropulsion`, `ManeuveringThruster` - no suffix
- `VehicleLaunchAbility` - has suffix
**Impact:** Cannot reliably predict class name from ability type. Some abilities called "Ability", others not.
**Recommendation:** Either all ability classes end in `Ability` suffix, or none do. Current pattern seems to be: weapon abilities use suffix, others don't. Document this convention.
**Effort:** Medium (breaking change if renamed)

#### MINOR: Constants defined in multiple locations
**ID:** CON-SIM-010
**Location:** `game/simulation/projectile.py:8-11`, `game/simulation/physics_constants.py`
**Issue:** `TURN_COMMITMENT_THRESHOLD_DEG` defined locally in `projectile.py`. Other physics constants are in `physics_constants.py` or `game.core.constants.SimulationConstants`.
**Impact:** When looking for a constant, unclear which file contains it.
**Recommendation:** Move all simulation-specific constants to `physics_constants.py` or `game.core.constants.SimulationConstants`.
**Effort:** Simple

#### MINOR: Method naming verb inconsistency for retrieval operations
**ID:** CON-SIM-011
**Location:** Various files in `game/simulation/`
**Issue:** Retrieval methods use different verbs:
- `get_resource()`, `get_ability()`, `get_modifier()` - "get" prefix (most common)
- `find_nearest_edge()`, `find_valid_target()` - "find" for computed searches
- `calculate_firing_solution()`, `calculate_ability_totals()` - "calculate" for computation
- `load_ship_from_file()` - "load" for file I/O
The pattern is mostly sensible (get=lookup, find=search, calculate=compute, load=I/O) but some overlap.
**Impact:** Minor cognitive load choosing the right verb.
**Recommendation:** Document the verb convention: `get_` = direct lookup (O(1) or cached), `find_` = search/filter (may iterate), `calculate_` = compute from data, `load_` = I/O.
**Effort:** Simple

#### MINOR: Inconsistent type hints for callable parameters
**ID:** CON-SIM-012
**Location:** `game/simulation/managers/retreat_manager.py:132-134`
**Issue:** Callable parameters typed inconsistently:
- `Callable[[str], Optional['Ship']]` - positional form
- Some methods lack type hints entirely for callbacks
**Impact:** IDE support varies across methods.
**Recommendation:** Use full type hints for all callback parameters. Consider using Protocol for complex callbacks.
**Effort:** Simple

#### MINOR: Inconsistent use of dataclasses vs regular classes
**ID:** CON-SIM-013
**Location:** `game/simulation/managers/retreat_manager.py:28-35`, `game/simulation/services/vehicle_design_service.py:22-29`
**Issue:** Simple data containers use both patterns:
- `RetreatState` is a `@dataclass`
- `DesignResult` is a `@dataclass`
- But `BattleConfig`, `BattleEndCondition` are regular classes with `__init__`
**Impact:** Inconsistent patterns for similar purposes.
**Recommendation:** Use dataclasses for pure data containers. Use regular classes when custom __init__ logic or methods are needed. Current usage is reasonable, just document the guideline.
**Effort:** Simple

#### INFO: Import organization varies slightly
**ID:** CON-SIM-014
**Location:** All files in `game/simulation/`
**Issue:** Import organization is mostly consistent (stdlib, third-party, local) but some files group TYPE_CHECKING imports differently. Some put `if TYPE_CHECKING:` block at end of imports, others in middle.
**Impact:** Very minor readability difference.
**Recommendation:** Standardize: stdlib imports, then third-party, then local, then `if TYPE_CHECKING:` block last.
**Effort:** Simple

#### INFO: Some __init__.py files export different subsets
**ID:** CON-SIM-015
**Location:** `game/simulation/__init__.py`, `game/simulation/components/__init__.py`
**Issue:** The main `__init__.py` exports a curated public API. Subpackage `__init__.py` files vary - some export everything, some export nothing.
**Impact:** Unclear what's part of public API at each level.
**Recommendation:** Document which classes are part of the public API. Main `__init__.py` already does this well. Subpackage `__init__.py` can remain minimal.
**Effort:** Simple

#### INFO: Two-stage aggregation pattern well-documented but implicit
**ID:** CON-SIM-016
**Location:** `game/simulation/entities/ability_aggregator.py`
**Issue:** The two-stage aggregation pattern (collect abilities, then apply modifiers) is documented in CLAUDE.md but the actual implementation in `_aggregate_ability_groups()` doesn't reference this pattern by name.
**Impact:** Developers must connect documentation to implementation.
**Recommendation:** Add comment in code referencing the two-stage aggregation pattern: "Phase 1: Intra-group MAX (redundancy). Phase 2: Inter-group SUM/MULT (stacking)."
**Effort:** Simple

#### MINOR: Duplicate code between ability recalculate() methods
**ID:** CON-SIM-017
**Location:** `game/simulation/components/abilities/resources.py:43-44`, `crew.py:20-21`, etc.
**Issue:** Many ability classes have nearly identical `recalculate()` implementations:
```python
def recalculate(self):
    self.attribute = self._base_attribute * self.get_effective_stat('stat_mult', 1.0)
```
The `STAT_BINDINGS` system was introduced to declare these bindings but the actual recalculation logic still duplicates the pattern.
**Impact:** Adding new bindings requires copying the same pattern. Risk of inconsistency.
**Recommendation:** Consider a base class method that applies all STAT_BINDINGS automatically, so subclasses only need to override for special cases (like CrewRequired's sqrt scaling).
**Effort:** Medium

## Top 5 Priority Issues

1. **CON-SIM-005 (MAJOR): Facade pattern inconsistently applied** - The god class decomposition is a major architectural pattern but the access patterns are unclear. Should be resolved to prevent divergent usage patterns.

2. **CON-SIM-001 (MAJOR): Mixed return conventions** - Fundamental API consistency issue. Affects how callers handle errors and missing data. Should establish clear convention.

3. **CON-SIM-002 (MAJOR): Inconsistent docstring format** - Documentation quality directly impacts developer productivity. Google-style docstrings should be the standard.

4. **CON-SIM-003 (MAJOR): Boolean method prefix inconsistency** - `is_`, `has_`, `can_` prefixes overlap. Document clear convention to prevent proliferation of inconsistent naming.

5. **CON-SIM-017 (MINOR): Duplicate recalculate() patterns** - The STAT_BINDINGS framework was designed to reduce this duplication but isn't fully leveraged. Good opportunity to reduce boilerplate.
