# PROJ-392 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/simulation/entities/ship_stats.py` | Production | Edit | LEG-01-001 — delete `_priority_sort_key` (lines 503-505); 0 call sites |
| `game/ui/screens/race_setup/screen.py` | Production | Edit | LEG-02-007 — delete `name_input = None` placeholder at line 261; 0 readers |
| `game/ui/panels/battle_panels.py` | Production | Edit | LEG-03-025 — delete `expanded_ships` alias at line 92; 0 readers |
| `game/ui/screens/strategy_renderer.py` | Production | Edit | LEG-01-006 — inline 3 image-load wrappers (lines 217-245) |
| `game/strategy/quickstart_builder.py` | Production | Edit | LEG-01-007 — inline 2 dir wrappers (lines 39-45) |
| `game/strategy/services/galaxy_pathfinding_service.py` | Production | Edit | LEG-01-009 — inline `find_path_deep_space` static at lines 61-64 |
| `game/strategy/data/pathfinding.py` | Production | Edit | LEG-01-009 — possibly migrate the line-44 call site |
| `game/simulation/entities/stat_contributors/command.py` | Production | Edit | LEG-01-010 — delete `priority_sort_key` wrapper (lines 36-38) |
| `tests/.../test_command.py` | Test | Edit | LEG-01-010 — update to `lookup_crew_priority` |
| `game/app.py` | Production | Edit | LEG-02-015 — rename `_menu_scene` → `menu_scene` (lines 233-234, 449) |
| `game/assets/asset_manager.py` | Production | Edit | LEG-03-010 — delete `get_asset_manager` alias at line 348 |
| `game/ui/screens/empire_build_queue_window.py` | Production | Edit | LEG-03-014 — inline `_get_sector_text` at line 589 |
| `game/ui/screens/builder/stat_getters.py` | Production | Edit | LEG-03-016 — rename `_get_total_crew_requirement` → public, drop `get_crew_required` (line 66) |
| `game/ui/screens/new_game_setup_screen.py` | Production | Edit | LEG-04-006 — delete 2 static wrappers (lines 701-720) |
