# Command-to-Order Pipeline Analysis Report

**Date:** 2026-02-27
**Scope:** Fleet order command pipeline: Command classes, CommandHandlerRegistry, handlers, UI entry points, and bypass paths.

---

## Summary

- **Total issues found:** 13
- **Critical:** 1
- **Major:** 4
- **Minor:** 5
- **Info:** 3

The pipeline architecture is fundamentally sound. All UI entry points correctly create Command objects and route them through `facade.handle_command()` -> `GameSession.handle_command()` -> `CommandHandlerRegistry.dispatch()` -> handler. However, there are two notable bypass paths (BUILD orders and FleetOrdersWindow clear), a significant validation asymmetry between IssueColonize and QueueColonizeMission, leftover diagnostic logging in the TransferCommandHandler, and substantial DRY violations in command class boilerplate and auto-load population logic.

---

## Findings

### CRITICAL

#### CP-001: FleetOrdersWindow bypasses command pipeline for Clear All
**ID:** CP-001
**Location:** `game/ui/screens/fleet_orders_window.py:386`
**Issue:** The "Clear All" confirmation handler directly calls `self.fleet.clear_orders()` instead of dispatching a `ClearFleetOrdersCommand` through the facade. This means:
1. The command pipeline (validation, logging, event tracking) is bypassed.
2. The `ClearOrdersCommandHandler` exists and works correctly, but is not used by this code path.
3. The `FleetOrdersWindow` holds a direct reference to the domain `Fleet` object (not a DTO), violating the CQRS-lite pattern.

**Impact:** Any logic added to `ClearOrdersCommandHandler` in the future (e.g., audit logging, validation rules, undo support) will not apply to the UI clear path. The direct domain object manipulation also breaks the facade's encapsulation contract.

**Recommendation:** Refactor `FleetOrdersWindow` to issue a `ClearFleetOrdersCommand` via the facade. This requires passing the facade reference or a callback into the window. Also refactor order reordering and deletion (lines 271-318) to use commands instead of direct `fleet.orders` manipulation.

**Effort:** Medium

---

### MAJOR

#### CP-002: BUILD order created directly in UI, bypassing command pipeline
**ID:** CP-002
**Location:** `game/ui/screens/strategy_build_queue_manager.py:138`
**Issue:** `_handle_fleet_build_queue_close()` directly constructs `FleetOrder(OrderType.BUILD)` and inserts it into `fleet.orders` at position 0. There is no `IssueBuildCommand` class, no handler registered in `CommandHandlerRegistry`, and no validation step.

Additionally, line 142 directly manipulates `fleet.orders` to remove BUILD orders via list comprehension.

**Impact:** BUILD orders are the only order type that completely bypass the command pipeline. While BUILD is a simpler order (no target, no path), the inconsistency means:
- No centralized validation or logging for BUILD order creation/removal.
- If ownership checks or empire-level constraints are ever needed, they must be added to this UI code directly.

**Recommendation:** Create `IssueBuildCommand` / `CancelBuildCommand` classes and corresponding handlers. The handler can be simple but ensures all order types flow through the same pipeline.

**Effort:** Medium

---

#### CP-003: Duplicated auto-load population logic between colonize handlers
**ID:** CP-003
**Location:** `game/strategy/engine/command_handlers.py:145-157` and `game/strategy/engine/command_handlers.py:340-352`
**Issue:** The BUG-70 auto-load population logic is copy-pasted verbatim between `ColonizeCommandHandler` and `ColonizeMissionCommandHandler`. Both contain identical blocks:
```python
origin_colony = session._find_colony_at_fleet(fleet)
if origin_colony and origin_colony.populations:
    species_id = origin_colony.populations[0].race_id if origin_colony.populations else "default"
    transfer_params = {
        'direction': 'load',
        'cargo_type': 'passengers',
        'amount': 0,
        'planet_id': origin_colony.id,
        'species_id': species_id
    }
    load_order = FleetOrder(OrderType.LOAD_POPULATION, target=transfer_params)
    fleet.add_order(load_order)
```

**Impact:** If the auto-load behavior needs to change (e.g., different amount logic, multi-species support), it must be updated in two places. The redundant conditional `if origin_colony.populations` inside a block already guarded by `origin_colony.populations` is also a minor clarity issue.

**Recommendation:** Extract to a method on `BaseCommandHandler`, e.g., `_auto_load_population(session, fleet)`. Both handlers can then call the shared method.

**Effort:** Simple

---

#### CP-004: Validation asymmetry between IssueColonize and QueueColonizeMission
**ID:** CP-004
**Location:** `game/strategy/engine/command_handlers.py:126-171` vs `game/strategy/engine/command_handlers.py:279-372`
**Issue:** The two colonize handlers have significantly different validation depth:

- `ColonizeCommandHandler` validates via `session.turn_engine.validate_colonize_order()` which delegates to `ColonizeValidator.validate()`.
- `ColonizeMissionCommandHandler` performs additional colony pod validation (PROJ-140): checking `find_ship_with_colony_pod`, checking chain limits (`get_available_colony_pods` / `get_committed_colony_pods`), and returning specific error codes (`NO_COLONY_POD`, `COLONY_POD_EXHAUSTED`).

The direct `IssueColonizeCommand` does NOT check colony pod availability or chain limits. This means a fleet at a planet could issue a colonize command even if all pods are already committed by other queued orders.

**Impact:** Potential for issuing invalid colonize orders that will fail at execution time (in `FleetOrderProcessor.process_colonize`), wasting a turn.

**Recommendation:** Ensure `ColonizeCommandHandler` performs the same pod validation that `ColonizeMissionCommandHandler` does, or unify the validation into a shared method on `BaseCommandHandler` or `ColonizeValidator`.

**Effort:** Medium

---

#### CP-005: Superweapon mission handlers skip validation that direct handlers perform
**ID:** CP-005
**Location:** `game/strategy/engine/superweapon_command_handlers.py:225-347`
**Issue:** All five mission handlers (`ImplodePlanetMissionCommandHandler`, `StellerateStarMissionCommandHandler`, `OpenWarpPointMissionCommandHandler`, `CloseWarpPointMissionCommandHandler`, `CreateDysonSphereMissionCommandHandler`) only validate fleet/planet resolution and pathfinding. They do NOT call the `SuperweaponValidator` methods that their corresponding direct handlers call.

For example:
- `ImplodePlanetCommandHandler` calls `SuperweaponValidator.validate_implode_planet()` -- the mission handler does not.
- `StellerateStarCommandHandler` calls `SuperweaponValidator.validate_stellerate_star()` -- the mission handler does not.

The UI layer (`strategy_superweapons.py`) performs capability checks (e.g., `fleet.capabilities.has_ability("DestroyPlanet")`), but this is a UI-layer guard, not engine-layer validation. It could be bypassed by programmatic command creation or future AI integration.

**Impact:** Mission commands could be queued for fleets that lack the required superweapon components. The orders would then either fail silently at execution time or produce unexpected behavior.

**Recommendation:** Add `SuperweaponValidator` calls to mission handlers, or accept that deferred validation at execution time is the intended design (and document this contract explicitly).

**Effort:** Medium

---

### MINOR

#### CP-006: Excessive diagnostic logging in TransferCommandHandler
**ID:** CP-006
**Location:** `game/strategy/engine/command_handlers.py:401-466`
**Issue:** The `TransferCommandHandler` contains 9 `logger.info("DIAG ...")` calls that appear to be leftover debugging instrumentation. These are at `info` level, not `debug`, meaning they will produce output in production.

**Impact:** Log noise; makes it harder to spot actual issues in logs. The DIAG prefix suggests these were always intended as temporary.

**Recommendation:** Remove all DIAG-prefixed log statements or downgrade them to `logger.debug()`.

**Effort:** Simple

---

#### CP-007: Command class `__init__` boilerplate is repetitive
**ID:** CP-007
**Location:** `game/strategy/engine/commands.py:1-324`
**Issue:** Every command class manually sets `self.type = CommandType.ISSUE_ORDER` in its `__init__`. Since all 20 command classes use `CommandType.ISSUE_ORDER`, this is pure boilerplate. A base class `__init__` or `__post_init__` on the dataclass could eliminate this.

Additionally, each command defines an explicit `__init__` that overrides the `@dataclass` auto-generated one, defeating the purpose of using `@dataclass` in the first place. The `@dataclass` decorator is only providing `__repr__` and `__eq__` at this point.

**Impact:** Maintenance overhead when adding new commands. Easy to forget `self.type = CommandType.ISSUE_ORDER`.

**Recommendation:** Use `__post_init__` to set the type:
```python
@dataclass
class Command:
    type: CommandType = field(init=False, default=CommandType.ISSUE_ORDER)
```
Then remove the explicit `__init__` from all subclasses and let `@dataclass` generate them.

**Effort:** Simple

---

#### CP-008: FleetOrdersWindow directly manipulates domain objects
**ID:** CP-008
**Location:** `game/ui/screens/fleet_orders_window.py:271-318`
**Issue:** The `move_order()`, `delete_order()`, and `undo_delete()` methods directly manipulate `self.fleet.orders` (list swap, pop, insert) and `self.fleet.path`. This is direct domain object mutation from the UI layer, bypassing the command pipeline entirely.

There are no corresponding `ReorderFleetOrderCommand` or `DeleteFleetOrderCommand` classes.

**Impact:** Violates the CQRS-lite facade pattern. Any future audit trail, undo system, or multiplayer synchronization would need to be retrofitted into this UI code.

**Recommendation:** Consider adding `ReorderOrderCommand` and `DeleteOrderCommand` to the command pipeline. For now, this is acceptable for a single-player game but creates architectural debt.

**Effort:** Complex (would require 2 new command types + handlers)

---

#### CP-009: No ownership validation in any command handler
**ID:** CP-009
**Location:** `game/strategy/engine/command_handlers.py` (all handlers)
**Issue:** `BaseCommandHandler._resolve_fleet()` accepts an optional `empire_id` parameter for ownership validation, but NO handler passes it. Every handler calls `self._resolve_fleet(session, cmd.fleet_id)` without the empire_id argument.

This means any command can operate on any fleet, regardless of which empire issued it. In a single-player game this is benign, but represents a missing security boundary.

**Impact:** Low in single-player context. Would be a security vulnerability in multiplayer or if AI ever dispatches commands directly.

**Recommendation:** Commands should carry an `empire_id` field, and handlers should pass it to `_resolve_fleet()`. Alternatively, the `GameSession.handle_command()` method could inject the current empire before dispatching.

**Effort:** Medium

---

#### CP-010: `ColonizeMissionCommandHandler` path optimization differs from `_setup_mission_move`
**ID:** CP-010
**Location:** `game/strategy/engine/command_handlers.py:354-364` vs `game/strategy/engine/superweapon_command_handlers.py:185-222`
**Issue:** `ColonizeMissionCommandHandler` has its own inline move+path logic that is slightly different from `_setup_mission_move()` used by all superweapon mission handlers. Specifically, `ColonizeMissionCommandHandler` uses `find_hybrid_path` directly with additional logic for auto-load order insertion, while `_setup_mission_move()` is a cleaner extracted helper.

The colonize handler could not use `_setup_mission_move()` directly because it inserts a LOAD_POPULATION order before the MOVE order, which changes the "is it the first order?" check. However, the duplication of the move/path setup pattern across these two locations is a minor DRY issue.

**Recommendation:** Accept current state. The colonize mission has unique requirements (auto-load, pod validation) that make full unification impractical without over-abstraction.

**Effort:** N/A (accepted)

---

### INFO

#### CP-011: IssueWarpCommand has no UI entry point
**ID:** CP-011
**Location:** `game/strategy/engine/commands.py:307-324`
**Issue:** `IssueWarpCommand` is fully implemented with a registered handler (`WarpCommandHandler`), but there is no UI code in `game/ui/` that creates or dispatches this command. A grep for `IssueWarpCommand` in the `game/ui/` directory returns no results.

**Impact:** The warp command may be used programmatically or by future AI, but currently has no user-facing entry point. This is not necessarily a bug -- the WARP order type is processed by the movement engine during ticks.

**Recommendation:** Verify whether warp traversal is triggered by clicking on warp points in the UI (which might use MOVE orders instead) or if a WARP UI trigger is still needed. If warp point traversal works via MOVE orders to warp point hexes, then this command class may be dead code.

**Effort:** Simple (investigation only)

---

#### CP-012: TransferCommandHandler finds owning empire by iterating all empires
**ID:** CP-012
**Location:** `game/strategy/engine/command_handlers.py:411-419`
**Issue:** `TransferCommandHandler` finds the owning empire by iterating `session.empires` and checking `fleet in emp.fleets`. This is O(E*F) where E = empires and F = fleets per empire. Other handlers don't need this because they use `fleet.owner_id` or don't need empire context.

The result `owning_empire` is resolved but never actually used after validation -- the handler only uses it for the "Fleet owner not found" check.

**Impact:** Minor performance concern and dead code. The `owning_empire` variable is resolved but has no downstream usage.

**Recommendation:** Remove the owning empire lookup if it is not needed. If ownership validation is desired, use `fleet.owner_id` instead.

**Effort:** Simple

---

#### CP-013: Consistent use of facade pattern across all UI modules
**ID:** CP-013
**Location:** All UI files in scope
**Issue:** This is a positive finding. All six UI modules examined (`strategy_fleet_ops.py`, `strategy_colonization.py`, `transfer_dialog.py`, `cargo_quick_dialog.py`, `strategy_superweapons.py`, `fleet_orders_window.py`) correctly use `self.facade.handle_command(cmd)` for command dispatch. None of them access `GameSession` directly for order creation.

The exceptions (BUILD order in `strategy_build_queue_manager.py` and clear/reorder in `fleet_orders_window.py`) are noted in CP-001, CP-002, and CP-008 above.

**Impact:** Positive -- the architectural pattern is well-adopted.

**Recommendation:** No action needed. Continue enforcing this pattern for new features.

**Effort:** N/A

---

## Top 5 Priority Issues

1. **CP-001 (Critical):** FleetOrdersWindow bypasses command pipeline for Clear All -- Direct domain mutation from UI violates the command pattern and could miss future validation/logging.

2. **CP-005 (Major):** Superweapon mission handlers skip validation -- Mission commands can be queued for fleets without the required superweapon components; validation only happens at execution time (if at all).

3. **CP-004 (Major):** Validation asymmetry between colonize handlers -- `IssueColonizeCommand` lacks the colony pod chain-limit checks that `QueueColonizeMissionCommand` performs, potentially allowing invalid orders.

4. **CP-002 (Major):** BUILD order bypasses command pipeline entirely -- The only order type with no Command class, no handler, and no registry entry.

5. **CP-003 (Major):** Duplicated auto-load population logic -- Identical 12-line block copy-pasted between two handlers; straightforward to extract.

---

## Architecture Assessment

The command-to-order pipeline has a clean, well-structured architecture:

```
UI Action
  -> Command object (dataclass)
    -> facade.handle_command(cmd)
      -> GameSession.handle_command(cmd)
        -> CommandHandlerRegistry.dispatch(cmd.name, session, cmd)
          -> Handler.execute(session, cmd)
            -> Validate
            -> FleetOrder(OrderType.X, target=...)
            -> fleet.add_order(order)
            -> ValidationResult
```

**20 command types** are registered in the registry. **All 20** have corresponding handlers that follow the `resolve -> validate -> apply` pattern. The `BaseCommandHandler` provides useful shared resolution helpers.

**Key bypass paths** (2 found):
1. `strategy_build_queue_manager.py` -- BUILD orders created directly
2. `fleet_orders_window.py` -- Order deletion, reordering, and clearing done directly

**AI layer** does not participate in strategy-level fleet orders. AI is limited to combat simulation targeting/movement. No AI-issued fleet commands were found.

**FleetOrder construction** is properly confined to command handlers and the save/load deserialization path (`Fleet.from_dict`). No UI code constructs `FleetOrder` objects directly (except the BUILD order bypass).
