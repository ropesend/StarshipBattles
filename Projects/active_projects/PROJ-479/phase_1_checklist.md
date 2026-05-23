# Phase 1: CAT-4 Duplicate Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate the 21 verified CAT-4 duplicate-test findings from review `2026-05-20_210550_test-review`. Each item is a pair (or small cluster) of tests that exercise the same production path with only input values differing. Reclaim ~400 LOC by per-pair deletion or `@pytest.mark.parametrize` merge.

---

## Tasks

### Task 1.1: test_battle_panels_characterization.py — draw_battle_over triplet
**File:** `tests/unit/ui/test_battle_panels_characterization.py`
**Tests:** `pytest tests/unit/ui/test_battle_panels_characterization.py`

- [ ] Parametrize the 3 near-identical `draw_battle_over` tests (lines 435-468) on `(ships_config, expected_text)` → "TEAM 1 WINS" / "TEAM 2 WINS" / "DRAW".
- [ ] Verify: `pytest tests/unit/ui/test_battle_panels_characterization.py` passes; LOC delta ≈ -25.

### Task 1.2: test_propulsion_ability_bindings.py — 3 ability-class triplets
**File:** `tests/unit/modifiers/test_propulsion_ability_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_propulsion_ability_bindings.py`

- [ ] Parametrize the 3 ability classes (TestCombatPropulsionBindings, TestManeuveringThrusterBindings, TestStrategicMovementBindings, lines 10-121) on `(ability_class, stat_key, attr_name, base_value, mult_value, expected)`.
- [ ] Verify: `pytest tests/unit/modifiers/test_propulsion_ability_bindings.py` passes; LOC delta ≈ -75.

### Task 1.3: test_movement_phase_collaborator.py vs test_tick_phase_descriptors.py
**File:** `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

- [ ] Consolidate one of the `_CaptureResolver` tests (lines 89-133 collaborator vs 147-196 descriptor) as the canonical resolver-capture test; add a cross-reference comment in the other file.
- [ ] Verify: both files' tests pass; LOC delta ≈ -45.

### Task 1.4: test_ship_component_manager_di.py — 2 source-check tests
**File:** `tests/unit/builder/test_ship_component_manager_di.py`
**Tests:** `pytest tests/unit/builder/test_ship_component_manager_di.py`

- [ ] Parametrize the 2 identical source-check tests (lines 13-29) on `(module, attribute)`.
- [ ] Verify: `pytest tests/unit/builder/test_ship_component_manager_di.py` passes; LOC delta ≈ -8.

### Task 1.5: test_modifier_manager.py — legacy vs stateful coverage merge
**File:** `tests/unit/simulation/components/test_modifier_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_manager.py`

- [ ] Merge the legacy TestModifierManager class (lines 10-53) and the stateful test cluster (lines 186-283 + 55-75 + 312-379), but **verify Component.add_modifier's recalc path is still tested at Component level**. _(verification adjusted from review's plain "delete legacy" — the legacy tests exercise `Component.recalculate_stats` as a side effect that the stateful tests don't. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/simulation/components/test_modifier_manager.py` + Component-level recalc tests still cover the path; LOC delta ≈ -90.

### Task 1.6: test_process_colonize_validation.py — pod-type duplicates
**File:** `tests/unit/strategy/engine/test_process_colonize_validation.py`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py`

- [ ] Parametrize the 2 identical-except-pod_type tests (lines 181-241) on `pod_type` ∈ ["CONTINENTAL", "ICE_DWARF"] (now equivalent after Phase-3 universal pods).
- [ ] Verify: `pytest tests/unit/strategy/engine/test_process_colonize_validation.py` passes; LOC delta ≈ -28.

### Task 1.7: test_group_policies.py — overlap with parametrized invariants test
**File:** `tests/unit/strategy/data/test_group_policies.py`
**Tests:** `pytest tests/unit/strategy/data/test_group_policies.py`

- [ ] Delete `test_registry_loads_from_data_file` (lines 20-29) — the parametrized `test_policy_registry_structural_invariants` at line 31 covers the same ground with stronger assertions.
- [ ] Verify: `pytest tests/unit/strategy/data/test_group_policies.py` passes; LOC delta ≈ -10.

### Task 1.8: test_service_edge_cases.py — speed-value duplicates
**File:** `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_service_edge_cases.py`

- [ ] Parametrize `test_project_path_zero_speed` + `test_project_path_negative_speed` (lines 414-424) on `speed` ∈ [0.0, -5.0].
- [ ] Verify: `pytest tests/unit/strategy/fleet_navigation/test_service_edge_cases.py` passes; LOC delta ≈ -8.

### Task 1.9: test_planet_specific_colonization.py — 2 ColonizeValidator duplicates
**File:** `tests/unit/strategy/engine/test_planet_specific_colonization.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_specific_colonization.py`

- [ ] Consolidate the 2 ColonizeValidator tests (lines 309-337, 638-659) — they both create combat ship, fleet, validate, assert `result.is_valid is True`. Differ only in whether Empire is created.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_planet_specific_colonization.py` passes; LOC delta ≈ -25.

### Task 1.10: test_strategy_game_state_manager.py — TestAdvanceTurn pair
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py`

- [ ] Consolidate the structurally identical TestAdvanceTurnPerPlayerSwitch + TestAdvanceTurnRolloverBranch pair (lines 510-687); parametrize on `human_player_ids` to cover else-branch + rollover-branch.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py` passes; LOC delta ≈ -90.

### Task 1.11: test_turn_engine_lazy_properties.py — lazy-cache duplicate
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`

- [ ] Delete the lazy-cache variant test (lines 290-302) — identical isinstance + identity pattern as the 18-test cluster, only the double-access differs.
- [ ] Verify: `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` passes; LOC delta ≈ -12.

### Task 1.12: test_superweapon_command_handlers.py — SelfDestruct subsumed
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [ ] Extend the parametrized 5-handler test at lines 135-151 with a 6th case for SelfDestruct (preload `mock_fleet.ships`), then delete the dedicated TestSelfDestructCommandHandler test (lines 340-353).
- [ ] Verify: `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py` passes; LOC delta ≈ -13.

### Task 1.13: test_strategy_build_queue_manager.py — issue17 pair
**File:** `tests/unit/ui/screens/test_strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_build_queue_manager.py`

- [ ] Merge `test_issue17_on_active_player_changed_triggers_flush` (469-511) + `test_issue17_player_turn_change_flush_invokes_invalidate_widget_caches` (591-645) into a single test with sub-assertions for both flush + widget cache invalidation.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_build_queue_manager.py` passes; LOC delta ≈ -55.

### Task 1.14: test_modifier_loader_v2.py — hardened_mount overlap
**File:** `tests/unit/modifiers/test_modifier_loader_v2.py`
**Tests:** `pytest tests/unit/modifiers/test_modifier_loader_v2.py`

- [ ] Delete `test_modifier_v2_evaluate_effects` (lines 65-87) — fully subsumed by `test_hardened_mount_formula` (lines 129-158) which tests both param=2.0 and param=3.0.
- [ ] Verify: `pytest tests/unit/modifiers/test_modifier_loader_v2.py` passes; LOC delta ≈ -23.

### Task 1.15: test_component_health_manager.py — 3 invalid-input asserts
**File:** `tests/unit/simulation/test_component_health_manager.py`
**Tests:** `pytest tests/unit/simulation/test_component_health_manager.py`

- [ ] Parametrize the 3 `pytest.raises("amount must be numeric")` tests (lines 98-114) on `invalid_input` ∈ ["50", None, [10]].
- [ ] Verify: `pytest tests/unit/simulation/test_component_health_manager.py` passes; LOC delta ≈ -12.

### Task 1.16: test_fleet_aura_provider_identity.py — symmetric-mirror pair
**File:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`

- [ ] Parametrize the 2 symmetric-mirror tests (lines 126-179) on `(disabled_component, expected)`.
- [ ] Verify: `pytest tests/unit/simulation/combat/test_fleet_aura_provider_identity.py` passes; LOC delta ≈ -17.

### Task 1.17: test_planet_command_handlers.py — 8 handler classes × 2 tests
**File:** `tests/unit/strategy/engine/test_planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_command_handlers.py`

- [ ] Extract `test_planet_not_found` + `test_wrong_owner` into a parametrized helper. Use `@pytest.fixture(params=[...])` with the 8 handler classes (ActivatePlanetAbility + 7 others) so the 16 nearly-identical tests collapse to 1 parametrized test per concern.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_planet_command_handlers.py` passes; LOC delta ≈ -160.

### Task 1.18: test_tech_preset_loader.py — TestGetAvailable* twin classes
**File:** `tests/unit/strategy/data/test_tech_preset_loader.py`
**Tests:** `pytest tests/unit/strategy/data/test_tech_preset_loader.py`

- [ ] Consolidate TestGetAvailableComponents + TestGetAvailableModifiers (lines 191-259) into a parametrized class iterating over `(getter_method, expected_key, fixture_variant)`.
- [ ] Verify: `pytest tests/unit/strategy/data/test_tech_preset_loader.py` passes; LOC delta ≈ -35.

### Task 1.19: test_battle_service.py — 4 service-error pairs
**File:** `tests/unit/strategy/services/test_battle_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_battle_service.py`

- [ ] Parametrize the 2 pairs (add_ship/remove_ship × no_active_battle/after_battle_started) on `method_name` ∈ ["add_ship", "remove_ship"]. Lines 242-329.
- [ ] Verify: `pytest tests/unit/strategy/services/test_battle_service.py` passes; LOC delta ≈ -22.

### Task 1.20: test_save_load_ops.py — MockGameSession local copy
**File:** `tests/unit/strategy/save_game_service/test_save_load_ops.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/`

- [ ] Delete the local MockGameSession (lines 24-51) and import from sibling `conftest.py:12-39` (byte-identical).
- [ ] _(Note: this also lands HLP-001 cluster for this file; the cross-shard sweep in Phase 6 covers the other 4 copies.)_
- [ ] Verify: `pytest tests/unit/strategy/save_game_service/` passes; LOC delta ≈ -28.

### Task 1.21: test_warp_resources.py — make_warp_ship vs make_edge_ship
**File:** `tests/unit/strategy/fleet/test_warp_resources.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_warp_resources.py`

- [ ] Extract a shared mock-ship-creation helper for future consolidation; do not force-merge. _(verification adjusted from review's "merge ~70% overlap" — actual overlap is ~50%; signatures genuinely differ. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/strategy/fleet/test_warp_resources.py` passes; LOC delta ≈ -10.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2 — CAT-5 Fixture Bloat)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
