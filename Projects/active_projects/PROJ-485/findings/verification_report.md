# PROJ-485: Verification Report

**Source audit:** `Reviews/results/2026-05-20_210635_legacy-audit/`
**Run date:** 2026-05-22
**Bundle counts:** 3 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (this bundle)
**Run-wide totals across all 7 sibling projects:** 17 verified / 3 rejected / 0 uncertain / 0 INFO / 12 out-of-scope (audit-self-retracted)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy |
|----|------|--------|----------|------------|----------------|----------|--------|
| LEG-02-001 | `game/ai/carrier_controller.py:358-390` | `_find_tactical_launch_ability` | `_sum_launch_rate` | 0 production | delete | MAJOR | none |
| LEG-02-005 | `game/ai/carrier_controller.py:255-263` | `_pop_fighter_cvs` | `_pop_cvs_within_budget` | 0 production | delete | MAJOR | none |
| LEG-02-006 | `game/ai/carrier_controller.py:265-300` | `_pop_cvs` | `_pop_cvs_within_budget` | 0 production (only `_pop_fighter_cvs` calls it; transitively dead) | delete | MAJOR | none |

## Rejected

(None in this bundle.)

## Uncertain (resolved)

(None.)

## INFO (resolved)

(None — no INFO items in this cluster.)

## Out of Scope

(None directly tied to this cluster.)

## Notes

- All three deletions ship as one PR. Production grep across `game/` confirmed zero call sites; test callers exist and must be migrated to `_sum_launch_rate` / `_pop_cvs_within_budget` in the same PR.
- The audit's Quick Wins section explicitly calls out this cluster as a quick deletion (Rank 3, ~83 LOC).
