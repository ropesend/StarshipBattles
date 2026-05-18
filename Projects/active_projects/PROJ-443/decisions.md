# PROJ-443: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-18 | Project initialized from PROJ-436 Phase 2 discovery | `pytest.ini` `norecursedirs = ... data ...` matches any directory named `data` at any depth (not just the top-level `data/`), silently hiding 1575 tests in `tests/unit/strategy/data/` from the canonical sharded suite. Long-standing issue — predates PROJ-436. Surfaced when PROJ-436 Phase 2's new `test_bay_inventory_widened.py` (30 tests) didn't move the sharded count. |
| 2026-05-18 | **Fix `pytest.ini` AFTER triage, not before** | Flipping the config first would expose 65 pre-existing failures and turn the sharded gate red. Triage them in Phases 1-3 with the config still hiding them; flip the config in Phase 4 once the hidden directory is green via direct invocation; sharded gate then jumps from ~21233 to ~22700+ collected without introducing failures. |
| 2026-05-18 | **Use `--ignore=./data` in `addopts` instead of `norecursedirs = data`** | `norecursedirs` is a glob-style match against directory names (any depth, anywhere). `--ignore=./data` is a path-anchored exclusion relative to repo root, matching only the top-level `data/` directory. The latter is the intent we want. |
| 2026-05-18 | **Bundle 4 PROJ-436 deferred items in Phase 5 rather than spawning four follow-up projects** | PROJ-436's consults (Phase 3 finding (d) + (e), Phase 5 D2 caching, Phase 6 mock residue) each flagged a small, focused cleanup. Spawning four PROJ-44X projects would inflate project-management overhead. One umbrella phase here, with each sub-item as its own commit, is cleaner. |
| 2026-05-18 | **Phase 0 baseline ledger is mandatory** | PROJ-436 Phases 3/4/5/6/7 touched code that hidden tests cover (cargo manager API, Planet storage, Empire pool aggregation, protocols, transfer validator). The Phase 2 baseline of 65 failures is stale by 7 commits. Phase 0 captures the actual current state before any triage work begins. |
| 2026-05-18 | **Phase 5d (D2 large-empire profiling) only executes on a real perf signal** | Phase 5 D2 of PROJ-436 documented that `Empire.resource_pool` aggregation is net-zero cost vs the pre-PROJ-436 baseline (the deleted `_fleet_resource_pool.items()` summand was always an empty dict). No production stress test has shown a hot path. If a real signal emerges during this project or later, add caching with explicit invalidation per the PROJ-293 pattern. Otherwise document and close. |
| 2026-05-18 | **Regression guard in Phase 4 is an AST-level collection check, not a count check** | Asserting "sharded suite collects N tests" is brittle (every test addition changes N). Asserting "every `test_*.py` file under `tests/` is in the collection set" is structural and stable. |
| 2026-05-18 | **No worktrees; serial execution in main checkout** | Per user `feedback_no_worktrees.md`. PROJ-436 Phases 8/9 may run in parallel branches that the user manages on different machines; this project stays on `main`. |
| 2026-05-18 | **End-of-project Codex consult is Phase 6** | Per user `feedback_consult_at_project_end.md`. Same pattern as PROJ-436. |
