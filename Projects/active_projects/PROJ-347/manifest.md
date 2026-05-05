# PROJ-347 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/star_list_window.py` | Production (refactor) | T4.1 — add `virtual_table` placeholder per Pattern §33 |
| `game/ui/screens/planet_list_window.py` | Production (refactor) | T4.1 — same |
| `game/ui/screens/system_selection_window.py` | Production (refactor) | T4.2 — add `btn_confirm`/`btn_cancel` placeholders |
| `game/ui/screens/save_selection_window.py` | Production (refactor) | T4.3 — add `process_event` placeholder |
| `game/ui/screens/race_browser_dialog.py` | Production (refactor) | T4.3 — same (locate via grep) |
| `game/ui/screens/design_selector_window.py` | Production (refactor) | T4.3 — same (locate via grep) |
| `game/ui/screens/empire_panel_window.py` | Production (refactor) | T4.4 — move `load_resource_icons()` AFTER bypass guard |
| `docs/02_PATTERNS.md` | Doc (update) | T4.5 — fix self-contradiction lines 1765-1776 vs 1833 |
| `game/ui/screens/race_setup/screen.py` | Production (set field) | T4.6 — `_window_init_bypassed = False` in production path |
| `game/ui/screens/new_game_setup_screen.py` | Production (set field) | T4.6 — same |
| `game/ui/screens/new_game_setup_ui_builder.py` | Production (refactor) | T4.7 — option (a) move ~400 LOC widget code into `build()`; option (b) remove builder facade |
| `tests/unit/ui/screens/test_<class>_*.py` | Tests (add) | Stage-1 purity test for T4.4; characterization tests for each placeholder where missing |
| `Projects/active_projects/PROJ-347/plan.md` | Project artifact | Updates per phase |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 1 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 | `pytest tests/unit/ui/screens/ -x -q` then `python Tools/lint_test_files.py` |
