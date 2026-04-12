# PROJ-269 File Manifest

> Generated during project initialization. Used by parallel-execution protocols for conflict detection.
> Updated if implementation discovers additional files.

## Production files — new

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/simulation/battle_spec.py` | Production | 1 | `BattleSpec`, `TeamSpec`, `TaskForceSpec`, `SquadronSpec`, `ShipSpec`, `ComponentStateSpec`, `EntryVector`, `AIPolicy`, `CombatPolicies`, `PostBattleHook` |
| `game/simulation/battle_outcome.py` | Production | 1 | `BattleOutcome`, `TeamOutcome`, `TaskForceOutcome`, `ShipOutcome`, `ShipStatus`, `EndReason`, `HitRecord`, `WeaponSummary`, `ShipStats`, `ModifierApplication` |
| `game/simulation/battle_runner.py` | Production | 1, 6 | `run_battle(spec) -> BattleOutcome`; `extract_outcome(engine, spec)` helper |
| `game/simulation/combat/boundary.py` | Production | 1, 3 | `BoundaryRegion` protocol; `RectBoundary`, `CircleBoundary`, `UnboundedRegion`; `ExitPolicy` enum |
| `game/simulation/combat/modifier_stack.py` | Production | 1 | `ModifierStack`, `ModifierEntry` (source-tagged modifier) |
| `game/simulation/combat/formation.py` | Production | 1, 4 | `FormationShape` enum, `FormationSpec`; `FormationResolver`; `resolve_default_for_task_force` |
| `game/simulation/combat/telemetry.py` | Production | 1, 5 | `TelemetryLevel` enum; `WeaponSummaryAggregator`, `ShipStatsAggregator`, `HitLogRecorder` |
| `game/strategy/combat/spec_compiler.py` | Production | 1, 2, 4 | `build_strategy_battle_spec(...)` |
| `game/strategy/combat/post_battle_hook.py` | Production | 2 | `apply_outcome_to_fleets(outcome, fleets_by_team_id, empires)` |
| `game/strategy/fleets/component_state.py` | Production | 2 | `ComponentState` dataclass for persisted per-component HP |
| `game/ui/screens/battle_setup/__init__.py` | Production | 1 | New subdirectory marker |
| `game/ui/screens/battle_setup/spec_compiler.py` | Production | 1, 4 | `build_manual_battle_spec(ui_state, registries)` |
| `combat_lab/spec_compiler.py` | Production | 1, 4 | `build_test_battle_spec(scenario, registries)` |

## Production files — heavily modified

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/simulation/systems/battle_engine.py` | Production | 3 | Accept `BoundaryRegion`; N-team generalization; `engine.teams: Dict[int, List[Ship]]`; `get_enemies_of`; per-tick boundary enforcement |
| `game/simulation/systems/battle_end_conditions.py` | Production | 3 | `TeamEliminatedCondition`, `TeamIncapacitatedCondition` generalized to N teams |
| `game/simulation/battle_controller.py` | Production | 6 | Internal to `run_battle`; drop `BattleConfig` variant fields after Phase 6 |
| `game/simulation/services/battle_service.py` | Production | 6 | Pass-through updates |
| `game/simulation/entities/ship.py` | Production | 2 | Possibly add `Ship.from_spec(...)` factory if simpler than current routes |
| `game/simulation/entities/ship_serialization.py` | Production | 2 | Ensure `from_dict` round-trips per-component HP from spec |
| `game/strategy/fleets/ship_instance.py` | Production | 2 | Add `components: Dict[str, ComponentState]`; update `to_ship` / `update_from_ship` / `to_dict`/`from_dict` |
| `game/strategy/fleets/task_force.py` | Production | 4 | Add `formation: Optional[FormationSpec]` field |
| `game/strategy/fleets/fleet_battle_adapter.py` | Production | 6 | `update_from_battle_results` removed (replaced by PostBattleHook); file possibly deleted entirely |
| `game/strategy/combat/simulation_battle_resolver.py` | Production | 5, 6 | Drop ship-mutation side channels (modifiers via ModifierStack); reduce to spec → run_battle |
| `game/strategy/engine/conflict_resolution_engine.py` | Production | 6 | Call new entry point; consume outcome |
| `game/ui/screens/battle_setup_screen.py` | Production | 1, 6 | Build spec via compiler; remove `_apply_complex_modifiers` |
| `game/ui/screens/battle_screen.py` | Production | 6 | Consume `BattleOutcome` for display; no direct `BattleController` orchestration |
| `game/ui/screens/battle_results_screen.py` | Production | 6 | Accept `BattleOutcome` directly |
| `game/ui/screens/test_lab/test_executor.py` | Production | 6 | All 4 paths (visual/headless/batch/baseline) go through `run_battle` |
| `game/ui/services/battle_factories.py` | Production | 6 | `create_*_battle` functions deleted; file possibly deleted |
| `game/ai/controllers/*` | Production | 3 | `IsEnemy(self, other) = other.team_id != self.team_id`; no team_id preference |
| `combat_lab/runner.py` | Production | 1, 6 | Remove `USE_BATTLE_RUNNER` flag + legacy branch; use `run_battle` only |
| `combat_lab/services/test_execution_service.py` | Production | 6 | Remove `_is_started=True` hack |
| `combat_lab/scenarios/base.py` | Production | 1 | `TestScenario.to_spec(registries)` method |
| `combat_lab/scenarios/templates.py` | Production | 1, 6 | Templates emit specs via `to_spec`; `ComparisonScenario._run_baseline_battle` uses `run_battle` |

## Production files — deleted

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/simulation/combat/battle_mode_handler.py` | Production | 6 | All 4 handler classes removed |
| `game/simulation/battle_config.py` | Production | 6 | `BattleMode` enum removed; file either emptied or deleted depending on what `BattleConfig` retains |

## Test files — new

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `tests/unit/simulation/test_battle_spec.py` | Test | 1 | DTO shape + frozen + round-trip |
| `tests/unit/simulation/test_battle_outcome.py` | Test | 1 | DTO shape + frozen + invariants |
| `tests/unit/simulation/combat/test_boundary.py` | Test | 1, 3 | Boundary geometry + `contains` + `closest_inside_point` |
| `tests/unit/simulation/combat/test_modifier_stack.py` | Test | 1 | `ModifierStack.empty()`, entry shape |
| `tests/unit/simulation/combat/test_formation.py` | Test | 1 | `FormationShape` / `FormationSpec` type tests |
| `tests/unit/simulation/combat/test_telemetry.py` | Test | 1 | `TelemetryLevel` enum + ordering |
| `tests/unit/simulation/test_battle_runner.py` | Test | 1 | `run_battle` end-to-end with trivial spec |
| `tests/unit/combat_lab/test_spec_compiler.py` | Test | 1, 2, 4 | Combat Lab compiler produces valid spec |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` | Test | 1, 4 | Battle Setup compiler produces valid spec; no ship mutation |
| `tests/unit/strategy/combat/test_spec_compiler.py` | Test | 1, 2, 4 | Strategy compiler; populates components from ShipInstance |
| `tests/unit/strategy/fleets/test_ship_instance.py` | Test | 2 | `ShipInstance.components` field + serialization |
| `tests/unit/strategy/fleets/test_component_state.py` | Test | 2 | `ComponentState` dataclass shape |
| `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py` | Test | 2 | HP round-trip through `to_ship` / `update_from_ship` |
| `tests/unit/simulation/test_battle_runner_component_hp.py` | Test | 2 | `run_battle` honors per-component HP from spec |
| `tests/unit/strategy/combat/test_post_battle_hook.py` | Test | 2 | `apply_outcome_to_fleets` — survivors updated, destroyed removed, empty pruned |
| `tests/integration/strategy/combat/test_damage_persistence.py` | Test | 2 | E2E: damage persists across two consecutive strategy battles |
| `tests/unit/simulation/systems/test_battle_engine_boundary.py` | Test | 3 | Engine per-tick boundary enforcement |
| `tests/unit/simulation/systems/test_exit_policy.py` | Test | 3 | DESTROY / RETREAT / BOUNCE / NONE application |
| `tests/unit/simulation/systems/test_battle_engine_n_teams.py` | Test | 3 | N-team support |
| `tests/unit/ai/test_ai_n_team_targeting.py` | Test | 3 | AI targets every non-self team equally |
| `tests/unit/simulation/systems/test_battle_end_conditions_n_team.py` | Test | 3 | End conditions with N teams |
| `tests/integration/simulation/test_three_team_battle.py` | Test | 3 | 3-team runs to valid conclusion |
| `tests/integration/simulation/test_boundary_retreat.py` | Test | 3 | Ship crossing RETREAT boundary marked RETREATED |
| `tests/unit/strategy/fleets/test_task_force.py` | Test | 4 | `TaskForce.formation` serialization |
| `tests/unit/simulation/combat/test_formation_resolver.py` | Test | 4 | Each formation shape's positions; rotation invariance |
| `tests/unit/simulation/combat/test_formation_defaults.py` | Test | 4 | design_role → default formation mapping |
| `tests/unit/strategy/combat/test_spec_compiler_formation.py` | Test | 4 | Strategy compiler invokes FormationResolver |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py` | Test | 4 | Battle Setup compiler + formations |
| `tests/unit/combat_lab/test_spec_compiler_formation.py` | Test | 4 | Combat Lab compiler + CUSTOM formations |
| `tests/unit/simulation/combat/test_weapon_summary_aggregator.py` | Test | 5 | WeaponSummaryAggregator |
| `tests/unit/simulation/combat/test_ship_stats_aggregator.py` | Test | 5 | ShipStatsAggregator |
| `tests/unit/simulation/combat/test_hit_log_recorder.py` | Test | 5 | HitLogRecorder + modifier trace |
| `tests/unit/simulation/test_battle_runner_telemetry.py` | Test | 5 | Per-level outcome population |
| `tests/performance/test_telemetry_overhead.py` | Test | 5 | Measure per-level overhead |

## Test files — deleted

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `tests/unit/simulation/combat/test_battle_mode_handler.py` (if exists) | Test | 6 | Tests `BattleModeHandler` which is deleted |

## Documentation files — modified

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `docs/systems/combat_simulation.md` | Docs | 1, 2, 3, 4, 5, 6 | Pass-through note added (1); HP persistence section (2); Boundary + N-team section (3); Formation section (4); Telemetry section (5); full "Battle Orchestration" rewrite (6) |
| `docs/systems/strategy_layer.md` | Docs | 2, 4 | Note `ShipInstance.components` (2); `TaskForce.formation` (4) |
| `docs/02_PATTERNS.md` | Docs | 6 | Remove references to deleted `BattleModeHandler` pattern if any; add spec-compiler pattern note |

## Legend

- **Production**: game logic or integration code
- **Test**: pytest file
- **Docs**: markdown under `docs/`

## Notes

- Every row's `Phase` column links back to the phase where the file is first touched; subsequent phases may modify the same file further.
- Phase 6 does the final consolidation — many files see their final shape only after Phase 6.
- Parallel-execution planning: any two tasks whose `File` column rows do not overlap may be executed in parallel (see `Projects/protocols/03b_parallel_projects.md`).
