# PROJ-481 — Verification Report

**Source audit:** `Reviews/results/2026-05-20_210540_type-audit/`
**Independent re-verification:** 2026-05-22
**This bundle:** UI per-finding

## Batch summary
~79 verified / 0 rejected / 0 uncertain (resolved) / 0 out-of-scope, out of ~79 UI candidates.

The audit's own verifier reported 0/5 CRITICAL and 0/5 MAJOR spot-check false positives. The third-pass skeptical verifier opened 43 of 49 UI items personally and spot-checked the remaining 6 (`TYP-01-045/046/047/048/049/050`) live — all confirmed (two with line numbers that drifted since the audit: `fleet_report_window.process_event` 248 → 277; `_get_role_filter_options` 388 → 396).

## Verified

### CRITICAL (1)

| id | file:line | symbol | current | suggested |
|----|-----------|--------|---------|-----------|
| TYP-01-051 | strategy_modal_window.py:273 | `check_clicked_inside_or_blocking` | (missing) | `bool` |

### MAJOR (~40)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| TYP-01-011 | planet_list_filters.py:38 | gather_planets | list[Planet] |
| TYP-01-012 | planet_list_filters.py:174 | filter_planets | list[Planet] |
| TYP-01-013 | planet_list_filters.py:215 | sort_planets | list[Planet] |
| TYP-01-014 | planet_list_filters.py:252 | get_column_value | str |
| TYP-01-015 | planet_list_filters.py:280 | compute_planet_ranges | dict[str, tuple[float, float]] |
| TYP-01-016 | planet_list_filters.py:333 | get_system_name | str |
| TYP-01-017 | planet_list_filters.py:348 | get_owner_name | str |
| TYP-01-018 | planet_list_window.py:211,221,231,241 | filter_types/owner/effects/ranges | typed dicts |
| TYP-01-020 | star_list_filters.py:20 | gather_stars | list[Star] |
| TYP-01-021 | star_list_filters.py:67 | filter_stars | list[Star] |
| TYP-01-022 | star_list_filters.py:121 | sort_stars | list[Star] |
| TYP-01-023 | star_list_filters.py:163 | compute_star_ranges | dict[str, tuple[float, float]] |
| TYP-01-024 | star_list_filters.py:203 | get_system_name | str |
| TYP-01-025 | star_list_filters.py:217 | get_star_type_display | str |
| TYP-01-026 | star_list_window.py:277,285 | filter_types/ranges | typed dicts |
| TYP-01-028 | setup_data_io.py:34 | get_base_path | str |
| TYP-01-029 | setup_data_io.py:39 | scan_ship_designs | list[dict[str, Any]] |
| TYP-01-030 | setup_data_io.py:65 | load_ships_from_entries | list[Ship] |
| TYP-01-031 | setup_data_io.py:171 | load_battle_setup | tuple[list[dict[str, Any]], list[dict[str, Any]]] \| tuple[None, None] |
| TYP-01-033 | setup_renderer.py:35 | draw_available_ships | int |
| TYP-01-034 | setup_screen.py:133 | get_team_display_groups | list[dict[str, str \| int]] |
| TYP-01-050 | design_selector_window.py:396 | _get_role_filter_options | list[str] (line drifted) |
| Shard03 | strategy_renderer.py:115 | _get_font | pygame.Font |
| Shard03 | strategy_renderer.py:121-157 | 10 delegation properties | concrete types via TYPE_CHECKING |
| Shard03 | strategy_screen.py | 12 delegation properties | concrete types via TYPE_CHECKING |
| Shard03 | strategy_superweapons.py:73-85 | 4 properties | concrete types |
| Shard03 | strategy_fleet_ops.py:61-69 | 3 properties | concrete types |
| TYP-04-004 | battle_screen.py:172 | engine | BattleEngine |
| TYP-04-005 | battle_screen.py:199 | show_overlay | bool |
| TYP-04-006 | battle_screen.py:207 | stats_panel_width | int |
| TYP-04-007 | battle_screen.py:211 | ships | list[Ship] |
| TYP-04-008 | battle_screen.py:215 | projectiles | list[Projectile] |
| TYP-04-009 | battle_screen.py:219 | ai_controllers | list[AIController] |
| TYP-04-010 | battle_screen.py:481 | is_battle_over | bool |
| TYP-04-011 | battle_screen.py:485 | get_winner | int |
| TYP-04-012 | workshop_viewmodel.py:407 | validate_design | DesignResult |
| MAJOR-02-02 | workshop_viewmodel_ship_ops.py:207 | validate_design | ValidationResult \| None |
| MAJOR-02-03 | builder/weapons_viewmodel.py:110,392 | hovered_weapon, calc_damage_at_range | Component \| None / float |
| TYP-04-013 | builder/left_panel.py:453 | get_add_count | int |
| TYP-04-014 | builder/modifier_logic.py:150 | calculate_snap_value | float |
| TYP-04-015 | test_lab/component_dropdown.py:101 | get_selected_component_id | str \| None |
| TYP-04-016 | test_lab/test_executor.py:175 | run_headless | bool |

### MINOR (~38)

| id | file:line | symbol | suggested |
|----|-----------|--------|-----------|
| TYP-01-019 | planet_list_window.py:292 | _capture_current_state | dict[str, Any] |
| TYP-01-027 | star_list_window.py:448 | _capture_current_state | dict[str, Any] |
| TYP-01-038 | strategy_click_dispatcher.py:53 | scene | StrategyScreen (TYPE_CHECKING) |
| TYP-01-039 | strategy_click_dispatcher.py:517 | _resolve_click_target | HexCoord |
| TYP-01-040 | strategy_colonization.py:40,44,48 | systems, camera, hex_size | concrete |
| TYP-01-041 | strategy_colonization.py:224 | request_colonize_order | dict[str, Any] \| None |
| TYP-01-042 | strategy_colonization.py:246,259 | _get_system_at_hex, _resolve_planet_global_hex | StarSystem \| None / HexCoord \| None |
| TYP-01-043 | strategy_event_router.py:336 | resolve_race (nested) | RaceConfig \| None |
| TYP-01-044 | strategy_event_router.py:363 | _get_race_config | RaceConfig \| None |
| TYP-01-045 | battle_setup/controller.py:411 | _build_end_condition | IEndCondition |
| TYP-01-046 | strategy_render/dyson_spheres.py:116 | load_dyson_sphere_image | pygame.Surface \| None |
| TYP-01-047 | test_lab/ship_panels.py:183 | get_selected_ship_info | dict \| None |
| TYP-01-048 | build_queue_list_window.py:210 | process_event | bool |
| TYP-01-049 | fleet_report_window.py:277 | process_event | bool (line drifted from 248) |
| TYP-04-025 | battle_results_screen.py:34 | _hp_color | tuple[int, int, int] |
| TYP-04-026 | fleet_report_filters.py:274 | get_sort_key | int \| float \| str |
| TYP-04-027 | strategy_camera_nav.py:40,44,48 | camera, systems, hex_size | concrete |
| TYP-04-028 | strategy_camera_nav.py:79 | _resolve_global_hex | HexCoord \| None |
| TYP-04-029 | strategy_camera_nav.py:204 | cycle_selection | Colony \| Fleet \| None |
| TYP-04-031 | transfer_view_model.py:105,122,148 | apply_arrow, apply_max, get_pending | float \| int |
| TYP-04-032 | workshop_screen.py:369-398 | 5 delegation properties | concrete types |
| TYP-04-033 | workshop_screen.py:193 | _get_vehicle_classes | dict[str, Any] |
| TYP-04-034 | workshop_screen.py:578 | _get_button_definitions | list[tuple[str, str, int]] |
| TYP-04-035 | builder/modifier_row.py:129 | build_ui | int |
| TYP-04-036 | galaxy_test/galaxy_mode.py:63 | create_ui | list |
| TYP-04-037 | test_lab/test_run_card.py:61 | get_height | int |
| Shard03 | strategy_fleet_ops.py:88,172 | handle_move/join_designation | dict \| None |
| Shard03 | strategy_superweapons.py:362,369 | _get_system_at_hex, _get_warp_point_at_hex | StarSystem/WarpPoint \| None |
| Shard03 | workshop_event_router.py:44 | _get_vehicle_classes | VehicleClassRegistry \| None |
| Shard03 | species_selector_mixin.py:147 | _get_active_race_config | RaceConfig \| None |
| Shard03 | battle_ui.py:87 | handle_click | bool |
| Shard03 | builder_selection.py:21,114 | normalize_selection, get_primary_selection | list[tuple] / tuple \| None |
| Shard03 | strategy_input_handler.py:158 | handle_click | bool |
| MINOR-02-01 | pygame_gui_patch.py:90 | _to_tuple | tuple \| None |
| Shard02 | transfer_mass_preview.py:189 | _get_catalog | ResourceCatalog |
| Shard03-MR | strategy_game_state_manager.py:166 | _iter_snapshot_windows | Iterator[Any] |
| Shard03-MR | test_lab/details/validation.py:39 | _phase_color | tuple[int, int, int] |
| TYP-04-MR-006 | atmosphere_target_editor.py:223 | _button_handlers | dict[UIButton, Callable[[], None]] |
| Shard03-MR | radiation_shield_editor.py:176 | _button_handlers | same |
| Shard02 | gravity_target_editor.py:164 | _button_handlers | same (verify not false-positive) |
| Shard02 | water_target_editor.py:173 | _button_handlers | same (verify not false-positive) |
| TYP-04-MR-007 | workshop_ship_io.py:67 | _design_catalog | DesignCatalog \| None |
| TYP-04-MR-008 | workshop_viewmodel.py:129 | _with_ship | Any (template-method; user opted to include) |
| TYP-01-059 | defeat_dialog.py:83 | `# type: ignore[assignment]` | declare `_dismiss_button: Optional[UIButton]` |
| (cross-shard) | turn_failed_dialog.py:99 | identical pattern | same fix |
| Shard03 | ship_theme_manager.py:254 | `# type: ignore[index]` | narrow `expected` parameter |

## Rejected
None. (Per protocol footnote: zero rejections is suspicious vs. reassuring — flagged in `decisions.md`. Audit verifier's prior of "0 false positives across 5 CRITICAL + 5 MAJOR spot-checks" plus the third-pass spot-checks held up; all reviewed items were source-accurate.)

## Uncertain (resolved)
None remaining in UI bundle. All UNCERTAIN UI items were resolved during Phase D Step 3 by quick spot-check (6 items → all VERIFIED) and user decisions.

## Out of Scope
- `builder/stat_getters.py` 47 `-> Any` functions — INFO/data-driven JSON dispatch (decision recorded in `decisions.md`)
- pygame_gui boundary `-> Any` callbacks (`process_event` overrides etc. where the upstream contract is `Any`)
- All justified `# type: ignore` sites in UI (e.g. `pygame_gui_patch.py:152` upstream-private; `panels/race_theme_gallery.py:118` intentional override; `panels/ship_detail_panel.py:593,594` test introspection)
