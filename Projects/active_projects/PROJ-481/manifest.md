# PROJ-481 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/ui/screens/strategy_modal_window.py | Production | Phase 1: add `-> bool` to `check_clicked_inside_or_blocking` |
| game/ui/screens/planet_list_filters.py | Production | Phase 2: 7 `-> Any` narrowings |
| game/ui/screens/planet_list_window.py | Production | Phase 2: 4 properties; Phase 3: `_capture_current_state` |
| game/ui/screens/star_list_filters.py | Production | Phase 2: 6 `-> Any` narrowings |
| game/ui/screens/star_list_window.py | Production | Phase 2: 2 properties; Phase 3: `_capture_current_state` |
| game/ui/screens/setup_data_io.py | Production | Phase 2: 4 `-> Any` narrowings |
| game/ui/screens/setup_renderer.py | Production | Phase 2: `draw_available_ships` |
| game/ui/screens/setup_screen.py | Production | Phase 2: `get_team_display_groups` |
| game/ui/screens/strategy_renderer.py | Production | Phase 2: 11 delegation properties + `_get_font` |
| game/ui/screens/strategy_screen.py | Production | Phase 2: 12 delegation properties |
| game/ui/screens/strategy_superweapons.py | Production | Phase 2: 4 properties; Phase 3: 2 `_get_*_at_hex` helpers |
| game/ui/screens/strategy_fleet_ops.py | Production | Phase 2: 3 properties; Phase 3: 2 handlers |
| game/ui/screens/battle_screen.py | Production | Phase 2: 8 property/method narrowings |
| game/ui/screens/workshop_viewmodel.py | Production | Phase 2: `validate_design`; Phase 3: `_with_ship` |
| game/ui/screens/workshop_viewmodel_ship_ops.py | Production | Phase 2: `validate_design` |
| game/ui/screens/builder/weapons_viewmodel.py | Production | Phase 2: `hovered_weapon` + `calc_damage_at_range` |
| game/ui/screens/builder/left_panel.py | Production | Phase 2: `get_add_count` |
| game/ui/screens/builder/modifier_logic.py | Production | Phase 2: `calculate_snap_value` |
| game/ui/screens/test_lab/component_dropdown.py | Production | Phase 2: `get_selected_component_id` |
| game/ui/screens/test_lab/test_executor.py | Production | Phase 2: `run_headless` |
| game/ui/screens/design_selector_window.py | Production | Phase 2: `_get_role_filter_options` (line 396) |
| game/ui/screens/strategy_render/dyson_spheres.py | Production | Phase 2: `load_dyson_sphere_image` |
| game/ui/screens/battle_setup/controller.py | Production | Phase 2: `_build_end_condition` |
| game/ui/screens/strategy_click_dispatcher.py | Production | Phase 3: `scene`, `_resolve_click_target` |
| game/ui/screens/strategy_colonization.py | Production | Phase 3: 3 properties + 3 helpers |
| game/ui/screens/strategy_event_router.py | Production | Phase 3: `resolve_race` + `_get_race_config` |
| game/ui/screens/strategy_camera_nav.py | Production | Phase 3: 3 properties + `_resolve_global_hex` + `cycle_selection` |
| game/ui/screens/workshop_screen.py | Production | Phase 3: 5 properties + `_get_vehicle_classes` + `_get_button_definitions` |
| game/ui/screens/workshop_ship_io.py | Production | Phase 3: `_design_catalog` |
| game/ui/screens/workshop_event_router.py | Production | Phase 3: `_get_vehicle_classes` |
| game/ui/screens/builder/modifier_row.py | Production | Phase 3: `build_ui` |
| game/ui/screens/galaxy_test/galaxy_mode.py | Production | Phase 3: `create_ui` |
| game/ui/screens/test_lab/test_run_card.py | Production | Phase 3: `get_height` |
| game/ui/screens/battle_results_screen.py | Production | Phase 3: `_hp_color` |
| game/ui/screens/fleet_report_filters.py | Production | Phase 3: `get_sort_key` inner |
| game/ui/screens/fleet_report_window.py | Production | Phase 3: `process_event` (line 277) |
| game/ui/screens/battle_ui.py | Production | Phase 3: `handle_click` |
| game/ui/screens/builder_selection.py | Production | Phase 3: `normalize_selection` + `get_primary_selection` |
| game/ui/screens/strategy_input_handler.py | Production | Phase 3: `handle_click` |
| game/ui/screens/species_selector_mixin.py | Production | Phase 3: `_get_active_race_config` |
| game/ui/screens/test_lab/ship_panels.py | Production | Phase 3: `get_selected_ship_info` |
| game/ui/screens/transfer_view_model.py | Production | Phase 3: `apply_arrow`, `apply_max`, `get_pending` |
| game/ui/screens/transfer_mass_preview.py | Production | Phase 3: `_get_catalog` |
| game/ui/screens/build_queue_list_window.py | Production | Phase 3: `process_event` |
| game/ui/screens/atmosphere_target_editor.py | Production | Phase 3: `_button_handlers` |
| game/ui/screens/radiation_shield_editor.py | Production | Phase 3: `_button_handlers` |
| game/ui/screens/gravity_target_editor.py | Production | Phase 3: `_button_handlers` (verify not false positive first) |
| game/ui/screens/water_target_editor.py | Production | Phase 3: `_button_handlers` (verify not false positive first) |
| game/ui/screens/strategy_game_state_manager.py | Production | Phase 3: `_iter_snapshot_windows` |
| game/ui/screens/test_lab/details/validation.py | Production | Phase 3: `_phase_color` |
| game/ui/pygame_gui_patch.py | Production | Phase 3: `_to_tuple` |
| game/ui/screens/defeat_dialog.py | Production | Phase 3: declare `_dismiss_button: Optional[UIButton]`, remove `# type: ignore` |
| game/ui/screens/turn_failed_dialog.py | Production | Phase 3: same cross-shard fix |
| game/ui/assets/ship_theme_manager.py | Production | Phase 3: narrow `expected` param, remove `# type: ignore[index]` |
