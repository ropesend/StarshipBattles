# PROJ-412 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

**Phase reordering (2026-05-12)**: Phase 1 measurement reordered the plan — Phase 4 is now UI callback coarsening (was 5.3), Phase 5 is harvesting cache (was 4), Phase 6 is remaining orchestration (snapshot + `_run_phases`; was 5.1/5.2), Phase 7 is secondary phases + final docs (was 6). Phases 6 and 7 are **conditional**: gated on remeasurement after Phases 4 and 5 land. Phase 3 (booster pipeline migration) is committed.

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
| `game/strategy/engine/harvesting_engine.py` | Production | Phase 2 (late-import move); Phase 3.3 (booster scan rewrite to use `IAbilitySource` pipeline); Phase 5 (storage + booster + per-facility ability caches) |
| `game/strategy/services/strategic_ability_scanner.py` or `system_effects_collector.py` | Production | Phase 3.3 — new helper for `IAbilitySource`-pipeline-based scope scan, or refactor of the existing helper to accept the new pipeline |
| `game/strategy/services/ability_iterator.py` | Production | Phase 3.3 — may need a focused iteration API for harvest-scope queries (read-only consult of existing API first) |
| `game/strategy/engine/turn_engine.py` | Production | **Phase 4 (callback cadence — Task 4.2)**; Phase 2 (late-import move); Phase 6 (snapshot + `_run_phases` micro-fixes if remeasurement shows them) |
| `game/strategy/engine/turn_state_snapshot.py` | Production | Phase 6.1 — narrow snapshot to actually-restored fields (only if remeasurement justifies) |
| `game/ui/screens/strategy_game_state_manager.py` | Production | **Phase 4 (callback comment block — Task 4.3)** |
| `game/strategy/engine/environmental_hazard_engine.py` | Production | Phase 2 (storm short-circuit); Phase 5.3 (booster invalidation hook on ship death); Phase 7.2 (storm cache) |
| `game/strategy/engine/order_processor.py` | Production | Phase 2 (join-order short-circuit) |
| `game/strategy/engine/action_execution_engine.py` | Production | Phase 2 (action-order short-circuit) |
| `game/strategy/engine/planet_action_engine.py` | Production | Phase 2 (planet-action short-circuit) |
| `game/strategy/engine/component_activation_engine.py` | Production | Phase 2 (no-transitions short-circuit) |
| `game/strategy/engine/planet_energy_engine.py` | Production | Phase 7.1 — remaining work proven by profiling (most cache infra already exists) |
| `game/strategy/engine/fleet_movement_engine.py` | Production | Phase 5.3 (booster invalidation hook for fleet movement, now real per Phase 3); Phase 7.3 (pathfind memoization) |
| `game/strategy/engine/production_engine.py` | Production | Phase 5.1 / 5.3 — set `_storage_dirty` / `_booster_dirty` flags on facility completion |
| `game/strategy/data/empire.py` | Production | Phase 5.1 — add transient `_storage_dirty` / `_booster_dirty` fields |
| `game/strategy/services/planet_write_service.py` | Production | Phase 5.1 — flip `_storage_dirty` on `add_facility` / `remove_facility` / operational toggle |
| `game/strategy/services/empire_write_service.py` | Production | Phase 5.1 — flip flags as needed when storage changes route through here |
| `game/strategy/engine/turn_engine_config.py` | Production | Phase 2.3 — only if `PlanetModifierEffectEngine` moves into DI |
| `game/strategy/engine/turn_phase_registry.py` | Production | Phase 6.2 — only if `args_resolver` reuse is implemented; phase ORDER does not change |
| `tests/performance/bench_turn_processing.py` | Test | **NEW (Phase 1.2, landed) — captures per-turn metrics from `_phase_times` plus total wall-clock** |
| `tests/performance/bench_turn_processing.baseline.json` | Test | **NEW (Phase 1.2, landed) — baseline JSON sibling, refreshed at the end of each phase** |
| `tests/integration/strategy/turn_engine/test_mid_turn_invariants.py` | Test | **NEW (Phase 1.5, landed) — 4 passing + 1 xfail-pending Phase 3** |
| `tests/unit/strategy/engine/test_harvesting_engine.py` | Test | **Phase 1.6 audit comment added (landed)** |
| `tests/unit/strategy/engine/test_turn_engine_progress_callback.py` | Test | **Phase 4.1 done** — replaced 100-invocation pin with new cadence (1, every Nth, 100) |
| `game/strategy/engine/turn_engine_settings.py` | Production | **Phase 4.2 done** — NEW: `TurnEngineSettings` dataclass + `load_turn_engine_settings` loader following `replay_settings.json` pattern |
| `output/settings/turn_engine_settings.json` | Settings | **Phase 4 done** — NEW user-editable JSON (`progress_callback_interval`, default 5, clamped `[1, 100]`); created on-demand; absent file falls back to defaults |
| `game/core/paths.py` | Production | **Phase 4.2 done** — `TURN_ENGINE_SETTINGS_FILE` path constant |
| `tests/unit/strategy/engine/test_turn_engine_settings.py` | Test | **Phase 4.2 done** — NEW: 10 tests for missing-file / corrupt-JSON / clamping |
| `docs/systems/strategy_layer.md` | Doc | Phase 3.4 (fleet boosters now in scope); Phase 4.3 (new callback cadence); Phase 7.4 (mention the new caching contracts) |
| `docs/systems/production_system.md` | Doc | Phase 3.4 (booster pipeline change); Phase 7.4 — mention `_storage_dirty` flip on facility completion if applicable |
| `docs/guides/performance_profiling.md` | Doc | Phase 7.4 — reference `bench_turn_processing.py` |
