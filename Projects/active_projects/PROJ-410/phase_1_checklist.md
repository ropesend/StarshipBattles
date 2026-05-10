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

### Task 1.1: Verify the `selected_design` reset gap [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py` (read-only) + a test file (TBD based on outcome)
**Tests:** Test addition only.

- [ ] Read `game/ui/panels/build_queue_drag_handler.py:88–101` directly. Confirm whether `reset_state()` clears `self.selected_design`.
- [ ] If NOT cleared (gap exists): write a failing test asserting `selected_design is None` after `reset_state()`. Production fix lands in Phase 3 Task 3.3.
- [ ] If already cleared: write a regression test that locks in the existing behavior (so future refactors don't regress it). Skip Phase 3 Task 3.3.
- [ ] Update `decisions.md` with the verified outcome.

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
- [ ] Setup: empire 1 opens build queue on planet P1; close; advance turn (or simulate `facade.get_active_empire()` returning empire 2); empire 2 opens build queue on planet P2.
- [ ] Assertions:
  - empire 2 sees only P2's queues (no leak from P1),
  - `on_active_player_changed()` was invoked between the two opens,
  - manager's `_last_active_empire_id` updated to empire 2's id.
- [ ] Use a mock or fake `StrategySessionFacade` exposing `get_active_empire()`.
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
  - selector enumerates both yards,
  - selector buttons are visible (the container's visibility flag is True, OR pygame_gui visibility check returns True),
  - clicking a yard button dispatches correctly.
- [ ] Verify fails on current code (Yard-Selector Investigator confirmed this is a real container-visibility bug independent of the cache).

**Notes:**

---

### Task 1.8: Failing test — save/load does not leak prior session [Medium]
**File:** `tests/integration/ui/build_queue_screen/test_basics.py` (extend) OR a new file `test_save_load.py` in the same directory
**Tests:** `pytest tests/integration/ui/build_queue_screen/ -k save_load`

- [ ] Add `test_build_queue_screen_after_save_load_reflects_new_session`.
- [ ] Setup: open build queue with empire 1's planet; save game; load a *different* saved game with a different empire/planet; open build queue.
- [ ] Assertions:
  - new session's data appears (not prior session),
  - `BuildQueueScreen.on_active_player_changed()` was called when the session swapped,
  - manager's cached `_last_active_empire_id` reset.
- [ ] Use `SaveGameService` test fixtures.
- [ ] Verify fails on current code (Risk Assessor finding).

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All 7+ new tests are red on current `main` (or one test from 1.1 is green if it locks in existing behavior).
- [ ] `TestRowPoolReuseGuard` (`tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard`) — still green; confirms no production change leaked into Phase 1.
- [ ] `TestSecondClickReuse` (`tests/unit/ui/screens/test_strategy_build_queue_manager.py`) — still green.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` — still green.
- [ ] `decisions.md` updated with the Task 1.1 outcome.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update `plan.md` phase table row to `Complete`.
- [ ] Update `plan.md` Current State to point to Phase 2.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-410 1` — output PASSED.
