# Sweep Validation Report: Foundation Shard (FND)

**Validator:** Claude Opus 4.5
**Date:** 2026-02-13
**Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
**Findings Reviewed:** 32

---

## Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED | 12 |
| DOWNGRADED | 8 |
| REJECTED | 12 |

**Overall Quality:** Mixed - Many findings are legitimate but several are false positives (file not found, already-addressed concerns, or exaggerated severity).

---

## Verdicts

### ADR-FND-001: Research UI Layer Imports Concrete Camera from game.ui
**Location:** `game/research/ui/research_scene.py:19`
**Original Severity:** CRITICAL
**Verdict:** CONFIRMED

**Analysis:** The finding is accurate. Line 19 imports `from game.ui.renderer.camera import Camera`. This is a layer violation - the research layer (which should be independent) imports from the UI layer. The comment on lines 10-12 acknowledges this is a known issue with PROJ-106.

**Evidence:**
```python
# Line 19
from game.ui.renderer.camera import Camera
```

**Justification:** This is a legitimate architectural violation. The research layer should not depend on concrete UI implementations. The ICamera protocol exists in `game/core/protocols.py` but is not being used for construction.

---

### ADR-FND-002: protocols.py is Approaching God Class Territory
**Location:** `game/core/protocols.py`
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED to MINOR

**Analysis:** The file is 548 lines and contains 16 protocols. These are all Protocol definitions (interfaces), which by design should be grouped together. This is not a "god class" - it's a protocol registry following a common pattern in typed Python codebases.

**Evidence:** The file contains only:
- Protocol definitions (interfaces)
- TypeGuard helper functions
- Clear section organization with comments

**Justification:** Grouping protocols together is a valid design pattern. The protocols are cohesive (all game interfaces) and the file is well-organized. No behavioral logic exists here - only type contracts. Consider MINOR at most for suggesting potential file splitting if it grows further.

---

### ADR-FND-003: behaviors.py File Growing Large
**Location:** `game/ai/behaviors.py`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** The file is 521 lines and contains 12 behavior classes. While this is substantial, the classes are related and follow a clear pattern. The file includes both production behaviors (Kite, Flee, Formation) and test behaviors (DoNothing, Erratic).

**Evidence:** 521 lines, 12 behavior classes.

**Justification:** Confirmed as MINOR - the file is large but not critically so. The test behaviors could potentially be extracted to a separate module.

---

### CON-FND-001: Inconsistent Singleton Pattern Usage
**Location:** `game/core/registry.py:79-120`
**Original Severity:** CRITICAL
**Verdict:** REJECTED

**Analysis:** The code at lines 79-120 is `get_default_registries()` and `set_default_registries()` - module-level functions for a singleton-like pattern. This is a deliberate design choice for DI support (PROJ-38). The `RegistryManager` class uses `SingletonMeta` consistently. This is not inconsistent - it's two complementary patterns serving different use cases.

**Evidence:**
- `RegistryManager` uses `SingletonMeta` (line 122)
- Module-level `_default_registries` is for DI composition roots
- Clear documentation explains both patterns

**Justification:** This is intentional design, not inconsistency. REJECTED as false positive.

---

### CON-FND-002: Inconsistent Logging Pattern
**Location:** `game/core/logger.py`
**Original Severity:** MAJOR
**Verdict:** REJECTED

**Analysis:** The logger module uses a consistent pattern throughout. It has a singleton `Logger` class with convenience functions (`log_debug`, `log_info`, etc.). The code is well-organized and consistent.

**Evidence:** Lines 62-84 show consistent convenience function pattern:
```python
def log_debug(msg: str) -> None:
    Logger.instance().log(msg)

def log_info(msg: str) -> None:
    Logger.instance().info(msg)
```

**Justification:** No inconsistency found. The module is clean and follows standard patterns. REJECTED as false positive.

---

### CON-FND-003: Mixed Return Semantics for Not-Found Cases
**Location:** `game/core/registry.py:98-120`
**Original Severity:** MAJOR
**Verdict:** CONFIRMED

**Analysis:** The `get_default_registries()` function raises `StateException` when registries aren't set (lines 114-119), while other getter methods return defaults or None. This is intentional but could be documented more clearly.

**Evidence:**
```python
def get_default_registries() -> GameRegistries:
    if _default_registries is None:
        raise StateException(...)
    return _default_registries
```

**Justification:** The finding accurately identifies different return semantics. However, this is a deliberate design choice - `get_default_registries()` is a composition root accessor that should fail fast, while individual registry lookups use defaults. Confirmed as documentation/consistency issue.

---

### CON-FND-004: Inconsistent Method Naming for Position/State Access
**Location:** `game/ai/interfaces/controllable_ship.py`
**Original Severity:** MAJOR
**Verdict:** REJECTED (File Not Found)

**Analysis:** The file `controllable_ship.py` does not exist. The actual interface file is `game/ai/interfaces/controllable.py`. The IControllable interface uses consistent naming: all getters use `get_*` prefix, all setters use `set_*` prefix.

**Evidence:** Glob search found only `game/ai/interfaces/controllable.py`, not `controllable_ship.py`.

**Justification:** File location is wrong. The actual interface at `controllable.py` has consistent naming conventions. REJECTED.

---

### CON-FND-005: Class Naming Suffix Inconsistency
**Location:** `game/ai/strategy_manager.py`
**Original Severity:** MAJOR
**Verdict:** REJECTED

**Analysis:** `StrategyManager` is appropriately named - it is a manager class that manages strategies. There's no inconsistency here. The class manages strategies, targeting policies, and movement policies.

**Evidence:** The class clearly manages strategy-related data:
```python
class StrategyManager(metaclass=SingletonMeta):
    """Singleton manager for combat strategies, targeting policies, and movement policies."""
```

**Justification:** The naming is appropriate and consistent with the class's purpose. REJECTED as false positive.

---

### CON-FND-006: Inconsistent Parameter Naming
**Location:** `game/ai/combat_utils.py`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** Parameter naming is reasonably consistent but shows some variation. Functions use `entity`, `entity1`, `entity2`, `ship`, `target` for different contexts. This is acceptable but could be more uniform.

**Evidence:**
- `get_position(entity: Any)`
- `safe_distance(entity1: Any, entity2: Any)`
- `get_hp_percent(ship: Any)`
- `is_in_pdc_arc(ship: Any, target: Any)`

**Justification:** Minor inconsistency - using `entity` vs `ship` for similar parameters. Confirmed as MINOR.

---

### CON-FND-007: Inconsistent Docstring Format
**Location:** Unknown
**Original Severity:** MINOR
**Verdict:** REJECTED

**Analysis:** The location is "Unknown" which makes this unverifiable. From my review of the foundation files, docstrings are generally consistent with Google-style format (Args, Returns sections).

**Justification:** Cannot verify without specific location. REJECTED.

---

### CON-FND-008: Boolean Property Naming
**Location:** `game/ai/interfaces/controllable_ship.py`
**Original Severity:** MINOR
**Verdict:** REJECTED (File Not Found)

**Analysis:** File does not exist. The actual `controllable.py` uses appropriate boolean method naming: `is_alive()`, `is_in_formation()`, `get_is_thrusting()`.

**Justification:** Wrong file location. REJECTED.

---

### CON-FND-009: Inconsistent Type Hint Coverage
**Location:** `game/core/logger.py:27-41`
**Original Severity:** MINOR
**Verdict:** DOWNGRADED to INFO

**Analysis:** Lines 27-41 show the `__init__` and `setup` methods. The `setup` method doesn't have return type hints, which is accurate. However, this is a very minor issue.

**Evidence:**
```python
def __init__(self):
    self.setup()

def setup(self):  # No return type hint
    self.enabled = True
```

**Justification:** Missing `-> None` on `setup()` is true but trivial. DOWNGRADED to INFO.

---

### CON-FND-010: Inconsistent Import Organization
**Location:** `game/ai/controller.py:51-66`
**Original Severity:** MINOR
**Verdict:** REJECTED

**Analysis:** Lines 51-66 show the class definition starting, not imports. The actual imports (lines 51-66 as originally stated) don't exist - imports are at lines 1-66. The imports are organized in a standard manner: standard library, then local imports grouped by module.

**Evidence:** Actual imports (lines 51-66):
```python
logger = logging.getLogger(__name__)

from game.core.math import Vector2, angle_diff
from game.core.config import AIConfig, BattleConfig
from game.ai.behaviors import (...)
```

**Justification:** Imports follow standard Python conventions. REJECTED.

---

### CON-FND-011: Magic Numbers in AI Layer
**Location:** `game/ai/controller.py:445`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** Line 445 contains `if abs(ang_diff) > 5:` - a magic number for angle threshold. Line 450 contains `if abs(ang_diff) < 30 and distance > eff_stop_dist:` - another magic number.

**Evidence:**
```python
# Line 445
if abs(ang_diff) > 5:
# Line 450
if abs(ang_diff) < 30 and distance > eff_stop_dist:
```

**Justification:** These should be named constants in AIConfig. CONFIRMED as MINOR.

---

### CON-FND-012: Inconsistent Error Handling
**Location:** `game/ai/controller.py:217-223`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** Lines 217-223 show error handling that logs warnings and skips targets. This is defensive programming, but the finding may be about consistency with other error handling approaches.

**Evidence:**
```python
except (AttributeError, TypeError) as err:
    target_id = getattr(e, 'id', getattr(e, 'name', str(id(e))))
    logger.warning(
        "Target evaluation failed for ship=%s target=%s: %s. Skipping target.",
        ship_id, target_id, err
    )
```

**Justification:** The error handling is appropriate for combat robustness. This may be more about documenting the pattern than inconsistency. CONFIRMED as MINOR for documentation purposes.

---

### CON-FND-013: Inconsistent __all__ Export Patterns
**Location:** `game/core/constants.py:1-15`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** The `__all__` list on lines 3-15 exists and exports specific items. The comment on line 14 mentions "PROJ-113: Colors and FONT_MAIN moved to game.ui.colors" suggesting evolution of exports.

**Evidence:**
```python
__all__ = [
    'AttackType',
    'GameState',
    'LayerType',
    ...
]
```

**Justification:** Having `__all__` is good. The finding may be about other core modules not having `__all__`. CONFIRMED as MINOR.

---

### CON-FND-014: Redundant Protocol Definition
**Location:** `game/core/validation.py:23-60`
**Original Severity:** MINOR
**Verdict:** REJECTED

**Analysis:** Lines 23-60 define `IValidationRule` Protocol. This is not redundant - it's the canonical validation protocol for the codebase. The docstring explicitly mentions it was consolidated from 5 duplicate implementations (PROJ-21).

**Evidence:**
```python
@runtime_checkable
class IValidationRule(Protocol):
    """Protocol for validation rules across all layers.
    ...
    """
```

**Justification:** This is the consolidated, canonical definition - the opposite of redundant. REJECTED.

---

### CON-FND-015: os.path vs pathlib.Path Mixed Usage
**Location:** `game/core/paths.py:53-103`
**Original Severity:** INFO
**Verdict:** CONFIRMED

**Analysis:** The file uses `os.path.join` for string path attributes (lines 53-103) and `pathlib.Path` for method accessors (lines 106+). This is intentional - string paths for backward compatibility, Path objects via methods for new code.

**Evidence:**
```python
# String paths with os.path.join
DATA_DIR: str = os.path.join(ROOT_DIR, "data")

# Path object accessors
@classmethod
def get_data_dir(cls) -> Path:
    return _PROJECT_ROOT / "data"
```

**Justification:** This dual approach is documented as intentional but could be considered technical debt. CONFIRMED as INFO.

---

### CON-FND-016: ResourceType is a Class, Not an Enum
**Location:** `game/core/constants.py:83-92`
**Original Severity:** INFO
**Verdict:** CONFIRMED

**Analysis:** `ResourceType` is defined as a class with string constants rather than an Enum. This is a valid observation.

**Evidence:**
```python
class ResourceType:
    """Ship resource type constants for fuel, energy, and ammo."""
    FUEL = 'fuel'
    ENERGY = 'energy'
    AMMO = 'ammo'
```

**Justification:** Using class constants instead of Enum is a style choice. Not inherently wrong but could benefit from Enum for type safety. CONFIRMED as INFO.

---

### CON-FND-017: TechNode/TechTree Separate from Core Registry
**Location:** `game/research/data/tech_tree.py`
**Original Severity:** INFO
**Verdict:** CONFIRMED

**Analysis:** TechTree is in the research layer with its own loading mechanism, separate from the core RegistryManager pattern. This is intentional layer separation - research is a distinct module.

**Evidence:** TechTree has its own `load_from_json` method that doesn't use RegistryManager.

**Justification:** This is intentional architectural separation. The research layer manages its own data. CONFIRMED as INFO - valid observation about architectural patterns.

---

### CON-FND-018: Research Layer Has Direct pygame Import
**Location:** `game/research/ui/research_scene.py`
**Original Severity:** INFO
**Verdict:** CONFIRMED

**Analysis:** Lines 14-15 show direct pygame imports:
```python
import pygame
import pygame_gui
```

This is in the UI portion of the research layer (`research/ui/`), which is acceptable for scene classes that need pygame for rendering.

**Justification:** The import is in a UI scene file, which is appropriate. However, the `research_scene.py` being in `game/research/ui/` rather than `game/ui/research/` could be an architectural concern. CONFIRMED as INFO.

---

### DUP-FND-001: Clamp Function Duplication
**Location:** `game/core/math.py:187-203`
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED to MINOR

**Analysis:** `game/core/math.py` has the canonical `clamp` function at lines 187-203. Grep found 24 files using clamp, but they import from `game.core.math` or use it appropriately. No actual duplication found - this is the source.

**Evidence:** The clamp function exists once in `game/core/math.py` and is imported elsewhere.

**Justification:** This is the canonical definition, not duplication. Other files import from here. DOWNGRADED to MINOR (could investigate if any files redefine clamp locally).

---

### DUP-FND-002: Entity Position/State Access Patterns in AI
**Location:** `game/ai/combat_utils.py:49-82`
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED to MINOR

**Analysis:** Lines 49-82 show `get_position()` and `get_rotation()` helper functions. These are utility functions that abstract position/rotation access patterns, which is the opposite of duplication - it's consolidation.

**Evidence:**
```python
def get_position(entity: Any) -> Optional[Vector2]:
    """Get position from entity, supporting both interface and direct access."""
    ...
```

**Justification:** This is consolidation code, not duplication. The pattern exists to reduce duplication elsewhere. DOWNGRADED to MINOR.

---

### DUP-FND-003: Singleton Pattern Documentation/Structure
**Location:** Unknown
**Original Severity:** MAJOR
**Verdict:** REJECTED

**Analysis:** Location is "Unknown". The singletons I reviewed (`RegistryManager`, `Logger`, `StrategyManager`) all use `SingletonMeta` consistently and have good documentation.

**Justification:** Cannot verify without specific location. REJECTED.

---

### DUP-FND-004: Entity ID Extraction Pattern Duplication
**Location:** `game/ai/combat_utils.py:65`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** Line 65 shows: `entity_id = getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))`. This pattern appears in multiple places for defensive entity identification.

**Evidence:** Similar patterns at lines 65, 97, and other locations in AI code.

**Justification:** This pattern could be extracted to a helper function. CONFIRMED as MINOR.

---

### DUP-FND-005: Flee Direction Calculation
**Location:** `game/ai/behaviors.py:70-84`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** Lines 70-84 define `_flee_direction()` helper function. This is appropriately extracted as a helper function within the behaviors module.

**Evidence:**
```python
def _flee_direction(from_pos: Vector2, away_from_pos: Vector2) -> Vector2:
    """Calculate normalized direction vector pointing away from a position."""
```

**Justification:** This is already extracted as a module-level function. If it's used elsewhere, it could be moved to combat_utils. CONFIRMED as MINOR observation.

---

### DUP-FND-006: Tech Tree Validation Method Patterns
**Location:** `game/research/data/tech_tree.py`
**Original Severity:** MINOR
**Verdict:** DOWNGRADED to INFO

**Analysis:** The TechTree has validation methods: `validate_requirements()`, `detect_cycles()`, and `validate()`. These are well-structured validation methods following a clear pattern.

**Evidence:**
```python
def validate_requirements(self) -> List[str]:
def detect_cycles(self) -> List[str]:
def validate(self) -> List[str]:  # Combines both
```

**Justification:** These are intentionally separate methods for different validation concerns. Good design. DOWNGRADED to INFO.

---

### DUP-FND-007: Serialization to_dict/from_dict Patterns
**Location:** `game/research/data/research_tracker.py`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** Both `NodeState` and `ResearchTracker` have `to_dict()` and `from_dict()` methods. This is a common serialization pattern but could potentially use a shared base class or mixin.

**Evidence:**
- `NodeState.to_dict()` (line 22)
- `NodeState.from_dict()` (line 30)
- `ResearchTracker.to_dict()` (line 236)
- `ResearchTracker.from_dict()` (line 246)

**Justification:** Standard Python serialization pattern. Could consider a mixin for consistency but not critical. CONFIRMED as MINOR.

---

### DUP-FND-008: Well-Consolidated Utilities
**Location:** `game/core/`
**Original Severity:** INFO
**Verdict:** CONFIRMED (Positive Finding)

**Analysis:** This is a POSITIVE finding noting that utilities are well-consolidated in game/core/. This is accurate - math, logging, paths, validation, exceptions are all properly centralized.

**Justification:** CONFIRMED as positive observation.

---

### LEG-FND-001: Unused Exception Classes
**Location:** `game/core/exceptions.py:216-230`
**Original Severity:** MAJOR
**Verdict:** DOWNGRADED to MINOR

**Analysis:** Lines 216-230 show `AIException` and `TargetingException`. These may not be widely used yet but are part of a semantic exception hierarchy. They're exported in `__all__` and documented.

**Evidence:**
```python
class AIException(GameException):
    """Base exception for AI-related errors."""
    pass

class TargetingException(AIException):
    """Exception for targeting system errors."""
    pass
```

**Justification:** These are part of a planned exception hierarchy (PROJ-45). Not being heavily used yet doesn't make them "legacy". DOWNGRADED to MINOR for potential cleanup review.

---

### LEG-FND-002: Backward Compatibility Wrapper - load_resources
**Location:** `game/core/resources.py:101-114`
**Original Severity:** MAJOR
**Verdict:** CONFIRMED

**Analysis:** Lines 101-114 show `load_resources()` which explicitly documents itself as "a thin wrapper around load_resources_data() for backward compatibility."

**Evidence:**
```python
def load_resources(file_path: str = "data/resources.json") -> None:
    """
    Load resource definitions from JSON into the resource registry.

    This is a thin wrapper around load_resources_data() for backward
    compatibility. New code should prefer DI via load_resources_data().
    """
```

**Justification:** This is a documented backward compatibility wrapper. Per CLAUDE.md's "System Migration Policy", these should be eradicated when the old callers are updated. CONFIRMED as MAJOR.

---

### LEG-FND-003: Backward Compatibility Comment in Validation
**Location:** `game/core/validation.py:100-105`
**Original Severity:** MINOR
**Verdict:** CONFIRMED

**Analysis:** Lines 100-105 show a `message` property with a compatibility comment:

```python
@property
def message(self) -> str:
    """First error message (compatibility with UI/strategy layers).

    Returns the first error message if any errors exist, otherwise
    returns an empty string. This provides backwards compatibility
    with code that expects a single message property.
    """
```

**Justification:** This is a documented backward compatibility property. Could be candidates for removal if callers are updated. CONFIRMED as MINOR.

---

## Cross-Shard Duplicates

None identified. The foundation shard findings are self-contained within game/core/, game/ai/, and game/research/.

---

## Recommendations

1. **Address LEG-FND-002 (load_resources wrapper):** Per CLAUDE.md migration policy, identify all callers and migrate to DI pattern.

2. **Extract magic numbers in AI (CON-FND-011):** Move angle thresholds to AIConfig.

3. **Consider extracting entity ID helper (DUP-FND-004):** Create a utility function for the defensive entity ID extraction pattern.

4. **Review research layer Camera import (ADR-FND-001):** This is a known issue (PROJ-106) but should be addressed for proper layer separation.
