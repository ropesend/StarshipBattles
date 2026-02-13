# Consistency Violations Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 14
- **Critical:** 0 | **Major:** 5 | **Minor:** 7 | **Info:** 2

## Findings

#### MAJOR: Inconsistent Logging Pattern - Direct logging module vs game.core.logger
**ID:** CON-FND-001
**Location:** `game/ai/combat_utils.py:14`, `game/ai/controller.py:51-52`
**Issue:** The AI module uses Python's standard `logging.getLogger(__name__)` pattern while the rest of the codebase uses the centralized `game.core.logger` module with functions like `log_info`, `log_warning`, `log_debug`, `log_error`.
**Impact:** Inconsistent log formatting and configuration. The standard logging pattern bypasses the centralized Logger singleton which has its own enabled flag and file handler setup.
**Recommendation:** Migrate all AI module logging to use `from game.core.logger import log_warning, log_debug, log_info` instead of the standard logging module. The established pattern is visible in all other modules (research, core, etc.).
**Effort:** Simple

#### MAJOR: Mixed os.path.join and Path-style path construction
**ID:** CON-FND-002
**Location:** `game/core/paths.py:53-99`, `game/research/data/tech_tree.py:40`, `game/ai/strategy_manager.py:91`
**Issue:** The Paths class defines directory constants using `os.path.join()` for string-based paths AND provides `get_*` class methods returning `pathlib.Path` objects. Consuming code mixes both styles inconsistently.
**Impact:** Cognitive overhead when reading code - unclear which style to use. Some code uses `os.path.join(base_path, file)`, others use `Path / "subdir"`.
**Recommendation:** Standardize on pathlib.Path for all new code. The Paths class provides both styles for legacy compatibility, but consuming code should prefer the `get_*()` methods that return Path objects.
**Effort:** Medium

#### MAJOR: Inconsistent Boolean Property Naming - is_ prefix usage
**ID:** CON-FND-003
**Location:** `game/core/profiling.py:63-64`, `game/ai/interfaces/controllable.py:338`
**Issue:** Some boolean state accessors use `is_active()` method pattern (Profiler), while others use `get_is_*()` method pattern (ShipControllableAdapter has `get_is_thrusting()`). The protocols also mix `is_alive` property vs `is_alive()` method.
**Impact:** Inconsistent API surface for checking boolean state. Callers must remember which pattern each class uses.
**Recommendation:** Establish convention: For interface methods use `get_is_*()` or `is_*()` methods. For properties, use `is_*` without the `get_` prefix. The dominant pattern in protocols is `is_alive` as a property.
**Effort:** Medium

#### MAJOR: Inconsistent Return Type for Not-Found Cases
**ID:** CON-FND-004
**Location:** `game/core/json_utils.py:33-67`, `game/core/strategy_metadata.py:98-111`
**Issue:** `load_json()` returns the `default` parameter on error (typically None or {}), while `load_json_required()` raises exceptions. However, `StrategyMetadataService.get_strategy_id_by_name()` returns `Optional[str]` (None for not found), while `get_strategy_display_name()` returns the input ID as fallback for not found.
**Impact:** Callers must handle different not-found semantics for similar operations. Some return None, some return a fallback value, some raise.
**Recommendation:** Document and standardize: lookup methods that are "required" should raise, optional lookups should return `Optional[T]` with None. The `get_strategy_display_name` returning the input ID as fallback is a reasonable defensive choice but should be documented.
**Effort:** Simple

#### MAJOR: Inconsistent Singleton Reset Patterns
**ID:** CON-FND-005
**Location:** `game/core/singleton.py:84-97`, `game/core/profiling.py:39-42`, `game/ai/strategy_manager.py:53-64`
**Issue:** The SingletonMeta provides a `reset()` method that destroys the instance entirely. Classes using SingletonMeta also implement `clear()` methods that preserve the instance but reset data. However, usage is inconsistent - some have both, some have only one.
**Impact:** Test isolation code must know which method to call for each singleton. Some call `reset()`, others call `clear()`, some need both.
**Recommendation:** All singletons using SingletonMeta should implement both patterns: `reset()` from metaclass (destroys instance) and `clear()` as instance method (resets data, preserves instance). Document the semantics clearly.
**Effort:** Simple

#### MINOR: Inconsistent Method Verb Prefixes for Accessors
**ID:** CON-FND-006
**Location:** `game/ai/interfaces/controllable.py`
**Issue:** The IControllable interface uses `get_*` prefix consistently for read operations, but the underlying Ship class uses direct property access (e.g., `position`, `angle`, `velocity`). The adapter translates between these.
**Impact:** Low - the adapter handles the translation. However, it creates two mental models for attribute access.
**Recommendation:** The current adapter pattern is acceptable. Document that external code should use the interface methods, not direct attribute access.
**Effort:** N/A (working as designed)

#### MINOR: Inconsistent Parameter Naming - node_id vs prereq_id vs node
**ID:** CON-FND-007
**Location:** `game/research/data/tech_tree.py`, `game/research/data/research_tracker.py`
**Issue:** Variable naming for tech tree nodes varies: `node_id` (string ID), `prereq_id`, `node` (TechNode object), `nid` (abbreviation). While context clarifies, abbreviated forms reduce readability.
**Impact:** Minor cognitive load when reading research module code.
**Recommendation:** Standardize on `node_id` for string IDs, `node` for TechNode objects. Avoid abbreviations like `nid`.
**Effort:** Simple

#### MINOR: Inconsistent Docstring Format - Args/Returns sections
**ID:** CON-FND-008
**Location:** Various files
**Issue:** Most files use Google-style docstrings with `Args:` and `Returns:` sections, but some shorter functions omit these sections entirely (e.g., `game/engine/physics.py:82-102`, `game/engine/spatial.py`).
**Impact:** Inconsistent documentation depth. IDE tools may not extract parameter info consistently.
**Recommendation:** Add Args/Returns sections to all public methods that have parameters or return values. The dominant convention (Google-style) is well-established.
**Effort:** Simple

#### MINOR: Magic Numbers in Research UI - Layout Constants
**ID:** CON-FND-009
**Location:** `game/research/ui/research_scene.py:40-44`
**Issue:** Layout constants (SIDEBAR_WIDTH=350, COLUMN_SPACING=280, ROW_SPACING=100, NODE_WIDTH=220, NODE_HEIGHT=70) are defined as class constants which is good, but `research_controls.py` has inline magic numbers for positioning (e.g., `y += 30`, `y += 22`).
**Impact:** Changing UI layout requires hunting through multiple inline values instead of adjusting named constants.
**Recommendation:** Extract positioning increments to named constants (e.g., `LABEL_SPACING = 22`, `SECTION_SPACING = 30`).
**Effort:** Simple

#### MINOR: Inconsistent Type Hints - Any vs Specific Protocol Types
**ID:** CON-FND-010
**Location:** `game/engine/collision.py:50-54`, `game/ai/combat_utils.py`
**Issue:** Some type hints use `Any` with comments explaining why (e.g., "to avoid tight coupling"), while the protocols module provides specific protocol types like `ICombatant`, `IPostBattleShip`. Not all code that could use protocols does so.
**Impact:** Loss of static type checking benefits where protocols could be used instead of Any.
**Recommendation:** Where protocol types exist (e.g., ICombatant for entities with team_id and is_alive), use them instead of Any. Reserve Any for truly dynamic cases.
**Effort:** Medium

#### MINOR: Inconsistent __all__ Export Patterns
**ID:** CON-FND-011
**Location:** `game/core/singleton.py:22`, `game/core/math.py` (missing), `game/core/hex_math.py` (missing)
**Issue:** Some modules define `__all__` explicitly (singleton.py, registry.py), while others rely on implicit exports (math.py, hex_math.py).
**Impact:** Inconsistent module API definition. `from module import *` behaves differently depending on whether __all__ is defined.
**Recommendation:** Add `__all__` to all public modules for explicit API definition. The core/__init__.py already re-exports everything, but leaf modules should still define their own exports.
**Effort:** Simple

#### MINOR: Inconsistent Private Attribute Naming
**ID:** CON-FND-012
**Location:** `game/ai/interfaces/controllable.py:278`, `game/research/ui/research_controls.py:57`
**Issue:** Private attributes sometimes use single underscore (`_ship`, `_selected_node`), which is correct. However, some internal methods lack the underscore prefix (e.g., `_eval_*` methods in target_evaluator.py are properly prefixed, but some helper methods in other files are not).
**Impact:** Minor - convention is generally followed but not uniformly.
**Recommendation:** All non-public methods should use single underscore prefix. The pattern is well-established in the codebase.
**Effort:** Simple

#### INFO: Optional vs Union[X, None] Usage
**ID:** CON-FND-013
**Location:** `game/core/protocols.py:24-31`
**Issue:** The codebase uses `Optional[T]` consistently rather than `Union[T, None]`, which is good. This is noted as a positive pattern that is consistently followed.
**Impact:** None - this is working well.
**Recommendation:** Continue using `Optional[T]` as the standard convention.
**Effort:** N/A

#### INFO: Import Organization Generally Consistent
**ID:** CON-FND-014
**Location:** All files
**Issue:** Import organization follows a consistent pattern: stdlib first, then third-party, then local imports. Some files use TYPE_CHECKING for conditional imports to avoid circular dependencies. This pattern is well-established.
**Impact:** None - this is working well.
**Recommendation:** Continue the current pattern. Document it in CLAUDE.md if not already documented.
**Effort:** N/A

## Top 5 Priority Issues

1. **CON-FND-001 (MAJOR): Inconsistent Logging Pattern** - The AI module using standard logging instead of game.core.logger breaks the centralized logging configuration. This is a straightforward fix with clear benefit for debugging consistency.

2. **CON-FND-004 (MAJOR): Inconsistent Return Type for Not-Found Cases** - Different modules handle "not found" differently (None vs fallback value vs raise). This requires documentation and possibly some API adjustments for consistency.

3. **CON-FND-005 (MAJOR): Inconsistent Singleton Reset Patterns** - Test isolation relies on knowing which reset method to call. Standardizing on both `reset()` and `clear()` for all singletons would improve test reliability.

4. **CON-FND-002 (MAJOR): Mixed Path Construction Styles** - While both styles work, standardizing on pathlib would modernize the codebase and reduce the mental overhead of two path APIs.

5. **CON-FND-003 (MAJOR): Inconsistent Boolean Property Naming** - The mix of `is_*`, `get_is_*`, and property vs method patterns creates API inconsistency that could confuse consumers.
