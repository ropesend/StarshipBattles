# PROJ-412 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

Phases 4-6 manifest entries are **conditional** on Phase 1 confirming the swarm-review hypothesis; remove rows if Phase 1 measurement reorders priorities. Phase 3 (booster pipeline migration) is committed.

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/performance/bench_turn_processing.py` | Test | NEW — Phase 1 benchmark (fixed-seed tiny scenario, 10-turn run, captures `_phase_times`) |
| `tests/performance/bench_turn_processing.baseline.json` | Test | NEW — baseline JSON sibling; updated after each phase |
| `tests/integration/strategy/turn_engine/test_mid_turn_invariants.py` | Test | NEW — three characterization tests (facility completion, harvester destruction, booster arrival) |
| `tests/unit/strategy/engine/test_harvesting_engine.py` | Test | MODIFY — rewrite `test_recalculate_storage_called_each_tick` from call-count to invariant assertion (Phase 1.6) |
| `tests/unit/strategy/turn_engine/test_turn_engine_progress_callback.py` | Test | MODIFY — update cadence assertion if Phase 4.3 changes callback cadence |
| `tests/unit/strategy/engine/test_planet_energy_engine.py` | Test | MODIFY — add cache-aware assertions (Phase 5.1) |
| `tests/unit/strategy/services/test_planet_write_service.py` | Test | MODIFY — assert `_storage_dirty` flips on mutator path (Phase 3.1) |
| `tests/unit/strategy/services/test_empire_write_service.py` | Test | MODIFY — same as above for empire-level state |
| `findings/profile_baseline_cpu.md` | Doc | NEW — Scalene top-30 hotspot report + unaccounted-overhead attribution table (Phase 1.3/1.4) |
| `findings/test_baseline.md` | Doc | NEW — full-suite baseline run record (Phase 1.1) |
| `game/strategy/engine/harvesting_engine.py` | Production | Phase 2 (late-import move); Phase 3.3 (booster scan rewrite to use `IAbilitySource` pipeline); Phase 4 (storage + booster + per-facility ability caches) |
| `game/strategy/services/strategic_ability_scanner.py` or `system_effects_collector.py` | Production | Phase 3.3 — new helper for `IAbilitySource`-pipeline-based scope scan, or refactor of the existing helper to accept the new pipeline |
| `game/strategy/services/ability_iterator.py` | Production | Phase 3.3 — may need a focused iteration API for harvest-scope queries (read-only consult of existing API first) |
| `game/strategy/engine/turn_engine.py` | Production | Phase 2 (late-import move); Phase 5 (snapshot + `_run_phases` micro-fixes) |
| `game/strategy/engine/turn_state_snapshot.py` | Production | Phase 5.1 — narrow snapshot to actually-restored fields |
| `game/strategy/engine/environmental_hazard_engine.py` | Production | Phase 2 (storm short-circuit); Phase 4.3 (booster invalidation hook on ship death); Phase 6.2 (storm cache) |
| `game/strategy/engine/order_processor.py` | Production | Phase 2 (join-order short-circuit) |
| `game/strategy/engine/action_execution_engine.py` | Production | Phase 2 (action-order short-circuit) |
| `game/strategy/engine/planet_action_engine.py` | Production | Phase 2 (planet-action short-circuit) |
| `game/strategy/engine/component_activation_engine.py` | Production | Phase 2 (no-transitions short-circuit) |
| `game/strategy/engine/planet_energy_engine.py` | Production | Phase 6.1 — remaining work proven by profiling (most cache infra already exists) |
| `game/strategy/engine/fleet_movement_engine.py` | Production | Phase 4.3 (booster invalidation hook for fleet movement, now real per Phase 3); Phase 6.3 (pathfind memoization) |
| `game/strategy/engine/production_engine.py` | Production | Phase 4.1 / 4.3 — set `_storage_dirty` / `_booster_dirty` flags on facility completion |
| `game/strategy/data/empire.py` | Production | Phase 4.1 — add transient `_storage_dirty` / `_booster_dirty` fields |
| `game/strategy/services/planet_write_service.py` | Production | Phase 4.1 — flip `_storage_dirty` on `add_facility` / `remove_facility` / operational toggle |
| `game/strategy/services/empire_write_service.py` | Production | Phase 4.1 — flip flags as needed when storage changes route through here |
| `game/strategy/engine/turn_engine_config.py` | Production | Phase 2.3 — only if `PlanetModifierEffectEngine` moves into DI |
| `game/strategy/engine/turn_phase_registry.py` | Production | Phase 5.2 — only if `args_resolver` reuse is implemented; phase ORDER does not change |
| `docs/systems/strategy_layer.md` | Doc | Phase 3.4 (fleet boosters now in scope); Phase 6.4 (mention the new caching contracts) |
| `docs/systems/production_system.md` | Doc | Phase 3.4 (booster pipeline change); Phase 6.4 — mention `_storage_dirty` flip on facility completion if applicable |
| `docs/guides/performance_profiling.md` | Doc | Phase 6.4 — reference `bench_turn_processing.py` |
