# Consistency Violations Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 43
- **Total Issues Found:** 22
- **Critical:** 1 | **Major:** 7 | **Minor:** 10 | **Info:** 4

## Findings

---

### Phase 1: Naming Convention Analysis

#### MAJOR: Mixed Singleton Patterns Across Core Layer
**ID:** CON-FND-001
**Location:** `game/core/strategy_metadata.py:34-83` vs `game/core/singleton.py`, `game/core/registry.py`, `game/core/logger.py`
**Issue:** `StrategyMetadataService` implements its own manual singleton pattern (class-level `_instance`, `_lock`, manual double-checked locking, `__init__` guard with `StateException`) while the rest of the codebase uses `SingletonMeta` metaclass. Every other singleton in game/core/ (`Logger`, `ScreenshotManager`, `Profiler`, `RegistryManager`) uses `SingletonMeta` from `game/core/singleton.py`.
**Impact:** Developers must understand two different singleton patterns. The manual pattern in `StrategyMetadataService` has different API semantics (raises `StateException` on direct construction vs `SingletonMeta` which silently returns the existing instance). This is a source of confusion and potential bugs.
**Recommendation:** Migrate `StrategyMetadataService` to use `SingletonMeta` metaclass, matching `Logger`, `ScreenshotManager`, `Profiler`, and `RegistryManager`.
**Effort:** Simple

#### MAJOR: Inconsistent Logging Approach Between game/ai/ and game/core/
**ID:** CON-FND-002
**Location:** `game/ai/combat_utils.py:19`, `game/ai/controller.py:55`, `game/ai/target_evaluator.py` vs `game/core/logger.py`
**Issue:** The `game/ai/` package uses Python's stdlib `logging.getLogger(__name__)` pattern for logging (e.g., `logger = logging.getLogger(__name__)` in `combat_utils.py`, `controller.py`), while `game/core/` provides and uses centralized convenience functions (`log_debug`, `log_info`, `log_warning`, `log_error` from `game.core.logger`). The `game/research/` package correctly uses the `game.core.logger` functions. This creates two logging systems operating in parallel.
**Impact:** Log output may go to different handlers/formatters. The `game/core/logger.Logger` instance writes to a file handler; stdlib loggers may not, unless separately configured. AI subsystem logs may be silently lost.
**Recommendation:** Migrate `game/ai/` to use `game.core.logger` convenience functions (`log_warning`, `log_debug`, `log_error`) consistently, matching `game/core/` and `game/research/`. Or, configure the core `Logger` to integrate with Python's stdlib logging hierarchy so both approaches produce consistent output.
**Effort:** Medium

#### MINOR: Inconsistent os.path vs pathlib Usage in game/core/paths.py
**ID:** CON-FND-003
**Location:** `game/core/paths.py:50-103` vs `game/core/paths.py:106-133`
**Issue:** The `Paths` class uses `os.path.join()` for all string path constants (lines 50-103) but provides `pathlib.Path` accessors via `get_*()` class methods (lines 106-133). Internal `_find_project_root()` uses `pathlib.Path`. This means the same path concept is represented two ways (`Paths.DATA_DIR` as `str` and `Paths.get_data_dir()` as `Path`), and the `get_*()` methods hardcode paths with `/` operators instead of referencing the existing string constants.
**Impact:** Callers must decide which form to use. The `get_saves_dir()` method constructs `"output" / "saves"` independently rather than referencing `SAVES_DIR`, creating risk of divergence if paths change.
**Recommendation:** Standardize on one approach. Since the codebase is Python 3, prefer `pathlib.Path` internally and derive string constants from Path objects if needed for backward compatibility.
**Effort:** Medium

#### MINOR: Missing Type Hints on HexCoord Methods
**ID:** CON-FND-004
**Location:** `game/core/hex_math.py:75-119` and module-level functions `hex_distance`, `hex_to_pixel`, `pixel_to_hex`, `hex_ring`, `hex_lerp`, `hex_linedraw`
**Issue:** `HexCoord.__init__`, `cube` property, `__eq__`, `__hash__`, `__repr__`, `__add__`, `__sub__`, `neighbors()` and all module-level functions (`hex_distance`, `hex_to_pixel`, `pixel_to_hex`, `_hex_round`, `hex_ring`, `hex_lerp`, `hex_linedraw`) lack type hints. Meanwhile, `hex_to_dict` and `hex_from_dict` at the bottom of the same file DO have type hints, as does every public function in `game/core/math.py`, `game/core/json_utils.py`, and other core modules.
**Impact:** Inconsistent with project convention requiring type hints on function signatures. Reduces IDE support and static analysis coverage for hex math operations.
**Recommendation:** Add type hints to all `HexCoord` methods and module-level hex functions, matching the style used in `hex_to_dict`/`hex_from_dict` and `game/core/math.py`.
**Effort:** Simple

#### MINOR: Missing Type Hints on game/engine/ Classes
**ID:** CON-FND-005
**Location:** `game/engine/spatial.py:6-35`, `game/engine/physics.py:56-113`, `game/engine/collision.py:58-167`
**Issue:** `SpatialGrid` methods (`__init__`, `clear`, `_get_cell`, `insert`, `query_radius`) have no type hints. `PhysicsBody.__init__` parameters lack type hints. `CollisionSystem.process_ramming` uses string annotation for `ships` parameter but `process_beam_attack` parameters are typed as generic `Dict`/`List` without specifics. This contrasts with the well-typed `game/core/` and `game/research/` modules.
**Impact:** The engine layer is the least type-hinted module in the shard, inconsistent with the project convention.
**Recommendation:** Add type hints to all `SpatialGrid`, `PhysicsBody`, and `CollisionSystem` method signatures.
**Effort:** Simple

#### MINOR: Duplicate Enum Import in constants.py
**ID:** CON-FND-006
**Location:** `game/core/constants.py:1` and `game/core/constants.py:27`
**Issue:** `from enum import Enum, auto` is imported at line 1, then `from enum import IntEnum` is imported separately at line 27. The `auto` import is unused. The `IntEnum` import should be combined with the first import statement.
**Impact:** Minor code smell. Suggests the file was assembled incrementally without cleanup.
**Recommendation:** Consolidate into a single import: `from enum import Enum, IntEnum` and remove the unused `auto` import.
**Effort:** Simple

#### MINOR: Inconsistent Docstring Presence on game/engine/ Module
**ID:** CON-FND-007
**Location:** `game/engine/spatial.py` (entire file)
**Issue:** `spatial.py` has no module docstring and `SpatialGrid` has no class docstring. In contrast, `physics.py` has an extensive module docstring and `collision.py` has a thorough module docstring. All three files are in the same package.
**Impact:** Inconsistent documentation within the same package reduces discoverability and understanding of the spatial indexing system.
**Recommendation:** Add a module docstring and class docstring to `spatial.py` matching the quality of `physics.py` and `collision.py`.
**Effort:** Simple

#### MINOR: ResourceType Uses Class Constants Instead of Enum
**ID:** CON-FND-008
**Location:** `game/core/constants.py:95-104`
**Issue:** `ResourceType` is defined as a plain class with string constants (`FUEL = 'fuel'`, etc.) and a `classmethod all()`. All other type constants in the same file use `Enum` (`AttackType(Enum)`, `GameState(IntEnum)`, `LayerType(Enum)`). `ResourceType` breaks this pattern by being a plain class.
**Impact:** `ResourceType` values cannot be compared with `isinstance` checks or used in `match` statements like other enums. API inconsistency within the same module.
**Recommendation:** Convert `ResourceType` to a `str, Enum` (like `InputAction`) for consistency with the other type enums in the same file.
**Effort:** Simple

---

### Phase 2: Structural Pattern Analysis

#### CRITICAL: Inconsistent Error Handling Strategy Between load_resources and load_resources_data
**ID:** CON-FND-009
**Location:** `game/core/resources.py:55-98` vs `game/core/resources.py:101-142`
**Issue:** `load_resources_data()` (the DI-friendly pure function) and `load_resources()` (the legacy wrapper) contain nearly identical code with duplicated error handling. Both independently call `_resolve_resource_path()`, `load_json_required()`, and handle the same exception types with the same fallback logic. However, `load_resources_data()` uses `copy.deepcopy()` on defaults and returned data while `load_resources()` does not, meaning the two functions have subtly different safety guarantees. The docstring on `load_resources()` says "New code should prefer DI via load_resources_data()" but the function does NOT delegate to `load_resources_data()` -- it reimplements the same logic.
**Impact:** Bug risk: any fix to error handling must be applied to both functions. The deepcopy difference means `load_resources()` allows mutations to propagate to the defaults dict while `load_resources_data()` does not. This violates DRY and creates a maintenance trap.
**Recommendation:** Refactor `load_resources()` to delegate to `load_resources_data()` and simply update the registry with the result, eliminating the duplicated error handling.
**Effort:** Simple

#### MAJOR: __init__.py Export Inconsistency Across Packages
**ID:** CON-FND-010
**Location:** `game/core/__init__.py`, `game/ai/__init__.py`, `game/engine/__init__.py` vs `game/research/__init__.py`
**Issue:** `game/core/__init__.py` has a comprehensive docstring documenting Public API, explicit imports, and `__all__`. `game/ai/__init__.py` follows the same pattern. `game/engine/__init__.py` follows it. But `game/research/__init__.py` has only a brief docstring with no imports and no `__all__`, delegating all exports to subpackage `__init__.py` files. The research subpackage `__init__.py` files (`data/__init__.py`, `systems/__init__.py`, `ui/__init__.py`) do have `__all__` and imports, but the top-level `game/research/__init__.py` does not re-export them.
**Impact:** Users cannot do `from game.research import ResearchService` -- they must use `from game.research.systems import ResearchService`. This is inconsistent with how the other packages work.
**Recommendation:** Either add re-exports in `game/research/__init__.py` matching the pattern in `game/core/__init__.py`, or document the deliberate subpackage-only export strategy if intended.
**Effort:** Simple

#### MAJOR: Unused json Import in registry.py
**ID:** CON-FND-011
**Location:** `game/core/registry.py:45`
**Issue:** `import json` is present but never used in `registry.py`. The module uses `game.core.json_utils` for JSON operations.
**Impact:** Dead import adds confusion about whether JSON operations happen in this module. Violates clean import conventions.
**Recommendation:** Remove the unused `import json` line.
**Effort:** Simple

#### MINOR: Missing Module Docstring in logger.py
**ID:** CON-FND-012
**Location:** `game/core/logger.py:1`
**Issue:** `logger.py` has no module docstring. Every other module in `game/core/` has a descriptive module docstring explaining the module's purpose, usage, and exception behavior. This is the only module in `game/core/` without one.
**Impact:** Inconsistent documentation within the core package.
**Recommendation:** Add a module docstring matching the style used in other core modules (e.g., `json_utils.py`, `math.py`, `paths.py`).
**Effort:** Simple

#### MINOR: Inconsistent Method Naming in Logger Class
**ID:** CON-FND-013
**Location:** `game/core/logger.py:43-57`
**Issue:** The `Logger` class has a method named `log()` that maps to `logger.debug()`, while separate methods `info()`, `warning()`, and `error()` map to their respective log levels. The module-level convenience function is `log_debug()` which calls `Logger.instance().log()`. The mismatch between the method name (`log` implying general logging) and its actual behavior (debug level) is confusing. All other methods use explicit level names.
**Impact:** `log()` suggests a general-purpose method but only logs at debug level. A developer might call `Logger.instance().log("critical info")` expecting it to be visible, but it goes to debug.
**Recommendation:** Rename `Logger.log()` to `Logger.debug()` to match the naming convention of the other methods (`info`, `warning`, `error`).
**Effort:** Simple

---

### Phase 3: API Design Consistency

#### MAJOR: Mixed Return Conventions for "Not Found" Across Core APIs
**ID:** CON-FND-014
**Location:** Multiple files in game/core/
**Issue:** Core APIs use inconsistent patterns for "not found" cases:
- `load_json()` returns a default value (default `None`) on failure -- never raises
- `load_json_required()` raises `FileNotFoundError` / `json.JSONDecodeError` on failure -- never returns default
- `RegistryManager.get_validator()` returns `None` when validator not set
- `get_default_registries()` raises `StateException` when not initialized
- `StrategyMetadataService.get_strategy_id_by_name()` returns `None` when not found
- `StrategyMetadataService.get_strategy_display_name()` returns the input `strategy_id` as fallback

While `load_json`/`load_json_required` is a deliberate pair (documented), the pattern is not consistently applied elsewhere. `get_default_registries()` raises while `get_validator()` returns None for the same concept ("not initialized").
**Impact:** Callers must know each function's specific convention. The inconsistency between raise-on-missing vs return-None-on-missing for initialization state is particularly error-prone.
**Recommendation:** Establish a clear convention: either all "required" accessors raise on uninitialized state, or all return `Optional`. Document the chosen convention in the module or CLAUDE.md.
**Effort:** Medium

#### MAJOR: StrategyManager Methods Lack Type Hints
**ID:** CON-FND-015
**Location:** `game/ai/strategy_manager.py:83-127`
**Issue:** `StrategyManager.load_data()`, `get_strategy()`, `get_targeting_policy()`, `get_movement_policy()`, and `resolve_strategy()` all lack return type hints. The `clear()` and `__init__()` methods also lack type hints on attributes. Meanwhile, every other class in the AI package (`IControllable`, `ShipControllableAdapter`, `AIBehavior`) has complete type hints on all method signatures.
**Impact:** `StrategyManager` is the least typed class in `game/ai/`, breaking the otherwise consistent typing pattern. Callers cannot benefit from IDE autocomplete or static analysis for strategy resolution.
**Recommendation:** Add return type hints to all `StrategyManager` methods, matching the thoroughness of `IControllable` and `ShipControllableAdapter`.
**Effort:** Simple

#### MINOR: Inconsistent Naming Between is_alive Property vs Method
**ID:** CON-FND-016
**Location:** `game/ai/interfaces/controllable.py:139` vs `game/engine/collision.py:138`
**Issue:** `IControllable.is_alive()` is defined as an `@abstractmethod` (callable method returning `bool`), and `ShipControllableAdapter.is_alive()` delegates to `self._ship.is_alive` (a property). In `collision.py:138`, `s.is_alive` is accessed as a property (no parentheses). In `controller.py:277`, it is called as `self.ship.is_alive()` (with parentheses). The underlying `Ship.is_alive` is a property, but `IControllable` defines it as a method.
**Impact:** The adapter works because Python allows properties and methods to be called interchangeably in some contexts, but the interface contract says "method" while the implementation is a property. This is a semantic inconsistency that could bite if someone creates a different `IControllable` implementation.
**Recommendation:** Change `IControllable.is_alive` to use `@property` decorator instead of `@abstractmethod` to match the actual Ship implementation.
**Effort:** Simple

---

### Phase 4: Project Pattern Adherence

#### MAJOR: StrategyMetadataService Uses Manual Singleton Instead of SingletonMeta (Project Pattern Violation)
**ID:** CON-FND-017
**Location:** `game/core/strategy_metadata.py:34-83`
**Issue:** This is the same finding as CON-FND-001 but viewed from the project pattern perspective. The project has a `SingletonMeta` metaclass specifically designed to eliminate duplicate singleton boilerplate ("Eliminates duplicate singleton boilerplate in ~7 classes" -- from `singleton.py` docstring). `StrategyMetadataService` is the only class in the entire shard that implements its own singleton pattern manually instead of using `SingletonMeta`.
**Impact:** Violates the project's established pattern for singletons. The project convention (per CLAUDE.md) prefers "Extract abstraction over copy-paste" and "Minimize technical debt."
**Recommendation:** Migrate to `SingletonMeta` metaclass.
**Effort:** Simple

#### INFO: Screenshot Manager Accesses Private Renderer via _renderer
**ID:** CON-FND-018
**Location:** `game/core/screenshot_manager.py:150,176`
**Issue:** `capture_strategy_layer()` accesses `scene._renderer` (a private attribute with underscore prefix), `scene.ui`, and checks for `scene.build_queue_screen`. This method reaches deep into strategy screen internals rather than using a public API.
**Impact:** Tight coupling between core layer and UI layer internals. If `StrategyScreen` refactors its renderer, this method breaks. However, this is in a debug/capture utility so practical impact is low.
**Recommendation:** Consider adding a public `render_to_surface()` method on `StrategyScreen` that `capture_strategy_layer` can call instead of reaching into private attributes.
**Effort:** Medium

---

### Phase 5: Per-Module Internal Consistency

#### INFO: game/engine/ Is Internally Consistent But Less Polished Than Other Modules
**ID:** CON-FND-019
**Location:** `game/engine/spatial.py`, `game/engine/physics.py`, `game/engine/collision.py`
**Issue:** The `game/engine/` package has a well-structured `__init__.py` with proper exports, but the individual modules vary significantly in code quality:
- `physics.py`: Excellent module docstring, clear coordinate system docs, type-hinted `apply_force()`
- `collision.py`: Excellent module docstring with mathematical formulas, proper type hints
- `spatial.py`: No docstring, no type hints, minimal code

This suggests `spatial.py` was written earlier and not revisited when the documentation/typing standards were established for the other two files.
**Impact:** Low -- the code works correctly. The inconsistency is purely in documentation/typing coverage.
**Recommendation:** Bring `spatial.py` up to the documentation and typing standard of `physics.py` and `collision.py`.
**Effort:** Simple

#### INFO: game/research/ Has Clean Internal Consistency
**ID:** CON-FND-020
**Location:** `game/research/` (all files)
**Issue:** The research package is internally very consistent:
- All data classes use `@dataclass` with proper type hints
- All serialization uses `to_dict()`/`from_dict()` pattern consistently
- All modules use `game.core.logger` functions (not stdlib logging)
- Service is stateless (`ResearchService` with `@classmethod` methods)
- UI components follow clear delegation patterns

No significant internal inconsistencies found. This package could serve as a model for other packages.
**Impact:** None (positive finding).
**Recommendation:** No action needed. Consider this package as a reference for code quality standards.
**Effort:** N/A

#### INFO: game/ai/ Has Mostly Good Internal Consistency With One Exception
**ID:** CON-FND-021
**Location:** `game/ai/` (all files)
**Issue:** The AI package is internally consistent in most respects:
- All behaviors follow the same `AIBehavior` base class pattern
- `IControllable` interface is comprehensive and well-documented
- `ShipControllableAdapter` implements every method with proper delegation
- `TargetEvaluator` uses a consistent static method pattern with `(score, match)` tuples

The one exception is the logging approach (CON-FND-002), where `game/ai/` uses stdlib logging while the rest of the codebase uses `game.core.logger`.
**Impact:** Low -- the pattern deviation is limited to logging.
**Recommendation:** Address CON-FND-002 to complete the consistency.
**Effort:** Simple

#### MINOR: Inconsistent Use of import Inside Function Body
**ID:** CON-FND-022
**Location:** `game/ai/behaviors.py:443,452` (`ErraticBehavior`), `game/core/resources.py:68`, `game/core/input_mapper.py:349`
**Issue:** Most modules in the shard import all dependencies at the top of the file. However:
- `ErraticBehavior` imports `random` inside both `enter()` and `update()` methods (line 443 and 452)
- `load_resources_data()` imports `copy` inside the function body (line 68)
- `InputMapper.save_user_overrides()` imports `Paths` inside the method body (line 349)

The `Paths` import in `input_mapper.py` is justified (avoiding circular import), and `copy` in `resources.py` may be intentional for lazy loading. But `import random` inside `ErraticBehavior` methods has no such justification -- `random` is a stdlib module with no circular dependency risk, and it's imported twice in the same class.
**Impact:** Minor performance overhead and code inconsistency. The `import random` is called every tick during combat.
**Recommendation:** Move `import random` to the top of `behaviors.py`. Keep the other in-function imports if they are intentional (add comments explaining why).
**Effort:** Simple

## Top 5 Priority Issues

1. **CON-FND-009 (CRITICAL):** `load_resources` and `load_resources_data` have duplicated error handling with subtle differences (deepcopy vs not). Refactor `load_resources` to delegate to `load_resources_data` to eliminate the maintenance trap and inconsistent safety guarantees.

2. **CON-FND-002 (MAJOR):** The `game/ai/` package uses stdlib `logging.getLogger(__name__)` while the rest of the codebase uses `game.core.logger` convenience functions. AI subsystem logs may go to different handlers or be silently lost. Unify the logging approach.

3. **CON-FND-001/017 (MAJOR):** `StrategyMetadataService` manually implements a singleton pattern while `SingletonMeta` exists specifically for this purpose. This creates two singleton patterns to understand and maintain. Migrate to `SingletonMeta`.

4. **CON-FND-014 (MAJOR):** Mixed return conventions for "not found" across core APIs (some raise, some return None, some return fallback values). Establish and document a clear convention.

5. **CON-FND-015 (MAJOR):** `StrategyManager` methods lack type hints, making it the least-typed class in `game/ai/`. Add return type hints to all public methods.
