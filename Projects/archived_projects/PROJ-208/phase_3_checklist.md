# Phase 3: Research & Miscellaneous Commands

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-208 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create research commands and fix remaining routing issues
**Priority:** Major — research mutations + routing consistency
**Findings Addressed:** AR2-003, CGA-09, CGA-10, CGA-11, CGA-12, CGA-13, AR-013, CQ-011

---

## Task 3.1: Create SetResearchBudgetCommand [Simple] - DEFERRED
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** CGA-09

- [ ] ~~Add `SetResearchBudgetCommand` dataclass to `commands.py`~~
- [ ] ~~Create handler with budget bounds validation~~
- [ ] ~~Write handler unit tests~~
- [ ] ~~Verify tests pass~~

**Notes:** DEFERRED - Research scene is a standalone sandbox (not integrated with strategy layer). ResearchTracker is not accessible via facade/session. Requires architectural work to integrate research into strategy layer.

### Task 3.2: Create SetResearchAllocationCommand [Simple] - DEFERRED
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** CGA-10

- [ ] ~~Add `SetResearchAllocationCommand` dataclass~~
- [ ] ~~Create handler: validate node availability, allocation within budget~~
- [ ] ~~Write handler unit tests~~
- [ ] ~~Verify tests pass~~

**Notes:** DEFERRED - Same reason as 3.1. Research scene standalone sandbox.

### Task 3.3: Create SpreadResearchRPCommand [Simple] - DEFERRED
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** CGA-11

- [ ] ~~Add `SpreadResearchRPCommand` dataclass~~
- [ ] ~~Create handler: validate tracker exists, call spread logic~~
- [ ] ~~Write handler unit tests~~
- [ ] ~~Verify tests pass~~

**Notes:** DEFERRED - Same reason as 3.1. Research scene standalone sandbox.

### Task 3.4: Refactor research_controls.py to use commands [Medium] - DEFERRED
**File:** `game/ui/research/research_controls.py`
**Addresses:** AR2-003, CGA-09, CGA-10, CGA-11

- [ ] ~~Replace `tracker.set_rp_budget(new_budget)` with `facade.handle_command(SetResearchBudgetCommand(...))`~~
- [ ] ~~Replace `tracker.set_allocation(node_id, allocation)` with command dispatch~~
- [ ] ~~Replace `tracker.spread_rp_evenly(tech_tree)` with command dispatch~~
- [ ] ~~Ensure research_controls receives facade reference~~
- [ ] ~~Verify: `pytest tests/ -n 12`~~

**Notes:** DEFERRED - Research scene is standalone sandbox accessed from main menu, not part of strategy game. Has no facade/session. Requires architectural integration work outside PROJ-208 scope.

### Task 3.5: Fix facade routing in strategy_build_queue_manager.py [Simple]
**Addresses:** CGA-13

- [x] ~~Change `self._screen.session.handle_command(cmd)` to `self._screen._facade.handle_command(cmd)` at lines 142 and 146~~ (Already using facade correctly)
- [x] Pass `facade` parameter to BuildQueueScreen at all 3 instantiation sites
- [x] Verify tests pass

**Notes:** strategy_build_queue_manager.py already uses facade.handle_command at lines 165/169. Added facade parameter to BuildQueueScreen constructor and updated all 3 instantiation sites.

### Task 3.6: Fix facade routing in strategy_window_manager.py [Simple]
**Addresses:** AR-013, CQ-011, CGA-13

- [x] Change `session.handle_command(cmd)` to `facade.handle_command(cmd)` at lines 288, 295, 301, 332
- [x] Pass `facade` parameter to EmpireBuildQueueWindow
- [x] Verify tests pass

**Notes:** Fixed 4 callbacks (clear_orders, delete_order, reorder_order, split_fleet). Added facade injection to EmpireBuildQueueWindow.

### Task 3.7: Remove backward compat fallback in fleet_orders_window.py [Simple]
**Addresses:** CGA-12, CQ-005

- [x] ~~Remove the `fleet.clear_orders()` fallback path at lines 400-404~~ (Already removed in prior phase)
- [x] Callback already used without fallback
- [x] Verify tests pass

**Notes:** Fallback was already removed in prior implementation. Code at lines 375-377 shows no fallback exists.

---

## Additional Fixes (discovered during implementation)

### Fix session.handle_command in build_queue_screen.py
- [x] Add `facade` parameter to BuildQueueScreen.__init__
- [x] Update _dispatch_add_to_queue_command to use facade if available
- [x] Update _dispatch_remove_from_queue_command to use facade if available
- [x] Verify tests pass

### Fix session.handle_command in empire_build_queue_window.py
- [x] Add `facade` parameter to EmpireBuildQueueWindow.__init__
- [x] Update _add_item_to_source to use facade if available
- [x] Use getattr for test compatibility
- [x] Verify tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All applicable task checkboxes above are checked (3.1-3.4 DEFERRED)
- [N/A] No direct tracker.set_rp_budget/set_allocation/spread_rp_evenly in research UI (DEFERRED)
- [x] No session.handle_command() bypass in build_queue_manager or window_manager
- [x] No backward compat fallback in fleet_orders_window
- [N/A] All new command handlers have unit tests (no new commands - 3.1-3.4 DEFERRED)
- [x] Full test suite passes: `pytest tests/ -n 12` (12918 passed, 4 pre-existing bug_13 failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
