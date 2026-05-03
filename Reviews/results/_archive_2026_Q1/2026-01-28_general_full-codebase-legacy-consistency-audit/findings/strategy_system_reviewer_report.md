# Strategy System Reviewer Report

## Summary
- **Total issues found:** 14
- **Critical:** 2, **Major:** 6, **Minor:** 4, **Info:** 2

---

## Critical Issues

### STR-001: Incomplete PROJ-35 Migration - Dual Movement Logic
**ID:** STR-001
**Location:** `game/strategy/engine/fleet_movement.py:1-331` AND `game/strategy/services/fleet_navigation_service.py:1-468`
**Issue:** PROJ-35 aimed to unify fleet movement logic, but the deprecated `FleetMovementSimulator` class (331 LOC) still exists in `/engine/` with deprecation warnings while the new `FleetNavigationService` exists in `/services/`. Both implementations provide similar path projection and calculation logic.
**Impact:**
- UI and turn engine may use different movement calculations
- Maintenance burden (code duplication across two modules)
- Risk of behavior divergence in path projection vs. execution
**Recommendation:**
1. Audit all `FleetMovementSimulator` usage to ensure all call sites migrated to `FleetNavigationService`
2. Remove deprecated `FleetMovementSimulator` entirely
3. Add integration test verifying UI projection matches turn execution
**Effort:** Medium

---

### STR-002: Type-Checking and String-Based Ship Identification
**ID:** STR-002
**Location:** `game/strategy/data/fleet.py:433-459`, `game/strategy/engine/fleet_movement.py:63-82`
**Issue:** Fleet still supports legacy string ship references mixed with modern `ShipInstance` objects. The `to_battle_ships()` method explicitly documents "Only works with ShipInstance objects - legacy strings cannot be converted." Multiple `isinstance(target, dict)` type checks scattered through pathfinding and serialization code.
**Impact:**
- Type checking spreads through codebase (fragile)
- Cannot reliably convert old fleets to battle
- Violates single responsibility (code checks types instead of polymorphism)
**Recommendation:**
1. Audit codebase for remaining string ship references
2. Implement complete migration of old save files to `ShipInstance` format
3. Remove all `isinstance(x, dict)` type checks for ship data
**Effort:** Complex

---

## Major Issues

### STR-003: Service Naming Inconsistency and Ambiguity
**ID:** STR-003
**Location:** `game/strategy/services/` (fleet_navigation_service.py, fleet_mobility_service.py, ship_stats_service.py)
**Issue:** Service names mix multiple patterns without clear distinction:
- `FleetNavigationService` - handles pathfinding AND navigation state
- `FleetMobilityService` - handles speed calculation only (not mobility)
- `ShipStatsService` - calculates all ship statistics (very broad)
**Impact:** New developers confused about service boundaries
**Recommendation:**
1. Rename `FleetMobilityService` → `FleetSpeedCalculator`
2. Rename `ShipStatsService` → `ShipStatsCalculator`
3. Create a services architecture document
**Effort:** Simple

---

### STR-004: Tight Coupling Between Strategy and Simulation Layers
**ID:** STR-004
**Location:** `game/strategy/adapters/simulation_adapter.py:24-142`, `game/strategy/data/fleet.py:425-508`
**Issue:** Direct imports of simulation layer in strategy:
- `fleet.to_battle_ships()` creates simulation `Ship` objects directly
- `SimulationBattleResolver` imports `BattleController`, `BattleService` directly
- `ShipInstance.to_ship()` directly calls `ShipSerializer.from_dict()`
**Impact:** Cannot swap simulation implementations; circular dependency risk
**Recommendation:**
1. Create strategy-layer `IBattleEntity` interface
2. Move `to_battle_ships()` logic behind an adapter
3. Use dependency injection to provide the builder
**Effort:** Complex

---

### STR-005: Backward Compatibility Code Scattered Everywhere
**ID:** STR-005
**Location:** `game/strategy/services/fleet_navigation_service.py:84-91`, `game/strategy/data/pathfinding.py:275-283`, `game/strategy/data/fleet.py:604-616`
**Issue:** Multiple backward compatibility patterns without central location:
- `PathSegment.to_dict()` includes legacy `'hex'` field alongside `'end'`
- `_ChaserProxy` class created just to handle NavigationState vs Fleet differences
- Fleet order deserialization handles 3+ different target formats
**Impact:** Hard to identify what's legacy vs. new; multiple code paths need maintenance
**Recommendation:**
1. Create `LegacyCompatibilityLayer` module
2. Move all backward-compat code into it (explicit, versioned)
3. Mark each compat handler with target version
**Effort:** Medium

---

### STR-006: Intercept Calculation Uses Type-Checked Union Without Abstraction
**ID:** STR-006
**Location:** `game/strategy/data/pathfinding.py:286-306`, `calculate_intercept_point:367-434`
**Issue:** `calculate_intercept_point()` accepts `Union['Fleet', 'NavigationState']` and uses `isinstance()` check to distinguish them. Creates `_ChaserProxy` object as workaround.
**Impact:** Violates duck typing; fragile to new types; makes code harder to test
**Recommendation:**
1. Create `IChaserInfo` protocol/interface
2. Add `from_fleet()` and `from_navigation_state()` factory methods
3. Remove `_ChaserProxy` and isinstance check
**Effort:** Simple

---

### STR-007: Resource Consumption Logic Assumes Component Format
**ID:** STR-007
**Location:** `game/strategy/engine/resource_management_engine.py:120-142`, `game/strategy/services/ship_stats_service.py:180-195`
**Issue:** Multiple places check `isinstance(components, dict)` and handle dual formats. Suggests two different component storage formats in layer data.
**Impact:** Resource consumption may not work for all component formats; bug risk if format isn't handled correctly
**Recommendation:**
1. Normalize to single component format throughout
2. Create `ComponentIterator` utility that handles format automatically
3. Add schema validation on design data load
**Effort:** Medium

---

## Minor Issues

### STR-008: Magic Numbers Throughout Fleet Speed and Resource Calculations
**ID:** STR-008
**Location:** `game/strategy/services/fleet_mobility_service.py:30-32`, `game/strategy/data/fleet.py:469-478`
**Issue:** Strategic constants scattered:
- K_STRATEGIC = 25 (movement conversion factor) - in one file only
- MAX_HEXES_PER_TURN = 10 - no clear derivation
- Formation positions: base_x = 20000, base_y = 50000, spacing = 2000
**Recommendation:** Create `game/strategy/config/STRATEGY_CONSTANTS.py`
**Effort:** Simple

---

### STR-009: Pathfinding Implementation Has Incomplete Comments
**ID:** STR-009
**Location:** `game/strategy/data/pathfinding.py:53-62`
**Issue:** Code has unresolved TODO-style comments suggesting exploratory implementation
**Recommendation:** Finalize design documentation; remove exploratory comments
**Effort:** Simple

---

### STR-010: AIController Mixing UI and Combat Logic
**ID:** STR-010
**Location:** `game/ai/controller.py:198-276`
**Issue:** `AIController.update()` mixes formation management, behavior selection, and weapon firing
**Recommendation:** Extract formation handling to `FormationManager` class; move behavior selection to `BehaviorSelector` class
**Effort:** Medium

---

### STR-011: StrategyManager Singleton Pattern
**ID:** STR-011
**Location:** `game/ai/strategy_manager.py:13-149`
**Issue:** Uses singleton pattern with thread-safe double-checked locking. Hard to test.
**Recommendation:** Document why singleton is necessary; consider providing factory method as alternative
**Effort:** Info

---

## Info Issues

### STR-012: Ship Stats Service Has Three Calling Patterns
**ID:** STR-012
**Location:** `game/strategy/services/ship_stats_service.py:86-149`
**Issue:** `calculate_stats()` method supports three calling patterns (instance, static, hybrid). This is a transitional pattern (PROJ-38).
**Recommendation:** Document which pattern should be used going forward; deprecate static pattern
**Effort:** Info

---

## Top 5 Priority Issues

1. **Complete PROJ-35 Migration (STR-001)** - Critical - Unifies movement logic, eliminates code duplication
2. **Remove Type-Checking for Ships (STR-002)** - Critical - Ensures all fleets work with battles
3. **Fix Service Naming (STR-003)** - Major - Clarifies architecture, improves discoverability
4. **Abstract Simulation Layer Coupling (STR-004)** - Major - Enables different battle implementations
5. **Centralize Backward Compatibility (STR-005)** - Major - Reduces codebase complexity
