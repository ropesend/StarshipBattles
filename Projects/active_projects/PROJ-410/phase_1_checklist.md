# Phase 1: Failing Regression Tests (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-410 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Write or extend tests for every observed bug + new risks before any production code change. Each new test must fail on current `main` and pass after the fix lands. Strict TDD per `AGENTS.md` Rule 1.

**Hard constraint:** No production code changes in Phase 1. Tests only.

---

## Tasks

### Task 1.1: Lock-in regression for `selected_design` reset [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py` (read-only verification) + `tests/unit/ui/panels/test_build_queue_drag_handler.py` (or wherever existing drag-handler tests live)
**Tests:** Test addition only.

> **Resolved by Codex review (arc01-002)**: `BuildQueueDragHandler.reset_state()` line 101 already sets `self.selected_design = None`. This task writes a *locking regression* (no production change). Phase 3 Task 3.3 dropped.

- [ ] Re-confirm by reading `build_queue_drag_handler.py:88–101` (one verification scan).
- [ ] Add a passing regression test asserting `selected_design is None` after `reset_state()`. Goal: prevent a future refactor from silently dropping line 101.

**Notes:**

---

### Task 1.2: Failing test — yard switch with identical geometry [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k yard_switch_invalidates`

- [ ] Add `test_same_context_type_yard_switch_invalidates_cache`.
- [ ] Setup: a planet with two yards (e.g. shipyard + planetary-yard), each with different items. Open yard A populated with N items; switch to yard B populated with M items where M ≠ N OR items differ.
- [ ] Assertions:
  - rows past min(N, M) are hidden (`row["bg"]` not visible),
  - row[0..min(N,M)-1] cells reflect yard B's data, not yard A's,
  - `virtual_table._data_identity_dirty` was set true at some point during the switch (assert via spy or via observable state change).
- [ ] Use `tests.fixtures.ui_widget_factory.make_ui_widget` / `bypass_init` per Pattern #33.
- [ ] Verify test fails on current code (run once and capture failure mode).

**Notes:**

---

### Task 1.3: Failing test — close + reopen on same yard [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k close_and_reopen`

- [ ] Add `test_close_and_reopen_invalidates_cache`.
- [ ] Setup: open yard A with N items; mutate the queue; close via `_request_close()`; reopen on the same yard.
- [ ] Assertions:
  - panel objects survive close (`panels.background.alive() == True`),
  - row caches refreshed on reopen,
  - no ghost rows from prior open visible,
  - `BuildQueueScreen` instance identity preserved (no new construction).
- [ ] Verify test fails on current code.

**Notes:**

---

### Task 1.4: Failing test — turn boundary → next-player open [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k turn_boundary`

- [ ] Add `test_turn_boundary_invalidates_cross_player_cache`.
- [ ] Setup: empire 1 opens build queue on planet P1; close; advance turn (or simulate `self._screen.current_empire` returning empire 2 — see `strategy_screen.py:192`); empire 2 opens build queue on planet P2.
- [ ] Assertions:
  - empire 2 sees only P2's queues (no leak from P1),
  - `on_active_player_changed()` was invoked between the two opens,
  - manager's `_last_active_empire_id` updated to empire 2's id,
  - **`cached_screen.empire` is rebound to empire 2 before `open_for_yard()` runs** — assert via spy on the empire setter, OR by asserting that the source-collection call in `open_for_yard()` receives empire 2's id (proves the rebind path executed).
- [ ] Use a fake `StrategyScreen` exposing `current_empire` (the actual production accessor — see Decision 5 in `decisions.md`).
- [ ] Verify fails on current code.

**Notes:**

---

### Task 1.5: Failing test — ship-yard ↔ planetary-yard same planet [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k same_planet_different_yard`

- [ ] Add `test_same_planet_different_yard_type_invalidates`.
- [ ] Setup: planet with both `qs_shipyard` and `qs_planetary_yard`; open the shipyard's queue; switch to the planetary-yard's queue.
- [ ] Assertions:
  - planetary-yard view shows only complexes (not the prior shipyard's ships),
  - `controller.active_queue_source` updated,
  - row pool widget caches refreshed.
- [ ] Verify fails on current code.

**Notes:**

---

### Task 1.6: Failing test — destructive `+/-` click after yard switch [Medium]
**File:** `tests/unit/ui/components/table/test_virtual_table.py` (extend) OR `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k button_press_after_yard_switch`

- [ ] Add `test_button_press_after_yard_switch_targets_new_row_index`.
- [ ] Setup: open yard A (3 items: ship_a, ship_b, ship_c); switch to yard B (3 items: complex_x, complex_y, complex_z); simulate a `+`-button click on visible row 0.
- [ ] Assertions: handler fires for yard B's row 0 (complex_x), not yard A's (ship_a). The dispatched command should reference complex_x's design id.
- [ ] Use a spy / mock on `controller.add_to_queue` or the facade `handle_command` boundary.
- [ ] **This is the most critical scenario** — the click is destructive on real users today. Make sure the test asserts the right destination.
- [ ] Verify fails on current code.

**Notes:**

---

### Task 1.7: Failing test — yard-selector visible on second player's planet [Medium]
**File:** `tests/integration/ui/build_queue_screen/test_queue_selector.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_queue_selector.py -k second_player_planet`

- [ ] Add `test_yard_selector_visible_on_second_player_planet`.
- [ ] Setup: two empires, both with planets that have ship-yard *and* planetary-yard; empire 1 opens build queue, closes; advance turn; empire 2 opens build queue.
- [ ] Assertions:
  - selector enumerates both yards (collected via `collect_build_queues_at_hex()` filtering by empire 2),
  - selector buttons are visible (the container's visibility flag is True, OR pygame_gui visibility check returns True),
  - clicking a yard button dispatches correctly.
- [ ] Verify fails on current code.
- [ ] **Note from Codex review (arc01-002)**: this symptom may have TWO causes — (a) container-visibility regression on `hide()`/`show()` (Yard-Selector Investigator), AND/OR (b) cached `BuildQueueScreen.empire` still holding empire 1's ref so `collect_build_queues_at_hex()` filters as empire 1 (`build_queue_source.py:412-416`). The Phase 4 empire rebind alone may resolve this test. If it does, Phase 3 Task 3.4 (container-visibility fix) becomes optional; document the determination in this test's docstring.

**Notes:**

---

### Task 1.8: Failing test — save/load does not leak cached screen across scene replacement [Medium]
**File:** `tests/unit/test_screen_router.py` (extend; existing load-game test at lines 303-365 is the natural neighbor) OR a new integration test under `tests/integration/ui/build_queue_screen/`
**Tests:** `pytest tests/unit/test_screen_router.py -k load_game_replaces_strategy_screen`

> **Reframed by Codex review (arc01-002)**: production load creates a brand-new `StrategyScreen` via `screen_router.py:324-344`; the `StrategyScreen.session` setter is test-only. The production guarantee is **"no cached `BuildQueueScreen` survives scene replacement"** — that's what we test.

- [ ] Add `test_load_game_replaces_strategy_screen_with_fresh_build_queue`.
- [ ] Setup: open build queue with empire 1's planet (cache populated on the original `StrategyScreen`); call the load path (`ScreenRouter._on_load_game()` or equivalent) with a different saved game.
- [ ] Assertions:
  - the active scene is now a *new* `StrategyScreen` instance (different identity from the original),
  - on the new instance, `_build_queue.build_queue_screen is None` (no cached BQ screen carried over),
  - opening the build queue on the new instance starts from a fresh construct (the existing manager reuse tests would catch this).
- [ ] Use `SaveGameService` + `ScreenRouter` test fixtures (the existing test at `test_screen_router.py:303-365` is the template).
- [ ] Verify the assertion would FAIL if a future regression caused the router to reuse the old `StrategyScreen` (could mock the construct path to confirm).

**Notes:**

---

### Task 1.9: Failing test — zero-source yard switch leaves controller refs unreset [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (extend) OR `tests/unit/ui/panels/test_build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k zero_source_yard_switch`

> **Added per Codex review (arc01-002 point 4):** `BuildQueueScreen.open_for_yard()` calls `controller.set_active_queue()` only when source is non-None (`build_queue_screen.py:317-324`). When the new yard has zero sources, `controller.active_queue_source` and `controller.selected_queue_sources` retain the prior yard's refs. Production fix lands in Phase 3 Task 3.6.

- [ ] Add `test_zero_source_yard_switch_clears_controller_queue_refs`.
- [ ] Setup: open yard A with at least one source (controller now holds refs); switch to yard B with zero sources.
- [ ] Assertions:
  - `controller.active_queue_source is None`,
  - `controller.selected_queue_sources == []` (or equivalent empty).
- [ ] Verify fails on current code.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All 8 new tests (Tasks 1.2–1.9 — 1.1 is a passing lock test, the others are originally red) are in the expected pass/fail state on current `main`.
- [ ] `TestRowPoolReuseGuard` (`tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard`) — still green; confirms no production change leaked into Phase 1.
- [ ] `TestSecondClickReuse` (`tests/unit/ui/screens/test_strategy_build_queue_manager.py`) — still green.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` — still green.
- [ ] `decisions.md` updated with the Task 1.1 outcome.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update `plan.md` phase table row to `Complete`.
- [ ] Update `plan.md` Current State to point to Phase 2.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-410 1` — output PASSED.
