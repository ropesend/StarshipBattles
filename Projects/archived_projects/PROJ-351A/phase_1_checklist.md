# Phase 1: TBD

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-351 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** [What this phase accomplishes]

---

## Tasks

### Task 1.1: [Task Name] [Simple/Medium/Complex]
**File:** `path/to/file.py`
**Tests:** `pytest tests/path/`

- [ ] Subtask with specific action
- [ ] Another subtask
- [ ] Verify: [what to check]

**Notes:**

### Task 1.2: Refactor execution path to consume injected resolver [Medium]
**File:** `game/strategy/engine/action_execution_engine.py:165-168`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine* -x` — initially expect 1 failure (the dead-DI test)

- [ ] Replace static `ActionTimeResolver.resolve_action_time(...)` with: use `self._action_time_resolver.resolve_action_time(...)` if `self._action_time_resolver is not None`, else fall back to static (preserves the no-injection default path).
- [ ] Run targeted slice — the dead-DI test will fail (it pins "never consulted"); other tests must pass.

**Notes:**

### Task 1.3: Rewrite the dead-DI pin test [Medium]
**File:** `tests/unit/strategy/engine/test_action_execution_engine_gaps.py:128-156`

- [ ] Read the test to understand what it asserts.
- [ ] Flip: assert that when an `action_time_resolver` is injected, the engine's execution path calls it (e.g., via `mock.assert_called_once_with(...)` matching the action arg) rather than the static class method.
- [ ] Optionally add a second test asserting the no-injection fallback still works (engine with `action_time_resolver=None` still resolves times via the static path).

**Notes:**

### Task 1.4: Targeted slice + commit [Simple]
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine* -x -q`

- [ ] All pass.
- [ ] `git status` — verify no unrelated files staged.
- [ ] Commit: `fix(action-execution-engine): consume injected action_time_resolver instead of static (PROJ-351A T6.3)`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
