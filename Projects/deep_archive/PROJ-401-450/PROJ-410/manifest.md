# PROJ-410 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/components/table/virtual_table.py` | Production | Phase 2: add `_data_identity_dirty: bool` flag (~line 103); add `invalidate_widget_caches() -> None`; gate `update_visible_rows()` early-return at lines 318–323 on the flag; clear flag after re-render loop; re-bind row indices for action buttons. No `.kill()` calls. |
| `game/ui/screens/build_queue_renderer.py` | Production | Phase 3: add `virtual_table.invalidate_widget_caches()` call between `data_source.set_queue(...)` and `virtual_table.update_visible_rows()` in `refresh_queue_display()` (~lines 140–164). |
| `game/ui/screens/build_queue_screen.py` | Production | Phase 3: tighten resets in `open_for_yard()` (lines 264–344) — explicitly handle the **zero-source branch** by calling `controller.set_selected_queues([])` (Task 3.6). Add `# PROJ-410:` comment near the C-hook. Possibly small change to `show()` (lines 369–373) to propagate visibility — gated on whether Phase 1 Task 1.7 still fails after Phase 4 lands. Phase 4: add `on_active_player_changed() -> None` near `_request_close()` (~lines 823–838). |
| `game/ui/panels/build_queue_drag_handler.py` | (no edit) | Codex review confirmed `reset_state()` line 101 already clears `selected_design`. Phase 1 Task 1.1 writes a locking regression test only. Phase 3 Task 3.3 dropped. |
| `game/ui/panels/build_queue_controller.py` | Production (small) | Phase 3 Task 3.6: zero-source reset path. Either reuse `set_selected_queues([])` (existing API at lines 132–143) from the screen's `open_for_yard()`, or add a new `clear_queue_selection()` method. Prefer the former for minimal API surface. |
| `game/ui/screens/build_queue_selector.py` | Production | Phase 3: container-visibility fix. Either call `show()` on the selector's `UIScrollingContainer` in `refresh()`, or rely on a fix in `BuildQueueScreen.show()` to propagate visibility. |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | Phase 4 Task 4.2: add `_last_active_empire_id: int \| None` to `__init__`. In `_open_build_queue()` (~lines 89–147), poll `self._screen.current_empire.id` (per `strategy_screen.py:192`); on change, call `cached_screen.on_active_player_changed()`. **Always before `open_for_yard()`**: rebind `cached_screen.empire` / `cached_screen.galaxy` / `cached_screen.facade` to current values so the cached screen queries as the current empire. |
| `game/ui/screens/strategy_screen.py` | (no edit) | Phase 4 Task 4.3 DROPPED entirely per Codex review (arc01-006). Production load creates a fresh `StrategyScreen` via `screen_router.py:324-344`; the `session` setter is test-only and never fires in production. The `current_empire` property at line 192 is READ by the manager (Task 4.2), not modified. |
| `docs/02_PATTERNS.md` | Documentation | Phase 5: extend Pattern #11 (Surface Caching) with cross-context invalidation guidance. Bump `Last verified` stamp. |
| `tests/unit/ui/components/table/test_virtual_table.py` | Test | Phase 1: tests for `_data_identity_dirty` initial value, button-press-after-switch (Task 1.6). Phase 2: tests for `invalidate_widget_caches()` (default, idempotent, no `.kill()`), guard gating on the flag, ephemeral flag clearing. |
| `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | Test | Phase 1: add tests 1.2 (yard-switch), 1.3 (close+reopen), 1.4 (turn-boundary), 1.5 (same-planet-different-yard), and possibly 1.6 (button-press) if not in test_virtual_table.py. Phase 4: test for `on_active_player_changed()`. |
| `tests/unit/ui/screens/test_strategy_build_queue_manager.py` | Test | Phase 4: test that manager polls `self._screen.current_empire.id` (existing `StrategyScreen` property at `strategy_screen.py:192`), calls `screen.on_active_player_changed()` on change, and rebinds `cached_screen.empire`/`galaxy`/`facade` before each `open_for_yard()`. |
| `tests/integration/ui/build_queue_screen/test_queue_selector.py` | Test | Phase 1: test 1.7 (yard-selector visible on second player's planet). |
| `tests/integration/ui/build_queue_screen/test_basics.py` | Test | Phase 1 (or new file): test 1.9 (zero-source yard switch). |
| `tests/unit/test_screen_router.py` | Test | Phase 1 Task 1.8 (reframed): assert `_on_load_game()` produces a fresh `StrategyScreen` with `_build_queue.build_queue_screen is None`; existing test at lines 303-365 is the natural neighbor. |
| `tests/unit/ui/panels/test_build_queue_drag_handler.py` | Test | Phase 1 Task 1.1: locking regression for `selected_design` reset (already-passing assertion to prevent future drop). |
| `tests/unit/ui/panels/test_build_queue_controller.py` | Test | Phase 1 Task 1.9 + Phase 3 Task 3.6 verification — zero-source yard switch clears controller queue refs. |
| `tests/unit/ui/screens/test_build_queue_renderer.py` | Test | Phase 3 (optional): assert `invalidate_widget_caches` is called exactly once per `refresh_queue_display()`. May not exist today; create or extend the closest sibling. |
