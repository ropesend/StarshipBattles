# Duplication & Fragmentation Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 41
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 3 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: Clamp Function Duplication
**ID:** DUP-FND-001
**Location:** `game/core/math.py:187-203` AND `game/strategy/generation/density/primitives/density_primitive.py:36-45`
**Issue:** Two implementations of clamp functionality exist:
- `game/core/math.py` provides a general-purpose `clamp(value, min_val, max_val)` function
- `game/strategy/generation/density/primitives/density_primitive.py` provides `clamp_density(value)` hardcoded to [0.0, 1.0] range

While `clamp_density` is more specialized, it duplicates the core functionality and could be replaced with a simple call to `clamp(value, 0.0, 1.0)` from core.

**Impact:** Low maintenance risk but violates DRY principle. Changes to clamping behavior would need to be made in two places.
**Recommendation:** Replace `clamp_density` with a call to `clamp(value, 0.0, 1.0)` from `game.core.math`, or document the intentional difference.
**Effort:** Simple

---

#### MAJOR: Entity Position/State Access Patterns in AI
**ID:** DUP-FND-002
**Location:** `game/ai/combat_utils.py:49-82` (get_position) AND `game/ai/combat_utils.py:84-112` (get_rotation)
**Issue:** The `get_position()` and `get_rotation()` utility functions in `combat_utils.py` implement nearly identical patterns for safe entity attribute access:
1. Try interface method (get_position/get_rotation)
2. Check if result is valid
3. Fall back to direct attribute access (.position/.angle)
4. Log warning on failure

Both functions share:
- ~20 lines of similar structure
- Same entity ID extraction pattern (`getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))`)
- Same try/except pattern with warning logging
- Same fallback logic

**Impact:** Any change to the access pattern must be duplicated. Future additions (e.g., `get_velocity()`) would copy the same pattern again.
**Recommendation:** Extract a generic `safe_entity_attribute()` helper or use a decorator pattern to reduce boilerplate. The entity ID extraction is already duplicated 3+ times in this file alone.
**Effort:** Medium

---

#### MAJOR: Singleton Pattern Documentation/Structure Duplication
**ID:** DUP-FND-003
**Location:** Multiple files using `metaclass=SingletonMeta`:
- `game/core/logger.py` (Logger)
- `game/core/registry.py` (RegistryManager)
- `game/core/profiling.py` (Profiler)
- `game/core/strategy_metadata.py` (StrategyMetadataService)
- `game/ai/strategy_manager.py` (StrategyManager)

**Issue:** While these classes correctly use the shared `SingletonMeta`, they each duplicate:
1. Docstring patterns for thread safety documentation
2. `clear()` method implementations that follow identical patterns
3. Similar lazy-loading patterns (especially in StrategyManager and StrategyMetadataService)

Example: Both `StrategyManager.clear()` and `StrategyMetadataService.clear()` follow the same structure - clear dictionaries, reset flags.

**Impact:** Documentation and method patterns must be maintained consistently across 5+ classes. The StrategyManager and StrategyMetadataService have very similar data loading patterns.
**Recommendation:** Consider a `SingletonService` base class that provides `clear()` template and standardized docstrings. The StrategyManager/StrategyMetadataService duplication specifically could benefit from consolidation - they both load strategy data from JSON.
**Effort:** Medium

---

#### MINOR: Entity ID Extraction Pattern Duplication
**ID:** DUP-FND-004
**Location:** `game/ai/combat_utils.py:65`, `game/ai/combat_utils.py:97`, `game/ai/combat_utils.py:143-144`, `game/ai/combat_utils.py:189-190`, `game/ai/controller.py:191`, `game/ai/controller.py:219`
**Issue:** The pattern `getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))` for safely extracting an entity identifier is repeated 6+ times across the AI module.

**Impact:** Minor maintenance overhead. Pattern is consistent but verbose.
**Recommendation:** Extract a `get_entity_id(entity)` helper function in `combat_utils.py`.
**Effort:** Simple

---

#### MINOR: Flee Direction Calculation
**ID:** DUP-FND-005
**Location:** `game/ai/behaviors.py:70-84` (_flee_direction function)
**Issue:** The `_flee_direction()` helper calculates a normalized direction vector away from a target. This pattern is used in multiple behaviors (FleeBehavior, KiteBehavior, AttackRunBehavior). While centralized in a function, the zero-length vector check and normalization is a common pattern that appears elsewhere in the codebase (e.g., weapon firing, projectile direction).

**Impact:** Low - the function is properly centralized within behaviors.py. However, similar patterns exist in simulation code.
**Recommendation:** Consider moving to `game/core/math.py` as a general `direction_away_from(from_pos, target_pos)` utility if the pattern is needed outside AI.
**Effort:** Simple

---

#### MINOR: Tech Tree Validation Method Patterns
**ID:** DUP-FND-006
**Location:** `game/research/data/tech_tree.py:191-263`
**Issue:** The `validate_requirements()` and `detect_cycles()` methods in TechTree share:
- Similar iteration patterns over nodes and requirements
- Similar error list accumulation
- Nearly identical docstring structures

The `validate()` method simply calls both and concatenates results.

**Impact:** Low - these are cohesive validation methods. However, if more validation types are added, the pattern will repeat.
**Recommendation:** Consider a validation framework with pluggable validators if the tech tree validation grows more complex.
**Effort:** Simple (low priority)

---

#### MINOR: Serialization to_dict/from_dict Patterns
**ID:** DUP-FND-007
**Location:** `game/research/data/research_tracker.py` (NodeState and ResearchTracker), `game/core/input_actions.py` (KeyBinding)
**Issue:** Multiple data classes implement `to_dict()` and `from_dict()` with similar patterns:
```python
def to_dict(self) -> Dict[str, Any]:
    return {'field1': self.field1, 'field2': self.field2}

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ClassName':
    return cls(field1=data.get('field1', default), ...)
```

30+ files across the codebase use this pattern (based on grep results).

**Impact:** Each serializable class must implement these methods manually. Changes to serialization format require updates to both methods.
**Recommendation:** Consider using a mixin or decorator for standardized serialization, or leverage dataclasses' `asdict()` more consistently. However, this is a broader codebase concern, not specific to the Foundation shard.
**Effort:** Complex (requires architectural decision)

---

#### INFO: Well-Consolidated Utilities
**ID:** DUP-FND-008
**Location:** `game/core/` module
**Issue:** No major issues found. The following are well-consolidated:
- **Vector2** (`game/core/math.py`) - Single implementation used throughout
- **ValidationResult** (`game/core/validation.py`) - Centralized, with clear documentation of previous consolidation (PROJ-21)
- **JSON utilities** (`game/core/json_utils.py`) - Centralized load/save with consistent error handling
- **Logging** (`game/core/logger.py`) - Single entry point for all logging
- **Hex math** (`game/core/hex_math.py`) - Complete hex grid implementation
- **Singleton pattern** (`game/core/singleton.py`) - Single metaclass used across codebase
- **Exception hierarchy** (`game/core/exceptions.py`) - Well-organized semantic exceptions

**Impact:** Positive - these are examples of good consolidation.
**Recommendation:** Use these as templates for future utility consolidation.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **DUP-FND-002 (MAJOR)**: Entity position/rotation access pattern duplication in AI combat_utils - creates maintenance burden and inconsistency risk as new accessor methods are added.

2. **DUP-FND-003 (MAJOR)**: Singleton service pattern duplication - StrategyManager and StrategyMetadataService have overlapping data loading concerns that could be unified.

3. **DUP-FND-004 (MINOR)**: Entity ID extraction pattern repeated 6+ times - simple fix that improves code clarity.

4. **DUP-FND-001 (MAJOR)**: Clamp function duplication - minor but demonstrates pattern of local utility functions that could use core utilities.

5. **DUP-FND-007 (MINOR)**: Serialization pattern duplication across 30+ files - architectural concern worth tracking for future refactoring.
