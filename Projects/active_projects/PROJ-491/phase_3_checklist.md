# Phase 3: Task 3.32 ActionExecutionEngine test rewrite

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-491 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rewrite 3 test methods that still patch `ActionTimeResolver.resolve_action_time(...)` statically to instead inject a stub resolver via the **already-existing** production DI seam.

**Background:** PROJ-479 deferred Task 3.32 citing "needs injectable `ActionTimeResolver` param in production". This was wrong — the production class already has it. From PROJ-479 audit finding F2 and Codex consult re-verification:

- `ActionExecutionEngine.__init__` accepts `action_time_resolver: Optional[ActionTimeResolver] = None` at `game/strategy/engine/action_execution_engine.py:55-68`.
- `_process_fleet_action_tick` prefers the injected resolver over the static method at `game/strategy/engine/action_execution_engine.py:183-192`.
- Tests still patch the static method at `tests/unit/strategy/engine/test_action_execution_engine.py:145-148, 199-202, 442-445` (3 methods).

**Discovered Issue:** DI-2026-05-23-003 — this phase resolves it.

---

## Tasks

### Task 3.1: Verify production DI seam still exists
**File:** `game/strategy/engine/action_execution_engine.py`
**Tests:** none — read-only verification

- [ ] Confirm `ActionExecutionEngine.__init__` accepts `action_time_resolver=None` kwarg.
- [ ] Confirm `_process_fleet_action_tick` calls `self._action_time_resolver.resolve_action_time(...)` when injected, falling back to `ActionTimeResolver.resolve_action_time(...)` static call when not.
- [ ] If either is missing → STOP. The DI seam was reverted. Surface this in plan.md Current State; this phase cannot proceed and the task should move to PROJ-493.

### Task 3.2: Rewrite test method at line 145-148
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py -k <method_name>`

- [ ] Identify the test method containing the lines 145-148 patch.
- [ ] Write a `StubActionTimeResolver` with the minimum interface: `.resolve_action_time(...)` returning the value the test expects.
- [ ] Replace the `patch('...ActionTimeResolver.resolve_action_time')` with `ActionExecutionEngine(..., action_time_resolver=StubActionTimeResolver(...))`.
- [ ] Delete the patch block; assert on the same observable outcome.
- [ ] Verify: targeted test passes.

### Task 3.3: Rewrite test method at line 199-202
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py -k <method_name>`

- [ ] Same pattern as Task 3.2 for this method.
- [ ] Reuse the `StubActionTimeResolver` from Task 3.2 (or extract to module-level if useful across files).
- [ ] Verify: targeted test passes.

### Task 3.4: Rewrite test method at line 442-445
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py -k <method_name>`

- [ ] Same pattern as Task 3.2 for this method.
- [ ] Verify: targeted test passes.

### Task 3.5: Close DI-2026-05-23-003
**File:** `AgentCoordination/discovered_issues/log.jsonl`
**Tests:** none

- [ ] After all 3 test rewrites pass, run the full file: `pytest tests/unit/strategy/engine/test_action_execution_engine.py`.
- [ ] Update the DI entry to status `resolved` with reference to this phase.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] DI-2026-05-23-003 marked resolved
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4

_Source: PROJ-479 audit finding F2 + Codex consult `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md`._
