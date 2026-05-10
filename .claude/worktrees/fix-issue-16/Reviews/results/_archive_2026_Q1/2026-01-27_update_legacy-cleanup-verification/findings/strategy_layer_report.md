# Strategy Layer Scout Report

## Summary
- Files Reviewed: 44
- Issues Found: 10
- Critical: 0, Major: 3, Minor: 7, Info: 0

---

## Findings

### MAJOR: Incomplete Implementation - StrategySessionFacade stub methods
**ID:** NEW-STRAT-001
**Location:** `game/strategy/facade/strategy_session_facade.py:88, 99`
**Issue:** get_fleet() and get_fleets_at_hex() raise NotImplementedError despite being public API. The facade is marked for CQRS pattern but only handle_command() and process_turn() are implemented.
**Impact:** API contract violated; facade appears complete but isn't; breaks architectural expectations.
**Recommendation:** Either implement the query methods or mark as internal/future and update documentation.
**Effort:** Medium

---

### MAJOR: High Complexity - calculate_intercept_point function
**ID:** NEW-STRAT-002
**Location:** `game/strategy/data/pathfinding.py:229-370`
**Issue:** Single function spanning 141 lines with deep nesting (6+ levels), excessive debug logging (~20 log statements), and complex algorithm with 5 early-exit conditions.
**Impact:** Hard to test, maintain, and debug; high cyclomatic complexity makes security audit difficult.
**Recommendation:** Extract logging to helper; split into smaller functions (calculate_base_intercept, apply_corrections, validate_result); document algorithm clearly.
**Effort:** Medium

---

### MAJOR: Incomplete Facade API
**ID:** NEW-STRAT-003
**Location:** `game/strategy/facade/strategy_session_facade.py:1-100`
**Issue:** Facade marked for CQRS pattern but only handle_command() and process_turn() are implemented; many query methods are stubbed with NotImplementedError.
**Impact:** Incomplete facade breaks architectural contract; callers cannot use expected API.
**Recommendation:** Complete implementation or clearly document scope as "Command-only facade".
**Effort:** Complex

---

### MINOR: Unused Method - TurnEngine._apply_battle_results
**ID:** NEW-STRAT-004
**Location:** `game/strategy/engine/turn_engine.py:433-467`
**Issue:** Method is defined (35 lines) but never called anywhere in the codebase. All battle result application uses _resolve_combat_simulated instead.
**Impact:** Dead code adds maintenance burden; confuses developers about intended flow.
**Recommendation:** Remove unused method or document why it exists for future use.
**Effort:** Simple

---

### MINOR: Dead Code - SaveGameService._migrate_temp_designs
**ID:** NEW-STRAT-005
**Location:** `game/strategy/systems/save_game_service.py:114-146`
**Issue:** Function defined (33 lines) but call is commented out at line 77 with a BUG-29 FIX note. The migration logic is orphaned.
**Impact:** Orphaned code suggests incomplete migration; unclear if designs are being migrated properly.
**Recommendation:** Document why disabled and add removal timeline, or remove entirely if no longer needed.
**Effort:** Simple

---

### MINOR: Missing Type Hints - pathfinding module
**ID:** NEW-STRAT-006
**Location:** `game/strategy/data/pathfinding.py:6, 13, 87, 105`
**Issue:** Functions find_path_deep_space, find_path_interstellar, get_system_at_hex, find_nearest_system lack type hints on parameters and return values.
**Impact:** Type checking cannot validate; IDE support degraded; harder to understand function contracts.
**Recommendation:** Add comprehensive type hints with return types for all public functions.
**Effort:** Simple

---

### MINOR: Tight Coupling - Movement/OrderProcessing Dependency
**ID:** NEW-STRAT-007
**Location:** `game/strategy/engine/fleet_movement_engine.py:79`
**Issue:** FleetMovementEngine directly imports FleetOrderProcessor concepts but there's no explicit dependency injection - just implicit behavior coupling.
**Impact:** Violates clean architecture; hard to test in isolation; tight coupling makes refactoring difficult.
**Recommendation:** Formalize dependencies via constructor injection or separate concerns more clearly.
**Effort:** Medium

---

### MINOR: Implicit Coupling - ShipInstance.create() serial handling
**ID:** NEW-STRAT-008
**Location:** `game/strategy/data/ship_instance.py:64-98`
**Issue:** create() method accepts optional 'empire' parameter but silently uses get_next_serial only when empire is provided. No error or warning if serial ends up None.
**Impact:** Silent failures possible; serial tracking may be incomplete for ships created without empire context.
**Recommendation:** Either require empire parameter or make serial requirement explicit with validation.
**Effort:** Simple

---

### MINOR: Redundant Helper Methods - GameSession
**ID:** NEW-STRAT-009
**Location:** `game/strategy/engine/game_session.py:472-481`
**Issue:** _get_fleet_by_id and _get_planet_by_id are simple wrappers (2-3 lines each) with no real logic beyond iteration.
**Impact:** Unnecessary indirection; duplication of simple loops; maintenance overhead.
**Recommendation:** Inline these methods or move to Galaxy/Empire helper classes for better organization.
**Effort:** Simple

---

### MINOR: Potential Circular Import Risk
**ID:** NEW-STRAT-010
**Location:** `game/strategy/engine/turn_engine.py:80-81`
**Issue:** SimulationBattleResolver is imported at runtime inside __init__ rather than at module level. This defers import errors until usage.
**Impact:** Harder to catch import issues during development; may hide circular dependencies.
**Recommendation:** Move import to top-level with proper circular import resolution, or document why runtime import is necessary.
**Effort:** Simple

---

## Files Reviewed

1. game/strategy/__init__.py
2. game/strategy/adapters/__init__.py
3. game/strategy/adapters/battle_resolver.py
4. game/strategy/adapters/simulation_battle_resolver.py
5. game/strategy/data/__init__.py
6. game/strategy/data/design_metadata.py
7. game/strategy/data/empire.py
8. game/strategy/data/fleet.py
9. game/strategy/data/fleet_order.py
10. game/strategy/data/galaxy.py
11. game/strategy/data/hex_math.py
12. game/strategy/data/pathfinding.py
13. game/strategy/data/planet.py
14. game/strategy/data/ship_instance.py
15. game/strategy/data/star_system.py
16. game/strategy/data/turn_tracker.py
17. game/strategy/engine/__init__.py
18. game/strategy/engine/fleet_movement_engine.py
19. game/strategy/engine/fleet_order_processor.py
20. game/strategy/engine/game_session.py
21. game/strategy/engine/production_engine.py
22. game/strategy/engine/turn_engine.py
23. game/strategy/facade/__init__.py
24. game/strategy/facade/strategy_session_facade.py
25. game/strategy/interfaces/__init__.py
26. game/strategy/interfaces/battle_resolver.py
27. game/strategy/services/__init__.py
28. game/strategy/services/fleet_stats_service.py
29. game/strategy/services/ship_stats_service.py
30. game/strategy/systems/__init__.py
31. game/strategy/systems/campaign_manager.py
32. game/strategy/systems/fleet_formation_manager.py
33. game/strategy/systems/pathfinding_service.py
34. game/strategy/systems/production_queue.py
35. game/strategy/systems/save_game_service.py
36. game/strategy/systems/ship_production.py
37. game/strategy/systems/starbase_manager.py
38. game/strategy/systems/stellar_cartography.py
39. game/strategy/systems/tech_tree_manager.py
40. game/strategy/systems/tech_tree_registry.py
41. game/strategy/systems/treasury.py
42. game/strategy/systems/war_status.py
43. game/strategy/ui/__init__.py
44. game/strategy/ui/combat_preview.py

---

## Key Observations

1. **Incomplete Facade Pattern** (NEW-STRAT-001, NEW-STRAT-003): The StrategySessionFacade is partially implemented, with several query methods throwing NotImplementedError. This breaks the architectural contract and may confuse developers.

2. **Complex Pathfinding** (NEW-STRAT-002): The calculate_intercept_point function is a maintenance concern at 141 lines with deep nesting.

3. **Dead/Orphaned Code** (NEW-STRAT-004, NEW-STRAT-005): Two methods exist but are never called, suggesting incomplete refactoring.

4. **Coupling Concerns** (NEW-STRAT-007, NEW-STRAT-010): Some engine classes have tight implicit coupling that violates clean architecture principles.

5. **Type Safety Gaps** (NEW-STRAT-006): The pathfinding module lacks type hints on key functions, reducing IDE support and type safety.
