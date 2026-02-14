# Duplication & Fragmentation Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 9
- **Critical:** 0 | **Major:** 3 | **Minor:** 4 | **Info:** 2

## Findings

#### MAJOR: Singleton Clear Pattern Duplication
**ID:** DUP-FND-001
**Location:** `game/core/profiling.py:39-42` AND `game/core/registry.py:217-237` AND `game/core/strategy_metadata.py:54-60` AND `game/ai/strategy_manager.py:53-64`
**Issue:** Four singleton classes implement nearly identical `clear()` methods for test isolation, each with:
- Reset of internal state dictionaries
- Docstrings explaining "Used for test isolation"
- Similar null/empty state restoration logic

Each class has its own version with slightly different field names but identical semantics:
- `Profiler.clear()`: resets `records` list and regenerates `session_id`
- `RegistryManager.clear()`: clears four dictionaries and `_validator`
- `StrategyMetadataService.clear()`: resets `_strategies` dict
- `StrategyManager.clear()`: resets three policy dicts and `_loaded` flag

**Impact:** When adding new singletons, developers may forget to add `clear()` or implement it inconsistently. Test isolation behavior varies.
**Recommendation:** The SingletonMeta metaclass already provides `reset()` for destroying instances. Consider documenting a standard pattern: either use `reset()` exclusively, or add a `Clearable` mixin/protocol that standardizes the `clear()` interface.
**Effort:** Medium

#### MAJOR: Strategy Metadata Dual Service Pattern
**ID:** DUP-FND-002
**Location:** `game/core/strategy_metadata.py:33-147` AND `game/ai/strategy_manager.py:20-134`
**Issue:** Two services manage overlapping strategy data:
1. `StrategyMetadataService` (core layer): Provides strategy names/IDs to UI
2. `StrategyManager` (AI layer): Loads full strategy definitions from JSON

The `StrategyManager.load_data()` method explicitly populates `StrategyMetadataService` on line 103:
```python
StrategyMetadataService.instance().set_strategies(self.strategies)
```

Both services:
- Are singletons with `clear()` methods
- Store strategy dictionaries
- Provide lookup methods (`get_strategy_display_name` vs `get_strategy`)
- Load from the same JSON file (`combat_strategies.json`)

**Impact:** Two singletons must be kept in sync. If one is reset without the other, data inconsistency occurs. The pattern increases cognitive load and maintenance burden.
**Recommendation:** Consider whether StrategyMetadataService is necessary. The core layer could expose a simpler protocol/interface that AI layer implements, rather than duplicating the data storage.
**Effort:** Complex

#### MAJOR: JSON Loading with Fallback Pattern
**ID:** DUP-FND-003
**Location:** `game/core/resources.py:54-98` AND `game/research/data/tech_tree.py:28-93`
**Issue:** Both files implement similar JSON loading with error handling and default fallback:

`resources.py`:
- Path resolution with fallback
- `load_json_required()` call
- Exception handling for FileNotFoundError, JSONDecodeError, PermissionError, TypeError
- Fallback to `_get_default_resources()`
- Logging on errors

`tech_tree.py`:
- Uses `load_json()` with default
- Handles missing/invalid entries gracefully
- Logs load count

While `json_utils.py` provides shared utilities, the pattern of "load JSON with path resolution, handle errors, provide defaults" is implemented independently in each consumer.

**Impact:** Each new JSON loader reinvents error handling. Edge cases may be handled inconsistently.
**Recommendation:** Consider a higher-level `load_json_with_defaults(path, default_factory, resolver)` function in `json_utils.py` that encapsulates path resolution and default fallback.
**Effort:** Simple

#### MINOR: Serialization Method Naming Convention
**ID:** DUP-FND-004
**Location:** `game/core/input_actions.py:307-316` AND `game/research/data/research_tracker.py:22-37`
**Issue:** Both files implement `to_dict()` and `from_dict()` serialization methods with identical signatures:
- `to_dict(self) -> Dict[str, Any]`
- `from_dict(cls, data: Dict[str, Any]) -> Self`

This is a common pattern repeated in 17 files across the codebase. While not problematic in itself, there's no shared protocol/interface defining this contract.

**Impact:** Low - the pattern works, but having a `Serializable` protocol in core would provide type safety and documentation.
**Recommendation:** Add an optional `ISerializable` protocol in `game/core/protocols.py` for documentation purposes. Not a high priority.
**Effort:** Simple

#### MINOR: Distance Calculation Access Patterns
**ID:** DUP-FND-005
**Location:** `game/ai/combat_utils.py:142-164` AND `game/ai/behaviors.py:154-156` AND `game/ai/controller.py:195-203`
**Issue:** Distance calculations between entities appear in multiple places:
- `combat_utils.safe_distance()`: Defensive wrapper with None checks and logging
- `behaviors.py` KiteBehavior: Direct `ship_pos.distance_to(target.position)`
- `controller.py` `_score_and_sort_enemies()`: Direct `ship_pos.distance_to(e_pos)`

The `safe_distance()` utility exists but isn't always used. Direct calls to `distance_to()` appear 17 times across 8 files.

**Impact:** Some code paths may crash on None positions while others handle gracefully.
**Recommendation:** Consistently use `safe_distance()` for all entity distance calculations in AI code. Consider making it the single entry point.
**Effort:** Simple

#### MINOR: Flee Direction Calculation
**ID:** DUP-FND-006
**Location:** `game/ai/behaviors.py:70-84` (helper function) AND `game/ai/behaviors.py:114-116` AND `game/ai/behaviors.py:162-164` AND `game/ai/behaviors.py:226-228`
**Issue:** The `_flee_direction()` helper function calculates direction away from a position. It's called in three different behaviors:
- `FleeBehavior.update()` line 114
- `KiteBehavior.update()` line 162
- `AttackRunBehavior.update()` line 226

The function itself is well-factored, but the "kite direction" calculation (line 162) and "flee direction" are semantically the same operation with different variable names.

**Impact:** Low - the current code is acceptable.
**Recommendation:** No action needed. The helper function is already shared appropriately.
**Effort:** N/A

#### MINOR: Camera Factory Pattern
**ID:** DUP-FND-007
**Location:** `game/research/ui/research_scene.py:31-46`
**Issue:** The `_create_default_camera()` factory function is defined locally in research_scene.py to avoid import-time layer violations. This pattern may need to be repeated if other scenes require similar late-import patterns.

**Impact:** Low currently (only one scene uses this), but could lead to duplication if more scenes need camera injection.
**Recommendation:** If multiple scenes need camera injection, consider moving the factory to a shared location or using a camera factory provider in the composition root.
**Effort:** Simple

#### INFO: Singleton Pattern Consistency
**ID:** DUP-FND-008
**Location:** Multiple files using `SingletonMeta`
**Issue:** The `SingletonMeta` metaclass is properly shared across 10 singleton classes. This is a positive observation showing good pattern reuse. All singletons correctly use:
- `metaclass=SingletonMeta`
- `.instance()` for access
- `.reset()` for test teardown (via metaclass)

**Impact:** None - this is working well.
**Recommendation:** Continue using this pattern. Document any new singletons should follow this approach.
**Effort:** N/A

#### INFO: Combat Utils Consolidation Success
**ID:** DUP-FND-009
**Location:** `game/ai/combat_utils.py`
**Issue:** According to the module docstring, PROJ-108 Phase 3 consolidated helper functions from TargetEvaluator into combat_utils.py. The public API exports:
- `is_vector2_like`, `get_entity_id`, `get_position`, `get_rotation`
- `get_all_components`, `safe_distance`, `get_hp_percent`, `is_in_pdc_arc`

This consolidation reduced duplication and provides a clean interface for position/rotation/distance access.

**Impact:** Positive - shows successful prior deduplication effort.
**Recommendation:** Reference this as an example when consolidating other duplicated utility functions.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-FND-002 (MAJOR)**: Strategy Metadata Dual Service Pattern - Two services storing overlapping data creates synchronization burden and potential inconsistency. Consider architectural simplification.

2. **DUP-FND-001 (MAJOR)**: Singleton Clear Pattern Duplication - Four implementations of test isolation `clear()` methods. Standardize via mixin or documented pattern.

3. **DUP-FND-003 (MAJOR)**: JSON Loading with Fallback Pattern - Path resolution and error handling repeated across JSON consumers. Create higher-level utility.

4. **DUP-FND-005 (MINOR)**: Distance Calculation Access Patterns - Inconsistent use of `safe_distance()` vs direct calls. Standardize on the defensive wrapper.

5. **DUP-FND-004 (MINOR)**: Serialization Method Naming Convention - Consider adding `ISerializable` protocol for type safety across 17+ serializable classes.
