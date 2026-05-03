# Duplication & Fragmentation Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Files Scanned:** 42
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 3 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: Singleton Pattern Used by Many Classes with Similar clear()/reset() Semantics
**ID:** DUP-FND-001
**Location:** `game/core/strategy_metadata.py:54-60` AND `game/core/profiling.py:39-42` AND `game/ai/strategy_manager.py:53-64` AND `game/core/registry.py:217-237`
**Issue:** Multiple singleton classes implement nearly identical `clear()` methods for test isolation:
- `StrategyMetadataService.clear()` - resets `_strategies = {}`
- `Profiler.clear()` - resets `records = []` and generates new `session_id`
- `StrategyManager.clear()` - resets multiple dicts and `_loaded = False`
- `RegistryManager.clear()` - clears multiple dicts and resets `_validator`

All share the same purpose (test isolation) and similar structure (clear internal state), but each implements it independently. The `SingletonMeta.reset()` destroys the instance entirely, but `clear()` preserves the instance and is implemented separately in each class.
**Impact:**
- Inconsistent behavior across singletons (some have `clear()`, some don't)
- Boilerplate code duplication
- Risk of forgetting to clear new fields when adding state
**Recommendation:** Consider adding a `Clearable` protocol or mixin that provides a standard clear interface. Alternatively, document the convention that all singletons with mutable state must implement `clear()` with consistent semantics.
**Effort:** Medium

#### MAJOR: JSON Loading with Fallback Defaults Pattern Repeated
**ID:** DUP-FND-002
**Location:** `game/ai/strategy_manager.py:91-100` AND `game/core/strategy_metadata.py:139-143` AND `game/core/resources.py:74-98`
**Issue:** Multiple modules implement the same pattern for loading JSON with fallback to defaults:
```python
# Pattern 1: StrategyManager.load_data
targeting_data = load_json(os.path.join(base_path, targeting_file), default={})
self.targeting_policies = targeting_data.get('policies', {})

# Pattern 2: StrategyMetadataService.load_data
strategy_data = load_json(os.path.join(base_path, strategy_file), default={})
self._strategies = strategy_data.get('strategies', {})

# Pattern 3: resources.py
data = load_json_required(resolved_path)
result = {}
for res_def in data.get('resources', []):
    res_id = res_def.get('id')
    if res_id:
        result[res_id] = copy.deepcopy(res_def)
```
Each has:
1. Path resolution logic
2. JSON loading with error handling
3. Extraction of a specific key from the data
4. Default fallback when missing
**Impact:** Inconsistent error handling, duplicated path resolution logic, maintenance burden
**Recommendation:** Create a `DataLoader` utility class in game/core that provides a standard pattern for loading JSON data files with key extraction, path resolution, and fallback defaults.
**Effort:** Medium

#### MAJOR: get_position/get_rotation Access Pattern in AI Layer
**ID:** DUP-FND-003
**Location:** `game/ai/combat_utils.py:66-96` AND `game/ai/combat_utils.py:99-125`
**Issue:** `get_position()` and `get_rotation()` functions implement nearly identical defensive access patterns:
```python
def get_position(entity: Any) -> Optional[Vector2]:
    get_pos = getattr(entity, 'get_position', None)
    if get_pos is not None and callable(get_pos):
        try:
            result = get_pos()
            if is_vector2_like(result):
                return result
        except (AttributeError, TypeError) as e:
            logger.warning(...)
    return getattr(entity, 'position', None)

def get_rotation(entity: Any) -> float:
    get_rot = getattr(entity, 'get_rotation', None)
    if get_rot is not None and callable(get_rot):
        try:
            result = get_rot()
            if isinstance(result, (int, float)):
                return float(result)
        except (AttributeError, TypeError) as e:
            logger.warning(...)
    return float(getattr(entity, 'angle', 0.0))
```
Both functions:
1. Check for interface method via getattr
2. Try to call it with exception handling
3. Validate return type
4. Fall back to direct attribute access
**Impact:** Code duplication, potential for divergent behavior if one is updated but not the other
**Recommendation:** Extract a generic `safe_property_access(entity, method_name, attr_fallback, type_validator, default)` helper function that implements this pattern once.
**Effort:** Simple

#### MINOR: Direction Calculation Repeated in Behaviors
**ID:** DUP-FND-004
**Location:** `game/ai/behaviors.py:70-84` (FleeBehavior) AND `game/ai/behaviors.py:162-164` (KiteBehavior) AND `game/ai/behaviors.py:226-227` (AttackRunBehavior)
**Issue:** The flee/kite direction calculation is implemented in the module-level `_flee_direction()` function and reused, but the pattern of calculating "target position + direction * distance" is duplicated:
```python
# FleeBehavior
flee_dir = _flee_direction(ship_pos, target.position)
flee_pos = ship_pos + flee_dir * self.FLEE_DISTANCE

# KiteBehavior
kite_dir = _flee_direction(ship_pos, target.position)
kite_pos = target.position + kite_dir * opt_dist

# AttackRunBehavior
flee_dir = _flee_direction(ship_pos, target.position)
flee_pos = ship_pos + flee_dir * self.FLEE_DISTANCE
```
**Impact:** Minor duplication, but the `_flee_direction` function is well-factored. The duplication is in the usage pattern.
**Recommendation:** This is acceptable as the distance calculations differ semantically. Low priority.
**Effort:** Simple

#### MINOR: to_dict/from_dict Serialization Pattern
**ID:** DUP-FND-005
**Location:** `game/research/data/research_tracker.py:22-37` (NodeState) AND `game/research/data/research_tracker.py:236-255` (ResearchTracker) AND `game/core/input_actions.py:307-316` (KeyBinding)
**Issue:** Multiple dataclasses implement `to_dict()`/`from_dict()` serialization with similar boilerplate:
```python
def to_dict(self) -> Dict[str, Any]:
    return {
        'field1': self.field1,
        'field2': self.field2,
        ...
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ClassName':
    return cls(
        field1=data.get('field1', default1),
        field2=data.get('field2', default2),
        ...
    )
```
**Impact:** Low - this is a common Python pattern and the fields differ per class
**Recommendation:** Consider using `dataclasses.asdict()` for simple cases, or a serialization library like `dacite` or `cattrs` for complex nested structures. However, manual control is often preferred for explicit default handling.
**Effort:** Simple

#### MINOR: Identical Depth/Layout Calculation Patterns
**ID:** DUP-FND-006
**Location:** `game/research/data/tech_tree.py:110-145` (calculate_depth) AND `game/research/ui/research_scene.py:164-178` (_calculate_layout)
**Issue:** The tech tree has depth calculation in two places:
1. `TechTree.calculate_depth()` - recursive depth calculation with caching
2. `ResearchTreeScene._calculate_layout()` - uses `get_max_depth()` and `get_nodes_at_depth()`

The layout calculation properly delegates to TechTree methods, so this is not true duplication. However, the position calculation logic in `_calculate_layout()` could be moved to TechTree for better encapsulation.
**Impact:** Low - the current split is reasonable (TechTree handles graph logic, Scene handles visual layout)
**Recommendation:** Consider moving layout constants (COLUMN_SPACING, ROW_SPACING) to a shared configuration if they need to be consistent across different views.
**Effort:** Simple

#### MINOR: Navigation Angle Calculation Pattern
**ID:** DUP-FND-007
**Location:** `game/ai/controller.py:434-450` (navigate_to) AND `game/ai/behaviors.py:300` (FormationBehavior)
**Issue:** Angle difference calculation and rotation direction logic appears in multiple places:
```python
# AIController.navigate_to
ang_diff = angle_diff(current_angle, target_angle)
if abs(ang_diff) > AIConfig.NAVIGATION_ROTATION_DEADBAND:
    direction = 1 if ang_diff > 0 else -1
    self.ship.rotate(direction)

# FormationBehavior
angle_diff = calc_angle_diff(ship.get_rotation(), master.angle)
if abs(angle_diff) < turn_speed_per_tick * self.TURN_PREDICT_FACTOR:
    ship.set_rotation(master.angle)
else:
    direction = 1 if angle_diff > 0 else -1
    ship.rotate(direction)
```
**Impact:** Low - the logic is similar but contexts differ (navigation vs formation matching)
**Recommendation:** The shared `angle_diff` function from `game.core.math` is already used. The rotation command pattern (`direction = 1 if angle_diff > 0 else -1; ship.rotate(direction)`) could be extracted to a helper, but the benefit is minimal.
**Effort:** Simple

#### INFO: SingletonMeta Usage is Consistent and Well-Factored
**ID:** DUP-FND-008
**Location:** `game/core/singleton.py` used by 8+ classes
**Issue:** The singleton pattern is centralized in `SingletonMeta` and used consistently across:
- `RegistryManager`
- `Logger`
- `Profiler`
- `StrategyManager`
- `StrategyMetadataService`
- `ShipThemeManager` (UI layer)
- `AssetManager` (assets layer)
- `ScreenshotManager` (UI layer)

This is a positive finding - the singleton boilerplate that existed in ~7 classes (as mentioned in the module docstring) has been consolidated.
**Impact:** None - this is good architecture
**Recommendation:** No action needed. The centralized SingletonMeta is working well.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-FND-002 (MAJOR): JSON Loading Pattern** - Extract a standard DataLoader utility to consolidate path resolution, JSON loading with fallbacks, and key extraction. This affects strategy, resources, and metadata loading.

2. **DUP-FND-003 (MAJOR): get_position/get_rotation Pattern** - The defensive accessor pattern in combat_utils could be generalized into a reusable helper function. This would reduce ~60 lines to ~30 and ensure consistent behavior.

3. **DUP-FND-001 (MAJOR): Singleton clear() Methods** - Document or standardize the `clear()` pattern across singletons for test isolation. Consider a `Clearable` protocol.

4. **DUP-FND-005 (MINOR): to_dict/from_dict** - Low priority but could benefit from a standard serialization approach if more dataclasses need serialization.

5. **DUP-FND-004 (MINOR): Direction Calculations** - Already well-factored with `_flee_direction()`. No immediate action needed.

---

## Analysis Notes

### Well-Factored Areas (No Issues Found)

1. **game/core/math.py** - The Vector2 class is comprehensive and centralized. No duplication found.

2. **game/core/json_utils.py** - Provides clean `load_json()`, `load_json_required()`, `save_json()` functions that are used throughout the codebase.

3. **game/core/validation.py** - The ValidationResult class is well-consolidated (PROJ-21 explicitly mentions consolidating from 5 duplicate implementations).

4. **game/core/hex_math.py** - HexCoord and related functions are centralized and comprehensive.

5. **game/engine/spatial.py** - Simple, focused SpatialGrid implementation with no duplication.

6. **game/engine/physics.py** - Clean PhysicsBody base class with no duplication.

### Files With No Duplication Concerns

The following files were scanned and found to have no significant duplication:
- game/core/__init__.py (exports only)
- game/core/constants.py (enum definitions)
- game/core/error_codes.py (enum definitions)
- game/core/exceptions.py (class hierarchy)
- game/core/paths.py (path constants)
- game/core/protocols.py (protocol definitions)
- game/core/input_actions.py (enum + dataclass)
- game/engine/__init__.py (exports only)
- game/engine/collision.py (stateless algorithms)
- game/research/* (well-structured research system)
- game/ai/target_evaluator.py (rule evaluation)
- game/ai/ai_factory.py (factory pattern)
- game/ai/interfaces/* (interface definitions)
