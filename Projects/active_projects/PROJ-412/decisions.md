# PROJ-412: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-10 | Project initialized from `Projects/Triage/turn_processing_performance.md` via `/claude-triage-to-proj` | Triage scoped this as cross-cutting and profiling-first, warranting a full project rather than a single bug ticket |
| 2026-05-10 | Project title: **"Reduce Strategy Turn Processing Time"** | User selected (outcome-focused framing) over "Profile and Optimize" and "Investigation" alternatives |
| 2026-05-10 | Reference scenario: 2 empires, 2 planets, a handful of ships, no active combat | User: "right now I just want to make small games playable. … Right now the criteria is 2 empires 2 planets and a handful of ships." |
| 2026-05-10 | Phase 1 scope: everything except combat (`ConflictResolutionEngine`) | User: "Worry about everything except combat, combat is a completely separate issue, and it takes a long time." |
| 2026-05-10 | 100-tick-per-turn subturn loop is preserved | User: "I want to maintain the 100tick system" |
| 2026-05-10 | No forward assumptions across ticks | User: "we cannot make assumptions about production 2 turns later, because a battle could occur that destroys the producing infrastructure at some point during the turn" |
| 2026-05-10 | Long-term port to Rust/C++ is out of scope here | User: "Eventually the entire game will be ported to rust or C++ and be sped up a lot, but right now I just want … the existing system to be coded as efficiently as possible" |
| 2026-05-10 | Phase plan: 1 Measure → 2 Cheap wins → 3 Harvesting cache → 4 Orchestration → 5 Secondary phases (conditional) | Triage notes called for "Phase 1: measurement; phases 2+: subsystem-specific optimization work". Swarm findings point to harvesting (~50%) and orchestration overhead (~30%) as the two main targets. |
| 2026-05-10 | Cache strategy: per-turn key + dirty-flag invalidation set by write services | Mirrors the PROJ-285 per-turn habitability cache already in the codebase; matches the documented `docs/02_PATTERNS.md` conventions; smaller invalidation surface than version counters |
| 2026-05-10 | Phase ordering (descriptor lists) is frozen | Enforced by golden tests `test_default_tick_phase_list.py` / `test_default_end_of_turn_phase_list.py`; all optimizations live inside sub-engines or orchestration, not in the descriptor list |
| 2026-05-10 | New benchmark `tests/performance/bench_turn_processing.py` is the acceptance gate | Per `tests/performance/bench_galaxy_planet_star.py` convention: fixed seed, fixed scenario, N min-of-runs, baseline JSON sibling, CI budget < 30 s |
| 2026-05-10 | Full sharded test-suite baseline run deferred to Phase 1 start | Profiling-first project — no production code changes in planning; the baseline run is the first action of Phase 1 |
| 2026-05-10 | Phases 3-5 are conditional on Phase 1 findings | If the profile contradicts the pre-profile hypothesis (harvesting dominant, snapshot/callback heavy), the phase ordering will be re-justified before Phase 2 starts |
| 2026-05-10 | Aspirational target: **~10× speedup** on the tiny scenario (~7.5 s → ~0.75 s) | User: "I have no idea what is possible, I'm hoping that it can be at least 10x as fast, but we will see what we can turn up and improve." This is the *aspiration*, not a hard gate — Phase 1 will measure the ceiling and the final acceptance number is agreed at the end of Phase 4 |
| 2026-05-10 | Progress-callback coarsening is in scope for Phase 4 | User: "I am open to reducing UI call backs." Phase 4.3 may reduce per-tick callback to every Nth tick (proposed default: every 5 ticks → 20 callbacks/turn). Final cadence still surfaced for confirmation if it changes UX visibly |
| 2026-05-10 | All Phase 2 "skip when nothing to do" short-circuits are in scope | User: "I'm fine with skipping anything that has nothing to do at any time." Confirms full Phase 2 task list (storms, orders, planet actions, component activation transitions, etc.) |
