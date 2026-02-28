# Review Report: 2026-02-27_153151_general_fleet-order-systems

## Metadata
- **Date:** 2026-02-27 15:31
- **Type:** General Review (focused deep-dive)
- **Description:** Fleet order systems — how orders are given, stored, and executed
- **Agents Used:** 2

## Executive Summary
- **Total Findings:** 22
- **Critical:** 2 | **Major:** 8 | **Minor:** 8 | **Info:** 4
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: JOIN_FLEET Processed in Two Execution Paths Simultaneously
**ID:** EP-001
**Agent:** Execution Paths
**Location:** `game/strategy/data/fleet.py:49-61`
**Effort:** Simple

**ID:** EP-001
**Location:** `game/strategy/data/fleet.py:49-61`, `game/strategy/engine/fleet_order_processor.py:634-636`, `game/strategy/engine/fleet_order_processor.py:677-711`
**Issue:** `JOIN_FLEET` is listed in `ACTION_ORDER_TYPES` (line 54 of `fleet.py`) AND is handled by `process_instant_orders()` (line 698). This means during each tick:
1. Phase 1: `process_instant_orders()` scans for JOIN_FLEET orders on co-located fleets and merges them.
2. Phase 1.5: `ActionExecutionEngine` also proce...

---

### 2. CRITICAL: Unresolved `_fleet_ref` and `_planet_ref` Markers After Deserialization
**ID:** ODM-001
**Agent:** Order Data Model
**Location:** `game/strategy/data/fleet.py:454-462`
**Effort:** Medium

**ID:** ODM-001
**Location:** `game/strategy/data/fleet.py:454-462`
**Issue:** When `Fleet.from_dict()` deserializes orders with `fleet_ref` or `planet_ref` targets, it stores temporary marker dicts (`{'_fleet_ref': id}` and `{'_planet_ref': id}`) with the expectation that "later resolution" will replace them with actual Fleet/Planet objects. However, a codebase-wide search reveals **no resolution pass exists**. The `game_session.py` load path restores empires and galaxy but never iterates fleet...

---

### 3. MAJOR: `complete_order()` and `cancel_order()` Are Dead Code in Production
**ID:** EP-002
**Agent:** Execution Paths
**Location:** `game/strategy/engine/fleet_order_processor.py:76-114`
**Effort:** Medium

**ID:** EP-002
**Location:** `game/strategy/engine/fleet_order_processor.py:76-114`
**Issue:** `FleetOrderProcessor` defines centralized `complete_order()` and `cancel_order()` methods (lines 76-114), but **no production code calls them**. Every execution path calls `fleet.pop_order()` directly instead:
- `fleet_order_processor.py`: 14 direct `fleet.pop_order()` calls
- `superweapon_order_processor.py`: 14 direct `fleet.pop_order()` calls
- `action_execution_engine.py`: 1 direct `fleet.pop_order...

---

### 4. MAJOR: SuperweaponOrderProcessor Instantiated Fresh on Every Dispatch
**ID:** EP-003
**Agent:** Execution Paths
**Location:** `game/strategy/engine/fleet_order_processor.py:654`
**Effort:** Simple

**ID:** EP-003
**Location:** `game/strategy/engine/fleet_order_processor.py:654`
**Issue:** In `process_end_turn_orders()`, a new `SuperweaponOrderProcessor()` is created every time a superweapon order is dispatched:
```python
proc = SuperweaponOrderProcessor()
```
This happens inside the per-fleet processing loop called by `ActionExecutionEngine` every speed-gated tick. For a fleet with a superweapon order at speed 5, this instantiation happens up to 5 times per turn (once per speed-gated tick ...

---

### 5. MAJOR: Duplicate BUILD Order Auto-Pop Logic
**ID:** EP-004
**Agent:** Execution Paths
**Location:** `game/strategy/engine/action_execution_engine.py:140-144`
**Effort:** Simple

**ID:** EP-004
**Location:** `game/strategy/engine/action_execution_engine.py:140-144`, `game/strategy/engine/fleet_order_processor.py:617-625`
**Issue:** BUILD order auto-completion (when construction queue is empty) is implemented in two places:
1. `ActionExecutionEngine._process_fleet_action_tick()` lines 140-144: checks `if not fleet.construction_queue` and calls `fleet.pop_order()`.
2. `FleetOrderProcessor.process_end_turn_orders()` lines 617-625: identical check and `fleet.pop_order()`.

T...

---

### 6. MAJOR: Inconsistent Error Handling Across Execution Paths
**ID:** EP-005
**Agent:** Execution Paths
**Location:** `Unknown`
**Effort:** Medium

**ID:** EP-005
**Location:** Multiple files
**Issue:** Each execution path handles errors (invalid orders, missing targets, failed validation) differently:

| Path | Error Pattern | Example |
|------|---------------|---------|
| **Instant** (process_instant_orders) | Silently skips invalid targets | Line 701: just checks `target_fleet is not None` |
| **Movement** (FleetMovementEngine) | `fleet.clear_orders()` - cancels ALL orders | Lines 152, 164, 169 |
| **Action** (process_end_turn_orders) | ...

---

### 7. MAJOR: Untyped Polymorphic `target` Field - 8+ Distinct Runtime Types
**ID:** ODM-002
**Agent:** Order Data Model
**Location:** `game/strategy/data/fleet.py:64-67`
**Effort:** Complex

**ID:** ODM-002
**Location:** `game/strategy/data/fleet.py:64-67`
**Issue:** `FleetOrder.target` is typed as `Any` (no annotation) and holds at least 8 different runtime types depending on `OrderType`:
1. `HexCoord` (MOVE, WARP)
2. `Planet` object (COLONIZE, IMPLODE_PLANET)
3. `Fleet` object (MOVE_TO_FLEET, JOIN_FLEET)
4. `dict` with transfer params (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION)
5. `dict` with warp params (OPEN_WARP_POINT)
6. `str` (CLOSE_WARP_POINT - warp_point_destination_id)
...

---

### 8. MAJOR: Planet Target Serializes as Full Planet Dict - Deserialization Silently Drops It
**ID:** ODM-003
**Agent:** Order Data Model
**Location:** `game/strategy/data/fleet.py:97-99`
**Effort:** Simple

**ID:** ODM-003
**Location:** `game/strategy/data/fleet.py:97-99` (to_dict), `game/strategy/data/fleet.py:450-471` (from_dict)
**Issue:** In `to_dict()`, when `target` is a `Planet` object (for COLONIZE orders), it serializes the entire planet via `self.target.to_dict()`, producing a dict with keys like `id`, `name`, `location`, `mass`, `radius`, etc. However, in `from_dict()`, this dict does not match any of the recognized patterns:
- It has no `q`/`r` keys (not HexCoord)
- It has no `type` key...

---

### 9. MAJOR: `from_dict()` Silently Drops Unrecognized Target Formats
**ID:** ODM-007
**Agent:** Order Data Model
**Location:** `game/strategy/data/fleet.py:450-471`
**Effort:** Simple

**ID:** ODM-007
**Location:** `game/strategy/data/fleet.py:450-471`
**Issue:** When `target_data` is a dict that doesn't match any recognized pattern (no `q`/`r`, no `type` key), the target remains `None`. This includes:
- Full Planet dicts from `to_dict()` (see ODM-003)
- Any future target format that's added to `to_dict()` but forgotten in `from_dict()`
- Corrupted data that happens to be a dict

There is no warning logged and no exception raised. The order is silently created with `target=Non...

---

### 10. MAJOR: `ClearOrdersCommandHandler` Bypasses `Fleet.clear_orders()` Method
**ID:** ODM-011
**Agent:** Order Data Model
**Location:** `game/strategy/engine/command_handlers.py:386-388`
**Effort:** Simple

**ID:** ODM-011
**Location:** `game/strategy/engine/command_handlers.py:386-388`
**Issue:** The `ClearOrdersCommandHandler.execute()` directly sets `fleet.orders = []` and `fleet.path = []` instead of calling `fleet.clear_orders()`. The `clear_orders()` method (line 332) does `self.orders.clear()` and `self.path = []`. While functionally equivalent, directly setting `fleet.orders` to a new list bypasses any future logic added to `clear_orders()` (e.g., event logging, cleanup hooks, execution_pro...

---


## Findings by Severity

### Critical (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| EP-001 | JOIN_FLEET Processed in Two Execution Pa | `game/strategy/data/fleet.py:49` | Simple |
| ODM-001 | Unresolved `_fleet_ref` and `_planet_ref | `game/strategy/data/fleet.py:45` | Medium |

### Major (8)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| EP-002 | `complete_order()` and `cancel_order()`  | `game/strategy/engine/fleet_ord` | Medium |
| EP-003 | SuperweaponOrderProcessor Instantiated F | `game/strategy/engine/fleet_ord` | Simple |
| EP-004 | Duplicate BUILD Order Auto-Pop Logic | `game/strategy/engine/action_ex` | Simple |
| EP-005 | Inconsistent Error Handling Across Execu | `Unknown` | Medium |
| ODM-002 | Untyped Polymorphic `target` Field - 8+  | `game/strategy/data/fleet.py:64` | Complex |
| ODM-003 | Planet Target Serializes as Full Planet  | `game/strategy/data/fleet.py:97` | Simple |
| ODM-007 | `from_dict()` Silently Drops Unrecognize | `game/strategy/data/fleet.py:45` | Simple |
| ODM-011 | `ClearOrdersCommandHandler` Bypasses `Fl | `game/strategy/engine/command_h` | Simple |

### Minor (8)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| EP-006 | `process_end_turn_orders` Name Is Mislea | `game/strategy/engine/fleet_ord` | Simple |
| EP-007 | ActionTimeResolver Returns 0 for Movemen | `game/strategy/services/action_` | Simple |
| EP-008 | WARP Order Type Not in ActionTimeResolve | `game/strategy/services/action_` | Simple |
| ODM-004 | Serialization Uses Both Order-Type and i | `game/strategy/data/fleet.py:81` | Medium |
| ODM-005 | BUILD OrderType Falls Outside Both Categ | `game/strategy/data/fleet.py:41` | Simple |
| ODM-008 | `CLOSE_WARP_POINT` Target Is a Raw Strin | `game/strategy/engine/superweap` | Simple |
| ODM-009 | Command and FleetOrder Carry Overlapping | `game/strategy/engine/commands.` | N |
| ODM-012 | `pop_order()` Uses `list.pop(0)` - O(n)  | `game/strategy/data/fleet.py:34` | Simple |

### Info (4)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| EP-009 | Turn Engine Phase Ordering Is Well-Docum | `game/strategy/engine/turn_engi` | N |
| EP-010 | Superweapon Processor Separation Is Just | `game/strategy/engine/superweap` | N |
| ODM-006 | Categorization Is Used Consistently Acro | `Unknown` | N |
| ODM-010 | Command -> FleetOrder Mapping Is Clean a | `game/strategy/engine/command_h` | N |


## Agent Reports

- [Architecture Unification Report](findings/architecture_unification_report.md)
- [Command Pipeline Report](findings/command_pipeline_report.md)
- [Execution Paths Report](findings/execution_paths_report.md)
- [Order Data Model Report](findings/order_data_model_report.md)
- [Validation Consistency Report](findings/validation_consistency_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 22 |
| Critical | 2 |
| Major | 8 |
| Minor | 8 |
| Info | 4 |
| Agents Used | 2 |

---
*Report generated: 2026-02-27 17:12*
