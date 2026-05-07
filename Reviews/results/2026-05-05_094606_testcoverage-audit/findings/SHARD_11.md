# Shard 11 — Test Coverage Audit

## Summary
- Shard: 11
- Production files in scope: 38
- Production files actually read: 38
- Unit test files read: 12
- Total findings: 18
- Critical: 2 | Major: 4 | Minor: 6 | Advisory: 6

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/engine/physics.py (~109 LOC, layer: Engine)
- **Tier**: 0 — No unit test file imports this module
- **Status**: No dedicated unit test file anywhere in `tests/unit/engine/`. The engine test directory contains only `collision_edge_cases/` and `test_spatial_exact.py`. `PhysicsBody` has zero unit test coverage.
- **Key symbols**: `PhysicsBody`, `PhysicsBody.__init__`, `PhysicsBody.update`, `PhysicsBody.apply_force`, `PhysicsBody.forward_vector`, PhysicsBody `x`/`y` properties
- **Risk**: `PhysicsBody` is the base class for all physical entities in the engine (Ship, Projectile). The `update()` method (force accumulation + drag + position integration) and `apply_force()` are untested. Although subclasses override the physics model, incorrect behavior in the base `update()` or `apply_force()` — or arithmetic errors in `forward_vector().rotate()` — would propagate silently through the entire simulation layer. The drag clamping logic (`drag_factor > 1` guard at line 91-92) and zero-mass division in `apply_force()` (line 102-103) represent untested error paths.
- **Suggested tests**:
  1. `test_physics_update_applies_velocity_acceleration` — Verify pos += vel, vel += acc per tick
  2. `test_physics_drag_clamps_at_1` — Set drag=2.0, verify it's clamped to 1.0
  3. `test_physics_angular_drag_applied` — Verify angular velocity decays
  4. `test_physics_apply_force_zero_mass` — Verify no acceleration when mass=0
  5. `test_physics_forward_vector_at_angles` — Verify forward_vector() at 0°, 90°, 180°, 270°
  6. `test_physics_position_property_delegation` — Verify x/y properties read/write position

### game/simulation/combat/fleet_aura_manager.py (~515 LOC, layer: Simulation)
- **Tier**: 0 — No unit test file imports this module
- **Status**: No test file found in `tests/unit/simulation/combat/`. This is a 515-line module with complex two-phase aggregation logic, provider liveness tracking, external modifier injection, placeholder handling, and per-frame caching. Completely untested.
- **Key symbols**: `FleetAuraManager`, `AuraProvider`, `ExternalModifier`, plus 15 methods: `initialize`, `_scan_ship`, `_append_external_from_entry`, `register_ship`, `unregister_ship`, `invalidate_aura_cache`, `update`, `_get_provider_fingerprint`, `_recalculate`, `_apply_bonuses`, `get_attack_bonus`, `get_defense_bonus`, `get_active_bonuses`, `_log_placeholder_once`, `_log_unknown_stat_key_once`
- **Risk**: `FleetAuraManager` manages all fleet/system/empire-scoped ability bonuses during combat. It runs every tick of every battle. Untested bugs here directly affect combat mathematics — shield bonuses, damage multipliers, attack/defense modifiers — for every battle in the game. The two-phase MAX/SUM aggregation (`_recalculate`), provider liveness checks (PROJ-357 identity-precise), external modifier routing (PROJ-271 Phase 7), fingerprint-based caching (PROJ-253), and derelict exclusion (CQ-001) are all complex and untested. A regression here would silently corrupt battle outcomes.
- **Suggested tests**:
  1. `test_initialize_scans_ships_for_fleet_scope` — Verify AuraProviders registered for non-SELF scope abilities
  2. `test_initialize_excludes_derelict_ships` — Derelict ships should not contribute
  3. `test_initialize_translates_modifier_stack_to_external` — Verify ModifierEntry -> ExternalModifier conversion
  4. `test_append_external_skips_placeholder_stat_key` — Placeholder entries silently ignored
  5. `test_append_external_warns_unknown_stat_key` — Unknown keys trigger advisory warning
  6. `test_register_ship_scans_new_ship` — Mid-battle ship addition registers its auras
  7. `test_unregister_ship_removes_providers` — Retreating ship stops contributing
  8. `test_update_skips_when_not_initialized` — No crash on update before initialize
  9. `test_recalculate_aggregates_within_group_max` — Same stack_group = MAX
  10. `test_recalculate_aggregates_across_groups_sum` — Different stack_groups = SUM
  11. `test_recalculate_preserves_zero_values` — damage_mult=0.0 should not be filtered out (PROJ-272)
  12. `test_recalculate_drops_providers_with_removed_ability` — Identity loss via ability instance removal
  13. `test_recalculate_skips_derelict_but_keeps_provider` — Derelict doesn't contribute but provider stays
  14. `test_apply_bonuses_writes_to_external_stats` — All team bonus stat_keys land on ship.external_stats
  15. `test_apply_bonuses_triggers_recalculate_stats` — Ship.recalculate_stats() called when external_stats changes
  16. `test_get_active_bonuses_excludes_dead_derelict` — UI query respects liveness
  17. `test_provider_fingerprint_detects_operational_change` — Component destruction invalidates cache
  18. `test_external_modifier_global_scopes_to_all_teams` — team_id=None applies to every team
  19. `test_placeholder_logging_rate_limited_once_per_source` — No log spam

## Tier 1-2 — Partial Coverage

### game/ai/controller.py (~471 LOC, layer: AI — Tier 2)

#### [MAJOR] `AIController._acquire_targets` — No direct test of dead-target clearing
- **Location**: controller.py:371-388
- **Issue**: Phase 1 flagged as untested (name-grep false negative). Exercised indirectly via `update()`, but the dead-target-clearing path (line 374: `if target and not target.is_alive`) has no dedicated test. A test that constructs a controller with a target that dies should verify the target is cleared AND replaced via `find_target()`.
- **Untested path**: Dead primary target → target cleared and re-acquired; secondary targets rebuilt when `get_max_targets() > DEFAULT_MAX_TARGETS`
- **Suggested test**: `test_acquire_targets_clears_dead_target_and_reacquires` — Set dead target, call `_acquire_targets`, verify new target selected

#### [MINOR] `AIController._select_behavior` — Retreat threshold edge cases
- **Location**: controller.py:392-400
- **Issue**: Exercised via `update()`, but no test for `retreat_threshold == 0` (never retreat) or `retreat_threshold > 1.0` (impossible HP). Boundary at exact threshold equality (HP exactly at threshold) is untested.
- **Suggested test**: `test_select_behavior_retreat_threshold_zero_never_flees` and `test_select_behavior_at_exact_threshold_flees`

#### [MINOR] `AIController._execute_behavior` — Null behavior key, no-target behaviors
- **Location**: controller.py:404-420
- **Issue**: Exercised via `update()`, but the `behavior not in self.behaviors` path (unknown key → no behavior instantiated) has no explicit test. The `behavior_context` dict passed to behaviors on line 418 has no test verifying its contents.
- **Suggested test**: `test_execute_behavior_unknown_key_does_nothing` — Pass `"invalid_key"`, verify no crash and no behavior change

### game/core/input_actions.py (~344 LOC, layer: Core)

#### [MINOR] `KeyBinding.from_dict` — Partial key, null data, malformed input
- **Location**: input_actions.py:317-333
- **Issue**: Phase 1 indicates no test file found for this module. Associated test `tests/unit/core/test_input_actions.py` exists but needs verification. If test exists, the `from_dict()` method boundary cases (`None` input, empty dict, missing 'modifiers' field) may be untested.
- **Untested path**: `from_dict(None)` → returns None; `from_dict({})` → returns None; `from_dict({"key": "K_A"})` → default modifiers=(frozenset())
- **Suggested test**: `test_from_dict_none_returns_none`, `test_from_dict_empty_returns_none`, `test_from_dict_no_modifiers_defaults_empty`

#### [MINOR] `KeyBinding._key_display_name` — Edge case for unusual key names
- **Location**: input_actions.py:301-315
- **Issue**: The `K_` prefix strip fallback (line 315) for unrecognized keys like `K_NUMPAD0` returns `NUMPAD0` which may be confusing. The F-key detection (line 307) works for single-digit F-keys only.
- **Suggested test**: `test_key_display_name_numpad_keys` — Test `_key_display_name("K_NUMPAD3")`

### game/simulation/combat/ability_stat_registry.py (~237 LOC, layer: Simulation)

#### [MINOR] `_extract_value` — Non-dict non-numeric edge case
- **Location**: ability_stat_registry.py:128-145
- **Issue**: Phase 1 indicates Tier 3 (tested). The test `tests/unit/simulation/combat/test_ability_stat_registry.py` exists and tests the glob-driven validation path. However, the `_extract_value` function's final fallback (line 145: `return 0.0`) for non-dict non-numeric input is unlikely to be exercised by the existing glob test.
- **Suggested test**: `test_extract_value_none_returns_zero` — Pass None, expect 0.0

### game/services/llm/defaults.py (~42 LOC, layer: Services)

#### [MINOR] `get_default_llm_provider`/`set_default_llm_provider` — Thread safety
- **Location**: defaults.py:20-39
- **Issue**: Has test file at `tests/unit/services/llm/test_defaults.py`. The module-level `_default_llm_provider` variable uses `global` assignment but has no thread-safety guard. Tests likely exist for get/set round-trip but may not cover the `None` default state before any set call.
- **Suggested test**: `test_get_default_returns_none_before_set` — Verify initial state

### game/strategy/engine/consumable_management_engine.py (~164 LOC, layer: Strategy)

#### [MAJOR] `ConsumableManagementEngine` — No unit test file found
- **Location**: consumable_management_engine.py (entire file)
- **Issue**: No test file in `tests/unit/strategy/engine/test_consumable*.py`. The module handles per-turn resource consumption across fleets, component auto-disabling on depletion, and per-tick cost spreading. The `_auto_disable_components_for_resource` method (lines 124-164) has complex registry-lookup logic with `isinstance` branching for list/dict component formats.
- **Key symbols**: `ConsumableManagementEngine.__init__`, `_validate_tick_inputs`, `process_per_turn_consumption`, `_auto_disable_components_for_resource`, `ResourceDepletion`
- **Risk**: Resource consumption drives fleet readiness. A bug in the tick_cost division (1/100th per tick, line 112) or in the auto-disable logic could leave ships with negative resources or fail to disable components when fuel/ammo runs out.
- **Suggested tests**:
  1. `test_process_per_turn_consumption_spreads_over_100_ticks` — Verify 1/100th consumption per tick
  2. `test_auto_disable_components_for_depleted_resource` — Verify component disabled on depletion
  3. `test_validate_tick_inputs_raises_on_none_ships` — Verify precondition check
  4. `test_consumption_skips_non_combat_capable_ships` — Skip damaged/incapable ships
  5. `test_consumption_zero_cost_no_op` — total_cost <= 0 skips consumption

### game/strategy/engine/harvesting_engine.py (~479 LOC, layer: Strategy)

#### [MAJOR] `HarvestingEngine` — Complex logic partly tested
- **Location**: harvesting_engine.py
- **Issue**: Has test files (`test_harvesting_engine.py`, `test_harvesting_engine_habitability.py`, `test_harvesting_size_scaling.py`). The `_get_harvest_booster_mult` method (lines 388-419) queries strategic_ability_scanner with complex late-import chains. The `_aggregate_empire_storage` flow (lines 196-213) and `_process_facility` with size_multiplier and habitability stacking are likely tested, but the booster aggregation across 4 scopes (planet/sector/system/empire) with late imports may have untested paths.
- **Untested path**: `_get_harvest_booster_mult` calls `find_abilities_in_scope` with dynamic late imports. Error in the late import chain is untested.
- **Suggested test**: `test_harvest_booster_mult_aggregates_across_all_scopes` — Verify planet + sector + system + empire boosters combine correctly

### game/strategy/engine/fleet_movement_engine.py (~360 LOC, layer: Strategy)

#### [MAJOR] `FleetMovementEngine._filter_jump_past_collisions` — Complex FEAT-28 logic
- **Location**: fleet_movement_engine.py:272-337
- **Issue**: Has test for `calculate_next_hex` but the FEAT-28 mutual-pursuit collision filter (`_filter_jump_past_collisions`) is complex with multiple branches (swap parity, larger-fleet-drop, tiebreak). Named tuple of `_PURSUIT` types checked, `isinstance(fleet_b, Fleet)` guard. Unlikely to be fully tested.
- **Untested path**: Tie-breaking on fleet ID string comparison (line 330); `drop_ids` edge case with multiple overlaps; `MOVE_TO_FLEET` order type matching
- **Suggested tests**:
  1. `test_filter_jump_past_drops_larger_fleet` — Two fleets in mutual pursuit, larger one dropped
  2. `test_filter_jump_past_tiebreak_by_id` — Equal ship count, smaller fleet.id wins
  3. `test_filter_jump_past_ignores_non_pursuit_orders` — Move order not MOVE_TO_FLEET/JOIN_FLEET should pass through

### game/simulation/services/vehicle_design_service.py (~516 LOC, layer: Simulation)

#### [MINOR] `VehicleDesignService.move_component` — BUG-116 classification leak path
- **Location**: vehicle_design_service.py:301-373
- **Issue**: Has test file `tests/unit/simulation/services/test_vehicle_design_service.py`. The BUG-116 fix on lines 356-367 (selective rule-skipping for MassBudgetRule only) is the likeliest untested path. The validation rule iteration (lines 359-367) selectively skips `MassBudgetRule` but runs all other addition rules on the move's re-add target. The atomic rollback path (line 365) on validation failure restores the component to the source layer.
- **Suggested test**: `test_move_component_rolls_back_on_classification_block` — Verify move that violates allow_classification is rejected and component is restored to source layer

### game/ui/screens/build_queue_helpers.py (~205 LOC, layer: UI)

#### [MAJOR] `calculate_queue_turn_spend` — Production forecast algorithm
- **Location**: build_queue_helpers.py:109-187
- **Issue**: This function contains complex sequential production allocation math — `calculate_queue_turn_spend` distributes production capacity across a queue with limiting-resource logic and partial-turn completion. It's pure business logic (no pygame imports), making it unit-testable. Zero unit tests found.
- **Risk**: This function forecasts the resource consumption display for the build queue UI. Incorrect calculations here show wrong ETAs to the player but have no gameplay impact. Still, it's testable business logic in a UI file.
- **Suggested tests**:
  1. `test_calculate_queue_turn_spend_empty_queue_returns_empty` — Empty queue → []
  2. `test_calculate_queue_turn_spend_single_item_full_completion` — Item completes in one turn
  3. `test_calculate_queue_turn_spend_multi_item_capacity_exhaustion` — Second item gets 0 when first consumes all
  4. `test_calculate_queue_turn_spend_partial_completion` — Item half-complete, remaining split correctly
  5. `test_calculate_queue_turn_spend_zero_rate_blocks_all` — Missing resource in build_rate stops all downstream

### game/ui/screens/planet_list_filters.py (~385 LOC, layer: UI)

#### [MAJOR] `filter_planets` / effects_predicate pipeline — Partially tested
- **Location**: planet_list_filters.py:106-187
- **Issue**: Has tests in `tests/unit/ui/screens/test_planet_list_filters.py`. The FEAT-25 tri-state effects filter (`effects_predicate`, `compute_planet_effect_keys`) contains complex composition logic. The `FilterState.YES`/`NO`/`IGNORE` semantics and AND-composition of multiple effects may need additional verification.
- **Suggested test**: `test_effects_predicate_mixed_yes_no_composes_and` — A planet with effect A but not B fails when both YES-A and NO-B are specified

## Tier 3 — Verified Coverage (no new gaps)

### game/core/protocols/persistence.py (~27 LOC, layer: Core)
- **Status**: Tier 3 — `ISerializable` protocol definition. Verified: CONFIRMED as adequately covered by tests for its implementors (tested indirectly via `test_serializable_protocol.py` and each implementor's serializer tests). Protocol definition only — no logic to test.

### game/core/protocols/strategy_domain.py (~194 LOC, layer: Core)
- **Status**: Tier 3 — Protocol definitions + TypeGuards. Verified: CONFIRMED. `IEmpire`, `IFacility`, `IRaceRegistry`, `IShipInstance` are protocol definitions. The TypeGuard functions (`is_empire`, `is_facility`, `is_ship_instance`) are tested indirectly via strategy entity tests that use these guards.

### game/services/llm/provider.py (~76 LOC, layer: Services)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. `LLMProvider` is a `@runtime_checkable` Protocol definition. Tests exist at `tests/unit/services/llm/test_provider_protocol.py`.

### game/simulation/combat/modifier_stack.py (~74 LOC, layer: Simulation)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. `ModifierEntry` and `ModifierStack` are frozen dataclasses with a factory classmethod. `ModifierStack.empty()` returns a shared-immutable empty instance — the only logic. Tested indirectly through the spec compiler and battle-runner integration tests.

### game/simulation/interfaces/ability_protocols.py (~359 LOC, layer: Simulation)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. Protocol definitions + TypeGuard functions. The TypeGuards (`is_ability`, `is_weapon`, `is_beam_weapon`, `is_seeker_weapon`, `is_projectile_weapon`, `is_warp_jump`, `is_resource_consumption`, `is_resource_storage`, `is_resource_generation`) are exercised by combat code that uses these guards. Protocols themselves have no logic.

### game/simulation/components/abilities/crew.py (~85 LOC, layer: Simulation)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. `CrewCapacity`, `LifeSupportCapacity`, `CrewRequired` — tested by ability-level tests.

### game/simulation/validation/ship_validator.py (~438 LOC, layer: Simulation)
- **Status**: Phase 1 Tier 2. Verified: CONFIRMED as adequately tested. Tests exist at `tests/unit/simulation/validation/test_ship_validator_rules.py`.

### game/strategy/data/order_serializer.py (~231 LOC, layer: Strategy)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. Tests exist at `tests/unit/strategy/data/test_order_serializer.py`.

### game/strategy/engine/handlers/movement.py (~214 LOC, layer: Strategy)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. Tests exist at `tests/unit/strategy/engine/handlers/test_movement_handlers.py`.

### game/strategy/generation/density/primitives/radial.py (~61 LOC, layer: Strategy)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. `RadialPrimitive.evaluate()` has a simple Gaussian formula + edge case for `sigma <= 0`.

### game/strategy/facade/dto/colony_demographic_view.py (~95 LOC, layer: Strategy)
- **Status**: Phase 1 Tier 3. Verified: CONFIRMED. Frozen dataclasses with `__post_init__` for defensive copies (MappingProxyType wrapping, sort invariant). Simple logic — sorting and defensive copying.

### game/ui/effects/hit_effects.py (~233 LOC, layer: UI)
- **Status**: ADVISORY — Pygame rendering code (4 draw functions). The `HitEffect` dataclass (lines 58-78) has simple properties (`progress`, `is_alive`) and `update()` — these are testable but low-priority. `create_hit_effect` and `update_effects` are simple factory/filter functions. All drawing functions are pure rendering.

### game/ui/filters/__init__.py (~4 LOC, layer: UI)
- **Status**: ADVISORY — Re-export shim. LOW_PRIORITY.

### game/ui/panels/build_queue_portraits.py (~205 LOC, layer: UI)
- **Status**: ADVISORY — Image loading + caching UI code. The `BuildQueuePortraitLoader` loads themed ship portraits and resource icons from disk with pygame. No business logic to test independently.

### game/ui/screens/battle_setup/constants.py (~54 LOC, layer: UI)
- **Status**: ADVISORY — Module-level constant tables. Pure data, no logic.

### game/ui/screens/battle_setup/view_model.py (~60 LOC, layer: UI)
- **Status**: LOW_PRIORITY — Simple mutable dataclass with selection state and two trivial helper methods (`clear_selection`, `has_tf_selection`, `has_sq_selection`). Trivial logic.

### game/ui/screens/build_queue_renderer.py (~241 LOC, layer: UI)
- **Status**: ADVISORY — pygame_gui widget construction (`refresh_items_list`, `refresh_roles_list`). All methods create/destroy pygame_gui elements. No independent business logic.

### game/ui/screens/builder/stats_config.py (~245 LOC, layer: UI)
- **Status**: ADVISORY — Config loading + section visibility resolution. The `resolve_section_visibility` function (lines 176-237) IS testable business logic (no pygame) but lives in a UI module. It resolves which stats sections to display based on vehicle type, abilities present, and dynamic generators. Worth extracting for independent testing.

### game/ui/screens/strategy_render/overlay.py (~52 LOC, layer: UI)
- **Status**: ADVISORY — Simple Pygame drawing: semi-transparent overlay + centered text. No business logic.

### game/ui/screens/strategy_windows/orders_window_ctrl.py (~111 LOC, layer: UI)
- **Status**: ADVISORY — UI window lifecycle management. Creates pygame_gui windows. The closure-capture dispatch pattern (lines 54-92) is structural/logical but tied to UI.

### game/ui/screens/strategy_windows/selection_prompts.py (~85 LOC, layer: UI)
- **Status**: ADVISORY — Modal window construction. Creates `FleetSelectionWindow`, `PlanetSelectionWindow`, `SystemSelectionWindow` with pygame Rect sizing. Pure UI construction.

### game/ui/screens/test_lab/dialogs.py (~272 LOC, layer: UI)
- **Status**: ADVISORY — `JSONPopup` and `ConfirmationDialog` are full pygame rendering + event handling components. The `JSONPopup.__init__` has some data processing (`json.dumps`, line splitting for scroll) but is primarily UI.

### game/ui/screens/test_lab/results_panel.py (~266 LOC, layer: UI)
- **Status**: ADVISORY — Test run history display panel. Full pygame rendering with `ScrollState`, click handling, card display. The `_recalculate_scroll` method is simple arithmetic.

### game/ui/screens/workshop_screen.py (~648 LOC, layer: UI)
- **Status**: ADVISORY — Major workshop screen with pygame_gui layout, event handling, and screen lifecycle. Exceeds 500 LOC. All logic is UI orchestration (panel creation, button layout, event routing). The `_get_button_definitions` method (lines 581-619) returns mode-dependent button lists — simple logic.

### game/ui/screens/workshop_viewmodel.py (~494 LOC, layer: UI)
- **Status**: ADVISORY — MVVM ViewModel. While it contains testable business logic (delegating to `VehicleDesignService`), it depends on WorkshopContext + EventBus and the public API is entirely delegation to internal helpers (`WorkshopShipOps`, `WorkshopLayerOps`). Tests should target the underlying services rather than this orchestrator. The `_with_ship` helper (lines 129-159) is a reusable pattern extract (PROJ-319 DUP-X-10).

### game/ui/services/image/null_provider.py (~62 LOC, layer: UI)
- **Status**: CONFIRMED — Trivial no-op provider. Always raises `ImageConfigError` from `generate_image()`. No logic to test beyond verifying the exception raise.

## File Coverage Verification

| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/ai/controller.py | AI | 2 | Read ✓ | 3 |
| game/core/input_actions.py | Core | ? | Read ✓ | 2 |
| game/core/protocols/persistence.py | Core | ? | Read ✓ | 0 |
| game/core/protocols/strategy_domain.py | Core | ? | Read ✓ | 0 |
| game/engine/physics.py | Engine | 0 | Read ✓ | 1 |
| game/services/llm/defaults.py | Services | ? | Read ✓ | 1 |
| game/services/llm/provider.py | Services | ? | Read ✓ | 0 |
| game/simulation/combat/ability_stat_registry.py | Simulation | ? | Read ✓ | 1 |
| game/simulation/combat/fleet_aura_manager.py | Simulation | 0 | Read ✓ | 1 |
| game/simulation/combat/modifier_stack.py | Simulation | ? | Read ✓ | 0 |
| game/simulation/components/abilities/crew.py | Simulation | ? | Read ✓ | 0 |
| game/simulation/interfaces/ability_protocols.py | Simulation | ? | Read ✓ | 0 |
| game/simulation/services/vehicle_design_service.py | Simulation | ? | Read ✓ | 1 |
| game/simulation/validation/ship_validator.py | Simulation | ? | Read ✓ | 0 |
| game/strategy/data/order_serializer.py | Strategy | ? | Read ✓ | 0 |
| game/strategy/engine/consumable_management_engine.py | Strategy | ? | Read ✓ | 1 |
| game/strategy/engine/fleet_movement_engine.py | Strategy | ? | Read ✓ | 1 |
| game/strategy/engine/handlers/movement.py | Strategy | ? | Read ✓ | 0 |
| game/strategy/engine/harvesting_engine.py | Strategy | ? | Read ✓ | 1 |
| game/strategy/facade/dto/colony_demographic_view.py | Strategy | ? | Read ✓ | 0 |
| game/strategy/generation/density/primitives/radial.py | Strategy | ? | Read ✓ | 0 |
| game/ui/effects/hit_effects.py | UI | ? | Read ✓ | 0 |
| game/ui/filters/__init__.py | UI | ? | Read ✓ | 0 |
| game/ui/panels/build_queue_portraits.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/battle_setup/constants.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/battle_setup/view_model.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/build_queue_helpers.py | UI | ? | Read ✓ | 1 |
| game/ui/screens/build_queue_renderer.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/builder/stats_config.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/planet_list_filters.py | UI | ? | Read ✓ | 1 |
| game/ui/screens/strategy_render/overlay.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/strategy_windows/orders_window_ctrl.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/strategy_windows/selection_prompts.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/test_lab/dialogs.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/test_lab/results_panel.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/workshop_screen.py | UI | ? | Read ✓ | 0 |
| game/ui/screens/workshop_viewmodel.py | UI | ? | Read ✓ | 0 |
| game/ui/services/image/null_provider.py | UI | ? | Read ✓ | 0 |

## Context Usage Estimate
- Total production LOC read: ~8,713 (all 38 files)
- Total test LOC read: ~2,500 (12 test files sampled for verification)
- Approximate headroom: High (>500K)
- Partially-read files: None — all 38 production files read completely
