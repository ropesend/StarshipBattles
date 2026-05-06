# Phase 2: Reuse `BuildQueueScreen` instance across opens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-373 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Deferred — see `decisions.md` (2026-05-06 row). Pre-flight investigation surfaced significant risk: every panel created by `BuildQueuePanelFactory` embeds yard-specific references (Planet vs Fleet `build_context`), the `controller`/`drag_handler` collaborators hold their own `build_context`/`design_library` references, and `BuildQueueScreen.__init__` orchestrates all of these via FEAT-17 pause-toggle button state, modal-window layering with `PlanetSelectionWindow`, and `_apply_tooltips`. A correct `open_for_yard()` must thread through all of those without breaking event routing — beyond the 30-minute investigation budget the project guidance set as the deferral threshold. Phases 1 + 3 + 4 ship independently; Phase 3's row-pool guard pays off when Phase 2 eventually lands.
**Objective:** Construct `BuildQueueScreen` once per `StrategyBuildQueueManager` lifetime; subsequent opens go through new `open_for_yard(yard)` that refreshes only yard-specific state and calls `show()`. Replace `_close()` with `hide()`. On second-and-later opens of the same context type (planet ↔ planet, fleet ↔ fleet) the panel tree is reused; cross-type transitions still rebuild. Saves the bulk of the 4.4s/click panel-construction cost.

---

## Pre-flight (TDD baseline)

- [ ] Phase 1 complete; `BuildQueueController.reset_filters()` exists.
- [ ] Re-read [findings/01_lifecycle_research.md](findings/01_lifecycle_research.md) end-to-end.
- [ ] `grep -n 'BuildQueueScreen(' game/` — confirm the 3 construction sites at [strategy_build_queue_manager.py:100, 213, 257](../../../game/ui/screens/strategy_build_queue_manager.py).
- [ ] `grep -rn 'build_queue_screen' game/ tests/` — capture every reference; many are status checks like `if self._screen.build_queue_screen is None` that will need updating.
- [ ] Identify any tests that assume a fresh instance per click — `tests/unit/ui/screens/test_build_queue_replay_button.py` is suspected; review and note in Task 2.10 if updates are needed.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count.

---

## Tasks

### Task 2.1: Define lifecycle test surface (TDD-first) [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -v`

- [ ] Add tests that codify the desired post-Phase-2 behavior:
  - `test_constructed_once` — the manager constructs `BuildQueueScreen` exactly once across N build-yard clicks (N ≥ 3) on the same context type.
  - `test_open_for_yard_refreshes_state` — call `open_for_yard(yard_a)`, then `open_for_yard(yard_b)` (same type). After the second call, `build_context is yard_b`, `queue_sources` reflects yard_b's hex, `selected_queue_indices == {0}`, `controller.selected_category == "complex"`, `controller.selected_role == "Any"`.
  - `test_open_for_yard_resets_drag_handler` — set drag-handler state, call `open_for_yard`, confirm state cleared.
  - `test_planet_to_fleet_rebuilds_panels` — opening with planet then fleet context triggers panel rebuild; same-type does not.
  - `test_hide_does_not_kill_panels` — after `hide()`, `panels.background.alive` is True; `panels.background.visible` is False.
  - `test_show_after_hide` — after `hide()` then `show()`, `panels.background.visible` is True.
  - `test_close_callback_no_longer_nulls_screen` — manager-side: after close, `self._screen.build_queue_screen` is still the same instance (not None).
- [ ] Use unit-test fakes/mocks for `pygame_gui.UIManager`, `Planet`, `Fleet`, `Galaxy`, `DesignLibrary`. Do not require pygame display init.
- [ ] Run the tests; **confirm they fail** on current code.
- [ ] **Verify:** failures match expected reasons.

**Notes:**

### Task 2.2: Add `reset_state()` to `BuildQueueDragHandler` [Simple]
**File:** `game/ui/screens/build_queue_drag_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_drag_handler.py -v`

- [ ] Add `reset_state(self) -> None` that clears `dragged_item = None`, `drag_start_pos = None`, `selected_design = None` (verify exact attribute names against [drag_handler:74-81](../../../game/ui/screens/build_queue_drag_handler.py#L74)).
- [ ] Add a unit test verifying all three attributes are reset.
- [ ] **Verify:** existing drag-handler tests still pass.

**Notes:**

### Task 2.3: Split `BuildQueueScreen.__init__` into shell + `open_for_yard` [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Task 2.1 tests + golden / smoke

- [ ] Identify which existing `__init__` work is "UI shell" (manager, mapper, facade, portrait_loader, panels factory invocation) vs. "yard-specific" (build_context, hex_coord, queue_sources, active_queue_source, selected_queue_indices, planet_selection_window, controller filters, drag handler state).
- [ ] In `__init__`, accept an optional `initial_yard` parameter that defaults to `None`. Construct UI shell unconditionally. If `initial_yard` is provided, call `self.open_for_yard(initial_yard)` at the end.
- [ ] Implement `open_for_yard(self, yard: Union[Planet, Fleet, BuildContext]) -> None`:
  - If `self.build_context is None` (first call) OR `self.build_context.context_type != yard.context_type`: rebuild panels via the existing factory call. (Defer panel rebuild logic to Task 2.4.)
  - Set `self.build_context = yard`, `self.hex_coord = yard.hex_coord`.
  - `self.queue_sources = collect_build_queues_at_hex(self.hex_coord, self.galaxy, self.empire)`.
  - `self.active_queue_source = self.queue_sources[0] if self.queue_sources else None`.
  - `self.selected_queue_indices = {0} if self.queue_sources else set()`.
  - `self.selected_queue_index = 0`.
  - `self.planet_selection_window = None`.
  - `self.controller.reset_filters()` (added in Phase 1).
  - `self.controller.set_active_queue(self.active_queue_source)` if non-None.
  - `self.drag_handler.reset_state()`.
  - `self._refresh_items_list()`.
  - `self._refresh_queue_display()`.
  - `self.show()`.
- [ ] **Verify:** Task 2.1's `test_open_for_yard_refreshes_state` passes.

**Notes:**

### Task 2.4: Add `hide()` / `show()` and rebuild-panels-on-context-type-change [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Task 2.1 tests

- [ ] Add `hide(self) -> None` that sets `self.panels.background.visible = False` and any other top-level container needed (verify by inspecting `BuildQueuePanels` dataclass).
- [ ] Add `show(self) -> None` that does the inverse.
- [ ] Add private `_rebuild_panels(self, context_type: str) -> None` that:
  - Kills the existing `panels.background` (and any other top-level UI containers) if `self.panels` is not None — this matches today's `_close` cleanup but limited to the panel tree.
  - Calls the panel factory to construct fresh panels for the new context type.
  - Re-wires `renderer`, `controller`, `drag_handler` references to the new panels (they hold panel references).
- [ ] In `open_for_yard`: detect `self.build_context is None or self.build_context.context_type != yard.context_type` and call `_rebuild_panels(yard.context_type)` before continuing.
- [ ] **Verify:** Task 2.1's `test_planet_to_fleet_rebuilds_panels` and `test_hide_does_not_kill_panels` pass.

**Notes:** The internal references between `BuildQueueScreen`, `panels`, `renderer`, `controller`, `drag_handler` mean rebuilding panels likely also requires reconstructing those collaborators. Inspect [build_queue_screen.py:120-159](../../../game/ui/screens/build_queue_screen.py#L120) to enumerate the wiring; treat this as the riskiest task in the phase.

### Task 2.5: Replace `_close()` with `hide()` [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Task 2.1 + smoke

- [ ] Find every caller of `self._close()` (close button, Esc key handler, etc. — `grep -n '_close' game/ui/screens/build_queue_screen.py`).
- [ ] Change calls to `self.hide()` and dispatch `self.on_close_callback()` (existing) for the close-button-style paths.
- [ ] Delete the `_close` method entirely OR make it a thin wrapper that calls `self.hide()`. Prefer deletion — explicit is better.
- [ ] **Verify:** `panels.background.kill()` no longer fires from this path.

**Notes:** The single `manager.update(0)` call inside `_close` (line 646) was load-bearing for pygame_gui cleanup of dying widgets; removing the kill obviates that. If any deferred-update warnings appear in logs, investigate and add a `manager.update(0)` to the `hide()` path.

### Task 2.6: Update `StrategyBuildQueueManager` to construct + reuse [Medium]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** Task 2.1 + smoke

- [ ] In `StrategyBuildQueueManager.__init__`, do NOT eagerly construct `BuildQueueScreen` — defer to first click (lazy). Add `self._screen.build_queue_screen = None` as today, but note the change in semantics.
- [ ] Modify each of the 3 click-handler entry points (lines 100, 213, 257):
  - Replace the entry guard `if self._screen.build_queue_screen is not None: return` with no-op (allow the call to proceed; the screen will just refresh).
  - Replace `BuildQueueScreen(planet, ...)` construction with:
    ```python
    if self._screen.build_queue_screen is None:
        self._screen.build_queue_screen = BuildQueueScreen(initial_yard=None, ...)
    self._screen.build_queue_screen.open_for_yard(planet)
    ```
- [ ] Update the `on_close_callback` (line 116) — it should NOT null `self._screen.build_queue_screen`. Just hide the build queue and re-show main strategy UI.
- [ ] Update any `self._screen.build_queue_screen is not None` checks elsewhere in the manager — they now indicate "ever opened", not "currently visible". If "currently visible" is the intent, use `self._screen.build_queue_screen.is_visible()` (add as method).
- [ ] **Verify:** Task 2.1's `test_constructed_once` and `test_close_callback_no_longer_nulls_screen` pass.

**Notes:** The 3 entry points may have minor differences (different yard sources). Map them carefully — don't paste the same code 3×; refactor into a single `_open_build_queue(yard)` helper on the manager.

### Task 2.7: Add `is_visible()` and visibility-gated event handling [Simple]
**File:** `game/ui/screens/build_queue_screen.py`

- [ ] Add `is_visible(self) -> bool` returning `self.panels is not None and self.panels.background.visible`.
- [ ] In `handle_event(self, event)` (around line 397), early-return if `not self.is_visible()`. Prevents pygame_gui events from running on a hidden screen.
- [ ] **Verify:** events fired while hidden are ignored.

**Notes:**

### Task 2.8: Manual smoke test [Simple]
**Tests:** Manual

- [ ] Launch the game.
- [ ] Open + close build queue at home planet 5×. Confirm subsequent opens are visibly faster (< 1s).
- [ ] Switch to a different planet's build queue. Confirm correct yard data (queue contents, planet stats).
- [ ] Switch to a fleet's build queue (planet → fleet transition). Confirm correct fleet panel layout.
- [ ] Switch back to a planet. Confirm correct planet panel layout.
- [ ] Drag-and-drop a queue item. Confirm drag works correctly. Open + close queue. Drag again. Confirm no stale drag state.
- [ ] **Verify:** all behaviors correct; no console warnings/errors.

**Notes:**

### Task 2.9: Re-profile and confirm gain [Simple]
**Tests:** `python Tools/profile_game/profile_game.py`

- [ ] Profile a session that opens the build queue 3× at the same yard (matching the original repro).
- [ ] Open the resulting HTML and inspect `BuildQueueScreen.__init__` cumulative time:
  - First open: still ~6.9s OR reduced if Phase 1 cache helps (will be ~4.7s with Phase 1).
  - Second + third opens: should be < 0.5s combined (vs. ~13.7s in the baseline).
- [ ] Capture before/after numbers in plan.md Current State.

**Notes:**

### Task 2.10: Update / migrate impacted tests [Medium]
**Files:** `tests/unit/ui/screens/test_build_queue_replay_button.py`, plus any others touched by `grep -n 'BuildQueueScreen(' tests/`

- [ ] For each test that constructs `BuildQueueScreen` directly: confirm it still works (constructor with `initial_yard=None` should be a no-op past UI-shell construction).
- [ ] For each test that asserts on `_close`-side effects (e.g., `panels.background.alive == False`): update to assert `is_visible() == False` instead.
- [ ] **Verify:** every previously-green test in the build-queue tree is still green.

**Notes:**

### Task 2.11: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Pass count ≥ baseline + new tests from Tasks 2.1, 2.2, plus migrations from 2.10.

**Notes:**

### Task 2.12: Commit Phase 2 [Simple]

- [ ] `git status --short` confirms only Phase 2 files are dirty.
- [ ] Commit message: `feat(PROJ-373): Phase 2 — reuse BuildQueueScreen across opens via open_for_yard / hide / show`
- [ ] Co-author trailer.
- [ ] Do NOT push.
- [ ] **Verify:** `git show --stat HEAD` shows only in-scope files.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BuildQueueScreen` is constructed once per session (or on first click) and reused
- [ ] `open_for_yard`, `hide`, `show`, `is_visible` are public methods
- [ ] `_close` deleted; close-button handlers route through `hide`
- [ ] Drag handler `reset_state()` exists; called on every `open_for_yard`
- [ ] Re-profile shows repeat-open cost ≪ first-open cost
- [ ] Manual smoke (5+ opens, planet/fleet switch, drag) passes
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
