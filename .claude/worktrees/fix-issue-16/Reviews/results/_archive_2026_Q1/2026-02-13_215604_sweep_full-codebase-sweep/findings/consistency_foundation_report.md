# Consistency Violations Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 5 | **Minor:** 9 | **Info:** 3

## Findings

#### CRITICAL: Return Type Inconsistency in registry.py
**ID:** CON-FND-001
**Location:** `game/core/registry.py:98-120` vs `game/core/registry.py:383-397`
**Issue:** `get_default_registries()` raises `StateException` when not initialized, but `get_default_registry_provider()` silently creates an instance if None. This inconsistency in error handling for the same conceptual operation (getting default registry access) creates confusing API semantics.
**Impact:** Developers may expect consistent behavior between these two "get_default" functions. One raises, one silently initializes - this could mask initialization bugs or cause unexpected exceptions.
**Recommendation:** Standardize on one pattern. Since registries must be explicitly set (composition root responsibility), `get_default_registry_provider()` should also raise if the provider hasn't been set up, OR both should lazy-initialize.
**Effort:** Medium

#### MAJOR: Mixed Singleton Patterns
**ID:** CON-FND-002
**Location:** `game/core/singleton.py`, `game/core/registry.py:379-397`
**Issue:** The codebase has `SingletonMeta` metaclass for thread-safe singletons, but `get_default_registry_provider()` uses a module-level global pattern (`_default_provider`) instead. This creates two different singleton patterns for similar use cases.
**Impact:** Cognitive overhead when maintaining code. Developers must remember which pattern each service uses.
**Recommendation:** Either use `SingletonMeta` for `DefaultRegistryProvider` or document why the module-global pattern is preferred here. The module-global is simpler but less thread-safe.
**Effort:** Simple

#### MAJOR: Inconsistent Method Naming for State Access
**ID:** CON-FND-003
**Location:** `game/ai/interfaces/controllable.py`, `game/ai/controller.py`
**Issue:** Property access via `is_alive()` vs `is_alive` is inconsistent:
- `IControllable.is_alive()` is defined as abstract method returning `bool`
- But `ShipControllableAdapter.is_alive()` accesses `self._ship.is_alive` as a property
- `AIController` uses `self.ship.is_alive()` (method call) in line 268, but raw ships use `ship.is_alive` (property) in line 281
**Impact:** API confusion - callers don't know if is_alive is a property or method. Risk of calling `ship.is_alive` on adapter vs `ship.is_alive()`.
**Recommendation:** Standardize on one pattern. Properties are Pythonic for state queries. Change interface to `@property` and update all call sites.
**Effort:** Medium

#### MAJOR: Inconsistent Logging Patterns
**ID:** CON-FND-004
**Location:** `game/ai/combat_utils.py:19`, `game/ai/controller.py:55`, `game/core/logger.py`
**Issue:** AI module uses both patterns:
- Standard library: `logger = logging.getLogger(__name__)` then `logger.warning()`
- Custom core logger: `log_warning()`, `log_info()` from `game.core.logger`
The core modules consistently use the custom logger, but AI mixes both.
**Impact:** Log filtering and configuration becomes inconsistent. The custom Logger singleton may not capture logs from the standard library logger in the AI module.
**Recommendation:** Use the centralized `log_*` functions from `game.core.logger` everywhere for consistency with the rest of the codebase.
**Effort:** Simple

#### MAJOR: Docstring Format Inconsistency
**ID:** CON-FND-005
**Location:** Multiple files across all directories
**Issue:** Mixed docstring formats observed:
- Google style with Args/Returns sections: `game/core/validation.py`, `game/core/json_utils.py`, `game/research/`
- reST style with `:param:` and `:returns:`: Not observed
- Simple descriptions without formal sections: `game/engine/physics.py`, `game/engine/collision.py`
The majority use Google style, but some files (especially in engine/) skip formal Args/Returns sections.
**Impact:** Documentation tooling may produce inconsistent output. Harder for developers to scan for parameters.
**Recommendation:** Standardize on Google-style docstrings with Args/Returns for all public APIs. Engine module should be updated.
**Effort:** Simple

#### MAJOR: Type Hint Gaps in Engine Module
**ID:** CON-FND-006
**Location:** `game/engine/physics.py:56-107`, `game/engine/collision.py:57-127`
**Issue:** Core and AI modules have comprehensive type hints, but engine module is missing them:
- `PhysicsBody.__init__` has no type hints
- `CollisionSystem.process_beam_attack` uses `Any` for ship types but no return type
- `SpatialGrid.insert` has `Any` for `obj` parameter
**Impact:** Static type checkers cannot verify engine code correctness. Inconsistent with the well-typed core module.
**Recommendation:** Add proper type hints to engine module. Use `TYPE_CHECKING` imports if needed to avoid circular dependencies.
**Effort:** Medium

#### MINOR: Boolean Naming Prefix Inconsistency
**ID:** CON-FND-007
**Location:** `game/ai/interfaces/controllable.py`, `game/research/data/research_tracker.py`
**Issue:** Most boolean properties/methods use `is_` prefix (`is_alive`, `is_in_formation`, `is_valid`), but some deviate:
- `auto_spread_enabled` in ResearchTracker (should be `is_auto_spread_enabled` or use `_enabled` suffix consistently)
- `get_is_thrusting()` uses awkward `get_is_` prefix instead of just `is_thrusting()`
**Impact:** Minor cognitive overhead when guessing method names.
**Recommendation:** Use `is_` prefix for boolean properties. For getters, just use `is_` without `get_` prefix.
**Effort:** Simple

#### MINOR: Verb Prefix Inconsistency for Similar Operations
**ID:** CON-FND-008
**Location:** `game/core/registry.py`, `game/research/data/research_tracker.py`
**Issue:** Similar operations use different verbs:
- `get_state()` vs `get_components()` vs `load_data()` vs `load_json()`
- `clear()` vs `reset()` - both exist with overlapping meanings
- `set_allocation()` vs `clear_allocation()` vs `clear_all_allocations()`
**Impact:** Developers must memorize which verb applies to which operation.
**Recommendation:** Document verb conventions: `get_*` for read, `set_*` for write, `clear_*` for reset single, `reset()` for full state reset, `load_*` for disk I/O.
**Effort:** Simple (documentation) / Medium (refactoring)

#### MINOR: Import Organization Inconsistency
**ID:** CON-FND-009
**Location:** `game/core/profiling.py:1-12`, `game/research/ui/research_scene.py:1-26`
**Issue:** Import grouping varies:
- Most files follow stdlib -> third-party -> local
- Some mix `from __future__` imports with stdlib
- Some have blank lines between same-group imports
**Impact:** Code review friction, inconsistent auto-formatting.
**Recommendation:** Standardize: `from __future__` -> stdlib -> third-party -> local, with single blank line between groups.
**Effort:** Simple

#### MINOR: Constants Location Inconsistency
**ID:** CON-FND-010
**Location:** `game/ai/behaviors.py:135-136`, `game/core/config.py`
**Issue:** Some constants are defined in behavior classes (`MIN_SPACING`, `FLEE_DISTANCE`), others reference `AIConfig`. The pattern is mixed - sometimes referencing, sometimes duplicating.
**Impact:** Risk of values drifting apart if someone updates one location but not the other.
**Recommendation:** Always reference `AIConfig` constants directly, don't create class-level copies unless computing a derived value.
**Effort:** Simple

#### MINOR: Class Naming Suffix Inconsistency
**ID:** CON-FND-011
**Location:** `game/ai/`, `game/research/systems/`
**Issue:** Service-like classes have inconsistent suffixes:
- `StrategyManager` (Manager)
- `ResearchService` (Service)
- `RegistryManager` (Manager)
- `StrategyMetadataService` (Service)
Both Manager and Service are used for similar singleton/stateless service patterns.
**Impact:** Minor - both are clear, but inconsistent.
**Recommendation:** Document convention: `*Manager` for stateful singletons, `*Service` for stateless operation classes.
**Effort:** Simple (documentation)

#### MINOR: Private Member Prefix Inconsistency
**ID:** CON-FND-012
**Location:** `game/research/ui/research_controls.py:57`, `game/ai/interfaces/controllable.py:271`
**Issue:** Internal state uses inconsistent prefixes:
- `self._selected_node` (underscore prefix)
- `self.tracker` (no prefix, but arguably internal)
- `self._ship` vs `self.ship` property
**Impact:** Unclear which attributes are part of the public API.
**Recommendation:** Use single underscore `_` consistently for non-public attributes. Expose via `@property` if external access is needed.
**Effort:** Simple

#### MINOR: Magic Numbers in Rendering Code
**ID:** CON-FND-013
**Location:** `game/research/ui/research_renderer.py:72-77`, `game/research/ui/research_scene.py:62-66`
**Issue:** Layout and rendering constants are scattered:
- `SIDEBAR_WIDTH = 350`, `COLUMN_SPACING = 280` in scene
- Font size `14`, padding `5`, border radius `4` in renderer
**Impact:** Harder to consistently update visual style.
**Recommendation:** Consolidate rendering constants to a single location or use a theme/config class.
**Effort:** Simple

#### MINOR: Inconsistent Parameter Ordering
**ID:** CON-FND-014
**Location:** `game/ai/target_evaluator.py:237`, `game/ai/combat_utils.py:142`
**Issue:** Similar functions have different parameter orders:
- `TargetEvaluator.evaluate(ship, candidate, rules, ...)` - ship first
- `safe_distance(entity1, entity2)` - generic naming
- `is_in_pdc_arc(ship, target)` - ship first
Most follow `ship` first, but parameter naming varies (`ship` vs `entity1`).
**Impact:** Minor - calling conventions are generally clear.
**Recommendation:** Standardize on `source` or `ship` first for all combat functions. Use consistent naming.
**Effort:** Simple

#### INFO: Natural Variation - Module-Level vs Class-Level Functions
**ID:** CON-FND-015
**Location:** `game/core/json_utils.py`, `game/core/validation.py`
**Issue:** `json_utils.py` uses module-level functions (`load_json()`, `save_json()`), while `validation.py` uses a dataclass with methods. Both are valid approaches for their use cases.
**Impact:** None - this is appropriate variation based on statelessness vs stateful result objects.
**Recommendation:** Document that stateless utilities should be module functions, stateful results should be classes. No change needed.
**Effort:** None

#### INFO: Protocol Usage Variation
**ID:** CON-FND-016
**Location:** `game/core/protocols.py`, `game/ai/interfaces/controllable.py`
**Issue:** Two approaches to interfaces:
- `typing.Protocol` with `@runtime_checkable` (core/protocols.py)
- `abc.ABC` with `@abstractmethod` (ai/interfaces/controllable.py)
Both are valid but serve slightly different purposes.
**Impact:** None - ABC for implementation contracts, Protocol for duck-typing checks.
**Recommendation:** Document when to use each: ABC when subclassing is expected, Protocol when structural typing is preferred.
**Effort:** None

#### INFO: Exception Hierarchy Well-Structured
**ID:** CON-FND-017
**Location:** `game/core/exceptions.py`
**Issue:** The exception hierarchy is well-designed and consistently used across all modules reviewed. Error codes are standardized.
**Impact:** Positive - good pattern to maintain.
**Recommendation:** Continue using this pattern. Consider adding docstrings with example usage to each exception class.
**Effort:** None

#### MINOR: Defensive Programming Inconsistency
**ID:** CON-FND-018
**Location:** `game/ai/combat_utils.py`, `game/engine/collision.py:146-149`
**Issue:** AI module uses extensive defensive patterns with fallbacks and logging, while engine module uses basic error handling:
- AI: `getattr(entity, 'id', None)` with fallbacks everywhere
- Engine: Uses `getattr(s, 'hp', 100)` only in one place (ramming)
**Impact:** Engine code may crash on missing attributes that AI code would handle gracefully.
**Recommendation:** Apply consistent defensive patterns across all combat-related code.
**Effort:** Medium

## Top 5 Priority Issues

1. **CON-FND-001 (CRITICAL)**: Return type inconsistency between `get_default_registries()` (raises) and `get_default_registry_provider()` (lazy creates). This is a subtle API design bug that could cause hard-to-debug initialization issues.

2. **CON-FND-003 (MAJOR)**: `is_alive` property vs method inconsistency. This affects the core AI interface and could cause runtime errors if callers use the wrong syntax.

3. **CON-FND-004 (MAJOR)**: Mixed logging patterns. Using both `logging.getLogger()` and `game.core.logger` functions means logs may not be captured consistently.

4. **CON-FND-006 (MAJOR)**: Engine module lacks type hints. This is a foundational module for physics/collision that should have the same type safety as core.

5. **CON-FND-002 (MAJOR)**: Mixed singleton patterns. While not causing bugs, it increases cognitive load and creates inconsistent patterns for developers to follow.
