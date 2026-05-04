# PROJ-327: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | User direction: full unit test suite takes >2 minutes on a 12-core machine; this is a measured problem. PROJ-327 picks up all 9 PROJ-322 deferrals not addressed by PROJ-324. |
| 2026-05-04 | **D-001:** Project does NOT start until PROJ-326 reports Complete | Per user direction: "they can be deferred but when 326 is done I want to work on them." |
| 2026-05-04 | **D-002:** Phase 0 baseline measurement is mandatory before any change | Without baseline, deltas are unprovable. The user's "2-minute" pain is the input; quantified per-file/per-shard runtimes are the success metric. |
| 2026-05-04 | **D-003:** Phase 1 (`test_virtual_table.py` `@patch` sweep) is highest-leverage | 81 decorators × 17 tests = ~1.4 seconds in one file alone (~1ms per `@patch` setup/teardown). Plus all-tests overhead even when the patched dependency isn't observed. |
| 2026-05-04 | **D-004:** Phase 4 (`strategy_screen` 50-test refactor) is CONDITIONAL | Only execute if Phases 1-3 cumulative delta is insufficient. The OpenCode 322-review estimated this as a "multi-day production refactor" — not worth it if Phases 1-3 already hit the target. |
| 2026-05-04 | **D-005:** If Phase 4 estimate exceeds 3 LLM-paced sessions, stop and surface to user | Risk-mitigation against scope creep. A multi-day refactor that grows into a months-long effort should become its own scoped project, not balloon PROJ-327. |
| 2026-05-04 | **D-006:** Re-confirmation of PROJ-322 deferred items as deferred is a VALID outcome | Phase 3 (DUP-001 + HLP-001) may conclude that even with runtime context, the builder-pattern factory is still net complexity-positive. That outcome must be documented (closed with rationale), NOT silently dropped. The user directed: "I do not want the additional issues forgotten." Re-confirmation closure honors that. |
| 2026-05-04 | **D-007:** Pre-flight verification before each task | PROJ-322 deferrals are stale by the time PROJ-327 starts. Each task verifies the cited file still exists and the cited tests still exist before doing work. Obsolete tasks are marked obsolete (not silently skipped). |
| 2026-05-04 | **D-008:** Use `pytest-randomly` for Phase 2 cross-isolation testing if available | The `reset_mock()` autouse pattern (rejected by PROJ-322) is the obvious unblock for class-scoped fixtures with mutation. If used, surface the cross-isolation risk with `pytest-randomly` ordering tests. |
| 2026-05-04 | **D-009:** Run baseline measurement 3x and take the median | Sharded test runtime varies ±10% between runs. Single measurements are noise-dominated for the kinds of deltas this project will produce. |
| 2026-05-04 | **D-010:** Branch strategy: same as PROJ-324/325/326 unless those have merged to main first | If the 3 prior projects merge to main before PROJ-327 starts, branch off main. Otherwise continue on `feat/03c-phase-aware-execution`. |
