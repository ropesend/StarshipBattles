# Phase 2: Window Reuse (Track A)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-411 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

### Task 2.1: Window reuse — Galactic Planet Registry [Medium]
**Window:** `game/ui/screens/planet_list_window.py` (737 LOC — over ceiling; edits ≤25 LOC budget)
**Registrar:** `game/ui/screens/strategy_windows/list_windows.py` (`PlanetListWindowRegistrar`)

**Tests:**
- `tests/unit/ui/screens/test_planet_list_window.py` (regression — re-open does not re-walk galaxy)
- `tests/unit/ui/screens/strategy_windows/test_planet_list_window_registrar.py` (new — verify slot-reuse path)

- [ ] Add `show()` / `hide()` methods to `PlanetListWindow` mirroring `BuildQueueScreen.hide()` shape (lines 368-395 of `build_queue_screen.py`).
- [ ] Extract context-specific work from `__init__` into a new `open_for_galaxy(galaxy, empire, *, facade)` method. The widget-construction loop stays in `__init__`; the new method just rebinds `self.galaxy`, `self.empire`, resets `self.scroll_offset`, clears filter text, and triggers `refresh_list()`.
- [ ] In `list_windows.py::PlanetListWindowRegistrar.open()`: change `if c.planet_list_window: c.planet_list_window.kill()` to `if c.planet_list_window is not None: c.planet_list_window.open_for_galaxy(...) + show()`. Construct fresh only when slot is None.
- [ ] In the existing `kill()` path: ensure close-button + Esc still kill (no leak from session lifetime).
- [ ] Document the state-reset contract (selection cleared, scroll → 0, search text cleared, filter buttons preserved or reset — TBD per user preference).
- [ ] Add regression test asserting re-open does not call `gather_planets` a second time within the same turn (uses `facade_state` cache as proof).
- [ ] F9 profile sanity check: capture `Panel: PlanetRegistry.window_init` on 1st open and `Panel: PlanetRegistry.open_for_galaxy` (or equivalent re-open span — add one if needed) on 2nd open. Expect 1st: ~4.4 s, 2nd: <500 ms.

**Notes:** [Filled during implementation]

### Task 2.2: Window reuse — Galactic Star Registry [Medium]
**Window:** `game/ui/screens/star_list_window.py` (463 LOC — within budget)
**Registrar:** `game/ui/screens/strategy_windows/list_windows.py` (`StarListWindowRegistrar`)

**Tests:**
- `tests/unit/ui/screens/test_star_list_window.py` (regression)
- `tests/unit/ui/screens/strategy_windows/test_star_list_window_registrar.py` (new)

- [ ] Same 7 sub-steps as Task 2.1, with `open_for_galaxy(galaxy)` (no empire param — Star Registry doesn't bind to one empire).
- [ ] State-reset contract: identical to Planet Registry minus empire-specific bits.
- [ ] F9 profile sanity check: expect 1st: ~5 s, 2nd: <500 ms.

**Notes:**

### Task 2.3: Window reuse — Empire Overview [Medium]
**Window:** `game/ui/screens/empire_panel_window.py` (572 LOC — over ceiling; edits ≤15 LOC budget)
**Registrar:** `game/ui/screens/strategy_windows/empire_panel_ctrl.py` (`EmpirePanelRegistrar`)

**Tests:**
- `tests/unit/ui/screens/test_empire_panel_window.py` (regression)
- `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py` (regression — registrar reuse path)

- [ ] Same template. `open_for_empire(empire)` resets `self.empire`, resets `self.current_tab = TAB_TREASURY`, resets `self._population_tab_built = False` (so a different empire gets a fresh Population build).
- [ ] Important: Empire Overview can be opened for *different* empires (hot-seat). The slot-reuse path must re-bind `self.empire` and rebuild the Treasury tab content for the new empire. This is more state-reset than the read-only registries.
- [ ] State-reset contract: tab → Treasury (default), Treasury content rebuilt (since empire changed), Population-tab lazy-build flag reset.
- [ ] F9 profile sanity check: expect 1st: ~4.2 s, 2nd: ~300 ms (Treasury rebuild dominates re-open cost since empire changed).

**Notes:**

### Task 2.4: Window reuse — Event Log [Medium]
**Window:** `game/ui/screens/event_log_window.py` (539 LOC — within budget)
**Registrar:** `game/ui/screens/strategy_windows/event_log_window_ctrl.py`

**Tests:**
- `tests/unit/ui/screens/test_event_log_window.py` (regression)

- [ ] Same template. `open_for_events(events, *, empire_name=None)` rebinds `self.all_events`, resets `self.current_filter = "all"`, calls `_rebuild_list()`.
- [ ] Hot-seat awareness: re-open for a different empire MUST rebuild the events list (events are empire-scoped via `get_all_events(empire_id=...)`).
- [ ] State-reset contract: filter → "all", scroll → top.
- [ ] F9 profile sanity check: expect 1st: ~2.5 s, 2nd: <200 ms.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All 4 task checkboxes complete
- [ ] `python Tools/test_sharded/test_sharded.py` passes (no regressions vs 20,079-test baseline)
- [ ] F9 profile dump from a real game session shows re-open spans <500 ms for all 4 windows
- [ ] Document final before/after numbers in `findings/profile_after_phase2.md`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3

---

## Out of scope (deferred to Phase 3 or beyond)

- **First-open cost.** Even after Phase 2, first open of each window still costs 2.5–7 s. Reducing this needs Track B work: VirtualTable row-pool sizing, sidebar widget-count trimming, possibly pygame_gui `build_all_combined_ids` memoization. Track B becomes Phase 3 if the user prefers it over the planned Phase 3 regression-gates work.
- **Window reuse for transient sub-windows** (PlanetSelectionWindow during colonize flow, FleetSelectionWindow, etc.). PROJ-376 didn't reuse these; pattern not yet validated for one-shot dialogs.
- **Hot-seat selection-state preservation.** Each window's state-reset contract decides what carries between opens. The plan is "reset everything on open" for simplicity; user may later request preservation for some fields (e.g. scroll position last-viewed) as a separate refinement.
