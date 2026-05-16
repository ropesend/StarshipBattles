# PROJ-388: Design Document

## Source Audit

This project was created from the legacy-audit at `Reviews/results/2026-05-07_220621_legacy-audit/`.

- **Audit verified:** 32 items overall (across 11 sibling projects)
- **This bundle:** 1 verified, 0 uncertain, 1 INFO (resolved — included), 0 deferred
- **Project siblings:** PROJ-383..PROJ-387, PROJ-389..PROJ-393

## Cluster Identity

**Removal cluster:** `ModifierLogic` deprecated class wrapper. The entire class is a static-method wrapper around `ModifierLogicService`. Audit's quote: *"This is explicit Rule 3 territory — 'No compatibility shims.'"* The class header at `modifier_logic.py:177` carries `# Deprecated: ModifierLogic static wrapper`.

The INFO finding LEG-03-015 (`calculate_snap_value`) is one of the static methods on this class — naturally swept up by the same deletion.

## Severity Breakdown

| Severity | Count |
|----------|-------|
| MAJOR | 1 (LEG-03-009) |
| INFO | 1 (LEG-03-015 — disappears with the class) |

## Out-of-Scope Note: Cross-System Pair 4

The audit's cross-system report flagged a deeper question — `ModifierService` (sim layer) vs `ModifierLogicService` (UI layer) overlap with subtle behavioral divergence in `_get_base_firing_arc` and `arc_set` detection. The user excluded that consolidation from this run during Phase D Step 4: it requires an architectural decision and a separate project. This project only removes the static wrapper class, not the service-layer consolidation question.

## Risk Notes

- The static wrapper exists specifically so callers can use `ModifierLogic.foo()` without constructing `ModifierLogicService`. Migrating every caller to constructor injection is the standard fix.
- If the consumer count is larger than the audit reports (1 prod + 1 test), Task 1.1's grep will surface them — do not skip the enumeration step.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
