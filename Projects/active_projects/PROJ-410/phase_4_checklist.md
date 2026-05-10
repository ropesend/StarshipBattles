# Phase 4: Turn-Boundary Hook

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-410 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire A-hook (manager polls active empire **and rebinds cached screen domain context**) so a player change between opens flushes state AND queries the new empire's data. After this phase all Phase 1 tests pass.

**Hard constraints:**
- Use **manager polling** (`self._screen.current_empire.id` per `strategy_screen.py:192`), not facade callbacks. Per Phase B swarm consensus + Codex review (Decision 5).
- All facade interactions through read accessors and `handle_command`. No direct session bypass — `tests/static_guards/test_facade_bypass_guard.py` must stay green.
- `BuildQueueScreen.on_active_player_changed()` must be idempotent (calling on a hidden screen with `panels=None` is a no-op).
- **Rebind cached `BuildQueueScreen.empire`/`galaxy`/`facade` BEFORE every `open_for_yard()` when the empire id changed.** Without this, the cached screen still queries as the previous empire (Codex point 1, evidence: `build_queue_screen.py:95,113-114` + `build_queue_source.py:412-416`).

---

## Tasks

### Task 4.1: Add `BuildQueueScreen.on_active_player_changed()` [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Add unit test in `test_build_queue_screen_lifecycle.py`.

- [ ] Add `def on_active_player_changed(self) -> None:` after `_request_close()` (~lines 823–838).
- [ ] Body:
  - If `self.is_visible()`, call `self.hide()`.
  - If `self.panels is not None`, call `self.panels.<virtual_table_path>.invalidate_widget_caches()`. Read `BuildQueuePanels` dataclass at `build_queue_panel_factory.py:50` to confirm the exact attribute path (likely `self.panels.queue_panel.virtual_table` or similar — read source).
  - Reset cached references that should not survive a player change: `self.queue_sources = []`, `self.active_queue_source = None`. The screen-side rebind of `self.empire` / `self.galaxy` / `self.facade` happens in the **manager** (Task 4.2), not here, so `on_active_player_changed()` only does the *flush* half — leaves rebinding to the caller. Read source carefully to confirm full reset set.
  - Idempotent — handle the `panels is None` case (shell-only screen) gracefully.
- [ ] Add `# PROJ-410:` comment with one-line rationale.
- [ ] Add unit tests:
  - After call: `is_visible()` is False, table caches invalidated (`_data_identity_dirty == True`), `queue_sources`/`active_queue_source` cleared.
  - Idempotent: call twice → same observable state, no errors.
  - Shell-only safety: call with `panels is None` → no error.

**Notes:**

---

### Task 4.2: Manager polling + cached-screen rebind in `_open_build_queue()` [Medium]
**File:** `game/ui/screens/strategy_build_queue_manager.py:89–147`
**Tests:** Phase 1 Tasks 1.4 and 1.7 pass.

- [ ] Confirm the active-empire accessor: `self._screen.current_empire.id` (`strategy_screen.py:192`). Read it once to verify the property still exists and returns the rotated empire (per BUG-125 docstring).
- [ ] Add `self._last_active_empire_id: int | None = None` to manager `__init__`.
- [ ] In `_open_build_queue()` (around line 89), before reusing the cached `BuildQueueScreen`:
  - Read `current_empire = self._screen.current_empire`; `current_id = current_empire.id`.
  - If `self._last_active_empire_id is not None and current_id != self._last_active_empire_id`:
    - Call `cached_screen.on_active_player_changed()` to flush widget/queue state.
  - **Always before `open_for_yard()` (whether or not change detected)** — rebind cached domain context:
    - `cached_screen.facade = self._screen.facade` (or whatever the screen needs — confirm via `build_queue_screen.py:95`)
    - `cached_screen.galaxy = self._screen.galaxy`
    - `cached_screen.empire = current_empire`
  - After the open succeeds: `self._last_active_empire_id = current_id`.
  - **Why rebind unconditionally**: the cached screen's `self.empire` was set at construction (`build_queue_screen.py:114`); on every reopen we want it to reflect *now*'s active empire, not the one in scope when the screen was first built. Cheaper than tracking a separate "context dirty" flag.
- [ ] Add unit tests:
  - Two opens with the SAME active empire → `on_active_player_changed()` NOT called, but rebind still runs (idempotent).
  - Two opens with DIFFERENT active empires → `on_active_player_changed()` IS called between them, rebind runs.
  - Assert `cached_screen.empire` reflects the second-call empire after the second open (proves rebind happened).
  - Assert that on the second-player open, `collect_build_queues_at_hex()` (or the source-collection call in `open_for_yard()`) receives the new empire's id, not the first's.
- [ ] Add `# PROJ-410:` comment.

**Notes:**

---

### Task 4.3: DROPPED [n/a]

> **Dropped per Codex review (arc01-004) and confirmed in arc01-006.** The `StrategyScreen.session` setter is test-only; production load creates a fresh `StrategyScreen` via `screen_router.py:324-344`. The production guarantee that no cached BQ screen leaks across scene replacement is asserted by Phase 1 Task 1.8 — no Phase 4 work needed. If a future production flow ever uses `StrategyScreen.session = ...` for a real mid-session swap, that feature should add its own failing test and cleanup hook then. No production edit; no checklist items.

---

### Task 4.4: Run scenarios (c), (yard-selector), and save/load and verify pass [Simple]
**File:** (verification only)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k "turn_boundary or yard_selector_visible_on_second_player" tests/integration/ui/build_queue_screen/ -k save_load`

- [ ] Phase 1 Task 1.4 test passes (turn boundary; rebind verified).
- [ ] Phase 1 Task 1.7 test passes (yard-selector visible on second player). May pass purely from the empire rebind in this phase even before any container-visibility fix in Phase 3 Task 3.4. If so, note in the test file and update Task 3.4's status.
- [ ] Phase 1 Task 1.8 test passes (save/load: new screen has `build_queue_screen is None`).
- [ ] All other Phase 1 tests still pass.
- [ ] `TestRowPoolReuseGuard`, `TestSecondClickReuse`, lifecycle close+reopen tests still green.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` green.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All Phase 4 task checkboxes are checked.
- [ ] All 7+ Phase 1 tests pass (including the new 1.9 zero-source test from Phase 3).
- [ ] `pytest tests/ --testmon` clean.
- [ ] `TestRowPoolReuseGuard` green.
- [ ] Static guard `test_facade_bypass_guard.py` green.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update `plan.md` phase table row to `Complete`.
- [ ] Update `plan.md` Current State to point to Phase 5.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-410 4` — output PASSED.
