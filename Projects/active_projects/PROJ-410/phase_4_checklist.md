# Phase 4: Turn-Boundary + Save/Load Hooks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-410 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire A-hook (manager polls active empire) and the `StrategyScreen.session` setter hook for save/load. After this phase all Phase 1 tests pass.

**Hard constraints:**
- Use **manager polling** (`facade.get_active_empire()`), not facade callbacks. Per Phase B swarm consensus and Decision 5 in `decisions.md`.
- All facade interactions through read accessors and `handle_command`. No direct session bypass — `tests/static_guards/test_facade_bypass_guard.py` must stay green.
- `BuildQueueScreen.on_active_player_changed()` must be idempotent (calling on a hidden screen with `panels=None` is a no-op).

---

## Tasks

### Task 4.1: Add `BuildQueueScreen.on_active_player_changed()` [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Add unit test in `test_build_queue_screen_lifecycle.py`.

- [ ] Add `def on_active_player_changed(self) -> None:` after `_request_close()` (~lines 823–838).
- [ ] Body:
  - If `self.is_visible()`, call `self.hide()`.
  - If `self.panels is not None`, call `self.panels.virtual_table.invalidate_widget_caches()`.
  - Reset cached references: `self.queue_sources = []`, `self.active_queue_source = None`. Other refs as needed (read source to confirm full set).
  - Idempotent — handle the `panels is None` case (shell-only screen) gracefully.
- [ ] Add `# PROJ-410:` comment with one-line rationale.
- [ ] Add unit tests:
  - After call: `is_visible()` is False, table caches invalidated (`_data_identity_dirty == True`), refs cleared.
  - Idempotent: call twice → same observable state, no errors.
  - Shell-only safety: call with `panels is None` → no error.

**Notes:**

---

### Task 4.2: Manager polling in `_open_build_queue()` [Medium]
**File:** `game/ui/screens/strategy_build_queue_manager.py:89–147`
**Tests:** Phase 1 Task 1.4 test passes.

- [ ] Determine the right facade accessor for "current active empire id". Read `game/strategy/facade/strategy_session_facade.py` and slices under `game/strategy/facade/slices/`. Likely candidates: `facade.get_active_empire()`, `facade.get_active_empire_id()`, or via `EventSlice.get_human_player_ids()` + turn rotation. Pick the cleanest single-call accessor.
- [ ] Add `self._last_active_empire_id: int | None = None` to manager `__init__`.
- [ ] In `_open_build_queue()` (around line 89), before reusing the cached `BuildQueueScreen`:
  - Read current empire id from facade.
  - If `self._last_active_empire_id is not None` and `current_id != self._last_active_empire_id`, call `self._screen.build_queue_screen.on_active_player_changed()` (or appropriate path on the manager) before continuing.
  - After the open succeeds: `self._last_active_empire_id = current_id`.
- [ ] Add unit test using existing manager-test fixtures: simulate two opens with different active empires; assert `on_active_player_changed()` is called between them.
- [ ] Add `# PROJ-410:` comment.

**Notes:**

---

### Task 4.3: Save/load hook in `StrategyScreen.session` setter [Medium]
**File:** `game/ui/screens/strategy_screen.py:231–248` (session setter)
**Tests:** Phase 1 Task 1.8 test passes.

- [ ] Read the current session setter to confirm the line range and the existing facade-rebind pattern.
- [ ] After the facade rebind (~line 247):
  - If `self.build_queue_screen is not None`, call `self.build_queue_screen.on_active_player_changed()`.
  - Reset `self._build_queue_manager._last_active_empire_id = None` so the next open re-detects the active empire from scratch.
- [ ] Add `# PROJ-410:` comment explaining the save/load context.
- [ ] Add unit test asserting the hook fires on session swap.

**Notes:**

---

### Task 4.4: Run scenarios (c) and save/load and verify pass [Simple]
**File:** (verification only)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k turn_boundary tests/integration/ui/build_queue_screen/ -k save_load`

- [ ] Phase 1 Task 1.4 test passes (turn boundary).
- [ ] Phase 1 Task 1.8 test passes (save/load).
- [ ] All other Phase 1 tests still pass.
- [ ] `TestRowPoolReuseGuard`, `TestSecondClickReuse`, lifecycle close+reopen tests still green.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` green.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All Phase 4 task checkboxes are checked.
- [ ] All 7+ Phase 1 tests pass.
- [ ] `pytest tests/ --testmon` clean.
- [ ] `TestRowPoolReuseGuard` green.
- [ ] Static guard `test_facade_bypass_guard.py` green.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update `plan.md` phase table row to `Complete`.
- [ ] Update `plan.md` Current State to point to Phase 5.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-410 4` — output PASSED.
