# Phase 2: Commands and Handlers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-34 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Objective:** Add new command types and their handlers in GameSession
**Status:** Complete

---

## Task 2.1: Add New Command Classes [Simple]
**File:** `game/strategy/engine/commands.py`
**Tests:** `pytest tests/strategy/test_commands.py`

- [x] Add `IssueInterceptCommand` dataclass
- [x] Add `IssueJoinFleetCommand` dataclass
- [x] Add `QueueColonizeMissionCommand` dataclass
- [x] Add `ClearFleetOrdersCommand` dataclass
- [x] All commands inherit from `Command` with `type = CommandType.ISSUE_ORDER`

**Notes:** All 4 command classes implemented with proper __init__ methods that set type = ISSUE_ORDER. 8 new tests in test_commands.py.

---

## Task 2.2: Implement Intercept Command Handler [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::TestInterceptCommandHandler`

- [x] Add `_handle_intercept_command(self, cmd: IssueInterceptCommand) -> ValidationResult` method
- [x] Resolve fleet by ID from empires
- [x] Resolve target_fleet by ID from empires
- [x] Validate both fleets exist
- [x] Create `FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)`
- [x] Call `fleet.add_order(order)`
- [x] Return `ValidationResult(is_valid=True, message="Intercept order issued")`
- [x] Add dispatch case in `handle_command()` for 'IssueInterceptCommand'
- [x] Write unit test for successful intercept
- [x] Write unit test for invalid fleet ID

**Notes:** Handler implemented with validation for source and target fleets. 3 tests in TestInterceptCommandHandler.

---

## Task 2.3: Implement Join Fleet Command Handler [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::TestJoinFleetCommandHandler`

- [x] Add `_handle_join_command(self, cmd: IssueJoinFleetCommand) -> ValidationResult` method
- [x] Resolve fleet and target_fleet by ID
- [x] Validate both fleets exist
- [x] Create `FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)`
- [x] Create `FleetOrder(OrderType.JOIN_FLEET, target=target_fleet)`
- [x] Add both orders to fleet (MOVE_TO_FLEET first, then JOIN_FLEET)
- [x] Return ValidationResult
- [x] Add dispatch case in `handle_command()`
- [x] Write unit tests

**Notes:** Handler queues 2 orders (MOVE_TO_FLEET then JOIN_FLEET). 3 tests in TestJoinFleetCommandHandler.

---

## Task 2.4: Implement Colonize Mission Command Handler [Complex]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::TestColonizeMissionCommandHandler`

This is the most complex handler - it moves logic from `strategy_colonization.py:183-206`

- [x] Add `_handle_colonize_mission_command(self, cmd: QueueColonizeMissionCommand) -> ValidationResult`
- [x] Resolve fleet by ID
- [x] Resolve planet by ID
- [x] Determine start_hex:
  - If fleet has orders, use last order's target hex
  - Otherwise use fleet.location
- [x] Calculate path using `find_hybrid_path(self.galaxy, start_hex, cmd.target_hex)`
- [x] If no path found, return validation error
- [x] Create MOVE order: `FleetOrder(OrderType.MOVE, target=cmd.target_hex)`
- [x] Assign path to fleet: `fleet.path = path`
- [x] Create COLONIZE order: `FleetOrder(OrderType.COLONIZE, target=planet)`
- [x] Add both orders to fleet
- [x] Return ValidationResult
- [x] Add dispatch case in `handle_command()`
- [x] Write unit test for successful mission queue
- [x] Write unit test for unreachable destination
- [x] Write unit test for invalid fleet/planet IDs

**Notes:** Handler implements full colonize mission logic including path calculation from last order target if fleet has orders. 5 tests in TestColonizeMissionCommandHandler.

---

## Task 2.5: Implement Clear Orders Command Handler [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::TestClearFleetOrdersCommandHandler`

- [x] Add `_handle_clear_orders_command(self, cmd: ClearFleetOrdersCommand) -> ValidationResult`
- [x] Resolve fleet by ID
- [x] Clear `fleet.orders = []`
- [x] Clear `fleet.path = []`
- [x] Return ValidationResult
- [x] Add dispatch case in `handle_command()`
- [x] Write unit test

**Notes:** Handler clears both orders and path. 3 tests in TestClearFleetOrdersCommandHandler.

---

## Phase 2 Verification
- [x] All 4 new command classes defined
- [x] All 4 command handlers implemented
- [x] All dispatch cases added to `handle_command()`
- [x] Run `pytest tests/strategy/test_command_handlers.py` - all pass (18 tests)
- [x] Run `pytest tests/ --testmon` - no regressions (4795 passed)
