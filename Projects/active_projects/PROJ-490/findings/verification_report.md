# PROJ-490: Verification Report

**Source audit:** `Reviews/results/2026-05-20_210635_legacy-audit/`
**Run date:** 2026-05-22
**Bundle counts:** 9 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (this bundle)
**Run-wide totals across all 7 sibling projects:** 17 verified / 3 rejected / 0 uncertain / 0 INFO / 12 out-of-scope (audit-self-retracted)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy |
|----|------|--------|----------|------------|----------------|----------|--------|
| LEG-01-002 | `game/strategy/data/ship_instance.py:170` | `# legacy carried_items: List[Dict[str, Any]] mixed-shape list.` | n/a (delete or rewrite past tense) | n/a (comment) | remove orphan marker | MINOR | none |
| LEG-01-003 | `game/strategy/data/ship_instance.py:180` | `# legacy dict-list shape — see carried_items property.` | n/a | n/a | remove orphan marker | MINOR | none |
| LEG-01-004 | `game/strategy/data/ship_instance_serializer.py:62` | `# legacy carried_items dict-list shape is no longer the` | n/a (keep but date) | n/a | tighten wording | MINOR | none |
| LEG-02-002 | `game/strategy/services/mine_group_service.py:130` | `# legacy test stub that still uses fleets.` | n/a (add dated TODO or migrate stubs) | n/a | add dated TODO or migrate | MINOR | none |
| LEG-02-009 | `game/simulation/entities/ship_stat_querier.py:144-145` | `# PROJ-225: Removed redundant cached_summary property (DUP-SIM-007). # Use Ship.cached_summary instead.` | PROJ-225 archived (deep_archive) | n/a | remove orphan marker | MINOR | none |
| LEG-02-010 | `game/strategy/data/build_context.py:1-4` | module docstring referencing PROJ-67 | PROJ-67 archived (deep_archive, 2026-02-10) | n/a | remove orphan marker | MINOR | none |
| LEG-02-011 | `game/strategy/data/design_metadata.py:253-254` | `PROJ-218: Fixed field name from 'cost' to 'resource_cost' for consistency.` | PROJ-218 archived (deep_archive, 2026-03-14) | n/a | remove orphan marker | MINOR | none |
| D-01 | `game/ui/screens/strategy_detail_fmt.py:564` | `# legacy projection).` | n/a (delete; misleading) | n/a | remove orphan marker | MINOR | none |
| A-05 | `game/strategy/data/ship_instance.py:170-180, 549-552` | doc comments implying `carried_items` property exists | property deleted in PROJ-436 Phase 9 | n/a | remove orphan markers | MINOR | none |

## Rejected

(None in this bundle.)

## Uncertain (resolved)

(None.)

## INFO (resolved)

(None.)

## Out of Scope

(None directly tied to this cluster.)

## Notes

- All 9 items are documentation-quality only — zero behavioral risk.
- A-05 and LEG-01-002/003 overlap on `ship_instance.py:170-180`; address them together in Task 1.1.
- LEG-01-004 has a softer recommendation ("keep or date") — treat as optional cleanup.
