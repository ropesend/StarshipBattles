# Duck Typing Instances (655 total)

## game\ai\behaviors.py
- Line 281: if not master or not master.is_alive or getattr(master, 'is_derelict', False):
- Line 334: if getattr(master, 'is_thrusting', False):
- Line 336: master_target_speed = getattr(master, 'max_speed', 0) * getattr(master, 'engine_throttle', 1.0)
## game\ai\combat_utils.py
- Line 44: if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):
- Line 47: return hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'distance_to')
- Line 63: return getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))
- Line 83: get_pos = getattr(entity, 'get_position', None)
- Line 96: return getattr(entity, 'position', None)
- Line 113: get_rot = getattr(entity, 'get_rotation', None)
- Line 125: return float(getattr(entity, 'angle', 0.0))
- Line 137: if hasattr(entity, 'get_all_components') and callable(getattr(entity, 'get_all_components', None)):
- Line 180: total_max = sum(getattr(c, 'max_hp', 0) for c in components)
- Line 181: total_current = sum(getattr(c, 'current_hp', getattr(c, 'max_hp', 0)) for c in components)
- Line 207: get_by_ability = getattr(ship, 'get_components_by_ability', None)
- Line 212: has_pdc = getattr(comp, 'has_pdc_ability', None)
## game\ai\controller.py
- Line 125: if (getattr(obj, 'type', '') == 'missile' or getattr(obj, 'type', '') == AttackType.MISSILE)
- Line 127: and getattr(obj, 'team_id', -1) != self.ship.get_team_id()
- Line 156: ship_id = getattr(ship, 'id', None)
- Line 199: e_pos = getattr(e, 'position', None)
- Line 391: if getattr(comp, 'current_hp', 1) < getattr(comp, 'max_hp', 1):
- Line 411: own_ship = getattr(self.ship, 'ship', self.ship)
- Line 420: thresh = self.ship.get_radius() + getattr(obj, 'radius', 40) + BattleConfig.COLLISION_BUFFER
## game\ai\interfaces\controllable.py
- Line 32: Accessed via getattr(ship, 'formation_rotation_mode', 'relative') with default.
- Line 406: return getattr(self._ship, 'max_targets', CombatConstants.DEFAULT_MAX_TARGETS)
- Line 426: return getattr(self._ship, 'ai_strategy', 'standard_ranged')
- Line 430: return getattr(self._ship, 'vehicle_type', 'Ship')
- Line 472: if master and hasattr(master, 'formation') and hasattr(master.formation, 'members'):
## game\ai\target_evaluator.py
- Line 87: mass = getattr(candidate, 'mass', 100)
- Line 118: speed = getattr(candidate, 'velocity', Vector2(0, 0)).length()
- Line 166: candidate_id = getattr(candidate, 'id', None)
- Line 184: armor_hp = sum(getattr(c, 'hp', 0) for c in armor_comps)
- Line 194: e_type = getattr(candidate, 'type', '')
## game\app.py
- Line 199: if hasattr(self, 'builder_scene') and hasattr(self.builder_scene, 'cleanup'):
- Line 203: if hasattr(self.strategy_scene, 'handle_resize'):
- Line 447: return_state = getattr(self, '_keybindings_return_state', GameState.MENU)
- Line 451: if hasattr(self.strategy_scene, '_ui') and hasattr(self.strategy_scene._ui, '_apply_tooltips'):
- Line 564: if hasattr(self, 'showing_new_game_setup') and self.showing_new_game_setup:
- Line 597: if hasattr(self, 'return_state') and self.return_state == GameState.TEST_LAB:
- Line 636: savegame_path = game_session.save_path if hasattr(game_session, 'save_path') else None
- Line 639: empire_theme_id = empire.empire_theme_id if hasattr(empire, 'empire_theme_id') else None
- Line 647: built_designs=empire.built_ship_designs if hasattr(empire, 'built_ship_designs') else set(),
- Line 667: elif self.state == GameState.RESEARCH_TREE and hasattr(self.active_scene, 'handle_input'):
- Line 669: elif self.state == GameState.GALAXY_TEST and hasattr(self.active_scene, 'handle_input'):
## game\core\math.py
- Line 32: if hasattr(x, 'x') and hasattr(x, 'y'):
- Line 36: elif hasattr(x, '__iter__'):
- Line 83: if not hasattr(other, 'x') or not hasattr(other, 'y'):
## game\engine\collision.py
- Line 107: if source_ship and hasattr(source_ship, 'get_total_sensor_score'):
- Line 138: if getattr(s, 'ai_strategy', '') != 'kamikaze': continue
- Line 147: hp_rammer = getattr(s, 'hp', 100)
- Line 148: hp_target = getattr(target, 'hp', 100)
## game\simulation\battle_state.py
- Line 91: for mod in getattr(component, 'modifiers', []):
- Line 296: if hasattr(ship, 'current_target') and ship.current_target:
- Line 298: current_target_id = getattr(ship.current_target, 'name', None)
- Line 500: if hasattr(proj, 'target') and proj.target:
- Line 505: if hasattr(proj_type, 'value'):
- Line 517: max_endurance=getattr(proj, 'max_endurance', proj.endurance or 0),
- Line 519: turn_rate=getattr(proj, 'turn_rate', 0),
- Line 520: max_speed=getattr(proj, 'max_speed', 0),
- Line 522: hp=getattr(proj, 'hp', 1),
- Line 523: max_hp=getattr(proj, 'max_hp', 1),
- Line 524: distance_traveled=getattr(proj, 'distance_traveled', 0),
- Line 697: if hasattr(engine, 'end_condition') and engine.end_condition:
- Line 701: if hasattr(engine, 'end_condition') and engine.end_condition:
## game\simulation\combat\targeting_system.py
- Line 101: if not getattr(candidate, 'is_alive', True):
- Line 104: if getattr(candidate, 'team_id', -1) == ship.team_id:
- Line 152: if not getattr(candidate, 'is_alive', True):
- Line 154: if getattr(candidate, 'team_id', -1) == ship.team_id:
- Line 159: t_type = getattr(candidate, 'type', None)
- Line 200: t_vel = getattr(target, 'velocity', Vector2(0, 0))
## game\simulation\combat\weapon_firing_system.py
- Line 151: if not hasattr(comp, 'shots_fired'):
- Line 249: comp_facing = ship.angle + getattr(comp, 'facing_angle', 0)
## game\simulation\components\abilities\base.py
- Line 236: ability_stats = getattr(self.component, 'ability_stats', {})
- Line 243: stats = getattr(self.component, 'stats', {})
- Line 311: stats = getattr(self.component, 'stats', {})
- Line 325: base_value = getattr(self, base_attr, None)
- Line 329: current_value = getattr(self, binding.attribute_name, base_value)
- Line 370: val = getattr(cls, attr, '')
- Line 393: base = getattr(self, self.base_attr)
- Line 402: val = getattr(self, self.value_attr)
- Line 407: return float(getattr(self, self.value_attr))
## game\simulation\components\abilities\stat_keys.py
- Line 164: base_value = getattr(ability, base_attr, None)
## game\simulation\components\abilities\weapons.py
- Line 170: if not hasattr(self.component, 'facing_angle'):
- Line 258: self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))
- Line 278: self.accuracy_falloff = float(getattr(self.component, 'accuracy_falloff', 0.001))
- Line 279: self.base_accuracy = float(getattr(self.component, 'base_accuracy', 1.0))
- Line 334: self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))
- Line 335: self.endurance = float(getattr(self.component, 'endurance', 3.0))
- Line 336: self.turn_rate = float(getattr(self.component, 'turn_rate', 30.0))
- Line 337: self.to_hit_defense = float(getattr(self.component, 'to_hit_defense', 0.0))
- Line 338: self.projectile_damage = float(getattr(self.component, 'projectile_damage', 0))
- Line 339: self.projectile_hp = float(getattr(self.component, 'projectile_hp', 1.0))
- Line 340: self.projectile_stealth = float(getattr(self.component, 'projectile_stealth', 0.0))
## game\simulation\components\ability_manager.py
- Line 120: if hasattr(ab, 'tags') and 'pdc' in ab.tags:
- Line 140: if hasattr(ab, 'get_ui_rows'):
- Line 195: if hasattr(ab, 'sync_data'):
## game\simulation\components\component.py
- Line 207: if hasattr(self, '_ability_index') and ability_name in self._ability_index:
- Line 216: if hasattr(self, '_ability_index') and ability_name in self._ability_index:
- Line 226: if hasattr(self, '_ability_index') and ability_name in self._ability_index:
- Line 329: trigger = getattr(ability, 'trigger', None)
## game\simulation\components\component_resource_manager.py
- Line 51: trigger = getattr(ability, 'trigger', None)
- Line 52: check_fn = getattr(ability, 'check_available', None)
- Line 96: getattr(component, 'evaluated_resource_cost', None)
- Line 107: eval_context['ship_class_mass'] = getattr(
## game\simulation\components\component_stats_calculator.py
- Line 82: if hasattr(component, prop):
- Line 91: if hasattr(component, 'cost'):
- Line 147: eval_context['ship_class_mass'] = getattr(component.ship, 'max_mass_budget', 1000)
- Line 159: if hasattr(component, attr):
- Line 160: if isinstance(getattr(component, attr), int):
## game\simulation\components\modifier_introspection.py
- Line 141: effects = mod_def.evaluate_effects(mod_value) if hasattr(mod_def, 'evaluate_effects') else []
- Line 146: 'name': mod_def.display_name if hasattr(mod_def, 'display_name') else mod_def.id,
- Line 153: 'component_name': component.display_name if hasattr(component, 'display_name') else component.id,
- Line 155: 'total_stats': dict(component.stats) if hasattr(component, 'stats') else {},
- Line 185: summary = ability.get_effect_summary() if hasattr(ability, 'get_effect_summary') else []
- Line 271: summary = ability.get_effect_summary() if hasattr(ability, 'get_effect_summary') else []
## game\simulation\entities\ability_aggregator.py
- Line 102: ability_instances = getattr(comp, 'ability_instances', None)
- Line 124: stack_group = getattr(ab, 'stack_group', None)
- Line 139: abilities = getattr(comp, 'abilities', {})
- Line 207: instances = getattr(comp, 'ability_instances', None)
## game\simulation\entities\combat_endurance.py
- Line 43: abilities = getattr(c, 'ability_instances', [])
- Line 49: trigger = getattr(ab, 'trigger', 'constant')
- Line 50: resource_type = getattr(ab, 'resource_type', '')
- Line 51: amount = getattr(ab, 'amount', 0.0)
- Line 70: reload_t = getattr(inst, 'reload_time', 1.0)
## game\simulation\entities\projectile.py
- Line 23: self.team_id = getattr(owner, 'team_id', -1)
- Line 143: if hasattr(self.owner, 'combat_engine'):
## game\simulation\entities\ship.py
- Line 228: if not hasattr(self, '_combat_engine') or self._combat_engine is None:
- Line 576: if not getattr(comp, 'ship', None): comp.ship = self
## game\simulation\entities\ship_combat_engine.py
- Line 180: if cost_amount > 0 and hasattr(ship, 'resources'):
- Line 194: if getattr(ship, 'repair_rate', 0) > 0:
## game\simulation\entities\ship_formation.py
- Line 63: if master and hasattr(master, 'formation'):
- Line 70: if self.master and hasattr(self.master, 'formation'):
- Line 91: if hasattr(ship, 'formation'):
- Line 109: if hasattr(ship, 'formation'):
## game\simulation\entities\ship_physics.py
- Line 28: if getattr(self, 'is_thrusting', False):
- Line 34: target_v = potential_max_speed * getattr(self, 'engine_throttle', 1.0)
- Line 82: turn_per_tick = (self.turn_speed * getattr(self, 'turn_throttle', 1.0)) / 100.0
## game\simulation\entities\ship_serialization.py
- Line 67: "strategic_movement": getattr(ship, 'total_strategic_movement', 0),
- Line 70: "warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
- Line 71: "warp_energy_cost": getattr(ship, 'warp_energy_cost', 0),
## game\simulation\entities\ship_stat_querier.py
- Line 130: rng = getattr(ab, 'range', 0.0)
- Line 133: if rng <= 0 and hasattr(ab, 'projectile_speed') and hasattr(ab, 'endurance'):
## game\simulation\entities\ship_stats.py
- Line 282: abilities = getattr(comp, 'ability_instances', [])
- Line 286: res_type = getattr(ability, 'resource_type', '')
- Line 287: max_amt = getattr(ability, 'max_amount', 0.0)
- Line 296: res_type = getattr(ability, 'resource_type', '')
- Line 297: rate = getattr(ability, 'rate', 0.0)
- Line 315: tonnage = getattr(ab, 'max_tonnage', 0)
- Line 319: acc['warp_energy_cost'] += getattr(ab, 'energy_cost', 0)
- Line 344: if ab.__class__.__name__ == 'ResourceConsumption' and getattr(ab, 'resource_type', '') == ResourceType.ENERGY:
- Line 345: acc['shield_cost'] += getattr(ab, 'amount', 0.0)
- Line 496: prev_max_fuel = getattr(ship, '_prev_max_fuel', 0)
- Line 497: prev_max_ammo = getattr(ship, '_prev_max_ammo', 0)
- Line 498: prev_max_energy = getattr(ship, '_prev_max_energy', 0)
- Line 499: prev_max_shields = getattr(ship, '_prev_max_shields', 0)
- Line 506: if not getattr(ship, '_resources_initialized', False):
## game\simulation\formula_system.py
- Line 110: if hasattr(builtins, name):
- Line 111: names[name] = getattr(builtins, name)
## game\simulation\managers\battle_state_manager.py
- Line 137: if not hasattr(state, 'mode'):
- Line 139: if not hasattr(state, 'ships'):
## game\simulation\projectile_manager.py
- Line 139: if hasattr(p, 'source_weapon') and p.source_weapon:
- Line 141: if weapon_ab and hasattr(weapon_ab, 'get_damage'):
- Line 174: if hasattr(p, 'source_weapon') and p.source_weapon:
## game\simulation\systems\battle_engine.py
- Line 425: self.logger.log(f"Missile fired at {getattr(attack, 'target', 'unknown')}")
## game\simulation\validation\ship_validator.py
- Line 362: capacity = getattr(ab, 'max_amount', 0)
## game\strategy\data\design_metadata.py
- Line 156: vehicle_type=getattr(ship, 'vehicle_type', 'Ship'),
- Line 164: theme_id=getattr(ship, 'theme_id', '')
- Line 210: if getattr(comp, 'major_classification', None) == 'Weapons':
- Line 213: if hasattr(comp, 'get_abilities'):
- Line 218: damage = getattr(weapon, 'damage', 0)
- Line 219: reload_time = getattr(weapon, 'reload_time', 1.0)
- Line 226: if getattr(comp, 'major_classification', None) == 'Armor':
- Line 227: power += getattr(comp, 'max_hp', 0) * 0.5
## game\strategy\data\fleet.py
- Line 81: elif self.type == OrderType.IMPLODE_PLANET and hasattr(self.target, 'id'):
- Line 93: elif hasattr(self.target, 'to_dict'):
- Line 95: elif hasattr(self.target, 'id'):
## game\strategy\data\galaxy_entity_registry.py
- Line 56: if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
- Line 82: if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
- Line 111: if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
- Line 161: if not hasattr(obj, 'occupied_hexes'):
- Line 180: if not hasattr(obj, 'occupied_hexes'):
## game\strategy\data\galaxy_spatial_index.py
- Line 49: if not hasattr(obj, 'location'):
- Line 164: if hasattr(star, 'location'):
- Line 167: if hasattr(star, 'occupied_hexes'):
- Line 173: diameter = getattr(planet, 'diameter_hexes', 0)
## game\strategy\data\pathfinding.py
- Line 318: getattr(chaser, 'id', 'unknown'),
- Line 416: f"target={getattr(target_fleet, 'id', '?')} @ {target_fleet.location}")
## game\strategy\data\planet.py
- Line 93: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\strategy\data\race_config.py
- Line 336: if not (lo <= getattr(self, attr) <= hi):
- Line 359: value = getattr(self, attr)
## game\strategy\engine\command_handlers.py
- Line 300: turn_engine = getattr(session, 'turn_engine', None)
- Line 302: registries = getattr(turn_engine, '_registries', None)
- Line 304: component_registry = getattr(registries, 'components', None)
- Line 445: logger.info(f"DIAG TransferCommandHandler: validation result is_valid={result.is_valid}, errors={result.errors}, error_code={getattr(result, 'error_code', None)}")
## game\strategy\engine\empire_economy_calculator.py
- Line 128: resource_pool = getattr(empire, 'resource_pool', {})
- Line 129: max_storage = getattr(empire, 'max_storage', {})
- Line 150: colonies = getattr(empire, 'colonies', [])
- Line 152: facilities = getattr(colony, 'facilities', [])
- Line 155: if not getattr(facility, 'is_operational', True):
- Line 158: design_data = getattr(facility, 'design_data', {})
- Line 178: planet_resources = getattr(colony, 'resources', {})
- Line 203: colonies = getattr(empire, 'colonies', [])
- Line 205: facilities = getattr(colony, 'facilities', [])
- Line 208: if not getattr(facility, 'is_operational', True):
- Line 211: design_data = getattr(facility, 'design_data', {})
- Line 218: fleets = getattr(empire, 'fleets', [])
- Line 220: ships = getattr(fleet, 'ships', [])
- Line 222: design_data = getattr(ship, 'design_data', {})
## game\strategy\engine\fleet_order_processor.py
- Line 149: if not target_fleet or not hasattr(target_fleet, 'location'):
- Line 222: if hasattr(candidate, 'planet_type'):
- Line 280: planet_id=getattr(final_planet, 'id', None),
- Line 335: for emp in getattr(galaxy, 'empires', []): # This depends on how galaxy is structured
- Line 544: race_config = getattr(empire, 'race_config', None)
- Line 548: and hasattr(race_config, 'race_id')
- Line 549: and isinstance(getattr(race_config, 'race_id', None), str)
- Line 694: if target_fleet and hasattr(target_fleet, 'location'):
## game\strategy\engine\game_session.py
- Line 118: cat_value = category.value if hasattr(category, 'value') else category
- Line 119: etype_value = event_type.value if hasattr(event_type, 'value') else event_type
- Line 172: can_warp = fleet.can_use_warp() if hasattr(fleet, 'can_use_warp') else 'N/A'
## game\strategy\engine\harvesting_engine.py
- Line 74: abilities = getattr(comp_def, 'abilities', {}) or {}
- Line 144: colonies = getattr(empire, 'colonies', [])
- Line 146: facilities = getattr(colony, 'facilities', [])
- Line 148: if not getattr(facility, 'is_operational', True):
- Line 159: design_data = getattr(facility, 'design_data', {})
- Line 213: abilities = getattr(comp_def, 'abilities', {}) or {}
- Line 226: colonies = getattr(empire, 'colonies', [])
- Line 238: facilities = getattr(colony, 'facilities', [])
- Line 240: if not getattr(facility, 'is_operational', True):
- Line 259: design_data = getattr(facility, 'design_data', {})
- Line 322: planet_resources = getattr(colony, 'resources', {})
- Line 345: f"{getattr(colony, 'name', 'unknown')} (quality={quality:.2f}, "
## game\strategy\engine\population_engine.py
- Line 52: colonies = getattr(empire, 'colonies', [])
- Line 64: populations = getattr(colony, 'populations', [])
- Line 95: max_pop = getattr(colony, 'max_population', 0)
- Line 103: aptitude = getattr(race_config, 'aptitude_population_growth', 50)
- Line 141: race_config = getattr(empire, 'race_config', None)
- Line 146: if getattr(race_config, 'race_id', '') == race_id:
## game\strategy\engine\resource_management_engine.py
- Line 141: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\strategy\engine\resupply_engine.py
- Line 159: abilities = getattr(comp_def, 'abilities', {}) or {}
## game\strategy\engine\superweapon_order_processor.py
- Line 97: if hasattr(target_planet, 'owner_id') and target_planet.owner_id is not None:
- Line 99: if hasattr(empire, 'colonies') and target_planet in empire.colonies:
- Line 119: empire_id=getattr(empire, 'id', 0),
- Line 121: planet_id=getattr(target_planet, 'id', None),
- Line 172: if hasattr(planet, 'owner_id') and planet.owner_id is not None:
- Line 174: if hasattr(emp, 'colonies') and planet in emp.colonies:
- Line 182: if hasattr(galaxy, 'unregister_fleet'):
- Line 194: empire_id=getattr(empire, 'id', 0),
- Line 297: empire_id=getattr(empire, 'id', 0),
- Line 372: empire_id=getattr(empire, 'id', 0),
- Line 423: star_loc = getattr(primary_star, 'location', HexCoord(0, 0))
- Line 445: if hasattr(planet, 'owner_id') and planet.owner_id is not None:
- Line 446: if hasattr(empire, 'colonies') and planet in empire.colonies:
- Line 454: race = getattr(empire, 'race_config', None) if empire else None
- Line 511: empire_id=getattr(empire, 'id', 0),
- Line 563: name = getattr(ship, 'name', None)
- Line 580: empire_id=getattr(empire, 'id', 0),
## game\strategy\engine\turn_engine.py
- Line 312: component_registry = getattr(self._registries, 'components', None)
- Line 374: component_registry=getattr(self._registries, 'components', None),
## game\strategy\facade\dto\fleet_dto.py
- Line 128: elif hasattr(order.target, "name"):
- Line 131: if hasattr(order.target, "location"):
- Line 135: if hasattr(order.target, "id"):
## game\strategy\services\action_time_resolver.py
- Line 122: design_data = getattr(ship, 'design_data', {})
## game\strategy\services\cargo_transfer_service.py
- Line 40: if not planets and hasattr(fleet, 'location') and fleet.location:
- Line 70: passengers = getattr(fleet_info, 'passengers_current', 0)
- Line 100: if hasattr(planet_info, 'population_details') and planet_info.population_details:
- Line 112: pop = getattr(planet_info, 'total_population', 0)
- Line 139: if hasattr(obj_info, 'passengers_current'):
- Line 140: passengers = getattr(obj_info, 'passengers_current', 0)
- Line 149: elif hasattr(obj_info, 'population_details') and obj_info.population_details:
- Line 159: elif hasattr(obj_info, 'total_population'):
- Line 160: passengers = getattr(obj_info, 'total_population', 0)
## game\strategy\services\component_inspector.py
- Line 38: return getattr(comp_def, 'abilities', {})
- Line 107: design_data = getattr(ship, 'design_data', {})
- Line 154: design_data = getattr(ship, 'design_data', {})
## game\strategy\services\fleet_navigation_service.py
- Line 151: if not target_fleet or not hasattr(target_fleet, 'location'):
- Line 454: first_order_progress = getattr(fleet.orders[0], 'execution_progress', 0)
- Line 636: if not target_fleet or not hasattr(target_fleet, 'location'):
## game\strategy\services\ship_stats_calculator.py
- Line 192: abilities = getattr(comp_def, 'abilities', {}) or {}
- Line 331: comp_type = getattr(comp_def, 'type_str', '')
- Line 339: abilities = getattr(comp_def, 'abilities', {}) or {}
- Line 358: threshold = getattr(comp_def, 'damage_threshold', DEFAULT_DAMAGE_THRESHOLD)
- Line 465: val = getattr(obj, attr, default)
## game\strategy\validation\colonize_validator.py
- Line 29: design_data = getattr(ship, 'design_data', {})
- Line 88: if hasattr(galaxy, 'get_zones_at_global_hex'):
- Line 92: if hasattr(zone_obj, 'planet_type') and zone_obj not in all_planets_at_hex:
- Line 117: if hasattr(candidate, 'planet_type'):
- Line 244: for order in getattr(fleet, 'orders', []):
- Line 248: if hasattr(target, 'planet_type'):
## game\strategy\validation\superweapon_validator.py
- Line 97: if not getattr(system, 'stars', []):
- Line 139: for wp in getattr(current_system, 'warp_points', []):
- Line 178: for wp in getattr(current_system, 'warp_points', []):
- Line 220: if not getattr(current_system, 'stars', []):
## game\ui\components\table\header.py
- Line 131: if hasattr(el, "col_ref") and hasattr(el, "direction"):
- Line 135: elif hasattr(el, "sort_col_ref"):
## game\ui\panels\battle_panels.py
- Line 37: ui_service = getattr(self.scene, 'ui_service', None)
- Line 48: return getattr(self.scene, 'ships', [])
- Line 70: ship_id = getattr(ship, 'id', None)
- Line 74: ship_name = getattr(ship, 'name', None)
- Line 115: team1_alive = sum(1 for s in team1_ships if s.is_alive and not getattr(s, 'is_derelict', False))
- Line 128: team2_alive = sum(1 for s in team2_ships if s.is_alive and not getattr(s, 'is_derelict', False))
- Line 149: elif getattr(ship, 'is_derelict', False):
- Line 155: elif getattr(ship, 'is_derelict', False):
- Line 274: proj_id = getattr(proj, 'id', None)
- Line 352: status = getattr(proj, 'status', 'active')
- Line 400: max_speed = getattr(proj, 'max_speed', p_vel_len) * 100.0 if getattr(proj, 'max_speed', 0) > 0 else p_vel_len
- Line 406: hp = getattr(proj, 'hp', 0)
- Line 407: max_hp = getattr(proj, 'max_hp', hp) if getattr(proj, 'max_hp', 0) > 0 else max(hp, 1)
- Line 417: endurance = getattr(proj, 'endurance', 0)
- Line 418: max_endurance = getattr(proj, 'max_endurance', endurance) if getattr(proj, 'max_endurance', 0) > 0 else max(endurance, 1)
- Line 433: target = getattr(proj, 'target', None)
- Line 434: t_name = target.name if target and hasattr(target, 'name') else "None"
- Line 489: team1_alive = sum(1 for s in ships if s.team_id == 0 and s.is_alive and not getattr(s, 'is_derelict', False))
- Line 490: team2_alive = sum(1 for s in ships if s.team_id == 1 and s.is_alive and not getattr(s, 'is_derelict', False))
- Line 495: if hasattr(self.scene, 'test_mode') and self.scene.test_mode:
- Line 497: is_over = self.scene.is_battle_over() if hasattr(self.scene, 'is_battle_over') else False
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
## game\ui\panels\design_report_panel.py
- Line 102: if hasattr(self, 'name_label'):
- Line 104: if hasattr(self, 'type_class_label'):
- Line 143: vehicle_type = getattr(ship, 'vehicle_type', 'Unknown')
- Line 144: ship_class = getattr(ship, 'ship_class', 'Unknown')
- Line 183: theme = getattr(ship, 'theme_id', 'Federation')
- Line 184: ship_class = getattr(ship, 'ship_class', 'Unknown')
- Line 287: if hasattr(self, 'panel'):
## game\ui\panels\design_stats_panel.py
- Line 329: if hasattr(row, 'definition'):
## game\ui\panels\modifier_impact_grid.py
- Line 165: if not hasattr(component, 'ability_instances') or not component.ability_instances:
- Line 172: if hasattr(ability_class, 'STAT_BINDINGS'):
- Line 438: if hasattr(self, '_stat_summary'):
## game\ui\panels\planet_report_panel.py
- Line 203: if hasattr(self.planet, 'planet_type'):
- Line 263: if not hasattr(self.planet, 'facilities') or not self.planet.facilities:
- Line 339: planet_resources = getattr(self.planet, 'resources', {}) or {}
- Line 442: if hasattr(self, 'resource_panel') and self.resource_panel:
- Line 446: if hasattr(self, 'panel'):
- Line 465: if getattr(planet, 'owner_id', None) is None:
- Line 478: for facility in getattr(planet, 'facilities', []):
- Line 479: if not getattr(facility, 'is_operational', True):
- Line 481: design_data = getattr(facility, 'design_data', {})
- Line 491: planet_resources = getattr(planet, 'resources', {})
- Line 510: abilities = getattr(comp_def, 'abilities', {}) or {}
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
- Line 61: status = getattr(comp, 'status', ComponentStatus.ACTIVE)
- Line 112: if not hasattr(ship, 'resources') or not ship.resources:
- Line 152: if not comp.is_active and getattr(comp, 'status', ComponentStatus.ACTIVE) != ComponentStatus.ACTIVE:
- Line 178: stats_str = f"S:{getattr(comp, 'shots_fired', 0)} H:{getattr(comp, 'shots_hit', 0)}"
- Line 239: if hasattr(ship, 'source_file') and ship.source_file:
- Line 310: crew_req = getattr(ship, 'crew_required', 0)
- Line 311: crew_cur = getattr(ship, 'crew_onboard', 0)
- Line 322: target_name = getattr(ship.current_target, 'name', getattr(ship.current_target, 'type', 'Target').title())
- Line 328: sec_targets = getattr(ship, 'secondary_targets', [])
- Line 332: st_name = getattr(st, 'name', getattr(st, 'type', 'Target').title())
- Line 338: max_targets = getattr(ship, 'max_targets', CombatConstants.DEFAULT_MAX_TARGETS)
## game\ui\panels\strategy_widgets.py
- Line 33: if not hasattr(star, 'spectrum'):
- Line 42: val = getattr(s, attr, 0.0)
- Line 114: if not hasattr(planet, 'atmosphere') or not planet.atmosphere:
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
- Line 444: if not hasattr(self.test_scenario, 'results') or not self.test_scenario.results:
- Line 554: color = getattr(p, 'color', (255, 200, 50))
- Line 556: pygame.draw.circle(screen, (255, 255, 100), (int(end[0]), int(end[1])), int(getattr(p, 'radius', 4)))
- Line 641: if hasattr(self.ui, 'print_headless_summary'):
## game\ui\screens\battle_ui.py
- Line 43: if getattr(proj, 'type', None) == AttackType.MISSILE:
- Line 183: if hasattr(s, 'aim_point') and s.aim_point:
- Line 256: if hasattr(self.scene, 'test_scenario') and self.scene.test_scenario:
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
## game\ui\screens\builder\components.py
- Line 84: budget = getattr(ship_context, 'base_mass', 1000)
- Line 85: if hasattr(ship_context, 'max_mass_budget'):
- Line 87: elif hasattr(ship_context, 'base_mass'):
- Line 123: if hasattr(ab, 'base_accuracy'):
- Line 125: if hasattr(ab, 'reload_time'):
## game\ui\screens\builder\detail_panel.py
- Line 94: elif hasattr(selection_data, 'id'):
- Line 144: if hasattr(comp, 'get_ui_rows'):
## game\ui\screens\builder\grouping_strategies.py
- Line 42: if getattr(m.definition, 'readonly', False):
## game\ui\screens\builder\interaction_controller.py
- Line 146: if hasattr(self.builder.left_panel, 'get_add_count'):
- Line 152: if hasattr(target, 'suppress_toggle'):
## game\ui\screens\builder\layer_panel.py
- Line 349: if hasattr(item, 'handle_event'):
- Line 377: if getattr(item, 'is_selected', False):
## game\ui\screens\builder\left_panel.py
- Line 214: return getattr(self, '_dropdown_expanded', False)
- Line 254: v_type = getattr(self.builder.ship, 'vehicle_type', "Ship")
- Line 352: if getattr(item, 'is_hovered', False) and item != self.selected_item:
## game\ui\screens\builder\modifier_row.py
- Line 177: if hasattr(self.slider, 'enable_arrow_buttons'):
- Line 269: if not hasattr(event, 'ui_element'):
## game\ui\screens\builder\right_panel.py
- Line 56: if hasattr(self, 'stats_panel') and self.stats_panel.needs_rebuild(ship):
- Line 79: curr_theme = getattr(self.builder.ship, 'theme_id', 'Federation')
- Line 91: curr_type = getattr(self.builder.ship, 'vehicle_type', "Ship")
- Line 172: curr_theme = getattr(s, 'theme_id', 'Federation')
- Line 181: curr_type = getattr(s, 'vehicle_type', "Ship")
- Line 241: theme = getattr(self.builder.ship, 'theme_id', 'Federation')
- Line 332: if hasattr(self, 'stats_panel'):
## game\ui\screens\builder\schematic_view.py
- Line 70: theme_id = getattr(ship, 'theme_id', 'Federation')
## game\ui\screens\builder\stats_config.py
- Line 29: return getattr(ship, self.getter, 0)
- Line 30: return getattr(ship, self.attr_key, 0)
- Line 111: return getattr(ship, 'max_targets', 1)
- Line 124: return getattr(ship, 'total_maneuver_points', 0)
- Line 133: mass = getattr(ship, 'mass', 0)
- Line 134: movement_points = getattr(ship, 'total_strategic_movement', 0)
- Line 143: return getattr(ship, 'fuel_consumption', 0)
- Line 146: return getattr(ship, 'ammo_consumption', 0)
- Line 149: return getattr(ship, 'energy_consumption', 0)
- Line 176: if hasattr(ship, attr_name):
- Line 177: val = getattr(ship, attr_name, 0)
- Line 187: if hasattr(comp, 'ability_instances'):
- Line 221: if attr and hasattr(ship, attr):
- Line 222: return getattr(ship, attr, 0)
- Line 232: return getattr(ship, attr, 0)
- Line 362: if hasattr(comp, 'ability_instances'):
- Line 406: if hasattr(ship, f'{res}{attr_suffix}'):
- Line 407: val = getattr(ship, f'{res}{attr_suffix}', 0)
- Line 570: if hasattr(ship, 'resources'):
- Line 603: return ship.construction_cost.get(r, 0) if hasattr(ship, 'construction_cost') else 0
## game\ui\screens\builder\structure_list_items.py
- Line 434: if getattr(self.event_handler, 'toggle_suppress_timer', 0) > 0:
## game\ui\screens\builder\weapons_viewmodel.py
- Line 147: self._target_defense_mod = getattr(ship, 'total_defense_score', 0.0)
- Line 297: base_acc = getattr(ab, 'base_accuracy', 2.0)
- Line 298: falloff = getattr(ab, 'accuracy_falloff', 0.001)
- Line 304: if hasattr(ship, 'get_total_sensor_score'):
- Line 378: base_acc = getattr(ab, 'base_accuracy', 2.0) if is_beam else None
- Line 379: falloff = getattr(ab, 'accuracy_falloff', 0.001) if is_beam else None
- Line 383: if hasattr(ship, 'get_total_sensor_score'):
- Line 396: if hasattr(ab, 'get_damage'):
- Line 470: base_acc = getattr(ab, 'base_accuracy', 1.0)
- Line 471: falloff = getattr(ab, 'accuracy_falloff', 0.0)
- Line 474: if hasattr(ship, 'get_total_sensor_score'):
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
## game\ui\screens\empire_panel_window.py
- Line 213: race_config = getattr(self.empire, 'race_config', None)
- Line 277: portrait_id = getattr(self.empire, 'portrait_id', None) or getattr(race_config, 'portrait_id', None)
- Line 290: flag_id = getattr(self.empire, 'flag_id', None) or getattr(race_config, 'flag_id', None)
- Line 319: ("Faction Name", getattr(race_config, 'faction_name', '')),
- Line 320: ("Race Name", getattr(race_config, 'race_name', '')),
- Line 321: ("Government Type", getattr(race_config, 'government_type', '')),
- Line 322: ("Government Organization", getattr(race_config, 'government_organization', '')),
- Line 323: ("Leader", f"{getattr(race_config, 'leader_title', '')} {getattr(race_config, 'leader_name', '')}".strip()),
- Line 324: ("Physical Type", getattr(race_config, 'physical_type', '')),
- Line 325: ("Society Type", getattr(race_config, 'society_type', '')),
- Line 354: ("Strength", getattr(race_config, 'aptitude_strength', 50)),
- Line 355: ("Intelligence", getattr(race_config, 'aptitude_intelligence', 50)),
- Line 356: ("Constitution", getattr(race_config, 'aptitude_constitution', 50)),
- Line 357: ("Dexterity", getattr(race_config, 'aptitude_dexterity', 50)),
- Line 358: ("Species Tolerance", getattr(race_config, 'aptitude_tolerance_other_species', 50)),
- Line 359: ("Cooperation", getattr(race_config, 'aptitude_cooperation', 50)),
- Line 360: ("Happiness", getattr(race_config, 'aptitude_happiness', 50)),
- Line 361: ("Pop Growth", getattr(race_config, 'aptitude_population_growth', 50)),
- Line 362: ("Conflict Tolerance", getattr(race_config, 'aptitude_conflict_tolerance', 50)),
- Line 399: gravity_ideal = getattr(race_config, 'gravity_ideal', 1.0)
- Line 400: gravity_tol = getattr(race_config, 'gravity_tolerance', 0.3)
- Line 401: temp_ideal = getattr(race_config, 'temperature_ideal', 293.0)
- Line 402: temp_tol = getattr(race_config, 'temperature_tolerance', 50.0)
- Line 403: water_ideal = getattr(race_config, 'water_ideal', 0.5)
- Line 404: water_tol = getattr(race_config, 'water_tolerance', 0.2)
- Line 405: radiation = getattr(race_config, 'radiation_tolerance', 0.0)
- Line 433: bio = getattr(race_config, 'bio_description', '')
- Line 434: socio = getattr(race_config, 'socio_description', '')
## game\ui\screens\event_log_window.py
- Line 231: if hasattr(event, "type") and event.type == pygame_gui.UI_BUTTON_PRESSED:
- Line 232: clicked = getattr(event, "ui_element", None)
## game\ui\screens\fleet_orders_window.py
- Line 92: if hasattr(element, 'kill'):
- Line 167: if hasattr(t, 'q') and hasattr(t, 'r'):
- Line 172: p_name = order.target.name if hasattr(order.target, 'name') else "Unknown"
- Line 175: f_id = order.target.id if hasattr(order.target, 'id') else "?"
- Line 178: f_id = order.target.id if hasattr(order.target, 'id') else "?"
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
- Line 517: color = star.color if hasattr(star, 'color') else (255, 255, 200)
## game\ui\screens\keybindings_scene.py
- Line 61: if attr.startswith("K_") and isinstance(getattr(pygame, attr), int):
- Line 62: _PYGAME_KEY_NAMES[getattr(pygame, attr)] = attr
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
## game\ui\screens\planet_selection_window.py
- Line 131: if hasattr(planet, 'image_id') and planet.image_id:
- Line 135: if portrait_surface and hasattr(planet, 'image_rotation') and planet.image_rotation:
## game\ui\screens\race_asset_loader.py
- Line 269: if hasattr(empire, 'empire_theme_id') and empire.empire_theme_id:
- Line 274: if hasattr(empire, 'flag_id') and empire.flag_id:
## game\ui\screens\race_setup_screen.py
- Line 384: if hasattr(self, '_ship_preview_elements'):
- Line 389: if not hasattr(self, 'ship_preview_scroll'):
- Line 889: elif hasattr(self, 'btn_load') and self.btn_load and event.ui_element == self.btn_load:
## game\ui\screens\strategy_build_queue_manager.py
- Line 43: if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
- Line 62: savegame_path = getattr(self._screen.session, 'save_path', None)
- Line 96: queue_sources = getattr(self._screen.build_queue_screen, 'queue_sources', [])
- Line 101: fleet_id = getattr(fleet, 'id', id(fleet))
- Line 154: if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
- Line 177: savegame_path = getattr(self._screen.session, 'save_path', None)
- Line 201: if hasattr(self._screen, 'build_queue_screen') and self._screen.build_queue_screen is not None:
- Line 220: savegame_path = getattr(self._screen.session, 'save_path', None)
## game\ui\screens\strategy_camera_nav.py
- Line 70: if hasattr(obj, 'location'):
- Line 72: if hasattr(obj, 'planet_type'):
- Line 77: elif hasattr(obj, 'ships'):
- Line 80: elif hasattr(obj, 'global_location'):
- Line 140: elif hasattr(self.scene.selected_object, 'location'):
## game\ui\screens\strategy_click_dispatcher.py
- Line 524: if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
## game\ui\screens\strategy_colonization.py
- Line 81: if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
- Line 82: zone_lookup = getattr(self.scene.galaxy, 'get_zones_at_global_hex', None)
- Line 87: if hasattr(zone_obj, 'planet_type') and zone_obj not in potential_planets:
- Line 195: if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
- Line 196: zone_lookup = getattr(self.scene.galaxy, 'get_zones_at_global_hex', None)
- Line 201: if hasattr(zone_obj, 'planet_type') and zone_obj not in candidates:
- Line 202: if getattr(zone_obj, 'owner_id', None) is None:
## game\ui\screens\strategy_detail_fmt.py
- Line 92: if hasattr(planet, 'owner_id') and planet.owner_id is not None:
- Line 96: populations = getattr(planet, 'populations', [])
- Line 98: max_pop = getattr(planet, 'max_population', 0)
- Line 137: facilities = getattr(planet, 'facilities', [])
- Line 141: f_name = getattr(facility, 'name', getattr(facility, 'design_id', 'Unknown'))
- Line 142: f_status = getattr(facility, 'status', 'Active')
- Line 213: data = getattr(ship, 'design_data', None) or {}
- Line 251: for cargo_type, amount in getattr(ship, 'cargo_contents', {}).items():
- Line 290: p_name = getattr(order.target, 'name', 'Unknown')
- Line 293: queue = getattr(fleet, 'construction_queue', [])
## game\ui\screens\strategy_detail_formatter.py
- Line 207: if hasattr(self.scene, 'current_empire'):
- Line 342: if hasattr(self.scene, 'turn_engine'):
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
- Line 127: if getattr(self.scene, 'input_mode', 'SELECT') == 'MOVE' and self.scene.selected_fleet:
- Line 519: diameter_hexes = getattr(planet, 'diameter_hexes', 11.0)
## game\ui\screens\strategy_screen.py
- Line 202: if hasattr(self, 'build_queue_screen') and self.build_queue_screen is not None:
- Line 292: elif hasattr(obj, 'location'):
- Line 335: 'empire': self.session.player_empire if hasattr(self, 'session') else None,
- Line 336: 'game_session': self.session if hasattr(self, 'session') else None
## game\ui\screens\strategy_superweapons.py
- Line 374: if hasattr(self.scene.ui, 'show_confirmation_dialog'):
- Line 390: if hasattr(self.scene.ui, 'show_system_picker'):
- Line 407: if hasattr(self.scene.ui, 'show_ship_picker'):
## game\ui\screens\strategy_ui.py
- Line 210: if hasattr(self, 'system_tree'):
- Line 212: if hasattr(self, 'sector_tree'):
- Line 255: if hasattr(self.scene, '_get_object_asset'):
- Line 284: if not hasattr(self.scene, 'current_empire'):
## game\ui\screens\strategy_window_manager.py
- Line 202: if hasattr(self.scene, "facade")
## game\ui\screens\test_lab\data_extractor.py
- Line 120: if hasattr(scenario_cls, 'ship_file') and scenario_cls.ship_file:
## game\ui\screens\test_lab\dialogs.py
- Line 60: if hasattr(self, 'close_button') and self.close_button:
- Line 193: if hasattr(self, 'confirm_button') and self.confirm_button:
- Line 195: if hasattr(self, 'cancel_button') and self.cancel_button:
## game\ui\screens\test_lab\screen.py
- Line 63: self.screen_width = game.screen.get_width() if hasattr(game, 'screen') else WIDTH
- Line 64: self.screen_height = game.screen.get_height() if hasattr(game, 'screen') else HEIGHT
- Line 330: if self.selected_test_id and hasattr(self.game.battle_scene, 'test_scenario'):
- Line 335: if not hasattr(scenario, 'results') or scenario.results is None:
- Line 340: scenario.results['passed'] = getattr(scenario, 'passed', False)
- Line 355: if hasattr(self.game.battle_scene, 'test_completed'):
- Line 357: if hasattr(self.game.battle_scene, 'test_scenario'):
- Line 367: if hasattr(self.game, 'menu_screen') and hasattr(self.game.menu_screen, 'create_particles'):
- Line 578: if event.type == pygame_gui.UI_BUTTON_PRESSED and hasattr(event, 'ui_element'):
## game\ui\screens\transfer_dialog.py
- Line 158: if hasattr(self, 'lbl_debug'):
## game\ui\screens\workshop_event_router.py
- Line 76: if hasattr(gui, 'component_modifier_grid_panel'):
- Line 307: elif hasattr(gui, 'hull_toggle_btn') and event.ui_element == gui.hull_toggle_btn:
- Line 313: elif hasattr(gui, 'std_data_btn') and event.ui_element == gui.std_data_btn:
- Line 315: elif hasattr(gui, 'test_data_btn') and event.ui_element == gui.test_data_btn:
- Line 317: elif hasattr(gui, 'select_data_btn') and event.ui_element == gui.select_data_btn:
- Line 319: elif hasattr(gui, 'verbose_btn') and event.ui_element == gui.verbose_btn:
- Line 334: elif hasattr(gui, 'right_panel') and hasattr(gui.right_panel, 'vehicle_type_dropdown') and event.ui_element == gui.right_panel.vehicle_type_dropdown:
- Line 336: elif hasattr(gui.right_panel, 'theme_dropdown') and event.ui_element == gui.right_panel.theme_dropdown:
- Line 375: if new_type == getattr(gui.ship, 'vehicle_type', "Ship"):
## game\ui\screens\workshop_screen.py
- Line 399: if hasattr(self, 'pending_action') and self.pending_action:
- Line 439: if hasattr(self.modifier_panel, 'update'):
- Line 483: if not hovered and hasattr(self, 'weapons_report_panel'):
- Line 597: if hasattr(self, 'weapons_report_panel'):
- Line 612: if hasattr(self, 'ui_manager') and self.ui_manager:
## game\ui\screens\workshop_ship_io.py
- Line 100: built_designs = getattr(self.context, 'built_designs', set())
## game\ui\screens\workshop_viewmodel.py
- Line 166: elif hasattr(item, 'id'):  # It's a component
## game\ui\services\battle_factories.py
- Line 133: max_ticks=scenario.max_ticks if hasattr(scenario, 'max_ticks') else 100000,
## game\ui\services\battle_ui_service.py
- Line 169: if ship.current_target and hasattr(ship.current_target, 'name'):
- Line 175: if hasattr(target, 'name'):
- Line 179: ship_id = str(getattr(ship, 'id', id(ship)))
- Line 204: crew_onboard=getattr(ship, 'crew_onboard', 0),
- Line 205: crew_required=getattr(ship, 'crew_required', 0),
- Line 227: if hasattr(comp, 'status') and hasattr(comp.status, 'name'):
- Line 232: if hasattr(comp, 'has_ability'):
- Line 243: shots_fired=getattr(comp, 'shots_fired', 0),
- Line 244: shots_hit=getattr(comp, 'shots_hit', 0)
- Line 258: target = getattr(proj, 'target', None)
- Line 259: if target and hasattr(target, 'name'):
- Line 263: proj_id = str(getattr(proj, 'id', id(proj)))
- Line 266: proj_type = getattr(proj, 'type', None)
- Line 274: radius=getattr(proj, 'radius', 4.0),
- Line 276: hp=getattr(proj, 'hp', 0.0),
- Line 277: max_hp=getattr(proj, 'max_hp', 0.0),
- Line 278: status=getattr(proj, 'status', 'active'),
- Line 279: endurance=getattr(proj, 'endurance', 0.0),
- Line 280: max_endurance=getattr(proj, 'max_endurance', 0.0),
- Line 282: max_speed=getattr(proj, 'max_speed', 0.0)
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
