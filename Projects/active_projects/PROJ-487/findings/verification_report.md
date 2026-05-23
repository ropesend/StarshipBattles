# PROJ-487: Verification Report

**Source audit:** `Reviews/results/2026-05-20_210635_legacy-audit/`
**Run date:** 2026-05-22
**Bundle counts:** 1 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (this bundle)
**Run-wide totals across all 7 sibling projects:** 17 verified / 3 rejected / 0 uncertain / 0 INFO / 12 out-of-scope (audit-self-retracted)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy |
|----|------|--------|----------|------------|----------------|----------|--------|
| LEG-04-MAJOR | `game/strategy/data/planetary_facility.py:209-221` | `get_fuel_storage`, `get_max_fuel_storage`, `add_fuel`, `withdraw_fuel` (4 wrappers in one finding) | generic `*_consumable` API on `PlanetaryFacility` | 3 production (resupply_engine.py:135, 208, 293) + 56 test | migrate_callers_then_delete | MAJOR | none |

## Rejected

(None in this bundle.)

## Uncertain (resolved)

(None.)

## INFO (resolved)

(None.)

## Out of Scope

(None directly tied to this cluster.)

## Notes

- The audit marked this MAJOR rather than CRITICAL because the wrappers are in active production use. Removal requires caller migration.
- F-A-012 in the deprecation marker is an internal ticket reference with no linked project or removal timeline — this project is the removal plan.
