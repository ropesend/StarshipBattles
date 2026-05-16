# PROJ-386: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 4 verified, 0 uncertain, 0 INFO, 0 deferred
- **Project siblings:** PROJ-383, PROJ-384, PROJ-385, PROJ-387..PROJ-393

## Cluster Identity

**Removal cluster:** save-format migration code. Four distinct legacy-format compatibility blocks across 4 files, each gating on a shape check (missing `phase` key, presence of `_complex_toggles`, presence of `side_0`/`side_1`, etc.). The audit's deterministic save-migration scanner missed all 4 because they don't use the literal word "migration" in their logic — only in their comments. Sonnet's third-pass verification confirmed each block is reachable during normal save loading.

## Severity Breakdown

| Severity | Count |
|----------|-------|
| MAJOR | 3 (LEG-03-008, LEG-04-005, LEG-03-017) |
| MINOR | 1 (LEG-03-018) |

## Policy Notes

CLAUDE.md Rule 3 ("Root Cause Fixes") states: *"Do not add compatibility shims, fallback systems, monkey patches, duplicate logic, or save-file migrations. Old saves are disposable. When a system is replaced, remove the old path and update all callers."* All 4 findings in this bundle violate this rule directly. They are non-negotiable deletions: do not preserve them with fallback comments, version-gates, or "transitional" annotations. The implementer must delete the legacy-format handling outright. Old saves that fail to load after this change are by design.

## Risk Notes

- LEG-03-018 (`ship_instance_serializer`) is the only one whose own code-comments cite the disposable-saves policy yet keep the compat paths anyway — the implementer should treat the existing comments as a confession, not a justification.
- Tests that feed legacy save fixtures into these deserializers will fail. Per Rule 3, those tests are also legacy and should be deleted, not adapted.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
