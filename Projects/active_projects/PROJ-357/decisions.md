# PROJ-357: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-357 | User-directed sequence start at 356; this is #2 of 5. |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #2 (P1 correctness): same-class multi-provider aura disable leaves stale value active. |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md` from initial scaffold. Mirrored canonical templates from `Projects/scripts/create_project.py` and `Reviews/scripts/review_to_project.py`. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D, default for new projects. |
| 2026-05-04 | Two-phase split: characterization then rework | Strict-TDD per AGENTS.md — golden tests for current single-provider behavior must lock in before identity rework. |
| 2026-05-04 | Identity choice deferred to Phase 2 | Need to choose between (component id + ability instance index) vs (ability instance reference + "still present" check). Decision belongs with the rework, not in plan.md scaffolding. |
| 2026-05-04 | Phase 2: Option A (`component` + `ability` references on `AuraProvider`) | Cheaper than re-resolution by id/index; the manager already holds `ship` references; "ability instance still in `component.ability_instances`" is a precise drop signal. `_recalculate` reads live `ability.value` so formula re-resolution is automatically reflected. |
| 2026-05-04 | Phase 2: skip (don't drop) providers whose component is non-operational | Components can be repaired mid-battle (functionally — fingerprint cache invalidates on op-count change). Dropping providers permanently on disable would prevent re-contribution after repair. Drop only on real identity loss (ability instance no longer in `component.ability_instances`) or on ship death/unregister. |
| 2026-05-04 | Phase 2: Bug surfaces only with same-ship-multi-provider — no wider blast radius | The buggy `_recalculate` walked the provider's *own* ship for "any same-class non-self ability." Cross-ship same-class providers were unaffected because each had their own provider record on their own ship. No other systems key on `(ship, ability_class_name)` for liveness — confirmed via grep on `AuraProvider` constructor sites (only 2 callers, both updated). |
| 2026-05-04 | Phase 2: Sharded suite pre-existing flake observed | Run #1 showed 7 `test_post_battle_hook.py` failures (`ComponentStateSpec.__init__() missing 'max_hp' and 'status'`); run #2 showed 1 different failure (`test_end_of_turn_engine_raise_wraps_in_engine_phase_error_and_records_timing`); run #3 was clean (17325 passed, 0 failed). Confirmed test-isolation flakes — unrelated to PROJ-357 (the post_battle_hook tests do construct `ComponentStateSpec` with `max_hp` and `status`, indicating the failure is intra-shard state mutation, not an API change). Working tree also has unrelated dirty changes (per AGENTS.md "don't revert unrelated changes" rule, not addressed here). |
