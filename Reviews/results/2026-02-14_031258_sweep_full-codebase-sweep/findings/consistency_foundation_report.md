# Consistency Violations Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 16
- **Critical:** 0 | **Major:** 4 | **Minor:** 9 | **Info:** 3

## Findings

### Phase 1: Naming Convention Analysis

#### MINOR: Inconsistent Verb Prefix for Retrieval Methods
**ID:** CON-FND-001
**Location:** `game/ai/combat_utils.py:50-140`, `game/ai/interfaces/controllable.py:40-210`
**Issue:** The IControllable interface uses `get_` prefix consistently (e.g., `get_position`, `get_rotation`, `get_velocity`), but combat_utils.py uses different patterns:
- `get_position()` - follows interface
- `get_rotation()` - follows interface
- `get_entity_id()` - not part of interface, standalone utility
- `safe_distance()` - no prefix at all
- `get_hp_percent()` - follows interface pattern
- `is_in_pdc_arc()` - uses `is_` prefix for boolean check (correct)

The inconsistency is that `safe_distance` does not follow the pattern of `get_distance` or `calculate_distance`.
**Impact:** Minor cognitive overhead when navigating the API.
**Recommendation:** Consider renaming `safe_distance` to `get_safe_distance` or `calculate_distance` to match the verb prefix pattern.
**Effort:** Simple

#### MINOR: Mixed Boolean Naming Patterns
**ID:** CON-FND-002
**Location:** `game/ai/interfaces/controllable.py:139-148`, `game/ai/combat_utils.py:34-47`
**Issue:** Boolean methods use inconsistent naming:
- `is_alive()` - uses `is_` prefix
- `is_in_formation()` - uses `is_` prefix
- `is_vector2_like()` - uses `is_` prefix (in combat_utils)
- `get_is_thrusting()` - uses `get_is_` which is redundant

The `get_is_thrusting()` pattern deviates from the cleaner `is_thrusting()` pattern used elsewhere.
**Impact:** Minor inconsistency in API ergonomics.
**Recommendation:** Prefer `is_` prefix directly for boolean checks. `get_is_thrusting()` could be `is_thrusting()`.
**Effort:** Medium (interface change requires adapter updates)

#### INFO: Class Suffix Patterns
**ID:** CON-FND-003
**Location:** Multiple files across shard
**Issue:** Class naming suffixes are reasonably consistent within this shard:
- Services: `ResearchService`, `StrategyMetadataService` - consistent `Service` suffix
- Managers: `StrategyManager`, `RegistryManager` - consistent `Manager` suffix
- Controllers: `AIController`, `ResearchControlPanel` - slight variation (`Controller` vs `ControlPanel`)
- Providers: `DefaultRegistryProvider`, `TestRegistryProvider` - consistent `Provider` suffix
- Trackers: `ResearchTracker` - uses `Tracker` suffix

This is internally consistent within domain boundaries.
**Impact:** Low - natural variation based on domain concepts.
**Recommendation:** No action needed - current naming is appropriate.
**Effort:** N/A

### Phase 2: Structural Pattern Analysis

#### MAJOR: Inconsistent Singleton Pattern Usage
**ID:** CON-FND-004
**Location:** `game/core/singleton.py`, `game/core/registry.py:379-397`, `game/ai/strategy_manager.py`
**Issue:** The codebase has a proper `SingletonMeta` metaclass but also uses module-level singleton patterns:
1. `SingletonMeta` - proper metaclass-based singleton (used by Logger, Profiler, StrategyManager, etc.)
2. `_default_provider` in registry.py:379-397 - manual module-level singleton pattern
3. `_default_registries` in registry.py:81 - manual module-level singleton pattern

The `get_default_registry_provider()` function implements its own singleton pattern instead of using `SingletonMeta`:
```python
_default_provider: Optional[DefaultRegistryProvider] = None

def get_default_registry_provider() -> DefaultRegistryProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = DefaultRegistryProvider()
    return _default_provider
```

This is inconsistent with the metaclass pattern used by RegistryManager itself.
**Impact:** Two different singleton patterns in the same module increase cognitive load and potential for bugs.
**Recommendation:** Either have `DefaultRegistryProvider` use `SingletonMeta`, or document why the manual pattern is intentional here.
**Effort:** Medium

#### MAJOR: Mixed Logging Patterns
**ID:** CON-FND-005
**Location:** `game/core/logger.py`, `game/ai/combat_utils.py:19`, `game/ai/controller.py:52`
**Issue:** Two different logging patterns are in use:
1. **Core logger module** (`game/core/logger.py`): Uses custom `Logger` singleton with convenience functions `log_debug`, `log_info`, `log_warning`, `log_error`
2. **AI module** (`game/ai/combat_utils.py:19`, `game/ai/controller.py:52`): Uses standard `logging.getLogger(__name__)` pattern

Example in combat_utils.py:
```python
import logging
logger = logging.getLogger(__name__)
...
logger.warning("Distance calculation failed: %s", e)
```

Example in core/json_utils.py:
```python
from game.core.logger import log_error, log_debug
...
log_error(f"Invalid JSON in {file_path}: {e}")
```

**Impact:** Inconsistent logging makes it harder to configure log levels uniformly and trace issues across modules.
**Recommendation:** Standardize on one pattern. The core logger functions could wrap the standard logging module to provide a unified API.
**Effort:** Medium

#### MINOR: Inconsistent Docstring Format
**ID:** CON-FND-006
**Location:** Throughout shard
**Issue:** Docstrings follow Google-style format generally, but with some variations:
- Most modules use Google-style with Args/Returns/Raises sections
- Some functions have minimal docstrings without full Args/Returns sections
- Type hints are present on most functions but some internal helpers lack them

Examples of good format (game/core/validation.py):
```python
def add_error(self, error: str, code: Optional[Union[str, ErrorCode]] = None) -> None:
    """Add an error and mark result as invalid.

    Args:
        error: Error message describing the validation failure.
        code: Optional error code for programmatic handling.
    """
```

Examples of minimal format (game/engine/spatial.py):
```python
def insert(self, obj: Any) -> None:
    """Insert an object into the grid based on its position."""
```

**Impact:** Minor - most critical APIs are well-documented.
**Recommendation:** Add full Args/Returns documentation to public APIs in engine and research modules.
**Effort:** Simple

#### MINOR: Import Organization Variations
**ID:** CON-FND-007
**Location:** Various files
**Issue:** Import organization is mostly consistent but has some variations:
- Most files group: stdlib -> third-party -> local imports
- Some files mix typing imports with regular imports
- Conditional imports with `TYPE_CHECKING` are used correctly in several places

Example of good organization (game/ai/ai_factory.py):
```python
from typing import List, Optional, TYPE_CHECKING

from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
from game.simulation.interfaces.ai_controller import IAIController

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.engine.spatial import SpatialGrid
```

**Impact:** Low - imports are generally well organized.
**Recommendation:** Ensure all files follow stdlib -> third-party -> local pattern with blank lines between groups.
**Effort:** Simple

### Phase 3: API Design Consistency

#### MAJOR: Inconsistent Error Handling Return Patterns
**ID:** CON-FND-008
**Location:** `game/core/json_utils.py:33-97`, `game/core/resources.py:54-98`
**Issue:** Similar operations have different error handling patterns:

1. `load_json()` returns `default` on failure (silent fallback)
2. `load_json_required()` raises exceptions on failure
3. `save_json()` returns `bool` indicating success/failure
4. `load_resources_data()` returns defaults with warnings logged

This means callers need to know which pattern each function uses:
```python
# Pattern 1: Check for None/default
data = load_json("config.json", default={})
# Pattern 2: Try/except
try:
    data = load_json_required("critical.json")
except FileNotFoundError:
    ...
# Pattern 3: Check bool return
if not save_json("output.json", data):
    handle_error()
```

**Impact:** API consumers must remember which pattern each function uses.
**Recommendation:** Document the patterns clearly in module docstring (which is done in json_utils.py). Consider adding a `load_json_or_raise()` pattern for consistency.
**Effort:** Simple (documentation already exists)

#### MINOR: Inconsistent Method Visibility Conventions
**ID:** CON-FND-009
**Location:** `game/research/ui/research_renderer.py:67-78`, `game/ai/controller.py:133-173`
**Issue:** Private method naming is mostly consistent with single underscore prefix, but some methods that could be private are public:
- `_get_font()`, `_draw_dependency_lines()`, `_draw_nodes()` - properly private
- `_build_capabilities_cache()`, `_score_and_sort_enemies()` - properly private
- `check_avoidance()`, `navigate_to()` in AIController - public but only used internally by behaviors

The `check_avoidance()` and `navigate_to()` methods are called by behavior classes, so they need to be "public" to the behavior classes, making this a design choice rather than an inconsistency.
**Impact:** Low - current visibility matches usage patterns.
**Recommendation:** No action needed - methods are appropriately visible for their usage.
**Effort:** N/A

### Phase 4: Project Pattern Adherence

#### INFO: Registry Pattern Adherence
**ID:** CON-FND-010
**Location:** `game/core/registry.py`
**Issue:** The registry pattern is well-implemented with:
- `GameRegistries` container for DI
- `RegistryManager` singleton for direct access
- `DefaultRegistryProvider`/`TestRegistryProvider` for testability
- Module-level functions for convenience (`get_default_registries()`, `freeze_registry()`)

This is a good implementation of the project's registry pattern with clear documentation of the three access tiers.
**Impact:** Positive - good pattern implementation.
**Recommendation:** This is a model to follow in other parts of the codebase.
**Effort:** N/A

#### MINOR: Singleton Pattern vs Dependency Injection Tension
**ID:** CON-FND-011
**Location:** `game/ai/strategy_manager.py:20-40`, `game/ai/controller.py:94`
**Issue:** `StrategyManager` uses singleton pattern but CLAUDE.md prefers dependency injection:
```python
class StrategyManager(metaclass=SingletonMeta):
    ...

# In AIController:
def get_resolved_strategy(self) -> Dict[str, Any]:
    strategy_id = self.ship.get_ai_strategy()
    return StrategyManager.instance().resolve_strategy(strategy_id)
```

The AIController directly accesses the singleton instead of receiving `StrategyManager` via constructor injection.
**Impact:** Makes unit testing AIController harder without mocking the singleton.
**Recommendation:** Consider passing StrategyManager (or IStrategyProvider protocol) to AIController constructor.
**Effort:** Medium

### Phase 5: Per-Module Internal Consistency

#### MINOR: game/core/ - Internal Consistency Good
**ID:** CON-FND-012
**Location:** `game/core/` (18 files)
**Issue:** The core module is internally consistent:
- All singletons use `SingletonMeta`
- All configuration classes use class attributes with `@classmethod` getters
- Exception hierarchy is clean and follows a pattern
- Protocols use `@runtime_checkable` consistently

Minor variation: Some modules have `__all__` at the top (constants.py), some at the bottom (exceptions.py).
**Impact:** Very low - module is well-organized.
**Recommendation:** Standardize `__all__` placement (prefer top of file after imports).
**Effort:** Simple

#### MINOR: game/ai/ - Internal Consistency Good
**ID:** CON-FND-013
**Location:** `game/ai/` (9 files)
**Issue:** The AI module is internally consistent:
- All behaviors inherit from `AIBehavior` base class
- All behaviors implement `enter()` and `update()` methods
- Interface adapter pattern is clean (`ShipControllableAdapter`)
- Logging uses standard library consistently within AI module

The module deviates from core by using standard logging instead of core logger.
**Impact:** See CON-FND-005 for cross-module logging inconsistency.
**Recommendation:** Consider whether AI module should use core logger for consistency.
**Effort:** Simple

#### MAJOR: game/research/ - Data Class Serialization Patterns
**ID:** CON-FND-014
**Location:** `game/research/data/research_tracker.py:22-37`, `game/research/data/tech_node.py`
**Issue:** Serialization patterns differ between data classes:
- `NodeState` has `to_dict()` and `from_dict()` class method
- `ResearchTracker` has `to_dict()` and `from_dict()` class method
- `TechNode` has no serialization methods (loaded from JSON via `TechTree.load_from_json()`)
- `TechRequirement` has no serialization methods

This creates an asymmetry where some classes can round-trip through serialization and others cannot.
**Impact:** If TechNode needs to be serialized (e.g., for save games), serialization code would need to be added.
**Recommendation:** Add `to_dict()`/`from_dict()` to TechNode and TechRequirement if save game support is needed.
**Effort:** Simple

#### INFO: game/engine/ - Internal Consistency Good
**ID:** CON-FND-015
**Location:** `game/engine/` (4 files)
**Issue:** The engine module is internally consistent and minimal:
- All classes are stateless or simple state containers
- Type hints use `Any` appropriately to avoid tight coupling
- Configuration comes from `PhysicsConfig` consistently

The module is small and focused, which limits opportunities for inconsistency.
**Impact:** Positive - well-scoped module.
**Recommendation:** No action needed.
**Effort:** N/A

#### MINOR: Camera Protocol Usage
**ID:** CON-FND-016
**Location:** `game/research/ui/research_scene.py:31-46`, `game/core/protocols.py:500-580`
**Issue:** The research scene uses dependency injection for Camera (PROJ-132), which is good:
```python
def _create_default_camera(width: int, height: int) -> Any:
    from game.ui.renderer.camera import Camera
    return Camera(width, height)
```

The `ICamera` protocol is defined in core/protocols.py and used correctly by `ResearchRenderer`. However, the late import in the factory function creates a slight code smell.
**Impact:** Low - the pattern works and avoids layer violations.
**Recommendation:** Document this pattern as an approved approach for cross-layer DI.
**Effort:** Simple (documentation)

## Top 5 Priority Issues

1. **CON-FND-005 (MAJOR):** Mixed Logging Patterns - AI module uses standard logging while core provides custom logger. Standardize on one approach for easier debugging and log configuration.

2. **CON-FND-004 (MAJOR):** Inconsistent Singleton Pattern Usage - `DefaultRegistryProvider` uses manual singleton while other classes use `SingletonMeta`. Choose one pattern for clarity.

3. **CON-FND-008 (MAJOR):** Inconsistent Error Handling Return Patterns - Different functions use different patterns (return default vs raise vs return bool). While documented, this increases cognitive load.

4. **CON-FND-014 (MAJOR):** Data Class Serialization Patterns - Not all research data classes have serialization methods, creating asymmetry.

5. **CON-FND-011 (MINOR):** Singleton Pattern vs Dependency Injection Tension - AIController accesses StrategyManager singleton directly, making testing harder. Consider DI approach.

---
*Analysis completed: 42 files scanned exhaustively in game/core/, game/ai/, game/research/, game/engine/*
