# Remaining Duck Typing Instances (295 total)

## game\ai\combat_utils.py
- Line 48: if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):
- Line 67: if hasattr(entity, 'name'):
- Line 92: return getattr(entity, 'position', None)
- Line 108: return float(getattr(entity, 'angle', 0.0))
- Line 125: method = getattr(entity, 'get_all_components', None)
- Line 201: method = getattr(ship, 'get_components_by_ability', None)
## game\ai\controller.py
- Line 160: ship_id = getattr(ship, 'name', None)  # INTENTIONAL: defensive for cache building
## game\ai\interfaces\controllable.py
- Line 32: Accessed via getattr(ship, 'formation_rotation_mode', 'relative') with default.
## game\ai\target_evaluator.py
- Line 172: candidate_id = getattr(candidate, 'name', None)  # INTENTIONAL: Projectiles lack .name
- Line 190: # BUG FIX: Component has .current_hp, not .hp (getattr(c, 'hp', 0) always returned 0)
## game\app.py
- Line 200: if hasattr(self, 'builder_scene') and hasattr(self.builder_scene, 'cleanup'):
- Line 204: if hasattr(self.strategy_scene, 'handle_resize'):
- Line 448: return_state = getattr(self, '_keybindings_return_state', GameState.MENU)
- Line 452: if hasattr(self.strategy_scene, '_ui') and hasattr(self.strategy_scene._ui, '_apply_tooltips'):
- Line 565: if hasattr(self, 'showing_new_game_setup') and self.showing_new_game_setup:
- Line 598: if hasattr(self, 'return_state') and self.return_state == GameState.TEST_LAB:
- Line 637: savegame_path = game_session.save_path if hasattr(game_session, 'save_path') else None
- Line 640: empire_theme_id = empire.empire_theme_id if hasattr(empire, 'empire_theme_id') else None
- Line 648: built_designs=empire.built_ship_designs if hasattr(empire, 'built_ship_designs') else set(),
- Line 668: elif self.state == GameState.RESEARCH_TREE and hasattr(self.active_scene, 'handle_input'):
- Line 670: elif self.state == GameState.GALAXY_TEST and hasattr(self.active_scene, 'handle_input'):
## game\core\math.py
- Line 32: if hasattr(x, 'x') and hasattr(x, 'y'):
- Line 36: elif hasattr(x, '__iter__'):
- Line 83: if not hasattr(other, 'x') or not hasattr(other, 'y'):
## game\engine\collision.py
- Line 107: if source_ship and hasattr(source_ship, 'get_total_sensor_score'):
- Line 138: if getattr(s, 'ai_strategy', '') != 'kamikaze': continue
- Line 147: hp_rammer = getattr(s, 'hp', 100)
- Line 148: hp_target = getattr(target, 'hp', 100)
## game\simulation\components\abilities\base.py
- Line 327: base_value = getattr(self, base_attr, None)
- Line 331: current_value = getattr(self, binding.attribute_name, base_value)
- Line 372: val = getattr(cls, attr, '')
- Line 395: base = getattr(self, self.base_attr)
- Line 404: val = getattr(self, self.value_attr)
- Line 409: return float(getattr(self, self.value_attr))
## game\simulation\components\abilities\stat_keys.py
- Line 165: base_value = getattr(ability, base_attr, None)
## game\simulation\components\abilities\weapons.py
- Line 173: if getattr(self.component, 'facing_angle', None) is None:
- Line 261: self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))
- Line 281: self.accuracy_falloff = float(getattr(self.component, 'accuracy_falloff', 0.001))
- Line 282: self.base_accuracy = float(getattr(self.component, 'base_accuracy', 1.0))
- Line 337: self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))
- Line 338: self.endurance = float(getattr(self.component, 'endurance', 3.0))
- Line 339: self.turn_rate = float(getattr(self.component, 'turn_rate', 30.0))
- Line 340: self.to_hit_defense = float(getattr(self.component, 'to_hit_defense', 0.0))
- Line 341: self.projectile_damage = float(getattr(self.component, 'projectile_damage', 0))
- Line 342: self.projectile_hp = float(getattr(self.component, 'projectile_hp', 1.0))
- Line 343: self.projectile_stealth = float(getattr(self.component, 'projectile_stealth', 0.0))
## game\simulation\components\component.py
- Line 330: trigger = getattr(ability, 'trigger', None)
## game\simulation\components\component_resource_manager.py
- Line 97: base_costs = getattr(component, 'evaluated_resource_cost', None) or component.data.get("resource_cost", {})
- Line 107: eval_context['ship_class_mass'] = getattr(
## game\simulation\components\component_stats_calculator.py
- Line 148: eval_context['ship_class_mass'] = getattr(component.ship, 'max_mass_budget', 1000)
- Line 161: current = getattr(component, attr, None)
## game\simulation\components\modifier_introspection.py
- Line 142: effects = mod_def.evaluate_effects(mod_value) if hasattr(mod_def, 'evaluate_effects') else []
- Line 147: 'name': getattr(mod_def, 'display_name', mod_def.id),
## game\simulation\entities\ship.py
- Line 649: return getattr(self, attr_name, 0.0)
## game\simulation\formula_system.py
- Line 110: if hasattr(builtins, name):
- Line 111: names[name] = getattr(builtins, name)
## game\strategy\data\galaxy_spatial_index.py
- Line 52: if not hasattr(obj, 'location'):
## game\strategy\data\planet.py
- Line 94: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\strategy\data\race_config.py
- Line 337: if not (lo <= getattr(self, attr) <= hi):
- Line 361: value = getattr(self, attr)
## game\strategy\engine\fleet_order_processor.py
- Line 342: for emp in getattr(galaxy, 'empires', []):
## game\strategy\engine\game_session.py
- Line 118: cat_value = category.value if hasattr(category, 'value') else category
- Line 119: etype_value = event_type.value if hasattr(event_type, 'value') else event_type
## game\strategy\engine\harvesting_engine.py
- Line 75: abilities = getattr(comp_def, 'abilities', {}) or {}
- Line 213: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\strategy\engine\resource_management_engine.py
- Line 141: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\strategy\engine\resupply_engine.py
- Line 159: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\strategy\services\component_inspector.py
- Line 39: return getattr(comp_def, 'abilities', {})
## game\strategy\services\ship_stats_calculator.py
- Line 192: abilities = getattr(comp_def, 'abilities', {}) or {}
- Line 331: comp_type = getattr(comp_def, 'type_str', '')
- Line 339: abilities = getattr(comp_def, 'abilities', {}) or {}
- Line 358: threshold = getattr(comp_def, 'damage_threshold', DEFAULT_DAMAGE_THRESHOLD)
- Line 465: val = getattr(obj, attr, default)
## game\ui\components\table\header.py
- Line 131: if hasattr(el, "col_ref") and hasattr(el, "direction"):
- Line 135: elif hasattr(el, "sort_col_ref"):
## game\ui\panels\battle_panels.py
- Line 38: ui_service = getattr(self.scene, 'ui_service', None)
- Line 49: return getattr(self.scene, 'ships', [])
- Line 71: ship_id = getattr(ship, 'id', None)
- Line 75: ship_name = getattr(ship, 'name', None)
- Line 275: proj_id = getattr(proj, 'id', None)
- Line 353: status = getattr(proj, 'status', 'active')
- Line 401: max_speed = getattr(proj, 'max_speed', p_vel_len) * 100.0 if getattr(proj, 'max_speed', 0) > 0 else p_vel_len
- Line 407: hp = getattr(proj, 'hp', 0)
- Line 408: max_hp = getattr(proj, 'max_hp', hp) if getattr(proj, 'max_hp', 0) > 0 else max(hp, 1)
- Line 418: endurance = getattr(proj, 'endurance', 0)
- Line 419: max_endurance = getattr(proj, 'max_endurance', endurance) if getattr(proj, 'max_endurance', 0) > 0 else max(endurance, 1)
- Line 434: target = getattr(proj, 'target', None)
- Line 435: t_name = target.name if target and hasattr(target, 'name') else "None"
- Line 496: if hasattr(self.scene, 'test_mode') and self.scene.test_mode:
- Line 498: is_over = self.scene.is_battle_over() if hasattr(self.scene, 'is_battle_over') else False
## game\ui\panels\build_queue_controller.py
- Line 307: if getattr(source, 'planet_id', None) is not None:
- Line 337: return getattr(source, 'planet_id', None)
- Line 341: if getattr(source, 'planet_id', None) is not None:
## game\ui\panels\build_queue_drag_handler.py
- Line 108: if hasattr(element, 'design_id'):
- Line 135: idx = getattr(element, 'queue_index', -1)
## game\ui\panels\build_queue_portraits.py
- Line 86: if hasattr(self.session, 'player_empire') and hasattr(self.session.player_empire, 'empire_theme_id'):
- Line 89: ship_class = getattr(design, 'ship_class', 'Unknown')
- Line 157: vehicle_type = getattr(design, 'vehicle_type', 'Ship')
## game\ui\panels\builder_widgets.py
- Line 83: self._cached_scroll_position = self.scroll_container.vert_scroll_bar.scroll_position if hasattr(self.scroll_container, 'vert_scroll_bar') and self.scroll_container.vert_scroll_bar else 0
- Line 145: if not hasattr(row, 'y') or row.y != row_y:
- Line 273: if hasattr(self, 'clear_settings_btn') and event.ui_element == self.clear_settings_btn:
## game\ui\panels\component_modifier_grid_panel.py
- Line 85: elif selection_data and hasattr(selection_data, 'id'):
## game\ui\panels\design_stats_panel.py
- Line 329: if hasattr(row, 'definition'):
## game\ui\panels\modifier_impact_grid.py
- Line 177: stat_bindings = getattr(ability_class, 'STAT_BINDINGS', None)
## game\ui\panels\planet_report_panel.py
- Line 443: if hasattr(self, 'resource_panel') and self.resource_panel:
- Line 447: if hasattr(self, 'panel'):
- Line 511: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\ui\panels\race_aptitudes_panel.py
- Line 218: return getattr(self.race_config, attr_name, 5)
## game\ui\panels\race_environment_panel.py
- Line 435: if not getattr(self, 'points_label', None):
- Line 585: if hasattr(event, 'ui_element') and event.ui_element == self.homeworld_dropdown:
## game\ui\panels\race_identity_panel.py
- Line 443: if hasattr(event, 'ui_element') and event.ui_element == self.faction_name_input:
- Line 447: elif hasattr(event, 'ui_element') and event.ui_element == self.race_name_input:
- Line 457: if hasattr(event, 'ui_element') and event.ui_element == self.government_type_dropdown:
## game\ui\panels\ship_detail_panel.py
- Line 429: if hasattr(event, 'user_type') and event.user_type == 'ui_button_pressed':
## game\ui\panels\ship_stats_renderer.py
- Line 66: status = getattr(comp, 'status', ComponentStatus.ACTIVE)
- Line 158: if not comp.is_active and getattr(comp, 'status', ComponentStatus.ACTIVE) != ComponentStatus.ACTIVE:
- Line 184: stats_str = f"S:{getattr(comp, 'shots_fired', 0)} H:{getattr(comp, 'shots_hit', 0)}"
- Line 245: if hasattr(ship, 'source_file') and ship.source_file:
- Line 316: crew_req = getattr(ship, 'crew_required', 0)
- Line 317: crew_cur = getattr(ship, 'crew_onboard', 0)
- Line 328: target_name = getattr(ship.current_target, 'name', getattr(ship.current_target, 'type', 'Target').title())
- Line 338: st_name = getattr(st, 'name', getattr(st, 'type', 'Target').title())
## game\ui\panels\strategy_widgets.py
- Line 46: val = getattr(s, attr, 0.0)
## game\ui\panels\system_tree_panel.py
- Line 357: if hasattr(item, 'is_group'):
- Line 374: if hasattr(child, 'is_group'):
- Line 388: if hasattr(item, 'is_group'):
- Line 397: if hasattr(child, 'is_group'):
- Line 399: if hasattr(child, 'group_key'):
## game\ui\renderer\camera.py
- Line 65: if hasattr(self.target, 'is_alive') and not self.target.is_alive:
## game\ui\renderer\game_renderer.py
- Line 71: theme_id = getattr(ship, 'theme_id', 'Federation')
- Line 101: show_overlay = getattr(camera, 'show_overlay', False)
## game\ui\screens\battle_screen.py
- Line 445: if not hasattr(self.test_scenario, 'results') or not self.test_scenario.results:
- Line 555: color = getattr(p, 'color', (255, 200, 50))
- Line 557: pygame.draw.circle(screen, (255, 255, 100), (int(end[0]), int(end[1])), int(getattr(p, 'radius', 4)))
- Line 640: if hasattr(self.ui, 'print_headless_summary'):
## game\ui\screens\battle_ui.py
- Line 44: if getattr(proj, 'type', None) == AttackType.MISSILE:
- Line 184: if hasattr(s, 'aim_point') and s.aim_point:
- Line 257: if hasattr(self.scene, 'test_scenario') and self.scene.test_scenario:
## game\ui\screens\build_queue_panel_factory.py
- Line 191: ship_count = len(self.build_context.ships) if hasattr(self.build_context, 'ships') else 0
- Line 445: empire = getattr(self.session, 'current_empire', None)
- Line 446: if empire and hasattr(empire, 'resource_pool'):
- Line 458: turn_number = getattr(self.session, 'turn', 0)
## game\ui\screens\build_queue_renderer.py
- Line 74: raw_cost = getattr(design, 'resource_cost', None)
- Line 275: if getattr(item_panel, 'queue_index', -1) == selected_queue_index:
## game\ui\screens\build_queue_screen.py
- Line 177: if not hasattr(build_context, 'owner_id'):
- Line 179: f"build_context '{getattr(build_context, 'name', 'unknown')}' missing 'owner_id' attribute",
- Line 183: if not hasattr(build_context, 'name'):
## game\ui\screens\build_queue_selector.py
- Line 140: if not hasattr(button, 'queue_source_index'):
## game\ui\screens\builder\detail_panel.py
- Line 95: elif hasattr(selection_data, 'id'):
- Line 145: if hasattr(comp, 'get_ui_rows'):
## game\ui\screens\builder\left_panel.py
- Line 214: return getattr(self, '_dropdown_expanded', False)
- Line 254: v_type = getattr(self.builder.ship, 'vehicle_type', "Ship")
- Line 352: if getattr(item, 'is_hovered', False) and item != self.selected_item:
## game\ui\screens\builder\modifier_row.py
- Line 177: if hasattr(self.slider, 'enable_arrow_buttons'):
- Line 269: if not hasattr(event, 'ui_element'):
## game\ui\screens\builder\schematic_view.py
- Line 71: theme_id = getattr(ship, 'theme_id', 'Federation')
## game\ui\screens\builder\stats_config.py
- Line 20: The `get_value()` method uses `getattr(ship, self.attr_key, 0)` intentionally.
- Line 42: return getattr(ship, self.getter, 0)
- Line 44: return getattr(ship, self.attr_key, 0)
## game\ui\screens\builder_selection.py
- Line 22: elif hasattr(item, 'id'):  # It's a component
## game\ui\screens\design_selector_window.py
- Line 285: if hasattr(self, 'design_rows'):
- Line 459: elif hasattr(event.ui_element, 'is_obsolete_button') and event.ui_element.is_obsolete_button:
- Line 464: elif hasattr(event.ui_element, 'design_id'):
## game\ui\screens\empire_build_queue_formatter.py
- Line 79: system = getattr(entity, 'system_name', None)
- Line 86: return getattr(sys_obj, 'name', '-')
- Line 88: location = getattr(entity, 'location', None)
- Line 92: return getattr(sys_obj, 'name', '-')
- Line 107: location = getattr(entity, 'location', None)
- Line 112: hex_loc = getattr(entity, 'global_hex', None) or getattr(entity, 'location', None)
## game\ui\screens\empire_build_queue_window.py
- Line 328: return getattr(entity, 'location', None)
## game\ui\screens\event_log_window.py
- Line 231: if hasattr(event, "type") and event.type == pygame_gui.UI_BUTTON_PRESSED:
- Line 232: clicked = getattr(event, "ui_element", None)
## game\ui\screens\fleet_orders_window.py
- Line 94: if hasattr(element, 'kill'):
## game\ui\screens\fleet_report_window.py
- Line 158: if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel.process_event(event):
- Line 162: if hasattr(event, 'user_type') and event.user_type == 'ui_button_pressed':
- Line 171: if hasattr(event, 'user_type') and event.user_type == 'ui_vertical_scroll_bar_moved':
- Line 356: if hasattr(self, 'virtual_table') and self.virtual_table:
- Line 360: if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel:
## game\ui\screens\formation_editor.py
- Line 778: if hasattr(self, 'rotation_mode_btn'):
- Line 797: if hasattr(self, 'renumber_slider'):
## game\ui\screens\galaxy_test\screen.py
- Line 214: if button == getattr(self, 'btn_galaxy', None):
- Line 216: elif button == getattr(self, 'btn_system', None):
- Line 218: elif button == getattr(self, 'btn_close', None):
- Line 220: elif button == getattr(self.system_helper, 'btn_back', None) or button == getattr(self.galaxy_helper, 'btn_back', None):
- Line 222: elif button == getattr(self.galaxy_helper, 'btn_generate', None):
- Line 224: elif button == getattr(self.system_helper, 'btn_generate_system', None):
## game\ui\screens\galaxy_test\system_mode.py
- Line 520: color = star.color if hasattr(star, 'color') else (255, 255, 200)
## game\ui\screens\keybindings_scene.py
- Line 63: if attr.startswith("K_") and isinstance(getattr(pygame, attr), int):
- Line 64: _PYGAME_KEY_NAMES[getattr(pygame, attr)] = attr
## game\ui\screens\planet_data_source.py
- Line 160: if hasattr(obj, a):
- Line 161: obj = getattr(obj, a)
- Line 185: if not hasattr(planet, "image_id") or not planet.image_id:
- Line 189: rotation = getattr(planet, "image_rotation", 0) or 0
## game\ui\screens\planet_list_filters.py
- Line 70: owner_id = getattr(p, 'owner_id', None)
- Line 136: if hasattr(obj, a):
- Line 137: obj = getattr(obj, a)
- Line 163: if hasattr(obj, a):
- Line 164: obj = getattr(obj, a)
- Line 202: if hasattr(p, 'surface_gravity'):
- Line 205: if hasattr(p, 'surface_temperature'):
- Line 208: if hasattr(p, 'mass'):
- Line 240: if hasattr(planet, '_temp_system_ref'):
- Line 260: if galaxy and hasattr(galaxy, 'empires'):
- Line 297: if hasattr(planet, 'resources') and resource_name in planet.resources:
## game\ui\screens\planet_list_window.py
- Line 365: if not hasattr(self, 'last_preset_selection'):
- Line 440: if hasattr(self, 'asset_resolver') and self.asset_resolver:
- Line 495: if hasattr(self, 'virtual_table'):
## game\ui\screens\race_asset_loader.py
- Line 269: if hasattr(empire, 'empire_theme_id') and empire.empire_theme_id:
- Line 274: if hasattr(empire, 'flag_id') and empire.flag_id:
## game\ui\screens\race_setup_screen.py
- Line 384: if hasattr(self, '_ship_preview_elements'):
- Line 389: if not hasattr(self, 'ship_preview_scroll'):
- Line 889: elif hasattr(self, 'btn_load') and self.btn_load and event.ui_element == self.btn_load:
## game\ui\screens\strategy_build_queue_manager.py
- Line 44: if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
- Line 63: savegame_path = getattr(self._screen.session, 'save_path', None)
- Line 97: queue_sources = getattr(self._screen.build_queue_screen, 'queue_sources', [])
- Line 155: if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
- Line 178: savegame_path = getattr(self._screen.session, 'save_path', None)
- Line 202: if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
- Line 221: savegame_path = getattr(self._screen.session, 'save_path', None)
## game\ui\screens\strategy_click_dispatcher.py
- Line 524: if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
## game\ui\screens\strategy_colonization.py
- Line 82: if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
- Line 83: zone_lookup = getattr(self.scene.galaxy, 'get_zones_at_global_hex', None)
- Line 196: if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
- Line 197: zone_lookup = getattr(self.scene.galaxy, 'get_zones_at_global_hex', None)
## game\ui\screens\strategy_detail_fmt.py
- Line 302: p_name = getattr(order.target, 'name', 'Unknown')
- Line 305: queue = getattr(fleet, 'construction_queue', [])
## game\ui\screens\strategy_detail_formatter.py
- Line 208: if hasattr(self.scene, 'current_empire'):
- Line 346: if hasattr(self.scene, 'turn_engine'):
## game\ui\screens\strategy_event_router.py
- Line 58: if hasattr(self.ui.scene, 'build_queue_screen') and self.ui.scene.build_queue_screen is not None:
- Line 88: if hasattr(self.ui.scene, 'on_ui_selection'):
- Line 131: if hasattr(self.ui.scene, '_quit_confirm_dialog') and event.ui_element == self.ui.scene._quit_confirm_dialog:
- Line 149: if hasattr(ui.scene, 'on_design_click'):
- Line 191: if not hasattr(ui.scene, 'galaxy'):
- Line 213: if hasattr(ui.scene, 'request_colonize_order'):
- Line 218: if hasattr(ui.scene, 'request_colonize_order'):
## game\ui\screens\strategy_game_state_manager.py
- Line 110: turn_engine = getattr(self._screen.session, 'turn_engine', None)
- Line 113: events = getattr(turn_engine, 'last_scuttle_events', [])
## game\ui\screens\strategy_input_handler.py
- Line 56: if hasattr(self.scene, 'build_queue_screen') and self.scene.build_queue_screen is not None:
- Line 61: if hasattr(self.scene, 'ui') and hasattr(self.scene.ui, 'planet_list_window') and self.scene.ui.planet_list_window is not None:
- Line 163: if hasattr(self.scene, 'ui') and hasattr(self.scene.ui, '_has_modal_open'):
## game\ui\screens\strategy_renderer.py
- Line 122: if getattr(self.scene, 'input_mode', 'SELECT') == 'MOVE' and self.scene.selected_fleet:
## game\ui\screens\strategy_screen.py
- Line 202: if hasattr(self, 'build_queue_screen') and self.build_queue_screen is not None:
- Line 336: 'empire': self.session.player_empire if hasattr(self, 'session') else None,
- Line 337: 'game_session': self.session if hasattr(self, 'session') else None
## game\ui\screens\strategy_superweapons.py
- Line 374: if hasattr(self.scene.ui, 'show_confirmation_dialog'):
- Line 390: if hasattr(self.scene.ui, 'show_system_picker'):
- Line 407: if hasattr(self.scene.ui, 'show_ship_picker'):
## game\ui\screens\strategy_ui.py
- Line 211: if hasattr(self, 'system_tree'):
- Line 213: if hasattr(self, 'sector_tree'):
- Line 256: if hasattr(self.scene, '_get_object_asset'):
- Line 285: if not hasattr(self.scene, 'current_empire'):
## game\ui\screens\strategy_window_manager.py
- Line 202: if hasattr(self.scene, "facade")
## game\ui\screens\test_lab\data_extractor.py
- Line 120: if hasattr(scenario_cls, 'ship_file') and scenario_cls.ship_file:
## game\ui\screens\test_lab\dialogs.py
- Line 61: if hasattr(self, 'close_button') and self.close_button:
- Line 194: if hasattr(self, 'confirm_button') and self.confirm_button:
- Line 196: if hasattr(self, 'cancel_button') and self.cancel_button:
## game\ui\screens\test_lab\screen.py
- Line 65: self.screen_width = game.screen.get_width() if hasattr(game, 'screen') else WIDTH
- Line 66: self.screen_height = game.screen.get_height() if hasattr(game, 'screen') else HEIGHT
- Line 332: if self.selected_test_id and hasattr(self.game.battle_scene, 'test_scenario'):
- Line 337: if not hasattr(scenario, 'results') or scenario.results is None:
- Line 342: scenario.results['passed'] = getattr(scenario, 'passed', False)
- Line 357: if hasattr(self.game.battle_scene, 'test_completed'):
- Line 359: if hasattr(self.game.battle_scene, 'test_scenario'):
- Line 369: if hasattr(self.game, 'menu_screen') and hasattr(self.game.menu_screen, 'create_particles'):
- Line 580: if event.type == pygame_gui.UI_BUTTON_PRESSED and hasattr(event, 'ui_element'):
## game\ui\screens\transfer_dialog.py
- Line 158: if hasattr(self, 'lbl_debug'):
## game\ui\screens\workshop_viewmodel.py
- Line 166: elif hasattr(item, 'id'):  # It's a component
## game\ui\services\battle_factories.py
- Line 133: max_ticks=scenario.max_ticks if hasattr(scenario, 'max_ticks') else 100000,
## game\ui\services\battle_ui_service.py
- Line 170: if ship.current_target and hasattr(ship.current_target, 'name'):
- Line 176: if hasattr(target, 'name'):
- Line 180: ship_id = str(getattr(ship, 'id', id(ship)))
- Line 205: crew_onboard=getattr(ship, 'crew_onboard', 0),
- Line 206: crew_required=getattr(ship, 'crew_required', 0),
- Line 228: if hasattr(comp, 'status') and hasattr(comp.status, 'name'):
- Line 233: if hasattr(comp, 'has_ability'):
- Line 244: shots_fired=getattr(comp, 'shots_fired', 0),
- Line 245: shots_hit=getattr(comp, 'shots_hit', 0)
- Line 259: target = getattr(proj, 'target', None)
- Line 260: if target and hasattr(target, 'name'):
- Line 264: proj_id = str(getattr(proj, 'id', id(proj)))
- Line 267: proj_type = getattr(proj, 'type', None)
- Line 275: radius=getattr(proj, 'radius', 4.0),
- Line 277: hp=getattr(proj, 'hp', 0.0),
- Line 278: max_hp=getattr(proj, 'max_hp', 0.0),
- Line 279: status=getattr(proj, 'status', 'active'),
- Line 280: endurance=getattr(proj, 'endurance', 0.0),
- Line 281: max_endurance=getattr(proj, 'max_endurance', 0.0),
- Line 283: max_speed=getattr(proj, 'max_speed', 0.0)
## game\ui\services\input_mapper.py
- Line 158: value = getattr(pygame, key_name, None)
- Line 204: if getattr(event, "type", None) != pygame.KEYDOWN:
## game\ui\services\screenshot_manager.py
- Line 149: if hasattr(scene, 'ui') and scene.ui:
- Line 155: if hasattr(scene, 'build_queue_screen') and scene.build_queue_screen:
- Line 161: sidebar_width = getattr(scene, 'SIDEBAR_WIDTH', 300)
- Line 162: top_bar_height = getattr(scene, 'TOP_BAR_HEIGHT', 40)
## game\ui\services\ship_io.py
- Line 142: if getattr(new_ship, '_loading_warnings', []):
