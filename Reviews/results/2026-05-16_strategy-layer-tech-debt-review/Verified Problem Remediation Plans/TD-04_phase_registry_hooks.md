# TD-04: Move business behavior out of `turn_phase_registry.py` hooks

**Status:** VERIFIED
**Source report:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/report.md` section TD-04
**Primary file under review:** `game/strategy/engine/turn_phase_registry.py`
**Primary consumer:** `game/strategy/engine/turn_engine.py`

---

## Verification Summary

This problem is real and still present in the current code.

`game/strategy/engine/turn_phase_registry.py` is supposed to be a descriptor module, but it currently contains six behavior-bearing helpers:
- `_log_turn_start_tick_1`
- `_log_after_construction_tick_1`
- `_accumulate_env_events`
- `_capture_move_queue`
- `_derive_moved_fleet_ids`
- `_resolve_planet_modifier_effects`

The worst offender is `_derive_moved_fleet_ids`, which performs movement diffing, `_booster_dirty` propagation, minefield resolution, and fleet pruning. `_resolve_planet_modifier_effects` is also misplaced because it constructs and caches a gameplay collaborator from inside the registry module.

The fix is still the same in principle: keep the phase list declarative, and move real work onto `TurnEngine` or a named collaborator owned by `TurnEngine`.

---

## End State

The finished shape must satisfy all of these:
- `turn_phase_registry.py` contains only descriptor data, dataclasses, and constants.
- `DEFAULT_TICK_PHASE_LIST` and `DEFAULT_END_OF_TURN_PHASE_LIST` keep the same order, phase keys, timing buckets, and gating semantics.
- `turn_phase_registry.py` imports no gameplay engine classes such as `PlanetModifierEffectEngine` or `MinefieldResolver`.
- The movement-only post-phase logic has a named home with direct unit tests.
- `TurnEngine.last_environmental_events`, `_booster_dirty`, minefield behavior, and `TURN PERF` output remain behaviorally unchanged.

---

## Weak-LLM Guardrails

- Do not rename any phase key.
- Do not rename any timing bucket.
- Do not add a new strategy engine interface just for this refactor.
- Do not add a new `TurnEngineConfig` field unless an existing failing test forces it.
- Prefer extending existing test files over creating speculative new ones.
- Keep logging and env-event glue on `TurnEngine` unless a separate class is clearly necessary.
- Create exactly one new collaborator for the movement-specific work if needed. Do not create a separate class for every one-line hook.

---

## File Touch Map

Files that should change:
- `game/strategy/engine/turn_phase_registry.py`
- `game/strategy/engine/turn_engine.py`
- optional new `game/strategy/engine/movement_phase_collaborator.py`

Files that may change if required by implementation details:
- `game/strategy/engine/planet_modifier_effect_engine.py`
- `game/strategy/engine/minefield_resolver.py`
- `docs/systems/strategy_layer.md`

Existing tests to extend first:
- `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`
- `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py`
- `tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py`
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
- `tests/unit/strategy/engine/test_turn_engine_config.py`
- `tests/unit/strategy/engine/test_no_lazy_fallback_init.py`
- `tests/integration/test_fms_b_e2e.py`
- `tests/integration/test_fms_b_statistical_balance.py`

New test files are acceptable only where there is no clean existing home:
- `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py`
- `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`

---

## Phased Remediation Plan

### Phase 0 - Freeze the real contract with red tests

Add failing or characterization tests before moving code.

Required assertions:
- `ctx.last_environmental_events` accumulates returned environmental events.
- `movement_calc` still stores both `move_queue` and `pre_movement_locations`.
- `movement_apply` still computes `moved_fleet_ids`.
- `_booster_dirty` flips only for empires whose fleets moved.
- `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)` is still used.
- Fleets emptied by minefield damage are removed from the owning empire.

Preferred test homes:
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
- `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

Do not start extraction work until these tests fail for the intended reason and pass against the current code.

### Phase 1 - Move planet-modifier engine resolution onto `TurnEngine`

Touch list:
- `game/strategy/engine/turn_engine.py`
- `game/strategy/engine/turn_phase_registry.py`
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
- `tests/unit/strategy/engine/test_no_lazy_fallback_init.py`

Steps:
1. Add a failing test that proves `turn_phase_registry.py` no longer imports `PlanetModifierEffectEngine`.
2. Add a `TurnEngine.planet_modifier_effect_engine` lazy property that owns the cache currently hidden in the registry module.
3. Change the descriptor resolver to `lambda e: e.planet_modifier_effect_engine.process_modifier_effects_tick`.
4. Delete `_resolve_planet_modifier_effects` from `turn_phase_registry.py`.

Important constraint:
- Do **not** add a new `TurnEngineConfig` field if a lazy property alone solves the problem. That extra field would create unrelated test and doc churn.

### Phase 2 - Move small hook logic onto named `TurnEngine` methods

Touch list:
- `game/strategy/engine/turn_engine.py`
- `game/strategy/engine/turn_phase_registry.py`
- `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`

Required engine methods:
- one method for the tick-1 pre-harvesting log;
- one method for the tick-1 post-production log;
- one method for env-event accumulation.

Steps:
1. Add failing tests for each method.
2. Implement named methods on `TurnEngine`.
3. Repoint the registry hooks at those methods.
4. Delete `_log_turn_start_tick_1`, `_log_after_construction_tick_1`, and `_accumulate_env_events`.

Do not create a separate `TurnLogger` file unless `turn_engine.py` becomes materially less clear without it.

### Phase 3 - Extract the movement-only collaborator

This is the only behavior here that warrants its own dedicated object.

Touch list:
- `game/strategy/engine/turn_engine.py`
- `game/strategy/engine/turn_phase_registry.py`
- optional new `game/strategy/engine/movement_phase_collaborator.py`
- `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py`
- optional new `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`

Required public methods on the collaborator:
- `snapshot_before(ctx, result)`
- `resolve_after(engine, ctx)`

Recommended private split:
- `_diff_moved_fleets(ctx)`
- `_mark_boosters_dirty(empires, moved_owner_ids)`
- `_resolve_minefields(engine, ctx, moved_fleets)`
- `_prune_destroyed_fleet_contents(owning_empire, fleet, destroyed_ship_ids)`

Execution steps:
1. Add failing tests for snapshot-before and resolve-after behavior.
2. Move `_capture_move_queue` into `snapshot_before`.
3. Move `_derive_moved_fleet_ids` into `resolve_after`.
4. Keep the current broad catch around minefield resolution exactly intact.
5. Wire the `movement_calc` and `movement_apply` hooks to the collaborator.
6. Delete the old registry hook functions.

Do not:
- change how `engine=None` descriptor tests behave;
- move minefield resolution to a different phase;
- change the `registries=engine._registries` call contract.

### Phase 4 - Add a registry-purity guard

Touch list:
- `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py` or `test_tick_phase_descriptors.py`

The guard must enforce:
- no module-level functions remain in `turn_phase_registry.py`;
- no gameplay engine imports remain there;
- descriptor order and keys are unchanged.

### Phase 5 - Validate and document

Run, at minimum:

```bash
pytest tests/unit/strategy/turn_engine/ -x
pytest tests/unit/strategy/engine/test_turn_engine_config.py tests/unit/strategy/engine/test_no_lazy_fallback_init.py -x
pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_b_statistical_balance.py -x
```

Only after those are green:

```bash
python Tools/test_sharded/test_sharded.py
```

Update `docs/systems/strategy_layer.md` only if it explicitly describes hook placement or registry ownership.

---

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| A weak LLM changes phase order or keys while moving code. | Lock order and keys first with descriptor tests. |
| The refactor adds unnecessary interfaces or config fields. | Explicitly forbid that unless an existing failing test requires it. |
| Minefield behavior drifts subtly. | Require focused movement tests plus `test_fms_b_e2e.py` before the sharded run. |
| `engine=None` descriptor tests start evaluating hook bodies. | Keep hook wiring as resolvers and callable references, not eager calls. |
| The movement collaborator becomes another grab-bag object. | Limit it strictly to movement snapshotting, movement diffing, minefield handling, and pruning. |

---

## Ordering Constraints

Hard ordering constraints:
- None.

Soft ordering notes:
- TD-09 is **not** a blocker. This plan no longer assumes a new engine interface.
- TD-10 is **not** a blocker. The collaborator can keep using `MinefieldResolver` until TD-10 changes that subsystem.

Effect on `EXECUTION_ORDER.md`:
- Any hard `TD-09 -> TD-04` dependency should be downgraded to a soft preference or removed.

---

## Acceptance Criteria

- [ ] `turn_phase_registry.py` defines no module-level behavior functions.
- [ ] `turn_phase_registry.py` imports no gameplay engine classes.
- [ ] `DEFAULT_TICK_PHASE_LIST` and `DEFAULT_END_OF_TURN_PHASE_LIST` keep the same phase keys and order.
- [ ] `TURN PERF` output format is unchanged.
- [ ] `TurnEngine.last_environmental_events` behavior is unchanged.
- [ ] `_booster_dirty` behavior is unchanged.
- [ ] Minefield resolution still runs after movement and before combat with `registries=engine._registries`.
- [ ] Fleets destroyed by minefields are pruned exactly as before.
- [ ] Focused turn-engine and FMS-B suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
