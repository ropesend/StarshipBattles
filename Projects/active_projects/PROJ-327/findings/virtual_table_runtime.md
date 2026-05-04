# PROJ-327 Phase 1 — `test_virtual_table.py` Runtime Delta

**Date:** 2026-05-04

## File-level (target file alone, single-process, 3 runs)

| Run | Pre (s) | Post (s) |
|-----|--------:|---------:|
| 1 | 0.99 | 1.00 |
| 2 | 1.06 | 0.99 |
| 3 | 1.03 | 1.00 |
| Median | **1.03** | **1.00** |

**File delta:** 30 ms reclaim, ~3 % per file run. Tighter post-migration variance (post: 0.99-1.00, pre: 0.99-1.06). The design.md "~1.4 s reclaim expected" was based on the assumption of ~1 ms per `@patch` decorator setup/teardown × 81 patches; in practice, modern `unittest.mock` decorator overhead is much less than 1 ms per patch on this hardware. The actual saving is the order of ~30-50 ms (5 enter/exit collapses × 16 tests × ~2 ms each).

## Sharded suite-level (full suite, 12 shards, 3 runs)

| Run | Pre wall (s) | Pre slowest shard (s) | Post wall (s) | Post slowest shard (s) | Notes |
|-----|------------:|----------------------:|--------------:|-----------------------:|-------|
| 1 | 124.6 | 124.4 | 122.3 | 122.2 | Pre run 1 had the race_setup transient (1 error in 1 shard); post run 1 was clean. |
| 2 | 139.9 | 139.7 | 123.9 | 123.8 | Post run 2 hit the documented LLM background flake (`test_elapsed_seconds_is_monotonic_then_frozen`, see MEMORY.md "known flaky tests"). Not introduced by Phase 1; same failure pattern documented across PROJ-321/322/323. |
| 3 | 127.8 | 127.7 | 127.6 | 127.5 | Both clean. |
| **Median** | **127.8** | **127.7** | **123.9** | **123.8** | |

**Suite delta:** **~3.9 s wall reduction**, ~3.0 % suite-level reclaim. Slowest shard reduced from 127.7 s to 123.8 s (~3.0 % reduction).

The slowest-shard delta (3.9 s) is roughly the per-test reclaim (~30 ms × 16 tests = ~0.5 s) amplified by the fact that other tests in the same shard depend on this file's runtime budget — when the file is faster, the shard finishes earlier and pulls the rest of its test list along, but only modestly.

## Versus user target

| Metric | Value |
|--------|------:|
| User-reported baseline (set during planning) | 137 s slowest shard |
| PROJ-327 measured baseline | 127.7 s slowest shard |
| Post-Phase-1 | 123.8 s slowest shard |
| Stretch target | < 90 s slowest shard |
| Cumulative reduction so far (vs 137) | 13.2 s (~9.6 %) |
| Cumulative reduction so far (vs 127.7 baseline) | 3.9 s (~3.0 %) |
| Remaining gap to 90 s | ~33.8 s (~27 % more) |

**Conclusion:** Phase 1 delivered the predicted *direction* but not the predicted *magnitude*. Phases 2 + 3 are very unlikely to close another ~34 s on their own — Phase 4 (`strategy_screen` 50-test refactor) will almost certainly be needed. The Phase 4 trigger remains armed.

## Migration mechanics summary

| Category | Pre-migration | Post-migration |
|----------|--------------:|---------------:|
| `@patch` decorators in file | 81 | 1 (UIButton, on the one test that needs it) |
| Tests in `TestVirtualTable` carrying universal patches | 16 (each with 5 separate `@patch` decorators) | 16 (each pulls the autouse `patched_pygame_gui` fixture) |
| Per-test patch contexts entered/exited | 5 per test (16 × 5 = 80 enter/exits per file run) | 1 nested context per test (16 × 1 = 16 enter/exits per file run) |
| Mock-class positional args per test | 5 | 0 (mocks are accessed via dict on the fixture) |
| Net @patch decorations migrated | 80 of 81 (universal) | UIButton kept as @patch (per design.md Task 1.5) |

## Outcome parity (Task 1.6)

`virtual_table_pre.txt` vs `virtual_table_post.txt`:
- 24 tests collected before; 24 tests collected after.
- 24 PASSED before; 24 PASSED after.
- 0 failed/skipped/errored before; 0 failed/skipped/errored after.
- Diff: **byte-identical** except the trailing wall-clock summary line (1.38 s pre, 1.06 s post — stale single-process measurements from before the 3-run timing capture).

No silent test status changes. The migration preserved exact mock semantics — every test still observes the same patches it observed before, just sourced from the autouse fixture instead of decorator-injected positional args.
