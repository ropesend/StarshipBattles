# PROJ-352 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/new_game_setup_screen.py` | Production (docstring) | T4.7 — fix misleading docstring at lines 20-28 (builder does NOT own the widget tree currently — `build()` passthroughs to `screen._create_ui()`) |
| `game/ui/screens/strategy_screen_lifecycle.py` | Production (refactor) | T6.6 — `show_load_game_dialog()` registers the dialog with the modal tracker instead of dropping the instance |
| `game/ui/screens/save_selection_window.py` | Production (possibly refactor) | T6.6 — migrate to `StrategyModalWindow` OR keep as raw UIWindow but ensure modal tracker sees it |
| `game/ui/screens/strategy_window_manager.py` | Production (possibly add slot) | T6.6 — add `load_dialog` (or similar) slot to `iter_live_modals()` flow if going the slot route |
| `game/ui/screens/strategy_event_router.py` | Production (possibly refactor) | T6.6 — modal detection at lines 47-73 includes the load dialog |
| `tests/unit/ui/screens/test_save_selection_window*.py` | Test (update) | T6.6 — adapt to whichever shape lands |
| `tests/unit/ui/screens/test_strategy_event_router_modal_tracking.py` (or similar) | Test (NEW) | T6.6 — regression test asserting load dialog blocks strategy input |
| `Projects/active_projects/PROJ-352/plan.md` | Project artifact | Updates per phase |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 2 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 (T4.7) | `pytest tests/unit/ui/screens/ -k "new_game_setup" -x -q` |
| 2 (T6.6) | `pytest tests/unit/ui/screens/ -k "save_selection or strategy_event_router or strategy_screen_lifecycle or strategy_window_manager" -x -q` |
| Final | `pytest tests/unit/ -q` then `python Tools/lint_test_files.py` then manual load-dialog smoke |
