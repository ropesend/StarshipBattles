# PROJ-392: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 9 verified, 1 uncertain (resolved — included), 2 INFO (resolved — included), 0 deferred
- **Project siblings:** PROJ-383..PROJ-391, PROJ-393

## Cluster Identity

**Removal cluster:** Misc orphan wrappers + zero-call-site placeholders. Twelve small legacy artifacts that don't belong to any larger system being eradicated but together represent ~12 small cleanups. Phase 1 is a Critical-severity quick-win deletion (3 zero-callsite items). Phase 2 contains 9 inline-and-delete or rename tasks at MAJOR severity.

## Severity Breakdown

| Severity | Count | Phase |
|----------|-------|-------|
| MINOR (zero-callsite quick deletions) | 3 (LEG-01-001, LEG-02-007, LEG-03-025) | Phase 1 |
| MAJOR (inline-and-delete + small migrations) | 6 (LEG-01-006, LEG-01-007, LEG-01-009, LEG-01-010, LEG-04-006) plus UNCERTAIN-included LEG-02-015 | Phase 2 |
| MINOR (small inline) | 1 (LEG-03-014) | Phase 2 |
| INFO (included by user) | 2 (LEG-03-010, LEG-03-016) | Phase 2 |

## Quick Wins

Phase 1 collects 3 deletions with literally zero call sites — single PR, no migration, no test updates needed beyond the file edits themselves. (The audit's 0-callsite count was confirmed by Sonnet's third-pass verification.)

## Risk Notes

- Phase 2 tasks are independent of each other — no ordering required. They can be done in any order or in parallel.
- LEG-02-015 was UNCERTAIN — user opted to rename to public `menu_scene` rather than keep the misleading underscore prefix.
- LEG-03-010 and LEG-03-016 are INFO-bucket — user opted them in because they are mechanical find-and-replace cleanups with zero behavioral change.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
