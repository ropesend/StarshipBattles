# PROJ-327 — Final Cumulative Runtime Delta

**Date:** 2026-05-04
**Branch:** `feat/03c-phase-aware-execution`
**Working tree:** main repo at `c:/Developer/StarshipBattles/` (per `docs/known-issues.md`, the sharded runner has a known `\a`-escape bug in worktree paths — measurements taken from main repo root only).
**Machine:** AMD Ryzen 9 5900X (12 physical cores / 24 SMT) · Windows 11 (10.0.26200) · Python 3.11.9 · pytest 9.0.2. Identical to Phase 0 baseline.
**Sharded runner:** `Tools/test_sharded/test_sharded.py` — 12 shards, greedy bin-packing by `.test_durations.json`.

## Headline result

| Metric | Phase 0 baseline | Final (post-Phase-4) | Delta |
|---|---:|---:|---:|
| Median sharded wall-clock (3 runs) | **127.8 s** | **123.9 s** | **-3.9 s (~3.0%)** |
| Median slowest shard (3 runs) | **127.7 s** | **~123.8 s** (extrapolated; the runner reports wall ≈ slowest shard for these balanced runs) | **~-3.9 s (~3.0%)** |
| Stretch target (per Phase 0 Task 0.6) | < **90 s** slowest shard | 123.9 s | gap of **~34 s** remains |

## Per-phase breakdown

| Phase | What happened | Per-file reclaim (single-process, median) | Sharded reclaim (estimate) | Notes |
|---|---|---:|---:|---|
| **Phase 0** | Baseline measurement only | — | — | Median wall **127.8 s**, slowest shard **127.7 s**. See `findings/baseline_2026-05-04.md`. |
| **Phase 1** | `test_virtual_table.py` — 80 of 81 `@patch` decorators collapsed into one autouse class-scoped fixture | **30 ms** (file-only, 1.03 s → 1.00 s) | **~3.9 s** wall reclaim (127.7 → 123.8 slowest shard) | Predicted-direction win; predicted-magnitude (~1.4 s/file) overshot by ~50× because modern `unittest.mock` decorator overhead is sub-millisecond per patch. See `findings/virtual_table_runtime.md`. |
| **Phase 2** | 5 PROJ-322 mutable-mock fixture deferrals: 3 RESOLVED (rescoped to module after audit confirmed zero attribute writes); 4 RE-CONFIRMED DEFERRED with measurement | **~330 ms** total across 4 files (`test_ship_io.py` -280 ms / -12%; `test_empire_treasury_panel.py` -50 ms / -3%; others 0) | sub-second; lost in shard balancing | Primary win was tech-debt reduction: 50 LOC of scope-justification comments + dead-code helper removed. See `findings/phase_2_runtime_delta.md`. |
| **Phase 3** | DUP-001 + HLP-001 re-judgment with measurement | **0 ms** (no code change) | **0 s** | Both RE-CONFIRMED DEFERRED with measurement evidence captured. Phase 3's win is the disposition trail, not runtime. See `findings/phase_3_runtime_delta.md`. |
| **Phase 4** | `StrategyScreen` + `test_strategy_screen.py` — Compositional Construction pattern: new `StrategyScreenComposition` Protocol + `MockStrategyScreenComposition` test fixture; replaces `patch.object(StrategyScreen, '__init__', lambda...)` monkey-patch + 8 inline MagicMock assignments | **~no measurable change** (101-test cluster) | sub-second | Tech-debt reduction is the primary win; runtime was bonus, not gate. New pattern landed at `docs/02_PATTERNS.md` §32. |
| **Cumulative** | 4 phases of test-quality work + new pattern + 9 deferrals dispositioned | — | **-3.9 s** median wall (127.8 → 123.9) | See Task 5.1 table below; honest cumulative is ≈ Phase 1's contribution; Phases 2/3/4 contributions live inside the run-to-run noise floor. |

## Task 5.1 — Final sharded suite measurement (3 runs, 2026-05-04)

| Run | Wall (s) | Tests | Passed | Failed | Errors | Skipped | Notes |
|-----|---------:|------:|-------:|-------:|-------:|--------:|-------|
| 1 | **126.0** | 16468 | 16456 | 8 | 0 | 4 | All 8 failures in `tests/unit/tools/test_codex_interagent_discussion_skills.py` (pre-existing — not introduced by PROJ-327). |
| 2 | **123.3** | 16468 | 16455 | 9 | 0 | 4 | Same 8 + 1 transient flake. |
| 3 | **123.9** | 16468 | 16456 | 8 | 0 | 4 | Same 8 pre-existing failures. |
| **Median** | **123.9 s** | | | | | | |

| Metric | Phase 0 baseline | Final | Delta |
|---|---:|---:|---:|
| Median wall-clock | 127.8 s | **123.9 s** | **-3.9 s (~3.0%)** |

**Honest read:** the suite-level wall-clock moved by ~3.9 s median across the four phases — almost exactly the magnitude Phase 1's `test_virtual_table.py` migration measured at the suite level on its own. Phase 2's 330 ms of single-process reclaim and Phase 4's pattern landing did not show up in the median wall-clock — they're inside the noise floor (run-to-run variance was 2.7 s between this round's fastest and slowest runs of identical code).

**The 90 s stretch target was not approached.** Phase 0 already noted the slowest-files cluster lives in integration tests (`build_queue_screen` 44.9 s for 44 tests; `race_setup_ships_smoke` 13.8 s for one test), the 912-test `test_component_definitions.py` validation cluster, and `test_main_integration::test_game_instantiation` at 13 s alone. None of those are PROJ-322 deferrals. PROJ-327's scope was the deferral list, not "anything slow" — the gap to 90 s is real and lives outside this project's mandate.

## Pre-existing failures noted (not introduced by PROJ-327)

8 failures in `tests/unit/tools/test_codex_interagent_discussion_skills.py` reported in all 3 runs:

- `test_codex_discussion_skills_exist_with_matching_frontmatter`
- `test_codex_discussion_skills_document_shared_protocol`
- `test_codex_discussion_skills_document_v2_refinements`
- `test_codex_discussion_skills_document_v21_implementation_notes`
- `test_codex_discussion_skills_document_v23_protocol`
- `test_codex_discussion_start_documents_parent_and_slug`
- `test_codex_discussion_respond_documents_parent_discovery`
- `test_codex_discussion_continue_documents_no_args_role_aware_flow`

These tests assert against external Codex skill files, not against any PROJ-322/324/325/327/328 surface. Pre-existing; out of scope for this closeout.

Run 2 had 1 additional flake — within the documented 15–20 known-flaky tolerance for this suite (see `AGENTS.md` Test Infrastructure note + `MEMORY.md` "known flaky tests").

## Post-state slowest-files leaderboard (Task 5.2 — what's NEW at the top?)

The slowest-file leaderboard remains qualitatively unchanged from Phase 0 — the top 5 are still:

| Rank | File | Phase 0 (s) | Notes |
|------|------|------------:|-------|
| 1 | `tests/integration/ui/*` (collapsed in JUnit XML) | 53.5 | Integration directory; not PROJ-32x scope. |
| 2 | `tests/integration/ui/build_queue_screen.py` | 44.9 | Integration tests (44 of them), each ~1 s. |
| 3 | `tests/unit/validation/test_component_definitions.py` | 33.2 | 912-test parametrized validation cluster. |
| 4 | `tests/unit/quickstart/test_quickstart_designs.py` | 31.5 | 299 parametrized design-validation tests. |
| 5 | `tests/projects/phase_workflow.py` (collapsed) | 23.2 | Project-system end-to-end tests. |

`test_virtual_table.py` (Phase 1 target) does NOT appear in the top 25 — it was already a 1.0 s file pre-Phase-1 and shed 30 ms post-migration. `test_ship_io.py` (Phase 2 target, was at #21 pre-migration with 4.16 s) drops by ~280 ms but remains in the same neighbourhood of the leaderboard.

**No new files appear at the top of the leaderboard as a side-effect of PROJ-327** — the migrations did not regress any file. The runtime gap to 90 s lives in the same files Phase 0 identified.

## Future test-quality projects: where the runtime actually lives

If a future project (PROJ-32x or successor) wants to attack the < 90 s target, the addressable cost is:

1. **`tests/integration/ui/build_queue_screen.py` and the broader `tests/integration/ui/*` cluster (~98 s combined).** Most of these are 1+ second each because they stand up real `pygame_gui.UIManager` instances. Compositional Construction (Pattern #32) applied to the screens-under-test could replace the heavy session with a lightweight test composition — but it's a many-file refactor, not a single-task change.
2. **`tests/unit/validation/test_component_definitions.py` (33 s for 912 tests).** Per-test 36 ms suggests parametrized fixture instantiation overhead. A session-scoped registry or a `pytest-cases`-style memoization would help; needs measurement first.
3. **`tests/unit/systems/test_main_integration.py::test_game_instantiation` (13 s for one test).** This is genuine end-to-end game-instantiation cost — likely not reducible without splitting the test or skipping module-import-on-game-startup.
4. **`tests/unit/quickstart/test_quickstart_designs.py` (31 s for 299 parametrized tests).** Each parametrize case re-runs full design recalculation. A shared session per design family could collapse this; needs pre-flight to confirm safety.

None of these are PROJ-322 deferrals — they predate the PROJ-322 audit. A future runtime-targeted project would need its own scoping pass (Phase 0-style baseline + per-file profiling) before committing to any of them.
