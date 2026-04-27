# Top 30 Functions by Visual Depth

Sorted by `visual_depth` descending. This metric ignores elif-chain artifacts and reflects how a human reads the code's indentation.

| Rank | Visual | AST | elif_run | LOC | File | Function | Longest Ladder |
|-----:|-------:|----:|---------:|----:|------|----------|----------------|
| 1 | 7 | 7 | 1 | 175 | `game/ui/screens/builder/layer_panel.py` | `LayerPanel.rebuild` | `for->if->for->if->for->if->if` |
| 2 | 7 | 7 | 1 | 24 | `game/ui/screens/builder/stat_rows_dynamic.py` | `get_planetary_engineering_rows` | `for->for->if->if->def->for->if` |
| 3 | 6 | 6 | 3 | 122 | `game/strategy/services/system_effects_collector.py` | `_collect_effects` | `for->for->for->for->for->if` |
| 4 | 6 | 8 | 3 | 114 | `game/simulation/entities/combat_endurance.py` | `calculate_combat_endurance` | `for->for->if->if->if->if->if->if` |
| 5 | 6 | 6 | 2 | 86 | `game/ui/components/table/virtual_table.py` | `VirtualTable.update_visible_rows` | `for->if->for->if->if->if` |
| 6 | 6 | 6 | 1 | 69 | `game/strategy/engine/planet_energy_engine.py` | `PlanetEnergyEngine._process_planet` | `if->for->for->if->for->if` |
| 7 | 6 | 6 | 1 | 60 | `game/ui/screens/builder_selection.py` | `process_selection_change` | `if->if->if->for->if->if` |
| 8 | 6 | 6 | 1 | 56 | `game/strategy/quickstart_builder.py` | `QuickstartBuilder.copy_quickstart_designs` | `for->for->try->if->if->if` |
| 9 | 6 | 6 | 2 | 41 | `game/strategy/data/build_queue_source.py` | `colony_has_planetary_yard` | `for->for->if->if->if->if` |
| 10 | 6 | 6 | 1 | 34 | `game/ui/screens/builder/stat_rows_dynamic.py` | `get_planetary_defense_rows` | `for->for->if->def->for->if` |
| 11 | 6 | 6 | 1 | 34 | `game/ui/screens/builder/stat_rows_dynamic.py` | `get_strategic_modifier_rows` | `for->for->if->def->for->if` |
| 12 | 6 | 6 | 1 | 33 | `game/strategy/data/build_queue_source.py` | `_get_planetary_yard_size_multiplier` | `for->for->if->if->if->if` |
| 13 | 6 | 6 | 1 | 14 | `game/ui/screens/builder/stat_rows_dynamic.py` | `_get_constant_consumption` | `try->for->for->for->if->if` |
| 14 | 5 | 5 | 2 | 232 | `game/ui/panels/system_tree_panel.py` | `SystemTreePanel.set_items` | `if->def->for->if->for` |
| 15 | 5 | 7 | 2 | 156 | `game/ui/screens/strategy_detail_fmt.py` | `format_planet_info` | `if->if->if->if->for->if->if` |
| 16 | 5 | 9 | 5 | 154 | `game/ui/screens/race_setup_screen.py` | `RaceSetupScreen.process_event` | `if->if->if->if->if->if->if->if->if` |
| 17 | 5 | 5 | 1 | 124 | `game/strategy/engine/game_session.py` | `GameSession.from_dict` | `for->for->for->if->if` |
| 18 | 5 | 7 | 4 | 117 | `game/ui/renderer/game_renderer.py` | `draw_ship` | `if->if->for->if->if->if->if` |
| 19 | 5 | 5 | 1 | 115 | `game/strategy/services/combat_modifier_collector.py` | `collect_combat_modifiers` | `if->for->for->for->if` |
| 20 | 5 | 5 | 1 | 107 | `game/ui/panels/planet_report_panel.py` | `PlanetReportPanel._build_resource_grid` | `for->for->if->if->try` |
| 21 | 5 | 5 | 1 | 99 | `game/simulation/battle_state.py` | `ShipState.to_ship` | `for->for->if->for->if` |
| 22 | 5 | 5 | 1 | 92 | `game/ui/screens/planet_list_presets.py` | `apply_planet_list_state` | `if->if->for->if->if` |
| 23 | 5 | 6 | 2 | 84 | `game/engine/collision.py` | `CollisionSystem.process_beam_attack` | `if->if->if->if->if->if` |
| 24 | 5 | 5 | 1 | 82 | `game/ui/screens/test_lab/renderer.py` | `TestLabRenderer._is_condition_verified` | `if->try->if->for->if` |
| 25 | 5 | 5 | 1 | 66 | `game/ui/screens/planet_selection_window.py` | `PlanetSelectionWindow.update` | `if->if->if->if->if` |
| 26 | 5 | 6 | 2 | 65 | `game/ui/screens/builder/layer_panel.py` | `LayerPanel.get_range_selection` | `for->if->if->for->for->if` |
| 27 | 5 | 5 | 1 | 65 | `game/ui/screens/strategy_colonization.py` | `ColonizationSystem.on_colonize_click` | `if->if->if->for->if` |
| 28 | 5 | 5 | 1 | 64 | `game/ui/screens/strategy_renderer.py` | `StrategyRenderer._draw_fleets` | `for->for->if->if->if` |
| 29 | 5 | 5 | 1 | 58 | `game/ui/screens/strategy_renderer.py` | `StrategyRenderer._draw_warp_lanes` | `for->for->if->if->if` |
| 30 | 5 | 5 | 1 | 56 | `game/simulation/entities/ship_layer_manager.py` | `ShipLayerManager.change_class` | `if->for->if->for->if` |
