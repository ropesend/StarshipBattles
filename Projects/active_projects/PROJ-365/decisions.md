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
