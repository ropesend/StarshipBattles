# Execution Path Analysis Report

## Summary
- Total issues found: 10
- Critical: 1, Major: 4, Minor: 3, Info: 2

---

## Findings

### 1. Execution Path Fragmentation

The system has **4 distinct execution paths**, not 3:

| Path | Engine | Order Types | Timing |
|------|--------|-------------|--------|
| **Instant** | `FleetOrderProcessor.process_instant_orders()` | JOIN_FLEET (co-located) | Every tick, Phase 1 |
| **Movement** | `FleetMovementEngine` | MOVE, MOVE_TO_FLEET, WARP | Speed-gated ticks, Phase 2-3 |
| **Action (tick-based)** | `ActionExecutionEngine` | COLONIZE, TRANSFER, LOAD/UNLOAD_POPULATION, all superweapons, JOIN_FLEET | Speed-gated ticks, Phase 1.5 |
| **Persistent** | `ProductionEngine` (+ ActionExecutionEngine BUILD auto-pop) | BUILD | Phase 0e + tick-gated auto-pop |

The three-way split between Instant, Movement, and Action is well-motivated by genuine behavioral differences. Movement needs pathfinding and hex-by-hex traversal. Actions need progress tracking over time. Instant orders (JOIN_FLEET when co-located) are fire-and-forget. This separation is architecturally sound.

---

#### CRITICAL: JOIN_FLEET Processed in Two Execution Paths Simultaneously
**ID:** EP-001
**Location:** `game/strategy/data/fleet.py:49-61`, `game/strategy/engine/fleet_order_processor.py:634-636`, `game/strategy/engine/fleet_order_processor.py:677-711`
**Issue:** `JOIN_FLEET` is listed in `ACTION_ORDER_TYPES` (line 54 of `fleet.py`) AND is handled by `process_instant_orders()` (line 698). This means during each tick:
1. Phase 1: `process_instant_orders()` scans for JOIN_FLEET orders on co-located fleets and merges them.
2. Phase 1.5: `ActionExecutionEngine` also processes JOIN_FLEET because it's in `ACTION_ORDER_TYPES`. It increments `execution_progress` and eventually calls `process_end_turn_orders()`, which dispatches to `process_join_fleet()`.

A fleet with a JOIN_FLEET order that is already co-located gets processed in Phase 1 (instant merge), so the order is consumed before Phase 1.5. But if the fleet is NOT co-located and somehow arrives at the target through some other mechanism, both paths could theoretically attempt to process it. More practically, the ActionExecutionEngine path will increment `execution_progress` on a JOIN_FLEET order every speed-gated tick, and once `execution_progress >= action_time` (default 1), it will call `process_end_turn_orders()` which calls `process_join_fleet()` -- but this only merges if co-located, otherwise it **cancels the order** (line 168: `fleet.pop_order()`).

This means: a JOIN_FLEET fleet that isn't co-located will have its order **cancelled by the action engine on the very first speed-gated tick** (because action_time defaults to 1 for JOIN_FLEET, and there's no ability mapping for it in `ActionTimeResolver`). The fleet will lose its JOIN_FLEET order before it can be moved to the target. This is a bug: typically JOIN_FLEET is preceded by a MOVE_TO_FLEET order in the queue (see `command_handlers.py:268-269`), so it only becomes the current order after arrival. But if someone issues JOIN_FLEET directly without a preceding MOVE_TO_FLEET, the action engine will kill it.

**Impact:** Dual processing of the same order type across two execution paths creates confusion, potential bugs with premature cancellation, and makes it hard to reason about order behavior.
**Recommendation:** Remove `OrderType.JOIN_FLEET` from `ACTION_ORDER_TYPES`. JOIN_FLEET should only be handled by `process_instant_orders()` in Phase 1. It is inherently an instant action (merge when co-located). If the fleet isn't co-located, it should simply wait until the preceding MOVE_TO_FLEET completes.
**Effort:** Simple

---

#### MAJOR: `complete_order()` and `cancel_order()` Are Dead Code in Production
**ID:** EP-002
**Location:** `game/strategy/engine/fleet_order_processor.py:76-114`
**Issue:** `FleetOrderProcessor` defines centralized `complete_order()` and `cancel_order()` methods (lines 76-114), but **no production code calls them**. Every execution path calls `fleet.pop_order()` directly instead:
- `fleet_order_processor.py`: 14 direct `fleet.pop_order()` calls
- `superweapon_order_processor.py`: 14 direct `fleet.pop_order()` calls
- `action_execution_engine.py`: 1 direct `fleet.pop_order()` call
- `fleet_navigation_service.py`: 3 direct `fleet.pop_order()` calls

Only test files use `complete_order()` and `cancel_order()`. The `cancel_all_orders()` method is only used in one test.

**Impact:** The centralized lifecycle methods exist but are universally bypassed. This means there is no single point for order completion/cancellation logging, metrics, or hooks. The stated design goal of "pop_order in single location" (docstring line 10) is not achieved.
**Recommendation:** Either (a) enforce use of `complete_order()`/`cancel_order()` across all callers by removing direct `fleet.pop_order()` calls, or (b) delete these dead methods and accept that `fleet.pop_order()` is the canonical completion mechanism.
**Effort:** Medium

---

#### MAJOR: SuperweaponOrderProcessor Instantiated Fresh on Every Dispatch
**ID:** EP-003
**Location:** `game/strategy/engine/fleet_order_processor.py:654`
**Issue:** In `process_end_turn_orders()`, a new `SuperweaponOrderProcessor()` is created every time a superweapon order is dispatched:
```python
proc = SuperweaponOrderProcessor()
```
This happens inside the per-fleet processing loop called by `ActionExecutionEngine` every speed-gated tick. For a fleet with a superweapon order at speed 5, this instantiation happens up to 5 times per turn (once per speed-gated tick while progress is still building).

**Impact:** Unnecessary object churn. While `SuperweaponOrderProcessor.__init__` is trivially cheap (just `pass`), this pattern violates the dependency injection pattern used everywhere else in the codebase. The TurnEngine injects all its sub-engines; the ActionExecutionEngine receives its order processor via DI; but the SuperweaponOrderProcessor is hard-created inline.
**Recommendation:** Inject `SuperweaponOrderProcessor` into `FleetOrderProcessor` at construction time, matching the DI pattern used by all other engines. This also enables mocking for tests.
**Effort:** Simple

---

#### MAJOR: Duplicate BUILD Order Auto-Pop Logic
**ID:** EP-004
**Location:** `game/strategy/engine/action_execution_engine.py:140-144`, `game/strategy/engine/fleet_order_processor.py:617-625`
**Issue:** BUILD order auto-completion (when construction queue is empty) is implemented in two places:
1. `ActionExecutionEngine._process_fleet_action_tick()` lines 140-144: checks `if not fleet.construction_queue` and calls `fleet.pop_order()`.
2. `FleetOrderProcessor.process_end_turn_orders()` lines 617-625: identical check and `fleet.pop_order()`.

The ActionExecutionEngine path is the one that actually fires during gameplay (it checks BUILD before checking `ACTION_ORDER_TYPES` and returns `None`). The FleetOrderProcessor path can only be reached if someone calls `process_end_turn_orders()` directly with a BUILD order, which shouldn't happen since ActionExecutionEngine skips BUILD before delegating.

**Impact:** Duplicated logic that can diverge. If the auto-pop condition changes (e.g., BUILD should persist for N ticks after queue empties), it would need to be updated in two places.
**Recommendation:** Remove the BUILD handling from `process_end_turn_orders()` since it's unreachable via the normal ActionExecutionEngine flow. BUILD is a persistent order managed by ProductionEngine; its auto-pop belongs in one place only.
**Effort:** Simple

---

#### MAJOR: Inconsistent Error Handling Across Execution Paths
**ID:** EP-005
**Location:** Multiple files
**Issue:** Each execution path handles errors (invalid orders, missing targets, failed validation) differently:

| Path | Error Pattern | Example |
|------|---------------|---------|
| **Instant** (process_instant_orders) | Silently skips invalid targets | Line 701: just checks `target_fleet is not None` |
| **Movement** (FleetMovementEngine) | `fleet.clear_orders()` - cancels ALL orders | Lines 152, 164, 169 |
| **Action** (process_end_turn_orders) | `fleet.pop_order()` - cancels only current | Lines 157, 168, 214, etc. |
| **Superweapon** (SuperweaponOrderProcessor) | `fleet.pop_order()` + returns failure result | Lines 81, 92, 167, etc. |

The movement path is notably aggressive: when a fleet runs out of fuel or can't warp, it calls `fleet.clear_orders()` which destroys the entire order queue. Compare with the action path which only pops the failing order, preserving subsequent orders in the queue.

**Impact:** A MOVE order failing (e.g., out of fuel) destroys all queued orders including a subsequent COLONIZE or TRANSFER. This is inconsistent with how action order failures work, where only the failed order is removed.
**Recommendation:** Standardize error handling: failures should cancel only the current order (`pop_order()`) unless there's a specific reason to clear the entire queue. If "stranded with no fuel" truly means "all orders invalid", document this policy explicitly.
**Effort:** Medium

---

#### MINOR: `process_end_turn_orders` Name Is Misleading
**ID:** EP-006
**Location:** `game/strategy/engine/fleet_order_processor.py:585`
**Issue:** The method is named `process_end_turn_orders` but is called during ticks by `ActionExecutionEngine`, not at end-of-turn. The docstring even acknowledges this: "Name retained for compatibility" (line 600). The interface `IOrderProcessor` also preserves this misleading name.
**Impact:** Developers reading the code will be confused about when this method runs. The name implies it fires once at end-of-turn; in reality it fires per-fleet during each speed-gated tick.
**Recommendation:** Rename to `execute_completed_action()` or `dispatch_action_order()` to reflect its actual role: dispatching a single fleet's action order after the ActionExecutionEngine determines it should complete.
**Effort:** Simple (but requires updating interface, implementation, and all call sites)

---

#### MINOR: ActionTimeResolver Returns 0 for Movement Orders But They Never Reach It
**ID:** EP-007
**Location:** `game/strategy/services/action_time_resolver.py:85-87`
**Issue:** `ActionTimeResolver.resolve_action_time()` has a special case returning `0` for movement orders (MOVE, MOVE_TO_FLEET). But movement orders are filtered out by `ActionExecutionEngine` at line 136 (`if order.type in MOVEMENT_ORDER_TYPES: return None`) before `resolve_action_time` is ever called. The fallback in ActionTimeResolver is dead code.
**Impact:** Minor confusion. The code suggests movement orders might flow through the action time resolution, but they never do.
**Recommendation:** Remove the movement order check from `ActionTimeResolver.resolve_action_time()` and add a comment or assertion that it should never receive movement orders.
**Effort:** Simple

---

#### MINOR: WARP Order Type Not in ActionTimeResolver's Movement Set
**ID:** EP-008
**Location:** `game/strategy/services/action_time_resolver.py:47-48`, `game/strategy/data/fleet.py:41-45`
**Issue:** `_get_movement_order_types()` in ActionTimeResolver returns `{OrderType.MOVE, OrderType.MOVE_TO_FLEET}` but the canonical `MOVEMENT_ORDER_TYPES` in `fleet.py` includes `OrderType.WARP` as well. This mismatch means if a WARP order somehow reached `ActionTimeResolver`, it would get `action_time=1` instead of `0`.

In practice, WARP orders are filtered by `ActionExecutionEngine` using the correct `MOVEMENT_ORDER_TYPES` frozenset (which includes WARP), so this discrepancy is currently harmless.

**Impact:** Maintenance risk. Two separate definitions of "movement order types" that can diverge.
**Recommendation:** Delete `_get_movement_order_types()` and import the canonical `MOVEMENT_ORDER_TYPES` from `fleet.py` instead.
**Effort:** Simple

---

#### INFO: Turn Engine Phase Ordering Is Well-Documented
**ID:** EP-009
**Location:** `game/strategy/engine/turn_engine.py:11-24`, `game/strategy/engine/turn_engine.py:347-359`
**Issue:** (Positive finding) The TurnEngine has excellent documentation of phase ordering in both the module docstring (lines 11-24) and the `_process_tick` docstring (lines 347-359). The phase numbering scheme (0, 0a-0f, 1, 1.5, 2, 3, 4) clearly communicates the execution order. The code directly follows this documented order with labeled comments for each phase.

The phase ordering is logically sound:
- Economic phases (0-0f) run first, so resource state is current
- Instant orders (Phase 1) run before actions, enabling same-tick JOIN_FLEET after arrival
- Actions (Phase 1.5) run before movement, so action progress ticks before fleet can move
- Movement (Phase 2-3) is two-phase (collect then apply), enabling simultaneous movement
- Combat (Phase 4) resolves after all movement, catching newly co-located fleets

**Impact:** Positive. Good documentation reduces onboarding time and bug risk.
**Recommendation:** None needed. This is a model for how phase-based systems should be documented.
**Effort:** N/A

---

#### INFO: Superweapon Processor Separation Is Justified
**ID:** EP-010
**Location:** `game/strategy/engine/superweapon_order_processor.py`
**Issue:** (Positive finding) The SuperweaponOrderProcessor handles 6 distinct superweapon types, each with unique galaxy-mutating logic (planet destruction, star destruction, warp point creation/removal, Dyson Sphere construction, self-destruct). The file is 592 lines, and the logic is domain-specific (physics calculations, galaxy topology mutations, cross-empire effects).

The separation from FleetOrderProcessor is justified because:
1. Superweapon logic involves galaxy-level mutations (unregister planets, modify star systems, create new entities) that are fundamentally different from simple order completion
2. Each superweapon has unique validation, execution, and cleanup steps
3. The 592-line file would bloat FleetOrderProcessor significantly if inlined
4. The superweapon processor follows the same patterns as FleetOrderProcessor (pop_order on failure, return result dataclass, log events)

**Impact:** Positive separation of concerns.
**Recommendation:** The only improvement is EP-003 (inject rather than inline-create). The separation itself is clean.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **EP-001 (CRITICAL):** JOIN_FLEET in both `ACTION_ORDER_TYPES` and `process_instant_orders()` creates dual processing with premature cancellation risk. Fix: remove from `ACTION_ORDER_TYPES`.

2. **EP-002 (MAJOR):** `complete_order()`/`cancel_order()` are dead code; every caller uses `fleet.pop_order()` directly, defeating the centralized lifecycle design. Fix: enforce use or delete dead methods.

3. **EP-005 (MAJOR):** Movement failures call `clear_orders()` (destroying entire queue) while action failures call `pop_order()` (preserving queue). This inconsistency punishes movement-related failures disproportionately. Fix: standardize to `pop_order()` with documented exceptions.

4. **EP-004 (MAJOR):** BUILD order auto-pop logic duplicated in ActionExecutionEngine and FleetOrderProcessor. Fix: remove unreachable duplicate in FleetOrderProcessor.

5. **EP-003 (MAJOR):** SuperweaponOrderProcessor created fresh every dispatch, bypassing the DI pattern used by all other engines. Fix: inject at construction time.
