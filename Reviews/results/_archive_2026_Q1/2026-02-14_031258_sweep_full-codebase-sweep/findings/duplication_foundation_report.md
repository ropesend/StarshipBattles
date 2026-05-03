# Duplication & Fragmentation Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 6
- **Critical:** 0 | **Major:** 2 | **Minor:** 3 | **Info:** 1

## Findings

#### MAJOR: Strategy Data Loading Duplication
**ID:** DUP-FND-001
**Location:** `game/core/strategy_metadata.py:124-146` AND `game/ai/strategy_manager.py:83-105`
**Issue:** Both `StrategyMetadataService.load_data()` and `StrategyManager.load_data()` implement nearly identical JSON loading patterns for combat_strategies.json. Both:
- Take similar parameters (base_path, strategy_file)
- Load from the same JSON file
- Extract `strategies` from the data
- Store the result in an instance dict
- Log the count of loaded strategies

The only difference is that StrategyManager also loads targeting and movement policies. StrategyMetadataService.load_data() exists as an alternative entry point that bypasses StrategyManager.

**Impact:** Maintenance risk - if the strategy file format changes, both locations need updating. Potential for divergence in loading logic. Cognitive overhead when understanding data flow.
**Recommendation:** Remove `StrategyMetadataService.load_data()` entirely. It's only called by WorkshopDataLoader. Instead, have WorkshopDataLoader call `StrategyManager.instance().ensure_loaded()` which already populates StrategyMetadataService via `set_strategies()`. This is the intended data flow (StrategyManager is the authoritative loader).
**Effort:** Simple

#### MAJOR: Singleton Clear Pattern Repetition
**ID:** DUP-FND-002
**Location:** `game/core/strategy_metadata.py:54-60`, `game/ai/strategy_manager.py:53-64`, `game/core/registry.py:217-237`, `game/core/profiling.py:39-42`
**Issue:** Every singleton using SingletonMeta implements its own `clear()` method with identical boilerplate pattern:
```python
def clear(self) -> None:
    """Reset all data. Used for test isolation."""
    self.field1 = {}  # or initial value
    self.field2 = {}
    # etc.
```

Additionally, StrategyManager.clear() calls `StrategyMetadataService.instance().clear()` creating a cross-service coupling that could be missed if someone adds a new dependent service.

**Impact:** Low bug risk but unnecessary code repetition across ~4 singletons in this shard. The pattern is consistent but violates DRY.
**Recommendation:** Consider adding a `clear_fields()` abstract method or registration pattern to SingletonMeta that allows singletons to declare clearable fields. Alternatively, accept this as acceptable boilerplate since each singleton has unique fields.
**Effort:** Medium (if abstracting), Simple (if accepting as-is)

#### MINOR: StrategyManager and StrategyMetadataService Coordination
**ID:** DUP-FND-003
**Location:** `game/ai/strategy_manager.py:63-64` AND `game/core/strategy_metadata.py`
**Issue:** StrategyManager.clear() explicitly calls `StrategyMetadataService.instance().clear()`, creating tight coupling. The two services maintain overlapping data (strategies dict) with StrategyManager being the source of truth and StrategyMetadataService being a UI-facing cache.

This is intentional design (StrategyManager populates StrategyMetadataService), but the coupling means:
1. StrategyManager must know about StrategyMetadataService
2. Adding new "metadata services" would require updating StrategyManager
3. The strategies dict exists in both places

**Impact:** Minor maintenance burden. The design is documented and works, but the data is technically duplicated across the two services (one in ai layer, one in core layer).
**Recommendation:** This is likely intentional for layer separation (core shouldn't depend on ai). Document this pattern clearly. No code change needed unless the number of such cross-layer caches grows.
**Effort:** N/A (documentation only)

#### MINOR: Position Access Patterns in AI Module
**ID:** DUP-FND-004
**Location:** `game/ai/behaviors.py` (19 occurrences), `game/ai/controller.py` (10 occurrences), `game/ai/combat_utils.py` (4 occurrences)
**Issue:** The AI module uses two patterns for accessing entity position:
1. `entity.get_position()` - via IControllable interface (preferred)
2. `entity.position` - direct attribute access (legacy/raw ships)

The `game/ai/combat_utils.py:get_position()` function attempts to unify this by trying interface method first, then falling back to attribute. However, behaviors.py and controller.py mix both patterns depending on context:
- `self.controller.ship.get_position()` for the controlled ship
- `target.position` for targets (which are raw Ship objects)

**Impact:** Low risk - this is intentional because the adapter wraps only the controlled ship, not targets. Code is harder to read but functionally correct.
**Recommendation:** Document this pattern difference explicitly. Consider having targeting code use `get_position(target)` from combat_utils for consistency, but this is a minor improvement.
**Effort:** Simple

#### MINOR: Serialization Pattern (to_dict/from_dict) Without Base Class
**ID:** DUP-FND-005
**Location:** `game/research/data/research_tracker.py:22-37` (NodeState), `game/research/data/research_tracker.py:236-255` (ResearchTracker), `game/core/input_actions.py:290-316` (KeyBinding), `game/core/hex_math.py:254-277` (HexCoord functions)
**Issue:** Multiple dataclasses and entities implement `to_dict()` and `from_dict()` serialization methods with similar patterns but no shared base class or protocol. Each implementation:
- Returns a dict with specific keys
- Has a `@classmethod from_dict(cls, data)` factory
- Handles defaults via `.get()` with fallback values

**Impact:** Low risk - each serialization is type-specific and the pattern is consistent. However, there's no shared interface (e.g., `ISerializable` protocol) that could enable generic serialization utilities.
**Recommendation:** Consider adding a `ISerializable` protocol in game/core/protocols.py for type hints and potential generic utilities. Not urgent unless serialization complexity grows.
**Effort:** Simple

#### INFO: Well-Consolidated Distance Calculations
**ID:** DUP-FND-006
**Location:** `game/core/math.py:143-149` (Vector2.distance_to, distance_squared_to)
**Issue:** NOT a duplication issue. Distance calculations are properly consolidated in Vector2. All 8 files using distance calculations leverage Vector2.distance_to() rather than reimplementing the formula. The `game/ai/combat_utils.py:safe_distance()` wrapper adds error handling but delegates to Vector2.

**Impact:** Positive - shows good consolidation.
**Recommendation:** None. This is working as intended.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-FND-001 (MAJOR)**: Strategy Data Loading Duplication - Remove StrategyMetadataService.load_data() to eliminate redundant loading path.

2. **DUP-FND-002 (MAJOR)**: Singleton Clear Pattern - Consider documenting as accepted pattern or adding SingletonMeta enhancement (lower priority).

3. **DUP-FND-003 (MINOR)**: StrategyManager/StrategyMetadataService Coordination - Document the cross-layer cache pattern.

4. **DUP-FND-004 (MINOR)**: Position Access Patterns - Minor documentation/consistency improvement opportunity.

5. **DUP-FND-005 (MINOR)**: Serialization Pattern - Consider ISerializable protocol for future extensibility.

---

## Notes

**Patterns Working Well (No Issues Found):**
- SingletonMeta is properly centralized in game/core/singleton.py - no duplicated singleton implementations
- Vector2 math utilities are properly consolidated - no redundant distance/normalize implementations
- JSON loading is properly routed through game/core/json_utils.py
- Error handling follows consistent patterns via game/core/exceptions.py
- All behaviors share the common AIBehavior base class
- TargetEvaluator rule evaluation is properly organized with clear separation of rule types

**Architecture Observations:**
- The StrategyMetadataService exists to decouple UI from AI layer - this is good layer separation even though it creates some data duplication
- The IControllable interface in AI layer successfully decouples AI logic from Ship internals
- The research module is self-contained with clear data/systems/ui separation
- The engine module is minimal and focused (physics, collision, spatial)
