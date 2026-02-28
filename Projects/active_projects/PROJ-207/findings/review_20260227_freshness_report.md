# PROJ-207 Task Freshness Report

**Date:** 2026-02-27
**Analyst:** Claude Opus 4.6 (Task Freshness Analyst)
**Scope:** All 15 tasks across 5 phases

---

## Executive Summary

**All 15 tasks are STILL_VALID.** No tasks have been pre-completed, rendered obsolete, or had their prerequisites changed. The codebase state matches all task descriptions accurately.

---

## Phase 1: Save/Load Data Integrity

### Task 1.1: ODM-001 - Fix _fleet_ref/_planet_ref Resolution After Deserialization
**Status:** STILL_VALID
**Evidence:**
- `Fleet.from_dict()` in `game/strategy/data/fleet.py` lines 454-462 stores `{'_fleet_ref': target_data['id']}` and `{'_planet_ref': target_data['id']}` marker dicts.
- Grep for `resolve_order_references` across the entire `game/` directory returns zero results.
- No code anywhere resolves these markers back to live `Fleet` or `Planet` objects after loading.
- The `_fleet_ref` and `_planet_ref` markers are only set (lines 456, 462) and never consumed.

### Task 1.2: ODM-003 - Fix Planet Target Serialization Round-Trip
**Status:** STILL_VALID
**Evidence:**
- `FleetOrder.to_dict()` at line 97-99 serializes Planet targets via `self.target.to_dict()`, producing a full planet dict with keys like `id`, `name`, `location`, `mass`, etc.
- `FleetOrder.from_dict()` (lines 448-471) only recognizes: `{'q', 'r'}` (HexCoord), `{'type': 'fleet_ref'}`, `{'type': 'transfer'}`, `{'type': 'planet_ref'}`, `{'type': 'ship_id_list'}`, `{'type': 'warp_params'}`, `{'type': 'raw'}`.
- A full `Planet.to_dict()` dict has no top-level `q`/`r` keys and no `type` key, so it falls through all conditionals. The target ends up as `None`.
- COLONIZE orders with specific planet targets lose their target on save/load round-trip.

---

## Phase 2: Superweapon Validation & Execution

### Task 2.1: VC-001 - Pass component_registry to Superweapon Validators
**Status:** STILL_VALID
**Evidence:**
- All 6 direct command handlers in `superweapon_command_handlers.py` call `SuperweaponValidator.validate_*()` WITHOUT passing `component_registry`:
  - Line 46-48: `validate_implode_planet(session.galaxy, fleet, planet)` - missing 4th arg
  - Line 70-72: `validate_stellerate_star(session.galaxy, fleet)` - missing 3rd arg
  - Line 94-96: `validate_open_warp_point(session.galaxy, fleet, cmd.target_system_name)` - missing 4th arg
  - Line 122-124: `validate_close_warp_point(session.galaxy, fleet, cmd.warp_point_destination_id)` - missing 4th arg
  - Line 146-148: `validate_create_dyson_sphere(session.galaxy, fleet)` - missing 3rd arg
  - Line 170: `validate_self_destruct(fleet, cmd.ship_ids)` - missing 3rd arg
- In `SuperweaponValidator`, each validator has `if component_registry is not None:` guard (e.g., line 58), meaning ability checks are silently skipped when `component_registry` is `None`.

### Task 2.2: VC-002/CP-005 - Add Validation to Superweapon Mission Handlers
**Status:** STILL_VALID
**Evidence:**
- All 5 mission handlers (`ImplodePlanetMissionCommandHandler`, `StellerateStarMissionCommandHandler`, `OpenWarpPointMissionCommandHandler`, `CloseWarpPointMissionCommandHandler`, `CreateDysonSphereMissionCommandHandler`) in `superweapon_command_handlers.py` lines 223-345 perform NO validation calls.
- They only call `_setup_mission_move()` for pathing, then directly queue the action order without checking if the fleet has the required superweapon ability.
- Compare with the direct handlers (lines 30-178) which DO call `SuperweaponValidator.validate_*()`.

### Task 2.3: VC-007 - Eliminate ships[0] Fallback in SuperweaponOrderProcessor
**Status:** STILL_VALID
**Evidence:**
- `superweapon_order_processor.py` has `fleet.ships[0]` fallback at 4 locations:
  - Line 97: `ship = fleet.ships[0] if fleet.ships else None` (process_implode_planet)
  - Line 265: `ship = fleet.ships[0] if fleet.ships else None` (process_open_warp_point)
  - Line 357: `ship = fleet.ships[0] if fleet.ships else None` (process_close_warp_point)
  - Line 435: `ship = fleet.ships[0] if fleet.ships else None` (process_create_dyson_sphere)
- Each follows the pattern: if `component_registry` is provided, try to find the right ship; if not found or no registry, fall back to `ships[0]`.

---

## Phase 3: Execution Path Cleanup

### Task 3.1: EP-001 - Remove JOIN_FLEET from Dual Execution Path
**Status:** STILL_VALID
**Evidence:**
- `OrderType.JOIN_FLEET` is in `ACTION_ORDER_TYPES` (fleet.py line 54), making it eligible for tick-based execution via `ActionExecutionEngine`.
- `FleetOrderProcessor.process_end_turn_orders()` handles `JOIN_FLEET` at line 627-629 (tick-based path via ActionExecutionEngine).
- `FleetOrderProcessor.process_instant_orders()` also handles `JOIN_FLEET` at line 691 (instant path every subtick).
- Both paths call `process_join_fleet()`, creating dual execution.

### Task 3.2: EP-005 - Standardize Error Handling Across Execution Paths
**Status:** STILL_VALID
**Evidence:**
- `FleetMovementEngine.apply_movement()` calls `fleet.clear_orders()` on failure (lines 153, 165, 170), destroying the entire order queue.
- `FleetOrderProcessor` methods call `fleet.pop_order()` on failure (lines 157, 212, 238, 250, 311, 352, 620), removing only the current failed order and preserving the rest of the queue.
- Inconsistency: A movement resource failure wipes all queued orders (including non-movement orders like COLONIZE that follow), while an action failure preserves queued orders.

---

## Phase 4: Command Pipeline Consistency

### Task 4.1: CP-002 - Route BUILD Orders Through Command Pipeline
**Status:** STILL_VALID
**Evidence:**
- `strategy_build_queue_manager.py` line 138: `fleet.orders.insert(0, FleetOrder(OrderType.BUILD))` creates BUILD orders directly by constructing `FleetOrder` objects and inserting into `fleet.orders`.
- No `IssueBuildFleetOrderCommand` or equivalent exists in `commands.py`. The existing `IssueBuildShipCommand` (command_handlers.py line 296) handles planet production queue, not fleet BUILD orders.
- BUILD fleet orders bypass the entire command pipeline (validation, logging, event dispatch).

### Task 4.2: CP-001 - Route FleetOrdersWindow Clear Through Command Pipeline
**Status:** STILL_VALID
**Evidence:**
- `FleetOrdersWindow.handle_global_event()` at line 386: `self.fleet.clear_orders()` directly manipulates the fleet's order list.
- `ClearFleetOrdersCommand` exists (commands.py line 104) and `ClearOrdersCommandHandler` exists (command_handlers.py line 462) and is registered in the command registry (line 628).
- The UI bypasses this established command pipeline, directly mutating fleet state.

### Task 4.3: CP-003 - Extract Shared Auto-Load Population Helper
**Status:** STILL_VALID
**Evidence:**
- `ColonizeCommandHandler.execute()` lines 234-246: auto-load population block using `session._find_colony_at_fleet(fleet)`.
- `ColonizeMissionCommandHandler.execute()` lines 429-441: nearly identical auto-load population block.
- Both blocks: find origin colony, check populations, extract species_id, create transfer_params dict, create `FleetOrder(OrderType.LOAD_POPULATION, target=transfer_params)`, add to fleet.
- Only difference: the comment on `amount` field (`0` vs `0  # 0 = load as much as possible`).

---

## Phase 5: Code Hygiene & Dead Code

### Task 5.1: EP-002 - Remove Dead Lifecycle Methods
**Status:** STILL_VALID
**Evidence:**
- `FleetOrderProcessor.complete_order()` (line 76): grep across `game/` directory finds NO callers except the definition itself and the class docstring.
- `FleetOrderProcessor.cancel_order()` (line 95): grep across `game/` directory finds NO callers except the definition itself.
- `FleetOrderProcessor.cancel_all_orders()` (line 116): grep across `game/` directory finds NO callers except the definition itself.
- Test files `test_fleet_order_processor.py` and `test_build_order_processor.py` reference these methods, but no production code calls them.
- All production code calls `fleet.pop_order()` or `fleet.clear_orders()` directly on the Fleet object instead.

### Task 5.2: EP-004 - Remove Duplicate BUILD Auto-Pop Logic
**Status:** STILL_VALID
**Evidence:**
- `ActionExecutionEngine._process_fleet_action_tick()` lines 140-144: checks `OrderType.BUILD`, auto-pops if `not fleet.construction_queue`, returns None (skips further processing).
- `FleetOrderProcessor.process_end_turn_orders()` lines 606-614: checks `OrderType.BUILD`, auto-pops if `not fleet.construction_queue`, returns False.
- `ActionExecutionEngine` calls `self._order_processor.process_end_turn_orders()` (line 198), but BUILD orders are already handled at line 140 and return `None` before reaching line 148's `ACTION_ORDER_TYPES` check, so the `process_end_turn_orders()` BUILD path at line 606 is never reached via ActionExecutionEngine.
- The `process_end_turn_orders()` BUILD path is dead code when called through ActionExecutionEngine (the only production caller).

### Task 5.3: AU-005 - Extract Template Method for SuperweaponOrderProcessor
**Status:** STILL_VALID
**Evidence:**
- `superweapon_order_processor.py` has 6 `process_*` methods spanning 592 lines total.
- Common skeleton across 5 of 6 methods (excluding `process_self_destruct`):
  1. Get current order, check type
  2. Find ship with ability via `SuperweaponValidator.find_ship_with_ability()`
  3. Fallback to `fleet.ships[0]` if no ship found
  4. Execute effect (planet/star/warp manipulation)
  5. Remove ship from fleet
  6. Pop order
  7. Check fleet_consumed
  8. Log event
  9. Return SuperweaponResult
- Only the "execute effect" step differs per method.

### Task 5.4: AU-002 - Replace process_end_turn_orders() God-Method with Registry
**Status:** STILL_VALID
**Evidence:**
- `FleetOrderProcessor.process_end_turn_orders()` (lines 574-668) is a 94-line method with an if/elif dispatch chain.
- Handles 11 order types: BUILD, COLONIZE, JOIN_FLEET, TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION, IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE, SELF_DESTRUCT.
- Adding a new order type requires modifying this method (violates Open/Closed Principle).
- The superweapon section (lines 638-666) is itself a nested if/elif chain dispatching to SuperweaponOrderProcessor methods.

### Task 5.5: AU-004 - Unify Mission Move+Action Chaining Pattern
**Status:** STILL_VALID
**Evidence:**
- Three distinct implementations of "move to target then perform action":
  1. `add_move_order_if_needed()` in `command_handlers.py` (line 27) - used by `TransferCommandHandler` and `WarpCommandHandler`. Checks `fleet.location == target_hex`, calculates path, adds MOVE order if needed.
  2. `_setup_mission_move()` in `superweapon_command_handlers.py` (line 185) - used by 5 superweapon mission handlers. Determines start hex from last order, calculates path, adds MOVE order. Different from #1: considers existing orders for start hex.
  3. Inline implementation in `ColonizeMissionCommandHandler` (command_handlers.py lines 417-451) - similar to #2 but also inserts LOAD_POPULATION order before the MOVE.
- Patterns #1 and #2 are similar but differ in start hex calculation logic. Pattern #3 adds additional auto-load behavior interleaved with movement setup.

---

## Summary Table

| Task | ID | Status | Notes |
|------|----------|-------------|-------|
| 1.1 | ODM-001 | STILL_VALID | _fleet_ref/_planet_ref markers never resolved |
| 1.2 | ODM-003 | STILL_VALID | Planet.to_dict() output not parseable by FleetOrder.from_dict() |
| 2.1 | VC-001 | STILL_VALID | 6 direct handlers omit component_registry |
| 2.2 | VC-002/CP-005 | STILL_VALID | 5 mission handlers skip validation entirely |
| 2.3 | VC-007 | STILL_VALID | 4 ships[0] fallbacks remain |
| 3.1 | EP-001 | STILL_VALID | JOIN_FLEET in both instant and tick-based paths |
| 3.2 | EP-005 | STILL_VALID | clear_orders() vs pop_order() inconsistency |
| 4.1 | CP-002 | STILL_VALID | BUILD orders bypass command pipeline |
| 4.2 | CP-001 | STILL_VALID | FleetOrdersWindow.clear_orders() bypasses pipeline |
| 4.3 | CP-003 | STILL_VALID | Auto-load population copy-pasted in 2 handlers |
| 5.1 | EP-002 | STILL_VALID | 3 dead lifecycle methods with 0 production callers |
| 5.2 | EP-004 | STILL_VALID | BUILD auto-pop in both ActionExecutionEngine and FleetOrderProcessor |
| 5.3 | AU-005 | STILL_VALID | 6 process_* methods with repeated skeleton |
| 5.4 | AU-002 | STILL_VALID | 94-line if/elif dispatch chain for 11 order types |
| 5.5 | AU-004 | STILL_VALID | 3 different move+action chaining implementations |

---

## Conclusion

The PROJ-207 task list is fully fresh. All 15 tasks accurately describe the current codebase state and are ready for implementation without modifications. No tasks need to be marked done, removed, or updated.
