# Phase 1.1 — Test Baseline

**Date:** 2026-05-12
**Command:** `python Tools/test_sharded/test_sharded.py`
**Result:** **20155 passed, 0 failed, 0 errors, 4 skipped** — green baseline.
**Wall time:** 132.4 s (12 shards)

## Pre-existing flakes / notes

- No flakes observed on this run.
- Highest-variance files (all under 1 s each, statistically noise-bound at this sample size):
  - `tests/unit/strategy/engine/test_fleet_speed_invariants.py` (var=153%, last=0.1 s)
  - `tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py` (var=122%)
  - `tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py` (var=111%)
  - Several others all at < 0.2 s — noise, not real flakes.
- The known LLM-background-timing flake (CLAUDE.md memory: `tests/unit/services/llm/test_background.py::test_elapsed_seconds_is_monotonic_then_frozen`) did **not** flake on this run.
- Slowest shards: `tests/performance/test_panel_full_open_benchmark.py` (87.6 s), `test_build_queue_screen_lifecycle.py` (52.1 s), `test_basics.py` for build queue (50.7 s). These are PROJ-411 / build-queue UI tests; not in scope for PROJ-412.

## Implication

Phase 1 starts from a clean tree. Any future test failures during PROJ-412 implementation are attributable to PROJ-412 changes, not pre-existing breakage.
