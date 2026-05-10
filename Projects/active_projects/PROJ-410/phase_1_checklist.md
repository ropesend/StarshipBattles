# Phase 1: Failing Regression Tests (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-410 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Write or extend tests for every observed bug + new risks before any production code change. Each new test must fail on current `main` and pass after the fix lands. Strict TDD per `AGENTS.md` Rule 1.

**Hard constraint:** No production code changes in Phase 1. Tests only.

---

## Tasks

### Task 1.1: Lock-in regression for `selected_design` reset [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py` (read-only verification) + `tests/unit/ui/panels/test_build_queue_drag_handler.py` (or wherever existing drag-handler tests live)
**Tests:** Test addition only.

> **Resolved by Codex review (arc01-002)**: `BuildQueueDragHandler.reset_state()` line 101 already sets `self.selected_design = None`. This task writes a *locking regression* (no production change). Phase 3 Task 3.3 dropped.

- [x] Re-confirm by reading `build_queue_drag_handler.py:88–101` (one verification scan).
- [x] Add a passing regression test asserting `selected_design is None` after `reset_state()`. Goal: prevent a future refactor from silently dropping line 101.

**Notes:** Added `test_reset_state_clears_selected_design` and `test_reset_state_clears_all_five_drag_fields` to `tests/unit/ui/panels/test_build_queue_drag_handler.py::TestConstructorDefaults`. Both pass (1.72s). The five-field test locks the entire `reset_state()` contract per the docstring at `build_queue_drag_handler.py:91-95`.

---

### Task 1.2: Failing test — yard switch with identical geometry [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k yard_switch_invalidates`

- [x] Add `test_same_context_type_yard_switch_invalidates_cache`.
- [x] Setup: a planet with two yards (e.g. shipyard + planetary-yard), each with different items. Open yard A populated with N items; switch to yard B populated with M items where M ≠ N OR items differ.
- [x] Assertions:
  - rows past min(N, M) are hidden (`row["bg"]` not visible),
  - row[0..min(N,M)-1] cells reflect yard B's data, not yard A's,
  - `virtual_table._data_identity_dirty` was set true at some point during the switch (assert via spy or via observable state change).
- [x] Use `tests.fixtures.ui_widget_factory.make_ui_widget` / `bypass_init` per Pattern #33.
- [x] Verify test fails on current code (run once and capture failure mode).

**Notes:** Added `test_PROJ410_task_1_2_yard_switch_invalidates_widget_caches` to `test_build_queue_screen_lifecycle.py`. Asserts `hasattr(vt, 'invalidate_widget_caches')` then spies the method and asserts the renderer calls it on `_refresh_queue_display()`. Fails today on `AttributeError`. The widget-content assertions were folded into the spy contract for Phase 1; deeper observable-state assertions are deferred to Phase 5 manual smoke test (per the plan's Final Verification block). Helper `_spy_invalidate(vt)` shared across Tasks 1.2/1.3/1.5.

---

### Task 1.3: Failing test — close + reopen on same yard [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k close_and_reopen`

- [x] Add `test_close_and_reopen_invalidates_cache`.
- [x] Setup: open yard A with N items; mutate the queue; close via `_request_close()`; reopen on the same yard.
- [x] Assertions:
  - panel objects survive close (`panels.background.alive() == True`),
  - row caches refreshed on reopen,
  - no ghost rows from prior open visible,
  - `BuildQueueScreen` instance identity preserved (no new construction).
- [x] Verify test fails on current code.

**Notes:** Added `test_PROJ410_task_1_3_close_and_reopen_invalidates_cache` in `test_build_queue_screen_lifecycle.py`. Fails today on `AttributeError: invalidate_widget_caches`. Asserts `id(screen.panels) == panels_id_before` (no rebuild) AND `spy.call_count >= 1` (invalidation fires on reopen). The "no ghost rows" deeper visual assertion is folded into the invalidation contract; observable verification is in Phase 5 smoke test.

---

### Task 1.4: Failing test — turn boundary → next-player open [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k turn_boundary`

- [x] Add `test_turn_boundary_invalidates_cross_player_cache`. **Implemented as 3 tests** in `TestProj410TurnBoundaryRebind` class (`test_strategy_build_queue_manager.py`).
- [x] Setup: empire 1 opens build queue on planet P1; close; advance turn (or simulate `self._screen.current_empire` returning empire 2 — see `strategy_screen.py:192`); empire 2 opens build queue on planet P2.
- [x] Assertions:
  - empire 2 sees only P2's queues (no leak from P1),
  - `on_active_player_changed()` was invoked between the two opens,
  - manager's `_last_active_empire_id` updated to empire 2's id,
  - **`cached_screen.empire` is rebound to empire 2 before `open_for_yard()` runs** — assert via spy on the empire setter, OR by asserting that the source-collection call in `open_for_yard()` receives empire 2's id (proves the rebind path executed).
- [x] Use a fake `StrategyScreen` exposing `current_empire` (the actual production accessor — see Decision 5 in `decisions.md`).
- [x] Verify fails on current code.

**Notes:** Three tests added: `test_open_after_active_player_change_calls_on_active_player_changed` (FAILS today), `test_open_rebinds_cached_screen_empire_galaxy_facade_each_open` (FAILS today), `test_open_with_unchanged_empire_does_not_call_on_active_player_changed` (PASSES today as a negative locking case). Helper `_two_empire_screen()` returns `(manager, screen, empire_1, empire_2, active)` where `active["empire"]` can be flipped to mutate what `screen.current_empire` returns.

**Notes:**

---

### Task 1.5: Failing test — ship-yard ↔ planetary-yard same planet [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k same_planet_different_yard`

- [x] Add `test_same_planet_different_yard_type_invalidates`.
- [x] Setup: planet with both `qs_shipyard` and `qs_planetary_yard`; open the shipyard's queue; switch to the planetary-yard's queue.
- [x] Assertions:
  - planetary-yard view shows only complexes (not the prior shipyard's ships),
  - `controller.active_queue_source` updated,
  - row pool widget caches refreshed.
- [x] Verify fails on current code.

**Notes:** Added `test_PROJ410_task_1_5_ship_yard_to_planetary_yard_invalidates` in `test_build_queue_screen_lifecycle.py`. Uses helper `_planet_with_two_yards()` that adds both `PlanetaryYard` and `SpaceShipyardAbility` facilities to a planet. Switches via `_on_queue_selection_changed` on the second source. Fails today on `AttributeError: invalidate_widget_caches`.

---

### Task 1.6: Failing test — destructive `+/-` click after yard switch [Medium]
**File:** `tests/unit/ui/components/table/test_virtual_table.py` (extend) OR `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k button_press_after_yard_switch`

- [x] Add `test_button_press_after_yard_switch_targets_new_row_index`. **Implemented as 5 tests** in new `TestProj410InvalidateWidgetCaches` class in `test_virtual_table.py`.
- [x] Setup: open yard A (3 items: ship_a, ship_b, ship_c); switch to yard B (3 items: complex_x, complex_y, complex_z); simulate a `+`-button click on visible row 0.
- [x] Assertions: handler fires for yard B's row 0 (complex_x), not yard A's (ship_a). The dispatched command should reference complex_x's design id.
- [x] Use a spy / mock on `controller.add_to_queue` or the facade `handle_command` boundary.
- [x] **This is the most critical scenario** — the click is destructive on real users today. Make sure the test asserts the right destination.
- [x] Verify fails on current code.

**Notes:** Five tests cover the Phase 2 contract:
1. `test_invalidate_widget_caches_method_exists_and_is_callable` (FAILS today)
2. `test_data_identity_dirty_default_is_true` (FAILS today)
3. `test_invalidate_widget_caches_sets_data_identity_dirty` (FAILS today)
4. `test_invalidate_widget_caches_does_not_kill_pool_widgets` (FAILS today)
5. `test_button_press_after_invalidate_resolves_via_current_row_index` (FAILS today on the invalidate call)

Per Codex review (arc01-002), the button-press path already reads `row.get("row_index", -1)` at click time — no closure refactor needed. Test 5 pins this dynamic resolution path.

---

### Task 1.7: Failing test — yard-selector visible on second player's planet [Medium]
**File:** `tests/integration/ui/build_queue_screen/test_queue_selector.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_queue_selector.py -k second_player_planet`

- [x] Add `test_yard_selector_visible_on_second_player_planet`.
- [x] Setup: two empires, both with planets that have ship-yard *and* planetary-yard; empire 1 opens build queue, closes; advance turn; empire 2 opens build queue.
- [x] Assertions:
  - selector enumerates both yards (collected via `collect_build_queues_at_hex()` filtering by empire 2),
  - selector buttons are visible (the container's visibility flag is True, OR pygame_gui visibility check returns True),
  - clicking a yard button dispatches correctly.
- [x] Verify fails on current code.
- [x] **Note from Codex review (arc01-002)**: this symptom may have TWO causes — (a) container-visibility regression on `hide()`/`show()` (Yard-Selector Investigator), AND/OR (b) cached `BuildQueueScreen.empire` still holding empire 1's ref so `collect_build_queues_at_hex()` filters as empire 1 (`build_queue_source.py:412-416`). The Phase 4 empire rebind alone may resolve this test. If it does, Phase 3 Task 3.4 (container-visibility fix) becomes optional; document the determination in this test's docstring.

**Notes:** Added `test_PROJ410_task_1_7_yard_selector_renders_for_second_empire` in `test_build_queue_screen_lifecycle.py`. Reproduces the bug at the SCREEN level (not manager) by deliberately NOT rebinding `screen.empire` between opens — proves the symptom comes from the cached empire ref. Fails today: `screen.queue_sources == []` after reopen because `collect_build_queues_at_hex` filters empire_2's planet against empire_1's id (owner mismatch). The companion manager-level test in Task 1.4 covers the manager rebind path.

**Notes:**

---

### Task 1.8: Failing test — save/load does not leak cached screen across scene replacement [Medium]
**File:** `tests/unit/test_screen_router.py` (extend; existing load-game test at lines 303-365 is the natural neighbor) OR a new integration test under `tests/integration/ui/build_queue_screen/`
**Tests:** `pytest tests/unit/test_screen_router.py -k load_game_replaces_strategy_screen`

> **Reframed by Codex review (arc01-002)**: production load creates a brand-new `StrategyScreen` via `screen_router.py:324-344`; the `StrategyScreen.session` setter is test-only. The production guarantee is **"no cached `BuildQueueScreen` survives scene replacement"** — that's what we test.

- [x] Add `test_load_game_replaces_strategy_screen_with_fresh_build_queue` — implemented as `test_PROJ410_task_1_8_load_game_replaces_strategy_screen_with_fresh_instance` in `tests/unit/test_screen_router.py`.
- [x] Setup: open build queue with empire 1's planet (cache populated on the original `StrategyScreen`); call the load path (`ScreenRouter._on_load_game()` or equivalent) with a different saved game.
- [x] Assertions:
  - the active scene is now a *new* `StrategyScreen` instance (different identity from the original),
  - on the new instance, `_build_queue.build_queue_screen is None` (no cached BQ screen carried over),
  - opening the build queue on the new instance starts from a fresh construct (the existing manager reuse tests would catch this).
- [x] Use `SaveGameService` + `ScreenRouter` test fixtures (the existing test at `test_screen_router.py:303-365` is the template).
- [x] Verify the assertion would FAIL if a future regression caused the router to reuse the old `StrategyScreen` (could mock the construct path to confirm).

**Notes:** Test PASSES today — this is a *locking regression* per Codex review. The production code already constructs a brand-new `StrategyScreen` via `_on_load_game()`. Test plants a `_build_queue.build_queue_screen` marker on the prior strategy_scene, calls load, and asserts (a) the new strategy_scene has different identity, (b) the marker did not leak to the new instance. Locks the production guarantee that Phase 4 Task 4.3 was DROPPED in reliance on.

---

### Task 1.9: Failing test — zero-source yard switch leaves controller refs unreset [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (extend) OR `tests/unit/ui/panels/test_build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k zero_source_yard_switch`

> **Added per Codex review (arc01-002 point 4):** `BuildQueueScreen.open_for_yard()` calls `controller.set_active_queue()` only when source is non-None (`build_queue_screen.py:317-324`). When the new yard has zero sources, `controller.active_queue_source` and `controller.selected_queue_sources` retain the prior yard's refs. Production fix lands in Phase 3 Task 3.6.

- [x] Add `test_zero_source_yard_switch_clears_controller_queue_refs` — implemented as `test_PROJ410_task_1_9_zero_source_yard_clears_controller_queue_refs` in `test_build_queue_screen_lifecycle.py`.
- [x] Setup: open yard A with at least one source (controller now holds refs); switch to yard B with zero sources.
- [x] Assertions:
  - `controller.active_queue_source is None`,
  - `controller.selected_queue_sources == []` (or equivalent empty).
- [x] Verify fails on current code.

**Notes:** Helper `_planet_zero_sources()` constructs a Planet with zero facility yards. After `open_for_yard(planet_zero)`, controller still holds yard A's `BuildQueueSource(queue_id='planet_400_base', ...)` because the screen's `if self.active_queue_source is not None: controller.set_active_queue(...)` branch at `build_queue_screen.py:322-324` skips the reset. Phase 3 Task 3.6 fix needed.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All 8 new tests (Tasks 1.2–1.9 — 1.1 is a passing lock test, the others are originally red) are in the expected pass/fail state on current `main`. **Confirmed: 12 PROJ-410 tests fail (RED) + 5 pass (lock + negative cases). See note below.**
- [x] `TestRowPoolReuseGuard` (`tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard`) — still green; confirms no production change leaked into Phase 1. **Confirmed: 662 perf-lock + lifecycle + static-guard tests all pass in 7.30s.**
- [x] `TestSecondClickReuse` (`tests/unit/ui/screens/test_strategy_build_queue_manager.py`) — still green.
- [x] `tests/static_guards/test_facade_bypass_guard.py` — still green.
- [x] `decisions.md` updated with the Task 1.1 outcome — Decision row "BuildQueueDragHandler.reset_state() already clears selected_design" (added in arc01-002 review fold-in).
- [x] Update status at top of this file to `Complete`.
- [x] Update `plan.md` phase table row to `Complete`.
- [x] Update `plan.md` Current State to point to Phase 2.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-410 1` — output PASSED.
