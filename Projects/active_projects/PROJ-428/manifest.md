# PROJ-428 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/turn_phase_registry.py` | Production | Remove six module-level hook helpers; remove gameplay engine imports; repoint descriptors at `TurnEngine` properties/methods or the new collaborator. |
| `game/strategy/engine/turn_engine.py` | Production | Add `planet_modifier_effect_engine` lazy property; add named methods for tick-1 logs and env-event accumulation; own `MovementPhaseCollaborator` instance; wire collaborator into `movement_calc` and `movement_apply` hooks. |
| `game/strategy/engine/movement_phase_collaborator.py` | Production (new) | New collaborator with `snapshot_before(ctx, result)` and `resolve_after(engine, ctx)`. Private split: `_diff_moved_fleets`, `_mark_boosters_dirty`, `_resolve_minefields`, `_prune_destroyed_fleet_contents`. Preserves `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)` contract and existing broad-catch. |
| `game/strategy/engine/planet_modifier_effect_engine.py` | Production (may change) | Only if implementation needs to expose a no-arg constructor or adjust caching surface. No behavior change expected. |
| `game/strategy/engine/minefield_resolver.py` | Production (may change) | Only if implementation needs to expose a constructor surface the collaborator can call. Public call contract unchanged. |
| `docs/systems/strategy_layer.md` | Documentation (may change) | Only if it explicitly describes hook placement or registry ownership. |
| `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py` | Test (modify) | Add characterization assertions for env-event accumulation, descriptor wiring; possibly host the AST registry-purity guard. |
| `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` | Test (modify) | Golden assertions on phase keys / order / timing buckets unchanged. |
| `tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py` | Test (modify) | Golden assertions on end-of-turn list unchanged. |
| `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py` | Test (modify) | Extend with red tests for `move_queue` / `pre_movement_locations` snapshotting, `moved_fleet_ids` derivation, `_booster_dirty` flips, minefield call contract, fleet pruning. |
| `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` | Test (modify) | Add coverage for new `planet_modifier_effect_engine` lazy property. |
| `tests/unit/strategy/engine/test_turn_engine_config.py` | Test (modify) | Verify NO new config field was added; existing behavior preserved. |
| `tests/unit/strategy/engine/test_no_lazy_fallback_init.py` | Test (modify) | Confirm the new lazy property does not regress the no-lazy-fallback rule. |
| `tests/unit/strategy/turn_engine/test_turn_phase_registry_purity.py` | Test (new, optional) | AST-driven guard: no module-level functions, no gameplay engine imports, descriptor order/keys unchanged. May be folded into `test_tick_phase_descriptors.py` instead. |
| `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py` | Test (new, optional) | Unit coverage for `MovementPhaseCollaborator.snapshot_before` / `resolve_after` and the private split. |
| `tests/integration/test_fms_b_e2e.py` | Test (regression gate) | Must stay green; covers end-to-end movement+minefield path. |
| `tests/integration/test_fms_b_statistical_balance.py` | Test (regression gate) | Statistical balance regression gate for movement-affected outcomes. |
