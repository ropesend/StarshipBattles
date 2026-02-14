# Consistency Violations Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 18
- **Critical:** 0 | **Major:** 5 | **Minor:** 10 | **Info:** 3

## Findings

#### MAJOR: Inconsistent Singleton Pattern Usage
**ID:** CON-FND-001
**Location:** `game/core/registry.py:379-397`, `game/core/strategy_metadata.py`, `game/core/profiling.py`, `game/ai/strategy_manager.py`
**Issue:** Two different singleton patterns exist in the codebase. Most singletons use `SingletonMeta` metaclass with `instance()` class method, but `get_default_registry_provider()` uses a manual module-level `_default_provider` variable with None check. This creates inconsistency in how singletons are accessed.
**Impact:** Developers may not know which pattern to use. Manual singleton may lack thread safety guarantees that SingletonMeta provides. Inconsistent reset/clear semantics.
**Recommendation:** Convert `DefaultRegistryProvider` singleton to use `SingletonMeta` pattern like `StrategyManager`, `StrategyMetadataService`, `Profiler`, and `Logger`. Use `DefaultRegistryProvider.instance()` instead of `get_default_registry_provider()`.
**Effort:** Medium

#### MAJOR: Inconsistent Return Type for Missing Items (Return vs Raise)
**ID:** CON-FND-002
**Location:** `game/core/json_utils.py:33-67` vs `game/core/json_utils.py:70-96`
**Issue:** `load_json()` returns default value on error while `load_json_required()` raises exceptions. This is intentional API design but creates inconsistency with similar patterns elsewhere. `StrategyManager.get_strategy()` returns default on missing key, while `get_default_registries()` raises `StateException` when not initialized.
**Impact:** Caller must know which pattern each function uses. Inconsistent error handling propagation throughout codebase.
**Recommendation:** Document and standardize the naming convention: `_required` suffix for raising methods, no suffix for safe defaults. Consider adding `get_default_registries_or_none()` for consistency.
**Effort:** Simple

#### MAJOR: Mixed Method Naming for Accessor Functions
**ID:** CON-FND-003
**Location:** `game/ai/interfaces/controllable.py:40-210`, `game/core/protocols.py:82-105`
**Issue:** IControllable interface uses `get_` prefix consistently for all accessors (e.g., `get_position()`, `get_velocity()`, `get_rotation()`), but Protocol classes in `protocols.py` use `@property` decorators without `get_` prefix (e.g., `location`, `name`, `owner_id`). The research module uses direct attribute access (`state.current_level`) while AI uses getter methods.
**Impact:** Cognitive overhead when switching between modules. Developers unsure whether to use property or getter pattern.
**Recommendation:** Establish convention: Use properties for simple attribute reads, `get_` methods for computed values or when hiding implementation. Document in CLAUDE.md.
**Effort:** Complex (large refactor to unify)

#### MAJOR: Inconsistent Parameter Ordering for Similar Functions
**ID:** CON-FND-004
**Location:** `game/ai/combat_utils.py:66-96` vs `game/ai/combat_utils.py:142-164`
**Issue:** `get_position(entity)` and `get_rotation(entity)` take a single entity, but `safe_distance(entity1, entity2)` takes two entities with numbered names. `is_in_pdc_arc(ship, target)` uses semantic names. Parameter naming is inconsistent: `entity` vs `ship` vs `entity1`.
**Impact:** Confusing when reading code - unclear which parameter is which type of object.
**Recommendation:** Use semantic names consistently: `source`/`target` or `attacker`/`defender` for pairs. Use `entity` for single-entity functions.
**Effort:** Simple

#### MAJOR: Logging Pattern Inconsistency
**ID:** CON-FND-005
**Location:** `game/ai/combat_utils.py:19`, `game/ai/controller.py:55`, `game/ai/target_evaluator.py` (no logger)
**Issue:** `combat_utils.py` and `controller.py` use Python's `logging.getLogger(__name__)` pattern, while most of the codebase uses `game.core.logger` functions (`log_info`, `log_debug`, `log_warning`, `log_error`). `target_evaluator.py` has no logging at all.
**Impact:** Inconsistent log output format. Some logs go to game logger, others to Python's root logger. Mixed debugging experience.
**Recommendation:** Standardize on `game.core.logger` functions throughout AI module. Add logging to `target_evaluator.py` for evaluation failures.
**Effort:** Simple

#### MINOR: Inconsistent Docstring Style
**ID:** CON-FND-006
**Location:** `game/engine/physics.py:82-87` vs `game/research/data/tech_node.py:22-34`
**Issue:** Most files use Google-style docstrings with Args/Returns sections, but some methods have minimal one-line docstrings. `physics.py.update()` has inline comments instead of docstring. `TechRequirement.resolve()` has full docstrings while `TechRequirement.is_met()` has abbreviated style.
**Impact:** Minor - inconsistent documentation quality within modules.
**Recommendation:** Ensure all public methods have Args/Returns sections in docstrings.
**Effort:** Simple

#### MINOR: Type Hint Inconsistency for Vector2
**ID:** CON-FND-007
**Location:** `game/ai/interfaces/controllable.py:18-20`, `game/engine/physics.py:51`
**Issue:** `IControllable` interface uses `Any` type hints for Vector2 to avoid pygame dependency, noted in comments. But `PhysicsBody` imports and uses `game.core.math.Vector2` directly. The project has its own Vector2 but AI layer treats it as opaque `Any`.
**Impact:** Loss of type checking benefits in AI layer. IDE cannot provide autocomplete for vector operations.
**Recommendation:** Import `game.core.math.Vector2` in AI interfaces since it's framework-agnostic and part of the core layer.
**Effort:** Simple

#### MINOR: Constants Naming - Mixed Casing for Similar Concepts
**ID:** CON-FND-008
**Location:** `game/core/config.py:49-91`
**Issue:** `AIConfig` uses `UPPER_SNAKE_CASE` consistently for constants (e.g., `MIN_SPACING`, `DEFAULT_ORBIT_DISTANCE`), but `FormationBehavior` in `behaviors.py:265-274` duplicates these by copying to class attributes with same names. Both are valid Python but creates redundancy.
**Impact:** Two sources of truth for the same constants. Changes to AIConfig may be missed in behavior classes.
**Recommendation:** Remove duplicate constant assignments in behavior classes. Access `AIConfig.CONSTANT_NAME` directly instead of creating class copies.
**Effort:** Simple

#### MINOR: Inconsistent Use of `clear()` vs `reset()` Methods
**ID:** CON-FND-009
**Location:** `game/core/registry.py:217-237` vs `game/core/singleton.py:84-97`
**Issue:** `RegistryManager` has `clear()` method (empties data, preserves instance). `SingletonMeta` has `reset()` class method (destroys instance entirely). `StrategyManager` has `clear()`. `ResearchTracker` has `reset()`. The semantics differ but naming suggests similarity.
**Impact:** Developers may call wrong method expecting different behavior.
**Recommendation:** Document convention: `clear()` = empty contents, preserve instance; `reset()` = destroy instance. Consider renaming `SingletonMeta.reset()` to `destroy_instance()` for clarity.
**Effort:** Simple

#### MINOR: Mixed `Optional` vs `| None` Type Hint Style
**ID:** CON-FND-010
**Location:** `game/core/registry.py:81`, `game/research/ui/research_scene.py:16`
**Issue:** Most files use `Optional[Type]` from typing module. Python 3.10+ supports `Type | None` syntax. Codebase should be consistent.
**Impact:** Minor style inconsistency. Code works correctly either way.
**Recommendation:** Standardize on `Optional[Type]` for compatibility with older Python versions, or document minimum Python version and use `| None`.
**Effort:** Simple

#### MINOR: Incomplete `__all__` Exports
**ID:** CON-FND-011
**Location:** `game/core/constants.py:3-15`
**Issue:** `__all__` list includes `SimulationConstants` and `ResourceType` which are defined in the file but `SimulationConstants` is not exported from `game/core/__init__.py`. `ENABLE_SCREENSHOTS` is in `__all__` but not re-exported in package init.
**Impact:** Import confusion - users may not know what's available from `game.core`.
**Recommendation:** Either add missing exports to `game/core/__init__.py` or remove from module `__all__`.
**Effort:** Simple

#### MINOR: Inconsistent Boolean Naming - `is_` vs `has_` Prefix
**ID:** CON-FND-012
**Location:** `game/ai/interfaces/controllable.py:229-230`, `game/ai/combat_utils.py:186`
**Issue:** `is_in_formation()` uses `is_` prefix for state check. `is_in_pdc_arc()` uses `is_` for condition check. But `has_weapons` key in capabilities cache uses `has_`. Generally consistent but `is_vector2_like()` could be `has_vector2_interface()`.
**Impact:** Minor - mostly consistent but could be clearer.
**Recommendation:** Convention: `is_` for state/condition, `has_` for possession. `is_vector2_like` is correct (checking type likeness, not possession).
**Effort:** Simple

#### MINOR: Error Code Enum Incomplete Coverage
**ID:** CON-FND-013
**Location:** `game/core/error_codes.py:52-153`
**Issue:** `ErrorCode` enum has V001-V004, S001-S004, R001-R003, P001-P005, F001-F004, C001-C005 but gaps exist (e.g., V002 is missing). Comments indicate planned codes but not implemented.
**Impact:** Minor - gaps may indicate removed codes or reserved for future use.
**Recommendation:** Add comment documenting that gaps are intentional (reserved) or fill them.
**Effort:** Simple

#### MINOR: Factory Function Naming Inconsistency
**ID:** CON-FND-014
**Location:** `game/research/ui/research_scene.py:31-46`
**Issue:** `_create_default_camera()` uses underscore prefix indicating private, but it's a factory function. Compare to `get_default_registry_provider()` which is public and uses `get_` prefix.
**Impact:** Minor naming inconsistency. Both are valid approaches.
**Recommendation:** Private factory functions with underscore prefix is fine. Document convention: `_create_*` for private factories, `create_*` for public factories.
**Effort:** Simple

#### INFO: Module Docstring Completeness Variation
**ID:** CON-FND-015
**Location:** `game/engine/spatial.py:1-6` vs `game/ai/controller.py:1-50`
**Issue:** Some modules have extensive docstrings explaining architecture and usage (`controller.py`, `behaviors.py`), while others have minimal descriptions (`spatial.py`, `collision.py`). Both are valid but quality varies.
**Impact:** Documentation quality inconsistency. Complex modules are well-documented, simple ones less so.
**Recommendation:** No action needed - proportional documentation is acceptable.
**Effort:** N/A

#### INFO: Import Organization Consistency
**ID:** CON-FND-016
**Location:** Multiple files
**Issue:** Import organization follows stdlib -> third-party -> local pattern consistently. Some files use `from __future__ import annotations` (math.py, input_actions.py), others don't. Usage appears based on need for forward references.
**Impact:** None - imports are well-organized.
**Recommendation:** No action needed - `__future__` import usage is appropriate.
**Effort:** N/A

#### INFO: Configuration Class vs Module Constants Pattern
**ID:** CON-FND-017
**Location:** `game/core/config.py`, `game/core/constants.py`
**Issue:** `config.py` uses classes with class attributes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`). `constants.py` uses mix of classes (`LayerDefaults`, `CombatConstants`) and module-level constants (`PLANET_RESOURCES`). Both patterns coexist.
**Impact:** Two valid patterns exist. Classes group related constants, module-level for standalone values.
**Recommendation:** Current approach is reasonable. Document: use classes for grouped constants, module-level for isolated values.
**Effort:** N/A

#### MINOR: Inconsistent Default Parameter Handling
**ID:** CON-FND-018
**Location:** `game/research/data/research_tracker.py:55-65`, `game/ai/strategy_manager.py:83-89`
**Issue:** `ResearchTracker.__init__()` uses `session_seed: int = None` with runtime generation if None. `StrategyManager.load_data()` has all defaults inline. Some functions use `Optional[int] = None`, others use `int = None` (technically incorrect typing).
**Impact:** Type checker may flag `int = None` as incorrect (should be `Optional[int]`).
**Recommendation:** Use `Optional[int] = None` or `int | None = None` for parameters that accept None.
**Effort:** Simple

## Top 5 Priority Issues

1. **CON-FND-005 - Logging Pattern Inconsistency**: The AI module uses Python's logging module directly while the rest of the codebase uses `game.core.logger`. This causes split log output and inconsistent debugging. Fix by converting AI module to use core logger functions.

2. **CON-FND-001 - Inconsistent Singleton Pattern**: Two different singleton patterns (`SingletonMeta` vs manual module-level variable) create confusion and potential thread safety issues. Standardize on `SingletonMeta` throughout.

3. **CON-FND-003 - Mixed Method Naming for Accessors**: The inconsistency between `get_*()` methods and properties creates cognitive load when moving between modules. Establish and document a clear convention.

4. **CON-FND-004 - Inconsistent Parameter Ordering/Naming**: Parameters use inconsistent names (`entity` vs `ship` vs `entity1`) making API usage confusing. Standardize on semantic names.

5. **CON-FND-007 - Type Hint Inconsistency for Vector2**: Using `Any` for Vector2 in AI layer loses type checking benefits when `game.core.math.Vector2` is available and framework-agnostic.
