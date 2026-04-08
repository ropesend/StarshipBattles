# PROJ-222 Phase 3: Pursuer Registration & Lifecycle

**Objective:** Wire FleetPursuerTracker into Fleet and command handlers. Pursuers are registered when orders are created and unregistered when orders are removed.

## Task 3.1: Add FleetPursuerTracker to Fleet [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_basics.py`
- [ ] Add import: `from game.strategy.data.fleet_pursuer_tracker import FleetPursuerTracker` (after line 15)
- [ ] Add in `__init__` after line 70: `self._pursuer_tracker = FleetPursuerTracker(self)`
- [ ] Add property after `battle` property (after line 141): `@property pursuer_tracker(self) -> 'FleetPursuerTracker': return self._pursuer_tracker`
- [ ] Add test in `test_basics.py`: `test_fleet_has_pursuer_tracker` — verify `fleet.pursuer_tracker` exists and is empty
- [ ] Run tests: `pytest tests/unit/strategy/fleet/test_basics.py`
**Notes:**

## Task 3.2: Register Pursuers in JoinCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`
- [ ] In `JoinCommandHandler.execute()`, after creating both orders (after line 367): add `target_fleet.pursuer_tracker.add_pursuer(fleet)`
- [ ] Add self-targeting validation (before order creation): `if fleet.id == target_fleet.id: return ValidationResult.error("Fleet cannot join itself.")`
- [ ] Add same-empire validation: `if fleet.owner_id != target_fleet.owner_id: return ValidationResult.error("Cannot join fleet of another empire.")`
- [ ] Add test: `test_join_registers_pursuer` — verify `target_fleet.pursuer_tracker.pursuer_count == 1` after command
- [ ] Add test: `test_join_self_targeting_rejected` — verify error returned
- [ ] Add test: `test_join_cross_empire_rejected` — verify error returned
- [ ] Run tests: `pytest tests/unit/strategy/test_command_handlers.py`
**Notes:**

## Task 3.3: Register Pursuers in InterceptCommandHandler [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`
- [ ] In `InterceptCommandHandler.execute()`, after creating order (after line 339): add `target_fleet.pursuer_tracker.add_pursuer(fleet)`
- [ ] Add self-targeting validation: `if fleet.id == target_fleet.id: return ValidationResult.error("Fleet cannot intercept itself.")`
- [ ] Add test: `test_intercept_registers_pursuer` — verify pursuer registered
- [ ] Add test: `test_intercept_self_targeting_rejected` — verify error returned
- [ ] Run tests: `pytest tests/unit/strategy/test_command_handlers.py`
**Notes:**

## Task 3.4: Unregister Pursuers on Order Removal [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
- [ ] Add helper: `_unregister_from_target(self, order: FleetOrder) -> None` — if order type is MOVE_TO_FLEET or JOIN_FLEET and `hasattr(order.target, 'pursuer_tracker')`, call `order.target.pursuer_tracker.remove_pursuer(self)`
- [ ] In `clear_orders()`: before clearing, iterate `self.orders` and call `self._unregister_from_target(order)` for each
- [ ] In `pop_order()`: after popping, call `self._unregister_from_target(finished)` on the popped order
- [ ] In `remove_order_at()`: after removing, call `self._unregister_from_target(removed)` on the removed order
- [ ] In `remove_orders_by_type()`: call `self._unregister_from_target(order)` for each removed order
- [ ] Add test: `test_clear_orders_unregisters_pursuers` — register pursuer, clear orders, verify unregistered
- [ ] Add test: `test_pop_order_unregisters_pursuer` — register pursuer, pop order, verify unregistered
- [ ] Add test: `test_remove_order_at_unregisters_pursuer` — register pursuer, remove by index, verify unregistered
- [ ] Add test: `test_unregister_handles_non_fleet_target_gracefully` — order with HexCoord target doesn't crash
- [ ] Run tests: `pytest tests/unit/strategy/fleet/`
**Notes:** Use `hasattr(order.target, 'pursuer_tracker')` as duck-type guard since order.target can be Fleet, HexCoord, Planet, or Dict.

## Task 3.5: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] All tests must pass (minus pre-existing failures)
**Notes:**

## Phase 3 Completion
- [ ] All Task 3.1-3.5 items checked
- [ ] `pytest tests/ -n 12` passes
