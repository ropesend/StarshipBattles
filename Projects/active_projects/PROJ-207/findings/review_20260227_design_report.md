# PROJ-207 Design Pattern Analysis Report

**Date:** 2026-02-27
**Analyst:** Claude Opus 4.6 (Design Pattern Review Agent)
**Scope:** Verify PROJ-207 design assumptions against current codebase state
**Method:** Full source review of all 10 in-scope files plus related infrastructure

## Summary

The PROJ-207 plan is well-aligned with current codebase patterns. The architecture described in the design document accurately reflects the codebase as it exists today. However, several specific implementation details in the phase checklists reference incorrect accessor paths, use the wrong API name, or overlook existing patterns that could simplify the work.

**Overall assessment:** 8 findings, 0 blockers, 3 requiring plan updates, 5 informational.

---

## Findings

### F-001: Task 2.1 References Non-Existent `session.registries.components` Accessor

**Plan Assumption:** Phase 2, Task 2.1 instructs the implementer to use `session.registries.components` to pass the component registry to superweapon validators.

**Current Reality:** `GameSession` has no `registries` property. The existing pattern in the codebase accesses the component registry via `session.turn_engine._registries.components`. This is the pattern used by `ColonizeMissionCommandHandler` at `command_handlers.py` line 388:
```python
component_registry = session.turn_engine._registries.components
```
No public accessor exists on `GameSession` for registries.

**Impact:** Medium. An implementer following the checklist literally would get an `AttributeError`. They would need to discover the correct path themselves.

**Proposed Resolution:** Update Task 2.1 (and Task 2.2) checklist items to reference `session.turn_engine._registries.components` instead of `session.registries.components`. Alternatively, consider adding a `@property` accessor to `GameSession` as a preliminary step, but that would be scope creep for this project.

---

### F-002: Task 4.2 (CP-001) Uses Wrong API Name: `dispatch_command` vs `handle_command`

**Plan Assumption:** Task 4.2 proposes routing `FleetOrdersWindow` clear through command pipeline using `self.session.dispatch_command(cmd)`.

**Current Reality:** `GameSession` does not have a `dispatch_command()` method. The correct API is `handle_command(cmd)` (defined at `game_session.py` line 194). Additionally, UI components do not call `session.handle_command()` directly -- they go through `StrategySessionFacade.handle_command()`:

```python
# Typical UI pattern (e.g., strategy_fleet_ops.py line 123):
result = self.facade.handle_command(cmd)
```

The plan's example code:
```python
cmd = ClearFleetOrdersCommand(fleet_id=self.fleet.id)
self.session.dispatch_command(cmd)  # WRONG: method is handle_command, via facade
```

**Impact:** Medium. Two errors in the example: wrong method name and wrong access pattern (direct session vs facade).

**Proposed Resolution:** Update Task 4.2 to:
1. Use `facade.handle_command(cmd)` instead of `session.dispatch_command(cmd)`.
2. Note that the facade reference needs to be threaded through from the parent screen (see F-003).

---

### F-003: Task 4.2 Underestimates Threading Depth for Session/Facade Access

**Plan Assumption:** Task 4.2 notes "If session not available, thread it through from the parent screen" for `FleetOrdersWindow`.

**Current Reality:** The threading chain is deeper than implied:
1. `FleetOrdersWindow.__init__` accepts `(rect, manager, fleet, input_mapper)` -- no session or facade.
2. `StrategyWindowManager.open_orders_window()` creates the window at line 279 -- it also has no session/facade reference.
3. The `handle_global_event` method (line 382-391) is called by `StrategyEventRouter` at line 105 -- which has access to `self.ui` (a `StrategyUI` instance) but not the session directly.

The standard UI pattern is to use `StrategySessionFacade` (in `game/strategy/facade/strategy_session_facade.py`), which wraps `GameSession.handle_command()`. Getting this reference to `FleetOrdersWindow` requires modifying three layers.

**Impact:** Low-Medium. The task is still feasible but the effort is underestimated. The existing `ClearOrdersCommandHandler` (line 462-477 of `command_handlers.py`) just does `fleet.orders = []; fleet.path = []`, which is functionally identical to the current `fleet.clear_orders()` call.

**Proposed Resolution:** The task should either:
(a) Explicitly list the files needing signature changes: `strategy_window_manager.py`, `fleet_orders_window.py`, and the calling context in `strategy_event_router.py` or `strategy_screen.py`, OR
(b) Reconsider whether the command logging value justifies the three-file change, given the handler's implementation is trivially simple.

---

### F-004: `add_move_order_if_needed()` Is NOT Chain-Aware -- Task 5.5 Would Break Multi-Order Chaining

**Plan Assumption:** Task 5.5 (AU-004) proposes updating `ColonizeMissionCommandHandler` to use `add_move_order_if_needed()` (lines 27-60 of `command_handlers.py`) instead of inline path calculation.

**Current Reality:** `add_move_order_if_needed()` calculates the path from `fleet.location`:
```python
# add_move_order_if_needed (line 44):
if fleet.location == target_hex:  # Only checks CURRENT location
```

Both `ColonizeMissionCommandHandler` (lines 417-422) and `_setup_mission_move()` (lines 199-204 of `superweapon_command_handlers.py`) are chain-aware -- they check the last queued MOVE order's target:
```python
# ColonizeMissionCommandHandler (line 419-422):
start_hex = fleet.location
if fleet.orders:
    last = fleet.orders[-1]
    if last.type == OrderType.MOVE:
        start_hex = last.target
```

If `ColonizeMissionCommandHandler` is naively switched to use `add_move_order_if_needed()`, multi-order chains would break. For example, a TRANSFER followed by a COLONIZE mission would calculate the MOVE path from the fleet's current location instead of from the TRANSFER's destination.

**Impact:** Medium. This would introduce a regression in multi-order chaining if implemented as described.

**Proposed Resolution:** Task 5.5 should either:
(a) Enhance `add_move_order_if_needed()` to accept an optional `start_hex` parameter for chain awareness, OR
(b) Refactor `ColonizeMissionCommandHandler` to use `_setup_mission_move()` from the superweapon module (but this creates a cross-concern dependency).
Option (a) is cleaner. The task checklist should explicitly note the chain-awareness requirement.

---

### F-005: Task 4.1 BUILD Order Has Unique Semantics Not Fully Addressed

**Plan Assumption:** Task 4.1 proposes creating `IssueBuildOrderCommand` + `BuildOrderCommandHandler` following the standard command/handler pattern.

**Current Reality:** The BUILD order has unique semantics that differ from all other commands (see `strategy_build_queue_manager.py` lines 128-142):
1. It is inserted at position 0 (`fleet.orders.insert(0, FleetOrder(OrderType.BUILD))`), not appended via `fleet.add_order()`.
2. It also clears the path (`fleet.path = []`).
3. It has removal logic: when the construction queue empties, BUILD orders are filtered out via list comprehension (`fleet.orders = [o for o in fleet.orders if o.type != OrderType.BUILD]`).
4. The removal is triggered by a UI close callback (`_on_build_queue_close`), not by a user command.

A `BuildOrderCommandHandler` would need to handle insert-at-0 semantics (using `fleet.add_order(order, index=0)` -- the method already supports this) and path clearing.

**Impact:** Low. The existing `fleet.add_order(order, index=0)` API supports position-0 insertion. The main concern is whether the removal path also needs a command.

**Proposed Resolution:** The task should clarify that only BUILD order *creation* goes through the command pipeline. The auto-removal on empty queue is an internal lifecycle operation and should remain as-is in `_on_build_queue_close`. This is consistent with how other lifecycle-driven order changes (e.g., `fleet.pop_order()` during execution) work outside the command pipeline.

---

### F-006: Superweapon Template Method (Task 5.3) Should Exclude `process_self_destruct`

**Plan Assumption:** Task 5.3 says "All 6 `process_*` methods repeat an identical skeleton" and proposes a template method.

**Current Reality:** 5 of the 6 methods follow the described pattern. However, `process_self_destruct()` (lines 525-592) diverges significantly:
- It does NOT look up a ship by ability name (it takes a list of ship IDs directly).
- It removes MULTIPLE ships (not just one).
- It does NOT use `SuperweaponValidator.find_ship_with_ability()`.
- It does NOT consume a ship in exchange for an effect -- it destroys specified ships as its primary action.

**Impact:** Low. The template method can still provide strong value for the 5 conforming methods (implode, stellerate, open warp, close warp, dyson sphere). Self-destruct should remain standalone.

**Proposed Resolution:** Update Task 5.3 to note that the template applies to 5 of 6 methods, with `process_self_destruct` remaining standalone due to its fundamentally different ship selection and removal pattern. Adjust the line count estimates accordingly (5 methods, not 6).

---

### F-007: Phase 1 Task 1.1 -- The `resolve_order_references` Call Site Needs Precise Placement

**Plan Assumption:** Task 1.1 says "Call `resolve_order_references()` in the game session load path, after all empires and galaxy are fully restored."

**Current Reality:** In `GameSession.from_dict()` (lines 265-330 of `game_session.py`):
- Line 301: Galaxy is loaded (all planets exist with IDs)
- Lines 312-315: Empires are loaded (each empire loads its fleets via `Fleet.from_dict()`, which creates `_fleet_ref` and `_planet_ref` markers)
- Line 330: `return session`

The resolution call needs to go between lines 321-329, after ALL empires are loaded (so cross-empire fleet references can be resolved) and after the galaxy is available (for planet lookups). The method would need `session.galaxy` and `session.empires` as inputs.

Additionally, `Empire.from_dict()` already resolves colony planet references (lines 233-238) using `galaxy.get_planet_by_id()`, establishing a precedent for post-load resolution. The fleet order resolution would follow the same pattern.

**Impact:** Informational. The plan's description is correct but could be more specific about the exact insertion point.

**Proposed Resolution:** No plan change needed. The implementer should insert the resolution loop at approximately line 325 of `game_session.py`, after `session.empires` is fully populated.

---

### F-008: ClearFleetOrdersCommand Handler Already Exists -- CP-001 Infrastructure Is Ready

**Plan Assumption:** Task 4.2 proposes routing `FleetOrdersWindow` clear through `ClearFleetOrdersCommand`.

**Current Reality:** The full infrastructure already exists:
- `ClearFleetOrdersCommand` class: `commands.py` line 104
- `ClearOrdersCommandHandler`: `command_handlers.py` line 462
- Handler registered: `create_default_registry()` at line 628

The handler resolves the fleet, clears orders/path, logs the action, and returns `ValidationResult`. The only missing piece is wiring it from the UI.

**Impact:** Positive. This confirms the approach is viable and the command/handler infrastructure is already in place. Only the call-site wiring is needed.

**Proposed Resolution:** No change needed. This confirms the plan's approach.

---

## Cross-Cutting Observations

### Pattern Consistency: Confirmed

The codebase consistently uses these patterns:
- `BaseCommandHandler` with `_resolve_fleet()` / `_resolve_planet()` helpers
- `CommandHandlerRegistry` for dispatch
- `StrategySessionFacade.handle_command()` for UI-to-engine communication
- `ValidationResult` for return values
- `FleetOrder(OrderType.X, target=Y)` for order creation
- `fleet.add_order()` for appending (with `index` parameter for position-0 insertion)

The plan correctly identifies and reuses all of these patterns.

### No New Patterns Since Plan Creation

No evidence of new patterns being introduced since the plan was written. The codebase structure matches what the design document describes. Key files have not been refactored in ways that would invalidate the plan's approach.

### Dependency Chain: Validated

The plan's phase ordering (Phase 3 before Phase 5) is correct:
- Task 5.4 (replace if/elif chain) depends on Task 3.1 (remove JOIN_FLEET from ACTION_ORDER_TYPES) and Task 5.2 (remove BUILD auto-pop duplicate).
- After Phase 3 removes the JOIN_FLEET branch, the if/elif chain in `process_end_turn_orders()` shrinks, making the registry conversion in Task 5.4 cleaner.

### IOrderProcessor Interface: Task 5.4 Rename Impact

Task 5.4 proposes renaming `process_end_turn_orders()` to `execute_action_order()` and updating the `IOrderProcessor` interface in `engines.py`. The interface is at `engines.py` line 165, and the abstract method `process_end_turn_orders` is at line 202. This rename would also need to update `ActionExecutionEngine._execute_action()` (line 198 of `action_execution_engine.py`) which calls this method.

### Line Number Accuracy

Most line numbers in the plan are accurate to the current file state:
- `fleet.py` line 54: `JOIN_FLEET` in `ACTION_ORDER_TYPES` -- **correct**
- `fleet_order_processor.py` lines 574-668: `process_end_turn_orders` -- **correct** (574 start, 668 end)
- `fleet_order_processor.py` lines 670-704: `process_instant_orders` -- **correct**
- `fleet_order_processor.py` lines 76-127: lifecycle methods -- **correct**
- `fleet_movement_engine.py` lines 153, 165, 170: `clear_orders()` calls -- **correct**
- `action_execution_engine.py` lines 140-145: BUILD auto-pop -- **correct**
- `superweapon_order_processor.py` lines 97, 265, 357, 435: `ships[0]` fallbacks -- **correct**
- `fleet_orders_window.py` line 386: `clear_orders()` call -- **correct**
- `strategy_build_queue_manager.py` line 138: direct BUILD order insertion -- **correct**
- `command_handlers.py` line ~514 for `create_default_registry()` -- **stale**, actual line is 599

### Test Baseline

The plan states a baseline of 12,827 tests. This should be re-verified before starting implementation, as the test count may have changed since the plan was written.

---

## Recommendations (Priority Order)

1. **[Required] Update Task 2.1 and 2.2** to use `session.turn_engine._registries.components` instead of `session.registries.components`.
2. **[Required] Update Task 4.2** to use `facade.handle_command(cmd)` instead of `session.dispatch_command(cmd)`, and note the facade threading requirement.
3. **[Required] Update Task 5.5** to note that `add_move_order_if_needed()` needs a `start_hex` parameter for chain-aware path calculation before it can replace the inline logic in `ColonizeMissionCommandHandler`.
4. **[Recommended] Update Task 5.3** to note `process_self_destruct` exclusion from the template method.
5. **[Recommended] Verify test baseline** before starting Phase 1.
6. All other plan assumptions are validated and the implementation approach is sound.
