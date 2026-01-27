# Phase 2: Commands and Handlers

**Objective:** Add new command types and their handlers in GameSession
**Status:** Not Started

---

## Task 2.1: Add New Command Classes [Simple]
**File:** `game/strategy/engine/commands.py`
**Tests:** `pytest tests/strategy/test_commands.py`

- [ ] Add `IssueInterceptCommand` dataclass:
  ```python
  @dataclass
  class IssueInterceptCommand(Command):
      fleet_id: int
      target_fleet_id: int

      def __init__(self, fleet_id: int, target_fleet_id: int):
          self.type = CommandType.ISSUE_ORDER
          self.fleet_id = fleet_id
          self.target_fleet_id = target_fleet_id
  ```
- [ ] Add `IssueJoinFleetCommand` dataclass:
  ```python
  @dataclass
  class IssueJoinFleetCommand(Command):
      fleet_id: int
      target_fleet_id: int
  ```
- [ ] Add `QueueColonizeMissionCommand` dataclass:
  ```python
  @dataclass
  class QueueColonizeMissionCommand(Command):
      fleet_id: int
      target_hex: Any  # HexCoord
      planet_id: int
  ```
- [ ] Add `ClearFleetOrdersCommand` dataclass:
  ```python
  @dataclass
  class ClearFleetOrdersCommand(Command):
      fleet_id: int
  ```
- [ ] All commands inherit from `Command` with `type = CommandType.ISSUE_ORDER`

**Notes:**

---

## Task 2.2: Implement Intercept Command Handler [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::test_intercept_command`

- [ ] Add `_handle_intercept_command(self, cmd: IssueInterceptCommand) -> ValidationResult` method
- [ ] Resolve fleet by ID from empires
- [ ] Resolve target_fleet by ID from empires
- [ ] Validate both fleets exist
- [ ] Create `FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)`
- [ ] Call `fleet.add_order(order)`
- [ ] Return `ValidationResult(is_valid=True, message="Intercept order issued")`
- [ ] Add dispatch case in `handle_command()` for 'IssueInterceptCommand':
  ```python
  elif cmd_name == 'IssueInterceptCommand':
      return self._handle_intercept_command(command)
  ```
- [ ] Write unit test for successful intercept
- [ ] Write unit test for invalid fleet ID

**Notes:**

---

## Task 2.3: Implement Join Fleet Command Handler [Medium]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::test_join_command`

- [ ] Add `_handle_join_command(self, cmd: IssueJoinFleetCommand) -> ValidationResult` method
- [ ] Resolve fleet and target_fleet by ID
- [ ] Validate both fleets exist
- [ ] Create `FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)`
- [ ] Create `FleetOrder(OrderType.JOIN_FLEET, target=target_fleet)`
- [ ] Add both orders to fleet (MOVE_TO_FLEET first, then JOIN_FLEET)
- [ ] Return ValidationResult
- [ ] Add dispatch case in `handle_command()`
- [ ] Write unit tests

**Notes:**

---

## Task 2.4: Implement Colonize Mission Command Handler [Complex]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::test_colonize_mission_command`

This is the most complex handler - it moves logic from `strategy_colonization.py:183-206`

- [ ] Add `_handle_colonize_mission_command(self, cmd: QueueColonizeMissionCommand) -> ValidationResult`
- [ ] Resolve fleet by ID
- [ ] Resolve planet by ID
- [ ] Determine start_hex:
  - If fleet has orders, use last order's target hex
  - Otherwise use fleet.location
- [ ] Calculate path using `find_hybrid_path(self.galaxy, start_hex, cmd.target_hex)`
- [ ] If no path found, return validation error
- [ ] Create MOVE order: `FleetOrder(OrderType.MOVE, target=cmd.target_hex)`
- [ ] Assign path to fleet: `fleet.path = path`
- [ ] Create COLONIZE order: `FleetOrder(OrderType.COLONIZE, target=planet)`
- [ ] Add both orders to fleet
- [ ] Return ValidationResult
- [ ] Add dispatch case in `handle_command()`
- [ ] Write unit test for successful mission queue
- [ ] Write unit test for unreachable destination
- [ ] Write unit test for invalid fleet/planet IDs

**Notes:**

---

## Task 2.5: Implement Clear Orders Command Handler [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/strategy/test_command_handlers.py::test_clear_orders_command`

- [ ] Add `_handle_clear_orders_command(self, cmd: ClearFleetOrdersCommand) -> ValidationResult`
- [ ] Resolve fleet by ID
- [ ] Clear `fleet.orders = []`
- [ ] Clear `fleet.path = []`
- [ ] Return ValidationResult
- [ ] Add dispatch case in `handle_command()`
- [ ] Write unit test

**Notes:**

---

## Phase 2 Verification
- [ ] All 4 new command classes defined
- [ ] All 4 command handlers implemented
- [ ] All dispatch cases added to `handle_command()`
- [ ] Run `pytest tests/strategy/test_command_handlers.py` - all pass
- [ ] Run `pytest tests/ --testmon` - no regressions
