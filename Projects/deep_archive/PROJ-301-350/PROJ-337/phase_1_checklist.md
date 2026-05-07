# PROJ-337 Phase 1 — Gap-Fill Checklist

Each behavior listed becomes one test with a specific name. Assertion
technique notes are inline (which mock to spy on, which property to
assert). All new tests reuse existing fixtures (see `manifest.md`).

---

## research_scene.py — gap-fill (~12 tests)

Target: `tests/unit/research/research_scene/test_event_routing_and_draw.py`
Fixture: `_patched_research_scene` contextmanager.

### Section A: handle_event routing

- [ ] `test_handle_event_returns_early_when_ui_manager_consumes`
      — patched `ui_manager.process_events` returns True; assert
      `control_panel.handle_event` not called.
- [ ] `test_handle_event_returns_early_when_control_panel_consumes`
      — `control_panel.handle_event` returns True; assert no further
      routing (no `_handle_click`, no camera dispatch).
- [ ] `test_handle_event_escape_key_invokes_on_close`
      — synthesize `pygame.KEYDOWN` with `K_ESCAPE`; assert
      `on_close_callback` called once.
- [ ] `test_handle_event_left_click_on_canvas_calls_handle_click`
      — `MOUSEBUTTONDOWN` button=1 with `pos` inside canvas; spy on
      `_handle_click`.
- [ ] `test_handle_event_left_click_on_sidebar_is_ignored`
      — `pos.x >= canvas_width`; assert `_handle_click` not called.
- [ ] `test_handle_event_mousewheel_over_canvas_routes_to_camera`
      — `MOUSEWHEEL` while `pygame.mouse.get_pos()` (patched) is over
      canvas; assert `camera.handle_zoom` (or equivalent) called.
- [ ] `test_handle_event_mousewheel_over_sidebar_is_ignored`
      — mouse pos in sidebar; assert camera not called.

### Section B: draw + lifecycle

- [ ] `test_draw_fills_background_then_canvas_then_renderer_then_sidebar_then_ui`
      — pass `MagicMock(spec=pygame.Surface)`; record call order via a
      single `Mock.mock_calls` chain; assert sequence.
- [ ] `test_handle_input_routes_to_camera_only_when_mouse_over_canvas`
      — patch `pygame.mouse.get_pos`; assert `camera.handle_input` only
      invoked when in-canvas.
- [ ] `test_handle_resize_re_pushes_selected_node_when_set`
      — set `_selected_node_id`; call `handle_resize`; assert new
      `control_panel.update_selected_node` called with that node.
- [ ] `test_validate_requirements_errors_logged_first_5`
      — patch `tech_tree.validate_requirements` to return 7 errors;
      assert logger captures exactly the first 5.
- [ ] `test_on_next_turn_refreshes_selected_node_display`
      — set selected node; call `_on_next_turn`; assert
      `control_panel.update_selected_node` called with the same node
      after `process_turn`.

---

## research_renderer.py — gap-fill (~18 tests)

Target: `tests/unit/research/test_research_renderer_drawing.py`
Fixture: `renderer_module` autouse + `MagicMock(spec=pygame.Surface)` +
`monkeypatch` of `pygame.draw.line` / `pygame.draw.rect`.

### Section A: draw orchestration

- [ ] `test_draw_sets_clip_to_canvas_rect_then_clears`
      — spy on `screen.set_clip`; assert called with `canvas_rect` then
      with `None` (or no-arg) by end of `draw`.
- [ ] `test_draw_calls_dependency_lines_before_nodes`
      — spy on private methods via patch; assert `_draw_dependency_lines`
      invoked before `_draw_nodes`.

### Section B: dependency lines

- [ ] `test_dependency_lines_skip_nodes_missing_from_positions`
      — node id absent from `node_positions`; assert no `pygame.draw.line`
      call references its position.
- [ ] `test_dependency_lines_skip_off_screen_nodes`
      — camera placed so node is off-screen; assert no draw call for it.
- [ ] `test_dependency_line_color_uses_met_when_prereq_meets_required_level`
      — `tech_levels[prereq] >= req.level`; assert color arg is the met
      color (RESEARCH_COMPLETED-derived).
- [ ] `test_dependency_line_color_uses_unmet_when_prereq_below_required`
      — assert color arg is the unmet color.
- [ ] `test_negated_requirement_is_met_when_prereq_below_required`
      — `req.negate=True`, prereq < required; assert dashed-met color.
- [ ] `test_negated_requirement_uses_dashed_drawer`
      — assert `_draw_dashed_line` invoked, not `pygame.draw.line`.

### Section C: dashed line geometry

- [ ] `test_dashed_line_zero_length_is_noop`
      — start == end; assert zero `pygame.draw.line` calls.
- [ ] `test_dashed_line_clamps_final_dash_to_endpoint`
      — choose length not divisible by `dash_length*2`; assert last call
      endpoint exactly equals provided end.

### Section D: node drawing

- [ ] `test_node_color_completed_uses_research_completed`
      — status `completed`; assert `pygame.draw.rect` color arg.
- [ ] `test_node_color_available_uses_research_available`
- [ ] `test_node_color_locked_fallback`
      — status not in known set; assert default color used.
- [ ] `test_selected_node_drawn_with_selected_color_width_3`
      — selected_id matches; assert border draw call width=3.
- [ ] `test_unselected_node_uses_lightened_border_width_1`
      — assert width=1.
- [ ] `test_rp_allocation_bar_drawn_only_when_allocation_positive`
      — allocation>0 triggers extra rect call; allocation==0 does not.
- [ ] `test_node_text_drawn_only_when_zoom_above_quarter`
      — zoom <= 0.25 → no text blits; zoom > 0.25 → text blit calls.
- [ ] `test_node_off_screen_with_margin_is_culled`
      — node outside `_is_visible(margin=NODE_WIDTH)`; assert no draw.

### Section E: node text

- [ ] `test_long_name_truncated_with_ellipsis`
      — patched font reports width > rect.width; assert rendered string
      ends with `...`.
- [ ] `test_chance_label_only_rendered_when_status_available`
      — status `completed` or locked → no chance render.
- [ ] `test_rp_color_text_muted_when_allocation_zero`
      — assert font.render color arg is TEXT_MUTED.

### Section F: misc

- [ ] `test_get_font_enforces_minimum_size_8`
      — call `_get_font(2)`; assert delegated `get_font` invoked with 8.

---

## research_controls.py — gap-fill (~25 tests)

Target: `tests/unit/research/research_controls/test_event_routing_and_updates.py`
Fixtures: `mock_pygame_gui` autouse, `mock_tracker`, `mock_node`.
Pattern: `MagicMock(spec=ResearchControlPanel)` instance with real
methods bound via lambda (per `test_reset_state.py`).

### Section A: handle_event button routing

- [ ] `test_btn_next_turn_invokes_callback_returns_true`
      — synthesize `UI_BUTTON_PRESSED` whose `ui_element` is
      `panel.btn_next_turn`; assert `on_next_turn` called and method
      returns True.
- [ ] `test_btn_close_invokes_callback_returns_true`
- [ ] `test_btn_reset_invokes_callback_returns_true`
- [ ] `test_btn_auto_spread_toggles_and_invokes_callback`
      — assert `_toggle_auto_spread` invoked; verify `on_auto_spread_changed`
      called with new state.
- [ ] `test_unhandled_event_returns_false`
      — `UI_BUTTON_PRESSED` with unknown ui_element; assert returns False.

### Section B: handle_event slider routing

- [ ] `test_slider_budget_updates_tracker_label_and_allocation_range`
      — `UI_HORIZONTAL_SLIDER_MOVED` on `slider_budget`; assert
      `tracker.set_rp_budget`, `update_budget_display`, and
      `_update_allocation_slider_range` all called.
- [ ] `test_slider_allocation_uses_actual_clamped_value_in_label`
      — `tracker.set_allocation` returns clamped value different from
      slider value; assert label text uses returned value.

### Section C: update_selected_node

- [ ] `test_update_selected_node_populates_all_seven_labels`
      — assert all 7 label `set_text` calls fire.
- [ ] `test_update_selected_node_price_label_shows_maxed_when_at_cap`
      — `current_level == max_levels`; assert price label text contains
      `"- (maxed)"`.
- [ ] `test_update_selected_node_enables_allocation_slider_only_when_available`
      — status != 'available' → slider disabled.
- [ ] `test_update_selected_node_sets_allocation_to_state_rp_allocation`
      — assert slider `set_current_value(state.rp_allocation)`.

### Section D: clear_selection

- [ ] `test_clear_selection_resets_all_seven_labels_to_placeholder`
- [ ] `test_clear_selection_disables_allocation_slider_resets_to_zero`

### Section E: budget + auto-spread

- [ ] `test_update_budget_display_writes_allocated_over_budget`
      — assert text matches `"{allocated} / {budget}"` format.
- [ ] `test_toggle_auto_spread_on_calls_spread_rp_evenly`
      — flag transitions False→True; assert
      `tracker.spread_rp_evenly(tech_tree)` called.
- [ ] `test_toggle_auto_spread_off_does_not_call_spread_rp_evenly`
      — flag transitions True→False; assert NOT called.
- [ ] `test_update_auto_spread_button_text_matches_state`
      — verify `"Auto-Spread: ON"` and `"Auto-Spread: OFF"` cases.
- [ ] `test_update_allocation_slider_range_uses_max_one_floor`
      — `current_allocation + remaining == 0`; assert range upper bound
      is 1, not 0.

### Section F: update_turn_log

- [ ] `test_update_turn_log_no_events_writes_no_events_text`
      — empty events list; assert text contains `"No events."`.
- [ ] `test_update_turn_log_breakthrough_renders_breakthrough_text`
      — assert HTML contains `BREAKTHROUGH` and `new_level`.
- [ ] `test_update_turn_log_progress_renders_chance_roll_rp`
      — assert chance %, roll, and RP all appear.
- [ ] `test_update_turn_log_decay_renders_old_arrow_new_chance`
      — assert `old_chance` arrow `new_chance` rendered.
- [ ] `test_update_turn_log_prepends_new_turn_to_existing_log`
      — pre-load log; assert new turn HTML appears before existing.
- [ ] `test_update_turn_log_truncates_after_five_turns`
      — CHARACTERIZE: pin observed split-then-keep behavior even if it
      looks wrong (file separate ticket if so).
- [ ] `test_update_turn_log_replaces_no_events_placeholder`
      — initial `"No events yet"`; first turn replaces it.

### Section G: clear_log

- [ ] `test_clear_log_resets_log_to_placeholder_text`
      — assert `set_text` called with placeholder constant.
