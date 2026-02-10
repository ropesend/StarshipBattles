# Phase 5: GameSession Command Handlers [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract command handler methods into a CommandHandlerRegistry pattern

**File:** `game/strategy/engine/game_session.py`
**New File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/gameplay_loop/ -n 4`

---

## Tasks

### Task 5.1: Create command handler infrastructure [Medium]
**File:** `game/strategy/engine/command_handlers.py` (NEW)
- [ ] Define `ICommandHandler` protocol with `execute(session, command_data)` method
- [ ] Create `CommandHandlerRegistry` class with `register(command_type, handler)` and `dispatch(command_type, session, data)` methods
- [ ] Create individual handler classes, each extracting one `_handle_*_command()` method from GameSession:
  - `BuildShipCommandHandler` ← `_handle_build_ship_command()`
  - `MoveCommandHandler` ← `_handle_move_command()`
  - `TransferCommandHandler` ← `_handle_transfer_command()`
  - `ColonizeCommandHandler` ← `_handle_colonize_command()`
  - `ColonizeMissionCommandHandler` ← `_handle_colonize_mission_command()`
  - `InterceptCommandHandler` ← `_handle_intercept_command()`
  - `JoinCommandHandler` ← `_handle_join_command()`
  - `ClearOrdersCommandHandler` ← `_handle_clear_orders_command()`

**Notes:** Each handler receives the session as a parameter to access empires, galaxy, etc.

### Task 5.2: Wire GameSession to use registry [Simple]
**File:** `game/strategy/engine/game_session.py`
- [ ] Create `self._command_registry = CommandHandlerRegistry()` in `__init__`
- [ ] Register all 8 handlers in `__init__`
- [ ] Replace `handle_command()` if/elif chain with:
  ```python
  def handle_command(self, command_type: str, data: dict):
      self._command_registry.dispatch(command_type, self, data)
  ```
- [ ] Remove all 8 `_handle_*_command()` methods from GameSession
- [ ] Run `pytest tests/unit/strategy/ -n 4` — all pass

**Notes:**

### Task 5.3: Write tests and verify [Simple]
**File:** `tests/unit/strategy/test_command_handlers.py` (NEW)
- [ ] Test each handler in isolation with mock session
- [ ] Test registry dispatch (correct handler called for each command type)
- [ ] Test unknown command type handling
- [ ] Run `pytest tests/integration/gameplay_loop/ -n 4` — all pass
- [ ] Verify GameSession line count reduced by ~200 lines
- [ ] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
