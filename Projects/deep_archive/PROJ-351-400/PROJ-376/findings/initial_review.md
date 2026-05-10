# PROJ-376 Initial Review — Top 5 Surprising Facts

> Notes from the planning-time investigation, kept tight per ≤1 page guidance.
> Each item links to the file:line evidence so the implementing agent can
> jump straight to the relevant code.

---

## 1. `BuildQueueScreen` is NOT a `pygame_gui.UIWindow` — it is a plain Python class wrapping a full-screen `UIPanel` tree

The original PROJ-373 deferral note suggested PROJ-313's `StrategyModalWindow` machinery might be relevant. It isn't. The class declaration at `game/ui/screens/build_queue_screen.py:38` is `class BuildQueueScreen:` — no parent. The "modal" overlay is achieved by:

- `panels.background` is a `pygame_gui.UIPanel` sized to the full screen (`build_queue_panel_factory.py:200-204`).
- The galaxy UI is hidden separately via `screen.ui.hide_ui()` at `strategy_build_queue_manager.py:82`.
- The nested `PlanetSelectionWindow` (the only `UIWindow` child) is constructed with `window_manager=None` and a comment "PROJ-313: build queue screen has its own modal lifecycle" (`build_queue_screen.py:628`).

**Implication:** PROJ-376 does NOT migrate to `StrategyModalWindow`. The "lifecycle" we're refactoring is plain Python object lifecycle plus pygame_gui panel visibility, not modal-window registry semantics.

## 2. `BuildQueueDragHandler` holds **5** transient state fields, not 3

The PROJ-373 plan listed 3 (`dragged_item`, `drag_start_pos`, `selected_design`). Reading `game/ui/panels/build_queue_drag_handler.py:73-81` (this file is the canonical drag handler — note that `build_queue_drag_handler.py` has been moved to `game/ui/panels/`, not `game/ui/screens/` as PROJ-373 implies in some places):

```python
self.dragged_item: Optional[dict] = None        # line 74
self.drag_preview: Optional[pygame.Surface] = None  # line 75 — surface cache
self.drag_start_pos: Optional[tuple] = None     # line 76
self._pending_queue_index: Optional[int] = None # line 78 — captured queue-row click
self.selected_design: Optional[str] = None      # line 81
```

**Implication:** `reset_state()` must clear 5 fields. Missing `_pending_queue_index` would let a half-clicked queue row in yard A prime the drag in yard B. Phase 1 Task 1.5 enumerates all 5 explicitly.

## 3. `_close()` flow is shorter than expected — only 4 actions; `manager.update(0)` is the load-bearing one

`game/ui/screens/build_queue_screen.py:639-649`:

1. Kill `planet_selection_window` if non-None.
2. Kill `panels.background` (recursive child kill).
3. `manager.update(0)` — flush deferred kills.
4. `on_close_callback()`.

Replacement plan: `hide()` does (1) and a `set_visible(False)` instead of (2). `manager.update(0)` from (3) is preserved. (4) moves to the close-button handler so `hide()` can be called from non-close paths without firing the manager-side cleanup.

## 4. `_validation_cache` cross-open value is gated entirely by this project — TODAY it provides ZERO cross-open value

PROJ-373 review MAJ-003 flagged this; the magnitude is worth re-emphasizing. `BuildQueueController._validation_cache` is allocated in `BuildQueueController.__init__` at `build_queue_controller.py:115`. The controller is instantiated inside `BuildQueueScreen.__init__` at `build_queue_screen.py:132`. **Every `_close()` destroys both.** PROJ-373 Phase 1 saves 2.2 s only on intra-open category toggles ("Ships → Complexes → Ships" within one click). PROJ-376 unlocks the cross-open win.

**Implication:** PROJ-373's acceptance bar (`< 0.5s` repeat-open) only becomes achievable after Phase 2 ships. Phase 3's re-profile is the moment of truth.

## 5. PROJ-373 Phase 3's row-pool guard is BIT-CORRECT but provides ZERO savings today (similar to MAJ-003)

The guard at `game/ui/components/table/virtual_table.py:148-211` correctly checks `(panel_height, panel_width, row_height, col_fp)` (PROJ-373 review MAJ-001 + MAJ-002 already remediated in-band). On a repeat open, the pool's fingerprint would be identical and the guard would short-circuit the 1.5 s rebuild. **But the guard never triggers today** because the entire `VirtualTable` is destroyed and reconstructed when `panels.background.kill()` recursively kills it. Phase 2's panel-tree reuse is the trigger. PROJ-373 review INFO-003 made this explicit.

**Implication:** PROJ-376 Phase 2 is the operational unlock for both PROJ-373 Phase 1 (2.2 s) AND Phase 3 (1.5 s) cross-open savings — combined ~3.7 s/click on top of Phase 4's first-open-only ~3 s win.

---

## Cross-cutting note: `is not None` callsites today conflate "instance exists" with "currently displayed"

Three production sites currently gate on `scene.build_queue_screen is not None`:

- `game/ui/screens/strategy_event_router.py:58` — modal-block check
- `game/ui/screens/strategy_input_handler.py:55` — event-routing check
- `game/ui/screens/strategy_screen.py:246` — draw call

Today these mean "currently displayed" because the slot is nulled on close. Post-Phase-2 they will mean "ever opened in this session". All three migrate to `is_visible()` per decisions.md row 4. The modal-block check at the event router is the most subtle: when build queue is hidden, `ui.show_ui()` has restored the galaxy underneath and there IS a galaxy to receive clicks — so `is_visible()` correctly preserves the original "is the modal currently overlaying the galaxy" semantics.
