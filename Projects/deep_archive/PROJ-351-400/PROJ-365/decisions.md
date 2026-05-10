# PROJ-365: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Strategy Layer Tech Debt Review finding #3 (P2 — TurnEngine phase god object) |
| 2026-05-04 | Renumbered from PROJ-355 to PROJ-365 | Merge-conflict collision on PROJ-351..360 |
| 2026-05-04 | TickContext as cross-phase state carrier | Per findings/01 §3, a context object decouples phase 2/3/4 better than barrier phases. The Phase-320 `moved_fleet_ids` derivation lives in a phase 3 `post_exec_hook` writing into `TickContext.moved_fleet_ids`; phase 4's `args_resolver` reads it. |
| 2026-05-04 | `callable_target` is a resolver lambda, not a bound method | TurnEngine engines are lazily resolved via properties. A resolver lambda `lambda e: e.harvesting_engine.process_harvesting_tick` defers resolution until iteration time, avoiding eager engine construction during descriptor definition. |
| 2026-05-04 | New module at `engine/turn_phase_registry.py` | Per findings/01 §5/6, TurnEngineConfig (PROJ-259) bundles engine *instances* (DI), TickPhase descriptors are *metadata* (sequencing). Different concerns; different module. |
| 2026-05-04 | End-of-turn engines OUT OF SCOPE | Lines 571-602 (organics_consumption / happiness / population_growth / quality / atmosphere / water) run outside the per-tick loop. They use `_time_phase` similarly but have different lifecycle semantics. Future project could absorb them. |
| 2026-05-04 | Phase 1 = golden-list test, then refactor | TDD entry — pin the current order before refactor. Any divergence between the descriptor-driven order and the current imperative order will be caught immediately. |
| 2026-05-04 | Mid-phase logging via `post_exec_hook` + `tick_gating='only_tick_1'` | The two `_log_empire_state` calls (lines 705, 723-724) only fire on tick==1. Encoded as descriptor metadata so `_process_tick` body has zero conditional logic. |
| 2026-05-04 | PlanetModifierEffectEngine lazy import (line 751): hoist to module level if no circular deps | Per findings/02 §6, the engine is stateless per tick. The lazy import is historical; descriptor refactor is a natural moment to re-evaluate. If a circular dep is found, keep lazy via the resolver lambda. |
| 2026-05-04 | Constructor unchanged | The 18-collaborator constructor is a separate concern from `_process_tick` decomposition. Out of scope. |
| 2026-05-04 | Added `pre_exec_hook` field to `TickPhase` | The plan's checklist specified `post_exec_hook` only, but the imperative `_process_tick` calls `_log_empire_state(empires, "TURN START tick=1")` BEFORE harvesting (line 705). Encoding that as a `post_exec_hook` on a "previous" phase is awkward (harvesting is the first phase). Adding a symmetric `pre_exec_hook` keeps the descriptor declarative and lets the harvesting descriptor carry its own pre-hook. |
| 2026-05-04 | `tick_gating` is documentary; hooks self-gate via `ctx.tick` | The plan's pseudocode (`phase_3_checklist.md:43`) had the dispatch loop skip an entire phase when `tick_gating == 'only_tick_1' and tick != 1`. That would break harvesting + production on ticks 2..100. Instead, hooks themselves check `ctx.tick == 1` (`_log_turn_start_tick_1`, `_log_after_construction_tick_1`). The `tick_gating` field remains as documentary metadata + future-hook point for stricter enforcement. |
| 2026-05-04 | `planet_modifier_effects` added to `_phase_times` (now 21 keys) | The descriptor model routes EVERY per-tick phase through `_time_phase` uniformly. Pre-PROJ-365 this phase was a raw local-construct call. The 21-key dict is a tiny widening (1 extra key) and the canonical keys characterization tests were updated alongside the production change. |
| 2026-05-04 | `move_queue` carried via `TickContext` (not closure) | `movement_calc`'s `post_exec_hook` writes the returned `move_queue` onto `ctx.move_queue`; `movement_apply`'s `args_resolver` reads it back. Same pattern for `pre_movement_locations` (snapshot in `_capture_move_queue`) → `moved_fleet_ids` (derived in `_derive_moved_fleet_ids`). Pure data-flow through the context object. |

## Audit Remediation (2026-05-05)

OpenCode review `req_20260505_055831_a52654` raised 0 CRIT and 2 MAJ findings against the PROJ-365 implementation (commit `3d9519090`). MINOR / NIT findings were skipped per the remediation scope.

| Finding | Verdict | Rationale / Action |
|---------|---------|--------------------|
| MAJ-001: `planet_modifier_effects` missing from TURN PERF format string | **FIX** | The descriptor refactor explicitly routes this phase through `_time_phase` and accumulates timings into `_phase_times`. Omitting it from the perf log silently drops observability for the newly-uniform phase. Added `planet_modifier_effects=%.3fs` token + arg in phase order, between `activation_timers` and `move_calc`. |
| MAJ-002: End-of-turn phases (organics_consumption, happiness, quality_improvement, atmosphere, water_modification) missing from TURN PERF format string | **FIX** | PROJ-343 T1.2-engines routes these five through `_time_phase` for rollback safety; their timings accumulate but were never logged — five silent perf-regression vectors. Added each as a labeled `<phase>=%.3fs` token + arg after `combat`, before `population=` (the legacy alias for `population_growth`, kept verbatim for log-grep compatibility). |
| MAJ-003 (corrected to MIN): `orders=` label vs `instant_orders` dict key | **FIX** (opportunistically) | Trivial relabel folded into the same edit since the surrounding format string was already being modified. Now reads `instant_orders=%.3fs`, matching the dict key. |

**Regression guard** — added `test_turn_perf_log_format_string_includes_all_phase_keys` in `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py`. It introspects `TurnEngine.process_turn` source and asserts that every key in `_phase_times` has a corresponding labeled token in the format string, with a small allowlist of legacy log-label aliases (`population_growth → population`, `movement_calc → move_calc`, `movement_apply → move_apply`) preserved for back-compat. Future additions to `_phase_times` will fail this test until the perf log is updated, preventing recurrence.

**MIN/NIT skipped** — module docstring 14-vs-15 phase drift, request-instruction count, `tick_gating` / `error_policy` / `TICK_GATE_ONLY_TICK_1` dead-metadata notes are all out of scope for the MAJ remediation pass.

**Test results** — `pytest tests/unit/strategy/turn_engine/`: 111 passed. Full sharded suite: 17766 passed, 0 failed, 4 skipped (baseline).
