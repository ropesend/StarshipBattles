# PROJ-489: Verification Report

**Source audit:** `Reviews/results/2026-05-20_210635_legacy-audit/`
**Run date:** 2026-05-22
**Bundle counts:** 1 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (this bundle)
**Run-wide totals across all 7 sibling projects:** 17 verified / 3 rejected / 0 uncertain / 0 INFO / 12 out-of-scope (audit-self-retracted)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy |
|----|------|--------|----------|------------|----------------|----------|--------|
| LEG-F-1 | `game/ui/screens/builder/modifier_logic.py:34`, `game/ui/services/component_service.py:22`, `game/simulation/components/modifier_manager.py:108-117` | `ModifierLogicService`, `ComponentService.is_modifier_allowed`, `ModifierManager.add_modifier` inline check | `ModifierService` at `game/simulation/services/modifier_service.py:16` | 4 UI files use `ModifierLogicService` (1 production + 6 test) + 16 files reference `ComponentService` + inline in `ModifierManager` | consolidate_with | MAJOR | none |

## Rejected

(None in this bundle.)

## Uncertain (resolved)

(None.)

## INFO (resolved)

(None.)

## Out of Scope

- **LEG-F-2** (WorkshopDataLoader vs RegistryLoader): REJECTED at the run-wide level. The verifier found the audit's framing inverted — `reload_registries_from_directory` is test-only infrastructure (0 production callers), not the canonical from which `WorkshopDataLoader.load_all` was extracted. They are not duplicates; they serve different architectural needs (test utility vs production UI loader). Recorded in run-wide REJECTED list in `bundling_decisions.md`.

## Notes

- Behavioral reconciliation between `_has_arc_set_effect` (generic) and hardcoded `turret_mount` is the critical pre-step. If they differ, consolidation must preserve the generic approach (covers future arc_set modifiers).
- `ModifierManager.add_modifier`'s missing `allow_abilities` check is technically a bug fix bundled with the consolidation. Test suite results during implementation will reveal whether any existing tests inadvertently depended on the buggy behavior.
