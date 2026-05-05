# PROJ-340 — Phase 1 Checklist

Per-file behaviors-to-pin. Tick each box as the corresponding test lands
green. Master-plan target: 40–60 tests; this plan totals **45**.

---

## File: `battle_ui_service.py` — `tests/unit/ui/services/test_battle_ui_service.py`

- [ ] `test_get_ships_returns_empty_list_when_engine_is_none`
- [ ] `test_get_ships_converts_each_engine_ship_to_shipdto`
- [ ] `test_convert_ship_uses_ship_angle_as_dto_heading`
- [ ] `test_convert_ship_resolves_current_target_name_to_string`
- [ ] `test_convert_ship_lists_secondary_target_names_in_order`
- [ ] `test_convert_projectile_uses_projectile_colors_mapping_for_type`
- [ ] `test_convert_projectile_falls_back_to_default_color_for_unknown_type`
- [ ] `test_convert_beam_defaults_missing_color_to_white`

**Mocking notes:** Mock `BattleService.get_engine()`. Mock engine with
`.ships`, `.projectiles`, `.recent_beams`, `.tick_counter`,
`.is_battle_over()`, `.get_winner()`. No pygame.

---

## File: `ship_theme_manager.py` — `tests/unit/ui/assets/test_ship_theme_manager.py`

- [ ] `test_initialize_early_returns_when_themes_dir_missing`
- [ ] `test_initialize_skips_theme_with_invalid_theme_json`
- [ ] `test_initialize_warns_and_continues_on_unknown_schema_version`
- [ ] `test_initialize_skips_ship_class_when_skin_file_missing`
- [ ] `test_load_image_falls_back_to_default_theme_for_unknown_theme`
- [ ] `test_load_image_returns_synthetic_surface_for_unknown_ship_class`
- [ ] `test_load_image_caches_surface_and_does_not_reload_on_second_call`
- [ ] `test_get_image_metrics_returns_none_before_initialize`
- [ ] `test_get_portrait_image_returns_fallback_surface_when_portrait_missing`
- [ ] `test_clear_resets_caches_and_discovery_complete_flag`
- [ ] `test_get_available_themes_reflects_current_theme_data_keys`
- [ ] `test_set_default_ship_theme_manager_swaps_module_singleton`

**Mocking notes:** Monkeypatch
`game.ui.assets.ship_theme_manager.Paths.SHIP_THEMES_DIR` to `tmp_path`.
Patch `pygame.image.load` to return `pygame.Surface((100, 100), SRCALPHA)`
with `.convert_alpha()` returning self. Build hand-written `theme.json`
files in the fake tree.

---

## File: `scrollable_json_panel.py` — `tests/unit/ui/widgets/test_scrollable_json_panel.py`

- [ ] `test_set_json_with_diff_handles_none_payload_with_zero_content_height`
- [ ] `test_set_json_with_diff_appends_error_line_for_invalid_json_string`
- [ ] `test_format_value_truncates_long_strings_with_ellipsis`
- [ ] `test_get_diff_colors_suppresses_added_on_non_final_panel`
- [ ] `test_get_diff_colors_suppresses_removed_on_final_panel`
- [ ] `test_get_diff_colors_shows_changed_on_both_panels`
- [ ] `test_handle_event_consumes_mouse_wheel_inside_bounds`
- [ ] `test_handle_event_ignores_mouse_wheel_outside_bounds`
- [ ] `test_handle_event_starts_drag_on_scrollbar_mousedown`
- [ ] `test_path_has_changes_matches_direct_and_nested_paths`

**Mocking notes:** Patch `get_font` to return a Mock whose `.render`
returns a Mock with `.get_width=lambda: len(text)*7`. Build pygame `Event`
objects directly. Pass a real `pygame.Surface((W, H))` for `draw`.

---

## File: `hit_effects.py` — `tests/unit/ui/effects/test_hit_effects.py`

- [ ] `test_progress_clamps_at_one_when_elapsed_exceeds_duration`
- [ ] `test_progress_returns_one_when_duration_is_zero`
- [ ] `test_is_alive_flips_false_when_elapsed_meets_duration`
- [ ] `test_update_effects_drops_expired_and_advances_remaining`
- [ ] `test_draw_effects_skips_when_alpha_is_zero`
- [ ] `test_draw_shield_early_returns_when_size_is_below_threshold`
- [ ] `test_draw_armor_or_component_early_returns_when_radius_below_one`
- [ ] `test_ship_destroyed_flash_active_only_during_first_third_of_duration`
- [ ] `test_create_hit_effect_snapshots_position_and_radius_from_ship`

**Mocking notes:** Mock `camera.world_to_screen` returning `(x, y)`;
`camera.zoom` numeric. Real `pygame.Surface` as screen. Mock ship with
`.position.x/.y` and `.radius`.

---

## File: `base_gallery.py` — `tests/unit/ui/panels/test_base_gallery.py`

- [ ] `test_init_constructs_expected_widget_tree_for_populated_asset_list`
- [ ] `test_handle_button_click_returns_false_for_untracked_button`
- [ ] `test_existing_selection_in_config_fires_on_asset_selected_during_init`

**Mocking notes:** Patch `pygame_gui.elements.{UIPanel, UIManager,
UIScrollingContainer, UIButton, UIImage, UILabel}`. Subclass `BaseGallery`
in the test with all 9 abstracts implemented to return Mocks/lists. Assert
call shape (which classes built, with which rects), not pixel output.

---

## File: `builder_widgets.py` — `tests/unit/ui/panels/test_builder_widgets.py`

- [ ] `test_layout_renders_select_component_hint_when_editing_component_is_none`
- [ ] `test_on_row_change_toggle_true_adds_modifier_and_recalculates`
- [ ] `test_handle_event_clear_settings_button_returns_clear_settings_action`

**Mocking notes:** Patch `pygame_gui.elements.*` and `ModifierControlRow`.
Mock `GameRegistries` with `.modifiers` dict. Mock `ModifierLogic` /
`ModifierLogicService`. Mock editing component with `.name`,
`.add_modifier`, `.remove_modifier`, `.get_modifier`, `.recalculate_stats`.

---

## Totals

| File | Behaviors |
|---|---:|
| `battle_ui_service.py` | 8 |
| `ship_theme_manager.py` | 12 |
| `scrollable_json_panel.py` | 10 |
| `hit_effects.py` | 9 |
| `base_gallery.py` | 3 |
| `builder_widgets.py` | 3 |
| **Total** | **45** |

## Per-file commit checklist

- [ ] Commit 1 — `tests/unit/ui/services/test_battle_ui_service.py`
- [ ] Commit 2 — `tests/unit/ui/assets/test_ship_theme_manager.py`
- [ ] Commit 3 — `tests/unit/ui/widgets/test_scrollable_json_panel.py`
- [ ] Commit 4 — `tests/unit/ui/effects/test_hit_effects.py`
- [ ] Commit 5 — `tests/unit/ui/panels/test_base_gallery.py`
- [ ] Commit 6 — `tests/unit/ui/panels/test_builder_widgets.py`

## Verification (run after each commit and at end of phase)

- `pytest <new test path> -x -q`
- `python Tools/test_sharded/test_sharded.py` (end of phase)
- `python Tools/lint_test_files.py` (end of phase)
