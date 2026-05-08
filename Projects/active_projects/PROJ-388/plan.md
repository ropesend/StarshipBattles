# PROJ-388: Legacy removal — ModifierLogic deprecated class wrapper (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-388` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-388 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate consumer + delete ModifierLogic class | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220621_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Removes the entire `ModifierLogic` class at `game/ui/screens/builder/modifier_logic.py:177` — a deprecated static-method wrapper around `ModifierLogicService`. Class exists solely so callers can import `ModifierLogic` without constructor injection. The audit explicitly cites this as "Rule 3 territory — no compatibility shims." Includes 1 INFO sub-finding (LEG-03-015 `calculate_snap_value`) which disappears with the class.

## Goals
- Migrate `ModifierEditorPanel._build_panels` (and any other consumer found via grep) to use `ModifierLogicService` with constructor injection.
- Delete the `ModifierLogic` class.
- Note: a separate audit-flagged architectural decision about `ModifierService` vs `ModifierLogicService` (cross-system Pair 4) is **out of scope** here — see [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Scope
**In:** LEG-03-009 (the deprecated `ModifierLogic` class), LEG-03-015 (`calculate_snap_value` static — disappears with the class).
**Out:** Other clusters from the same audit (siblings PROJ-383..PROJ-387, PROJ-389..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md). Cross-system Pair 4 (ModifierService vs ModifierLogicService consolidation) is excluded — needs separate architectural decision.

## Key Files
| Component | File Path |
|-----------|-----------|
| Production target `[DELETE class]` | `game/ui/screens/builder/modifier_logic.py` |
| Consumer to migrate | `game/ui/panels/modifier_editor_panel.py` (or wherever `ModifierEditorPanel._build_panels` lives) |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No remaining imports of `ModifierLogic` (the class) anywhere (`grep -rn "from game.ui.screens.builder.modifier_logic import ModifierLogic" .`)
- [ ] User verified
