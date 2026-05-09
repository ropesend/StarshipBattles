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
| 1. Delete deprecated `*_static` methods | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1 (Complete — code-side)
**Last Action:** All 12 deprecated `*_static` methods deleted from `ability_manager.py` (-57 LOC) and `modifier_manager.py` (-109 LOC, including unused `GameRegistries` TYPE_CHECKING import); 3 test methods in `test_ability_manager.py` migrated to instance API. Focused regression: `pytest tests/ -k "ability_manager or modifier_manager"` → 63 passed. Stale comment block in `test_modifier_manager.py` updated to attribute removal to PROJ-384.
**Next Action:** **Commit blocked** — working tree contains 6 unresolved merge-conflicted files unrelated to PROJ-384 (`Tracking/bugs/active/BUG-124.md`, `Tracking/debug_plan.md`, `Tracking/feature_plan.md`, `Tracking/features/active/FEAT-27.md`, `Tracking/features/active/FEAT-28.md`, `docs/systems/strategy_layer.md`). Per CLAUDE.md "don't revert unrelated user changes," these need user resolution before any commit can proceed. PROJ-384 staged changes are ready (`git status --short` shows `M` on both target files + plan.md + checklist).
**Blockers:** Pre-existing unresolved merge in working tree blocks `git commit`.

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
