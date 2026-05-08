# PROJ-384: Legacy removal — PROJ-241 deprecated *_static methods (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-384` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-384 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete deprecated `*_static` methods | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220621_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Deletes 12 deprecated `@staticmethod` methods (166 LOC total) on `AbilityManager` and `ModifierManager` left over from the PROJ-241 instance-API migration. Verified zero production callers; only 3 test methods + 1 internal self-reference remain. Quick-win deletion: ships in a single PR.

## Goals
- Delete 6 `*_static` methods on `AbilityManager` (lines 286-341, 56 LOC).
- Delete 6 `*_static` methods on `ModifierManager` (lines 221-330, 110 LOC).
- Migrate 3 test methods in `test_ability_manager.py` to the instance API.

## Scope
**In:** LEG-01-003 (`AbilityManager.*_static`), LEG-01-004 (`ModifierManager.*_static`).
**Out:** Other clusters from the same audit (siblings PROJ-383, PROJ-385..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| Production target | `game/simulation/components/ability_manager.py` |
| Production target | `game/simulation/components/modifier_manager.py` |
| Test migration | `tests/.../test_ability_manager.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] No remaining references to any of the 12 deleted method names (`grep -rn "_static\b" game/simulation/components/{ability,modifier}_manager.py`)
- [ ] User verified
