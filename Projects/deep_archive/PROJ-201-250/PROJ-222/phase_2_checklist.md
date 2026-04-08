# PROJ-222 Phase 2: Fleet API Consolidation

**Objective:** Refactor command handlers to use Fleet's public API for order mutations. Add new Fleet methods needed for pursuer cleanup hooks.

## Task 2.1: Add Fleet.remove_order_at() Method [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_basics.py`
- [ ] Add method `remove_order_at(self, index: int) -> Optional[FleetOrder]` after `pop_order()` (after line 180)
- [ ] Implementation: validate index bounds, `orders.pop(index)`, clear path if index == 0, return removed order (or None if invalid)
- [ ] Add test in `test_basics.py` class `TestFleetOrders`: `test_remove_order_at_valid_index`
- [ ] Add test: `test_remove_order_at_index_zero_clears_path`
- [ ] Add test: `test_remove_order_at_invalid_index_returns_none`
- [ ] Add test: `test_remove_order_at_middle_preserves_path`
- [ ] Run tests: `pytest tests/unit/strategy/fleet/test_basics.py`
**Notes:**

## Task 2.2: Add Fleet.remove_orders_by_type() Method [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_basics.py`
- [ ] Add method `remove_orders_by_type(self, order_type: OrderType) -> List[FleetOrder]` after `remove_order_at()`
- [ ] Implementation: collect matching orders, filter `self.orders` in-place, return removed orders
- [ ] Add test: `test_remove_orders_by_type_removes_matching`
- [ ] Add test: `test_remove_orders_by_type_preserves_others`
- [ ] Run tests: `pytest tests/unit/strategy/fleet/test_basics.py`
**Notes:** This replaces the list comprehension in RemoveBuildOrderCommandHandler.

## Task 2.3: Refactor ClearOrdersCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`
- [ ] Change line 454 from `fleet.orders = []` to `fleet.clear_orders()`
- [ ] Remove line 455 (`fleet.path = []`) — already handled by `clear_orders()`
- [ ] Run tests: `pytest tests/unit/strategy/test_command_handlers.py`
**Notes:**

## Task 2.4: Refactor DeleteFleetOrderCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`
- [ ] Change line 703 from `fleet.orders.pop(cmd.order_index)` to `fleet.remove_order_at(cmd.order_index)`
- [ ] Remove lines 706-707 (path invalidation) — already handled by `remove_order_at()`
- [ ] Run tests: `pytest tests/unit/strategy/test_command_handlers.py`
**Notes:**

## Task 2.5: Refactor RemoveBuildOrderCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`
- [ ] Change line 570 from `fleet.orders = [o for o in fleet.orders if o.type != OrderType.BUILD]` to `fleet.remove_orders_by_type(OrderType.BUILD)`
- [ ] Run tests: `pytest tests/unit/strategy/test_command_handlers.py`
**Notes:**

## Task 2.6: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite to verify no regressions from API consolidation
- [ ] All 13358+ tests must pass (minus the 9 pre-existing failures)
**Notes:**

## Phase 2 Completion
- [ ] All Task 2.1-2.6 items checked
- [ ] `pytest tests/ -n 12` passes
