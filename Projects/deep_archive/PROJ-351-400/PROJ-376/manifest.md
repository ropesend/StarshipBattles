# PROJ-376 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| game/ui/screens/build_queue_screen.py | Production | 1, 2 | Phase 1: split `__init__` into shell + `open_for_yard()`; add `hide()`, `show()`, `is_visible()`, private `_rebuild_panels()`. Phase 2: delete `_close()`; route close button + Esc + `BUILD_QUEUE_CLOSE` action through `hide()` + `on_close()`. Phase 2: visibility-gate `handle_event`. |
| game/ui/panels/build_queue_drag_handler.py | Production | 1 | Add `reset_state()` (5 fields: `dragged_item`, `drag_preview`, `drag_start_pos`, `_pending_queue_index`, `selected_design`). |
| game/ui/screens/strategy_build_queue_manager.py | Production | 2 | Extract `_open_build_queue(yard, hex_coord, portrait_surface)` helper; 3 entry points (lines 71, 175, 229) call it. First call constructs `BuildQueueScreen(initial_yard=None, ...)`; subsequent calls invoke `open_for_yard()`. Update `_on_build_queue_close` (line 116) — call `hide()` instead of nulling. Remove 3 entry guards (lines 74, 186, 232). |
| game/ui/screens/strategy_event_router.py | Production | 2 | Migrate line 58 modal-block check to `is_visible()`. |
| game/ui/screens/strategy_input_handler.py | Production | 2 | Migrate lines 55-56 event routing to `is_visible()`. |
| game/ui/screens/strategy_screen.py | Production | 2 | Migrate line 246 draw call to `is_visible()`. |
| game/ui/panels/build_queue_controller.py | Production | 3 | Update `reset_filters()` docstring/comment (line 260-268): replace "Phase 2 prerequisite, dead code until then" with "Live since PROJ-376; called from `BuildQueueScreen.open_for_yard`." Address PROJ-373 review MIN-002 (HFS+ comment near line 213). |
| game/ui/components/table/virtual_table.py | Production | 3 | Address PROJ-373 review MIN-003: docstring for public `rebuild_row_pool()` notes the layout-pass dependency. No code change. |
| tests/unit/ui/screens/test_build_queue_screen_lifecycle.py | Test (NEW) | 1, 2 | Phase 1: shell-only construction, `open_for_yard` state mutation parity, `reset_state()` clears all 5 drag fields, `_rebuild_panels` on context-type change. Phase 2: instance reuse across N opens, `hide`/`show`/`is_visible`, close-callback no longer nulls slot, FEAT-17 pause label resync, PlanetSelectionWindow killed on hide. |
| tests/unit/ui/screens/test_strategy_build_queue_manager.py | Test (modify) | 2 | Update `MockBQS.assert_called_once()` (line 99) to assert "first open constructs, second open calls open_for_yard". Add tests for the close-callback no longer nulling. |
| tests/integration/ui/build_queue_screen/test_basics.py | Test (modify) | 2 | Update `_close()` reference at line 188 to `hide()`. |
| tests/unit/ui/components/table/test_virtual_table.py | Test (modify) | 3 | Add test for column-config change without dimension change (PROJ-373 review MIN-005). |
| Projects/active_projects/PROJ-373/plan.md | Doc | 3 | Backfill MAJ-003 caveat (Phase 1 row 17 — "Effective cross-open only after PROJ-376"); update Phase 2 detailed status (lines 105-108 — "Deferred → Completed in PROJ-376"). |
| Projects/active_projects/PROJ-376/findings/post_proj376_profile.md | Doc (NEW) | 3 | Re-profile evidence: before/after numbers from `python Tools/profile_game/profile_game.py` confirming repeat-open `< 0.5 s` acceptance bar. |

## File-conflict summary by phase

- **Phase 1:** `build_queue_screen.py`, `build_queue_drag_handler.py`, plus the new lifecycle test file. Two production files.
- **Phase 2:** `build_queue_screen.py` (deletes `_close`), `strategy_build_queue_manager.py`, `strategy_event_router.py`, `strategy_input_handler.py`, `strategy_screen.py`, plus the existing manager test + the integration `test_basics.py` plus the lifecycle test file. Five production files. Phase 2 conflicts with Phase 1 on `build_queue_screen.py` — must be sequential per 03c DAG.
- **Phase 3:** `build_queue_controller.py`, `virtual_table.py` (docstring only), test_virtual_table, PROJ-373 plan.md, new findings doc. No conflict with Phase 1/2.

## DAG

```
phase_1 → phase_2 → phase_3
```

All sequential. Phase 1 must be `verified` before Phase 2 spawns; Phase 2 must be `verified` before Phase 3 spawns. `buffer_depth: 0`.
