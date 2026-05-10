# PROJ-410 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/components/table/virtual_table.py` | Production | Phase 2: add `_data_identity_dirty: bool` flag (~line 103); add `invalidate_widget_caches() -> None`; gate `update_visible_rows()` early-return at lines 318–323 on the flag; clear flag after re-render loop; re-bind row indices for action buttons. No `.kill()` calls. |
| `game/ui/screens/build_queue_renderer.py` | Production | Phase 3: add `virtual_table.invalidate_widget_caches()` call between `data_source.set_queue(...)` and `virtual_table.update_visible_rows()` in `refresh_queue_display()` (~lines 140–164). |
| `game/ui/screens/build_queue_screen.py` | Production | Phase 3: verify and tighten resets in `open_for_yard()` (lines 264–344) for `controller.active_queue_source` / `controller.selected_queue_sources` / `drag_handler.selected_design`. Add `# PROJ-410:` comment near the C-hook. Possibly small change to `show()` (lines 369–373) to propagate visibility to selector container. Phase 4: add `on_active_player_changed() -> None` near `_request_close()` (~lines 823–838). |
| `game/ui/panels/build_queue_drag_handler.py` | Production | Phase 3 (CONDITIONAL on Phase 1 Task 1.1 finding): add `self.selected_design = None` to `reset_state()` body (lines 88–101). Skip if Phase 1 verifies the field is already cleared. |
| `game/ui/panels/build_queue_controller.py` | Production | Phase 3: verify only — likely no edit if `set_active_queue()` already clears `selected_queue_sources`. If gap, small additive reset. |
| `game/ui/screens/build_queue_selector.py` | Production | Phase 3: container-visibility fix. Either call `show()` on the selector's `UIScrollingContainer` in `refresh()`, or rely on a fix in `BuildQueueScreen.show()` to propagate visibility. |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | Phase 4: add `_last_active_empire_id: int \| None` to `__init__`. In `_open_build_queue()` (~lines 89–147), poll `facade.get_active_empire()` and call `screen.build_queue_screen.on_active_player_changed()` when the empire id changes. |
| `game/ui/screens/strategy_screen.py` | Production | Phase 4: in the `session` setter (~lines 231–248), after the facade rebind call `self.build_queue_screen.on_active_player_changed()` and reset `self._build_queue_manager._last_active_empire_id`. |
| `docs/02_PATTERNS.md` | Documentation | Phase 5: extend Pattern #11 (Surface Caching) with cross-context invalidation guidance. Bump `Last verified` stamp. |
| `tests/unit/ui/components/table/test_virtual_table.py` | Test | Phase 1: tests for `_data_identity_dirty` initial value, button-press-after-switch (Task 1.6). Phase 2: tests for `invalidate_widget_caches()` (default, idempotent, no `.kill()`), guard gating on the flag, ephemeral flag clearing. |
| `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | Test | Phase 1: add tests 1.2 (yard-switch), 1.3 (close+reopen), 1.4 (turn-boundary), 1.5 (same-planet-different-yard), and possibly 1.6 (button-press) if not in test_virtual_table.py. Phase 4: test for `on_active_player_changed()`. |
| `tests/unit/ui/screens/test_strategy_build_queue_manager.py` | Test | Phase 4: test that manager polls `facade.get_active_empire()` and calls `screen.on_active_player_changed()` on change. |
| `tests/integration/ui/build_queue_screen/test_queue_selector.py` | Test | Phase 1: test 1.7 (yard-selector visible on second player's planet). |
| `tests/integration/ui/build_queue_screen/test_basics.py` | Test | Phase 1 (or new file `test_save_load.py` in the same directory): test 1.8 (save/load does not leak prior session). |
| `tests/unit/ui/panels/test_build_queue_drag_handler.py` | Test | Phase 1: test 1.1 — verifies `selected_design` reset behavior (failing or locking, depending on outcome). May not exist as a file today; if not, create. |
| `tests/unit/ui/screens/test_build_queue_renderer.py` | Test | Phase 3 (optional): assert `invalidate_widget_caches` is called exactly once per `refresh_queue_display()`. May not exist today; create or extend the closest sibling. |
