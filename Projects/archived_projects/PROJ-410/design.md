# PROJ-410: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Two perf landings compose poorly under yard switches with identical panel geometry:

- **PROJ-373 phase 3** (`aca743a25`): `VirtualTable._rebuild_row_pool()` early-returns when `_pool_dims_changed()` is false. Geometry is the only signal; data identity is not considered.
- **PROJ-376 phase 2** (`a93330bb9`): `BuildQueueScreen` is a reused singleton across yards, panel reopens, and player turns. Panels survive `_request_close()`.

When these compose:

1. `BuildQueueScreen.open_for_yard()` is called for a new yard with the same panel geometry.
2. `BuildQueueRenderer.refresh_queue_display()` calls `data_source.set_queue(queue, build_rate)` then `virtual_table.update_visible_rows()`.
3. `_rebuild_row_pool()` early-returns — pool widgets retain `_last_text` / `_last_img` / `_last_color` from the previous yard.
4. `update_visible_rows()` early-returns at lines 318–323 when `(scroll_pct, row_count)` match the previous yard. When this fires, the entire refresh is skipped.
5. When the dirty check does not fire, the inner per-widget update at line 420 still skips writes when `text == widget.get("_last_text")` — labels with matching text keep stale image/color.
6. Action button handlers bound during pool construction reference the pool row's stored `row_index`. If the pool is reused without re-binding, `+`/`-` clicks dispatch to the *previous* yard's data row index — destructive.
7. `BuildQueueController.active_queue_source` and `selected_queue_sources` may not get reset between yards (verified by swarm).
8. `BuildQueueDragHandler.selected_design` reset status is ambiguous — to be resolved in Phase 1 Task 1.1.
9. No UI hook flushes any of this at end-of-turn or save-load.

## Swarm Findings Summary

Eight Phase B Explore agents reviewed the proposed B+C+A design. Detailed reports under `findings/`. Highlights:

### Architecture
- `VirtualTable.invalidate_widget_caches()` belongs on the component itself; `virtual_table.py` is at 607 LOC (over the 500 ceiling but pre-existing; PROJ-410 adds ~10–12 lines).
- `StrategySessionFacade` has no callback/subscribe surface; only `process_turn(progress_callback=...)` exists. Manager polling `self._screen.current_empire.id` (existing `StrategyScreen` property at `strategy_screen.py:192`; no new facade method) is more consistent with the existing read-only accessor pattern than introducing a new event API.
- PROJ-382 facade-bypass guard is unaffected; bypass = direct session calls, not new facade methods.
- Pattern #11 (Surface Caching) endorses `invalidate_cache()` methods on components owning local caches — the new method follows precedent.

### Key Patterns to Reuse
- **Pattern #5 (Facade/Delegate)** — manager polls `self._screen.current_empire.id` (existing `StrategyScreen` property at `strategy_screen.py:192`; no new facade method); UI never touches strategy state directly.
- **Pattern #8 (MVVM, Build Queue collaborators)** — the canonical split (`BuildQueueController`, `BuildQueueRenderer`, `BuildQueuePanelFactory`, `BuildQueueDragHandler`) is preserved; invalidation responsibility lives in the renderer (data) and the screen (lifecycle).
- **Pattern #11 (Surface Caching)** — extend with cross-context invalidation note; document the new method as the canonical example.
- **Pattern #33 (UI Widget Test Factory)** — reuse `make_ui_widget` / `bypass_init` for new tests.

### Dependencies & Risks
1. **PROJ-373 phase 3 perf lock** — `TestRowPoolReuseGuard` asserts widget `.kill()` call counts. Invalidation MUST NOT call `.kill()`. Mitigation: only null cache attributes; do not rebuild the pool.
2. **PROJ-376 phase 2 perf budget** — `<0.5s` repeat-open. Mitigation: invalidation cost is ~1–2 ms (Performance Analyst measured ~30 rows × ~16 widgets); next re-render ~6–15 ms; well within budget.
3. **Save/load mid-session leaks stale empire/planet refs into the cached screen.** Originally surfaced by Risk Assessor as a need for a `StrategyScreen.session` setter hook. **Codex review (arc01-002) corrected this**: the production load path constructs a brand-new `StrategyScreen` via `screen_router.py:324-344`; the `session` setter is test-only and never fires in production. **Final mitigation:** Phase 1 Task 1.8 asserts the production guarantee that `_on_load_game()` produces a fresh screen with `_build_queue.build_queue_screen is None`. No setter hook needed.
4. **Permanent dirty flag would cause per-frame re-render** (~10–20% FPS drop). Mitigation: ephemeral flag — clear after first re-render in `update_visible_rows()`.
5. **`drag_handler.selected_design` reset claim was ambiguous.** Triage and one swarm agent reported it not cleared; Yard-Selector Investigator reported it is. **Codex review (arc01-002) confirmed it IS cleared** at `build_queue_drag_handler.py:101`. Phase 1 Task 1.1 writes a locking regression to prevent future regressions. Phase 3 Task 3.3 dropped.
6. **B-hook fires on every queue mutation** (~1–2 ms redundant when contents unchanged). Acceptable for now per Performance Analyst; deferred generation-counter optimization noted in decisions.md.

### Opportunities Discovered
- The yard-selector "missing on second player's planet" symptom turns out to be a *separate, smaller* container-visibility regression, not the cache bug. Small fix folds cleanly into PROJ-410's same-scenario regression coverage.
- The architecture lets us avoid adding any new facade event/subscription surface, keeping the strategy session facade clean.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

## Three-Layered Hook Architecture

```
+-----------------------------------------------------+
|  StrategyBuildQueueManager._open_build_queue()       |
|    current_id = self._screen.current_empire.id      |
|    if current_id != self._last_active_empire_id:    |   <- A-hook
|        cached_screen.on_active_player_changed()     |       (player-change
|    cached_screen.empire = self._screen.current_empire        flush)
|    cached_screen.galaxy = self._screen.galaxy       |   <- A-hook
|    cached_screen.facade = self._screen.facade       (rebind, every
|    self._last_active_empire_id = current_id         |       open)
|    cached_screen.open_for_yard(...)                 |
+--------------------------+--------------------------+
                           |
                           v
+-----------------------------------------------------+
|  BuildQueueScreen.open_for_yard()                    |
|    - resets controller queue refs                   |
|      (incl. ZERO-source path, new Task 3.6)         |   <- C-hook (lifecycle)
|    - drag_handler.reset_state() (selected_design    |
|      already cleared per Codex; locked by 1.1)      |
|    - calls _refresh_queue_display()                 |
+--------------------------+--------------------------+
                           |
                           v
+-----------------------------------------------------+
|  BuildQueueRenderer.refresh_queue_display()          |
|    - data_source.set_queue(...)                     |
|    - virtual_table.invalidate_widget_caches()       |   <- B-hook (content)
|    - virtual_table.force_update()  (already there)  |
|    - virtual_table.update_visible_rows()            |
+--------------------------+--------------------------+
                           |
                           v
+-----------------------------------------------------+
|  VirtualTable.update_visible_rows()                  |
|    - early-return guard now also checks             |
|      _data_identity_dirty (defense-in-depth;        |
|       force_update() is the BQ-specific trigger)    |
|    - re-renders all visible rows on first pass      |
|    - row["row_index"] = data_idx for each visible   |
|      row (ALREADY present; click handlers read this |
|      at click time per check_action_button_press()) |
|    - clears _data_identity_dirty (ephemeral)        |
+-----------------------------------------------------+

Save/load — production guarantee (no setter hook needed):
  ScreenRouter._on_load_game()  (game/screen_router.py:324-344)
    - constructs a brand-new StrategyScreen(session=game_session, ...)
    - replaces strategy_scene wholesale
    - new screen has _build_queue.build_queue_screen == None
    - Phase 1 Task 1.8 asserts this guarantee
```

## Constraints Summary

| Constraint | Source | Mitigation in PROJ-410 |
|---|---|---|
| `TestRowPoolReuseGuard` `.kill()` count assertions | PROJ-373 phase 3 | Invalidation only nulls cache attrs; never calls `.kill()` |
| `<0.5s` repeat-open | PROJ-376 phase 2 | Invalidation overhead ~7–17 ms; well within budget |
| Facade-bypass guard | PROJ-382 phase 1 | All new code routes through facade read accessors and `handle_command` |
| Validation cache survives yard switches | PROJ-373 phase 1 | Untouched; lives on controller, not on table or panels |
| Manager reuse semantics | PROJ-376 phase 2 | Manager continues to reuse the cached screen instance; A-hook just calls a method on it AND rebinds `empire`/`galaxy`/`facade` before each `open_for_yard()` |
| Pattern #5 facade contract | docs/02_PATTERNS.md | Manager polls `self._screen.current_empire.id` (existing property at `strategy_screen.py:192`); no new facade event surface, no new facade accessor |
