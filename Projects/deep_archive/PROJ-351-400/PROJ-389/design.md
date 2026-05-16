# PROJ-389: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 1 verified, 0 uncertain, 0 INFO, 0 deferred
- **Project siblings:** PROJ-383..PROJ-388, PROJ-390..PROJ-393

## Cluster Identity

**Removal cluster:** `score_planet_for_race` wrapper. 1-line module-level wrapper delegating to `calculate_habitability` in the same module. Kept "for source-stability of existing callers." Audit confirmed 6 production call sites and a dual re-export from `formulas/__init__.py`.

## Severity Breakdown

| Severity | Count |
|----------|-------|
| MAJOR | 1 (LEG-02-009) |

## Risk Notes

- Both functions live in the same module so callers can be migrated by import-rewrite + name-rewrite without changing import paths.
- The dual re-export from `formulas/__init__.py:9` must be updated in the same change — leaving the public re-export listing both names defeats the cleanup.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
