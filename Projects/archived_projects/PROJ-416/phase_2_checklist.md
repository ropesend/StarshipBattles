# Phase 2: Remove Game.running legacy attribute

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-416 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove the `self.running` legacy attribute from `game.app.Game`. `RunLoop.running` is the canonical flag. This requires migrating BOTH 6 test usages AND 3 production write/read sites in `game/app.py` (confirmed by codex consult; see decisions.md for detail). Do NOT introduce `Game.is_running()` — tests should assert behavior (shutdown delegation) not attribute state.

Severity tier: Minor (test migration + attribute deletion + production refactor of bridging code).

---

## Tasks

### Task 2.1: TDD — write failing tests first

Before touching production code, write tests that will pass after the attribute is removed:

- [x] Write a test (or rewrite existing) for `_request_shutdown()`: assert it calls `_loop.request_shutdown()` — should not reference `game.running`
- [x] Write a test (or rewrite existing) for `_handle_strategy_action("quit_game")`: assert it calls `_request_shutdown()` — should not reference `game.running`
- [x] Write a test (or rewrite existing) for `run()`: assert it delegates to `_loop.run()` without requiring `game.running` to be set
- [x] Confirm the new tests fail with the current implementation (expected, since they are written against the to-be-refactored code)

### Task 2.2: Migrate 3 production write/read sites in game/app.py

**Production sites to remove/replace (all in `game/app.py`):**
- `_request_shutdown()` (line ~266): `self.running = False` — remove this line; `self._loop.request_shutdown()` below it is the canonical path
- `_handle_strategy_action("quit_game")` (line ~452): `self.running = False` — replace with `self._request_shutdown()` (routes through RunLoop properly)
- `run()` (lines ~502-507): bridge `self._loop.running = self.running` / `self.running = self._loop.running` — delete both bridge lines; `self._loop.run()` is the only call needed

- [x] Remove `self.running = False` from `_request_shutdown()` (keep `self._loop.request_shutdown()`)
- [x] Replace `self.running = False` in `_handle_strategy_action("quit_game")` with `self._request_shutdown()`
- [x] Delete the `self.running` bridge lines from `run()` at lines ~502-507

### Task 2.3: Delete the legacy attribute declaration

- [x] Delete the `self.running = True` line and legacy comment block at `game/app.py:124-127`

### Task 2.4: Migrate 6 test usages

**Test files (confirmed by grep):**
- `tests/unit/test_app_delegators.py:11,15,20,25` — 4 usages (manual `game.running = True` setup + `assert game.running is False`)
- `tests/unit/ui/screens/test_strategy_menu_actions.py:276,316` — 2 usages

- [x] Rewrite `tests/unit/test_app_delegators.py`: replace `game.running = True` setup with loop-level setup; replace `assert game.running is False` with behavior assertions (e.g., assert `_loop.request_shutdown()` was called)
- [x] Rewrite `tests/unit/ui/screens/test_strategy_menu_actions.py`: same approach

### Task 2.5: Verify

- [x] `pytest tests/unit/test_app_delegators.py tests/unit/ui/screens/test_strategy_menu_actions.py tests/unit/test_run_loop.py` passes
- [x] `grep -rn 'Game\.running\|game\.running\|self\.running' game/app.py` returns zero hits
- [x] `grep -rn '\.running' tests/unit/test_app_delegators.py tests/unit/ui/screens/test_strategy_menu_actions.py` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
