# Phase 4: Command Pipeline Consistency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-207 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bring BUILD orders and FleetOrdersWindow into the command pipeline; extract duplicated auto-load logic
**Priority:** Medium

---

## Tasks

### Task 4.1: CP-002 - Route BUILD Orders Through Command Pipeline [Medium]
**Files:**
- `game/strategy/engine/commands.py` — add IssueBuildCommand
- `game/strategy/engine/command_handlers.py` — add BuildOrderCommandHandler (distinct from existing BuildShipCommandHandler which handles planet production)
- `game/ui/screens/strategy_build_queue_manager.py` (line 138)
**Tests:** `pytest tests/unit/strategy/engine/ -k "build"`

**Problem:** At `strategy_build_queue_manager.py` line 138, BUILD orders are created directly:
`fleet.orders.insert(0, FleetOrder(OrderType.BUILD))`. This bypasses the command pipeline entirely —
no Command class, no handler, no validation. It also directly removes BUILD orders via list
comprehension instead of through a command.

- [ ] Create `IssueBuildOrderCommand` in `commands.py` (following existing command pattern)
- [ ] Create `BuildOrderCommandHandler` in `command_handlers.py` that:
  - Resolves the fleet
  - Creates `FleetOrder(OrderType.BUILD)` and inserts at position 0
  - Returns ValidationResult.success()
- [ ] Register the handler in `create_default_registry()` (line ~599)
- [ ] Update `strategy_build_queue_manager.py` line 138: Replace direct `FleetOrder` creation with command dispatch through the session facade
- [ ] Also update the BUILD order removal logic in the same file to go through a command or at minimum through `fleet.pop_order()`
- [ ] Write test: BuildOrderCommandHandler creates BUILD order correctly
- [ ] Verify: build queue UI still functions correctly (manual test: open build queue, queue a ship design)

**Notes:** BuildShipCommandHandler (existing) handles adding designs to planet production queues. This new handler manages the fleet-level BUILD order that tells the fleet to execute its construction queue.

### Task 4.2: CP-001 - Route FleetOrdersWindow Clear Through Command Pipeline [Simple]
**File:** `game/ui/screens/fleet_orders_window.py` (line 386)
**Tests:** `pytest tests/unit/ui/ -k "fleet_orders"`

**Problem:** `handle_global_event()` at line 386 calls `self.fleet.clear_orders()` directly instead
of dispatching a `ClearFleetOrdersCommand`. This bypasses command logging.

- [ ] At line 386: Replace `self.fleet.clear_orders()` with command dispatch via `facade.handle_command()`:
  ```python
  # Change from:
  self.fleet.clear_orders()
  # To:
  cmd = ClearFleetOrdersCommand(fleet_id=self.fleet.id)
  self.facade.handle_command(cmd)
  ```
- [ ] Thread facade reference to `FleetOrdersWindow`: `StrategyScreen` → `StrategyWindowManager` → `FleetOrdersWindow.__init__()`. Consider passing a callback closure from StrategyScreen that calls `self.session.handle_command()` to avoid direct session dependency in UI.
- [ ] Write test: Clear All in fleet orders window dispatches command
- [ ] Verify: manual test — open fleet orders window, click Clear All

**Notes:** `ClearFleetOrdersCommand` (commands.py line 104) and `ClearOrdersCommandHandler` (command_handlers.py line 462) already exist and are registered in `create_default_registry()` (line 628). No new Command or Handler class needed — only the call site wiring and facade threading. Note: `FleetOrdersWindow` also has `delete_order()`, `move_order()`, and `undo_delete()` that bypass the pipeline — those are documented for a future project, not this one.

### Task 4.3: CP-003 - Extract Shared Auto-Load Population Helper [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "colonize"`

**Problem:** The auto-load population logic is copy-pasted between `ColonizeCommandHandler`
(lines 234-246) and `ColonizeMissionCommandHandler` (lines 429-441). Both build identical
`transfer_params` dicts and create LOAD_POPULATION orders.

- [ ] Extract a shared helper method on `BaseCommandHandler` or as a module-level function:
  ```python
  def _create_auto_load_order(fleet, origin_colony):
      """Create LOAD_POPULATION order to pick up founding population."""
      transfer_params = {
          'direction': 'load',
          'cargo_type': 'population',
          # ... (copy exact params from either handler)
      }
      return FleetOrder(OrderType.LOAD_POPULATION, target=transfer_params)
  ```
- [ ] Update `ColonizeCommandHandler.execute()` (lines 234-246) to call the extracted helper
- [ ] Update `ColonizeMissionCommandHandler.execute()` (lines 429-441) to call the extracted helper
- [ ] Verify: both colonize paths produce identical orders (write a comparison test)
- [ ] Verify: no regressions in colonize tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — full suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
