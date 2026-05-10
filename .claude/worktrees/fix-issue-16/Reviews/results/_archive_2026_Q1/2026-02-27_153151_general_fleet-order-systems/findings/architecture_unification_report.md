# Fleet Order System Architecture & Unification Analysis

## Summary
- Total issues found: **14**
- Critical: **1**, Major: **5**, Minor: **5**, Info: **3**

---

## 1. System Count and Boundaries

The fleet order pipeline involves **7 distinct systems**:

| # | System | File(s) | Responsibility |
|---|--------|---------|----------------|
| 1 | **Command Definitions** | `commands.py` | 20 dataclass command objects |
| 2 | **Command Handlers** | `command_handlers.py`, `superweapon_command_handlers.py` | 20 handler classes: resolve, validate, create orders |
| 3 | **Command Registry** | `command_handlers.py` (CommandHandlerRegistry) | Dispatch command name -> handler |
| 4 | **Validators** | `colonize_validator.py`, `transfer_validator.py`, `superweapon_validator.py` | Business-rule validation |
| 5 | **Order Data Model** | `fleet.py` (FleetOrder, OrderType) | Order representation, serialization |
| 6 | **Order Lifecycle Processor** | `fleet_order_processor.py`, `superweapon_order_processor.py` | Execute completed orders, mutate game state |
| 7 | **Execution Engines** | `action_execution_engine.py`, `fleet_movement_engine.py`, `turn_engine.py` | Tick scheduling, progress tracking, orchestration |

### Current Flow Diagram

```
UI Click
  -> Command dataclass created (commands.py)
    -> CommandHandlerRegistry.dispatch() (command_handlers.py)
      -> Handler.execute():
        1. Resolve fleet/planet (BaseCommandHandler helpers)
        2. Validate (Validator classes or inline)
        3. Create FleetOrder(s) and add to fleet.orders
  -> Turn begins:
    -> TurnEngine._process_tick() [100 times]:
      -> Phase 1: FleetOrderProcessor.process_instant_orders() [JOIN_FLEET]
      -> Phase 1.5: ActionExecutionEngine.process_action_ticks()
        -> Increment execution_progress
        -> When complete: FleetOrderProcessor.process_end_turn_orders()
          -> Dispatch by order.type (if/elif chain)
          -> For superweapons: SuperweaponOrderProcessor
      -> Phase 2-3: FleetMovementEngine.collect_movements() + apply_movements()
```

### Boundary Assessment

The boundaries between systems 1-3 (Command -> Handler -> Registry) are **well-defined and consistent**. The registry pattern was a good extraction (PROJ-87).

The boundaries between systems 4-6 (Validator -> Order -> Processor) are **fragmented** -- validation happens in different places (handlers, validators, processors) and the dispatch in the processor is a hand-coded if/elif chain instead of using the same registry pattern as commands.

The boundary between system 6 and 7 (Processor -> Engines) is **mostly clean**, with ActionExecutionEngine providing a good tick-based wrapper. However, FleetOrderProcessor.process_end_turn_orders() is doing double duty as both the ActionExecutionEngine's delegate and as a direct dispatcher with its own if/elif chain.

---

## 2. Findings

### CRITICAL

#### {CRITICAL}: FleetOrder.to_dict() serialization is a fragile type-switching cascade
**ID:** AU-001
**Location:** `game/strategy/data/fleet.py:75-113` (FleetOrder.to_dict) and `fleet.py:443-478` (Fleet.from_dict order restoration)
**Issue:** FleetOrder serialization uses a cascading `isinstance` / `order.type` check to determine how to serialize the `target` field. There are 7 distinct target formats (HexCoord, Planet, Fleet ref, transfer dict, planet_ref, ship_id_list, warp_params, raw fallback). Deserialization has a matching 7-way branch. Every new order type requires updating both branches.
**Impact:** This is the single most fragile point in the entire pipeline. Adding a new order type requires remembering to update both to_dict and from_dict. A missed case silently loses data through the `raw` fallback. The serialization format has no discriminated union -- some branches check `order.type`, others check `isinstance(target, ...)`, creating an inconsistent dispatch strategy.
**Recommendation:** Introduce a discriminated `OrderTarget` type hierarchy (or a `target_type` enum field on FleetOrder) so serialization is driven by the target's own `to_dict()`/`from_dict()` methods rather than external isinstance checks. Each target type would be self-serializing. Example:
```python
@dataclass
class HexTarget:
    coord: HexCoord
    def to_dict(self): return {'type': 'hex', 'q': self.coord.q, 'r': self.coord.r}

@dataclass
class TransferTarget:
    params: dict
    def to_dict(self): return {'type': 'transfer', 'value': self.params}
```
**Effort:** Medium (touches serialization/deserialization and all order-creation sites)

---

### MAJOR

#### {MAJOR}: FleetOrderProcessor.process_end_turn_orders() is a dispatch god-method
**ID:** AU-002
**Location:** `game/strategy/engine/fleet_order_processor.py:585-675`
**Issue:** This method is a 90-line if/elif chain dispatching on `order.type` across 10+ order types. It manually imports and instantiates `SuperweaponOrderProcessor()` on every call. This pattern is the exact opposite of the registry-based dispatch already used for commands (CommandHandlerRegistry). There is no polymorphism or lookup table -- just cascading conditionals.
**Impact:** Every new action order type requires editing this method. The superweapon block alone is 6 nested conditionals. The method name ("process_end_turn_orders") is misleading since PROJ-187 moved it to per-tick execution -- the docstring acknowledges this but says "name retained for compatibility."
**Recommendation:** Replace the if/elif chain with an `OrderExecutorRegistry` following the same pattern as `CommandHandlerRegistry`. Each order type gets a registered executor. The method becomes a 5-line dispatch. Also rename to `execute_action_order()` to reflect its actual purpose.
**Effort:** Medium

#### {MAJOR}: Validation is split across three layers with inconsistent patterns
**ID:** AU-003
**Location:** Cross-cutting: `command_handlers.py`, `colonize_validator.py`, `transfer_validator.py`, `superweapon_validator.py`, `fleet_order_processor.py`
**Issue:** Validation happens in three different places:
1. **Command handlers** (inline): `MoveCommandHandler` does pathfinding validation inline. `WarpCommandHandler` does warp capability validation inline. `ColonizeCommandHandler` delegates to `TurnEngine.validate_colonize_order()` which delegates to `ColonizeValidator`.
2. **Validator classes** (dedicated): `ColonizeValidator`, `TransferValidator`, `SuperweaponValidator` -- but with inconsistent APIs. ColonizeValidator uses static methods with `ValidationResult`. SuperweaponValidator has 6 separate `validate_X()` static methods. TransferValidator has a single `validate()` with internal dispatch.
3. **Order processor** (re-validation at execution): `FleetOrderProcessor.process_colonize()` calls `ColonizeValidator.validate()` again at execution time. Superweapon processors don't re-validate.

This means some orders are validated twice (COLONIZE), some once (superweapons at command time), and some inline (MOVE, WARP).
**Impact:** Inconsistent reliability -- if a colonize order's preconditions change between queuing and execution, it's caught. But if a superweapon's preconditions change, it's not caught because there's no execution-time re-validation.
**Recommendation:** Standardize to: (a) lightweight validation at command time (can I queue this?), (b) full validation at execution time (can I execute this now?). All validators should have a consistent `validate()` entry point returning `ValidationResult`. Move execution-time validation into the order executors uniformly.
**Effort:** Complex

#### {MAJOR}: Mission command handlers duplicate MOVE-then-action pattern
**ID:** AU-004
**Location:** `game/strategy/engine/superweapon_command_handlers.py:185-346` and `game/strategy/engine/command_handlers.py:276-372`
**Issue:** The "move to location then perform action" pattern is implemented in 7 places:
1. `ColonizeMissionCommandHandler` -- has its own inline move logic (lines 329-364)
2. `ImplodePlanetMissionCommandHandler` -- uses `_setup_mission_move()`
3. `StellerateStarMissionCommandHandler` -- uses `_setup_mission_move()`
4. `OpenWarpPointMissionCommandHandler` -- uses `_setup_mission_move()`
5. `CloseWarpPointMissionCommandHandler` -- uses `_setup_mission_move()`
6. `CreateDysonSphereMissionCommandHandler` -- uses `_setup_mission_move()`
7. `TransferCommandHandler` -- has its own inline move logic (lines 446-452)
8. `WarpCommandHandler` -- has its own inline move logic (lines 501-504)

The superweapon missions share `_setup_mission_move()` (good), but ColonizeMission, Transfer, and Warp each reinvent the wheel with slightly different implementations. ColonizeMission includes population auto-load logic mixed in with movement setup. Transfer skips pathfinding validation.
**Impact:** Bugs fixed in one move-prefix implementation may not be applied to others. The ColonizeMission handler at 93 lines is the most complex handler, mixing population loading, path calculation, pod validation, and order queuing.
**Recommendation:** Extract a unified `MissionBuilder` that takes (fleet, target_hex, action_orders) and handles: determine start hex from existing orders, calculate path, queue MOVE if needed, queue action orders. ColonizeMission's population-load step would be a pre-action hook.
**Effort:** Medium

#### {MAJOR}: SuperweaponOrderProcessor duplicates the "find ability ship, remove ship, pop order, check empty" pattern
**ID:** AU-005
**Location:** `game/strategy/engine/superweapon_order_processor.py:54-591`
**Issue:** Every superweapon processor method (6 total) repeats the same skeleton:
1. Check order type
2. Find ship with ability via `SuperweaponValidator.find_ship_with_ability()`
3. Fallback to `fleet.ships[0]` if no registry
4. Execute the effect
5. Remove the ship
6. Pop the order
7. Check `len(fleet.ships) == 0` for fleet_consumed
8. Log event

Steps 1-3 and 5-8 are identical across all 6 methods. Only step 4 (the effect) differs. This is 540 lines of code where ~350 lines are template boilerplate.
**Impact:** Each new superweapon requires copying ~60 lines of boilerplate and changing ~15 lines of actual logic. The "fallback to fleet.ships[0]" pattern is duplicated in 5 places.
**Recommendation:** Extract a `_execute_superweapon_template()` method that handles the common skeleton and takes a callback for the unique effect. Alternatively, use a strategy pattern where each superweapon effect is a small class with an `execute_effect()` method.
**Effort:** Simple

---

### MINOR

#### {MINOR}: Command dataclasses manually set self.type in __init__ instead of using dataclass defaults
**ID:** AU-006
**Location:** `game/strategy/engine/commands.py` (all 20 command classes)
**Issue:** Every command dataclass has a manual `__init__` that sets `self.type = CommandType.ISSUE_ORDER`. Since all commands currently use the same CommandType, this could be a class attribute or a default field value on the base `Command` dataclass. The manual `__init__` also defeats the purpose of using `@dataclass`.
**Impact:** Low -- it works, but it's boilerplate. Every new command class must remember to include `self.type = CommandType.ISSUE_ORDER`.
**Recommendation:** Set `type: CommandType = CommandType.ISSUE_ORDER` as a default on the `Command` base class and remove manual `__init__` methods. Use `field(default=...)` if needed.
**Effort:** Simple

#### {MINOR}: Diagnostic logging left in TransferCommandHandler
**ID:** AU-007
**Location:** `game/strategy/engine/command_handlers.py:401-466`
**Issue:** TransferCommandHandler.execute() contains 9 `DIAG` log statements (e.g., `"DIAG TransferCommandHandler: cmd fleet_id=..."`). TransferValidator._validate_load() contains 4 more DIAG log statements. These are development/debugging artifacts.
**Impact:** Log noise in production. These are logger.info level, so they appear in normal operation.
**Recommendation:** Remove all `DIAG` prefixed log lines or demote to `logger.debug()`.
**Effort:** Simple

#### {MINOR}: Inconsistent target resolution for TRANSFER orders at execution time
**ID:** AU-008
**Location:** `game/strategy/engine/fleet_order_processor.py:292-380`
**Issue:** `process_transfer()` resolves the target planet/fleet by searching through `galaxy.get_planet_by_id()` or iterating through all empires' fleets. This is different from command handlers which use `session._get_planet_by_id()`. The fleet-to-fleet transfer resolution uses `getattr(galaxy, 'empires', [])` because the galaxy may or may not have an empires attribute, then falls back to searching the current empire. This is fragile and environment-dependent.
**Impact:** Fleet-to-fleet transfers may silently fail if the target fleet isn't found through the search path.
**Recommendation:** Pass a fleet resolver function or all empires explicitly to `process_transfer()`, consistent with how `process_end_turn_orders()` receives `empires` for superweapons.
**Effort:** Simple

#### {MINOR}: BUILD order auto-completion is duplicated between FleetOrderProcessor and ActionExecutionEngine
**ID:** AU-009
**Location:** `game/strategy/engine/fleet_order_processor.py:617-625` and `game/strategy/engine/action_execution_engine.py:139-145`
**Issue:** Both `FleetOrderProcessor.process_end_turn_orders()` and `ActionExecutionEngine._process_fleet_action_tick()` check for BUILD orders with empty construction queues and auto-pop them. This means the same logic runs twice per tick for BUILD orders.
**Impact:** Low -- the double-check is harmless because the first pop removes it. But it indicates unclear ownership of BUILD order lifecycle.
**Recommendation:** BUILD order auto-completion should live in exactly one place. Since ActionExecutionEngine explicitly skips BUILD orders (returns None), the check there is defensive. Remove the BUILD check from one location (preferably FleetOrderProcessor since ActionExecutionEngine is the primary tick processor).
**Effort:** Simple

#### {MINOR}: process_end_turn_orders() name is misleading
**ID:** AU-010
**Location:** `game/strategy/engine/fleet_order_processor.py:585` and `game/strategy/interfaces/engines.py:202`
**Issue:** The method is named `process_end_turn_orders()` but since PROJ-187, it is called during ticks by ActionExecutionEngine, not at end-of-turn. The docstring explicitly says "Name retained for compatibility." The interface `IOrderProcessor` also defines this misleading name.
**Impact:** New developers will be confused about when this method runs. The name suggests once-per-turn semantics when it actually runs per-tick.
**Recommendation:** Rename to `execute_action_order()` or `process_completed_action()` across the codebase. Update the interface simultaneously.
**Effort:** Simple (find-and-replace, but touches interface + implementation + callers)

---

### INFO

#### {INFO}: Order type categorization uses frozensets defined at module level
**ID:** AU-011
**Location:** `game/strategy/data/fleet.py:39-61`
**Issue:** `MOVEMENT_ORDER_TYPES` and `ACTION_ORDER_TYPES` are defined as module-level frozensets. `ActionTimeResolver` maintains a separate mapping (`_get_order_to_ability_map()`). These categorizations must be kept in sync manually. Adding a new order type requires updating the OrderType enum, the appropriate frozenset, the action_time_resolver map, the process_end_turn_orders if/elif chain, and the serialization logic.
**Impact:** Low risk if developers know all the touch points, but there's no enforcement mechanism. A forgotten update to one set will cause silent misrouting of orders.
**Recommendation:** Consider a decorator or metadata system on OrderType that declares the category and ability mapping in one place. Alternatively, document a "new order type checklist" in the codebase.
**Effort:** Medium (architectural change) or Simple (documentation)

#### {INFO}: Superweapon command definitions are verbose but uniform
**ID:** AU-012
**Location:** `game/strategy/engine/commands.py:158-324`
**Issue:** The 11 superweapon-related command classes (6 direct + 5 mission) follow an identical pattern and are very uniform. Each is a simple dataclass with fleet_id and type-specific parameters. This is verbose (170 lines) but not incorrect.
**Impact:** None functionally. The uniformity is actually a strength -- it's predictable and easy to understand.
**Recommendation:** No action needed. The verbosity is acceptable for type safety and IDE support. A more dynamic approach (e.g., generic `IssueOrderCommand(order_type, **params)`) would sacrifice type safety.
**Effort:** N/A

#### {INFO}: Well-designed BaseCommandHandler with shared resolution helpers
**ID:** AU-013
**Location:** `game/strategy/engine/command_handlers.py:43-88`
**Issue:** This is a positive finding. The `BaseCommandHandler` with `_resolve_fleet()` and `_resolve_planet()` static methods was a good extraction (PROJ-176 Phase 2). All 19+ handlers use these consistently. The tuple return pattern `(object, error)` is Go-like but effective.
**Impact:** Positive -- reduces duplication and ensures consistent error messages.
**Recommendation:** None needed. This is a good pattern to preserve and extend.
**Effort:** N/A

---

## 3. Pattern Consistency Scores

| Pattern | Score (1-5) | Notes |
|---------|:-----------:|-------|
| **Command creation** | 4 | Uniform dataclass pattern, minor issue with manual `__init__` |
| **Validation** | 2 | Three different locations, inconsistent APIs (static methods with varying signatures), some orders validated twice, some not at execution time |
| **Order creation** | 3 | FleetOrder(type, target) is uniform, but target formats are wildly heterogeneous (HexCoord, Planet, Fleet, dict, list, string) |
| **Execution** | 2 | if/elif dispatch in FleetOrderProcessor, separate SuperweaponOrderProcessor, duplicated boilerplate patterns |
| **Error handling** | 4 | Consistently uses ValidationResult throughout. Command handlers and validators all return ValidationResult |
| **Serialization** | 1 | 7 different target formats with instanceof-based dispatch, no discriminated union, paired branches in to_dict/from_dict |
| **Order completion/cleanup** | 3 | Most paths call fleet.pop_order(), but some call self.complete_order() while others call fleet.pop_order() directly, bypassing the centralized method |

**Overall Architecture Score: 2.7/5** -- The command layer (UI -> Handler -> Order) is well-structured. The execution layer (Order -> Processor -> Effect) is fragmented.

---

## 4. Top 5 Priority Issues

| Rank | ID | Title | Effort | Impact |
|------|----|-------|--------|--------|
| 1 | AU-001 | Fragile serialization cascade | Medium | Prevents data loss, simplifies adding new orders |
| 2 | AU-002 | God-method dispatch in process_end_turn_orders | Medium | Removes largest maintenance bottleneck |
| 3 | AU-005 | Superweapon processor boilerplate duplication | Simple | Quick win: ~350 lines reducible to ~100 |
| 4 | AU-004 | Mission command handler move-prefix duplication | Medium | Prevents inconsistent mission behavior |
| 5 | AU-003 | Inconsistent validation across layers | Complex | Ensures all orders are validated at execution time |

### Ideal End State Architecture

```
Command (dataclass)
  -> CommandHandlerRegistry.dispatch()
    -> Handler: resolve, lightweight validate, create FleetOrder(s)
      -> FleetOrder has typed OrderTarget (self-serializing)

Turn tick:
  -> ActionExecutionEngine: track progress per tick
    -> When complete: OrderExecutorRegistry.dispatch(order.type)
      -> Executor: full validate, execute effect, cleanup
        -> Each executor is a small focused class
        -> Common template for "find ability ship, execute, remove ship, pop order"

Validators: uniform API, always called at execution time
Serialization: OrderTarget.to_dict() / OrderTarget.from_dict()
```

---

## 5. Justified Heterogeneity

The following differences are **correct design choices** and should NOT be unified:

### Movement vs Action orders -- JUSTIFIED
Movement (MOVE, MOVE_TO_FLEET, WARP) is fundamentally different from actions (COLONIZE, TRANSFER, superweapons). Movement is path-based, operates every tick at speed-derived intervals, and is managed by FleetMovementEngine with spatial pathfinding. Actions are progress-based with action_time from abilities. The two-engine split (FleetMovementEngine + ActionExecutionEngine) is the right design.

### ColonizeValidator vs SuperweaponValidator API differences -- PARTIALLY JUSTIFIED
ColonizeValidator has a complex multi-concern API (location check, pod matching, chain exhaustion) because colonization genuinely has more preconditions. SuperweaponValidator having separate `validate_X()` methods per weapon type is reasonable because each weapon has unique preconditions (system has stars, warp link exists, etc.). However, the lack of a common base protocol is unjustified.

### TRANSFER target dict vs other order targets -- JUSTIFIED
Transfer orders need a parameter dict (direction, cargo_type, amount, planet_id, species_id) because they represent a compound operation. This is genuinely different from MOVE (needs a HexCoord) or COLONIZE (needs a Planet). The heterogeneity in target types is semantically justified -- but the serialization approach (instanceof cascade) is not.

### Instant orders (JOIN_FLEET) vs tick-based actions -- JUSTIFIED
JOIN_FLEET needs to be processed every tick without progress tracking because fleet merging is instantaneous when co-located. Other actions need progress tracking. The separate `process_instant_orders()` path is correct.

### BUILD order special handling -- JUSTIFIED
BUILD orders are persistent (they last until the construction queue empties) and are managed by ProductionEngine, not ActionExecutionEngine. This is fundamentally different from one-shot actions. The carve-out for BUILD in both engines is correct, though the duplicate auto-pop check (AU-009) should be cleaned up.

### Superweapon-specific processors -- PARTIALLY JUSTIFIED
Each superweapon has unique galaxy-altering effects (destroy planet, destroy star system, create warp link, etc.) that genuinely require different implementations. However, the boilerplate around them (find ship, remove ship, pop order, check empty) is common and should be extracted, while preserving the unique effect logic.

---

## 6. Unification Opportunity Details

### Could there be a unified OrderExecutor interface/protocol?
**Yes.** An `IOrderExecutor` protocol with `execute(fleet, empire, galaxy, **context) -> OrderExecutionResult` would replace the if/elif chain in `process_end_turn_orders()`. Each order type gets a registered executor. The `OrderExecutionResult` dataclass would include `success`, `fleet_consumed`, and `message` (generalizing `ColonizeResult`, `TransferResult`, `JoinFleetResult`, and `SuperweaponResult`).

### Could validators use a common base pattern?
**Partially.** A common `validate(galaxy, fleet, order, component_registry) -> ValidationResult` signature would work for most validators. Colonize and Transfer need extra parameters (target_planet, cargo_type, direction), but these could be extracted from the order's target. The key unification: all validators should be called at execution time, not just some.

### Could order chaining (MOVE + action) be standardized?
**Yes.** The `_setup_mission_move()` helper in superweapon_command_handlers.py is the right idea but should be promoted to a shared utility used by all mission handlers (including ColonizeMission, Transfer, and Warp). The pre-action hooks (like population loading for colonize) can be callbacks.

### Could serialization be simplified with a discriminated target type?
**Yes, and this should be the highest priority.** A tagged union approach where `FleetOrder.target` is always a typed object with its own `to_dict()`/`from_dict()` would eliminate the 7-way isinstance cascade. The `type` field already partially exists in the serialized format (`{'type': 'transfer', ...}`, `{'type': 'fleet_ref', ...}`) but isn't used consistently.

### Could the dispatch in fleet_order_processor be replaced with a registry pattern?
**Yes.** It should mirror `CommandHandlerRegistry`. An `OrderExecutorRegistry` with `register(OrderType, IOrderExecutor)` and `dispatch(order_type, fleet, empire, galaxy, ...) -> result` would make `process_end_turn_orders()` a 5-line method.
