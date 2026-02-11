# Phase 2: Simulation Layer - CRITICAL + MAJOR

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-110 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add unit tests for all Simulation layer CRITICAL and MAJOR coverage gaps (TCG-SIM-001 through TCG-SIM-009). Expected: ~80 new tests.

---

## Tasks

### Task 2.1: Registry Loader Service Tests (TCG-SIM-001) [Medium]
**File:** `tests/unit/simulation/services/test_registry_loader.py` (NEW)
**Source:** `game/simulation/services/registry_loader.py` (124 LOC)
**Tests:** `pytest tests/unit/simulation/services/test_registry_loader.py`

Note: Uses `unittest.mock.patch` for load_modifiers, load_components, load_vehicle_classes.

- [ ] `test_reload_nonexistent_directory_returns_false` - Non-existent dir returns False
- [ ] `test_reload_clears_all_registries` - components, modifiers, vehicle_classes all cleared
- [ ] `test_reload_loads_modifiers_first` - Modifiers loaded before components
- [ ] `test_reload_loads_components` - load_components called with correct path
- [ ] `test_reload_loads_vehicle_classes` - load_vehicle_classes called
- [ ] `test_reload_with_layers_file` - Passes layers_file_path when vehiclelayers.json exists
- [ ] `test_reload_test_prefix_fallback` - test_components.json preferred over components.json
- [ ] `test_reload_missing_modifiers_file_continues` - No crash if modifiers.json absent
- [ ] `test_reload_missing_components_file_continues` - No crash if components.json absent
- [ ] `test_reload_returns_true_even_if_some_files_missing` - True if dir exists
- [ ] `test_reload_frozen_registry_raises` - FrozenStateException when frozen
- [ ] `test_reload_component_load_error_logged` - JSONDecodeError in components logged, not raised
- [ ] `test_reload_modifier_load_error_logged` - TypeError in modifiers logged, not raised

**Estimated tests: ~13**

---

### Task 2.2: Physics Constants Tests (TCG-SIM-002) [Simple]
**File:** `tests/unit/simulation/test_physics_constants.py` (NEW)
**Source:** `game/simulation/physics_constants.py` (30 LOC)
**Tests:** `pytest tests/unit/simulation/test_physics_constants.py`

- [ ] `test_k_speed_is_positive_int` - K_SPEED > 0 and isinstance int
- [ ] `test_k_thrust_is_positive_int` - K_THRUST > 0
- [ ] `test_k_turn_is_positive_int` - K_TURN > 0
- [ ] `test_speed_formula_known_values` - (100 thrust * 25) / 50 mass = 50 speed
- [ ] `test_acceleration_formula_known_values` - (100 thrust * 2500) / (50^2) = 100 accel
- [ ] `test_turn_formula_known_values` - (10 raw * 25000) / (50^1.5) = known value
- [ ] `test_speed_inverse_mass_scaling` - Double mass halves speed
- [ ] `test_turn_heavier_ships_turn_slower` - Higher mass = lower turn speed

**Estimated tests: ~8**

---

### Task 2.3: Battle Configuration Tests (TCG-SIM-003) [Simple]
**File:** `tests/unit/simulation/test_battle_config.py` (NEW)
**Source:** `game/simulation/battle_config.py` (54 LOC)
**Tests:** `pytest tests/unit/simulation/test_battle_config.py`

BattleMode enum:
- [ ] `test_battle_mode_manual` - BattleMode.MANUAL.value == "manual"
- [ ] `test_battle_mode_test` - BattleMode.TEST.value == "test"
- [ ] `test_battle_mode_strategy` - BattleMode.STRATEGY.value == "strategy"
- [ ] `test_battle_mode_hypothetical` - BattleMode.HYPOTHETICAL.value == "hypothetical"
- [ ] `test_battle_mode_all_unique` - All values are distinct

BattleConfig:
- [ ] `test_default_mode_is_manual` - Default mode = MANUAL
- [ ] `test_default_max_ticks` - Default max_ticks matches SimulationConstants
- [ ] `test_default_headless_false` - headless defaults to False
- [ ] `test_default_logging_enabled` - enable_logging defaults to True
- [ ] `test_default_no_retreat` - allow_retreat defaults to False
- [ ] `test_hypothetical_mode_isolated` - isolated defaults to True
- [ ] `test_custom_seed` - Seed can be set to specific int
- [ ] `test_custom_max_ticks` - max_ticks can be overridden
- [ ] `test_map_bounds_default` - Default map_bounds tuple has 4 elements

**Estimated tests: ~14**

---

### Task 2.4: Component Constants Tests (TCG-SIM-004) [Simple]
**File:** `tests/unit/simulation/components/test_component_constants.py` (NEW)
**Source:** `game/simulation/components/component_constants.py` (69 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_component_constants.py`

ComponentStatus enum:
- [ ] `test_component_status_active` - ACTIVE is defined
- [ ] `test_component_status_damaged` - DAMAGED is defined
- [ ] `test_component_status_no_crew` - NO_CREW is defined
- [ ] `test_component_status_no_power` - NO_POWER is defined
- [ ] `test_component_status_no_fuel` - NO_FUEL is defined
- [ ] `test_component_status_no_ammo` - NO_AMMO is defined
- [ ] `test_component_status_all_unique` - All enum values are distinct

Modifier class:
- [ ] `test_modifier_init_minimal` - Modifier({'id': 'test', 'effects': []}) works
- [ ] `test_modifier_init_all_fields` - Name, description, restrictions, readonly parsed
- [ ] `test_modifier_default_name_is_id` - name defaults to id when not provided
- [ ] `test_modifier_param_min_max_default` - min_val, max_val, default_val from param dict
- [ ] `test_modifier_param_defaults_when_missing` - min=0, max=100, default=0 when no param
- [ ] `test_modifier_create_modifier_returns_application` - Returns ApplicationModifier instance
- [ ] `test_modifier_create_modifier_with_value` - ApplicationModifier gets specified value
- [ ] `test_modifier_create_modifier_default_value` - ApplicationModifier gets default when no value

ApplicationModifier class:
- [ ] `test_application_modifier_stores_definition` - definition attribute set
- [ ] `test_application_modifier_stores_value` - value attribute set
- [ ] `test_application_modifier_default_value` - Uses mod_def.default_val when value is None

**Estimated tests: ~18**

---

### Task 2.5: Modifier Schema Validation Tests (TCG-SIM-005) [Medium]
**File:** `tests/unit/simulation/components/test_modifier_schema.py` (NEW)
**Source:** `game/simulation/components/modifier_schema.py` (259 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_modifier_schema.py`

is_v2_format:
- [ ] `test_v2_format_list_effects_true` - {'effects': []} returns True
- [ ] `test_v1_format_dict_effects_false` - {'effects': {}} returns False
- [ ] `test_no_effects_key_false` - {} returns False
- [ ] `test_effects_not_list_or_dict_false` - {'effects': 'string'} returns False

validate_effect_v2:
- [ ] `test_valid_effect_minimal` - {'stat': 'x', 'formula': 'param'} is valid
- [ ] `test_effect_missing_stat_invalid` - {'formula': 'param'} is invalid
- [ ] `test_effect_missing_formula_invalid` - {'stat': 'x'} is invalid
- [ ] `test_effect_non_dict_invalid` - "string" is invalid
- [ ] `test_effect_valid_operations` - 'multiply', 'add', 'set', 'add_to_mult' all valid
- [ ] `test_effect_invalid_operation` - 'divide' is invalid
- [ ] `test_effect_target_ability_string_valid` - target_ability: "WeaponAbility" valid
- [ ] `test_effect_target_ability_non_string_invalid` - target_ability: 123 invalid
- [ ] `test_effect_depends_on_list_valid` - depends_on: ["a", "b"] valid
- [ ] `test_effect_depends_on_non_list_invalid` - depends_on: "a" invalid

normalize_effect_v2:
- [ ] `test_normalize_adds_default_operation` - Missing operation gets 'multiply'
- [ ] `test_normalize_preserves_existing_operation` - Existing 'add' unchanged

validate_param_v2:
- [ ] `test_valid_param` - {'name': 'x', 'type': 'linear', 'min': 0, 'max': 100, 'default': 50} valid
- [ ] `test_param_missing_required_field` - Missing 'name' invalid
- [ ] `test_param_non_numeric_min` - min: "zero" invalid
- [ ] `test_param_non_dict_invalid` - "string" is invalid

validate_restrictions_v2:
- [ ] `test_valid_restrictions` - {'allow_abilities': ['WeaponAbility']} valid
- [ ] `test_restrictions_invalid_require_mode` - require_mode: 'some' invalid
- [ ] `test_restrictions_non_string_ability` - allow_abilities: [123] invalid
- [ ] `test_restrictions_non_dict_invalid` - "string" is invalid

validate_modifier_v2:
- [ ] `test_valid_modifier_complete` - Full modifier definition valid
- [ ] `test_modifier_missing_id` - No id -> invalid
- [ ] `test_modifier_missing_effects` - No effects -> invalid
- [ ] `test_modifier_empty_effects` - Empty effects array -> invalid
- [ ] `test_modifier_invalid_effect_propagates` - Bad effect invalidates modifier
- [ ] `test_modifier_invalid_param_propagates` - Bad param invalidates modifier
- [ ] `test_modifier_invalid_restrictions_propagates` - Bad restrictions invalidates modifier

**Estimated tests: ~28**

---

### Task 2.6: Modifier Effects Evaluation Tests (TCG-SIM-006) [Medium]
**File:** `tests/unit/simulation/components/test_modifier_effects.py` (NEW)
**Source:** `game/simulation/components/modifier_effects.py` (326 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py`

ModifierEffect dataclass:
- [ ] `test_effect_describe_multiply` - "damage_mult x1.50"
- [ ] `test_effect_describe_add` - "accuracy_add +0.50"
- [ ] `test_effect_describe_set` - "arc_set =90.00"
- [ ] `test_effect_describe_with_target` - Includes "(on WeaponAbility)"
- [ ] `test_effect_is_targeted_true` - target_ability not None
- [ ] `test_effect_is_targeted_false` - target_ability is None
- [ ] `test_effect_to_dict_all_fields` - All fields present in dict

ModifierEffectEvaluator.evaluate_formula:
- [ ] `test_formula_simple_param` - "param" with param=2.0 returns 2.0
- [ ] `test_formula_power` - "param ^ 2" with param=3.0 returns 9.0
- [ ] `test_formula_exponential` - "2 ^ param" with param=3.0 returns 8.0
- [ ] `test_formula_linear` - "1.0 + param * 0.5" with param=2.0 returns 2.0
- [ ] `test_formula_logarithmic` - "1.0 + 0.514 * ln(1 + param / 30)" evaluates correctly
- [ ] `test_formula_syntax_error_raises` - "param +" raises FormulaException
- [ ] `test_formula_undefined_variable_raises` - "unknown_var" raises FormulaException
- [ ] `test_formula_division_by_zero_raises` - "param / 0" raises FormulaException

ModifierEffectEvaluator.evaluate_modifier:
- [ ] `test_evaluate_modifier_single_effect` - One effect produces one ModifierEffect
- [ ] `test_evaluate_modifier_multiple_effects` - Multiple effects produce list
- [ ] `test_evaluate_modifier_formula_error_fallback` - Bad formula falls back to param value
- [ ] `test_evaluate_modifier_with_target_ability` - target_ability passed through

validate_formula:
- [ ] `test_validate_formula_valid` - "param ^ 2" returns empty errors list
- [ ] `test_validate_formula_syntax_error` - "param +" returns error
- [ ] `test_validate_formula_undefined_var` - "xyz" returns error about undefined var

**Estimated tests: ~22**

---

### Task 2.7: Marker Abilities Tests (TCG-SIM-007) [Simple]
**File:** `tests/unit/simulation/components/abilities/test_markers.py` (NEW)
**Source:** `game/simulation/components/abilities/markers.py` (91 LOC)
**Tests:** `pytest tests/unit/simulation/components/abilities/test_markers.py`

VehicleLaunchAbility:
- [ ] `test_vehicle_launch_init_defaults` - capacity=0, cycle_time=5.0, cooldown=0
- [ ] `test_vehicle_launch_custom_values` - Custom capacity, fighter_class, cycle_time
- [ ] `test_vehicle_launch_try_launch_success` - Returns True and sets cooldown
- [ ] `test_vehicle_launch_try_launch_on_cooldown` - Returns False when cooldown > 0
- [ ] `test_vehicle_launch_update_decrements_cooldown` - Cooldown decreases by TICK_RATE
- [ ] `test_vehicle_launch_ui_rows` - get_ui_rows returns hangar and cycle info
- [ ] `test_vehicle_launch_primary_value` - get_primary_value returns capacity as float

CommandAndControl:
- [ ] `test_command_and_control_ui_rows` - Returns "Command: Active"
- [ ] `test_command_and_control_primary_value` - Returns 1.0

RequiresCommandAndControl:
- [ ] `test_requires_cc_ui_rows` - Returns "Requires C&C: Yes"

RequiresCombatMovement:
- [ ] `test_requires_propulsion_ui_rows` - Returns "Requires Propulsion: Yes"

StructuralIntegrity:
- [ ] `test_structural_integrity_ui_rows` - Returns "Structural Integrity: Yes"

**Estimated tests: ~12**

---

### Task 2.8: Stat Keys and Ability Bindings Tests (TCG-SIM-008) [Simple]
**File:** `tests/unit/simulation/components/abilities/test_stat_keys.py` (NEW)
**Source:** `game/simulation/components/abilities/stat_keys.py` (178 LOC)
**Tests:** `pytest tests/unit/simulation/components/abilities/test_stat_keys.py`

StatKey enum:
- [ ] `test_all_stat_keys_unique_values` - No duplicate .value strings
- [ ] `test_multiplicative_stat_default_1` - DAMAGE_MULT defaults to 1.0
- [ ] `test_additive_stat_default_0` - MASS_ADD defaults to 0.0
- [ ] `test_set_stat_default_none` - ARC_SET defaults to None
- [ ] `test_create_default_stats_dict_all_keys` - Dict has entry for every StatKey
- [ ] `test_create_default_stats_dict_has_properties` - Dict includes 'properties' key

AbilityStatBinding:
- [ ] `test_binding_init_basic` - StatKey, attribute_name, operation stored
- [ ] `test_binding_invalid_operation_raises` - ValueError for 'divide'
- [ ] `test_binding_get_base_attribute_explicit` - Returns explicit base_attribute
- [ ] `test_binding_get_base_attribute_auto` - Returns "_base_{attribute_name}"
- [ ] `test_binding_apply_multiply` - base * stat_value set on ability
- [ ] `test_binding_apply_add` - base + stat_value set on ability
- [ ] `test_binding_apply_set` - stat_value directly set on ability
- [ ] `test_binding_apply_missing_stat_returns_false` - Stat not in dict -> False
- [ ] `test_binding_apply_missing_base_attr_returns_false` - No base attr -> False
- [ ] `test_binding_describe` - Human-readable description string

**Estimated tests: ~16**

---

### Task 2.9: Modifier Application Logic Tests (TCG-SIM-009) [Simple]
**File:** `tests/unit/simulation/components/test_modifiers.py` (NEW)
**Source:** `game/simulation/components/modifiers.py` (185 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_modifiers.py`

_apply_effect_to_dict:
- [ ] `test_multiply_existing_key` - stats['x'] *= value
- [ ] `test_multiply_new_key` - stats['x'] = value (no prior key)
- [ ] `test_add_existing_key` - stats['x'] += value
- [ ] `test_add_new_key` - stats['x'] = value
- [ ] `test_set_key` - stats['x'] = value (always overwrite)
- [ ] `test_add_to_mult_existing` - stats['x'] += value
- [ ] `test_add_to_mult_new` - stats['x'] = 1.0 + value
- [ ] `test_unknown_operation_logged` - Warning logged, no crash

get_default_stat_multipliers:
- [ ] `test_defaults_mass_mult_is_1` - mass_mult starts at 1.0
- [ ] `test_defaults_mass_add_is_0` - mass_add starts at 0.0
- [ ] `test_defaults_arc_set_is_none` - arc_set starts at None
- [ ] `test_defaults_has_properties_dict` - properties key exists as empty dict

apply_modifier_effects:
- [ ] `test_apply_multiply_effect` - Multiplicative effect applied to stats
- [ ] `test_apply_add_effect` - Additive effect applied to stats
- [ ] `test_apply_set_effect` - Set effect overwrites stats
- [ ] `test_apply_targeted_effect_to_ability_stats` - Targeted effect goes to component.ability_stats
- [ ] `test_apply_null_effects_no_crash` - evaluate_effects returns None -> no crash

calculate_stat_multipliers:
- [ ] `test_calculate_with_no_modifiers` - Returns defaults
- [ ] `test_calculate_with_single_modifier` - Single modifier applied correctly
- [ ] `test_calculate_with_unknown_modifier_id` - Unknown ID silently skipped

**Estimated tests: ~20**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests pass: `pytest tests/unit/simulation/ -v --tb=short`
- [ ] Full test suite still passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
