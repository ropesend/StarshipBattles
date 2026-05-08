# PROJ-384: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 2 verified, 0 uncertain, 0 INFO, 0 deferred
- **Project siblings:** PROJ-383, PROJ-385, PROJ-386, PROJ-387, PROJ-388, PROJ-389, PROJ-390, PROJ-391, PROJ-392, PROJ-393

## Cluster Identity

**Removal cluster:** PROJ-241 deprecated `*_static` methods. After PROJ-241 migrated `AbilityManager` and `ModifierManager` to instance APIs, twelve `@staticmethod` shims were left in place "for transition" but never removed. All 12 are explicitly marked `DEPRECATED` in code with `NOQA: legacy-retained` annotations.

## Severity Breakdown

| Severity | Count |
|----------|-------|
| CRITICAL | 2 (LEG-01-003, LEG-01-004) |

## Quick Wins

Both items are zero-call-site deletions (LEG-01-003: 0 prod, 3 test; LEG-01-004: 0 external, 1 self-internal). Combined 166 LOC ships as a single PR — the largest single-PR deletion in this audit.

## Risk Notes

- `remove_modifier_inplace` (in LEG-01-004's set) has 1 internal call site inside `add_modifier_static` itself. Since both are deleted together, the internal reference is fine.
- The 3 test methods in `test_ability_manager.py` need to be re-pointed at the instance API in the same change — leaving test calls behind will fail import.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
