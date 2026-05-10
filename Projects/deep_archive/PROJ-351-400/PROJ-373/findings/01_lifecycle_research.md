# PROJ-373 — Build queue UI lifecycle research

> Source: Explore subagent run 2026-05-05.
> Read-only investigation; no files modified.

## 1. Lifecycle today

**Construction (3 entry points, all create a fresh instance):**
- `game/ui/screens/strategy_build_queue_manager.py:100`
- `game/ui/screens/strategy_build_queue_manager.py:213`
- `game/ui/screens/strategy_build_queue_manager.py:257`

Stored at `StrategyScreen.build_queue_screen`. Entry guards at lines 74-76,
186-188, 232-234 prevent double-open.

**Destruction:** `BuildQueueScreen._close()` at
[build_queue_screen.py:639-649](../../../../game/ui/screens/build_queue_screen.py#L639). Only kills
`planet_selection_window` and `panels.background`. Calls `manager.update(0)`
to flush pygame_gui cleanup. Invokes `on_close_callback`
([strategy_build_queue_manager.py:116](../../../../game/ui/screens/strategy_build_queue_manager.py#L116)) which
sets `self._screen.build_queue_screen = None`.

**No existing caching.** Every click is a fresh construction.

## 2. State held by `BuildQueueScreen`

**Yard-specific (must refresh per yard):**
- `build_context` (line 71), `hex_coord` (line 82): yard identity
- `queue_sources` (line 91): collected via `collect_build_queues_at_hex()`
- `active_queue_source` (line 97), `selected_queue_indices` (line 96): selection state
- `planet_selection_window` (line 85): dialog ref

**Session/galaxy (reusable):**
- `session` (line 72), `galaxy` (line 83), `empire` (line 84)
- `design_library`, `design_loader` (lines 80-81)

**UI shell (reusable):**
- `manager` (line 70) — pygame_gui UIManager
- `_mapper` (line 76) — input mapper
- `facade` (line 73) — CQRS facade
- `portrait_loader` (line 88) — has internal portrait cache

**Renderer/controller state:**
- `panels` (line 120): yard-context-dependent layout (planet vs fleet panel differs)
- `renderer` (line 124), `controller` (line 132): wraps panels
- `drag_handler` (line 152): holds drag state; needs reset on reuse
- `selected_queue_index` (line 77): per-yard selection

## 3. Reusable vs. must-rebuild

The **panel structure is NOT yard-data-dependent** — only the data populated into it changes. Layout is fixed per *context type* (planet vs. fleet), so the panel tree only needs rebuild on planet→fleet (or vice-versa) transitions.

Minimum yard-switch reset:
- Resync `queue_sources`
- Reset `active_queue_source`, `selected_queue_indices`
- Reset `controller.selected_category`, `controller.selected_role`
- Reset `drag_handler` state (`dragged_item`, `drag_start_pos`, `selected_design`)
- Reset `planet_selection_window`, `selected_queue_index`
- Repoint `controller`/`renderer` to new active queue source
- Re-run `_refresh_items_list()` and `_refresh_queue_display()`

## 4. `VirtualTable._rebuild_row_pool` (~1.5s/click)

Builds widget instances for visible rows: `UIPanel` row backgrounds, plus per-column `UILabel`/`UIImage`/`UIButton` widgets, action buttons (+, -, ↑, ↓, replay).

**Pool size:** `visible_rows = max(1, (panel_height // row_height) + 2)` ([virtual_table.py:161](../../../../game/ui/components/table/virtual_table.py#L161)). Typically 10-20 rows. Geometry-dependent (panel height), **not** queue-data-dependent.

Virtual scrolling decouples pool size from queue length — `update_visible_rows()` only changes content, not widget count.

**Reusable across opens:** YES if panel height is unchanged (typical case). Just call `data_source.set_queue()` ([virtual_table.py:159](../../../../game/ui/components/table/virtual_table.py#L159)) plus `update_scroll_bar() + force_update() + update_visible_rows()`. Cost drops from ~1.5s to milliseconds (already dirty-tracked at lines 272-274).

## 5. Coupling risks

- **No event-bus subscriptions** in `BuildQueueScreen` (battle_screen has them; build queue does not). Safe — no listeners to leak.
- **No constructor-time global registration** beyond pygame_gui buttons attached to `manager`. `panels.background.kill()` recursively kills children, so the existing close path already cleans pygame_gui state correctly — but if the screen is reused, we need to NOT kill the background and instead just hide it.
- **`portrait_loader`**: has internal cache; safe to reuse if `design_library` reference is updated.
- **`drag_handler`**: holds `dragged_item` / `drag_start_pos` / `selected_design` ([build_queue_drag_handler.py:74-81](../../../../game/ui/screens/build_queue_drag_handler.py#L74)). **Must reset on reuse.**
- **Only one external reference** to the screen instance: `StrategyScreen.build_queue_screen` (used at manager.py:74, 135, 186). Safe to keep alive across opens.

## 6. Existing refresh paths

**`_refresh_items_list()`** ([build_queue_screen.py:362](../../../../game/ui/screens/build_queue_screen.py#L362)):
- `controller.load_designs_by_category()` → scans designs from disk + validates
- `renderer.refresh_items_list()` ([build_queue_renderer.py:53](../../../../game/ui/screens/build_queue_renderer.py#L53)) → CLEARS scrollable container at line 63, recreates all design buttons
- **Full UI rebuild**, expensive even on a reused screen — Phase 1 of this project (validate-designs cache) addresses the disk/validate cost; the button-recreation part can be made incremental as a follow-up if needed.

**`_refresh_queue_display()`** ([build_queue_screen.py:369](../../../../game/ui/screens/build_queue_screen.py#L369)):
- Calls `renderer.refresh_queue_display()` → `data_source.set_queue()` + VirtualTable updates
- Already incremental via dirty-tracking — milliseconds when rows unchanged.

## 7. Concrete refactor sketch

1. **Move construction** from `on_build_yard_click` (3 sites) into `StrategyBuildQueueManager.__init__` or a lazy first-open path. Store as manager-level instance variable. Remove the 3 entry guards.
2. **Add `BuildQueueScreen.open_for_yard(yard)`** that:
   - If `build_context != yard`: refresh `queue_sources`, reset selection state, reset controller filters, reset drag handler, refresh items + queue display.
   - If panel layout type changes (planet ↔ fleet): rebuild panels (rare path).
   - Show UI.
3. **Replace `on_build_yard_click` body** with `screen.open_for_yard(planet)`. No more callback-driven nulling.
4. **Replace `_close()`** with `hide()` — don't kill `panels.background`, just hide it. Keep instance alive.
5. **Invalidation rule for full rebuild:** `build_context.context_type` changes (planet ↔ fleet), OR screen dimensions change significantly (`UIManager` resize). Otherwise: reuse panels and refresh data only.
6. **Caching location:** `StrategyBuildQueueManager._screen.build_queue_screen` persists across clicks. The close path becomes `hide()` (no `= None`).
