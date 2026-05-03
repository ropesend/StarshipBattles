# Order Data Model Analysis Report

## Summary
- Total issues found: 12
- Critical: 1, Major: 4, Minor: 5, Info: 2

## Findings

---

### 1. FleetOrder.target Polymorphism

#### CRITICAL: Unresolved `_fleet_ref` and `_planet_ref` Markers After Deserialization
**ID:** ODM-001
**Location:** `game/strategy/data/fleet.py:454-462`
**Issue:** When `Fleet.from_dict()` deserializes orders with `fleet_ref` or `planet_ref` targets, it stores temporary marker dicts (`{'_fleet_ref': id}` and `{'_planet_ref': id}`) with the expectation that "later resolution" will replace them with actual Fleet/Planet objects. However, a codebase-wide search reveals **no resolution pass exists**. The `game_session.py` load path restores empires and galaxy but never iterates fleet orders to resolve these markers. If a saved game contains a `MOVE_TO_FLEET`, `JOIN_FLEET`, or `IMPLODE_PLANET` order, the order's `.target` will remain as a dict with `_fleet_ref`/`_planet_ref` keys instead of an actual Fleet/Planet object.
**Impact:** After loading a save, any fleet with an in-progress `JOIN_FLEET` or `MOVE_TO_FLEET` order will fail at runtime when the fleet movement or order processor tries to access `order.target.location` (AttributeError on a dict). Similarly, `IMPLODE_PLANET` orders after load will fail when the superweapon processor tries to access `order.target.id` or `order.target.name`. This is a data corruption bug that silently persists across save/load cycles.
**Recommendation:** Add a `resolve_order_references(galaxy, all_fleets)` pass in `GameSession._load_game()` that iterates all fleet orders and replaces `{'_fleet_ref': id}` with the actual Fleet object and `{'_planet_ref': id}` with the actual Planet object. Alternatively, make `from_dict()` accept a resolution context.
**Effort:** Medium

#### MAJOR: Untyped Polymorphic `target` Field - 8+ Distinct Runtime Types
**ID:** ODM-002
**Location:** `game/strategy/data/fleet.py:64-67`
**Issue:** `FleetOrder.target` is typed as `Any` (no annotation) and holds at least 8 different runtime types depending on `OrderType`:
1. `HexCoord` (MOVE, WARP)
2. `Planet` object (COLONIZE, IMPLODE_PLANET)
3. `Fleet` object (MOVE_TO_FLEET, JOIN_FLEET)
4. `dict` with transfer params (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION)
5. `dict` with warp params (OPEN_WARP_POINT)
6. `str` (CLOSE_WARP_POINT - warp_point_destination_id)
7. `list[int]` (SELF_DESTRUCT - ship_ids)
8. `None` (STELLERATE_STAR, CREATE_DYSON_SPHERE, BUILD)
9. `dict` with `_fleet_ref`/`_planet_ref` markers (post-deserialization)

There is no type annotation, no discriminated union, and no runtime validation that the target matches the order type. Consumers must use `isinstance()` checks or implicit knowledge to extract data.
**Impact:** Every consumer of `FleetOrder.target` must independently know the expected type for each `OrderType`. This is error-prone and makes refactoring risky. The UI display code (`strategy_detail_fmt.py:295-327`) handles only a subset of types, and the serialization code (`to_dict`) uses a complex if/elif chain combining type checks with `isinstance()` and order-type checks.
**Recommendation:** Introduce a tagged union or per-order-type target dataclasses. For example:
```python
@dataclass
class MoveTarget:
    hex: HexCoord

@dataclass
class TransferTarget:
    direction: str
    cargo_type: str
    amount: int
    planet_id: Optional[int]
    species_id: Optional[str]
```
Each order type gets a specific target type, enforced at construction time. This eliminates `isinstance` chains and makes serialization trivial.
**Effort:** Complex

#### MAJOR: Planet Target Serializes as Full Planet Dict - Deserialization Silently Drops It
**ID:** ODM-003
**Location:** `game/strategy/data/fleet.py:97-99` (to_dict), `game/strategy/data/fleet.py:450-471` (from_dict)
**Issue:** In `to_dict()`, when `target` is a `Planet` object (for COLONIZE orders), it serializes the entire planet via `self.target.to_dict()`, producing a dict with keys like `id`, `name`, `location`, `mass`, `radius`, etc. However, in `from_dict()`, this dict does not match any of the recognized patterns:
- It has no `q`/`r` keys (not HexCoord)
- It has no `type` key (not fleet_ref, transfer, planet_ref, ship_id_list, warp_params, or raw)

The deserialization falls through all conditions and `target` remains `None` (the initial value). The COLONIZE order is restored but **its planet target is silently lost**.
**Impact:** After save/load, any queued COLONIZE order targeting a specific planet will revert to "colonize any planet" behavior (target=None), which could colonize the wrong planet. This is a save/load data loss bug.
**Recommendation:** In `to_dict()`, serialize COLONIZE planet targets consistently using the `planet_ref` format: `{'type': 'planet_ref', 'id': self.target.id}`. Then `from_dict()` already handles `planet_ref` and stores `{'_planet_ref': id}` which (once ODM-001 is fixed) would be resolved to the actual Planet object. Remove the full `self.target.to_dict()` serialization path.
**Effort:** Simple

#### MINOR: Serialization Uses Both Order-Type and isinstance Checks
**ID:** ODM-004
**Location:** `game/strategy/data/fleet.py:81-104`
**Issue:** The `to_dict()` method uses a hybrid approach: some branches check `self.type` (e.g., `self.type in (OrderType.TRANSFER, ...)`), others check `isinstance(self.target, ...)`, and some check both (e.g., `self.type == OrderType.IMPLODE_PLANET and isinstance(self.target, Planet)`). This mixed strategy creates ambiguity about what determines the serialization path.
**Impact:** Maintenance burden. When adding a new order type, a developer must understand the precedence of these conditions. The HexCoord isinstance check at line 94 is a catch-all that could silently serialize the wrong format if an order type is missing from the explicit checks above it.
**Recommendation:** Serialize based solely on `self.type` using a dictionary dispatch or match statement. Each order type should have exactly one serialization path.
**Effort:** Medium

---

### 2. OrderType Categorization

#### MINOR: BUILD OrderType Falls Outside Both Category Sets
**ID:** ODM-005
**Location:** `game/strategy/data/fleet.py:41-61`
**Issue:** The `OrderType` enum has 16 values. `MOVEMENT_ORDER_TYPES` contains 3 (MOVE, MOVE_TO_FLEET, WARP) and `ACTION_ORDER_TYPES` contains 11. `BUILD` is in neither set. This is intentional and documented (comment on line 48: "Excludes BUILD"), and it's handled explicitly in both `ActionExecutionEngine` (line 140) and `FleetMovementEngine` (line 240). However, there is no compile-time or runtime guarantee that all 16 values are categorized.
**Impact:** If a new OrderType is added and not placed in either set, it would silently be ignored by both engines. The `ActionExecutionEngine` has a defensive check at line 148 (`if order.type not in ACTION_ORDER_TYPES: return None`) but this means uncategorized orders are silently dropped rather than flagged.
**Recommendation:** Add a runtime assertion or test that `MOVEMENT_ORDER_TYPES | ACTION_ORDER_TYPES | {OrderType.BUILD}` covers all OrderType values. This exists partially in `test_action_execution_engine.py:506` but should be strengthened to an exhaustive check.
**Effort:** Simple

#### INFO: Categorization Is Used Consistently Across the Codebase
**ID:** ODM-006
**Location:** Multiple files
**Issue:** The `MOVEMENT_ORDER_TYPES` and `ACTION_ORDER_TYPES` frozensets are used in exactly the right places:
- `FleetMovementEngine.collect_movements()` skips `ACTION_ORDER_TYPES` and `BUILD`
- `ActionExecutionEngine._process_fleet_action_tick()` skips `MOVEMENT_ORDER_TYPES` and `BUILD`
- `FleetNavigationService` uses both sets for path projection
No inconsistencies found in categorization usage.
**Impact:** None - this is working correctly.
**Recommendation:** No action needed.
**Effort:** N/A

---

### 3. Serialization Complexity

#### MAJOR: `from_dict()` Silently Drops Unrecognized Target Formats
**ID:** ODM-007
**Location:** `game/strategy/data/fleet.py:450-471`
**Issue:** When `target_data` is a dict that doesn't match any recognized pattern (no `q`/`r`, no `type` key), the target remains `None`. This includes:
- Full Planet dicts from `to_dict()` (see ODM-003)
- Any future target format that's added to `to_dict()` but forgotten in `from_dict()`
- Corrupted data that happens to be a dict

There is no warning logged and no exception raised. The order is silently created with `target=None`.
**Impact:** Silent data loss during deserialization. Saves appear to load successfully but orders may have lost their targets. This can cause unexpected behavior during gameplay.
**Recommendation:** Add a catch-all `else` branch that logs a warning: `logger.warning(f"Fleet {data['id']}: order[{i}] has unrecognized target format: {target_data}")`. Also consider setting `target = target_data` as a passthrough to avoid data loss, or raise an exception.
**Effort:** Simple

#### MINOR: `CLOSE_WARP_POINT` Target Is a Raw String - Inconsistent With Other Order Types
**ID:** ODM-008
**Location:** `game/strategy/engine/superweapon_command_handlers.py:128`, `game/strategy/data/fleet.py:103-104`
**Issue:** The `CLOSE_WARP_POINT` order stores its target as a plain string (warp_point_destination_id). In `to_dict()`, this falls through to the raw fallback at line 104: `target_data = {'type': 'raw', 'value': str(self.target)}`. While this works, it means deserialization restores a string, but the code relies on the `raw` type handler which was intended as a fallback for unexpected types.
**Impact:** Minor. The serialization round-trip works, but it's fragile. If the raw handler is ever removed or changed, CLOSE_WARP_POINT orders break. The inconsistency also makes the code harder to reason about - a developer seeing `raw` type in saved data cannot tell what order type produced it.
**Recommendation:** Add a dedicated serialization format for CLOSE_WARP_POINT: `{'type': 'warp_dest_ref', 'id': self.target}`. Alternatively, make the command handler wrap the string in a dict like the other superweapon orders do.
**Effort:** Simple

---

### 4. FleetOrder vs Command Duplication

#### MINOR: Command and FleetOrder Carry Overlapping But Non-Identical Data
**ID:** ODM-009
**Location:** `game/strategy/engine/commands.py` (entire file), `game/strategy/data/fleet.py:64-68`
**Issue:** The Command classes and FleetOrder carry related but different data:
- `IssueTransferCommand` has `fleet_id`, `planet_id`, `cargo_type`, `direction`, `amount`, `species_id`, `target_fleet_id` (7 fields)
- `FleetOrder(TRANSFER)` stores all of this as a single untyped dict in `target`
- `IssueOpenWarpPointCommand` has `fleet_id`, `target_hex`, `target_system_name`
- `FleetOrder(OPEN_WARP_POINT)` stores `target_hex` and `target_system_name` in a dict

The command handlers manually extract command fields, resolve references (fleet_id -> Fleet, planet_id -> Planet), and pack the resolved data into FleetOrder.target. This mapping is bespoke for each handler.
**Impact:** The duplication is moderate but manageable given the registry pattern. Each handler's mapping code is ~5-15 lines. The real cost is that FleetOrder loses the structured typing that Commands provide - once data enters the FleetOrder, it's an untyped dict.
**Recommendation:** This is an intentional design choice (Commands are input-layer, FleetOrders are execution-layer). The duplication is acceptable IF FleetOrder.target gets proper typing (see ODM-002). No immediate action needed beyond ODM-002.
**Effort:** N/A (covered by ODM-002)

#### INFO: Command -> FleetOrder Mapping Is Clean and Consistent
**ID:** ODM-010
**Location:** `game/strategy/engine/command_handlers.py`, `game/strategy/engine/superweapon_command_handlers.py`
**Issue:** All command handlers follow the same pattern: resolve -> validate -> create FleetOrder -> add_order. The `BaseCommandHandler` mixin provides `_resolve_fleet()` and `_resolve_planet()` helpers. The `_setup_mission_move()` function extracts shared move-then-action logic for mission commands.
**Impact:** None - this is well-structured.
**Recommendation:** No action needed.
**Effort:** N/A

---

### 5. Order Queue Management

#### MAJOR: `ClearOrdersCommandHandler` Bypasses `Fleet.clear_orders()` Method
**ID:** ODM-011
**Location:** `game/strategy/engine/command_handlers.py:386-388`
**Issue:** The `ClearOrdersCommandHandler.execute()` directly sets `fleet.orders = []` and `fleet.path = []` instead of calling `fleet.clear_orders()`. The `clear_orders()` method (line 332) does `self.orders.clear()` and `self.path = []`. While functionally equivalent, directly setting `fleet.orders` to a new list bypasses any future logic added to `clear_orders()` (e.g., event logging, cleanup hooks, execution_progress reset).
**Impact:** If `clear_orders()` is enhanced in the future (e.g., to fire events, cancel in-progress actions, or log order cancellation), the command handler would not benefit. This also introduces an inconsistency: the `FleetOrderProcessor.cancel_all_orders()` method correctly calls `fleet.clear_orders()`, but the command handler does not.
**Recommendation:** Change `ClearOrdersCommandHandler.execute()` to call `fleet.clear_orders()` instead of directly manipulating the list and path.
**Effort:** Simple

#### MINOR: `pop_order()` Uses `list.pop(0)` - O(n) Operation
**ID:** ODM-012
**Location:** `game/strategy/data/fleet.py:344`
**Issue:** `Fleet.pop_order()` uses `self.orders.pop(0)`, which is O(n) for Python lists because it requires shifting all remaining elements. The order queue is always consumed from the front (FIFO).
**Impact:** Negligible in practice. Fleet order queues are typically very short (1-5 orders). However, this is a theoretical inefficiency that could be resolved with `collections.deque`.
**Recommendation:** Low priority. If order queues ever grow large, consider using `collections.deque` for O(1) popleft. Current queue sizes make this a non-issue.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **ODM-001 (CRITICAL)**: Unresolved `_fleet_ref` and `_planet_ref` markers after deserialization. Fleet/Planet references in saved orders are never resolved to actual objects after load, causing AttributeError crashes when those orders execute. This is a data-loss/crash bug that affects save/load reliability.

2. **ODM-003 (MAJOR)**: Planet targets on COLONIZE orders serialize as full Planet dicts but deserialize as `None`. Queued colonize orders targeting a specific planet silently lose their target after save/load, potentially colonizing the wrong planet.

3. **ODM-007 (MAJOR)**: `from_dict()` silently drops unrecognized target dict formats without logging any warning. This makes save/load bugs extremely hard to diagnose and allows data corruption to go unnoticed.

4. **ODM-002 (MAJOR)**: The untyped polymorphic `target` field accepts 8+ types with no type safety. This is the root cause of ODM-003 and ODM-004 - the serialization complexity is a direct consequence of the target field's lack of structure. Introducing typed target classes would prevent entire categories of bugs.

5. **ODM-011 (MAJOR)**: `ClearOrdersCommandHandler` bypasses `Fleet.clear_orders()`, creating an inconsistency with `FleetOrderProcessor.cancel_all_orders()`. Simple fix with low risk.
