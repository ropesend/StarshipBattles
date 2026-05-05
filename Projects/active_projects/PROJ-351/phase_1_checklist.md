# Phase 1: T6.3 — ActionExecutionEngine consume injected resolver

**Status:** Not Started
**Objective:** Make `ActionExecutionEngine` use the injected `action_time_resolver` if non-None; flip the test that pinned the dead-DI surface.

---

## Tasks

### Task 1.1: Read DI declaration + consumer site [Simple]
**File:** `game/strategy/engine/action_execution_engine.py:55-68, 165-168` (read-only)

- [ ] Read lines 55-68 to confirm `self._action_time_resolver` is stored from constructor.
- [ ] Read lines 162-168 to find the static call: `ActionTimeResolver.resolve_action_time(...)` (per Codex review evidence).
- [ ] Confirm the pattern: stored field vs. static call ignored.

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
- [ ] Commit: `fix(action-execution-engine): consume injected action_time_resolver instead of static (PROJ-351 T6.3)`

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] T6.3 commit landed
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State to point to Phase 2
