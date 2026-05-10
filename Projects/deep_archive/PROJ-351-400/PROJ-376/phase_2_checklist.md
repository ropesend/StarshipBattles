# Phase 2: Instance reuse — manager constructs once, calls `open_for_yard()` thereafter

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-376 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/ui/screens/build_queue_screen.py` (delete `_close()`, route close-button + Esc through `hide()` + `on_close()`)
- `game/ui/screens/strategy_build_queue_manager.py` (3 entry points + close callback)
- `game/ui/screens/strategy_event_router.py:58` (migrate to `is_visible()`)
- `game/ui/screens/strategy_input_handler.py:55-56` (migrate to `is_visible()`)
- `game/ui/screens/strategy_screen.py:246` (migrate to `is_visible()`)
- `tests/unit/ui/screens/test_strategy_build_queue_manager.py` (assert `open_for_yard` called on subsequent opens)
- `tests/integration/ui/build_queue_screen/test_basics.py:188` (`_close()` → `hide()`)
- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (Phase 2-specific tests)
**Objective:** `StrategyBuildQueueManager` constructs `BuildQueueScreen` lazily on first build-yard click and reuses the instance for every subsequent open via `open_for_yard()`. Replace `_close()` with `hide()`. Replace null-the-slot close-callback with hide-the-screen close-callback. Migrate three `is not None` callsites to `is_visible()` (input/draw/modal-block — see decisions.md row 4).

---

## Pre-flight

- [ ] Re-read `Projects/active_projects/PROJ-376/decisions.md` rows 4 (`is_visible()` migration), 6 (`hide()` semantics), 7 (`hide()` does not invoke `on_close`).
- [ ] Read `game/ui/screens/strategy_build_queue_manager.py` end-to-end (~272 LOC).
- [ ] Read `game/ui/screens/strategy_input_handler.py:50-60`.
- [ ] Read `game/ui/screens/strategy_event_router.py:50-80`.
- [ ] Read `game/ui/screens/strategy_screen.py:115-118, 240-250`.
- [ ] `grep -rn "build_queue_screen" game/ tests/ -l` — capture every reference; ensure all are accounted for in the plan.

---

## Tasks

### Task 2.1: Phase-2 lifecycle tests (TDD) [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (extend)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -v`

Add tests; confirm fail; implementation lands in 2.2-2.5.

- [ ] `test_manager_constructs_screen_once_across_n_clicks` — patch `BuildQueueScreen` in the manager module; call `on_build_yard_click` 3× on the same planet (calling `_on_build_queue_close` between clicks). Assert: `BuildQueueScreen.__init__` called exactly once; `open_for_yard` called 3 times.
- [ ] `test_close_callback_does_not_null_screen_slot` — open + close; assert `screen.build_queue_screen is not None` after close.
- [ ] `test_close_callback_calls_hide_not_kill` — open, mock `screen.build_queue_screen.hide` as a spy; trigger close. Assert `hide.called`; assert `panels.background.alive` still True.
- [ ] `test_feat17_pause_label_resyncs_on_yard_switch` — open yard A with `is_paused=True`; verify pause-button label "Unpause Build Queue". Call `open_for_yard(yard_b)` where `is_paused=False`. Assert label "Pause Build Queue".
- [ ] `test_planet_selection_window_killed_on_close_after_partial_selection` — open screen, set `screen.planet_selection_window = MagicMock()`, fire close-button event. Assert: window's `kill()` called; slot is None; `panels.background.alive` is True.
- [ ] `test_input_handler_visibility_gate_skips_hidden_screen` — mock `scene.build_queue_screen` with `is_visible() → False`; assert `handle_event` NOT called on the screen.
- [ ] `test_draw_visibility_gate_skips_hidden_screen` — same shape but for `strategy_screen.draw`.
- [ ] **Verify:** Run; **all tests fail** on Phase 1 code (no manager change).

**Notes:**

### Task 2.2: Replace `_close()` with `hide()` + on_close in `BuildQueueScreen` [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Task 2.1 + `pytest tests/integration/ui/build_queue_screen/ -v`

- [ ] `grep -n "_close" game/ui/screens/build_queue_screen.py` — capture all callers (expected: line 435 close button, line 562 keydown `BUILD_QUEUE_CLOSE` action, line 639 method def).
- [ ] In `_handle_button_press` (line 412), the close-button branch (line 434-435) currently calls `self._close()`. Change to `self.hide(); self.on_close()` — explicit two-step per decisions.md row 7.
- [ ] In `_handle_keydown` (line 556), the `BUILD_QUEUE_CLOSE` branch (line 561-563) currently calls `self._close()`. Same change.
- [ ] **Delete `_close()` entirely** (lines 639-649). Do not leave a thin wrapper — explicit per CLAUDE.md "Root Cause Fixes" (no shims).
- [ ] **Verify:** `grep -n "_close" game/ui/screens/build_queue_screen.py` returns nothing.
- [ ] **Verify:** `tests/integration/ui/build_queue_screen/test_basics.py:188` — currently calls `build_queue_screen._close()`. Change to `build_queue_screen.hide()` + manual `on_close()` if the test asserts on close-callback side effects.

**Notes:** PROJ-373 design.md R2.4 noted `manager.update(0)` in `_close()` was load-bearing for pygame_gui cleanup. Since `hide()` already includes `manager.update(0)` (Phase 1 Task 1.4), this is preserved.

### Task 2.3: Refactor `StrategyBuildQueueManager` to extract `_open_build_queue` helper [Medium]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_build_queue_manager.py -v`

- [ ] Add private helper:
  ```python
  def _open_build_queue(
      self,
      yard,  # Planet | Fleet
      hex_coord: 'HexCoord',
      portrait_surface: Optional[pygame.Surface],
  ) -> None:
      """Open the build queue for the given yard.

      PROJ-376: Lazy first-construction; reuse existing instance on
      subsequent calls via open_for_yard().
      """
      self._screen.ui.hide_ui()
      empire_id = yard.owner_id if hasattr(yard, 'owner_id') else self._screen.current_empire.id
      design_library = DesignLibrary(self._screen.session.save_path, empire_id)
      design_loader = DesignLoaderAdapter(registry_provider=_get_registries())

      if self._screen.build_queue_screen is None:
          self._screen.build_queue_screen = BuildQueueScreen(
              self._screen.ui.manager,
              build_context=None,            # shell-only
              session=self._screen.session,
              on_close_callback=self._on_build_queue_close,
              portrait_surface=portrait_surface,
              design_library=design_library,
              design_loader=design_loader,
              hex_coord=None,
              galaxy=self._screen.session.galaxy,
              empire=self._screen.current_empire,
              input_mapper=self._screen.input_mapper,
              facade=self._screen.facade,
              initial_yard=None,             # PROJ-376
          )

      # design_library may differ per yard (per-empire); re-bind on the
      # screen and its drag handler before the open path consumes it.
      self._screen.build_queue_screen.design_library = design_library
      self._screen.build_queue_screen.design_loader = design_loader

      self._screen.build_queue_screen.open_for_yard(
          yard, hex_coord=hex_coord, portrait_surface=portrait_surface
      )
      logger.info(f"Opened build queue for {yard.context_type} '{yard.name}'")
  ```
- [ ] Replace `on_build_yard_click` (lines 71-114) body — keep selection/ownership guard, drop the entry guard at line 74-76 and the construction block at lines 100-113. Replace with `self._open_build_queue(planet, hex_coord, portrait_surface)`. Compute `hex_coord` and `portrait_surface` first (lines 84-96 stay).
- [ ] Replace `on_navigate_to_hex_build` (lines 175-227) similarly. Drop entry guard at 186-188; drop construction block at 213-226. Add `self._open_build_queue(entity, hex_coord, portrait_surface)`.
- [ ] Replace `on_fleet_build_click` (lines 229-271) similarly. Drop entry guard at 232-234; drop construction block at 257-270. Add `self._open_build_queue(fleet, hex_coord, portrait_surface)`.
- [ ] **Verify:** the 3 entry-point methods are now ~10-15 lines each, all converging on `_open_build_queue`. The `if is_planet/is_fleet` ownership/capability guards stay in their respective entry points (logic differs per entry point).
- [ ] **Verify:** `test_manager_constructs_screen_once_across_n_clicks` (Task 2.1) passes.

**Notes:** Decisions.md row 5 — `_open_build_queue` accepts `hex_coord` and `portrait_surface` so each entry point computes them with the correct semantics (planet has `parent_sys.global_location + planet.location`; fleet has `fleet.location`; navigate_to_hex_build has `hex_coord` already). Don't try to push the hex math into `BuildQueueScreen`.

### Task 2.4: Update `_on_build_queue_close` — call `hide()` instead of nulling [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py:116-148`
**Tests:** Task 2.1 tests

- [ ] Today's `_on_build_queue_close`:
  - line 125: reads `queue_sources` from the screen (must work — the screen is still alive).
  - line 135: sets `self._screen.build_queue_screen = None` — **delete this line**.
  - line 137-138: `ui.show_ui()` — keep.
  - line 140-147: refresh selected-object detail panel — keep.
- [ ] Close-button/Esc handler in Task 2.2 calls `self.hide(); self.on_close()`. `_on_build_queue_close` does NOT call `hide()` again. Single source of truth.
- [ ] **Verify:** `test_close_callback_does_not_call_hide_again` (the close callback must NOT call `hide()`) and `test_close_callback_does_not_null_screen_slot` pass.

**Notes:** The fleet BUILD-order auto-issue logic (line 124-133) is unchanged. By the time `_on_build_queue_close` runs the screen is already hidden because the close-button handler in Task 2.2 calls `self.hide(); self.on_close()` in that order. Calling `hide()` again from the callback would duplicate the work and split the source of truth — the close-button/Esc handler is the only place that hides.

### Task 2.5: Migrate `is not None` checks to `is_visible()` [Simple]
**Tests:** Task 2.1 visibility-gate tests

- [ ] `game/ui/screens/strategy_input_handler.py:55-56`:
  ```python
  # Before:
  if self.scene.build_queue_screen is not None:
      self.scene.build_queue_screen.handle_event(event)
  # After:
  if self.scene.build_queue_screen is not None and self.scene.build_queue_screen.is_visible():
      self.scene.build_queue_screen.handle_event(event)
  ```
- [ ] `game/ui/screens/strategy_screen.py:246-247`:
  ```python
  # Before:
  if self.build_queue_screen is not None:
      self.build_queue_screen.draw(screen)
  # After:
  if self.build_queue_screen is not None and self.build_queue_screen.is_visible():
      self.build_queue_screen.draw(screen)
  ```
- [ ] `game/ui/screens/strategy_event_router.py:58`:
  ```python
  # Before:
  if self.ui.scene.build_queue_screen is not None:
      return True
  # After:
  if self.ui.scene.build_queue_screen is not None and self.ui.scene.build_queue_screen.is_visible():
      return True
  ```
  (per decisions.md row 4 — visible build queue means modal is open from the router's perspective; hidden = galaxy is back, no modal block.)
- [ ] **Verify:** `test_input_handler_visibility_gate_skips_hidden_screen` and `test_draw_visibility_gate_skips_hidden_screen` pass; existing modal-related tests in `tests/unit/ui/screens/test_strategy_event_router*.py` still pass.

**Notes:** No other production callers of `scene.build_queue_screen is not None` exist per the grep capture in Pre-flight. Verify.

### Task 2.6: Update existing manager tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_build_queue_manager.py`
**Tests:** the file itself

- [ ] Existing test `test_opens_build_queue_for_owned_planet` (lines 79-102) calls `MockBQS.assert_called_once()` — still valid for first open. Keep as-is.
- [ ] Add new test `test_second_click_calls_open_for_yard_not_construct`: patch `BuildQueueScreen`. First click constructs. Second click on same/different planet — assert `MockBQS` called exactly once total; assert `mock_screen_instance.open_for_yard.called`.
- [ ] Update `test_ignores_when_build_queue_already_open` (lines 52-59) — today this asserts the entry guard at line 74. Post-Phase-2 there is no entry guard; the manager just calls `open_for_yard` again. Either delete this test (semantics changed) OR rewrite to "second click doesn't crash and re-opens". **Decision: rewrite.**
- [ ] **Verify:** focused test file green.

**Notes:**

### Task 2.7: Manual smoke test [Simple]
**Tests:** Manual

- [ ] Launch the game.
- [ ] Open + close build queue at home planet 5×. Confirm subsequent opens visibly faster (target <1s subjective).
- [ ] Switch to a different owned planet's build queue. Confirm correct yard data + queue contents.
- [ ] Switch to a fleet's build queue (planet → fleet transition). Confirm correct fleet panel layout.
- [ ] Switch back to a planet. Confirm correct planet panel layout (PlanetReportPanel).
- [ ] Drag-and-drop a queue item; close; reopen at same yard. Drag again — confirm no stale drag preview / no ghost row.
- [ ] Open the build queue at a planet, click a complex (triggers `_prompt_target_planet` if multi-colony hex), do NOT select — close the build queue. Reopen — confirm no leftover PlanetSelectionWindow.
- [ ] Pause a queue (FEAT-17). Close. Reopen — confirm pause-button label reads "Unpause Build Queue".
- [ ] No console warnings/errors throughout.

**Notes:**

### Task 2.8: Sharded suite + commit [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] `git status --short` confirms only Phase 2 files dirty.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-376 phase_2 --repo .worktrees/phases/PROJ-376/phase_2`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BuildQueueScreen._close()` no longer exists (grep regression)
- [ ] `StrategyBuildQueueManager` constructs `BuildQueueScreen` exactly once across multiple opens (lazy first-open)
- [ ] `_on_build_queue_close` does NOT null `self._screen.build_queue_screen`
- [ ] Three `is not None` checks at input-handler / strategy-screen / event-router migrated to `is_visible()`
- [ ] Manual smoke (5 cycles + planet→fleet→planet + drag + planet-selection abort + pause toggle) passes clean
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
