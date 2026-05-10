# PROJ-393: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 11 verified, 3 uncertain (resolved — included), 2 INFO (resolved — included), 0 deferred
- **Project siblings:** PROJ-383..PROJ-392

## Cluster Identity

**Removal cluster:** Test-injection fallbacks + comment cleanups + scattered legacy paths. Catch-all bundle for legacy items that don't belong to any other cluster but together represent ~16 small cleanups across 18 files. Phases ordered by removal-risk:

- **Phase 1** — comment-only deletions and stale doc tags (zero logic change)
- **Phase 2** — production fallback branches that exist for tests that don't inject deps (require test audit before production deletion)
- **Phase 3** — backward-compat fields, hardcoded fallbacks, module-level side effects, and items previously tracked under archived projects

## Severity Breakdown

| Severity | Count | Phase |
|----------|-------|-------|
| MINOR (comment-only) | 2 verified + 2 INFO | Phase 1 |
| MAJOR (test-injection fallbacks) | 4 verified + 1 (LEG-02-002 IScene migration) | Phase 2 |
| MAJOR (backward-compat / misc) | 4 verified + 2 UNCERTAIN-included + 1 UNCERTAIN-included with asset scan | Phase 3 |

## Risk Notes

- **Phase 2's test-audit step is mandatory.** Each test-injection fallback has the shape "production fallback exists because some tests don't inject the dep." Deleting the fallback before all tests inject will break the test run. Audit first, then delete.
- **Phase 3 Task 3.5 (Combat Lab vars):** UNCERTAIN-included on the basis that PROJ-270 is archived and there is no live PROJ-270 Phase 10 follow-up. Verify before deleting — if a Combat Lab refactor is mid-flight, defer.
- **Phase 3 Task 3.6 (`_LEGACY_PATTERN`):** UNCERTAIN-included with an asset scan as the first step. If scan finds legacy-format filenames, the regex is still load-bearing and the task pauses for user input.
- **Phase 3 Task 3.3 (`view=None`):** UNCERTAIN-included; uncolonized-planet path was a real use case so audit needs to find every caller before deleting the legacy branch.
- LEG-02-001 (`Game.running` test backdoor) was UNCERTAIN-excluded by the user — kept until tests stop bypassing `Game.__init__`. Recorded in shared bundling_decisions.md.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
