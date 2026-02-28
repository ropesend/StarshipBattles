# Phase 4: Command Pipeline Consistency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-207 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Create `IssueBuildOrderCommand` in `commands.py` (following existing command pattern)
- [x] Create `BuildOrderCommandHandler` in `command_handlers.py` that:
  - Resolves the fleet
  - Creates `FleetOrder(OrderType.BUILD)` and inserts at position 0
  - Returns ValidationResult.success()
- [x] Register the handler in `create_default_registry()` (line ~599)
- [x] Update `strategy_build_queue_manager.py` line 138: Replace direct `FleetOrder` creation with command dispatch through the session facade
- [x] Also update the BUILD order removal logic in the same file to go through a command or at minimum through `fleet.pop_order()`
- [x] Write test: BuildOrderCommandHandler creates BUILD order correctly
- [x] Verify: build queue UI still functions correctly (manual test: open build queue, queue a ship design)

**Implementation Notes:**
- Created `IssueBuildOrderCommand` and `RemoveBuildOrderCommand` in commands.py
- Created `BuildOrderCommandHandler` and `RemoveBuildOrderCommandHandler` in command_handlers.py
- Both handlers registered in `create_default_registry()`
- Updated `_handle_fleet_build_queue_close()` to dispatch commands via `session.handle_command()`
- 13 new tests in `test_build_order_command_handler.py`
- Updated existing tests in `test_strategy_build_queue_manager.py` to verify command dispatch

### Task 4.2: CP-001 - Route FleetOrdersWindow Clear Through Command Pipeline [Simple]
**File:** `game/ui/screens/fleet_orders_window.py` (line 386)
**Tests:** `pytest tests/unit/ui/ -k "fleet_orders"`

**Problem:** `handle_global_event()` at line 386 calls `self.fleet.clear_orders()` directly instead
of dispatching a `ClearFleetOrdersCommand`. This bypasses command logging.

- [x] At line 386: Replace `self.fleet.clear_orders()` with command dispatch via `facade.handle_command()`:
- [x] Thread facade reference to `FleetOrdersWindow`: `StrategyScreen` → `StrategyWindowManager` → `FleetOrdersWindow.__init__()`. Consider passing a callback closure from StrategyScreen that calls `self.session.handle_command()` to avoid direct session dependency in UI.
- [x] Write test: Clear All in fleet orders window dispatches command
- [x] Verify: manual test — open fleet orders window, click Clear All

**Implementation Notes:**
- Added `clear_orders_callback` parameter to `FleetOrdersWindow.__init__()`
- Created callback closure in `StrategyWindowManager.open_orders_window()` that dispatches `ClearFleetOrdersCommand`
- Updated `handle_global_event()` to use callback when provided, fallback to direct clear for backward compatibility
- Added 2 new tests in `test_fleet_orders_refresh.py`

### Task 4.3: CP-003 - Extract Shared Auto-Load Population Helper [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "colonize"`

**Problem:** The auto-load population logic is copy-pasted between `ColonizeCommandHandler`
(lines 234-246) and `ColonizeMissionCommandHandler` (lines 429-441). Both build identical
`transfer_params` dicts and create LOAD_POPULATION orders.

- [x] Extract a shared helper method on `BaseCommandHandler` or as a module-level function
- [x] Update `ColonizeCommandHandler.execute()` (lines 234-246) to call the extracted helper
- [x] Update `ColonizeMissionCommandHandler.execute()` (lines 429-441) to call the extracted helper
- [x] Verify: both colonize paths produce identical orders (write a comparison test)
- [x] Verify: no regressions in colonize tests

**Implementation Notes:**
- Created module-level `create_auto_load_population_order(origin_colony)` function
- Returns `FleetOrder` or `None` if colony has no populations
- Updated both handlers to use the shared helper
- Added 4 new tests for the helper function
- All 275 colonize tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` — full suite passes (12876 passed, 4 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
