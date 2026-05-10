# PROJ-376: Design — BuildQueueScreen Lifecycle Refactor

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

---

## Initial Analysis

### Why this exists

PROJ-373 shipped 3 of its 4 phases. Phase 2 (instance reuse) was deferred mid-execution because the original subagent could not untangle the pygame_gui lifecycle, modal-stack interactions, FEAT-17 pause-button state, and the per-yard reference graph in the 30-minute investigation budget the project guidance set as the deferral threshold (PROJ-373 `decisions.md` 2026-05-06 row). The 2026-05-06 OpenCode review (`Reviews/results/2026-05-06_051908_.../report.md`) flagged the consequences:

- **MAJ-003** — `BuildQueueController._validation_cache` (PROJ-373 Phase 1, ~2.2 s/click win) lives on the controller, which is reconstructed per open. Without instance reuse the cache is destroyed on every close and provides zero cross-open value.
- **INFO-008** — `< 0.5 s` repeat-open acceptance bar is missed without Phase 2. Today's repeat open still pays ~4.7 s (cache destroyed on close).
- **INFO-003** — Phase 3's row-pool guard saves ~1.5 s/click but only triggers if `VirtualTable` survives across opens, which requires Phase 2.
- **MIN-001** — `BuildQueueController.reset_filters()` is dead code awaiting Phase 2's `open_for_yard()`.

Without PROJ-376, three PROJ-373 phases pay full implementation cost for partial value. PROJ-376 unlocks the rest.

### Yard-specific reference catalogue

Reading `BuildQueueScreen.__init__` end-to-end (`game/ui/screens/build_queue_screen.py:48-166`), the constructor does five distinct things, intermixed today:

1. **Pure DI / shell** (lines 70-89): assigns `manager`, `session`, `facade`, `on_close`, `portrait_surface`, `_mapper`, `design_library`, `design_loader`, `galaxy`, `empire`. These don't change per-yard.
2. **Yard identity + derived state** (lines 71-99): `build_context`, `hex_coord`, `selected_queue_index`, `planet_selection_window`, `queue_sources`, `selected_queue_indices`, `active_queue_source`. **All yard-specific.**
3. **Screen geometry** (lines 105-107): `screen_width`, `screen_height`. Re-derive on `_rebuild_panels`; otherwise stable.
4. **Panel + collaborator construction** (lines 110-159): `factory`, `panels`, `_queue_selector`, `renderer`, `controller`, `drag_handler`. The factory takes `build_context` (line 112) and `queue_sources` (line 114), so the panel tree depends on context type. The controller takes `build_context`, `hex_coord`, `galaxy`, `empire` (lines 132-144). The drag handler takes none of these.
5. **Tooltips + first refresh** (lines 162-166): `_apply_tooltips()`, `_refresh_items_list()`, `_refresh_queue_display()`.

**Reusable across yards (same context type):** items 1, 3, 4, 5 — except the panel-tree-internal references to `build_context` are baked in by the factory and do NOT track yard identity (the factory captures yard data once for the planet-or-fleet info panel; queue selector is rebuilt per yard via `queue_sources`).

**Must update on every yard switch:** all of item 2, plus `controller.build_context` / `controller.hex_coord` (set via `controller.set_active_queue` and direct attribute writes), plus `_queue_selector.queue_sources` (or rebuild via `BuildQueueSelector.refresh()`), plus the FEAT-17 pause-button label (already covered by `renderer.refresh_pause_button(...)`).

**Must rebuild on context-type change (planet ↔ fleet):** the entire panel tree, because `BuildQueuePanelFactory._create_context_report_panel(...)` dispatches between `PlanetReportPanel` and a fleet-info panel (`build_queue_panel_factory.py:206-241`). Same-type→same-type is the common case; cross-type is rare (the user has to drill into a different entity type at the same hex or different hex).

### Modal-stack + event-routing flow today

There are **two unrelated "modal" mechanisms** in play. Conflating them was a key risk in the original deferral.

1. **Strategy modal-window registry (PROJ-313).** Owned by `StrategyWindowManager`. Auto-registration via `StrategyModalWindow` base class. Walked by `StrategyEventRouter.has_modal_open()` and `_is_blocking_ui_element_at()` to gate galaxy-screen input. Used by every strategy-screen `UIWindow` subclass (16 windows; see `Projects/deep_archive/PROJ-301-350/PROJ-313/findings/strategy_modal_window_base_class.md`).
2. **Build-queue full-screen overlay.** `BuildQueueScreen` is **not** a `UIWindow`. It is a plain object that owns a `pygame_gui.UIPanel` tree (`panels.background`) sized to the full screen. It is checked separately by `StrategyEventRouter` (`game/ui/screens/strategy_event_router.py:58`) and `StrategyInputHandler` (`game/ui/screens/strategy_input_handler.py:55-56`) via `if scene.build_queue_screen is not None`.

PROJ-313's `StrategyModalWindow` base class is **not** the right shape for `BuildQueueScreen` because (a) BuildQueueScreen isn't a `UIWindow`; (b) the strategy modal registry is for input gating against the galaxy map, but BuildQueueScreen takes over the entire screen and hides the galaxy UI itself (`screen.ui.hide_ui()` at `strategy_build_queue_manager.py:82`); (c) PlanetSelectionWindow nested inside BuildQueueScreen passes `window_manager=None` deliberately ("PROJ-313: build queue screen has its own modal lifecycle", `build_queue_screen.py:628`). Decision: do not migrate.

The only nested `UIWindow` inside `BuildQueueScreen` is `PlanetSelectionWindow` (line 622), opened on demand from `_prompt_target_planet`. Its lifecycle is managed by hand (`self.planet_selection_window = ...` and `.kill()` from `_close()` at line 642). Phase 2 must continue this manual lifecycle: `hide()` should `kill()` `planet_selection_window` if open and clear the slot, the way `_close()` does today.

### Event-routing: when must events stop firing?

`BuildQueueScreen.handle_event` (line 397) calls `self.manager.process_events(event)` unconditionally. Today this is fine because the screen is destroyed on close. After Phase 2 the panels are still wired to the manager but invisible; pygame_gui events for hidden widgets normally don't fire (visibility-gated), but defensive `is_visible()` early-return is cheap and matches PROJ-373 design.md's R2.3 mitigation.

`StrategyInputHandler` at line 55 routes events to `build_queue_screen.handle_event` when the slot is non-None. Post-Phase-2 the slot is non-None even when hidden, so this routing must be visibility-gated:

```python
# Today (line 55):
if self.scene.build_queue_screen is not None:
    self.scene.build_queue_screen.handle_event(event)

# Target:
if self.scene.build_queue_screen is not None and self.scene.build_queue_screen.is_visible():
    self.scene.build_queue_screen.handle_event(event)
```

Same rule for `strategy_screen.py:246` (the draw call). The modal-block check at `strategy_event_router.py:58` is more nuanced — see decisions.md row 4.

### `_close()` audit

`BuildQueueScreen._close()` does four things (`build_queue_screen.py:639-649`):

1. Kill `planet_selection_window` if non-None (line 641-643). **Must preserve in `hide()`.**
2. Kill `panels.background` (line 645). **Must NOT preserve** — that's the whole point.
3. Call `manager.update(0)` (line 646) to flush pygame_gui's deferred-kill queue. **Becomes unnecessary** because nothing was killed; but if a stray warning appears in logs, add a `manager.update(0)` to `hide()`.
4. Invoke `on_close` callback (line 648-649). **Preserve.**

### Today's vs. target pipeline

**Today** (`strategy_build_queue_manager.py:71-114`, identical at `:175-227` and `:229-271`):

```
on_build_yard_click():
  if build_queue_screen is not None: return                 # entry guard
  ui.hide_ui()
  ... build DesignLibrary, DesignLoaderAdapter, hex_coord, portrait ...
  build_queue_screen = BuildQueueScreen(planet, ...)         # ~6.9 s
  # implicit show via construction
```

```
_on_build_queue_close():
  ... handle fleet BUILD-order auto-issue per-source ...
  build_queue_screen = None                                  # null the slot
  ui.show_ui()
  ... refresh selected-object detail panel ...
```

**Target** (after PROJ-376):

```
on_build_yard_click():
  ... build DesignLibrary, DesignLoaderAdapter, hex_coord, portrait ...
  _open_build_queue(planet, hex_coord, portrait)

_open_build_queue(yard, hex_coord, portrait):
  ui.hide_ui()
  if build_queue_screen is None:
      build_queue_screen = BuildQueueScreen(initial_yard=None, ...)   # ~6.9 s once
  build_queue_screen.open_for_yard(yard)                              # ~150 ms repeat
  # implicit show via open_for_yard
```

```
_on_build_queue_close():
  ... handle fleet BUILD-order auto-issue per-source ...
  # build_queue_screen NOT nulled — instance survives
  build_queue_screen.hide()                                  # explicit
  ui.show_ui()
  ... refresh selected-object detail panel ...
```

`open_for_yard(yard)` (new):

```
if build_context is not None and build_context.context_type != yard.context_type:
    _rebuild_panels(yard.context_type)
build_context = yard
hex_coord     = ... (passed in or recomputed; see decisions.md row 5)
queue_sources = collect_build_queues_at_hex(hex_coord, galaxy, empire, registries=session.registries)
selected_queue_indices = {0} if queue_sources else set()
active_queue_source    = queue_sources[0] if queue_sources else None
selected_queue_index   = None
planet_selection_window = None
controller.build_context = yard
controller.hex_coord     = hex_coord
if active_queue_source is not None:
    controller.set_active_queue(active_queue_source)
controller.reset_filters()                                # PROJ-373 Phase 1, dead until now
drag_handler.reset_state()
_queue_selector.queue_sources = queue_sources             # OR: _queue_selector.refresh(queue_sources)
_refresh_items_list()
_refresh_queue_display()                                  # also resyncs FEAT-17 pause label via renderer
show()
```

---

## Alternatives considered

### A. Keep one screen instance per yard (per-yard cache)
Construct on first click, store in `Dict[(yard_type, yard_id), BuildQueueScreen]`. **Rejected.** Memory unbounded; the user might cycle through 50 planets in a session. The win is from avoiding panel reconstruction, which is achieved with a single shared instance + `open_for_yard`. Per-yard caching is over-engineering.

### B. Keep `BuildQueueScreen.__init__` single-purpose (always takes a yard); reuse via "soft reset"
Same construction signature as today; add `open_for_yard(yard)` that does the post-init reset path. Manager constructs once with an arbitrary "initial" yard, then calls `open_for_yard` from then on. **Rejected.** The "arbitrary initial yard" creates phantom queue sources at app startup and forces the first user click to wait for an unused initial open. The shell-vs-yard split is cleaner and supports lazy first-open per PROJ-373 design.md alternative D.

### C. Rebuild panels every open, just keep `BuildQueueController` and `BuildQueueDragHandler`
Saves PROJ-373's 2.2 s validation cost (Phase 1 cache), but pays the 4.4 s panel construction every click. **Rejected.** The panel construction is the dominant cost; this gets us nowhere meaningfully closer to the 500 ms acceptance bar.

### D. Migrate `BuildQueueScreen` to subclass `pygame_gui.UIWindow` and use PROJ-313's `StrategyModalWindow`
Aligns with the strategy-window-modal pattern. **Rejected.** The full-screen-overlay vs. floating-window mismatch is structural — `UIWindow` adds title bars, draggable frames, etc., and `BuildQueueScreen` deliberately suppresses all of those by being a raw panel tree. The strategy modal-block check is for galaxy-screen input gating, but BuildQueueScreen hides the entire galaxy UI; there's no "underneath" to gate input from. This would be a much bigger refactor with no win for PROJ-376's goal.

### E. Eager construction at `StrategyBuildQueueManager.__init__`
Construct the screen up-front so the *first* click is also fast. **Rejected per PROJ-373 alternative D.** Pays the 6.9 s cost at game-load time even for sessions where the user never opens the build queue. Lazy first-open is correct.

### F. Use `manager.update(0)` after `hide()` to flush deferred work
Defensive: matches today's `_close()` flush. **Provisional accept.** Keep `manager.update(0)` in `hide()` for the first cycle; if no warnings appear in 30 seconds of hidden-state, remove. PROJ-373 design.md R2.4 raised this and we adopt the same posture.

### G. Reset queue-selector via `BuildQueueSelector.refresh()` vs. direct attribute mutation
The selector holds its own `queue_sources` list and rebuilds buttons on `refresh()`. Today the panel factory passes `queue_sources` once; the selector mutates internally. **Decision:** add a public `BuildQueueSelector.set_queue_sources(sources)` if one doesn't exist; otherwise mutate the attribute directly and call existing `refresh()`. Investigate during Phase 1 Task 1.5.

---

## Risks

- **R1 — Panel-tree internal state corruption.** UIPanel children retain pygame_gui state across hide/show. If any internal state corrupts (focus, drag, hover), subsequent opens behave oddly. Mitigation: add `manager.update(0)` to `hide()` and `show()` (provisional); manual smoke covers "open A, hide, open B, drag" path; add an automated smoke test that toggles hide/show 10 times and asserts no widget is in an invalid state.
- **R2 — `panels.background.kill()` was load-bearing for some side effect we don't see.** Today's `_close()` kills the panel tree, then calls `manager.update(0)` to flush the kill queue. Removing the kill removes the work but might also remove an implicit cleanup we depend on. Mitigation: hide-instead-of-kill is well-supported in pygame_gui (`set_visible(False)`); add a sharded test asserting `panels.background.alive` is True after `hide()` to lock the contract.
- **R3 — Cross-context-type rebuild leaks panels.** When `_rebuild_panels(context_type)` fires, the old panel tree must be killed before the new one is constructed; otherwise we get duplicate panels (and the drag handler's `dragged_item` references could dangle). Mitigation: `_rebuild_panels` calls `panels.background.kill()` first (matches today's `_close()` half), then `manager.update(0)`, then re-runs the factory. Add unit test for this path.
- **R4 — FEAT-17 pause-button label drifts.** The label is set via `renderer.refresh_pause_button(...)` which reads the active queue source's `is_paused`. If `open_for_yard` doesn't reset the active source first, the label could read the wrong yard's state. Mitigation: `open_for_yard` calls `controller.set_active_queue(active_queue_source)` (which is a no-op if same source) before any refresh path; `_refresh_queue_display()` already calls `renderer.refresh_pause_button(self.active_queue_source)` (line 387). Test: open yard A (paused), close, open yard B (unpaused) — assert label.
- **R5 — `PlanetSelectionWindow` lifecycle.** Opened mid-session via `_prompt_target_planet`. If left open when the user clicks Close, today's `_close()` kills it. Post-Phase-2, `hide()` must replicate this. Mitigation: copy lines 641-643 into `hide()`. Test: open planet selection window, close build queue without selecting — assert window is killed AND `self.planet_selection_window is None`.
- **R6 — Tests gated on construction count.** `tests/unit/ui/screens/test_strategy_build_queue_manager.py` calls `MockBQS.assert_called_once()` (line 99). Post-Phase-2 the second click does NOT call the constructor again. Mitigation: split the test into "first open constructs" and "subsequent open calls open_for_yard()" (Phase 2 task).
- **R7 — `is not None` check semantics shift.** Three sites (`strategy_event_router.py:58`, `strategy_input_handler.py:55`, `strategy_screen.py:246`) gate on `is not None`. Today this means "currently visible". Post-Phase-2 it means "ever opened". Migrating all three to `is_visible()` is correct for input/draw; the modal-block check is more subtle (decisions.md row 4).
- **R8 — Dimension-change pool rebuild on hide/show.** The PROJ-373 row-pool guard depends on the `_list_view_panel.get_relative_rect()` having had a layout pass (PROJ-373 review MIN-003). After `show()` the layout might be stale until the next `manager.update`. Mitigation: ensure `manager.update(0)` runs before `_refresh_queue_display()` triggers any pool-related work — or rely on the guard's correctness across stale-rect reads (unchanged dimensions = same fingerprint = no rebuild = correct outcome by accident; but flag this for the implementing agent).
- **R9 — Memory growth.** A surviving screen retains UIPanel trees + the `BuildQueueController._validation_cache`. Estimated ≤ 50 MB at 4K (PROJ-373 design.md R2.2). Acceptable.

---

## Dependencies

- **PROJ-373 Phase 1** must be merged (it is): controller cache + `reset_filters()` exist.
- **PROJ-373 Phase 3** must be merged (it is): row-pool guard pays off only when this lands.
- **PROJ-373 Phase 4** (`@fast_panel`) is independent but reduces first-open cost; doesn't affect this project.
- **PROJ-313** (StrategyModalWindow): not a dependency; we deliberately don't use it (decisions.md row 1).

## Open questions for the user

1. **Eager vs lazy first construction.** Do you want `BuildQueueScreen` constructed lazily on first build-yard click (cost paid at first open, subsequent opens fast — current PROJ-373 plan), OR eagerly at `StrategyBuildQueueManager.__init__` (cost paid at game-load, even first open is fast, but slows app startup by ~6.9 s for users who never open the build queue)? **Plan default: lazy** per PROJ-373 alternative D.
2. **Should `open_for_yard(yard, hex_coord)` accept hex_coord as a parameter, or recompute it from `yard`?** Today the manager computes `hex_coord` differently for planet (`parent_sys.global_location + planet.location`) vs. fleet (`fleet.location`) and via `on_navigate_to_hex_build` (passed in directly). If `open_for_yard` recomputes, we duplicate the logic; if it accepts the parameter, we leak manager-side concerns into the screen. **Plan default: accept `hex_coord` as a kwarg** — keeps the screen agnostic of the planet/fleet hex math.
3. **`hide()` semantics — set `panels.background.visible = False` (pygame_gui visibility flag) or call `set_visible(False)` (the official API)?** Plan default: `set_visible(False)` — the official API also stops event delivery to children, which is what we want. Confirm acceptable.
4. **Where does the close-callback `on_close()` fire — from `hide()` or the close-button handler only?** PROJ-373 phase_2_checklist.md tasks 2.5 punted on this. **Plan default: `hide()` does NOT invoke `on_close()`. The close-button handler invokes `hide()` then `on_close()` in sequence.** This way internal state-machine paths can hide without triggering the manager's "user closed it" semantics. Confirm.
5. **Should we eagerly invalidate the `_validation_cache` on a "leave strategy screen" event, or let it grow forever?** PROJ-373 design.md R5 estimated ≤ 50 MB but didn't measure. **Plan default: do nothing now**; revisit if telemetry shows growth. Confirm acceptable.
6. **Cross-context-type transitions (planet → fleet) — accept the construction cost or pre-cache both panel trees?** Plan default: rebuild on transition; same as PROJ-373 design.md "rare path". The user will see ~3.7 s on the rare cross-type click; acceptable in the typical "planet→planet→planet" flow. Confirm.
7. **Does Phase 1 ship-and-review independently, or is it bundled with Phase 2 for review?** 03c protocol fires a cumulative review per phase. Phase 1 is mechanically a no-op (manager unchanged) and a clean review locks the seam before Phase 2 mutates lifecycle. **Plan default: ship phase-by-phase under 03c.** Confirm.
