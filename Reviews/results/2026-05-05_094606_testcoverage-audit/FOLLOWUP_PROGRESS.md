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

## Suggested Next Work Packets

Continue with P1/P2 items that were not touched in this pass:

- Strategy engines: `planet_action_engine.py`, `harvesting_engine.py`,
  `production_engine.py`, `consumable_management_engine.py`,
  `fleet_movement_engine.py`, `component_activation_engine.py`,
  `organics_consumption_engine.py`, and `water_engine.py`.
- Simulation: `ship_combat_engine.py`, `ship_resource_manager.py`, and
  remaining `weapon_firing_system.py` branch coverage beyond existing
  integration tests.
- UI business logic: `strategy_fleet_command_router.py`,
  `workshop_viewmodel_selection.py`, `transfer_controller.py`,
  `battle_results_data.py`, `strategy_click_dispatcher.py`, and
  `transfer_view_model.py`.

Future agents should repeat the pattern used here: verify with `rg` and
existing tests first, add focused tests only for real gaps, and update this
file with completed scopes and command results.
