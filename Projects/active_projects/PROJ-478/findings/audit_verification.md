# PROJ-478 Audit Verification

**Audit:** Codex consult 2026-05-23, leaf `AgentCoordination/Scratchpad/Consult/20260523T035353Z_audit-PROJ-478/`
**Verifier:** Claude orchestrator (Batch 1)

| id | finding | verdict | evidence | action |
|----|---------|---------|----------|--------|
| F1 | `tests/unit/builder/test_ship_loading.py:96-108` — `pytest.skip()` fires unconditionally before the `len(ship_files) >= 1` guard from phase_1 task 1.10, leaving the guard as dead code | VERIFIED + IN-SCOPE | Lines 96-101 are the unconditional skip; lines 103-108 are unreachable | Phase 4: delete the dead guard + post-skip body (lines 102-end of function), keep the skip + docstring |
| F2 | `profiling/panels/bench_panel_full_open.py:141` and `:164` still define `test_full_window_open_uncached` and `test_full_window_open_with_cache` despite manifest:34 claiming `test_* → bench_*` rename | VERIFIED + IN-SCOPE | grep shows both functions still have `test_` prefix. pytest.ini `testpaths = tests` means no live collection bug, but the manifest claim is false and the prefix is misleading | Phase 4: rename both functions to `bench_*` |
| F3 | Manifest drift — multiple entries describe abandoned plan steps as if they shipped | VERIFIED + IN-SCOPE | `manifest.md:20` says test_ship_loading.py only gained guard (it now hard-skips); `:22` says conftest deleted (still present, deliberately); `:37` says build-queue tests converted to skips (they weren't — scope decision); `:34` claims rename happened (it didn't — F2) | Phase 4: rewrite the four affected manifest rows to match shipped state |
| F4 | Phase 3 skip refusal correct — VirtualTable.invalidate_widget_caches exists in production | REJECTED (Codex self-retraction) | `game/ui/components/table/virtual_table.py:315-385` confirmed | None |
| F5 | Untracked replacements not in commit | INFORMATIONAL | Orchestrator policy is no-commits in Batch 1; user will inspect working tree | None |
