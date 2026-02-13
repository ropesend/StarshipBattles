# Phase 2: Simulation Layer - CRITICAL + MAJOR

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-110 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add unit tests for all Simulation layer CRITICAL and MAJOR coverage gaps (TCG-SIM-001 through TCG-SIM-009). Expected: ~80 new tests.
**Actual:** 222 new tests added (16+11+23+22+57+31+16+22+24 = 222)

---

## Tasks

### Task 2.1: Registry Loader Service Tests (TCG-SIM-001) [Medium]
**File:** `tests/unit/simulation/services/test_registry_loader.py` (NEW)
**Source:** `game/simulation/services/registry_loader.py` (124 LOC)
**Tests:** `pytest tests/unit/simulation/services/test_registry_loader.py`

Note: Uses `unittest.mock.patch` for load_modifiers, load_components, load_vehicle_classes.

- [x] `test_reload_nonexistent_directory_returns_false` - Non-existent dir returns False
- [x] `test_reload_clears_all_registries` - components, modifiers, vehicle_classes all cleared
- [x] `test_reload_loads_modifiers_first` - Modifiers loaded before components
- [x] `test_reload_loads_components` - load_components called with correct path
- [x] `test_reload_loads_vehicle_classes` - load_vehicle_classes called
- [x] `test_reload_with_layers_file` - Passes layers_file_path when vehiclelayers.json exists
- [x] `test_reload_test_prefix_fallback` - test_components.json preferred over components.json
- [x] `test_reload_missing_modifiers_file_continues` - No crash if modifiers.json absent
- [x] `test_reload_missing_components_file_continues` - No crash if components.json absent
- [x] `test_reload_returns_true_even_if_some_files_missing` - True if dir exists
- [x] `test_reload_frozen_registry_raises` - FrozenStateException when frozen
- [x] `test_reload_component_load_error_logged` - JSONDecodeError in components logged, not raised
- [x] `test_reload_modifier_load_error_logged` - TypeError in modifiers logged, not raised
- [x] `test_accepts_string_path` - BONUS: path handling
- [x] `test_accepts_path_object` - BONUS: path handling
- [x] `test_file_instead_of_directory_returns_false` - BONUS: path handling

**Estimated tests: ~13**

---

### Task 2.2: Physics Constants Tests (TCG-SIM-002) [Simple]
**File:** `tests/unit/simulation/test_physics_constants.py` (NEW)
**Source:** `game/simulation/physics_constants.py` (30 LOC)
**Tests:** `pytest tests/unit/simulation/test_physics_constants.py`

- [x] `test_k_speed_is_positive_int` - K_SPEED > 0 and isinstance int
- [x] `test_k_thrust_is_positive_int` - K_THRUST > 0
- [x] `test_k_turn_is_positive_int` - K_TURN > 0
- [x] `test_speed_formula_known_values` - (100 thrust * 25) / 50 mass = 50 speed
- [x] `test_acceleration_formula_known_values` - (100 thrust * 2500) / (50^2) = 100 accel
- [x] `test_turn_formula_known_values` - (10 raw * 25000) / (50^1.5) = known value
- [x] `test_speed_inverse_mass_scaling` - Double mass halves speed
- [x] `test_turn_heavier_ships_turn_slower` - Higher mass = lower turn speed

**Estimated tests: ~8**

---

### Task 2.3: Battle Configuration Tests (TCG-SIM-003) [Simple]
**File:** `tests/unit/simulation/test_battle_config.py` (NEW)
**Source:** `game/simulation/battle_config.py` (54 LOC)
**Tests:** `pytest tests/unit/simulation/test_battle_config.py`

BattleMode enum:
- [x] `test_battle_mode_manual` - BattleMode.MANUAL.value == "manual"
- [x] `test_battle_mode_test` - BattleMode.TEST.value == "test"
- [x] `test_battle_mode_strategy` - BattleMode.STRATEGY.value == "strategy"
- [x] `test_battle_mode_hypothetical` - BattleMode.HYPOTHETICAL.value == "hypothetical"
- [x] `test_battle_mode_all_unique` - All values are distinct

BattleConfig:
- [x] `test_default_mode_is_manual` - Default mode = MANUAL
- [x] `test_default_max_ticks` - Default max_ticks matches SimulationConstants
- [x] `test_default_headless_false` - headless defaults to False
- [x] `test_default_logging_enabled` - enable_logging defaults to True
- [x] `test_default_no_retreat` - allow_retreat defaults to False
- [x] `test_hypothetical_mode_isolated` - isolated defaults to True
- [x] `test_custom_seed` - Seed can be set to specific int
- [x] `test_custom_max_ticks` - max_ticks can be overridden
- [x] `test_map_bounds_default` - Default map_bounds tuple has 4 elements

**Estimated tests: ~14**

---

### Task 2.4: Component Constants Tests (TCG-SIM-004) [Simple]
**File:** `tests/unit/simulation/components/test_component_constants.py` (NEW)
**Source:** `game/simulation/components/component_constants.py` (69 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_component_constants.py`

ComponentStatus enum:
- [x] `test_component_status_active` - ACTIVE is defined
- [x] `test_component_status_damaged` - DAMAGED is defined
- [x] `test_component_status_no_crew` - NO_CREW is defined
- [x] `test_component_status_no_power` - NO_POWER is defined
- [x] `test_component_status_no_fuel` - NO_FUEL is defined
- [x] `test_component_status_no_ammo` - NO_AMMO is defined
- [x] `test_component_status_all_unique` - All enum values are distinct

Modifier class:
- [x] `test_modifier_init_minimal` - Modifier({'id': 'test', 'effects': []}) works
- [x] `test_modifier_init_all_fields` - Name, description, restrictions, readonly parsed
- [x] `test_modifier_default_name_is_id` - name defaults to id when not provided
- [x] `test_modifier_param_min_max_default` - min_val, max_val, default_val from param dict
- [x] `test_modifier_param_defaults_when_missing` - min=0, max=100, default=0 when no param
- [x] `test_modifier_create_modifier_returns_application` - Returns ApplicationModifier instance
- [x] `test_modifier_create_modifier_with_value` - ApplicationModifier gets specified value
- [x] `test_modifier_create_modifier_default_value` - ApplicationModifier gets default when no value

ApplicationModifier class:
- [x] `test_application_modifier_stores_definition` - definition attribute set
- [x] `test_application_modifier_stores_value` - value attribute set
- [x] `test_application_modifier_default_value` - Uses mod_def.default_val when value is None

**Estimated tests: ~18**

---

### Task 2.5: Modifier Schema Validation Tests (TCG-SIM-005) [Medium]
**File:** `tests/unit/simulation/components/test_modifier_schema.py` (NEW)
**Source:** `game/simulation/components/modifier_schema.py` (259 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_modifier_schema.py`

is_v2_format:
- [x] `test_v2_format_list_effects_true` - {'effects': []} returns True
- [x] `test_v1_format_dict_effects_false` - {'effects': {}} returns False
- [x] `test_no_effects_key_false` - {} returns False
- [x] `test_effects_not_list_or_dict_false` - {'effects': 'string'} returns False

validate_effect_v2:
- [x] `test_valid_effect_minimal` - {'stat': 'x', 'formula': 'param'} is valid
- [x] `test_effect_missing_stat_invalid` - {'formula': 'param'} is invalid
- [x] `test_effect_missing_formula_invalid` - {'stat': 'x'} is invalid
- [x] `test_effect_non_dict_invalid` - "string" is invalid
- [x] `test_effect_valid_operations` - 'multiply', 'add', 'set', 'add_to_mult' all valid
- [x] `test_effect_invalid_operation` - 'divide' is invalid
- [x] `test_effect_target_ability_string_valid` - target_ability: "WeaponAbility" valid
- [x] `test_effect_target_ability_non_string_invalid` - target_ability: 123 invalid
- [x] `test_effect_depends_on_list_valid` - depends_on: ["a", "b"] valid
- [x] `test_effect_depends_on_non_list_invalid` - depends_on: "a" invalid

normalize_effect_v2:
- [x] `test_normalize_adds_default_operation` - Missing operation gets 'multiply'
- [x] `test_normalize_preserves_existing_operation` - Existing 'add' unchanged

validate_param_v2:
- [x] `test_valid_param` - {'name': 'x', 'type': 'linear', 'min': 0, 'max': 100, 'default': 50} valid
- [x] `test_param_missing_required_field` - Missing 'name' invalid
- [x] `test_param_non_numeric_min` - min: "zero" invalid
- [x] `test_param_non_dict_invalid` - "string" is invalid

validate_restrictions_v2:
- [x] `test_valid_restrictions` - {'allow_abilities': ['WeaponAbility']} valid
- [x] `test_restrictions_invalid_require_mode` - require_mode: 'some' invalid
- [x] `test_restrictions_non_string_ability` - allow_abilities: [123] invalid
- [x] `test_restrictions_non_dict_invalid` - "string" is invalid

validate_modifier_v2:
- [x] `test_valid_modifier_complete` - Full modifier definition valid
- [x] `test_modifier_missing_id` - No id -> invalid
- [x] `test_modifier_missing_effects` - No effects -> invalid
- [x] `test_modifier_empty_effects` - Empty effects array -> invalid
- [x] `test_modifier_invalid_effect_propagates` - Bad effect invalidates modifier
- [x] `test_modifier_invalid_param_propagates` - Bad param invalidates modifier
- [x] `test_modifier_invalid_restrictions_propagates` - Bad restrictions invalidates modifier

**Estimated tests: ~28**

---

### Task 2.6: Modifier Effects Evaluation Tests (TCG-SIM-006) [Medium]
**File:** `tests/unit/simulation/components/test_modifier_effects.py` (NEW)
**Source:** `game/simulation/components/modifier_effects.py` (326 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_modifier_effects.py`

ModifierEffect dataclass:
- [x] `test_effect_describe_multiply` - "damage_mult x1.50"
- [x] `test_effect_describe_add` - "accuracy_add +0.50"
- [x] `test_effect_describe_set` - "arc_set =90.00"
- [x] `test_effect_describe_with_target` - Includes "(on WeaponAbility)"
- [x] `test_effect_is_targeted_true` - target_ability not None
- [x] `test_effect_is_targeted_false` - target_ability is None
- [x] `test_effect_to_dict_all_fields` - All fields present in dict

ModifierEffectEvaluator.evaluate_formula:
- [x] `test_formula_simple_param` - "param" with param=2.0 returns 2.0
- [x] `test_formula_power` - "param ^ 2" with param=3.0 returns 9.0
- [x] `test_formula_exponential` - "2 ^ param" with param=3.0 returns 8.0
- [x] `test_formula_linear` - "1.0 + param * 0.5" with param=2.0 returns 2.0
- [x] `test_formula_logarithmic` - "1.0 + 0.514 * ln(1 + param / 30)" evaluates correctly
- [x] `test_formula_syntax_error_raises` - "param +" raises FormulaException
- [x] `test_formula_undefined_variable_raises` - "unknown_var" raises FormulaException
- [x] `test_formula_division_by_zero_raises` - "param / 0" raises FormulaException

ModifierEffectEvaluator.evaluate_modifier:
- [x] `test_evaluate_modifier_single_effect` - One effect produces one ModifierEffect
- [x] `test_evaluate_modifier_multiple_effects` - Multiple effects produce list
- [x] `test_evaluate_modifier_formula_error_fallback` - Bad formula falls back to param value
- [x] `test_evaluate_modifier_with_target_ability` - target_ability passed through

validate_formula:
- [x] `test_validate_formula_valid` - "param ^ 2" returns empty errors list
- [x] `test_validate_formula_syntax_error` - "param +" returns error
- [x] `test_validate_formula_undefined_var` - "xyz" returns error about undefined var

**Estimated tests: ~22**

---

### Task 2.7: Marker Abilities Tests (TCG-SIM-007) [Simple]
**File:** `tests/unit/simulation/components/abilities/test_markers.py` (NEW)
**Source:** `game/simulation/components/abilities/markers.py` (91 LOC)
**Tests:** `pytest tests/unit/simulation/components/abilities/test_markers.py`

VehicleLaunchAbility:
- [x] `test_vehicle_launch_init_defaults` - capacity=0, cycle_time=5.0, cooldown=0
- [x] `test_vehicle_launch_custom_values` - Custom capacity, fighter_class, cycle_time
- [x] `test_vehicle_launch_try_launch_success` - Returns True and sets cooldown
- [x] `test_vehicle_launch_try_launch_on_cooldown` - Returns False when cooldown > 0
- [x] `test_vehicle_launch_update_decrements_cooldown` - Cooldown decreases by TICK_RATE
- [x] `test_vehicle_launch_ui_rows` - get_ui_rows returns hangar and cycle info
- [x] `test_vehicle_launch_primary_value` - get_primary_value returns capacity as float

CommandAndControl:
- [x] `test_command_and_control_ui_rows` - Returns "Command: Active"
- [x] `test_command_and_control_primary_value` - Returns 1.0

RequiresCommandAndControl:
- [x] `test_requires_cc_ui_rows` - Returns "Requires C&C: Yes"

RequiresCombatMovement:
- [x] `test_requires_propulsion_ui_rows` - Returns "Requires Propulsion: Yes"

StructuralIntegrity:
- [x] `test_structural_integrity_ui_rows` - Returns "Structural Integrity: Yes"

**Estimated tests: ~12**

---

### Task 2.8: Stat Keys and Ability Bindings Tests (TCG-SIM-008) [Simple]
**File:** `tests/unit/simulation/components/abilities/test_stat_keys.py` (NEW)
**Source:** `game/simulation/components/abilities/stat_keys.py` (178 LOC)
**Tests:** `pytest tests/unit/simulation/components/abilities/test_stat_keys.py`

StatKey enum:
- [x] `test_all_stat_keys_unique_values` - No duplicate .value strings
- [x] `test_multiplicative_stat_default_1` - DAMAGE_MULT defaults to 1.0
- [x] `test_additive_stat_default_0` - MASS_ADD defaults to 0.0
- [x] `test_set_stat_default_none` - ARC_SET defaults to None
- [x] `test_create_default_stats_dict_all_keys` - Dict has entry for every StatKey
- [x] `test_create_default_stats_dict_has_properties` - Dict includes 'properties' key

AbilityStatBinding:
- [x] `test_binding_init_basic` - StatKey, attribute_name, operation stored
- [x] `test_binding_invalid_operation_raises` - ValueError for 'divide'
- [x] `test_binding_get_base_attribute_explicit` - Returns explicit base_attribute
- [x] `test_binding_get_base_attribute_auto` - Returns "_base_{attribute_name}"
- [x] `test_binding_apply_multiply` - base * stat_value set on ability
- [x] `test_binding_apply_add` - base + stat_value set on ability
- [x] `test_binding_apply_set` - stat_value directly set on ability
- [x] `test_binding_apply_missing_stat_returns_false` - Stat not in dict -> False
- [x] `test_binding_apply_missing_base_attr_returns_false` - No base attr -> False
- [x] `test_binding_describe` - Human-readable description string

**Estimated tests: ~16**

---

### Task 2.9: Modifier Application Logic Tests (TCG-SIM-009) [Simple]
**File:** `tests/unit/simulation/components/test_modifiers.py` (NEW)
**Source:** `game/simulation/components/modifiers.py` (185 LOC)
**Tests:** `pytest tests/unit/simulation/components/test_modifiers.py`

_apply_effect_to_dict:
- [x] `test_multiply_existing_key` - stats['x'] *= value
- [x] `test_multiply_new_key` - stats['x'] = value (no prior key)
- [x] `test_add_existing_key` - stats['x'] += value
- [x] `test_add_new_key` - stats['x'] = value
- [x] `test_set_key` - stats['x'] = value (always overwrite)
- [x] `test_add_to_mult_existing` - stats['x'] += value
- [x] `test_add_to_mult_new` - stats['x'] = 1.0 + value
- [x] `test_unknown_operation_logged` - Warning logged, no crash

get_default_stat_multipliers:
- [x] `test_defaults_mass_mult_is_1` - mass_mult starts at 1.0
- [x] `test_defaults_mass_add_is_0` - mass_add starts at 0.0
- [x] `test_defaults_arc_set_is_none` - arc_set starts at None
- [x] `test_defaults_has_properties_dict` - properties key exists as empty dict

apply_modifier_effects:
- [x] `test_apply_multiply_effect` - Multiplicative effect applied to stats
- [x] `test_apply_add_effect` - Additive effect applied to stats
- [x] `test_apply_set_effect` - Set effect overwrites stats
- [x] `test_apply_targeted_effect_to_ability_stats` - Targeted effect goes to component.ability_stats
- [x] `test_apply_null_effects_no_crash` - evaluate_effects returns None -> no crash

calculate_stat_multipliers:
- [x] `test_calculate_with_no_modifiers` - Returns defaults
- [x] `test_calculate_with_single_modifier` - Single modifier applied correctly
- [x] `test_calculate_with_unknown_modifier_id` - Unknown ID silently skipped

**Estimated tests: ~20**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All new tests pass: `pytest tests/unit/simulation/ -v --tb=short`
- [x] Full test suite still passes: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
