# PROJ-228: UI Structural Patterns — File Manifest

## Production Files

### Scroll Infrastructure (Phase 1)
- `game/ui/screens/test_lab/test_run_details.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/test_lab/results_panel.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/test_lab/screen_input_handler.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/test_lab/dialogs.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/test_lab/json_viewer.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/test_lab/renderer.py` — scroll_offset
- `game/ui/screens/test_lab/viewmodel.py` — scroll_offset
- `game/ui/screens/setup_screen.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/battle_screen.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/battle_state_viewer.py` — scroll_offset
- `game/ui/screens/builder/weapons_panel.py` — scroll_offset + MOUSEWHEEL
- `game/ui/screens/formation_editor.py` — MOUSEWHEEL
- `game/ui/screens/strategy_input_handler.py` — MOUSEWHEEL
- `game/ui/screens/planet_list_window.py` — MOUSEWHEEL
- `game/ui/screens/galaxy_test/screen.py` — MOUSEWHEEL
- `game/ui/screens/empire_build_queue_window.py` — MOUSEWHEEL
- `game/ui/panels/modifier_impact_grid.py` — scroll_offset + MOUSEWHEEL
- `game/ui/panels/battle_panels.py` — scroll_offset
- `game/ui/widgets/scrollable_json_panel.py` — scroll_offset + MOUSEWHEEL
- `game/ui/renderer/camera.py` — MOUSEWHEEL
- `game/ui/research/research_scene.py` — MOUSEWHEEL

### Scene Classes (Phase 2 — DUP-PAT-005)
- `game/ui/screens/menu_scene.py` — IScene implementor
- `game/ui/screens/keybindings_scene.py` — IScene implementor
- `game/ui/screens/test_lab/screen.py` — IScene implementor
- `game/ui/screens/strategy_screen.py` — IScene implementor
- `game/ui/screens/strategy_input_handler.py` — IScene implementor
- `game/ui/screens/setup_screen.py` — IScene implementor
- `game/ui/screens/workshop_screen.py` — IScene implementor
- `game/ui/screens/battle_screen.py` — IScene implementor
- `game/ui/research/research_scene.py` — IScene implementor
- `game/core/protocols.py` — IScene protocol definition

### UIWindow Subclasses (Phase 2 — DUP-PAT-006/007)
- `game/ui/screens/fleet_selection_window.py` — UIWindow subclass
- `game/ui/screens/planet_selection_window.py` — UIWindow subclass
- `game/ui/screens/system_selection_window.py` — UIWindow subclass
- `game/ui/screens/design_selector_window.py` — UIWindow subclass
- `game/ui/screens/fleet_report_window.py` — UIWindow subclass
- `game/ui/screens/fleet_orders_window.py` — UIWindow subclass (pygame_gui.elements.UIWindow)
- `game/ui/screens/event_log_window.py` — UIWindow subclass
- `game/ui/screens/empire_build_queue_window.py` — UIWindow subclass
- `game/ui/screens/empire_panel_window.py` — UIWindow subclass
- `game/ui/screens/planet_list_window.py` — UIWindow subclass
- `game/ui/screens/build_queue_list_window.py` — UIWindow subclass
- `game/ui/screens/save_selection_window.py` — UIWindow subclass (pygame_gui.elements.UIWindow)
- `game/ui/screens/transfer_dialog.py` — UIWindow subclass
- `game/ui/screens/cargo_quick_dialog.py` — UIWindow subclass
- `game/ui/screens/race_browser_dialog.py` — UIWindow subclass
- `game/ui/screens/new_game_setup_screen.py` — UIWindow subclass
- `game/ui/screens/race_setup_screen.py` — UIWindow subclass
- `game/ui/screens/strategy_window_manager.py` — manages windows

### Sidebar Pattern (Phase 3)
- `game/ui/screens/fleet_report_sidebar.py`
- `game/ui/screens/fleet_report_view_model.py`
- `game/ui/screens/event_log_sidebar.py`
- `game/ui/screens/empire_build_queue_sidebar.py`
- `game/ui/screens/empire_build_queue_filter_manager.py`
- `game/ui/screens/planet_list_sidebar.py`
- `game/ui/screens/strategy_panel_manager.py`
- `game/ui/screens/strategy_event_router.py`
- `game/ui/screens/strategy_ui.py`
- `game/ui/research/research_controls.py`

### Column/Toggle (Phase 3)
- `game/ui/components/table/column_manager.py`
- `game/ui/components/table/header.py`
- `game/ui/components/filters/tri_state_widget.py`

### VirtualTable & Data Sources (Phase 4)
- `game/ui/components/table/virtual_table.py`
- `game/ui/components/table/data_source.py`
- `game/ui/components/table/__init__.py`
- `game/ui/screens/planet_data_source.py`
- `game/ui/screens/fleet_data_source.py`
- `game/ui/screens/event_log_data_source.py`
- `game/ui/screens/empire_build_queue_data_source.py`
- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/build_queue_renderer.py`
- `game/ui/screens/build_queue_queue_data_source.py`
- `game/ui/screens/build_queue_panel_factory.py`

### Panel Pattern (Phase 5)
- `game/ui/screens/test_lab/ship_panels.py`
- `game/ui/screens/test_lab/results_panel.py`
- `game/ui/screens/test_lab/panel_manager.py`
- `game/ui/screens/test_lab/test_run_details.py`
- `game/ui/screens/builder/detail_panel.py`

### Serializable Protocol (Phase 6)
- `game/simulation/interfaces/entity_protocols.py`
- `game/simulation/interfaces/__init__.py`
- `game/simulation/battle_state.py`

## Test Files

### UI Screen Tests
- `tests/unit/ui/screens/test_fleet_report_window.py`
- `tests/unit/ui/screens/test_fleet_report_window_multi_select.py`
- `tests/unit/ui/screens/test_event_log_window.py`
- `tests/unit/ui/screens/test_empire_build_queue_window.py`
- `tests/unit/ui/screens/test_build_queue_list_window.py`
- `tests/unit/ui/screens/test_design_selector_window.py`
- `tests/unit/ui/screens/test_planet_selection_window.py`
- `tests/unit/ui/screens/test_system_selection_window.py`
- `tests/unit/ui/screens/test_strategy_window_manager.py`
- `tests/unit/ui/screens/test_sub_window_hotkeys.py`
- `tests/unit/ui/screens/test_fleet_orders_refresh.py`
- `tests/unit/ui/screens/test_cargo_quick_dialog.py`
- `tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py`
- `tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py`

### UI Scene Tests
- `tests/unit/ui/screens/test_keybindings_scene.py`
- `tests/unit/ui/screens/test_menu_scene.py`
- `tests/unit/ui/test_scene_protocol.py`
- `tests/unit/research/test_research_scene_di.py`
- `tests/integration/strategy/test_strategy_scene.py`

### VirtualTable & Data Source Tests
- `tests/unit/ui/components/table/test_virtual_table.py`
- `tests/unit/ui/components/table/test_data_source.py`
- `tests/unit/ui/screens/test_planet_data_source.py`
- `tests/unit/ui/screens/test_fleet_data_source.py`
- `tests/unit/ui/screens/test_event_log_data_source.py`
- `tests/unit/ui/screens/test_build_queue_data_source.py`
- `tests/unit/ui/screens/test_build_queue_queue_data_source.py`

### Other UI Tests
- `tests/unit/ui/screens/test_planet_production_display.py`
- `tests/unit/ui/panels/test_compute_planet_production.py`
- `tests/unit/test_lab/test_viewmodel.py`
- `tests/integration/ui/test_planet_list_window.py`
- `tests/integration/ui/test_build_queue_drag_drop.py`
- `tests/integration/ui/build_queue_screen/test_queue_selector.py`
- `tests/integration/ui/build_queue_screen/test_basics.py`
- `tests/repro_issues/test_bug_15_screenshot_strategy.py`
