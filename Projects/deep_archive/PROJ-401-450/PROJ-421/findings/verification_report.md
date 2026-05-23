# PROJ-421 — Verification Report

Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`
Run date: 2026-05-13

Batch summary (across all 9 sibling projects):
15 verified / 0 rejected / 1 uncertain (resolved → included in PROJ-421) / 7 INFO (resolved → all excluded) / 0 out-of-scope, out of 21 candidates total.

## Verified (this bundle)

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy violation |
|----|------|--------|----------|-----------:|----------------|----------|------------------|
| LEG-02-001 | `game/ui/screens/strategy_event_router.py` | `_handle_window_close slot-nulling lines (7 nulls across 9 windows)` | `Pattern #31 auto-deregistration via StrategyModalWindow.kill() (already live)` | 0 (no reader checks `event_router.<slot> is None` per verifier) | delete | MAJOR | — |

## Rejected

None. Zero items in this bundle were rejected.
_(Note: the audit's own verifier already flagged LEG-02-001's classification as "PARTIALLY ACCURATE — FATAL ANALYSIS ERROR" before this third-pass run. That item is in PROJ-421's UNCERTAIN section below.)_

## Uncertain (resolved)

| ID         | Question                                                                                                                                          | Decision           |
|------------|---------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| LEG-02-001 | Audit's "8 non-modal slots" claim fabricated — verifier confirmed all 9 are StrategyModalWindow subclasses. Remove slot-nulls as redundant?      | Include — frame as "remove redundant slot-nulls" |

The audit's verifier had already flagged this finding's classification as **PARTIALLY ACCURATE — FATAL ANALYSIS ERROR**. The third-pass verifier corroborated and added the no-slot-readers check. User chose to keep the finding under a reframed objective rather than drop it outright.

## INFO (resolved)

| ID         | Verifier note                                                                                              | Decision |
|------------|------------------------------------------------------------------------------------------------------------|----------|
| MIN-03-007 | Provider-registration side-effect import; intentional Pattern #4 (Registry).                               | Exclude  |
| LEG-01-002 | UI rendering label, not deprecation marker.                                                                | Exclude  |
| LEG-01-004 | Documented test-patch surface (Pattern #5).                                                                | Exclude  |
| LEG-01-005 | Canonical public-accessor-over-private-index pattern.                                                      | Exclude  |
| LEG-01-006 | ModifierManager vs ModifierService — zero behavioural overlap.                                             | Exclude  |
| MIN-03-003 | Idiomatic factory method on definition class.                                                              | Exclude  |
| MIN-004    | Documented Pattern #5 Facade/Delegate intentional delegation.                                              | Exclude  |

All 7 INFO items were excluded. Excluded INFO items are flagged in refinement feedback as a signal of over-eager INFO classification by the source skill.

## Out of Scope

None.
