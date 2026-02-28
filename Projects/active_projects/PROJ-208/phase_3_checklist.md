# Phase 3: Research & Miscellaneous Commands

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-208 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create research commands and fix remaining routing issues
**Priority:** Major — research mutations + routing consistency
**Findings Addressed:** AR2-003, CGA-09, CGA-10, CGA-11, CGA-12, CGA-13, AR-013, CQ-011

---

## Task 3.1: Create SetResearchBudgetCommand [Simple]
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** CGA-09

- [ ] Add `SetResearchBudgetCommand` dataclass to `commands.py`
- [ ] Create handler with budget bounds validation
- [ ] Write handler unit tests
- [ ] Verify tests pass

**Notes:** [Filled during implementation]

### Task 3.2: Create SetResearchAllocationCommand [Simple]
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** CGA-10

- [ ] Add `SetResearchAllocationCommand` dataclass
- [ ] Create handler: validate node availability, allocation within budget
- [ ] Write handler unit tests
- [ ] Verify tests pass

**Notes:** [Filled during implementation]

### Task 3.3: Create SpreadResearchRPCommand [Simple]
**File:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Addresses:** CGA-11

- [ ] Add `SpreadResearchRPCommand` dataclass
- [ ] Create handler: validate tracker exists, call spread logic
- [ ] Write handler unit tests
- [ ] Verify tests pass

**Notes:** [Filled during implementation]

### Task 3.4: Refactor research_controls.py to use commands [Medium]
**File:** `game/ui/research/research_controls.py`
**Addresses:** AR2-003, CGA-09, CGA-10, CGA-11

- [ ] Replace `tracker.set_rp_budget(new_budget)` with `facade.handle_command(SetResearchBudgetCommand(...))`
- [ ] Replace `tracker.set_allocation(node_id, allocation)` with command dispatch
- [ ] Replace `tracker.spread_rp_evenly(tech_tree)` with command dispatch
- [ ] Ensure research_controls receives facade reference
- [ ] Verify: `pytest tests/ -n 12`

**Notes:** [Filled during implementation]

### Task 3.5: Fix facade routing in strategy_build_queue_manager.py [Simple]
**Addresses:** CGA-13

- [ ] Change `self._screen.session.handle_command(cmd)` to `self._screen._facade.handle_command(cmd)` at lines 142 and 146
- [ ] Verify tests pass

**Notes:** Functionally identical but architecturally correct.

### Task 3.6: Fix facade routing in strategy_window_manager.py [Simple]
**Addresses:** AR-013, CQ-011, CGA-13

- [ ] Change `session.handle_command(cmd)` to `facade.handle_command(cmd)` at line 284
- [ ] Verify tests pass

**Notes:** [Filled during implementation]

### Task 3.7: Remove backward compat fallback in fleet_orders_window.py [Simple]
**Addresses:** CGA-12, CQ-005

- [ ] Remove the `fleet.clear_orders()` fallback path at lines 400-404
- [ ] Make `_clear_orders_callback` required (remove None default)
- [ ] Update any tests that don't provide the callback
- [ ] Verify tests pass

**Notes:** Per CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely."

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No direct tracker.set_rp_budget/set_allocation/spread_rp_evenly in research UI
- [ ] No session.handle_command() bypass in build_queue_manager or window_manager
- [ ] No backward compat fallback in fleet_orders_window
- [ ] All new command handlers have unit tests
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
