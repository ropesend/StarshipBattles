# Phase 1: CAT-4 Duplicate Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate the 21 verified CAT-4 duplicate-test findings from review `2026-05-20_210550_test-review`. Each item is a pair (or small cluster) of tests that exercise the same production path with only input values differing. Reclaim ~400 LOC by per-pair deletion or `@pytest.mark.parametrize` merge.

---

## Tasks

### Task 1.1: test_battle_panels_characterization.py — draw_battle_over triplet
**File:** `tests/unit/ui/test_battle_panels_characterization.py`
**Tests:** `pytest tests/unit/ui/test_battle_panels_characterization.py`

- [x] Parametrize the 3 near-identical `draw_battle_over` tests (lines 435-468) on `(ships_config, expected_text)` → "TEAM 1 WINS" / "TEAM 2 WINS" / "DRAW".
- [x] Verify: `pytest tests/unit/ui/test_battle_panels_characterization.py` passes; LOC delta ≈ -25.

### Task 1.2: test_propulsion_ability_bindings.py — 3 ability-class triplets
**File:** `tests/unit/modifiers/test_propulsion_ability_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_propulsion_ability_bindings.py`

- [x] Parametrize the 3 ability classes (TestCombatPropulsionBindings, TestManeuveringThrusterBindings, TestStrategicMovementBindings, lines 10-121) on `(ability_class, stat_key, attr_name, base_value, mult_value, expected)`.
- [x] Verify: `pytest tests/unit/modifiers/test_propulsion_ability_bindings.py` passes; LOC delta ≈ -75.

### Task 1.3: test_movement_phase_collaborator.py vs test_tick_phase_descriptors.py
**File:** `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

- [x] Consolidate one of the `_CaptureResolver` tests (lines 89-133 collaborator vs 147-196 descriptor) as the canonical resolver-capture test; add a cross-reference comment in the other file.
- [x] Verify: both files' tests pass; LOC delta ≈ -45.

_(Kept descriptor test canonical — it exercises the public hook + PROJ-FMS-B audit Fix 1. Replaced collaborator-test body with cross-reference comment.)_

### Task 1.4: test_ship_component_manager_di.py — 2 source-check tests
**File:** `tests/unit/simulation/entities/test_ship_component_manager_di.py` _(actual path; plan listed `tests/unit/builder/` which doesn't exist)_
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager_di.py`

- [x] Parametrize the 2 identical source-check tests (lines 13-29) on `(module, attribute)`.
- [x] Verify: tests pass; LOC delta ≈ -8.

### Task 1.5: test_modifier_manager.py — legacy vs stateful coverage merge
**File:** `tests/unit/simulation/components/test_modifier_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_modifier_manager.py`

- [x] Merge the legacy TestModifierManager class (lines 10-53) and the stateful test cluster — replaced bulk legacy tests with a 3-test `TestComponentModifierFacade` smoke class covering Component-level facade delegation. Recalc side-effect remains covered by `test_component_clone_propagates_ship`, `test_component_stats_calculator`, `test_size_mount_sub_one`, `test_facing_angle_modifier`.
- [x] Verify: `pytest tests/unit/simulation/components/test_modifier_manager.py` + Component-level recalc tests still cover the path; LOC delta ≈ -90.

### Task 1.6: test_process_colonize_validation.py — pod-type duplicates
**File:** `tests/unit/strategy/engine/test_process_colonize_validation.py`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py`

- [x] Parametrize the 2 identical-except-pod_type tests (lines 181-241) on `pod_type` ∈ ["CONTINENTAL", "ICE_DWARF"] (now equivalent after Phase-3 universal pods).
- [x] Verify: passes; LOC delta ≈ -28.

### Task 1.7: test_group_policies.py — overlap with parametrized invariants test
**File:** `tests/unit/strategy/data/test_group_policies.py`
**Tests:** `pytest tests/unit/strategy/data/test_group_policies.py`

- [x] Delete `test_registry_loads_from_data_file` — done.
- [x] Verify: passes; LOC delta ≈ -10.

### Task 1.8: test_service_edge_cases.py — speed-value duplicates
**File:** `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_service_edge_cases.py`

- [x] Parametrized on `speed` ∈ [0.0, -5.0].
- [x] Verify: passes; LOC delta ≈ -8.

### Task 1.9: test_planet_specific_colonization.py — 2 ColonizeValidator duplicates
**File:** `tests/unit/strategy/engine/test_planet_specific_colonization.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_specific_colonization.py`

- [x] Consolidated: deleted the duplicate at 638; the earlier `TestColonizeWithWrongPod::test_colonize_without_drop_pod_succeeds_at_command_time` is now the canonical. File actually lives at `tests/integration/colonization/test_planet_specific_colonization.py` (plan path was incorrect).
- [x] Verify: passes; LOC delta ≈ -25.

### Task 1.10: test_strategy_game_state_manager.py — TestAdvanceTurn pair
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py`

- [x] Consolidated the 2 structurally-identical test pairs (`applies_helper`, `runs_helper_after_sync_active_empire`) into module-scope parametrized tests on `(human_player_ids, expected_next_id, need_display_patch)`. Branch-specific tests (clears_selection / auto_selects_home / opens_event_log / no_double_fire) kept in their original classes since they carry distinct assertions.
- [x] Verify: 67 tests pass; LOC delta ≈ -65 effective (slightly less than the -90 planned because branch-specific tests were preserved per the user warning about real edge cases).

### Task 1.11: test_turn_engine_lazy_properties.py — lazy-cache duplicate
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`

- [x] Deleted `test_planet_modifier_effect_engine_property_returns_cached_instance`.
- [x] Verify: passes; LOC delta ≈ -12.

### Task 1.12: test_superweapon_command_handlers.py — SelfDestruct subsumed
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [x] Extended parametrized matrix to 6 cases with `needs_ships` flag for SelfDestruct; deleted dedicated test.
- [x] Verify: passes; LOC delta ≈ -13.

### Task 1.13: test_strategy_build_queue_manager.py — issue17 pair
**File:** `tests/unit/ui/screens/test_strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_build_queue_manager.py`

- [x] Plan referenced `test_issue17_on_active_player_changed_triggers_flush` which had already been refactored away in earlier work — the actual duplicate was `test_open_after_active_player_change_calls_on_active_player_changed` (weaker subset of `test_issue17_player_turn_change_flush_invokes_invalidate_widget_caches`). Deleted the weaker test.
- [x] Verify: passes; LOC delta ≈ -45.

### Task 1.14: test_modifier_loader_v2.py — hardened_mount overlap
**File:** `tests/unit/modifiers/test_modifier_loader_v2.py`
**Tests:** `pytest tests/unit/modifiers/test_modifier_loader_v2.py`

- [x] Deleted `test_modifier_v2_evaluate_effects`.
- [x] Verify: passes; LOC delta ≈ -23.

### Task 1.15: test_component_health_manager.py — 3 invalid-input asserts
**File:** `tests/unit/simulation/test_component_health_manager.py`
**Tests:** `pytest tests/unit/simulation/test_component_health_manager.py`

- [x] Parametrized.
- [x] Verify: passes; LOC delta ≈ -12. _(Actual file path: `tests/unit/simulation/components/test_component_health_manager.py`)_

### Task 1.16: test_fleet_aura_provider_identity.py — symmetric-mirror pair
**File:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`

- [x] Parametrized.
- [x] Verify: passes; LOC delta ≈ -17. _(Added missing `import pytest` to top of file.)_

### Task 1.17: test_planet_command_handlers.py — 8 handler classes × 2 tests
**File:** `tests/unit/strategy/engine/test_planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_command_handlers.py`

- [x] Added module-scope parametrized matrix `_HANDLER_CASES` covering all 8 handlers × 2 concerns (planet_not_found, wrong_owner) = 16 parametrized cases. Removed redundant per-class tests; kept ActivatePlanetAbility + DeactivatePlanetAbility companion message-substring tests ("not found" / "does not belong") since they assert beyond the basic contract.
- [x] Verify: 36 tests pass.

### Task 1.18: test_tech_preset_loader.py — TestGetAvailable* twin classes
**File:** `tests/unit/strategy/data/test_tech_preset_loader.py`
**Tests:** `pytest tests/unit/strategy/data/test_tech_preset_loader.py`

- [x] Consolidated into `TestGetAvailableComponentsAndModifiers` with 3 parametrized methods. Kept components-only `test_get_components_raises_for_missing_preset` (the modifiers class lacked the equivalent). _(Actual path: `tests/unit/simulation/systems/test_tech_preset_loader.py`)_
- [x] Verify: 44 tests pass; LOC delta ≈ -35.

### Task 1.19: test_battle_service.py — 4 service-error pairs
**File:** `tests/unit/strategy/services/test_battle_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_battle_service.py`

- [x] Parametrized the 2 pairs at module scope with `_call_with_method` adapter. _(Actual path: `tests/unit/simulation/services/test_battle_service.py`)_
- [x] Verify: 77 tests pass; LOC delta ≈ -22.

### Task 1.20: test_save_load_ops.py — MockGameSession local copy
**File:** `tests/unit/strategy/save_game_service/test_save_load_ops.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/`

- [x] Deleted local MockGameSession; imported from sibling conftest.
- [x] _(HLP-001 for this file landed; other 4 copies covered in Phase 6.)_
- [x] Verify: 61 tests pass; LOC delta ≈ -28.

### Task 1.21: test_warp_resources.py — make_warp_ship vs make_edge_ship
**File:** `tests/unit/strategy/fleet/test_warp_resources.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_warp_resources.py`

- [x] Extracted module-level `_build_mock_warp_ship` helper; both fixtures now delegate while preserving their original signatures.
- [x] Verify: 21 tests pass; LOC delta ≈ -10.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2 — CAT-5 Fixture Bloat)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
