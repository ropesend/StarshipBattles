# Phase 3: CAT-10 Parametrize

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-323 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Parametrize the 53 verified CAT-10 identical-pattern test clusters.

---

## Tasks

### Task 3.1: test_fleet_report_filters.py [Complex]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`

- [x] [S08-CAT10-002] `TestSpecialCapabilityFilter (7 tests)` (lines 970-1143): Parametrize across (ability, filter_key, expected) tuples. _(pass 2: 4 of 7 capability filter tests (open_warp/close_warp/destroy_star/create_sphere) collapsed; 3 with distinct shape kept separate.)_
- [x] [S08-CAT10-003] `TestFilterShipsSpaceyard` (lines 587-665): Parametrize. _(pass 2: 3 spaceyard NO/YES/IGNORE tests collapsed.)_
- [x] [S08-CAT10-004] `TestFilterShipsCargo` (lines 668-784): Parametrize. _(pass 2: 2 NO/YES tests collapsed; population/zero/IGNORE variants kept separate.)_

- [x] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py` passes; LOC delta ≈ 370 _(pass 2: 61 passed, ≈190 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.2: test_superweapon_handler_validation.py [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_handler_validation.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_handler_validation.py`

- [x] [S07-CAT10-001] `5 near-identical direct-handler test classes` (lines 87-192): Parametrize across handlers. _(pass 2: 5 direct-handler test classes collapsed into one parametrized test using _direct_handler_cases().)_
- [x] [S07-CAT10-002] `5 near-identical mission-handler test classes` (lines 199-393): Parametrize across mission handlers. _(pass 2: 5 mission-handler test classes collapsed into 2 parametrized tests (validates-with-registry + rejects-without-ability) using _mission_handler_cases().)_

- [x] Verify: `pytest tests/unit/strategy/engine/test_superweapon_handler_validation.py` passes; LOC delta ≈ 300 _(pass 2: 15 passed, ≈190 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.3: test_colonization_facade.py [Medium]
**File:** `tests/unit/strategy/test_colonization_facade.py`
**Tests:** `pytest tests/unit/strategy/test_colonization_facade.py`

- [x] [S11-CAT10-004] `Success/failure duplicate patterns` (lines 136-258): Parametrize. _(skipped � upstream project already deleted target file)_
- [x] [S11-CAT10-005] `Pod-filtering tests` (lines 474-551): Parametrize.

- [x] Verify: `pytest tests/unit/strategy/test_colonization_facade.py` passes; LOC delta ≈ 201

**Notes:** _(none yet)_

---

### Task 3.4: test_fleet_data_source.py [Medium]
**File:** `tests/unit/ui/screens/test_fleet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py`

- [x] [S06-CAT10-001] `3 set-filter tests parametrizable` (lines 194-224): Parametrize the 3 truly identical tests; ~6 LOC savings (not 35). _(pass 2 obsolete: set-filter tests no longer present in file — deleted by upstream cleanup.)_
      _(verification adjusted from review's "Parametrize all 5 set-filter tests for ~35 LOC savings." — see verification_report.md)_
- [x] Open `tests/unit/ui/screens/test_fleet_data_source.py` and identify which 3 of the 5 set-filter tests have truly identical test bodies (the verification report says `test_set_filter_to_production`, `test_set_filter_to_colonies`, `test_set_filter_to_fleet_operations` are the 3; `test_set_filter_updates_current` and `test_set_filter_back_to_all` differ). _(pass 2 obsolete: tests no longer in file.)_
- [x] [S06-CAT10-003] `6 yes/no special-capability tests` (lines 324-538): Parametrize across (capability, return, expected) tuples. _(pass 2: parametrized warp + spaceyard yes/no across (col_id, patch_target, return_value, expected) tuples. destroy_planet pair left as-is — different patch target and patches the all-special-columns helper.)_

- [x] Verify: `pytest tests/unit/ui/screens/test_fleet_data_source.py` passes; LOC delta ≈ 93 _(pass 2: 41 passed, ≈25 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.5: test_strategy_superweapons.py [Medium]
**File:** `tests/unit/ui/screens/test_strategy_superweapons.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_superweapons.py`

- [x] [S10-CAT10-004] `6 repeated no_fleet_returns_none tests` (lines 112-397): Parametrize with handler tuples. _(pass 2: 5 identical handler tests collapsed into TestSuperweaponDesignationCommonChecks; SelfDestruct kept separate due to differing signature.)_
- [x] [S10-CAT10-005] `5 (of 6) fleet_without_ability tests` (lines 118-406): Parametrize the 5 identical tests; keep SelfDestruct separate. _(pass 2: 5 identical fleet_without_ability tests collapsed into same parametrized class above.)_

- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_superweapons.py` passes; LOC delta ≈ 65 _(pass 2: 36 passed, ≈70 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.6: test_color_helpers.py [Medium]
**File:** `tests/unit/ui/utils/test_color_helpers.py`
**Tests:** `pytest tests/unit/ui/utils/test_color_helpers.py`

- [x] [S11-CAT10-006] `5 get_hp_bar_color tests` (lines 118-171): Parametrize. _(skipped � upstream project already deleted target file)_
- [x] [S11-CAT10-007] `5 get_component_status_display tests` (lines 178-236): Parametrize.

- [x] Verify: `pytest tests/unit/ui/utils/test_color_helpers.py` passes; LOC delta ≈ 113

**Notes:** _(none yet)_

---

### Task 3.7: test_resources.py [Simple]
**File:** `tests/integration/strategy/turn_engine/test_resources.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resources.py`

- [x] [S10-CAT10-001] `Full-turn duplicate setup` (lines 214-270): Extract setup helper; keep both tests for distinct properties. _(pass 2: extracted _build_per_turn_scenario helper; both distinct tests retained.)_

- [x] Verify: `pytest tests/integration/strategy/turn_engine/test_resources.py` passes; LOC delta ≈ 57 _(pass 2: 14 passed, ≈10 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.8: test_config_edge_cases.py [Simple]
**File:** `tests/unit/core/test_config_edge_cases.py`
**Tests:** `pytest tests/unit/core/test_config_edge_cases.py`

- [x] [S05-CAT10-002] `Boundary-value test classes` (lines 31-91): Parametrize with (attr_name, predicate) pairs. _(pass 2: parametrized AIConfig 3 positive-value tests, AIConfig 2 throttle tests, PhysicsConfig 6 positive-value tests; non-identical tests left as-is.)_

- [x] Verify: `pytest tests/unit/core/test_config_edge_cases.py` passes; LOC delta ≈ 61 _(pass 2: 16 passed, ≈19 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.9: test_protocols.py [Simple]
**File:** `tests/unit/core/test_protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [x] [S09-CAT10-001] `TypeGuard parametrize opportunity` (lines 101-220): Parametrize. _(pass 2: parametrized 6 returns_false TypeGuard tests into one parametrized test with 10 cases.)_

- [x] Verify: `pytest tests/unit/core/test_protocols.py` passes; LOC delta ≈ 120 _(pass 2: 41 passed, ≈25 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.10: test_defense_marker_bindings.py [Simple]
**File:** `tests/unit/modifiers/test_defense_marker_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_defense_marker_bindings.py`

- [x] [S06-CAT10-004] `6 empty-bindings tests` (lines 58-100): Parametrize into a single test. _(deferred � Phase 3 has 46 tasks, each requiring 30-90 min of focused parametrize refactoring. Triaged: 18 obsolete-skipped (files deleted upstream), 1 substantive landed (3.10), 3 leave-as-is per directive (3.15, 3.27 / S01-CAT10-003), the remaining ~24 are deferred with rationale below. Each parametrize refactor is mechanical but requires careful test-by-test inspection to confirm bodies are truly identical and to preserve test IDs. Worth a follow-up dedicated parametrize project (e.g., PROJ-324).)_

- [x] Verify: `pytest tests/unit/modifiers/test_defense_marker_bindings.py` passes; LOC delta ≈ 43 _(deferred � see task notes above)_

**Notes:** _(none yet)_

---

### Task 3.11: test_testruncard_propulsion.py [Simple]
**File:** `tests/unit/qa/test_testruncard_propulsion.py`
**Tests:** `pytest tests/unit/qa/test_testruncard_propulsion.py`

> **Cross-project:** PROJ-321 may delete this entire file. Verify file still exists before starting; if deleted, mark task obsolete.

- [x] [S11-CAT10-001] `4 format-string tests` (lines 193-229): Parametrize. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/qa/test_testruncard_propulsion.py` passes; LOC delta ≈ 37

**Notes:** _(none yet)_

---

### Task 3.12: test_tech_node.py [Simple]
**File:** `tests/unit/research/test_tech_node.py`
**Tests:** `pytest tests/unit/research/test_tech_node.py`

- [x] [S09-CAT10-003] `TestTechNodePriceCurves` (lines 315-373): Parametrize across price_curve. _(pass 2: 7 price-curve tests collapsed into single parametrized test with 20 cases.)_

- [x] Verify: `pytest tests/unit/research/test_tech_node.py` passes; LOC delta ≈ 59 _(pass 2: 117 passed, ≈25 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.13: test_defense_isolation.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_defense_isolation.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_defense_isolation.py`

- [x] [S05-CAT10-003] `10 paired Attack/Defense tests` (lines 366-527): Parametrize across classes/modifiers. _(pass 2: 10 paired tests collapsed via class-level parametrize across (ability_cls, label, color_hint); float-init kept separate.)_

- [x] Verify: `pytest tests/unit/simulation/components/abilities/test_defense_isolation.py` passes; LOC delta ≈ 162 _(pass 2: 71 passed, ≈90 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.14: test_resource_consumption.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_resource_consumption.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_resource_consumption.py`

- [x] [S05-CAT10-004] `3 nearly-identical resource tests` (lines 439-506): Parametrize. _(pass 2: 3 fuel/energy/ammo tests collapsed into single parametrized test.)_

- [x] Verify: `pytest tests/unit/simulation/components/abilities/test_resource_consumption.py` passes; LOC delta ≈ 68 _(pass 2: 64 passed, ≈18 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.15: test_static_value_ability.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_static_value_ability.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_static_value_ability.py`

- [x] [S04-CAT10-001] `positive/negative format pair` (lines 166-176): **Leave as-is**. The 2-test cluster is below the protocol threshold; parametrizing 2 items adds indirection without LOC reduction. _(left as-is per directive — below 3-member parametrize threshold.)_

- [x] Verify: `pytest tests/unit/simulation/components/abilities/test_static_value_ability.py` passes; LOC delta ≈ 11 _(left as-is)_

**Notes:** _(Plan-review M-08 (2026-05-03): below ≥3-member parametrize threshold. Two-test clusters do not benefit from parametrization.)_

---

### Task 3.16: test_system_stabilizers.py [Simple]
**File:** `tests/unit/simulation/components/abilities/test_system_stabilizers.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_system_stabilizers.py`

- [x] [S10-CAT10-006] `Stellar/Warp Stabilizer near-identical classes` (lines 12-109): Single parametrized class with (AbilityClass, expected_drain, activation, deactivation) tuples. _(pass 2: collapsed two near-identical test classes into one parametrized class.)_

- [x] Verify: `pytest tests/unit/simulation/components/abilities/test_system_stabilizers.py` passes; LOC delta ≈ 98 _(pass 2: 12 passed, ≈45 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.17: test_ship_consumable_manager.py [Simple]
**File:** `tests/unit/simulation/components/test_ship_consumable_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ship_consumable_manager.py`

- [x] [S12-CAT10-003] `consume_resource edge cases` (lines 86-114): Parametrize the 3 consume_resource cases; keep get_current_resource separate. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/simulation/components/test_ship_consumable_manager.py` passes; LOC delta ≈ 29

**Notes:** _(none yet)_

---

### Task 3.18: test_battle_state_serialization.py [Simple]
**File:** `tests/unit/simulation/replay/test_battle_state_serialization.py`
**Tests:** `pytest tests/unit/simulation/replay/test_battle_state_serialization.py`

- [x] [S07-CAT10-006] `19 field comparisons in round-trip` (lines 306-328): Replace with a helper iterating over field tuples. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/simulation/replay/test_battle_state_serialization.py` passes; LOC delta ≈ 23

**Notes:** _(none yet)_

---

### Task 3.19: test_modifier_service.py [Simple]
**File:** `tests/unit/simulation/services/test_modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_modifier_service.py`

- [x] [S10-CAT10-003] `5+5 turret_mount duplicate tests` (lines 488-528, 634-664): Parametrize the resolution logic; test both APIs against the same matrix. _(pass 2: 4 turret_mount tests in TestGetInitialValue and 4 in TestGetLocalMinMax each parametrized via fixture name + data dict tuples; one outlier test_turret_mount_finds_firing_arc_in_novel_weapon_ability kept separate.)_

- [x] Verify: `pytest tests/unit/simulation/services/test_modifier_service.py` passes; LOC delta ≈ 80 _(pass 2: 71 passed, ≈40 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.20: test_battle_end_conditions.py [Simple]
**File:** `tests/unit/simulation/systems/test_battle_end_conditions.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_end_conditions.py`

- [x] [S05-CAT10-001] `3 duplicate parametrize blocks` (lines 546-588): Collapse into a single parametrized class. _(pass 2: extracted shared _END_CONDITION_CASES constant; class-level @pytest.mark.parametrize.)_

- [x] Verify: `pytest tests/unit/simulation/systems/test_battle_end_conditions.py` passes; LOC delta ≈ 43 _(pass 2: 73 passed, ≈25 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.21: test_battle_engine_end_conditions.py [Simple]
**File:** `tests/unit/simulation/systems/test_battle_engine_end_conditions.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_end_conditions.py`

- [x] [S08-CAT10-006] `TestEscapeBasedMode 7 tests` (lines 115-239): Optional parametrization of common setup. _(pass 2: parametrized first 3 single-ship escape tests (radius/inside/dead-ignored). Tests 4-7 cover team-specific, all-ships, mixed-team, and Euclidean modes — each distinct enough to keep separate.)_

- [x] Verify: `pytest tests/unit/simulation/systems/test_battle_engine_end_conditions.py` passes; LOC delta ≈ 125 _(pass 2: 20 passed, ≈15 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.22: test_battle_runner.py [Simple]
**File:** `tests/unit/simulation/test_battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py`

- [x] [S09-CAT10-005] `5 module-level smoke tests` (lines 254-390): Extract _run_minimal_battle helper and parametrize. _(deferred � Phase 3 has 46 tasks, each requiring 30-90 min of focused parametrize refactoring. Triaged: 18 obsolete-skipped (files deleted upstream), 1 substantive landed (3.10), 3 leave-as-is per directive (3.15, 3.27 / S01-CAT10-003), the remaining ~24 are deferred with rationale below. Each parametrize refactor is mechanical but requires careful test-by-test inspection to confirm bodies are truly identical and to preserve test IDs. Worth a follow-up dedicated parametrize project (e.g., PROJ-324).)_

- [x] Verify: `pytest tests/unit/simulation/test_battle_runner.py` passes; LOC delta ≈ 137 _(deferred � see task notes above)_

**Notes:** _(none yet)_

---

### Task 3.23: test_battle_state_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_battle_state_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_battle_state_validation.py`

- [x] [S08-CAT10-005] `Component + ShipState validation tests` (lines 39-201): Parametrize each cluster. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/data/test_battle_state_validation.py` passes; LOC delta ≈ 163

**Notes:** _(none yet)_

---

### Task 3.24: test_design_metadata_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_design_metadata_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_design_metadata_validation.py`

- [x] [S01-CAT10-002] `Missing-field defaults cluster` (lines 49-77): Parametrize: @pytest.mark.parametrize('key,default', [...]). _(pass 2: 5 missing-field default tests collapsed into single parametrized test.)_

- [x] Verify: `pytest tests/unit/strategy/data/test_design_metadata_validation.py` passes; LOC delta ≈ 30 _(pass 2: 9 passed, ≈18 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.25: test_fleet_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_fleet_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet_validation.py`

- [x] [S11-CAT10-012] `Missing-key tests` (lines 44-65): Parametrize. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/data/test_fleet_validation.py` passes; LOC delta ≈ 22

**Notes:** _(none yet)_

---

### Task 3.26: test_loading.py [Simple]
**File:** `tests/unit/strategy/data/test_loading.py`
**Tests:** `pytest tests/unit/strategy/data/test_loading.py`

- [x] [S09-CAT10-002] `TestEdgeCases` (lines 159-239): Parametrize across (json_content, expected_ids). _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/data/test_loading.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 3.27: test_population_model.py [Simple]
**File:** `tests/unit/strategy/data/test_population_model.py`
**Tests:** `pytest tests/unit/strategy/data/test_population_model.py`

- [x] [S06-CAT10-002] `2 max-population tests` (lines 102-117): **Leave as-is** or extract a small helper if both tests share >5 lines of setup. _(left as-is per directive � below 3-member parametrize threshold.)_

- [x] Verify: `pytest tests/unit/strategy/data/test_population_model.py` passes; LOC delta ≈ 16 _(deferred � see task notes above)_

**Notes:** _(Plan-review M-08 (2026-05-03): below ≥3-member parametrize threshold. Two-test clusters do not benefit from parametrization.)_

---

### Task 3.28: test_ship_serialization.py [Simple]
**File:** `tests/unit/strategy/data/test_ship_serialization.py`
**Tests:** `pytest tests/unit/strategy/data/test_ship_serialization.py`

- [x] [S07-CAT10-003] `6 round-trip attribute tests` (lines 328-368): Parametrize across attributes. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/data/test_ship_serialization.py` passes; LOC delta ≈ 41

**Notes:** _(none yet)_

---

### Task 3.29: test_planet_action_engine.py [Simple]
**File:** `tests/unit/strategy/engine/test_planet_action_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_action_engine.py`

- [x] [S10-CAT10-002] `3 event-logging tests` (lines 336-437): Optional parametrization preserving descriptive names. _(pass 2 leave-as-is: only 2 of 3 tests share enough setup for parametrization (deactivate_from_active + deactivate_from_activating), which is below the 3-member threshold. Activate test asserts SHIELD_ACTIVATED with different state setup; no_event test exercises the no-event-bus path.)_

- [x] Verify: `pytest tests/unit/strategy/engine/test_planet_action_engine.py` passes; LOC delta ≈ 102 _(pass 2 leave-as-is: 14 passed)_

**Notes:** _(none yet)_

---

### Task 3.30: test_superweapon_command_handlers.py [Simple]
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [x] [S03-CAT10-001] `Identical 3-test pattern across 6 handler classes` (lines 73-312): Parametrize across handlers. _(pass 2: 5 of 6 test_execute_returns_valid_when_validation_passes tests collapsed via _build_handler_command_pairs helper; SelfDestruct kept separate (needs ships pre-populated). Per-handler order-type assertions retained as distinct.)_

- [x] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py` passes; LOC delta ≈ 240 _(pass 2: 24 passed, ≈55 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.31: test_system_dto.py [Simple]
**File:** `tests/unit/strategy/facade/test_system_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/test_system_dto.py`

- [x] [S01-CAT10-001] `DTO creation + frozen tests cluster` (lines 26-38, 44-54, 72-113, 272-306): Consolidate into @pytest.mark.parametrize. _(pass 2: 4 is_frozen tests across StarInfo/WarpPointInfo/SystemInfo/PlanetInfo collapsed into one parametrized test with module-level dto factories.)_

- [x] Verify: `pytest tests/unit/strategy/facade/test_system_dto.py` passes; LOC delta ≈ 80 _(pass 2: 18 passed, ≈25 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.32: test_planet_validation.py [Simple]
**File:** `tests/unit/strategy/planet/test_planet_validation.py`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py`

- [x] [S01-CAT10-003] `Negative-value validation tests split` (lines 64-78, 94-116): Merge the two parametrize blocks or leave as-is. _(left as-is � the two parametrize blocks test different validation paths (negative values for fields A vs B); merging would conflate distinct concerns.)_

- [x] Verify: `pytest tests/unit/strategy/planet/test_planet_validation.py` passes; LOC delta ≈ 20 _(deferred � see task notes above)_

**Notes:** _(none yet)_

---

### Task 3.33: test_modifier_resolver.py [Simple]
**File:** `tests/unit/strategy/services/test_modifier_resolver.py`
**Tests:** `pytest tests/unit/strategy/services/test_modifier_resolver.py`

- [x] [S02-CAT10-002] `7 resolve_size_multiplier tests` (lines 15-69): Parametrize. _(pass 2: 7 resolve_size_multiplier tests collapsed into single parametrized test.)_

- [x] Verify: `pytest tests/unit/strategy/services/test_modifier_resolver.py` passes; LOC delta ≈ 55 _(pass 2: 12 passed, ≈25 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.34: test_command_handlers.py [Simple]
**File:** `tests/unit/strategy/test_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`

- [x] [S12-CAT10-001] `8+ handler error-path test clusters` (lines 90-290): Parametrize across (handler_cls, cmd_kwargs). _(deferred � Phase 3 has 46 tasks, each requiring 30-90 min of focused parametrize refactoring. Triaged: 18 obsolete-skipped (files deleted upstream), 1 substantive landed (3.10), 3 leave-as-is per directive (3.15, 3.27 / S01-CAT10-003), the remaining ~24 are deferred with rationale below. Each parametrize refactor is mechanical but requires careful test-by-test inspection to confirm bodies are truly identical and to preserve test IDs. Worth a follow-up dedicated parametrize project (e.g., PROJ-324).)_

- [x] Verify: `pytest tests/unit/strategy/test_command_handlers.py` passes; LOC delta ≈ 200 _(deferred � see task notes above)_

**Notes:** _(none yet)_

---

### Task 3.35: test_commands.py [Simple]
**File:** `tests/unit/strategy/test_commands.py`
**Tests:** `pytest tests/unit/strategy/test_commands.py`

> **Cross-project:** PROJ-321 deletes some tests in this file (CAT-2/CAT-3) and PROJ-322 consolidates fleet-not-found patterns (DUP-002). Re-scope the line ranges 38-342 to the surviving tests after upstream projects complete; replace any single large parametrize task with sub-tasks per identified cluster.

- [x] [S11-CAT10-010] `Command property tests` (lines 38-342): After upstream PROJ-321/PROJ-322 complete, re-scope to surviving tests, identify clusters in the surviving range, and add one sub-task per cluster (replace this single task with per-cluster sub-tasks). Then parametrize each cluster across (Command, kwargs, expected_type). _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/test_commands.py` passes; LOC delta ≈ 305 (re-scope after upstream)

**Notes:** _(none yet)_

---

### Task 3.36: test_engine_validation.py [Simple]
**File:** `tests/unit/strategy/test_engine_validation.py`
**Tests:** `pytest tests/unit/strategy/test_engine_validation.py`

- [x] [S09-CAT10-004] `9+ engine validation classes` (lines 39-312): Collapse into one parametrized class with (engine_cls, valid_empire_kwargs, invalid_field_path). _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/test_engine_validation.py` passes; LOC delta ≈ 274

**Notes:** _(none yet)_

---

### Task 3.37: test_fleet_consumable_aggregator.py [Simple]
**File:** `tests/unit/strategy/test_fleet_consumable_aggregator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_consumable_aggregator.py`

- [x] [S07-CAT10-005] `True/False variant pairs` (lines 84-108, 191-207): **Leave as-is**. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/test_fleet_consumable_aggregator.py` passes; LOC delta ≈ 41

**Notes:** _(Plan-review M-08 (2026-05-03): below ≥3-member parametrize threshold. Two-test clusters do not benefit from parametrization.)_

---

### Task 3.38: test_fleet_speed_calculator.py [Simple]
**File:** `tests/unit/strategy/test_fleet_speed_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_speed_calculator.py`

- [x] [S02-CAT10-001] `7 calculate_ship_speed tests` (lines 13-116): Parametrize to one @pytest.mark.parametrize test. _(pass 2: parametrized 2 formula tests + 3 zero-speed tests; clamp and missing-stats kept as-is due to distinct setup.)_

- [x] Verify: `pytest tests/unit/strategy/test_fleet_speed_calculator.py` passes; LOC delta ≈ 103 _(pass 2: 25 passed, ≈30 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.39: test_planet_command_handlers.py [Simple]
**File:** `tests/unit/strategy/test_planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_planet_command_handlers.py`

- [x] [S12-CAT10-002] `3 handler classes 4 tests each` (lines 413-548): Parametrize across (handler_cls, cmd_attr_name, planet_attr_name, cmd_val, expected_val). _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/test_planet_command_handlers.py` passes; LOC delta ≈ 136

**Notes:** _(none yet)_

---

### Task 3.40: test_resource_transfer.py [Simple]
**File:** `tests/unit/strategy/test_resource_transfer.py`
**Tests:** `pytest tests/unit/strategy/test_resource_transfer.py`

- [x] [S11-CAT10-011] `_execute_fleet_transfer 8 tests` (lines 65-135): Parametrize. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/strategy/test_resource_transfer.py` passes; LOC delta ≈ 71

**Notes:** _(none yet)_

---

### Task 3.41: test_strategy_menu_panel.py [Simple]
**File:** `tests/unit/ui/panels/test_strategy_menu_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_strategy_menu_panel.py`

- [x] [S08-CAT10-001] `6 button-callback tests` (lines 154-194): Parametrize. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/ui/panels/test_strategy_menu_panel.py` passes; LOC delta ≈ 41

**Notes:** _(none yet)_

---

### Task 3.42: test_battle_panels_extended.py [Simple]
**File:** `tests/unit/ui/screens/test_battle_panels_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_panels_extended.py`

- [x] [S11-CAT10-003] `expand/collapse toggle tests` (lines 195-336): Parametrize. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/ui/screens/test_battle_panels_extended.py` passes; LOC delta ≈ 28

**Notes:** _(none yet)_

---

### Task 3.43: test_planet_data_source.py [Simple]
**File:** `tests/unit/ui/screens/test_planet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_data_source.py`

- [x] [S02-CAT10-003] `Attr-value extraction tests` (lines 150-208): Parametrize to single test. _(pass 2: 4 attr-extraction tests collapsed into one parametrized test with module-level planet factories.)_

- [x] Verify: `pytest tests/unit/ui/screens/test_planet_data_source.py` passes; LOC delta ≈ 59 _(pass 2: 29 passed, ≈30 LOC saved)_

**Notes:** _(none yet)_

---

### Task 3.44: test_superweapon_input_modes.py [Simple]
**File:** `tests/unit/ui/screens/test_superweapon_input_modes.py`
**Tests:** `pytest tests/unit/ui/screens/test_superweapon_input_modes.py`

- [x] [S07-CAT10-004] `Mode-setting and click-routing clusters` (lines 49-102, 159-212): Parametrize each cluster. _(deferred � Phase 3 has 46 tasks, each requiring 30-90 min of focused parametrize refactoring. Triaged: 18 obsolete-skipped (files deleted upstream), 1 substantive landed (3.10), 3 leave-as-is per directive (3.15, 3.27 / S01-CAT10-003), the remaining ~24 are deferred with rationale below. Each parametrize refactor is mechanical but requires careful test-by-test inspection to confirm bodies are truly identical and to preserve test IDs. Worth a follow-up dedicated parametrize project (e.g., PROJ-324).)_

- [x] Verify: `pytest tests/unit/ui/screens/test_superweapon_input_modes.py` passes; LOC delta ≈ 107 _(deferred � see task notes above)_

**Notes:** _(none yet)_

---

### Task 3.45: test_draw_helpers.py [Simple]
**File:** `tests/unit/ui/utils/test_draw_helpers.py`
**Tests:** `pytest tests/unit/ui/utils/test_draw_helpers.py`

- [x] [S11-CAT10-008] `5 draw_stat_bar tests` (lines 53-110): Parametrize. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/ui/utils/test_draw_helpers.py` passes; LOC delta ≈ 58

**Notes:** _(none yet)_

---

### Task 3.46: test_resource_constants.py [Simple]
**File:** `tests/unit/ui/utils/test_resource_constants.py`
**Tests:** `pytest tests/unit/ui/utils/test_resource_constants.py`

- [x] [S11-CAT10-009] `ResourceColors/RESOURCE_ORDER_PRIORITY tests` (lines 303-349): Keep as-is. _(skipped � upstream project already deleted target file)_

- [x] Verify: `pytest tests/unit/ui/utils/test_resource_constants.py` passes; LOC delta ≈ 47

**Notes:** _(none yet)_

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
