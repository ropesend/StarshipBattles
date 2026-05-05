# Top 30 Functions by max_depth

Sorted by AST `max_depth` desc, then `total_loc` desc. **`visual_depth`** treats `elif` chains as flat (this is the human-readable depth). **`elif_run`** is the longest if/elif/.../elif run; high values here with high `max_depth` and low `visual_depth` indicate dispatch ladders, not nested logic.

| Rank | AST | Visual | elif_run | LOC | File | Function | Longest Ladder |
|-----:|----:|-------:|---------:|----:|------|----------|----------------|
| 1 | 15 | 3 | 14 | 72 | `game/ui/screens/strategy_detail_fmt.py` | `_format_orders` | `for->if->if->if->if->if->if->if->if->if->if->if->if->if->if` |
| 2 | 14 | 2 | 14 | 105 | `game/ui/screens/battle_setup/input_handler.py` | `BattleSetupInputHandler._handle_button` | `if->if->if->if->if->if->if->if->if->if->if->if->if->if` |
| 3 | 14 | 3 | 13 | 61 | `game/ui/screens/fleet_report_filters.py` | `sort_ships` | `def->if->if->if->if->if->if->if->if->if->if->if->if->if` |
| 4 | 14 | 2 | 13 | 40 | `game/ui/screens/strategy_event_router.py` | `StrategyEventRouter._handle_button_pressed` | `if->if->if->if->if->if->if->if->if->if->if->if->if->if` |
| 5 | 13 | 3 | 11 | 61 | `game/ui/screens/builder/layer_panel.py` | `LayerPanel.handle_item_action` | `if->if->if->if->if->if->if->if->if->if->if->for->if` |
| 6 | 13 | 2 | 13 | 43 | `game/ui/screens/fleet_report_filters.py` | `sort_ships.get_sort_key` | `if->if->if->if->if->if->if->if->if->if->if->if->if` |
| 7 | 13 | 1 | 13 | 34 | `game/ui/screens/strategy_event_router.py` | `StrategyEventRouter._handle_window_close` | `if->if->if->if->if->if->if->if->if->if->if->if->if` |
| 8 | 12 | 5 | 7 | 52 | `game/ui/screens/star_list_filters.py` | `sort_stars` | `if->if->if->if->if->if->if->def->if->if->for->if` |
| 9 | 12 | 1 | 12 | 52 | `game/ui/screens/strategy_ui_action_router.py` | `UIActionRouter.handle_ui_action` | `if->if->if->if->if->if->if->if->if->if->if->if` |
| 10 | 12 | 2 | 12 | 47 | `game/ui/screens/workshop_event_router.py` | `WorkshopEventRouter._handle_panel_action` | `if->if->if->if->if->if->if->if->if->if->if->with` |
| 11 | 12 | 1 | 12 | 35 | `game/ui/screens/workshop_event_router.py` | `WorkshopEventRouter._handle_button_pressed` | `if->if->if->if->if->if->if->if->if->if->if->if` |
| 12 | 10 | 4 | 6 | 90 | `game/ui/screens/builder/left_panel.py` | `BuilderLeftPanel.handle_event` | `if->if->if->if->if->if->if->if->if->if` |
| 13 | 10 | 3 | 8 | 86 | `game/ui/screens/strategy_fleet_command_router.py` | `FleetCommandRouter.handle_fleet_action` | `if->if->if->if->if->if->if->if->if->if` |
| 14 | 10 | 2 | 9 | 52 | `game/strategy/data/order_types.py` | `Order.to_dict` | `if->if->if->if->if->if->if->if->if->if` |
| 15 | 10 | 3 | 9 | 51 | `game/ui/screens/strategy_fleet_command_router.py` | `FleetCommandRouter.handle_detail_action` | `if->if->if->if->if->if->if->if->if->if` |
| 16 | 10 | 5 | 5 | 48 | `game/ui/screens/planet_list_filters.py` | `sort_planets` | `if->if->if->if->if->def->if->if->for->if` |
| 17 | 9 | 5 | 5 | 154 | `game/ui/screens/race_setup_screen.py` | `RaceSetupScreen.process_event` | `if->if->if->if->if->if->if->if->if` |
| 18 | 9 | 3 | 8 | 47 | `game/ui/screens/orders_window.py` | `OrdersWindow._get_order_description` | `if->if->if->if->if->if->if->if->if` |
| 19 | 9 | 2 | 9 | 25 | `game/ui/screens/strategy_input_handler.py` | `StrategyInputHandler._handle_button_press` | `if->if->if->if->if->if->if->if->if` |
| 20 | 9 | 1 | 9 | 24 | `game/ui/screens/battle_screen.py` | `BattleScreen._handle_keydown` | `if->if->if->if->if->if->if->if->if` |
| 21 | 8 | 6 | 3 | 114 | `game/simulation/entities/combat_endurance.py` | `calculate_combat_endurance` | `for->for->if->if->if->if->if->if` |
| 22 | 8 | 3 | 5 | 69 | `game/ui/screens/builder/modifier_row.py` | `ModifierControlRow.handle_event` | `if->if->if->if->if->if->if->if` |
| 23 | 8 | 4 | 5 | 42 | `game/ui/screens/builder/stat_rows_dynamic.py` | `_get_strategic_abilities` | `for->for->for->if->if->if->if->if` |
| 24 | 8 | 2 | 7 | 34 | `game/ui/screens/transfer_dialog.py` | `TransferDialog.process_event` | `if->if->if->if->if->if->if->if` |
| 25 | 7 | 7 | 1 | 175 | `game/ui/screens/builder/layer_panel.py` | `LayerPanel.rebuild` | `for->if->for->if->for->if->if` |
| 26 | 7 | 5 | 2 | 156 | `game/ui/screens/strategy_detail_fmt.py` | `format_planet_info` | `if->if->if->if->for->if->if` |
| 27 | 7 | 4 | 5 | 132 | `game/ui/screens/strategy_renderer.py` | `StrategyRenderer._draw_system_details` | `for->if->if->if->if->if->if` |
| 28 | 7 | 5 | 4 | 117 | `game/ui/renderer/game_renderer.py` | `draw_ship` | `if->if->for->if->if->if->if` |
| 29 | 7 | 4 | 5 | 108 | `game/ui/screens/strategy_click_dispatcher.py` | `ClickModeDispatcher._hit_test_planets` | `for->if->if->if->if->if->if` |
| 30 | 7 | 1 | 7 | 73 | `game/ui/screens/strategy_detail_formatter.py` | `StrategyDetailFormatter.show_detailed_report` | `if->if->if->if->if->if->if` |
