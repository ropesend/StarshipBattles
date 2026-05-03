# Consistency Violations Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 67
- **Total Issues Found:** 21
- **Critical:** 1 | **Major:** 5 | **Minor:** 12 | **Info:** 3

## Findings

#### CRITICAL: Inconsistent Return Type for Not-Found Scenarios
**ID:** CON-SIM-001
**Location:** `game/simulation/components/component.py:679-704` vs `game/simulation/services/battle_service.py:274-289`
**Issue:** `create_component()` returns `None` on not-found, while similar factory methods like `BattleService.get_winner()` have explicit return type documentation. However, `add_modifier()` returns `False` on not-found (boolean). This creates API inconsistency: some methods return None, others return False for failure cases.
**Impact:** Callers must know each method's failure semantics. A caller checking `if not result:` catches both None and False but loses context. This pattern is inconsistent across the codebase.
**Recommendation:** Standardize on Result objects (like `BattleServiceResult`) for operations that can fail, or consistently use Optional[T] with None for missing/failure across all factory and lookup methods.
**Effort:** Medium

#### MAJOR: Inconsistent Method Verb Prefixes for Retrieval
**ID:** CON-SIM-002
**Location:** Multiple files
**Issue:** Retrieval methods use inconsistent verb prefixes:
- `get_ability()`, `get_abilities()` - in component.py
- `find_valid_target()`, `find_nearest_edge()` - in targeting_system.py, retreat_manager.py
- `get_ship_by_name()` - in battle_engine.py
- `select_target()` - in targeting_system.py

The pattern `find_*` implies searching/calculation while `get_*` implies direct access. `select_*` implies making a choice. These are used interchangeably.
**Impact:** Cognitive overhead when reading code - developer must understand each method to know if it does a simple lookup or complex search.
**Recommendation:** Establish convention: `get_*` for O(1) direct access, `find_*` for O(n) searches or calculations, `select_*` for heuristic/AI choices.
**Effort:** Medium

#### MAJOR: Mixed Docstring Formats
**ID:** CON-SIM-003
**Location:** Throughout simulation layer
**Issue:** Docstrings inconsistently formatted:
- Some use Google style with `Args:` and `Returns:` sections (e.g., `battle_state.py`, `battle_engine.py`)
- Some use reST style with `:param:` (rare but present in older code)
- Some have only single-line descriptions with no parameter documentation
- `Raises:` section inconsistently documented - sometimes present, often missing even when exceptions are raised
**Impact:** Documentation inconsistency reduces readability and IDE support quality.
**Recommendation:** Standardize on Google-style docstrings throughout. Add `Raises:` section to all methods that raise exceptions.
**Effort:** Complex

#### MAJOR: Inconsistent Error Handling Patterns
**ID:** CON-SIM-004
**Location:** `game/simulation/battle_controller.py:256-261` vs `game/simulation/services/battle_service.py:183-195`
**Issue:** Error handling varies:
- `run_headless()` raises `StateException` for "not started"
- `update()` returns `BattleServiceResult(success=False, errors=...)` for same condition
- `start_battle()` in `BattleService` also returns result object

Both methods on same class have different error semantics for the same precondition failure.
**Impact:** Callers must use both try/except AND result checking. Inconsistent contracts.
**Recommendation:** Standardize: Use `BattleServiceResult` for all operations that can fail gracefully, raise exceptions only for programmer errors (invariant violations).
**Effort:** Medium

#### MAJOR: Ability Class Naming Inconsistency
**ID:** CON-SIM-005
**Location:** `game/simulation/components/abilities/`
**Issue:** Ability class naming patterns are inconsistent:
- Some use `*Ability` suffix: `WeaponAbility`, `SeekerWeaponAbility`
- Some omit suffix: `ShieldProjection`, `ShieldRegeneration`, `CombatPropulsion`
- Some use noun form: `CrewCapacity`, `LifeSupportCapacity`
- Registry key also inconsistent: `"VehicleLaunch": VehicleLaunchAbility` (registry key omits suffix, class has it)
**Impact:** Hard to predict class name from ability name and vice versa.
**Recommendation:** All ability classes should use `*Ability` suffix. Update registry to match: `"VehicleLaunchAbility": VehicleLaunchAbility`.
**Effort:** Complex (requires updating JSON data files referencing old names)

#### MAJOR: Inconsistent Use of TYPE_CHECKING Guard
**ID:** CON-SIM-006
**Location:** `game/simulation/services/design_loader.py:26` vs `game/simulation/entities/ship.py:1-25`
**Issue:** TYPE_CHECKING import pattern inconsistent:
- `design_loader.py` imports `GameRegistries` inside TYPE_CHECKING block incorrectly as `from game.core.registries` (should be `game.core.registry`)
- Most files use `if TYPE_CHECKING:` block for Ship imports
- Some files use late imports inside methods instead
- `ship.py` uses both - TYPE_CHECKING for some, late imports for others
**Impact:** Inconsistent patterns make circular import issues harder to debug.
**Recommendation:** Standardize: Use TYPE_CHECKING block for all type-only imports. Document intentional late imports with comment.
**Effort:** Simple

#### MINOR: Boolean Parameter Naming
**ID:** CON-SIM-007
**Location:** Multiple files
**Issue:** Boolean parameters inconsistently named:
- `operational_only` (good - describes filter)
- `enable_logging` (good - describes action)
- `migrate_components` (good - describes action)
- Some methods lack `is_`/`has_`/`should_` prefixes where they would clarify

Most boolean parameters are well-named, but a few could be clearer (e.g., `check_derelict` in battle_end_conditions could be `should_check_derelict`).
**Impact:** Minor readability issue.
**Recommendation:** Consider `should_*` prefix for boolean parameters that control behavior.
**Effort:** Simple

#### MINOR: Inconsistent Private Member Naming
**ID:** CON-SIM-008
**Location:** Throughout simulation layer
**Issue:** Private member naming inconsistent:
- Single underscore for private: `_registries`, `_engine`, `_combat_engine`
- Double underscore rare (correctly avoided for name mangling)
- Some "private" methods lack underscore: `solve_lead()` in TargetingSystem (internal algorithm, not part of public API)
**Impact:** Unclear which methods are internal implementation details.
**Recommendation:** Consistently use single underscore for internal methods not intended as public API.
**Effort:** Simple

#### MINOR: Magic Numbers in Physics Calculations
**ID:** CON-SIM-009
**Location:** `game/simulation/entities/ship_stats.py:170-176`
**Issue:** Magic numbers in defense score calculation:
- `80.0` (baseline diameter)
- `-2.5` (size score coefficient)
- `20.0`, `360.0` (maneuver score divisors)

These lack named constants despite `physics_constants.py` existing for similar values.
**Impact:** Hard to tune/understand physics without context.
**Recommendation:** Move magic numbers to `physics_constants.py` with descriptive names like `DEFENSE_BASELINE_DIAMETER`, `DEFENSE_SIZE_COEFFICIENT`.
**Effort:** Simple

#### MINOR: Inconsistent sync_data Method Implementation
**ID:** CON-SIM-010
**Location:** `game/simulation/components/abilities/` - various files
**Issue:** `sync_data()` method implementation varies:
- Some abilities implement full sync of all fields
- Some just call `super().sync_data(data)` and do nothing else
- `ToHitAttackModifier`, `ToHitDefenseModifier`, `EmissiveArmor` have empty `recalculate()` methods but no `sync_data()` override

Pattern suggests some abilities may not properly handle data updates.
**Impact:** Potential bugs when ability data is updated at runtime.
**Recommendation:** Either implement `sync_data()` consistently for all abilities that have mutable data, or document that some abilities are immutable.
**Effort:** Simple

#### MINOR: Inconsistent Default Parameter Values
**ID:** CON-SIM-011
**Location:** Multiple files
**Issue:** Default parameter values vary for similar concepts:
- `team_id: int = 0` (common)
- Some methods don't provide defaults for optional-seeming parameters
- `seed: Optional[int] = None` vs `seed: int = None` type annotations

**Impact:** Minor - forces callers to be explicit.
**Recommendation:** Standardize defaults where sensible (e.g., `team_id=0` everywhere).
**Effort:** Simple

#### MINOR: Component Type Checking via String vs isinstance
**ID:** CON-SIM-012
**Location:** `game/simulation/entities/ship_stats.py:284-301`, `game/simulation/systems/battle_engine.py:600-602`
**Issue:** Component type checking uses multiple patterns:
- `ab_cls = ability.__class__.__name__` then `if ab_cls == 'ResourceStorage':`
- `isinstance(ab, ResourceConsumption)`
- `comp.type == "Weapon"` (string attribute check)
- `comp.has_ability('WeaponAbility')` (preferred pattern)

**Impact:** Multiple patterns for same task; string comparisons are fragile.
**Recommendation:** Standardize on `has_ability()` or `isinstance()` checks. Avoid string class name comparisons.
**Effort:** Medium

#### MINOR: Inconsistent Use of Dataclass Fields
**ID:** CON-SIM-013
**Location:** `game/simulation/battle_state.py`, `game/simulation/managers/retreat_manager.py`
**Issue:** Dataclass usage patterns vary:
- Some use `field(default_factory=list)` correctly
- Some use mutable defaults (would be caught by dataclass)
- Mix of dataclass and regular class for similar data structures

**Impact:** Minor - dataclasses are used correctly where present.
**Recommendation:** Consider converting more state containers to dataclasses for consistency.
**Effort:** Simple

#### MINOR: Inconsistent List Return Types
**ID:** CON-SIM-014
**Location:** `game/simulation/entities/ship.py:690-705`, `game/simulation/entities/ship.py:616-633`
**Issue:** List return behavior varies:
- `get_components_by_layer()` returns a fresh copy: `return list(layer_data.components)`
- `get_all_components()` returns cached list with warning "do not modify"

Callers must know which methods return safe-to-modify lists.
**Impact:** Potential bugs if caller modifies returned list.
**Recommendation:** Document return type mutability in docstrings. Consider always returning copies for safety.
**Effort:** Simple

#### MINOR: Callback Naming Convention
**ID:** CON-SIM-015
**Location:** `game/simulation/battle_controller.py:676-686`, `game/simulation/managers/retreat_manager.py:268-273`
**Issue:** Callback setters use different patterns:
- `set_on_battle_complete(callback)` - verb prefix
- `_on_ship_escaped` - private attribute with underscore
- Some callbacks are set via constructor, others via setter methods

**Impact:** Minor inconsistency in API surface.
**Recommendation:** Standardize on `set_on_*` pattern for callback setters.
**Effort:** Simple

#### MINOR: Inconsistent Context Parameter Usage
**ID:** CON-SIM-016
**Location:** `game/simulation/entities/ship.py:260`, `game/simulation/components/component.py:401`
**Issue:** Context dict parameter pattern varies:
- `update(dt: float = 0.01, context: Optional[dict] = None)`
- `recalculate_stats(context: dict = None)` (missing Optional annotation)
- Some methods use `context` for different purposes (combat context vs formula context)

**Impact:** Unclear what `context` contains for each method.
**Recommendation:** Use typed context dataclasses instead of generic dicts, or document expected keys in docstrings.
**Effort:** Medium

#### MINOR: Formula String Convention
**ID:** CON-SIM-017
**Location:** `game/simulation/components/abilities/weapons.py:59-66`
**Issue:** Formula strings start with `=` prefix (like Excel), but this convention isn't documented:
- `damage="=10 + range_to_target * 0.5"` in JSON
- Code strips the `=` prefix for evaluation

**Impact:** Convention exists but isn't consistently documented.
**Recommendation:** Document formula string convention in component schema documentation.
**Effort:** Simple

#### INFO: Singleton Pattern Usage
**ID:** CON-SIM-018
**Location:** `game/simulation/components/component.py:436-473`
**Issue:** `ComponentCacheManager` uses singleton pattern via `@classmethod instance()`. Project prefers dependency injection per CLAUDE.md.
**Impact:** Makes testing harder, though `reset()` method exists for test isolation.
**Recommendation:** Consider refactoring to injected cache manager for better testability. Low priority as current implementation works.
**Effort:** Complex

#### INFO: Ability Registry as Module-Level Dict
**ID:** CON-SIM-019
**Location:** `game/simulation/components/abilities/__init__.py:69-107`
**Issue:** `ABILITY_REGISTRY` is a module-level dict, not using the Registry pattern from `game/core/registry.py`.
**Impact:** Works correctly but doesn't follow the project's registry pattern.
**Recommendation:** Low priority - consider migrating to GameRegistries pattern for consistency.
**Effort:** Medium

#### INFO: Late Import Comments
**ID:** CON-SIM-020
**Location:** `game/simulation/entities/ship_stat_querier.py:119-121`
**Issue:** Late imports have good documentation: `# INTENTIONAL LATE IMPORT: Avoid circular dependency`. This pattern is well-documented.
**Impact:** Positive - good practice followed.
**Recommendation:** Continue using this documentation pattern for intentional late imports.
**Effort:** N/A

## Top 5 Priority Issues
1. **CON-SIM-001 (CRITICAL)**: Inconsistent Return Type for Not-Found Scenarios - Fix to prevent subtle bugs from mismatched error handling
2. **CON-SIM-004 (MAJOR)**: Inconsistent Error Handling Patterns - Standardize on Result objects vs exceptions
3. **CON-SIM-005 (MAJOR)**: Ability Class Naming Inconsistency - Clean up `*Ability` suffix usage
4. **CON-SIM-002 (MAJOR)**: Inconsistent Method Verb Prefixes - Establish get/find/select conventions
5. **CON-SIM-003 (MAJOR)**: Mixed Docstring Formats - Standardize on Google-style with Args/Returns/Raises
