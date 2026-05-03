# Strategy Module Specialist Report

## Summary
- **Total issues found:** 18
- **Critical:** 2, **Major:** 8, **Minor:** 5, **Info:** 3

---

## Critical Findings

### CRITICAL: Incomplete Fleet Order Serialization on Load
**ID:** STRAT-001
**Location:** `game/strategy/data/fleet.py:670`
**Issue:** Fleet orders are not restored from save games. The `from_dict()` method explicitly skips order restoration with a TODO comment.
**Impact:** **Critical data loss on save/load.** Players lose all fleet movement and action orders when loading a game.
**Recommendation:** Implement two-phase order restoration: (1) Deserialize order data to temporary objects, (2) Resolve fleet references after all fleets loaded.
**Effort:** Medium

### CRITICAL: UI Layer Coupling in Core Strategy Logic
**ID:** STRAT-002
**Location:** `game/strategy/data/fleet.py:140, 158`
**Issue:** Fleet class directly imports `has_warp_capability` from `game.ui.screens.fleet_report_filters`.
**Impact:** **Impossible to use strategy layer without UI.** Strategy engine cannot run headless. UI changes break strategy layer.
**Recommendation:** Move `has_warp_capability` logic to `game.strategy.services.ship_stats_service.ShipStatsService`.
**Effort:** Medium

---

## Major Findings

### MAJOR: Turn Engine Monolithic Design (737 lines)
**ID:** STRAT-003
**Location:** `game/strategy/engine/turn_engine.py`
**Issue:** TurnEngine is a 737-line monolith handling movement, path management, combat resolution, resource consumption, production, and colonization.
**Impact:** **Maintainability blocker.** Adding new order types requires modifying turn engine directly. Changes risk breaking multiple subsystems.
**Recommendation:** Extract subsystems: `FleetMovementEngine`, `CombatResolutionEngine`, `ProductionEngine`. Use dependency injection.
**Effort:** Complex

### MAJOR: Cross-Layer Coupling to Simulation Battle System
**ID:** STRAT-004
**Location:** `game/strategy/engine/turn_engine.py:572-618`
**Issue:** TurnEngine directly imports and instantiates `BattleController` from simulation layer.
**Impact:** **Cannot test strategy layer without simulation layer.** Changing battle mechanics requires careful strategy layer updates.
**Recommendation:** Use battle resolution interface/service pattern. Have TurnEngine call abstract `IBattleResolver`.
**Effort:** Medium

### MAJOR: Indentation Code Style Issues
**ID:** STRAT-005
**Location:** `game/strategy/engine/turn_engine.py:89`, `game/strategy/engine/game_session.py:191, 213, 216, 235, 243`
**Issue:** Multiple methods have inconsistent indentation (extra leading space).
**Impact:** **Code quality and maintainability.** Developers may misinterpret code scope.
**Recommendation:** Standardize indentation. Use linter with strict rules in CI/CD.
**Effort:** Simple

### MAJOR: Order State Management Scattered Across Multiple Methods
**ID:** STRAT-006
**Location:** `game/strategy/engine/turn_engine.py` (scattered)
**Issue:** Fleet order and path management fragmented: `pop_order()` called in 5 different places, `path` manipulated in 6 methods.
**Impact:** **Extensibility blocker.** Adding new order types requires modifying multiple locations.
**Recommendation:** Centralize order lifecycle in dedicated `FleetOrderManager` class.
**Effort:** Medium

### MAJOR: No Validation Before Applying Game State Changes
**ID:** STRAT-007
**Location:** `game/strategy/engine/turn_engine.py:701-705, 315`
**Issue:** Critical state changes happen without re-validating that conditions still hold.
**Impact:** **Data corruption risk.** Race conditions where planet becomes owned between validation and application.
**Recommendation:** Apply atomic transactions with immediate re-validation.
**Effort:** Medium

### MAJOR: Simulation Layer Integration Creates Version Coupling
**ID:** STRAT-008
**Location:** `game/strategy/engine/turn_engine.py:593-594`
**Issue:** TurnEngine directly calls `to_battle_ships()` and handles `BattleResults`.
**Impact:** **Version coupling between layers.** Simulation layer changes require strategy layer updates.
**Recommendation:** Define stable interfaces (DTOs) at the boundary between layers.
**Effort:** Medium

### MAJOR: Production System Dual Format Support
**ID:** STRAT-009
**Location:** `game/strategy/engine/turn_engine.py:109-116`
**Issue:** Construction queue items support both old list format and new dict format.
**Impact:** **Code complexity and bug risk.** Every place that touches construction queue must handle both formats.
**Recommendation:** Enforce single format. Provide migration utility. Remove old format support.
**Effort:** Simple

---

## Minor Findings

### Minor: Empire Fleet ID Generator Not Reset on Load
**ID:** STRAT-010
**Location:** `game/strategy/data/empire.py:124`
**Issue:** When loading empire from save, `_next_fleet_id` restored without validation.
**Impact:** Potential fleet ID collisions in edge cases.
**Recommendation:** Validate during load that `_next_fleet_id` is greater than all existing fleet IDs.
**Effort:** Simple

### Minor: No Error Handling for Missing Design Data During Production
**ID:** STRAT-012
**Location:** `game/strategy/engine/turn_engine.py:206-210`
**Issue:** When spawning ship, if design data cannot be loaded, function returns silently.
**Impact:** **Silent failures.** Players won't know why a ship didn't spawn.
**Recommendation:** Track failed productions. Notify player. Auto-refund production time.
**Effort:** Simple

### Minor: Warp Capability Check Uses UI Filter Function
**ID:** STRAT-013
**Location:** `game/strategy/data/fleet.py:140, 147`
**Issue:** Warp capability check is duplicated logic from UI filters.
**Impact:** **Maintenance burden.** Logic not DRY.
**Recommendation:** Create dedicated `WarpCapabilityChecker` in services layer.
**Effort:** Simple

### Minor: Default Formation Positions Hardcoded
**ID:** STRAT-014
**Location:** `game/strategy/data/fleet.py:519-537`
**Issue:** Formation positions have hardcoded coordinates (base_x = 20000/80000, spacing = 2000).
**Impact:** **Inflexibility.** Cannot customize formations without code changes.
**Recommendation:** Move formation strategy to pluggable service or configuration file.
**Effort:** Simple

---

## Info Findings

### Info: Battle Seed Counter Not Persisted
**ID:** STRAT-015
**Location:** `game/strategy/engine/turn_engine.py:20-26`
**Issue:** `_battle_seed_counter` is not serialized/loaded.
**Impact:** Battles non-deterministic across save boundaries.
**Recommendation:** Persist in GameSession serialization.
**Effort:** Simple

### Info: Pathfinding Module Incomplete
**ID:** STRAT-016
**Location:** `game/strategy/data/pathfinding.py:1-80`
**Issue:** Pathfinding file appears incomplete. `find_path_interstellar` has commented-out logic.
**Impact:** Pathfinding may not work correctly for interstellar travel.
**Recommendation:** Complete and test the pathfinding implementation.
**Effort:** Medium

### Info: Game Session Command Routing Pattern Inconsistent
**ID:** STRAT-017
**Location:** `game/strategy/engine/game_session.py:159-180`
**Issue:** Command dispatch uses string matching on class name rather than type checking.
**Impact:** **Extensibility issue.** Adding new commands requires modifying dispatcher.
**Recommendation:** Use `isinstance()` checks or command registry pattern.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **STRAT-001**: Fleet orders lost on save/load - **Immediate fix required**
2. **STRAT-002**: UI layer coupling in Fleet class - **Blocks headless strategy engine**
3. **STRAT-003**: Turn engine monolithic design - **Extensibility blocker**
4. **STRAT-004**: Battle system hard coupling - **Prevents independent testing**
5. **STRAT-006**: Scattered order state management - **Increases bug risk**

---

## Extensibility Assessment

### Rating: DIFFICULT (4/10)

**Barriers:**

1. **Order System:** Adding new order types requires modifying 5+ files
2. **Resource Types:** Adding new strategic resource requires 4+ files
3. **Empire Features:** Adding new empire mechanics requires 3+ files
4. **Combat Types:** Adding alternative combat systems has high architectural friction

**Why It's Difficult:**
- Monolithic TurnEngine - All logic in one 737-line class
- Scattered State Management - Order/path handling fragmented
- Hard Dependencies - Can't modify one subsystem without understanding interconnections
- Cross-Layer Coupling - Changes in simulation affect strategy

**Recommendations to Improve:**
1. Break TurnEngine into smaller services
2. Use abstract interfaces for pluggable systems
3. Implement proper state management patterns
4. Create registries for order types, resource types, combat resolvers
5. Move business logic out of data classes into services
