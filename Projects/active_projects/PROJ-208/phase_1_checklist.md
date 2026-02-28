# Phase 1: Fleet Management Commands

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-208 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress (Tasks 1.1-1.4 Complete)
**Objective:** Create fleet management commands and route all fleet mutations through facade
**Priority:** Critical — these are the most severe violations
**Findings Addressed:** AR-001 through AR-011, CQ-001 through CQ-004, CQ-007, CQ-009, CGA-01 through CGA-03, CGA-05, DCA-001, DCA-002

---

## Task 1.1: Create SplitFleetCommand [Medium] ✅
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** AR-001, AR-002, AR-003, AR-004, CQ-001, CQ-004, CQ-007, CGA-05, DCA-001

- [x] Add `SplitFleetCommand` dataclass to `commands.py` (see design.md for spec)
- [x] Create `SplitFleetCommandHandler` in `command_handlers.py`
- [x] Implement validation: fleet exists, ships belong to fleet, at least 1 ship remains
- [x] Implement handler: remove ships, create new fleet, register with empire
- [x] Write handler unit tests (success, validation failures, edge cases)
- [x] Verify: `pytest tests/ -k "split_fleet" -n 4`

**Notes:** 6 unit tests: fleet_not_found, no_ships_specified, ship_not_in_fleet, cannot_remove_all_ships, fleet_owner_not_found, valid_split_creates_new_fleet

### Task 1.2: Create DeleteFleetOrderCommand [Simple] ✅
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** AR-006, CGA-02

- [x] Add `DeleteFleetOrderCommand` dataclass to `commands.py`
- [x] Create `DeleteFleetOrderCommandHandler` in `command_handlers.py`
- [x] Implement validation: fleet exists, order_index valid
- [x] Implement handler: pop order, invalidate path if index 0
- [x] Write handler unit tests
- [x] Verify: `pytest tests/ -k "delete_fleet_order" -n 4`

**Notes:** 5 unit tests covering validation failures and path invalidation

### Task 1.3: Create ReorderFleetOrderCommand [Simple] ✅
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** AR-005, CGA-01

- [x] Add `ReorderFleetOrderCommand` dataclass to `commands.py`
- [x] Create `ReorderFleetOrderCommandHandler` in `command_handlers.py`
- [x] Implement validation: fleet exists, order_index valid, direction valid
- [x] Implement handler: swap orders, invalidate path if active order affected
- [x] Write handler unit tests
- [x] Verify: `pytest tests/ -k "reorder_fleet_order" -n 4`

**Notes:** 9 unit tests covering validation failures, position swapping, and path invalidation

### Task 1.4: Add facade methods for new fleet commands [Simple] ✅
**File:** `game/strategy/facade/strategy_session_facade.py`

- [x] Ensure `handle_command()` can route all three new command types
- [x] Verify command handler registration with GameSession
- [x] Test facade routing end-to-end

**Notes:** All three handlers registered in create_default_registry(). Routing verified through existing handle_command() mechanism.

### Task 1.5: Refactor fleet_report_window.py to use SplitFleetCommand [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Addresses:** AR-001, AR-002, AR-003, AR-004, AR-010, AR-011, CQ-001, CQ-004, CQ-007, CQ-009

- [ ] Replace `_on_remove_ship()` direct mutation with `facade.handle_command(SplitFleetCommand(...))`
- [ ] Replace `_on_remove_selected_ships()` with command dispatch
- [ ] Remove `_create_fleet_for_ships()` method (logic now in handler)
- [ ] Remove `Fleet` import from this file
- [ ] Ensure window receives facade reference (not raw fleet/empire)
- [ ] Update strategy_window_manager to pass facade to fleet_report_window
- [ ] Verify: `pytest tests/ -n 12` (full suite — many files touched)

**Notes:** [Filled during implementation]

### Task 1.6: Refactor fleet_orders_window.py to use order commands [Medium]
**File:** `game/ui/screens/fleet_orders_window.py`
**Addresses:** AR-005, AR-006, AR-007, AR-008, AR-009, CQ-002, CQ-003, CQ-005, CGA-01, CGA-02, CGA-03

- [ ] Replace `_move_order()` direct swap with `facade.handle_command(ReorderFleetOrderCommand(...))`
- [ ] Replace `_delete_order()` direct pop with `facade.handle_command(DeleteFleetOrderCommand(...))`
- [ ] Replace `_undo_delete()` direct insert with command dispatch (or remove undo feature)
- [ ] Remove direct `fleet.path = []` writes (now handled by command handlers)
- [ ] Remove backward compatibility fallback for clear_orders (CQ-005)
- [ ] Ensure window receives facade reference
- [ ] Update strategy_window_manager to pass facade to fleet_orders_window
- [ ] Verify: `pytest tests/ -n 12`

**Notes:** Decision needed: How to handle undo-delete? Options: (a) InsertFleetOrderCommand, (b) DeleteFleetOrderCommand returns removed order for client-side undo tracking, (c) Remove undo feature.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No direct fleet.remove_ship(), fleet.orders.pop/insert/swap, fleet.path=[] in fleet windows
- [ ] All new command handlers have unit tests
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
