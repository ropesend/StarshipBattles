# PROJ-338 — Phase 1 Checklist

One section per file. Each test name is a behavior pin in the form
`test_<scenario>_<expected_observable>`.

---

## Section A — `test_build_queue_drag_handler.py` (NEW, ~28 tests)

### A.1 — Constructor + state defaults

- [ ] `test_constructor_initial_state_no_drag` — `is_dragging is False`, `dragged_item is None`, `selected_design is None`, `_pending_queue_index is None`, `drag_threshold == 10`.
- [ ] `test_constructor_with_remove_callback_stores_it` — `_on_remove_from_queue` set to provided callable.
- [ ] `test_constructor_without_remove_callback_defaults_to_none` — legacy fallback path enabled.

### A.2 — `handle_mouse_down` design-list path (happy + branch)

- [ ] `test_mouse_down_right_button_returns_false` — non-left-click ignored.
- [ ] `test_mouse_down_multi_select_active_returns_false_no_state_change` — multi-select gates everything.
- [ ] `test_mouse_down_on_design_button_starts_drag_with_portrait` — `dragged_item` populated, `selected_design` set, `on_refresh_design_report` called with design_id, returns True.
- [ ] `test_mouse_down_on_design_button_with_no_matching_design_skips_dragged_item` — `selected_design` set + report callback fires, but `dragged_item` stays None.
- [ ] `test_mouse_down_on_design_button_uses_48px_portrait_for_cursor` — `portrait_loader.load_design_portrait` called with `(design, 48)`.
- [ ] `test_mouse_down_no_collision_returns_false_no_state_change` — no design hit, no queue hit → returns False.

### A.3 — `handle_mouse_down` queue-row path

- [ ] `test_mouse_down_on_queue_row_sets_pending_index_no_drag_yet` — `_pending_queue_index = clicked_row`, `drag_start_pos = event.pos`, no `dragged_item` yet.

### A.4 — `handle_mouse_motion` threshold

- [ ] `test_motion_below_threshold_no_drag_started` — moving 5px → returns False, `dragged_item` still None.
- [ ] `test_motion_above_threshold_starts_drag_pops_via_callback_when_present` — moving 11px with `_on_remove_from_queue` set → callback fires with idx, `construction_queue` NOT mutated directly.
- [ ] `test_motion_above_threshold_legacy_pops_directly_when_no_callback` — without `_on_remove_from_queue` → `construction_queue.pop(idx)` happens.
- [ ] `test_motion_above_threshold_with_invalid_index_skips_pop` — `_pending_queue_index >= len(construction_queue)` → no pop, but pending state still cleared.
- [ ] `test_motion_multi_select_active_returns_false_no_drag_started` — gating.
- [ ] `test_motion_button_not_pressed_returns_false` — `event.buttons[0]` is False → no-op.
- [ ] `test_motion_clears_pending_state_after_drag_starts` — `_pending_queue_index` and `drag_start_pos` reset to None.
- [ ] `test_motion_dragged_item_carries_source_queue_marker` — `dragged_item['source'] == 'queue'`.

### A.5 — `handle_mouse_up` drop

- [ ] `test_mouse_up_right_button_returns_none_no_state_change`.
- [ ] `test_mouse_up_click_without_drag_returns_pending_index` — `_pending_queue_index` set, `dragged_item` None → returns the pending index, calls `on_refresh_queue`.
- [ ] `test_mouse_up_drop_inside_panel_calls_add_to_queue_with_calculated_index` — drop on panel → `on_add_to_queue(design_id, turns, category, insert_idx)` fires.
- [ ] `test_mouse_up_drop_inside_clamps_index_at_queue_length` — `estimated_idx > len(queue)` → clamped to `len(queue)`.
- [ ] `test_mouse_up_drop_inside_clamps_index_at_zero` — negative `rel_y` → 0.
- [ ] `test_mouse_up_drop_outside_panel_drops_item_silently_when_from_queue` — `came_from_queue True` → `on_refresh_queue` invoked, no add.
- [ ] `test_mouse_up_drop_outside_panel_no_refresh_when_from_design_list` — `came_from_queue False` → no refresh.
- [ ] `test_mouse_up_clears_dragged_item_state_after_drop`.
- [ ] `test_mouse_up_multi_select_clears_all_pending_state_returns_none` — gating + cleanup.

### A.6 — `draw_drag_preview`

- [ ] `test_draw_preview_no_drag_no_blits` — early return.
- [ ] `test_draw_preview_with_portrait_blits_shadow_and_icon_and_border` — 3 blit/draw calls observed.
- [ ] `test_draw_preview_without_portrait_uses_color_map_fallback_for_known_category` — ship/complex/satellite/fighter colour map applied.
- [ ] `test_draw_preview_unknown_category_falls_back_to_text_dim` — colour-map miss path.

---

## Section B — `test_build_queue_controller.py` extension (~15 tests)

### B.1 — `load_designs_by_category` + `set_role` / `set_category`

- [ ] `test_load_designs_filters_by_vehicle_type_complex` — only "Planetary Complex" returned.
- [ ] `test_load_designs_unknown_category_defaults_to_ship` — type_map fallback.
- [ ] `test_load_designs_filters_by_role_when_not_any` — role filter applied.
- [ ] `test_load_designs_role_none_string_matches_designs_with_no_role` — `"None"` special path.
- [ ] `test_set_category_resets_role_to_any_and_fires_callback`.
- [ ] `test_set_role_fires_callback_does_not_reset_category`.

### B.2 — `_validate_designs` paths

- [ ] `test_validate_designs_without_registries_marks_all_valid`.
- [ ] `test_validate_designs_with_load_failure_marks_invalid`.
- [ ] `test_validate_designs_with_validator_exception_assumes_valid` — broad-catch path.

### B.3 — `_calculate_build_turns` / `_get_design_cost`

- [ ] `test_calculate_build_turns_no_cost_returns_one`.
- [ ] `test_calculate_build_turns_no_rate_returns_one`.
- [ ] `test_calculate_build_turns_max_across_resources` — max-resource bottleneck.
- [ ] `test_calculate_build_turns_zero_floor_at_001`.
- [ ] `test_get_design_cost_load_failure_returns_empty_dict`.
- [ ] `test_get_design_cost_oserror_caught_returns_empty_dict` — broad-catch path.

### B.4 — `refresh_design_report`

- [ ] `test_refresh_design_report_load_failure_shows_placeholder`.
- [ ] `test_refresh_design_report_ship_load_returns_none_shows_placeholder`.
- [ ] `test_refresh_design_report_success_calls_update_design`.
- [ ] `test_refresh_design_report_exception_shows_placeholder`.

---

## Section C — `test_system_tree_panel_characterization.py` (NEW, ~22 tests)

### C.1 — `set_items` empty + single object branches

- [ ] `test_set_items_empty_contents_no_items_built`.
- [ ] `test_set_items_kills_previous_items_on_rebuild` — BUG-26 guard verifying `kill()` called on each old item.
- [ ] `test_set_items_single_planet_no_root_group` — `root_items` has the planet leaf directly.
- [ ] `test_set_items_single_star_no_stars_group` — root-level direct add.
- [ ] `test_set_items_single_warp_point_label_uses_destination_id`.

### C.2 — Grouping branches

- [ ] `test_set_items_multi_planet_creates_planetary_system_root_group_with_largest_name`.
- [ ] `test_set_items_multi_star_creates_stars_group_with_count`.
- [ ] `test_set_items_multi_warp_creates_warp_points_group_with_count`.
- [ ] `test_set_items_planet_stack_at_same_hex_creates_sector_group_with_count`.
- [ ] `test_set_items_planet_stack_sorted_by_mass_descending`.
- [ ] `test_set_items_flat_view_skips_planetary_system_grouping_and_sorts_by_mass`.

### C.3 — Effects

- [ ] `test_set_items_with_system_obj_calls_hazard_then_effects_path` — order matters.
- [ ] `test_set_items_with_system_obj_no_empire_skips_effects` — early-return on empire_id None.
- [ ] `test_set_items_flat_view_with_hex_coord_calls_sector_effects_path`.
- [ ] `test_add_effects_group_skips_when_empty`.
- [ ] `test_add_effects_group_single_provider_renders_inline_with_source_label`.
- [ ] `test_add_effects_group_multi_provider_creates_collapsible_subgroup`.
- [ ] `test_add_effects_group_uses_legacy_provider_label_when_source_label_missing`.

### C.4 — `on_click` toggling

- [ ] `test_on_click_group_expand_adds_to_expanded_groups_set`.
- [ ] `test_on_click_group_collapse_removes_from_expanded_groups_set`.
- [ ] `test_on_click_group_expand_recursively_expands_child_groups` — "Expand All" semantics.
- [ ] `test_on_click_leaf_with_obj_invokes_selection_callback`.
- [ ] `test_on_click_leaf_without_callback_silent_no_crash`.

### C.5 — `_format_effect_value` / `_format_provider_value`

- [ ] `test_format_effect_value_resource_harvest_booster_renders_pct`.
- [ ] `test_format_effect_value_quality_improvement_uses_per_provider_rate_not_aggregate`.
- [ ] `test_format_effect_value_shield_modifier_delegates_to_intrinsic_formatter`.
- [ ] `test_format_provider_value_unknown_ability_returns_empty_string`.

---

## Section D — `test_system_tree_panel_hazard.py` extension (~5 tests)

- [ ] `test_thrust_modifier_at_one_no_hint`.
- [ ] `test_multiple_star_providers_each_yield_a_hint`.
- [ ] `test_non_star_provider_ignored_even_if_shield_modifier_low`.
- [ ] `test_missing_ability_data_dict_treated_as_empty_no_hint`.
- [ ] `test_environmental_damage_zero_rate_no_hint`.

---

## Section E — `test_planet_report_panel_characterization.py` (NEW, ~20 tests)

### E.1 — Construction

- [ ] `test_construction_with_show_complexes_creates_complexes_container`.
- [ ] `test_construction_without_show_complexes_text_panel_takes_full_width`.
- [ ] `test_construction_loads_resource_icons_for_each_displayed_resource`.
- [ ] `test_construction_resource_icon_file_missing_falls_back_to_colored_square`.
- [ ] `test_construction_resource_with_no_filename_uses_gray_placeholder`.
- [ ] `test_construction_atmosphere_graph_height_floor_50px_when_rect_too_short`.

### E.2 — `update_planet`

- [ ] `test_update_planet_overwrites_view_unconditionally_with_new_value`.
- [ ] `test_update_planet_overwrites_view_unconditionally_with_none` — PROJ-289 explicit policy.
- [ ] `test_update_planet_empire_none_preserves_construction_time_value` — PROJ-292 m1 sentinel.
- [ ] `test_update_planet_empire_provided_overrides_construction_time_value`.
- [ ] `test_update_planet_race_registry_same_sentinel_semantics`.
- [ ] `test_update_planet_rebuilds_text_box_html`.

### E.3 — `_update_complexes_list`

- [ ] `test_complexes_list_no_facilities_renders_none_label`.
- [ ] `test_complexes_list_single_facility_renders_name_only_no_count_suffix`.
- [ ] `test_complexes_list_duplicate_design_id_renders_x_count_suffix`.
- [ ] `test_complexes_list_kills_previous_items_on_refresh` — BUG-26 guard.
- [ ] `test_complexes_list_disabled_when_show_complexes_false_returns_silently`.

### E.4 — `_build_resource_grid` / `_net_cell_color`

- [ ] `test_resource_grid_net_row_positive_paints_hp_healthy`.
- [ ] `test_resource_grid_net_row_negative_paints_hp_critical`.
- [ ] `test_resource_grid_net_row_zero_paints_text_light`.
- [ ] `test_resource_grid_text_colour_setter_attribute_error_swallowed_silently`.
- [ ] `test_resource_grid_scrollable_area_dimensions_match_layout_constants`.

### E.5 — `kill`

- [ ] `test_kill_clears_resource_grid_items_and_panel`.

---

## Section F — `test_battle_panels_characterization.py` (NEW, ~22 tests)

### F.1 — `BattlePanel._get_ships()` fallback

- [ ] `test_get_ships_returns_ui_service_list_when_available`.
- [ ] `test_get_ships_falls_back_to_scene_ships_when_ui_service_returns_non_list` — MagicMock auto-result guard.
- [ ] `test_get_ships_falls_back_when_ui_service_get_ships_raises_attributeerror`.
- [ ] `test_get_ships_falls_back_to_empty_list_when_scene_has_no_ships_attr`.

### F.2 — `ExpandableIdPanel`

- [ ] `test_toggle_id_expanded_adds_then_removes_on_repeat`.
- [ ] `test_is_id_expanded_after_toggle_returns_true_then_false`.

### F.3 — `ShipStatsPanel`

- [ ] `test_draw_records_banner_rect_per_ship_id_using_scroll_offset`.
- [ ] `test_draw_clears_banner_rects_each_frame` — fresh dict per draw.
- [ ] `test_draw_dead_ship_uses_text_dim_color_and_appends_dead_label`.
- [ ] `test_draw_derelict_ship_uses_status_derelict_color_and_appends_derelict_label`.
- [ ] `test_handle_click_within_banner_toggles_expansion`.
- [ ] `test_handle_click_with_shift_returns_focus_ship_tuple`.
- [ ] `test_handle_click_outside_any_banner_returns_false`.
- [ ] `test_handle_click_uses_scroll_offset_to_translate_screen_y`.

### F.4 — `SeekerMonitorPanel`

- [ ] `test_clear_inactive_keeps_active_drops_others`.
- [ ] `test_handle_click_on_clear_button_calls_clear_inactive_returns_true`.
- [ ] `test_handle_click_on_x_button_for_inactive_seeker_removes_from_tracking`.
- [ ] `test_handle_click_on_x_button_for_active_seeker_does_not_remove`.
- [ ] `test_handle_click_on_seeker_row_toggles_expansion`.

### F.5 — `BattleControlPanel`

- [ ] `test_draw_battle_over_team0_alive_renders_team1_wins_text`.
- [ ] `test_draw_battle_over_team1_alive_renders_team2_wins_text`.
- [ ] `test_draw_battle_over_no_alive_renders_draw_text`.
- [ ] `test_draw_battle_ongoing_sets_end_battle_early_rect_not_battle_end_rect`.
- [ ] `test_handle_click_on_battle_end_button_returns_end_battle`.
- [ ] `test_handle_click_on_end_battle_early_button_returns_end_battle`.
- [ ] `test_handle_click_outside_buttons_returns_false`.
