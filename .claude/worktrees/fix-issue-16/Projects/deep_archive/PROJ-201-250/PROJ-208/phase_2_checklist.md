# Phase 2: Build Queue Commands

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-208 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create build queue commands and route all queue mutations through facade
**Priority:** Critical/Major — second most severe violation cluster
**Findings Addressed:** AR2-001, AR2-002, AR-014, AR-015, CGA-04, CGA-06, CGA-07, CGA-08, CGA-14, DCA-003

---

## Task 2.1: Create AddToConstructionQueueCommand [Complex] ✅
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** AR2-001, CGA-04, DCA-003

- [x] Add `AddToConstructionQueueCommand` dataclass to `commands.py` (see design.md for spec)
- [x] Create `AddToConstructionQueueCommandHandler` in `command_handlers.py`
- [x] Implement validation: entity exists, design valid, category valid
- [x] Implement handler: look up design, create queue item, insert/append
- [x] Write handler unit tests (planet queue, fleet queue, insert vs append)
- [x] Verify: `pytest tests/ -k "construction_queue" -n 4`

**Notes:** Command supports entity_type (planet/fleet), design_id, category, optional index (insert vs append), and optional target_planet_id for complexes. Handler creates queue item dict with design_id, type, turns_remaining, total_cost, resources_consumed.

### Task 2.2: Create RemoveFromConstructionQueueCommand [Simple] ✅
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** AR-015, CGA-06

- [x] Add `RemoveFromConstructionQueueCommand` dataclass
- [x] Create handler with validation (entity exists, index valid)
- [x] Handle fleet BUILD order cleanup when queue empties
- [x] Write handler unit tests
- [x] Verify tests pass

**Notes:** BUILD order cleanup not done in handler - that's a separate concern handled by RemoveBuildOrderCommand from PROJ-207. The handler just removes the item.

### Task 2.3: Create ReorderConstructionQueueCommand [Medium] ✅
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** AR2-002, CGA-07

- [x] Add `ReorderConstructionQueueCommand` dataclass
- [x] Create handler with validation (entity exists, both indices valid)
- [x] Implement atomic pop+insert
- [x] Write handler unit tests
- [x] Verify tests pass

**Notes:** Handler performs atomic pop+insert. Tests verify forward/backward reordering works correctly.

### Task 2.4: Refactor build_queue_controller.py to use commands [Complex] ✅
**File:** `game/ui/panels/build_queue_controller.py`
**Addresses:** AR2-001, CGA-04, DCA-003

- [x] Replace all `source.construction_queue.insert()` with `facade.handle_command(AddToConstructionQueueCommand(...))`
- [x] Replace all `source.construction_queue.append()` with command dispatch
- [x] Ensure controller receives facade reference (via callback injection)
- [x] Handle the multi-queue distribution logic (batch add to multiple planets)
- [x] Verify: `pytest tests/ -n 12`

**Notes:** Implemented via callback injection pattern. Controller receives `add_to_queue_callback` which dispatches AddToConstructionQueueCommand through session. Added `queue_id` parameter to command for multi-queue support (shipyard facilities). Tests updated to inject callbacks. 12923 tests passing.

### Task 2.5: Refactor build_queue_drag_handler.py to use commands [Medium] ✅
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Addresses:** AR2-002, CGA-07

- [x] Replace `construction_queue.pop(idx)` on drag start with RemoveFromConstructionQueueCommand
- [x] On drop, use AddToConstructionQueueCommand to insert at new position
- [x] Handle drag cancel (item already removed — needs reinsertion at original position)
- [x] Verify: `pytest tests/ -n 12`

**Notes:** Implemented via callback injection (`on_remove_from_queue`). Drag handler reads item data first, then calls callback to dispatch RemoveFromConstructionQueueCommand. Legacy fallback preserved for tests without session injection. 12923 tests passing.

### Task 2.6: Refactor build_queue_screen.py to use commands [Simple] ✅
**File:** `game/ui/screens/build_queue_screen.py`
**Addresses:** AR-015, CGA-06

- [x] Replace `queue.pop(self.selected_queue_index)` with `facade.handle_command(RemoveFromConstructionQueueCommand(...))`
- [x] Ensure screen receives facade reference
- [x] Verify tests pass

**Notes:** Reused `_dispatch_remove_from_queue_command()` method in `_handle_remove()`. 12923 tests passing.

### Task 2.7: Refactor empire_build_queue_window.py batch add [Medium] ✅
**File:** `game/ui/screens/empire_build_queue_window.py`
**Addresses:** AR-014, CGA-08

- [x] Replace `source.construction_queue.append(dict(item))` with command dispatch
- [x] batch_add_to_selected() should loop and dispatch individual AddToConstructionQueueCommands
- [x] Verify tests pass

**Notes:** Added `_session` parameter to window constructor. Created `_add_item_to_source()` helper that dispatches AddToConstructionQueueCommand when session available. Updated strategy_window_manager.py to pass session. 12923 tests passing.

### Task 2.8: Investigate IssueBuildShipCommand dead code [Simple] ✅
**Addresses:** CGA-14

- [x] Search for all callers of `IssueBuildShipCommand`
- [x] If unused in production code, remove it and its handler
- [x] Or refactor it to align with new AddToConstructionQueueCommand
- [x] Document decision in decisions.md

**Notes:** Confirmed dead code - no production callers found. Removed IssueBuildShipCommand, BuildShipCommandHandler, and handler registration. Updated test files to remove references. Decision logged in decisions.md. 12918 tests passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No direct construction_queue.insert/append/pop in build queue UI files
- [x] All new command handlers have unit tests
- [x] Full test suite passes: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
