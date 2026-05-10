# PROJ-387: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 1 verified, 0 uncertain, 0 INFO, 0 deferred
- **Project siblings:** PROJ-383..PROJ-386, PROJ-388..PROJ-393

## Cluster Identity

**Removal cluster:** Galaxy backward-compat property forwarders. Five underscore-prefixed forwarders on `Galaxy` proxy to internal `GalaxyState` attributes. The docstring explicitly tags them "backwards-compat under-prefixed forwarders" with a known migration plan ("Phase 3-cleanup work will migrate those to public accessors").

## Severity Breakdown

| Severity | Count |
|----------|-------|
| MAJOR | 1 (LEG-03-022) |

## Risk Notes

- The 5 forwarders are properties, not methods — readers do `galaxy._global_hex_X`, not `galaxy._global_hex_X()`. The migration is a reference rewrite, not a call rewrite.
- Underscored names suggest private-but-exported, which is the smell the audit flags. After migration, all access goes through public `GalaxyState` accessors.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
