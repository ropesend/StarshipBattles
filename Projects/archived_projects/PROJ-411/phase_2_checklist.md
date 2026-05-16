# Phase 2: Window Reuse (Track A)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-411 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Implementation Complete — Tasks 2.1–2.6 + 2.8 + 2.9 + 2.10 landed (awaiting F9 sanity check on input-block fix in 2.9 and hot-seat filter isolation in 2.10)
**Prerequisite:** Phase 1 complete; F9 profile dump shows per-window-init costs (StarRegistry 5 s, PlanetRegistry 4.4 s, EmpireOverview 4.2 s, EventLog 2.5 s).
**Objective:** Apply PROJ-376's window-reuse pattern (validated 7,088 ms → 408 ms = 94% reduction on Build Queue) to the four remaining strategy-layer windows: Galactic Planet Registry, Galactic Star Registry, Empire Overview, Event Log.

---

## Track choice rationale

User-visible lag is dominated by pygame_gui widget construction (cProfile: 72% of 65 s in `str.join` + `build_all_combined_ids`). Per-turn data caches landed in Phase 1 save microseconds against a multi-second pygame_gui cost. Phase 2 attacks the dominant cost directly by **paying it once per session and reusing the constructed window on subsequent opens**.

PROJ-376 already implemented this for Build Queue. The pattern is canonical:
- `BuildQueueScreen.__init__` constructs widgets once.
- `open_for_yard(...)` resets context-specific state + calls `show()`.
- `hide()` toggles `panels.background.hide()` without destroying widgets.
- `StrategyBuildQueueManager._open_build_queue` keeps the screen instance alive (`if self._screen.build_queue_screen is None: construct; else: update context + show`).

Each Phase 2 task mirrors this pattern for one window.

---

## Template: per-window reuse refactor

Every Phase 2 task follows the same 6 sub-steps. Concrete file paths and line numbers differ per window.

1. **Add `show()` / `hide()` to the window class.** `hide()` calls `self.set_blocking(False)` (or equivalent), kills any transient sub-windows (selection dialogs etc.), and toggles widget container visibility off. `show()` toggles back on. Widgets are not destroyed; widget cache survives.
2. **Extract context-update entry point.** Refactor `__init__`'s context-specific work (galaxy/empire reference assignment, filter reset, scroll-to-top, selection clear) into a new `open_for_X(...)` method. `__init__` calls it at the end of its widget-construction work. The registrar calls `open_for_X(...)` on re-open instead of `kill()` + `__init__`.
3. **Modify the registrar's open path.** Keep a reference to the live window on the registrar / window manager (the slot already exists for legacy reasons). On open: if the slot is occupied, call `open_for_X(...)` + `show()`; otherwise construct fresh.
4. **Override `kill()` to invoke `on_close_callback`.** Existing PROJ-313 lifecycle still works — the only mutation is that the registrar no longer triggers `kill()` on close; instead, `hide()`. Real `kill()` happens at scene exit or game shutdown.
5. **State reset contract.** Explicit list per window: selection cleared, scroll position back to top, search-text input cleared, filter buttons reset to default (or persisted — decide per window), sort order reset (or persisted). Capture decisions in the per-window task Notes.
6. **Regression test.** Two assertions: (a) on re-open, `__init__`'s expensive path is NOT called again (count-based: e.g. `gather_planets` only called once per window-lifetime, or a sentinel flag set in `__init__` not flipped twice); (b) state-reset contract is met (e.g. scroll position is 0 after `open_for_X`).

---

## Tasks (one PR per window per Phase C decision)

### Task 2.10: Per-empire filter snapshots for Planet/Star registries [Medium]
**Files:**
- `game/ui/screens/planet_list_window.py` — snapshot bookkeeping + `open_for_galaxy` save/restore
- `game/ui/screens/star_list_window.py` — same; add `empire=` kwarg to `__init__` + `open_for_galaxy`
- `game/ui/screens/strategy_windows/list_windows.py` — `StarListRegistrar` threads `current_empire`

**Tests:**
- `tests/unit/ui/screens/test_planet_list_filter_snapshot.py` — 6 tests
- `tests/unit/ui/screens/test_star_list_filter_snapshot.py` — 5 tests

- [x] Identified user-reported bug: under Phase 2 reuse, hot-seat handoffs leaked filter state across players. Original Phase 2 decision "filters/scroll/search preserved across opens" was correct for same-empire repeats but wrong for empire switches.
- [x] User picked option (B) per-empire memory over (A) reset-on-switch.
- [x] Added `_filter_snapshots_by_empire: dict[int, dict]` plus `_default_filter_snapshot` to both windows. Default captured at end of `__init__` (post-Stage-3) via existing `capture_*_list_state` helpers.
- [x] `open_for_galaxy` empire switch: capture outgoing, restore incoming (or apply default if first sight). Same-empire re-open is unchanged. Snapshot path gated on `_default_filter_snapshot is not None` so bypass-init tests stay on the legacy path.
- [x] StarListWindow now takes `empire=` kwarg; `StarListRegistrar` threads `c.scene.current_empire` on both first-construction and reuse paths.
- [x] 11 new tests, all green. 53 adjacent tests across reuse/registrar/snapshot files still green.
- [ ] User F9 verification: as Player 1 set a filter (e.g. hide one planet type), end turn, as Player 2 open Planet List — should be default view. Re-open as Player 1 — Player 1's filter restored.

**Notes:**
- Hot-seat round-trip test (A → B → A → A_filter_restored) is the most important behavioural assertion; covered by `test_round_trip_a_to_b_to_a_restores_a_snapshot`.
- Snapshot covers everything `capture_planet_list_state` covers: filter types, owners, effects, search text, ranges, columns visibility/order. Sort order (held on `column_manager`) is *not* per-empire — global by design.
- Event Log doesn't need per-empire snapshots — `open_for_events` already resets `current_filter` to "all" each open. Empire Panel doesn't need it either — different empire falls back to kill+rebuild (Phase 2 same-empire-only scope).

### Task 2.9: `StrategyInputHandler` planet-list gate must check `.visible` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py` line 66 — gate on visibility, not slot presence

**Tests:** `tests/unit/ui/screens/test_strategy_input_handler_hidden_planet_list.py` — 4 tests

- [x] Identified the actual root cause of the input-block (Tasks 2.5/2.6/2.8 addressed pygame_gui's side but not StarshipBattles' own gate). Line 66 had `if self.scene.ui.window_manager.planet_list_window is not None: handle_event; return`. Under Phase 2 reuse the slot stays populated when hidden, so the early-return permanently short-circuited `_handle_button_press` / `handle_click` / `_handle_scroll`.
- [x] Wrote 4 failing tests first (TDD): button-press routes to End Turn when hidden; hex-click reaches `handle_click` when hidden; mouse-wheel zoom reaches `_handle_scroll` when hidden; visible-modal still short-circuits (original F11/F12 suppression intent preserved).
- [x] Applied the minimal fix: extracted `planet_list = self.scene.ui.window_manager.planet_list_window`, gated on `planet_list is not None and planet_list.visible`. Single 2-line change.
- [x] All 4 new tests green. 104 adjacent input-handler tests still green.
- [ ] User F9 re-verification: open Planet List, Esc-close, confirm End Turn / zoom / hex / Open-Build-Yard all work.

**Notes:**
- This was the symptom's actual cause. Tasks 2.5/2.6/2.8 were necessary (pygame_gui-side leaks) but not sufficient — the StarshipBattles-side gate had its own dependency on slot presence that misfired under Phase 2 reuse.
- Only `planet_list_window` had this pattern in `strategy_input_handler.py`; star/empire/event-log slots don't have an analogous gate, which is why the symptom was tied to opening Planet List specifically.

### Task 2.8: Hidden modal must leave pygame_gui `UIWindowStack` [Simple]
**File:** `game/ui/screens/strategy_modal_window.py` — consolidate `hide()` / `show()` on base class

**Tests:** `tests/unit/ui/screens/test_strategy_modal_hidden_input.py` — 2 new tests (4 total in file)

- [x] Diagnosed lingering input-block after Task 2.6: user reported End Turn / zoom / hex still unresponsive after Esc-closing a panel, even with the visibility-aware `check_clicked_inside_or_blocking` override in place.
- [x] Root cause traced to pygame_gui's `UIWindowStack` (separate from `StrategyWindowManager._modals`): `UIWindow.kill()` removes from `window_stack`; the Task 2.5 `hide()` did NOT. Hidden windows remained z-top in pygame_gui's stack, so pygame_gui's hit-test/focus routed events to them despite `is_blocking=False` and the visibility-aware override.
- [x] Consolidated `hide()` / `show()` on `StrategyModalWindow` base class. `hide()` now: `is_blocking=False` → `wm.unregister_modal(self)` → `window_stack.remove_window(self)` → `super().hide()`. `show()` mirrors with dedup-via-remove-then-add. Subclass-level hide/show overrides removed (~80 LOC duplication eliminated).
- [x] 2 new tests: `test_hide_removes_window_from_pygame_gui_window_stack` and `test_show_re_adds_window_to_pygame_gui_window_stack`. Use real `EventLogWindow` via `bypass_init` + `patch("pygame_gui.elements.ui_window.UIWindow.hide/show")` to test the super() boundary cleanly.
- [x] Diagnostic logging from Task 2.6 verification removed from `strategy_event_router.py`.
- [x] Sharded suite green: 20,121 / 20,115 passed / 0 failed (2 errors = pre-existing flaky `test_selection_refinements.py` pygame-display-init, unrelated to PROJ-411).
- [ ] User F9 re-verification: open Planet List Window, Esc-close, verify End Turn / zoom / hex / Open-Build-Yard buttons all work.

**Notes:**
- The 4 subclasses (Planet/Star/Empire/EventLog) had their own hide/show overrides from Task 2.5 — these were removed. All hide/show behavior now lives in one place on the base.
- pygame_gui's `UIWindowStack` is a private-ish internal data structure but is the canonical mechanism for z-ordering and hit-test routing. `UIWindow.kill()` already mutates it; this brings `hide()`/`show()` to parity.

### Task 2.6: Hidden modal must be transparent to input [Simple]
**File:** `game/ui/screens/strategy_modal_window.py` — override `check_clicked_inside_or_blocking`

**Tests:** `tests/unit/ui/screens/test_strategy_modal_hidden_input.py` — 2 tests

- [x] Identified critical regression from Task 2.5: F9 capture showed `window_init` firing only once (perf goal met) but user reported End Turn / zoom / hex-click all unresponsive after closing a window via Esc.
- [x] Root cause traced to pygame_gui internals: `UIManager.process_events` walks all `is_window` sprites and calls `check_clicked_inside_or_blocking`. The default implementation calls `hover_point()` which only checks rect collision, not visibility. A 90%-screen hidden window consumed every left-click in its rect.
- [x] Overrode `check_clicked_inside_or_blocking` on `StrategyModalWindow` base class: returns False if `not self.visible`, else delegates to pygame_gui's default. Lives on the base so all subclasses benefit (harmless for non-reusable ones — killed modals are removed from the sprite group entirely).
- [x] 2 new tests: (1) hidden modal short-circuits to False without invoking super, (2) all 4 reusable windows inherit the override via MRO.
- [ ] User F9 re-verification: confirm End Turn / zoom / hex-click work after closing a panel with Esc.

**Notes:**
- pygame_gui's `hover_point()` predates the modal-stack design and doesn't filter by visibility. The fix lives at the StrategyModalWindow boundary so we don't touch pygame_gui itself.
- The 8-line override (`check_clicked_inside_or_blocking`) is the smallest possible scope. All existing modal-blocking semantics for VISIBLE windows are preserved unchanged.

### Task 2.5: Extend reuse to Esc-close via `request_close()` [Simple]
**Files:**
- `game/ui/screens/strategy_modal_window.py` — add `request_close()` base method (default = `kill()`)
- `game/ui/screens/strategy_event_router.py` — Esc handler routes to `request_close()` instead of `kill()` directly
- `game/ui/screens/planet_list_window.py`, `star_list_window.py`, `empire_panel_window.py`, `event_log_window.py` — override `request_close()` to call `self.hide()`

**Tests:** `tests/unit/ui/screens/test_strategy_modal_esc_close.py` — 5 tests (4 parametrized + 1 base-class)

- [x] Discovered Phase 2 verification gap: user F9 capture showed `window_init` firing on every open because Esc-close was killing the windows (clearing the registrar slot via `on_close_callback`).
- [x] Added `StrategyModalWindow.request_close()` extension point with default `self.kill()` (legacy contract unchanged for all other modals).
- [x] Modified Esc handler in `strategy_event_router.py:119` from `modals[-1].kill()` → `modals[-1].request_close()`.
- [x] Overrode `request_close → self.hide()` on all 4 reusable windows.
- [x] Added 5 regression tests. Adjacent `test_strategy_event_router.py` suite still green.
- [ ] User F9 re-verification: expect 1st open ~3-7 s, 2nd open <500 ms regardless of close method (X or Esc).

**Notes:**
- This was the missing piece that made Phase 2 verification fail. The fix is small (~12 LOC across 6 files) and uniform.
- Other strategy modals (PlanetSelectionWindow, FleetSelectionWindow, etc.) still kill on Esc — their `request_close()` inherits the base default.
- The `decisions.md` 2026-05-11 entry "Phase 2 Esc-close still kills" is now superseded by this Task 2.5 entry.



### Task 2.1: Window reuse — Galactic Planet Registry [Medium]
**Window:** `game/ui/screens/planet_list_window.py` (737 LOC — over ceiling; edits ≤25 LOC budget)
**Registrar:** `game/ui/screens/strategy_windows/list_windows.py` (`PlanetListWindowRegistrar`)

**Tests:**
- `tests/unit/ui/screens/test_planet_list_window.py` (regression — re-open does not re-walk galaxy)
- `tests/unit/ui/screens/strategy_windows/test_planet_list_window_registrar.py` (new — verify slot-reuse path)

- [x] Add `show()` / `hide()` methods to `PlanetListWindow`. `hide()` flips `is_blocking = False` and unregisters from `_window_manager`; `show()` flips back and re-registers.
- [x] Override `on_close_window_button_pressed` → `self.hide()` (the pygame_gui canonical pattern, docstring explicitly recommends this).
- [x] Add `open_for_galaxy(galaxy, empire, *, facade=None)` method that rebinds context, clears `selected_planet`, calls `show()` + `refresh_list()`.
- [x] In `list_windows.py::PlanetListRegistrar.open()`: check `existing = c.planet_list_window`. If alive, call `existing.open_for_galaxy(...)`. Else construct fresh (existing path).
- [x] `kill()` path unchanged — Esc + scene exit still actually kill (slot clears via `on_close_callback`).
- [x] State-reset contract: `selected_planet → None`. Scroll position, sort order, filter buttons, search text **preserved** across opens (decision: easier UX for repeat lookups; user can revisit explicitly if they want a clean state).
- [x] Add regression tests: 6 in `tests/unit/ui/screens/test_planet_list_window_reuse.py` (window methods) + 4 in `tests/unit/ui/screens/strategy_windows/test_planet_list_registrar_reuse.py` (registrar reuse path). All 20 adjacent-suite tests green.
- [ ] F9 profile sanity check (user-driven): capture `Panel: PlanetRegistry.window_init` on 1st open. 2nd open should NOT fire `Panel: PlanetRegistry.window_init` (reuse path skips `__init__` entirely). Expect <500 ms wall-clock for 2nd open vs ~4.4 s for 1st.

**Notes:**
- Esc close still kills (existing event-router contract). Only the X-button uses the new hide path. Documented as a tradeoff — Phase 3 or follow-up can equalize them if the user wants.
- The `getattr(facade, "facade_state", None)` defensive pattern from Phase 1 is preserved in the registrar's existing flow — no change needed.
- 10 new tests, all green; 20 adjacent tests (test_planet_list_window.py + reuse + registrar reuse) all green. No production regression on existing 20-test PlanetListWindow suite.

### Task 2.2: Window reuse — Galactic Star Registry [Medium]
**Window:** `game/ui/screens/star_list_window.py` (463 LOC — within budget)
**Registrar:** `game/ui/screens/strategy_windows/list_windows.py` (`StarListWindowRegistrar`)

**Tests:**
- `tests/unit/ui/screens/test_star_list_window.py` (regression)
- `tests/unit/ui/screens/strategy_windows/test_star_list_window_registrar.py` (new)

- [x] All 7 sub-steps applied — pattern identical to Task 2.1 minus the empire/facade rebinding.
- [x] State-reset contract: `selected_star → None`. Filters, scroll, search text preserved across opens.
- [x] 6 new tests in `tests/unit/ui/screens/test_star_list_window_reuse.py`, all green. 31 adjacent-suite tests green (test_star_list_window.py + reuse).
- [ ] F9 profile sanity check (user-driven): expect 1st: ~5 s, 2nd: <500 ms.

**Notes:**
- Pattern is now templated — Task 2.2 was a near-mechanical copy of Task 2.1's window-class changes + registrar changes. ~50 LOC additions to `star_list_window.py` + ~10 LOC change in registrar.
- No facade_state plumbing change needed in registrar — Phase 1's threading still works through the new path.

### Task 2.3: Window reuse — Empire Overview [Medium]
**Window:** `game/ui/screens/empire_panel_window.py` (572 LOC — over ceiling; edits ≤15 LOC budget)
**Registrar:** `game/ui/screens/strategy_windows/empire_panel_ctrl.py` (`EmpirePanelRegistrar`)

**Tests:**
- `tests/unit/ui/screens/test_empire_panel_window.py` (regression)
- `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py` (regression — registrar reuse path)

- [x] Scope narrowed: **same-empire reuse only**. `open_for_empire(empire)` asserts `empire is self.empire`; hot-seat empire switch is handled by the registrar via `kill() + reconstruct` (full cost path).
- [x] Added `show()`/`hide()`/`on_close_window_button_pressed`/`open_for_empire` to `EmpirePanelWindow`. `open_for_empire` resets `current_tab → TAB_TREASURY`, calls `panel.show()` on Treasury panel + `panel.hide()` on the others, updates tab button selection, then `self.show()`.
- [x] Modified `empire_panel_ctrl.py::EmpirePanelRegistrar.open()`: removed the original `if window: window.kill()` line. New 3-branch flow: (a) alive + same empire → `open_for_empire`. (b) alive + different empire → `kill()` then reconstruct. (c) no live window → reconstruct.
- [x] 5 new tests in `test_empire_panel_window_reuse.py`. Existing `test_empire_panel_open_kills_existing_window` still green (hot-seat path still kills).
- [ ] F9 profile sanity check: expect 1st open: ~4.2 s; 2nd open same empire: ~50–300 ms; 2nd open different empire: ~4.2 s (no win in hot-seat case).

**Notes:**
- Hot-seat optimization (full window-reuse across empires) is deferred — would need to invalidate per-empire widget content (Treasury snapshot, Population portrait/flag). Out of Phase 2 scope.
- `open_for_empire` does NOT rebuild Treasury content even on same-empire reuse — the snapshot still reflects the same empire and turn caching from Phase 1 Task 1.7 saves the work anyway.

### Task 2.4: Window reuse — Event Log [Medium]
**Window:** `game/ui/screens/event_log_window.py` (539 LOC — within budget)
**Registrar:** `game/ui/screens/strategy_windows/event_log_window_ctrl.py`

**Tests:**
- `tests/unit/ui/screens/test_event_log_window.py` (regression)

- [x] `open_for_events(events, *, empire_name=None)` rebinds `self.all_events`, resets `self.current_filter = "all"`, calls `data_source.update_events(events)` (existing API), updates window title via `set_display_title` (guarded for bypass_init paths), `show()`, `_rebuild_list()`.
- [x] Hot-seat-safe — `EventLogDataSource.update_events` was already an existing public API. Different empire's events list swaps cleanly.
- [x] State-reset contract: filter → "all". Scroll, sort order preserved across opens.
- [x] Modified `event_log_window_ctrl.py::_open_with`: alive slot → `open_for_events(events, empire_name=...)`. Removed the eager `if c.event_log_window: c.event_log_window.kill()`.
- [x] 7 new tests in `test_event_log_window_reuse.py`. All 13 existing `test_event_log_window.py` tests still green.
- [ ] F9 profile sanity check: expect 1st: ~2.5 s, 2nd: <200 ms.

**Notes:**
- Title update on reuse propagates the active empire name — under bypass_init the title-bar widget doesn't exist, so the call is `getattr`-guarded.
- The auto-popup path (`open_with_events`) for per-turn event log shows is unchanged behaviorally — only the `_open_with` helper switched from kill+construct to reuse.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All 4 task checkboxes complete (Tasks 2.1, 2.2, 2.3, 2.4 implementation green)
- [x] `python Tools/test_sharded/test_sharded.py` passes — one legacy test (`test_open_event_log_kills_existing`) updated to the new reuse contract.
- [ ] F9 profile dump from a real game session shows re-open spans <500 ms for all 4 windows _(user-driven verification)_
- [ ] Document final before/after numbers in `findings/profile_after_phase2.md` _(awaiting F9 dump)_
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

---

## Out of scope (deferred to Phase 3 or beyond)

- **First-open cost.** Even after Phase 2, first open of each window still costs 2.5–7 s. Reducing this needs Track B work: VirtualTable row-pool sizing, sidebar widget-count trimming, possibly pygame_gui `build_all_combined_ids` memoization. Track B becomes Phase 3 if the user prefers it over the planned Phase 3 regression-gates work.
- **Window reuse for transient sub-windows** (PlanetSelectionWindow during colonize flow, FleetSelectionWindow, etc.). PROJ-376 didn't reuse these; pattern not yet validated for one-shot dialogs.
- **Hot-seat selection-state preservation.** Each window's state-reset contract decides what carries between opens. The plan is "reset everything on open" for simplicity; user may later request preservation for some fields (e.g. scroll position last-viewed) as a separate refinement.
