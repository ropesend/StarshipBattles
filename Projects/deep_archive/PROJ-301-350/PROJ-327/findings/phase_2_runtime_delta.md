# PROJ-327 Phase 2 — Runtime Delta + Disposition Summary

**Date:** 2026-05-04
**Commit:** 7b05f610a
**Branch:** `feat/03c-phase-aware-execution`

## Per-task disposition summary (5 PROJ-322 deferrals)

| PROJ-322 Task | File | Strategy | Outcome |
|---|---|---|---|
| 2.6 | tests/unit/simulation/components/test_component_resource_manager.py | **D** | RE-CONFIRMED DEFERRED |
| 2.11 | tests/unit/ui/panels/test_empire_treasury_panel.py | **A** | RESOLVED (3 of 4 fixtures rescoped to module) |
| 2.15 | tests/unit/ui/screens/test_fleet_report_filters.py | (subsumed) | Subsumed under Phase 3 Task 3.2 (HLP-001) — `make_mock_ship` is a plain function, not a fixture |
| 2.19 | tests/unit/ui/services/test_ship_io.py | **A** | RESOLVED (2 fixtures rescoped to module + `minimal_ship` deleted as dead code) |
| 3.15 | tests/unit/ui/panels/test_empire_treasury_panel.py | **D** | RE-CONFIRMED DEFERRED (private-attr read is the only observable contract worth verifying) |

## Per-file runtime delta (median of 3 single-process runs)

| File | Pre (s) | Post (s) | Delta | Reclaim |
|---|---:|---:|---:|---:|
| test_component_resource_manager.py | 1.69 | 1.69 | 0.00 | 0% (deferred) |
| test_empire_treasury_panel.py | 1.69 | 1.64 | -0.05 | ~3% |
| test_fleet_report_filters.py | 1.99 | 1.99 | 0.00 | 0% (deferred to Phase 3) |
| test_ship_io.py | 2.41 | 2.13 | **-0.28** | **~12%** |
| **TOTAL Phase 2 reclaim (single-process, 4 files)** | | | **-0.33 s** | |

The `test_ship_io.py` reclaim (~280 ms) dominates because the rescope eliminated the per-test `fresh_registries` deepcopy (54 deepcopies → 1 session-shared registry).

## Cross-isolation verification

`pytest-randomly` is NOT installed on this machine (per Phase 0 baseline note). Manual verification:
- Each rescoped file re-run 3x sequentially in normal order: byte-identical pass count.
- `test_empire_treasury_panel.py` re-run with subset of 3 tests in intentionally-shuffled order (refresh-test → construction-test → upkeep-test): all pass.
- `test_ship_io.py` re-run with subset of 3 tests in intentionally-shuffled order (default-values → tkinter-not-init → sanitize-filename): all pass.

No `reset_mock()` autouse companion was needed (Strategy C wasn't used). No cross-isolation risk introduced.

## Readability / maintainability win (the actual primary outcome)

Per user priority order (readability > maintainability > functionality > runtime), Phase 2's primary win is tech-debt reduction:

1. **`test_empire_treasury_panel.py`** — added a 21-line scope-justification comment block explaining EXACTLY why each fixture is at its scope (which fixtures are pure inputs, which mutates, why). Future readers / re-auditors don't have to re-derive the audit.
2. **`test_ship_io.py`** — same scope-justification block. Plus deleted `minimal_ship` (dead code, zero references). Plus the explanatory comment captures the mistaken original deferral rationale so future audits know what was checked.
3. **`test_component_resource_manager.py`** — added a 24-line block explaining why each rescope strategy was rejected with measurement evidence (deepcopy breaks auto-spec, reset_mock can't restore re-bound attributes, runtime is import-bound). Future re-auditors won't waste time re-trying the same dead-end.

The comments are net **+50 LOC across the 3 files**, vs the `-10 LOC` PROJ-322 originally projected from fixture compaction. The +60 LOC delta buys: dead code removal, scope-justification, and a measurable runtime reclaim. Per user priority, this is success.
