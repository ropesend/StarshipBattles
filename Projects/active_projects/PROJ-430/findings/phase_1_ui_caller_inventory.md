# Phase 1 — UI Caller Inventory (PROJ-430 Phase 3 input)

Generated 2026-05-17 by `rg -l "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui`.

**Actual count: 16 files** (TD-08 plan / scaffold cited 25 — the difference probably reflects pre-PROJ-411 churn or counting individual call-sites rather than files). Re-confirmed against a fresh `rg`; 42 individual call-sites across these 16 files.

## File list

1. `game/ui/panels/planet_report_panel.py`
2. `game/ui/screens/build_queue_panel_factory.py`
3. `game/ui/screens/build_queue_screen.py`
4. `game/ui/screens/empire_build_queue_window.py`
5. `game/ui/screens/event_log_window.py`
6. `game/ui/screens/planet_list_controller.py`
7. `game/ui/screens/planet_selection_window.py`
8. `game/ui/screens/strategy_build_queue_manager.py`
9. `game/ui/screens/strategy_colonization.py`
10. `game/ui/screens/strategy_detail_formatter.py`
11. `game/ui/screens/strategy_fleet_ops.py`
12. `game/ui/screens/strategy_game_state_manager.py`
13. `game/ui/screens/transfer_controller.py`
14. `game/ui/screens/strategy_windows/empire_panel_ctrl.py`
15. `game/ui/screens/strategy_windows/event_log_window_ctrl.py`
16. `game/ui/screens/strategy_windows/list_windows.py`

## Batching plan

Phase 3 executes in one mechanical sweep (single commit). All 16 files use the same rename mapping documented in `manifest.md` § "UI callers". No file should require behavior change beyond text substitution.
