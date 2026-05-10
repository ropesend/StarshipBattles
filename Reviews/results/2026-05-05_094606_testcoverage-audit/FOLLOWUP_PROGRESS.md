# Test Coverage Follow-Up Progress

> Updated: 2026-05-06 by Codex

## Scope Completed This Pass

The first follow-up pass focused on verified or high-priority gaps from
`SUMMARY.md`, then re-verified each claim before adding tests. Several audit
items were false positives because tests already existed under different
paths or exercised the code through public facades.

## Completed Work Packets

### Simulation Combat Weapon Families

- Covered `game/simulation/combat/families/_beam_common.py`,
  `pdc.py`, and `seeker.py`.
- Added `tests/unit/simulation/combat/test_weapon_family_handlers.py`.
- New coverage includes beam zero aim-vector fallback, PDC shared beam
  resolution delegation, PDC beam-shaped result, and Seeker target
  `None`, out-of-arc, in-arc, and zero-vector cases.
- Production changes: none.

### Strategy Facade And Ability Display

- Covered `game/strategy/facade/slices/event_slice.py`,
  `game/strategy/services/ability_sources/fleet.py`, and
  `game/strategy/services/effect_ability_display.py`.
- Added tests to:
  - `tests/unit/strategy/facade/test_event_queries.py`
  - `tests/unit/strategy/services/ability_sources/test_fleet.py`
  - `tests/unit/strategy/services/test_effect_ability_display.py`
- New coverage includes scoped/unscoped EventLog API dispatch, fleet
  ability source filtering/memoization edge cases, malformed ability
  payload handling, and display fallback labels.
- Production changes: none.

### Strategy Validation And Command Handler Base

- Covered `game/strategy/validation/colonize_validator.py`,
  `game/strategy/validation/superweapon_validator.py`, and
  `game/strategy/engine/handlers/base.py`.
- Added tests to:
  - `tests/unit/strategy/validation/test_colonize_validator.py`
  - `tests/unit/strategy/validation/test_superweapon_validator.py`
  - `tests/unit/strategy/engine/test_base_command_handler.py`
- New coverage includes exact-sector colonization validation, committed pod
  exhaustion, `skip_chain_check`, open/close warp target edge cases,
  required/optional resolver helpers, queue owner lookup, and colonize
  target wrapping.
- Production changes: none.

### AI Group Target Coordination And Core Protocol Helper

- Covered `game/ai/group_target_coordinator.py` and
  `game/core/protocols/common.py`.
- Added tests to:
  - `tests/unit/ai/test_group_target_coordinator.py`
  - `tests/unit/core/test_protocols_common.py`
- New coverage includes all-dead filtering, unknown priority fallback,
  `None`/zero `max_hp`, aggregate ratio clamping, same-mass flagship tie
  behavior, direct `_has_attrs` behavior, and package re-export coverage.
- Production change: `GroupTargetCoordinator` now treats `None`/zero
  `max_hp` as zero capacity and clamps aggregate current HP to valid
  capacity when computing group HP ratios.

### Strategy Density Primitive Edge Cases

- Covered `game/strategy/generation/density/primitives/density_primitive.py`
  and `geometric.py`.
- Added `tests/unit/strategy/generation/density/test_density_primitive.py`.
- Added one branch test to
  `tests/unit/strategy/generation/density/test_geometric.py`.
- New coverage includes direct `clamp_density` bounds and the
  `GeometricPrimitive.sides < 3` circular fallback.
- Production changes: none.

### Replay Serialization And Component Inspector Helpers

- Covered `game/strategy/services/replay_verification_coordinator.py`,
  `game/simulation/replay/replay_serialization.py`, and
  `game/strategy/services/component_inspector.py`.
- Added tests to:
  - `tests/unit/strategy/services/test_replay_verification_coordinator.py`
  - `tests/unit/simulation/replay/test_serialization.py`
  - `tests/unit/strategy/test_component_inspector.py`
- New coverage includes `_json_safe` Enum/dict/list/tuple/fallback
  coercion, `_difference_to_dict` coercion, replay serialization
  fallback paths for `Vector2` passthrough, non-`FormationSpec`
  formations, unknown boundary subtype errors, component-registry hash
  dict/object/bad-`to_dict`/invalid-registry branches, and direct
  strategy component-inspector helpers for registry lookup, string
  component entries, unique ability listing, and ability payload
  normalization.
- Production changes: none.

### Strategy Planet Order Deserialization

- Verified `game/strategy/data/planet.py`, `order_types.py`, and
  `order_serializer.py` against existing tests in
  `tests/unit/strategy/planet/test_planet_validation.py`,
  `tests/unit/strategy/data/test_order_serializer.py`, and save/load
  round-trip coverage.
- Confirmed gap: corrupt `Planet.from_dict(..., orders=[...])` entries
  were silently dropped by `_deserialize_planet_orders`; no existing test
  covered that corruption path.
- False positives found: none for this packet.
- Added
  `tests/unit/strategy/planet/test_planet_validation.py::TestPlanetFromDictValidation::test_bad_order_raises_persistence_exception`.
- Production change: `game/strategy/data/planet.py` now raises
  `PersistenceException` with `field="orders"` and `order_index` context
  for malformed planet order data, and no longer falls back to the legacy
  `planet_orders` key when loading the current save schema.

### Strategy Engines Part 1

- Covered `game/strategy/engine/planet_action_engine.py`,
  `component_activation_engine.py`, and `fleet_movement_engine.py`.
- Added focused branch tests to:
  - `tests/unit/strategy/engine/test_component_activation_engine.py`
  - `tests/unit/strategy/engine/test_planet_action_engine.py`
  - `tests/unit/strategy/fleet_movement_engine/test_characterization.py`
- New coverage includes non-operational facility skips, non-dict component
  state skips, planet action activation/deactivation guards, facility target
  fallback branches, and FEAT-28 swap filter cases for ship count,
  `JOIN_FLEET`, non-pursuit, and non-`Fleet` targets.
- False positives found: these modules were not "mostly untested"; existing
  direct and characterization tests already covered their main paths.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/engine/test_component_activation_engine.py tests/unit/strategy/engine/test_planet_action_engine.py tests/unit/strategy/fleet_movement_engine/test_characterization.py`
  - Result: `46 passed`

### Strategy Engines Part 2

- Covered `game/strategy/engine/harvesting_engine.py` and
  `production_engine.py`.
- Added focused tests to:
  - `tests/unit/strategy/engine/test_harvesting_engine.py`
  - `tests/unit/strategy/engine/test_production_engine_queue.py`
- New coverage includes staging-yard capacity aggregation for inline and
  registry component entries, harvest booster aggregation across applicable
  scopes, no-empire/no-galaxy booster fallback, non-shipyard queue skips, and
  fleet-not-building skips before space-yard processing.
- False positives found: `consumable_management_engine.py`,
  `organics_consumption_engine.py`, `water_engine.py`, and most
  `production_engine.py` behavior already had direct or facade coverage.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/engine/test_harvesting_engine.py tests/unit/strategy/engine/test_production_engine_queue.py -q`
  - Result: `53 passed`

### Simulation Combat Engine Coordination

- Covered `game/simulation/entities/ship_combat_engine.py` and remaining
  branches in `game/simulation/combat/weapon_firing_system.py`.
- Added tests to:
  - `tests/unit/simulation/ship_combat_engine/test_combat_ops.py`
  - `tests/unit/simulation/combat/test_weapon_firing_system.py`
- New coverage includes `ShipCombatEngine` target-selection and firing-solution
  delegation, lethal `SHIP_DESTROYED` event emission, PDC missile context
  filtering for alive enemy missiles only, and typed `NoAttack` dispatch
  results returning no attack objects.
- False positives found: `ship_resource_manager.py` already has direct unit
  coverage, and positive PDC missile injection was already covered elsewhere.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/simulation/ship_combat_engine/test_combat_ops.py tests/unit/simulation/combat/test_weapon_firing_system.py -q`
  - Result: `35 passed`

### UI Fleet Command Router

- Covered `game/ui/screens/strategy_fleet_command_router.py`.
- Added `tests/unit/ui/screens/test_strategy_fleet_command_router.py`.
- New coverage includes direct fleet actions, no-selected-fleet guards, warp
  capability guards, cancel modes including `EDIT_MOVE`, superweapon target
  routing, self-destruct routing, detail actions for planet orders, abilities,
  fleet report, build, toggle hotkeys, ability-toggle activation/deactivation,
  and `finish_move_action` shift behavior.
- False positives found: `battle_results_data.py` already had direct coverage.
  Broad `strategy_click_dispatcher.py` coverage claims were partly false, but
  edit/choice callback branches remain a useful follow-up.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/ui/screens/test_strategy_fleet_command_router.py -q`
  - Result: `61 passed`

### UI Workshop And Transfer Selection

- Covered `game/ui/screens/workshop_viewmodel_selection.py`,
  `transfer_controller.py`, and `transfer_view_model.py`.
- Added:
  - `tests/unit/ui/screens/test_workshop_viewmodel_selection.py`
  - `tests/unit/ui/screens/test_transfer_controller.py`
- Added focused tests to
  `tests/unit/ui/screens/test_transfer_view_model.py`.
- New coverage includes selection normalization, append/toggle selection,
  modifier synchronization, source discovery including selected source fleets,
  projected-position planet fallback, pod design discovery sorting/fallback,
  cargo key parsing, DTO fetching, non-fleet endpoint aborts, command
  emission/counting, transfer filter visibility, and source/target labels.
- False positives found: `transfer_controller.py` and
  `transfer_view_model.py` had partial indirect/direct coverage already.
- Production change: `game/ui/screens/workshop_viewmodel_selection.py` now
  keeps duplicate incoming objects from re-adding an object toggled off earlier
  in the same append-toggle operation.
- Targeted command:
  `pytest tests/unit/ui/screens/test_strategy_fleet_command_router.py tests/unit/ui/screens/test_workshop_viewmodel_selection.py tests/unit/ui/screens/test_transfer_controller.py tests/unit/ui/screens/test_transfer_view_model.py -q`
  - Result: `86 passed`

### UI Click Dispatcher And Battle Results False Positive

- Covered remaining callback/edit branches in
  `game/ui/screens/strategy_click_dispatcher.py`.
- Added focused tests to
  `tests/unit/ui/screens/test_strategy_click_dispatcher.py`.
- New coverage includes unknown mode fallback, MOVE choice callbacks for move
  and intercept, JOIN choice callback, SELECT right-click quick-move choice
  callbacks, EDIT_MOVE left-click completion, and EDIT_MOVE right-click cancel
  cleanup.
- False positives found: existing click dispatcher tests already covered basic
  mode routing, transfer/cargo, warp, superweapon clicks, picking, and planet
  hit-testing. `game/ui/screens/battle_results_data.py` was also a false
  positive with direct coverage in `tests/unit/ui/test_battle_results_data.py`.
- Production changes: none.
- Targeted commands:
  - `pytest tests/unit/ui/screens/test_strategy_click_dispatcher.py -q`
    - Result: `13 passed`
  - `pytest tests/unit/ui/test_battle_results_data.py -q`
    - Result: `9 passed`

### Strategy Data And Prompt Helper Edges

- Covered `game/strategy/data/race_caption_loader.py`,
  `game/strategy/services/race_description_prompt_builder.py`, and
  `game/strategy/data/galaxy_system_generator.py`.
- Added focused tests to:
  - `tests/unit/strategy/data/test_race_caption_loader.py`
  - `tests/unit/strategy/services/test_race_description_prompt_builder.py`
  - `tests/unit/strategy/data/test_galaxy_system_generator.py`
- New coverage includes parsed non-object caption sidecars, unknown
  habitability factor preferences being skipped in prompt rendering, and lazy
  cache behavior for planet types, star types, and system archetypes.
- False positives found: most caption loader error paths were already covered;
  only the non-dict sidecar path was missing.
- Production changes: none.
- Targeted commands:
  - `pytest tests/unit/strategy/data/test_race_caption_loader.py -q`
    - Result: `11 passed`
  - `pytest tests/unit/strategy/services/test_race_description_prompt_builder.py -q`
    - Result: `15 passed`
  - `pytest tests/unit/strategy/data/test_galaxy_system_generator.py -q`
    - Result: `29 passed`

### Strategy Action Timing And Resupply Edges

- Covered `game/strategy/services/action_time_resolver.py` and
  `game/strategy/engine/resupply_engine.py`.
- Added focused tests to:
  - `tests/unit/strategy/services/test_action_time_resolver.py`
  - `tests/unit/strategy/engine/test_resupply_engine.py`
- New coverage includes ACTIVATE/DEACTIVATE ability timing, missing
  `ability_name` fallback, facility-instance filtering, non-operational
  facility fallback, `_transfer_fuel` withdrawing only actual ship acceptance,
  remaining-available capping, and early exit when available fuel is exhausted.
- Production changes: none.
- Targeted commands:
  - `pytest tests/unit/strategy/services/test_action_time_resolver.py -q`
    - Result: `18 passed`
  - `pytest tests/unit/strategy/engine/test_resupply_engine.py -q`
    - Result: `28 passed`

### Simulation Tick Phases And Replay Wrapper

- Covered `game/simulation/systems/tick_phase.py` and
  `game/simulation/replay/replay_player.py`.
- Added focused tests to:
  - `tests/unit/simulation/systems/test_tick_phases.py`
  - `tests/unit/simulation/replay/test_replay_player.py`
- New coverage includes default tick phase names/priorities, each default
  phase's engine collaborator call, `AttackProcessingPhase` use of
  `_alive_ships_cache`, and `run_replay_headless` forwarding reconstructed
  spec, `ai_factory`, `ship_builder`, `registry_provider`, and
  `capture_context=None`.
- Production changes: none.
- Targeted commands:
  - `pytest tests/unit/simulation/systems/test_tick_phases.py -q`
    - Result: `16 passed`
  - `pytest tests/unit/simulation/replay/test_replay_player.py -q`
    - Result: `1 passed`
  - `pytest tests/unit/simulation/replay -q`
    - Result: `54 passed`

### AI Battle Line And Ability Formula Detection

- Covered `game/ai/spatial_behaviors/battle_line.py` and
  `game/simulation/components/abilities/__init__.py`.
- Added focused tests to:
  - `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py`
  - `tests/unit/simulation/components/abilities/test_ability_registry.py`
- New coverage includes `leader=None`, empty group fallback, documented
  `wall` shape behavior, formula string detection, non-formula string
  detection, nested dict/list formula detection, and mixed primitive/empty
  data cases.
- Production change: `game/ai/spatial_behaviors/battle_line.py` now implements
  the documented `wall` shape by staggering alternating slots into a second
  rank. The formula helper already behaved correctly.
- Targeted commands:
  - `pytest tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py -q -k "missing_leader or empty_group or wall_shape"`
    - Initial TDD result: `2 passed`, `1 failed`; the `wall` shape behaved
      like a flat line before the fix.
    - Result after fix: `3 passed`
  - `pytest tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py -q`
    - Result: `27 passed`
  - `pytest tests/unit/simulation/components/abilities/test_ability_registry.py -q`
    - Result: `9 passed`
  - `pytest tests/unit/simulation/components/abilities -q`
    - Result: `862 passed`

### UI Strategy Render Context

- Covered `game/ui/screens/strategy_render/context.py`.
- Added `tests/unit/ui/screens/strategy_render/test_context.py`.
- New coverage includes the `radius_hexes <= 0` minimum visible-radius guard
  and tiny positive-radius clamping.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/ui/screens/strategy_render/test_context.py -q`
  - Initial result before adding the file: no tests ran.
  - Result after adding tests: `2 passed`

### Strategy Ability Source Adapter Edges

- Covered remaining branch edges in
  `game/strategy/services/ability_sources/facility.py` and
  `warp_point.py`.
- Verified `game/strategy/services/ability_sources/labels.py` against
  existing direct tests.
- Added focused tests to:
  - `tests/unit/strategy/services/ability_sources/test_facility.py`
  - `tests/unit/strategy/services/ability_sources/test_warp_point.py`
- New coverage includes facility activation-state lookup by owning component,
  missing activation-state getter, missing ability lookup, warp-point default
  label/source-id fallbacks, missing intrinsic abilities, missing coordinate
  data, incompatible coordinate types, identity-based system matching, and
  the always-`None` activation state contract.
- False positives found: the broad facility/warp/label claims were mostly
  already covered by dedicated adapter tests; only these branch edges were
  missing.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/services/ability_sources/test_facility.py tests/unit/strategy/services/ability_sources/test_warp_point.py tests/unit/strategy/services/ability_sources/test_labels.py -q`
  - Initial result before adding branch tests: `20 passed`
  - Result after adding tests: `30 passed`

### Strategy Fleet Pursuer Tracker Defensive Branch

- Covered `game/strategy/data/fleet_pursuer_tracker.py`.
- Added one focused test to
  `tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`.
- New coverage includes redirecting pursuer orders to a target object that
  does not expose `_pursuer_tracker`; order rewrite still succeeds and
  registration transfer is skipped.
- False positives found: the tracker already had broad redirect, exclude,
  unregister, merge, and destruction coverage; only the defensive `hasattr`
  branch was unpinned.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py -q`
  - Initial result before adding the branch test: `27 passed`
  - Result after adding tests: `28 passed`

### Simulation Marker Ability Requirement Branches

- Covered `game/simulation/components/abilities/markers.py`.
- Added focused tests to
  `tests/unit/simulation/components/abilities/test_markers.py`.
- New coverage includes `RequiresCommandAndControl.update()` with no ship
  context, active command provider success, inactive provider skip/failure,
  and self-component exclusion.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/simulation/components/abilities/test_markers.py -q`
  - Initial result before adding branch tests: `35 passed`
  - Result after adding tests: `39 passed`

### Strategy Replay, Ability Iterator, And Simulation Adapter Edges

- Covered remaining branch edges in:
  - `game/strategy/services/replay_ship_builder.py`
  - `game/strategy/services/replay_resolver.py`
  - `game/strategy/services/ability_iterator.py`
  - `game/strategy/adapters/simulation_adapter.py`
- Added focused tests to:
  - `tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py`
  - `tests/integration/replay/test_replay_resolver.py`
  - `tests/unit/strategy/services/test_ability_iterator.py`
  - `tests/unit/strategy/adapters/test_simulation_adapter.py`
- New coverage includes replay builder fallback selection, missing
  snapshot/no-fallback `ValueError`, resolver behavior when the store has
  no `replay_dir`, system-scope fleet ability-source lookup, incompatible
  planet/system coordinate `TypeError` handling, explicit seed passthrough,
  and lazy RNG creation/reuse for generated battle seeds.
- False positives found: `game/simulation/entities/stat_contributors/weapons.py`
  already has direct tests for `aggregate_targeting_scores` bool coercion,
  zero values, returned ECM score, and `baseline_to_hit_offense`.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/services/test_ability_iterator.py tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py tests/integration/replay/test_replay_resolver.py tests/unit/strategy/adapters/test_simulation_adapter.py tests/unit/strategy/combat/test_post_battle_hook.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py tests/unit/strategy/test_ship_instance_damage.py -q`
  - Result after adding tests: `110 passed`

### Strategy Post-Battle, Turn Phase Hooks, And ShipInstance Edges

- Covered remaining defensive branches in:
  - `game/strategy/combat/post_battle_hook.py`
  - `game/strategy/engine/turn_phase_registry.py`
  - `game/strategy/data/ship_instance.py`
- Added focused tests to:
  - `tests/unit/strategy/combat/test_post_battle_hook.py`
  - `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`
  - `tests/unit/strategy/test_ship_instance_damage.py`
- New coverage includes orphan outcome logging/skipping, unknown ship-status
  logging/skipping, empty-fleet pruning when the empire is missing or lacks
  a `fleets` list, `ValueError` during empty-fleet removal, movement queue
  capture, moved-fleet diff derivation, pod storage capacity/usage, pod
  capacity denial, ship activation-state roundtrip, partial repair cache
  invalidation, full repair component restoration, and direct stats-cache
  invalidation.
- False positives found: `game/simulation/combat/formation.py` already
  covers default-formation tie fallback and unknown-role `other` fallback
  in `tests/unit/simulation/combat/test_formation_defaults.py`.
  `game/strategy/engine/action_execution_engine.py` already has direct
  tests for the audited return-`None` branches, including speed/tick
  gating, no-order, movement-order skip, BUILD skip/auto-pop, and
  non-action order skip.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/services/test_ability_iterator.py tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py tests/integration/replay/test_replay_resolver.py tests/unit/strategy/adapters/test_simulation_adapter.py tests/unit/strategy/combat/test_post_battle_hook.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py tests/unit/strategy/test_ship_instance_damage.py -q`
  - Result after adding tests: `110 passed`

### Strategy Combat Modifier Collector Helper Edges

- Covered remaining helper branches in
  `game/strategy/services/combat_modifier_collector.py`.
- Added focused tests to
  `tests/unit/strategy/services/test_combat_modifier_collector.py`.
- New coverage includes `scope=None` falling back to ability default scope,
  `_find_reference_planet(..., galaxy=None, ...)` returning `None`, and
  `_find_empire` returning `None` for no matching empire.
- False positives found: none for this packet.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/services/test_combat_modifier_collector.py -q`
  - Initial result before adding helper tests: `7 passed`
  - Result after adding tests: `10 passed`

### Strategy Facade And Session Data Edges

- Covered remaining direct branches in:
  - `game/strategy/facade/slices/system_slice.py`
  - `game/strategy/facade/dto/fleet_dto.py`
  - `game/strategy/engine/game_session.py`
- Added focused tests to:
  - `tests/unit/strategy/facade/slices/test_system_slice.py`
  - `tests/unit/strategy/facade/test_fleet_dto.py`
  - `tests/unit/strategy/engine/test_game_session_from_dict.py`
- New coverage includes direct `SystemSlice` wrappers for all systems,
  system-at-hex, and system-containing-fleet; `FleetInfo.from_fleet`
  descriptions for `MOVE_TO_FLEET`, `BUILD`, `TRANSFER`, planetless
  `COLONIZE`, and carried-item default aggregation; `GameSession.from_dict`
  missing `config`/`galaxy` errors and pursuer tracker rebuild for
  `MOVE_TO_FLEET` / `JOIN_FLEET`.
- False positives found: `system_slice.py`, `fleet_dto.py`, and
  `game_session.py` already had broad facade/DTO/session coverage. Missing
  top-level `empires` is intentionally not an error because `from_dict`
  defaults it to `[]`.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/facade/slices/test_system_slice.py tests/unit/strategy/facade/test_fleet_dto.py tests/unit/strategy/engine/test_game_session_from_dict.py -q`
  - Result after adding tests: `36 passed`

### Simulation Contracts And Debug Helper Edges

- Covered remaining direct contract/debug branches in:
  - `game/simulation/combat/attack_contract.py`
  - `game/simulation/components/abilities/base.py`
  - `game/simulation/systems/battle_end_conditions.py`
  - `game/simulation/battle_controller.py`
  - `game/core/constants.py`
  - `game/strategy/data/classification_config.py`
- Added or extended focused tests in:
  - `tests/unit/simulation/combat/test_weapon_registry.py`
  - `tests/unit/simulation/components/abilities/test_ability_base.py`
  - `tests/unit/simulation/systems/test_battle_end_conditions.py`
  - `tests/unit/simulation/battle_controller/test_utilities.py`
  - `tests/unit/core/test_constants.py`
  - `tests/unit/strategy/data/test_classification_config.py`
- New coverage includes `FAMILY_METADATA` values for every
  `WeaponFamily`, `_parse_primary_value(..., fallback_keys=...)`,
  end-condition `__repr__` contracts, `BattleController.reset()` clearing
  `_initial_state`, `LayerDefaults` radius ordering, and classification
  config fallback for `KeyError`, `TypeError`, and `ValueError`.
- False positives found: `ModifierManager` deprecated static methods have no
  live callers outside the deprecated path and were not worth pinning before
  cleanup. `game/simulation/event_bus.py` does not exist in this checkout;
  active simulation event-bus coverage lives under `combat_events.py`.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/simulation/combat/test_weapon_registry.py tests/unit/simulation/components/abilities/test_ability_base.py tests/unit/simulation/components/test_modifier_manager.py tests/unit/simulation/systems/test_battle_end_conditions.py tests/unit/simulation/systems/test_mass_ratio_condition.py tests/unit/simulation/battle_controller/test_utilities.py tests/unit/core/test_constants.py tests/unit/strategy/data/test_classification_config.py -q`
  - Result after adding tests: `264 passed`

### Strategy Generation, Production, And Asset Metadata Edges

- Covered remaining edge branches in:
  - `game/strategy/generation/density/primitives/noise.py`
  - `game/strategy/engine/production_spawner.py`
  - `game/assets/asset_manager.py`
- Added focused tests to:
  - `tests/unit/strategy/generation/density/test_noise.py`
  - `tests/unit/strategy/engine/test_production_spawner.py`
  - `tests/unit/assets/test_asset_manager_resolutions.py`
- New coverage includes negative-scale and zero-octave noise behavior,
  `_hash_coord`, `_smooth_noise`, explicit `ProductionSpawner`
  collaborators, no-galaxy ship spawn metadata, planet-location metadata
  fallbacks, fleet-complex no-galaxy/no-planet guards, star metadata
  loading/defaults, star asset-key manifest lookup, star folder validation,
  and star image fallback/error handling.
- False positives found: `NoisePrimitive` already covered normal
  deterministic/output-bound behavior. `ProductionSpawner` already covered
  main dispatch, normal ship/fleet complex paths, staging-yard behavior,
  and target-planet selection. `AssetManager` planet image resolution
  branches were already covered.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/strategy/generation/density/test_noise.py tests/unit/strategy/engine/test_production_spawner.py tests/unit/strategy/engine/test_production_spawner_staging_yard.py tests/unit/assets/test_asset_manager_resolutions.py -q`
  - Initial result before adding tests: `38 passed`
  - Result after adding tests: `59 passed`

### UI Workshop Pure Business Logic

- Covered pure business/orchestration branches in:
  - `game/ui/screens/workshop_data_reloader.py`
  - `game/ui/screens/workshop_viewmodel_ship_ops.py`
  - `game/ui/screens/builder/stat_getters.py`
- Added or extended focused tests in:
  - `tests/unit/ui/screens/test_workshop_data_reloader.py`
  - `tests/unit/ui/screens/test_workshop_viewmodel_ship_ops.py`
  - `tests/unit/ui/screens/builder/test_stat_getters.py`
- New coverage includes reload success/failure/error handling, data-folder
  selection, standard/test data helpers, ship creation/component operations,
  bulk-add warning counts, class changes, summary/validation helpers,
  ship attribute setters, broad pure stat getter branches, warp/range/cargo
  helpers, superweapon summary, and formatter/registry mappings.
- False positives found: `workshop_viewmodel_ship_ops.pick_up_component`
  had indirect ViewModel coverage already. `stat_getters.py` already covered
  resource fallbacks, some formatters, and validators; remaining pure getter
  branches were real gaps.
- Production changes: none.
- Targeted command:
  `pytest tests/unit/ui/screens/test_workshop_data_loader.py tests/unit/ui/screens/test_workshop_data_reloader.py tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py tests/unit/ui/screens/test_workshop_viewmodel_selection.py tests/unit/ui/screens/test_workshop_viewmodel_ship_ops.py tests/unit/ui/screens/builder/test_stat_getters.py -q`
  - Initial nearby baseline before adding tests: `30 passed`
  - Result after adding tests: `70 passed`

## Verified False Positives Or Already-Covered Claims

- `game/simulation/battle_runner.py` already has dedicated unit coverage
  including DI, telemetry, component HP, replay ID, and runner behavior.
- `game/simulation/combat/telemetry.py` already has unit coverage for
  telemetry levels and aggregators.
- `game/ai/group_target_coordinator.py` had existing coverage; this pass
  added missing robustness branches and fixed one real edge bug.
- `game/strategy/validation/colonize_validator.py` and
  `superweapon_validator.py` had substantial existing coverage; this pass
  added missing sector/target branches rather than duplicate broad tests.
- `game/strategy/engine/handlers/base.py` had existing ownership and
  resolver coverage; this pass added helper branch coverage.
- `game/services/llm/deepseek.py` already has unit coverage for missing
  API key, auth failures, rate limits, 5xx retry/exhaustion, non-JSON
  responses, and missing response fields.
- `game/simulation/components/component_inspector.py` does not exist in
  this checkout; the verified component-inspector helper gap maps to
  `game/strategy/services/component_inspector.py`.
- `game/strategy/engine/component_activation_engine.py`,
  `planet_action_engine.py`, and `fleet_movement_engine.py` already had
  main-path coverage; this pass added only verified edge branches.
- `game/strategy/engine/consumable_management_engine.py`,
  `organics_consumption_engine.py`, and `water_engine.py` already had
  targeted coverage for the audited helper paths.
- `game/simulation/ship_resource_manager.py` already has direct unit
  coverage for resource manager helper behavior.
- `game/ui/screens/battle_results_data.py` already has direct unit coverage.
- `game/ai/target_evaluator.py`, `game/ai/protocols.py`,
  `game/ai/spatial_behaviors/base.py`, and
  `game/simulation/entities/stat_contributors/{launch,movement}.py` already
  have substantial direct tests.
- `game/strategy/data/tech_tree.py` now has direct tests for cycle detection,
  loading, validation, query depth, and requirement resolution.
- `game/strategy/engine/order_processor.py` pod staging helpers have multiple
  direct tests.
- `game/strategy/systems/save_game_service.py` replay-store hooks are covered
  in integration replay tests.
- `game/simulation/replay/replay_outcome.py` already has direct coverage in
  `tests/unit/simulation/replay/test_serialization.py`, with additional
  verifier/store/capture usage.
- `game/strategy/facade/slices/economy_slice.py` already has dedicated
  `get_colony_demographic_view` and race-registry tests under
  `tests/unit/strategy/facade/`.
- `game/strategy/data/naming.py` already has unit coverage for load errors,
  duplicate skipping, exhaustion, and Roman numeral edge cases, plus an
  integration test.
- `game/strategy/data/spatial_index.py` already has a direct sparse-index
  regression test for `get_k_nearest`.
- `game/simulation/components/abilities/planetary.py` already covers the
  non-dict constructor branches in `test_planetary_abilities.py`.
- `game/simulation/components/abilities/stat_keys.py` already covers the
  invalid operation `ValidationException` path.
- `game/simulation/entities/stat_contributors/weapons.py` already has direct
  branch tests for `aggregate_targeting_scores`.
- `game/simulation/combat/formation.py` already covers default-formation
  tie fallback and unknown-role `other` fallback.
- `game/strategy/engine/action_execution_engine.py` already covers the
  recommended return-`None` branches directly.
- `game/simulation/components/modifier_manager.py` deprecated static methods
  have no live callers outside the deprecated API path; pinning them before
  cleanup would preserve low-value behavior.
- `game/simulation/event_bus.py` does not exist in this checkout; active
  simulation event-bus coverage maps to `game/simulation/combat/combat_events.py`.
- `game/strategy/facade/slices/system_slice.py`,
  `game/strategy/facade/dto/fleet_dto.py`, and
  `game/strategy/engine/game_session.py` already had broad indirect or direct
  coverage; this pass only added verified missing direct branches.
- `game/strategy/generation/density/primitives/noise.py`,
  `game/strategy/engine/production_spawner.py`, and
  `game/assets/asset_manager.py` had substantial existing normal-path
  coverage; this pass added only helper/fallback/metadata edges.
- `game/ui/screens/builder/stat_getters.py` already had coverage for resource
  fallbacks, selected formatters, and validators.

## Test Commands Run

- `pytest tests/unit/strategy/generation/density/test_density_primitive.py tests/unit/strategy/generation/density/test_geometric.py -q`
  - Result: `12 passed`
- `pytest tests/unit/ai/test_group_target_coordinator.py tests/unit/core/test_protocols_common.py -q`
  - Result: `28 passed`
- Combined targeted suite:
  - `pytest tests/unit/ai/test_group_target_coordinator.py tests/unit/core/test_protocols_common.py tests/unit/simulation/combat/test_weapon_family_handlers.py tests/unit/simulation/combat/test_weapon_registry.py tests/unit/simulation/combat/test_weapon_firing_system.py tests/unit/strategy/facade/test_event_queries.py tests/unit/strategy/services/ability_sources/test_fleet.py tests/unit/strategy/services/test_effect_ability_display.py tests/unit/strategy/validation/test_colonize_validator.py tests/unit/strategy/validation/test_superweapon_validator.py tests/unit/strategy/engine/test_base_command_handler.py tests/unit/strategy/engine/test_command_ownership.py tests/unit/strategy/generation/density/test_density_primitive.py tests/unit/strategy/generation/density/test_geometric.py -q`
  - Result: `245 passed`
- Replay serialization and component-inspector packet:
  - `pytest tests/unit/strategy/services/test_replay_verification_coordinator.py tests/unit/strategy/test_component_inspector.py tests/unit/simulation/replay/test_serialization.py -q`
  - Result: `74 passed`
- Planet order deserialization packet:
  - `pytest tests/unit/strategy/planet/test_planet_validation.py -q`
  - Initial TDD result: failed as expected on
    `test_bad_order_raises_persistence_exception` because no
    `PersistenceException` was raised.
  - Result after fix: `38 passed`
- Full suite after production deserialization change:
  - `python Tools/test_sharded/test_sharded.py`
  - Result: `18528 passed`, `4 skipped`
- Strategy engines part 1:
  - `pytest tests/unit/strategy/engine/test_component_activation_engine.py tests/unit/strategy/engine/test_planet_action_engine.py tests/unit/strategy/fleet_movement_engine/test_characterization.py`
  - Result: `46 passed`
- Strategy engines part 2:
  - `pytest tests/unit/strategy/engine/test_harvesting_engine.py tests/unit/strategy/engine/test_production_engine_queue.py -q`
  - Result: `53 passed`
- UI workshop/transfer/fleet-router packet:
  - `pytest tests/unit/ui/screens/test_strategy_fleet_command_router.py tests/unit/ui/screens/test_workshop_viewmodel_selection.py tests/unit/ui/screens/test_transfer_controller.py tests/unit/ui/screens/test_transfer_view_model.py -q`
  - Initial TDD result: failed as expected on
    `test_append_selection_toggles_existing_object_off_without_readding_duplicate`
    before the selection fix.
  - Result after fix: `86 passed`
- Simulation combat engine coordination packet:
  - `pytest tests/unit/simulation/ship_combat_engine/test_combat_ops.py tests/unit/simulation/combat/test_weapon_firing_system.py -q`
  - Result: `35 passed`
- Combined targeted suite for all files touched in this pass:
  - `pytest tests/unit/ui/screens/test_strategy_fleet_command_router.py tests/unit/ui/screens/test_workshop_viewmodel_selection.py tests/unit/ui/screens/test_transfer_controller.py tests/unit/ui/screens/test_transfer_view_model.py tests/unit/strategy/engine/test_harvesting_engine.py tests/unit/strategy/engine/test_production_engine_queue.py tests/unit/strategy/engine/test_component_activation_engine.py tests/unit/strategy/engine/test_planet_action_engine.py tests/unit/strategy/fleet_movement_engine/test_characterization.py tests/unit/simulation/ship_combat_engine/test_combat_ops.py tests/unit/simulation/combat/test_weapon_firing_system.py -q`
  - Result: `220 passed`
- Full suite after production selection change:
  - `python Tools/test_sharded/test_sharded.py`
  - First result: `18630 passed`, `3 errors`, `4 skipped`; errors were all
    Pygame display setup errors in `tests/unit/builder/test_multi_selection_logic.py`.
  - Follow-up isolation:
    `pytest tests/unit/builder/test_multi_selection_logic.py -q`
    - Result: `3 passed`
  - Rerun result:
    `python Tools/test_sharded/test_sharded.py`
    - Result: `18633 passed`, `0 failed`, `0 errors`, `4 skipped`
- UI click dispatcher and battle-results check:
  - `pytest tests/unit/ui/screens/test_strategy_click_dispatcher.py -q`
    - Result: `13 passed`
  - `pytest tests/unit/ui/test_battle_results_data.py -q`
    - Result: `9 passed`
- Strategy data and prompt helper edges:
  - `pytest tests/unit/strategy/data/test_race_caption_loader.py -q`
    - Result: `11 passed`
  - `pytest tests/unit/strategy/services/test_race_description_prompt_builder.py -q`
    - Result: `15 passed`
  - `pytest tests/unit/strategy/data/test_galaxy_system_generator.py -q`
    - Result: `29 passed`
- Strategy action timing and resupply:
  - `pytest tests/unit/strategy/services/test_action_time_resolver.py -q`
    - Result: `18 passed`
  - `pytest tests/unit/strategy/engine/test_resupply_engine.py -q`
    - Result: `28 passed`
- Simulation replay and tick phases:
  - `pytest tests/unit/simulation/replay/test_replay_player.py -q`
    - Result: `1 passed`
  - `pytest tests/unit/simulation/replay -q`
    - Result: `54 passed`
  - `pytest tests/unit/simulation/systems/test_tick_phases.py -q`
    - Result: `16 passed`
- AI battle-line and formula helper:
  - `pytest tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py -q`
    - Result: `27 passed`
  - `pytest tests/unit/simulation/components/abilities/test_ability_registry.py -q`
    - Result: `9 passed`
  - `pytest tests/unit/simulation/components/abilities -q`
    - Result: `862 passed`
- UI strategy render context:
  - `pytest tests/unit/ui/screens/strategy_render/test_context.py -q`
    - Result: `2 passed`
- Strategy ability-source adapter edges:
  - `pytest tests/unit/strategy/services/ability_sources/test_facility.py tests/unit/strategy/services/ability_sources/test_warp_point.py tests/unit/strategy/services/ability_sources/test_labels.py -q`
    - Initial result before adding branch tests: `20 passed`
    - Result after adding tests: `30 passed`
- Strategy fleet pursuer tracker defensive branch:
  - `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py -q`
    - Initial result before adding the branch test: `27 passed`
    - Result after adding tests: `28 passed`
- Simulation marker ability requirement branches:
  - `pytest tests/unit/simulation/components/abilities/test_markers.py -q`
    - Initial result before adding branch tests: `35 passed`
    - Result after adding tests: `39 passed`
- Combined targeted suite for this continuation:
  - `pytest tests/unit/strategy/services/ability_sources/test_facility.py tests/unit/strategy/services/ability_sources/test_warp_point.py tests/unit/strategy/services/ability_sources/test_labels.py tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py tests/unit/simulation/components/abilities/test_markers.py -q`
    - Result: `97 passed`
- Combined targeted suite for this continuation:
  - `pytest tests/unit/ui/screens/test_strategy_click_dispatcher.py tests/unit/ui/test_battle_results_data.py tests/unit/strategy/data/test_race_caption_loader.py tests/unit/strategy/services/test_race_description_prompt_builder.py tests/unit/strategy/data/test_galaxy_system_generator.py tests/unit/strategy/services/test_action_time_resolver.py tests/unit/strategy/engine/test_resupply_engine.py tests/unit/simulation/systems/test_tick_phases.py tests/unit/simulation/replay/test_replay_player.py tests/unit/simulation/replay tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py tests/unit/simulation/components/abilities/test_ability_registry.py tests/unit/ui/screens/strategy_render/test_context.py -q`
  - Result: `231 passed`
- Full suite after AI battle-line production change:
  - `python Tools/test_sharded/test_sharded.py`
  - Result: `18664 passed`, `0 failed`, `0 errors`, `4 skipped`
- Baseline verification before this continuation's additions:
  - `pytest tests/unit/strategy/services/test_ability_iterator.py tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py tests/integration/replay/test_replay_resolver.py tests/unit/strategy/adapters/test_simulation_adapter.py tests/unit/strategy/combat/test_post_battle_hook.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py tests/unit/strategy/test_ship_instance_damage.py tests/unit/simulation/entities/stat_contributors/test_weapons.py tests/unit/simulation/combat/test_formation_defaults.py tests/unit/strategy/engine/test_action_execution_engine.py tests/unit/strategy/engine/test_action_execution_engine_gaps.py -q`
  - Result: `142 passed`
- Strategy replay/iterator/adapter and defensive branch continuation:
  - `pytest tests/unit/strategy/services/test_ability_iterator.py tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py tests/integration/replay/test_replay_resolver.py tests/unit/strategy/adapters/test_simulation_adapter.py tests/unit/strategy/combat/test_post_battle_hook.py tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py tests/unit/strategy/test_ship_instance_damage.py -q`
  - Result: `110 passed`
- Strategy combat/services, facade/data, simulation contracts, generation/assets,
  UI workshop business logic, and local micro-edge continuation:
  - `pytest tests/unit/strategy/services/test_combat_modifier_collector.py tests/unit/strategy/facade/slices/test_system_slice.py tests/unit/strategy/facade/test_fleet_dto.py tests/unit/strategy/engine/test_game_session_from_dict.py tests/unit/simulation/combat/test_weapon_registry.py tests/unit/simulation/components/abilities/test_ability_base.py tests/unit/simulation/components/test_modifier_manager.py tests/unit/strategy/generation/density/test_noise.py tests/unit/strategy/engine/test_production_spawner.py tests/unit/strategy/engine/test_production_spawner_staging_yard.py tests/unit/assets/test_asset_manager_resolutions.py tests/unit/ui/screens/test_workshop_data_loader.py tests/unit/ui/screens/test_workshop_data_reloader.py tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py tests/unit/ui/screens/test_workshop_viewmodel_pick_up.py tests/unit/ui/screens/test_workshop_viewmodel_selection.py tests/unit/ui/screens/test_workshop_viewmodel_ship_ops.py tests/unit/ui/screens/builder/test_stat_getters.py tests/unit/core/test_constants.py tests/unit/simulation/battle_controller/test_utilities.py tests/unit/simulation/systems/test_battle_end_conditions.py tests/unit/simulation/systems/test_mass_ratio_condition.py tests/unit/strategy/data/test_classification_config.py -q`
  - Result: `439 passed`
- Simulation/core contract subset:
  - `pytest tests/unit/simulation/combat/test_weapon_registry.py tests/unit/simulation/components/abilities/test_ability_base.py tests/unit/simulation/components/test_modifier_manager.py tests/unit/simulation/systems/test_battle_end_conditions.py tests/unit/simulation/systems/test_mass_ratio_condition.py tests/unit/simulation/battle_controller/test_utilities.py tests/unit/core/test_constants.py tests/unit/strategy/data/test_classification_config.py -q`
  - Result: `264 passed`

## Suggested Next Work Packets

- Simulation stats: re-check `game/simulation/entities/ship_stats.py`
  resource aggregation and external-stat application helper branches against
  current `ship_stats` and integration tests before adding any direct tests.
- Strategy habitability/economy helpers: re-check
  `game/strategy/data/habitability_factors.py` extractor factory branches
  and any remaining `EconomySlice` claims against existing facade tests.
- Strategy superweapon/order edges: re-check
  `superweapon_order_processor.py` and order/staging-yard helper claims against
  current `test_superweapon_order_processor*` and `test_order_processor*`
  files before adding tests.
- UI-adjacent logic: only test pure business branches such as editor math
  (`gravity_target_editor.py`, `atmosphere_target_editor.py`) or
  `BuildQueueScreen` parameter/action routing with heavy UI mocked out.
- Threaded services: `game/ui/services/image/background.py` remains a
  plausible high-value packet, but treat it as concurrency code and keep tests
  deterministic with fakes and explicit shutdown.
- Any newly selected packet should repeat verification against existing tests
  first; many broad audit claims in this area were false positives.

Future agents should repeat the pattern used here: verify with `rg` and
existing tests first, add focused tests only for real gaps, and update this
file with completed scopes and command results.
