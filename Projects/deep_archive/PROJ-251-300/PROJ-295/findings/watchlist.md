# PROJ-295 Watchlist

Observation window: **2026-04-26** (compressed — user opted for same-day completion).

## Sharded suite stability (Phase 5 verification)

Three back-to-back runs on Python 3.13.13 venv:

| Run | Result | Wall time | Notes |
|-----|--------|-----------|-------|
| 1 | 15112/15112 | 52.4s | Clean (after the warp-point hash test fix in Phase 3) |
| 2 | 15111/15112 | 49.6s | `test_warp_distance_scaling` flaked under one shard layout; passes in isolation |
| 3 | 15112/15112 | 47.4s | Clean |

**Verdict:** Run #2's failure is a pre-existing order-dependent flake (same character as `test_path_projection.py::test_project_chained_orders` flake observed on Python 3.10 earlier this session). Not a 3.13 regression.

## Items to monitor going forward

- **Order-dependent test flakes** — at least 2 known: `test_path_projection.py::test_project_chained_orders`, `test_warp_distance_scaling`. Consider a separate cleanup project to identify the test pollution source. Out of scope for PROJ-295.
- **`audioop-lts` maintenance status** — community-maintained. If it stops being updated, switch to a 3-line numpy-based RMS computation in `Tools/qa_observer/` and drop the dependency. Low urgency.
- **Future Python upgrades (3.14, 3.15)** — pyproject.toml's `requires-python = ">=3.13"` means newer Pythons will work without changes; this project's plan can be adapted as a template.
- **`google-cloud-speech` deprecation cycles** — the original PROJ-295 trigger. Now silent on 3.13. Watch for the next "support dropping" warning in 2-3 years and treat as a similar minor upgrade.

## Performance note

Wall time dropped from 76s (Python 3.10) to ~50s (Python 3.13), a **31% reduction**. This is real — Python 3.11+ included substantial interpreter perf work. Free win.

## No regressions detected

- Game launcher imports: clean
- QA observer voice loop: clean
- 15K-test suite: clean modulo flakes documented above
- No new warnings/deprecations from any dependency
- No `FutureWarning` from google libs (the original trigger)
