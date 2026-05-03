# Phase 3: CAT-10 Parametrize

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-323 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Parametrize the 53 verified CAT-10 identical-pattern test clusters.

---

## Tasks

### Task 3.1: test_fleet_report_filters.py [Complex]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`

- [ ] [S08-CAT10-002] `TestSpecialCapabilityFilter (7 tests)` (lines 970-1143): Parametrize across (ability, filter_key, expected) tuples.
- [ ] [S08-CAT10-003] `TestFilterShipsSpaceyard` (lines 587-665): Parametrize.
- [ ] [S08-CAT10-004] `TestFilterShipsCargo` (lines 668-784): Parametrize.

- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py` passes; LOC delta ≈ 370

**Notes:** _(none yet)_

---

### Task 3.2: test_superweapon_handler_validation.py [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_handler_validation.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_handler_validation.py`

- [ ] [S07-CAT10-001] `5 near-identical direct-handler test classes` (lines 87-192): Parametrize across handlers.
- [ ] [S07-CAT10-002] `5 near-identical mission-handler test classes` (lines 199-393): Parametrize across mission handlers.

- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_handler_validation.py` passes; LOC delta ≈ 300

**Notes:** _(none yet)_

---

### Task 3.3: test_colonization_facade.py [Medium]
**File:** `tests/unit/strategy/test_colonization_facade.py`
**Tests:** `pytest tests/unit/strategy/test_colonization_facade.py`

- [ ] [S11-CAT10-004] `Success/failure duplicate patterns` (lines 136-258): Parametrize.
- [ ] [S11-CAT10-005] `Pod-filtering tests` (lines 474-551): Parametrize.

- [ ] Verify: `pytest tests/unit/strategy/test_colonization_facade.py` passes; LOC delta ≈ 201

**Notes:** _(none yet)_

---

### Task 3.4: test_fleet_data_source.py [Medium]
**File:** `tests/unit/ui/screens/test_fleet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py`

- [ ] [S06-CAT10-001] `3 set-filter tests parametrizable` (lines 194-224): Parametrize the 3 truly identical tests; ~6 LOC savings (not 35).
      _(verification adjusted from review's "Parametrize all 5 set-filter tests for ~35 LOC savings." — see verification_report.md)_
- [ ] [S06-CAT10-003] `6 yes/no special-capability tests` (lines 324-538): Parametrize across (capability, return, expected) tuples.

- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_data_source.py` passes; LOC delta ≈ 93

**Notes:** _(none yet)_

---

### Task 3.5: test_strategy_superweapons.py [Medium]
**File:** `tests/unit/ui/screens/test_strategy_superweapons.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_superweapons.py`

- [ ] [S10-CAT10-004] `6 repeated no_fleet_returns_none tests` (lines 112-397): Parametrize with handler tuples.
- [ ] [S10-CAT10-005] `5 (of 6) fleet_without_ability tests` (lines 118-406): Parametrize the 5 identical tests; keep SelfDestruct separate.

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_superweapons.py` passes; LOC delta ≈ 65

**Notes:** _(none yet)_

---

### Task 3.6: test_color_helpers.py [Medium]
**File:** `tests/unit/ui/utils/test_color_helpers.py`
**Tests:** `pytest tests/unit/ui/utils/test_color_helpers.py`

- [ ] [S11-CAT10-006] `5 get_hp_bar_color tests` (lines 118-171): Parametrize.
- [ ] [S11-CAT10-007] `5 get_component_status_display tests` (lines 178-236): Parametrize.

- [ ] Verify: `pytest tests/unit/ui/utils/test_color_helpers.py` passes; LOC delta ≈ 113

**Notes:** _(none yet)_

---

### Task 3.7: test_resources.py [Simple]
**File:** `tests/integration/strategy/turn_engine/test_resources.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resources.py`

- [ ] [S10-CAT10-001] `Full-turn duplicate setup` (lines 214-270): Extract setup helper; keep both tests for distinct properties.

- [ ] Verify: `pytest tests/integration/strategy/turn_engine/test_resources.py` passes; LOC delta ≈ 57

**Notes:** _(none yet)_

---

### Task 3.8: test_config_edge_cases.py [Simple]
**File:** `tests/unit/core/test_config_edge_cases.py`
**Tests:** `pytest tests/unit/core/test_config_edge_cases.py`

- [ ] [S05-CAT10-002] `Boundary-value test classes` (lines 31-91): Parametrize with (attr_name, predicate) pairs.

- [ ] Verify: `pytest tests/unit/core/test_config_edge_cases.py` passes; LOC delta ≈ 61

**Notes:** _(none yet)_

---

### Task 3.9: test_protocols.py [Simple]
**File:** `tests/unit/core/test_protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] [S09-CAT10-001] `TypeGuard parametrize opportunity` (lines 101-220): Parametrize.

- [ ] Verify: `pytest tests/unit/core/test_protocols.py` passes; LOC delta ≈ 120

**Notes:** _(none yet)_

---

### Task 3.10: test_defense_marker_bindings.py [Simple]
**File:** `tests/unit/modifiers/test_defense_marker_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_defense_marker_bindings.py`

- [ ] [S06-CAT10-004] `6 empty-bindings tests` (lines 58-100): Parametrize into a single test.

- [ ] Verify: `pytest tests/unit/modifiers/test_defense_marker_bindings.py` passes; LOC delta ≈ 43

**Notes:** _(none yet)_

---

### Task 3.11: test_testruncard_propulsion.py [Simple]
**File:** `tests/unit/qa/test_testruncard_propulsion.py`
**Tests:** `pytest tests/unit/qa/test_testruncard_propulsion.py`

- [ ] [S11-CAT10-001] `4 format-string tests` (lines 193-229): Parametrize.

- [ ] Verify: `pytest tests/unit/qa/test_testruncard_propulsion.py` passes; LOC delta ≈ 37

**Notes:** _(none yet)_

---

### Task 3.12: test_tech_node.py [Simple]
**File:** `tests/unit/research/test_tech_node.py`
**Tests:** `pytest tests/unit/research/test_tech_node.py`

- [ ] [S09-CAT10-003] `TestTechNodePriceCurves` (lines 315-373): Parametrize across price_curve.

- [ ] Verify: `pytest tests/unit/research/test_tech_node.py` passes; LOC delta ≈ 59

**Notes:** _(none yet)_

---

### Task 3.13: test_defense_isolation.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_defense_isolation.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_defense_isolation.py`

- [ ] [S05-CAT10-003] `10 paired Attack/Defense tests` (lines 366-527): Parametrize across classes/modifiers.

- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_defense_isolation.py` passes; LOC delta ≈ 162

**Notes:** _(none yet)_

---

### Task 3.14: test_resource_consumption.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_resource_consumption.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_resource_consumption.py`

- [ ] [S05-CAT10-004] `3 nearly-identical resource tests` (lines 439-506): Parametrize.

- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_resource_consumption.py` passes; LOC delta ≈ 68

**Notes:** _(none yet)_

---

### Task 3.15: test_static_value_ability.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_static_value_ability.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_static_value_ability.py`

- [ ] [S04-CAT10-001] `positive/negative format pair` (lines 166-176): Parametrize.

- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_static_value_ability.py` passes; LOC delta ≈ 11

**Notes:** _(none yet)_

---

### Task 3.16: test_system_stabilizers.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_system_stabilizers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_system_stabilizers.py`

- [ ] [S10-CAT10-006] `Stellar/Warp Stabilizer near-identical classes` (lines 12-109): Single parametrized class with (AbilityClass, expected_drain, activation, deactivation) tuples.

- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_system_stabilizers.py` passes; LOC delta ≈ 98

**Notes:** _(none yet)_

---

### Task 3.17: test_ship_consumable_manager.py [Simple]
**File:** `tests/unit/simulation/components/test_ship_consumable_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ship_consumable_manager.py`

- [ ] [S12-CAT10-003] `consume_resource edge cases` (lines 86-114): Parametrize the 3 consume_resource cases; keep get_current_resource separate.

- [ ] Verify: `pytest tests/unit/simulation/components/test_ship_consumable_manager.py` passes; LOC delta ≈ 29

**Notes:** _(none yet)_

---

### Task 3.18: test_battle_state_serialization.py [Simple]
**File:** `tests/unit/simulation/replay/test_battle_state_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_battle_state_serialization.py`

- [ ] [S07-CAT10-006] `19 field comparisons in round-trip` (lines 306-328): Replace with a helper iterating over field tuples.

- [ ] Verify: `pytest tests/unit/simulation/replay/test_battle_state_serialization.py` passes; LOC delta ≈ 23

**Notes:** _(none yet)_

---

### Task 3.19: test_modifier_service.py [Simple]
**File:** `tests/unit/simulation/services/test_modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_modifier_service.py`

- [ ] [S10-CAT10-003] `5+5 turret_mount duplicate tests` (lines 488-528, 634-664): Parametrize the resolution logic; test both APIs against the same matrix.

- [ ] Verify: `pytest tests/unit/simulation/services/test_modifier_service.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 3.20: test_battle_end_conditions.py [Simple]
**File:** `tests/unit/simulation/systems/test_battle_end_conditions.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_end_conditions.py`

- [ ] [S05-CAT10-001] `3 duplicate parametrize blocks` (lines 546-588): Collapse into a single parametrized class.

- [ ] Verify: `pytest tests/unit/simulation/systems/test_battle_end_conditions.py` passes; LOC delta ≈ 43

**Notes:** _(none yet)_

---

### Task 3.21: test_battle_engine_end_conditions.py [Simple]
**File:** `tests/unit/simulation/systems/test_battle_engine_end_conditions.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_end_conditions.py`

- [ ] [S08-CAT10-006] `TestEscapeBasedMode 7 tests` (lines 115-239): Optional parametrization of common setup.

- [ ] Verify: `pytest tests/unit/simulation/systems/test_battle_engine_end_conditions.py` passes; LOC delta ≈ 125

**Notes:** _(none yet)_

---

### Task 3.22: test_battle_runner.py [Simple]
**File:** `tests/unit/simulation/test_battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py`

- [ ] [S09-CAT10-005] `5 module-level smoke tests` (lines 254-390): Extract _run_minimal_battle helper and parametrize.

- [ ] Verify: `pytest tests/unit/simulation/test_battle_runner.py` passes; LOC delta ≈ 137

**Notes:** _(none yet)_

---

### Task 3.23: test_battle_state_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_battle_state_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_battle_state_validation.py`

- [ ] [S08-CAT10-005] `Component + ShipState validation tests` (lines 39-201): Parametrize each cluster.

- [ ] Verify: `pytest tests/unit/strategy/data/test_battle_state_validation.py` passes; LOC delta ≈ 163

**Notes:** _(none yet)_

---

### Task 3.24: test_design_metadata_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_design_metadata_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_design_metadata_validation.py`

- [ ] [S01-CAT10-002] `Missing-field defaults cluster` (lines 49-77): Parametrize: @pytest.mark.parametrize('key,default', [...]).

- [ ] Verify: `pytest tests/unit/strategy/data/test_design_metadata_validation.py` passes; LOC delta ≈ 30

**Notes:** _(none yet)_

---

### Task 3.25: test_fleet_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_fleet_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet_validation.py`

- [ ] [S11-CAT10-012] `Missing-key tests` (lines 44-65): Parametrize.

- [ ] Verify: `pytest tests/unit/strategy/data/test_fleet_validation.py` passes; LOC delta ≈ 22

**Notes:** _(none yet)_

---

### Task 3.26: test_loading.py [Simple]
**File:** `tests/unit/strategy/data/test_loading.py`
**Tests:** `pytest tests/unit/strategy/data/test_loading.py`

- [ ] [S09-CAT10-002] `TestEdgeCases` (lines 159-239): Parametrize across (json_content, expected_ids).

- [ ] Verify: `pytest tests/unit/strategy/data/test_loading.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 3.27: test_population_model.py [Simple]
**File:** `tests/unit/strategy/data/test_population_model.py`
**Tests:** `pytest tests/unit/strategy/data/test_population_model.py`

- [ ] [S06-CAT10-002] `2 max-population tests` (lines 102-117): Parametrize.

- [ ] Verify: `pytest tests/unit/strategy/data/test_population_model.py` passes; LOC delta ≈ 16

**Notes:** _(none yet)_

---

### Task 3.28: test_ship_serialization.py [Simple]
**File:** `tests/unit/strategy/data/test_ship_serialization.py`
**Tests:** `pytest tests/unit/strategy/data/test_ship_serialization.py`

- [ ] [S07-CAT10-003] `6 round-trip attribute tests` (lines 328-368): Parametrize across attributes.

- [ ] Verify: `pytest tests/unit/strategy/data/test_ship_serialization.py` passes; LOC delta ≈ 41

**Notes:** _(none yet)_

---

### Task 3.29: test_planet_action_engine.py [Simple]
**File:** `tests/unit/strategy/engine/test_planet_action_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_action_engine.py`

- [ ] [S10-CAT10-002] `3 event-logging tests` (lines 336-437): Optional parametrization preserving descriptive names.

- [ ] Verify: `pytest tests/unit/strategy/engine/test_planet_action_engine.py` passes; LOC delta ≈ 102

**Notes:** _(none yet)_

---

### Task 3.30: test_superweapon_command_handlers.py [Simple]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [ ] [S03-CAT10-001] `Identical 3-test pattern across 6 handler classes` (lines 73-312): Parametrize across handlers.

- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py` passes; LOC delta ≈ 240

**Notes:** _(none yet)_

---

### Task 3.31: test_system_dto.py [Simple]
**File:** `tests/unit/strategy/facade/test_system_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/test_system_dto.py`

- [ ] [S01-CAT10-001] `DTO creation + frozen tests cluster` (lines 26-38, 44-54, 72-113, 272-306): Consolidate into @pytest.mark.parametrize.

- [ ] Verify: `pytest tests/unit/strategy/facade/test_system_dto.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 3.32: test_planet_validation.py [Simple]
**File:** `tests/unit/strategy/planet/test_planet_validation.py`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py`

- [ ] [S01-CAT10-003] `Negative-value validation tests split` (lines 64-78, 94-116): Merge the two parametrize blocks or leave as-is.

- [ ] Verify: `pytest tests/unit/strategy/planet/test_planet_validation.py` passes; LOC delta ≈ 20

**Notes:** _(none yet)_

---

### Task 3.33: test_modifier_resolver.py [Simple]
**File:** `tests/unit/strategy/services/test_modifier_resolver.py`
**Tests:** `pytest tests/unit/strategy/services/test_modifier_resolver.py`

- [ ] [S02-CAT10-002] `7 resolve_size_multiplier tests` (lines 15-69): Parametrize.

- [ ] Verify: `pytest tests/unit/strategy/services/test_modifier_resolver.py` passes; LOC delta ≈ 55

**Notes:** _(none yet)_

---

### Task 3.34: test_command_handlers.py [Simple]
**File:** `tests/unit/strategy/test_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`

- [ ] [S12-CAT10-001] `8+ handler error-path test clusters` (lines 90-290): Parametrize across (handler_cls, cmd_kwargs).

- [ ] Verify: `pytest tests/unit/strategy/test_command_handlers.py` passes; LOC delta ≈ 200

**Notes:** _(none yet)_

---

### Task 3.35: test_commands.py [Simple]
**File:** `tests/unit/strategy/test_commands.py`
**Tests:** `pytest tests/unit/strategy/test_commands.py`

- [ ] [S11-CAT10-010] `Command property tests` (lines 38-342): Parametrize across (Command, kwargs, expected_type).

- [ ] Verify: `pytest tests/unit/strategy/test_commands.py` passes; LOC delta ≈ 305

**Notes:** _(none yet)_

---

### Task 3.36: test_engine_validation.py [Simple]
**File:** `tests/unit/strategy/test_engine_validation.py`
**Tests:** `pytest tests/unit/strategy/test_engine_validation.py`

- [ ] [S09-CAT10-004] `9+ engine validation classes` (lines 39-312): Collapse into one parametrized class with (engine_cls, valid_empire_kwargs, invalid_field_path).

- [ ] Verify: `pytest tests/unit/strategy/test_engine_validation.py` passes; LOC delta ≈ 274

**Notes:** _(none yet)_

---

### Task 3.37: test_fleet_consumable_aggregator.py [Simple]
**File:** `tests/unit/strategy/test_fleet_consumable_aggregator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_consumable_aggregator.py`

- [ ] [S07-CAT10-005] `True/False variant pairs` (lines 84-108, 191-207): Parametrize.

- [ ] Verify: `pytest tests/unit/strategy/test_fleet_consumable_aggregator.py` passes; LOC delta ≈ 41

**Notes:** _(none yet)_

---

### Task 3.38: test_fleet_speed_calculator.py [Simple]
**File:** `tests/unit/strategy/test_fleet_speed_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_speed_calculator.py`

- [ ] [S02-CAT10-001] `7 calculate_ship_speed tests` (lines 13-116): Parametrize to one @pytest.mark.parametrize test.

- [ ] Verify: `pytest tests/unit/strategy/test_fleet_speed_calculator.py` passes; LOC delta ≈ 103

**Notes:** _(none yet)_

---

### Task 3.39: test_planet_command_handlers.py [Simple]
**File:** `tests/unit/strategy/test_planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_planet_command_handlers.py`

- [ ] [S12-CAT10-002] `3 handler classes 4 tests each` (lines 413-548): Parametrize across (handler_cls, cmd_attr_name, planet_attr_name, cmd_val, expected_val).

- [ ] Verify: `pytest tests/unit/strategy/test_planet_command_handlers.py` passes; LOC delta ≈ 136

**Notes:** _(none yet)_

---

### Task 3.40: test_resource_transfer.py [Simple]
**File:** `tests/unit/strategy/test_resource_transfer.py`
**Tests:** `pytest tests/unit/strategy/test_resource_transfer.py`

- [ ] [S11-CAT10-011] `_execute_fleet_transfer 8 tests` (lines 65-135): Parametrize.

- [ ] Verify: `pytest tests/unit/strategy/test_resource_transfer.py` passes; LOC delta ≈ 71

**Notes:** _(none yet)_

---

### Task 3.41: test_strategy_menu_panel.py [Simple]
**File:** `tests/unit/ui/panels/test_strategy_menu_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_strategy_menu_panel.py`

- [ ] [S08-CAT10-001] `6 button-callback tests` (lines 154-194): Parametrize.

- [ ] Verify: `pytest tests/unit/ui/panels/test_strategy_menu_panel.py` passes; LOC delta ≈ 41

**Notes:** _(none yet)_

---

### Task 3.42: test_battle_panels_extended.py [Simple]
**File:** `tests/unit/ui/screens/test_battle_panels_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_panels_extended.py`

- [ ] [S11-CAT10-003] `expand/collapse toggle tests` (lines 195-336): Parametrize.

- [ ] Verify: `pytest tests/unit/ui/screens/test_battle_panels_extended.py` passes; LOC delta ≈ 28

**Notes:** _(none yet)_

---

### Task 3.43: test_planet_data_source.py [Simple]
**File:** `tests/unit/ui/screens/test_planet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_data_source.py`

- [ ] [S02-CAT10-003] `Attr-value extraction tests` (lines 150-208): Parametrize to single test.

- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_data_source.py` passes; LOC delta ≈ 59

**Notes:** _(none yet)_

---

### Task 3.44: test_superweapon_input_modes.py [Simple]
**File:** `tests/unit/ui/screens/test_superweapon_input_modes.py`
**Tests:** `pytest tests/unit/ui/screens/test_superweapon_input_modes.py`

- [ ] [S07-CAT10-004] `Mode-setting and click-routing clusters` (lines 49-102, 159-212): Parametrize each cluster.

- [ ] Verify: `pytest tests/unit/ui/screens/test_superweapon_input_modes.py` passes; LOC delta ≈ 107

**Notes:** _(none yet)_

---

### Task 3.45: test_draw_helpers.py [Simple]
**File:** `tests/unit/ui/utils/test_draw_helpers.py`
**Tests:** `pytest tests/unit/ui/utils/test_draw_helpers.py`

- [ ] [S11-CAT10-008] `5 draw_stat_bar tests` (lines 53-110): Parametrize.

- [ ] Verify: `pytest tests/unit/ui/utils/test_draw_helpers.py` passes; LOC delta ≈ 58

**Notes:** _(none yet)_

---

### Task 3.46: test_resource_constants.py [Simple]
**File:** `tests/unit/ui/utils/test_resource_constants.py`
**Tests:** `pytest tests/unit/ui/utils/test_resource_constants.py`

- [ ] [S11-CAT10-009] `ResourceColors/RESOURCE_ORDER_PRIORITY tests` (lines 303-349): Keep as-is.

- [ ] Verify: `pytest tests/unit/ui/utils/test_resource_constants.py` passes; LOC delta ≈ 47

**Notes:** _(none yet)_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
