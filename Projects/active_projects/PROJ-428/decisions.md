# PROJ-428: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-16 | Project initialized from TD-04 plan | Source plan: `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified Problem Remediation Plans/TD-04_phase_registry_hooks.md`. |
| 2026-05-16 | Adopt 03c phase-aware execution protocol | TD-04 has six sequenced phases with distinct test surfaces; 03c's per-phase review boundary fits the work. |
| 2026-05-16 | No new `TurnEngineConfig` field for the planet-modifier engine | TD-04 guardrail. A `TurnEngine.planet_modifier_effect_engine` lazy property is sufficient. Adding a config field would force unrelated test/doc churn around config defaults and rehydration. |
| 2026-05-16 | No new strategy engine interface (ABC) for this refactor | TD-04 guardrail. The TD-04 plan was downgraded from "depends on TD-09" to a soft preference precisely because the lazy-property approach removes the need for a new ABC. |
| 2026-05-16 | Exactly one new collaborator (`MovementPhaseCollaborator`) for movement-specific work | TD-04 guardrail: "Create exactly one new collaborator … if needed. Do not create a separate class for every one-line hook." The other five hooks become named methods on `TurnEngine`. |
| 2026-05-16 | `MovementPhaseCollaborator` owns snapshot/diff/minefield/pruning | Single cohesive responsibility lifted from `_derive_moved_fleet_ids`. Public surface is `snapshot_before(ctx, result)` + `resolve_after(engine, ctx)`; private split is `_diff_moved_fleets`, `_mark_boosters_dirty`, `_resolve_minefields`, `_prune_destroyed_fleet_contents`. |
| 2026-05-16 | Do NOT create a separate `TurnLogger` class for the tick-1 logs | TD-04 guardrail: only split out a logger if `turn_engine.py` becomes materially less clear. Start with named methods on `TurnEngine`. Revisit only if the file balloons. |
| 2026-05-16 | Preserve `MinefieldResolver.resolve_minefield_entry(..., registries=engine._registries)` call contract exactly | TD-04 explicit non-goal: "Do not change the `registries=engine._registries` call contract." Avoids cross-cutting churn in `MinefieldResolver` itself. |
| 2026-05-16 | Preserve existing broad-catch around minefield resolution | TD-04 explicit instruction: "Keep the current broad catch around minefield resolution exactly intact." Behavior parity over stylistic cleanup. |
| 2026-05-16 | Add an AST registry-purity guard test | Prevents future drift. Future regressions will fail the moment a module-level function or a gameplay-engine import reappears in `turn_phase_registry.py`. Higher leverage than the one-time cleanup. |
| 2026-05-16 | Keep `DEFAULT_TICK_PHASE_LIST` / `DEFAULT_END_OF_TURN_PHASE_LIST` order, keys, and timing buckets unchanged | TD-04 acceptance criterion. Renaming phase keys or shuffling order is explicitly forbidden. |
| 2026-05-16 | Source TD-04 phases 0..5 renumbered to PROJ-428 phases 1..6 | `phase_state.json` and the 03c scripts index phases starting at 1. Phase intent and ordering are unchanged; only the label changes. |
| 2026-05-16 | Phase 1 (= TD-04 Phase 0) is test-only | Characterization tests must fail for the intended reason and pass against the current code before any extraction begins. No production changes in Phase 1. |
