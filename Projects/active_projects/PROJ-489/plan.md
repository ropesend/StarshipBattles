# PROJ-489: Legacy removal — ModifierService consolidation (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-489` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-489 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Consolidate to `ModifierService` canonical | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** All phases complete
**Last Action:** Phase 2 (audit remediation — doc drift) complete. Updated `docs/04_SERVICES.md` `ModifierLogicService` section to reflect post-PROJ-489 thin-facade reality; updated `docs/guides/modifier_system.md` (lines 98, 285) and `docs/guides/adding_modifiers.md` (lines 128, 162) so `ModifierManager.add_modifier()` is described as enforcing `allow_types`, `deny_types`, AND `allow_abilities` via delegation to `ModifierService`. All three docs' "Last verified" timestamps bumped to 2026-05-23.
**Note:** DI-2026-05-23-004 logged for pre-existing `efficient_engines` data bug surfaced by audit (out of scope).
**Next Action:** None — awaiting user confirmation / commit.
**Blockers:** None.

## Overview
The audit's cross-system analysis identified triplicate modifier-allowed-checking logic across three classes (plus a fourth inline implementation in `ModifierManager.add_modifier`). The simulation-layer `ModifierService` (`game/simulation/services/modifier_service.py:16`) is the canonical home; the UI-layer `ModifierLogicService` and `ComponentService.is_modifier_allowed` re-implement 80%+ of its surface. `ModifierManager.add_modifier` (lines 108-117) has a fourth inline restriction check.

Consolidate: have `ComponentService` and `ModifierManager` delegate to `ModifierService`. Keep `ModifierLogicService` as a UI facade but delegate to `ModifierService` instead of duplicating logic. Keep `calculate_snap_value` in `ModifierLogicService` (UI-only concern with no simulation equivalent).

## Goals
- Make `ModifierService` the single source of truth for `is_modifier_allowed`, `get_mandatory_modifiers`, `is_modifier_mandatory`, `get_initial_value`, `ensure_mandatory_modifiers`, `get_local_min_max`.
- Have `ComponentService.is_modifier_allowed` and `ModifierManager.add_modifier`'s inline check delegate to `ModifierService`.
- Have `ModifierLogicService` delegate to `ModifierService` instead of `ComponentService` for shared methods; retain `calculate_snap_value` locally.
- Reconcile the `_has_arc_set_effect` vs hardcoded `turret_mount` divergence: the generic `_has_arc_set_effect` approach (already in `ModifierService`) is preferred.

## Scope
**In:**
- `game/simulation/services/modifier_service.py` — canonical, additive changes only (no API breaks).
- `game/ui/screens/builder/modifier_logic.py` — refactor `ModifierLogicService` to delegate to `ModifierService`.
- `game/ui/services/component_service.py` — refactor `ComponentService.is_modifier_allowed` to delegate.
- `game/simulation/components/modifier_manager.py` — inline restriction check at lines 108-117 → delegate to `ModifierService.is_modifier_allowed`.
- UI imports: `workshop_screen.py`, `builder/detail_panel.py`, `builder/modifier_row.py`, `panels/builder_widgets.py` — re-point to receive a `ModifierService` instance instead of constructing a `ModifierLogicService`.

**Out:**
- `calculate_snap_value` (UI-only) stays in `ModifierLogicService`.
- All non-modifier-validation methods on these classes are unaffected.
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).
- Other legacy-audit clusters: see siblings PROJ-484, PROJ-485, PROJ-486, PROJ-487, PROJ-488, PROJ-490.

## Key Files
| Component | File Path |
|-----------|-----------|
| `ModifierService` (canonical) | `game/simulation/services/modifier_service.py` |
| `ModifierLogicService` [EDIT] | `game/ui/screens/builder/modifier_logic.py` |
| `ComponentService` [EDIT] | `game/ui/services/component_service.py` |
| `ModifierManager` [EDIT] | `game/simulation/components/modifier_manager.py` |
| UI callers [EDIT] | `game/ui/screens/workshop_screen.py`, `game/ui/screens/builder/detail_panel.py`, `game/ui/screens/builder/modifier_row.py`, `game/ui/panels/builder_widgets.py` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/verification_report.md](findings/verification_report.md)
- [findings/source_audit.md](findings/source_audit.md)
- [findings/bundling_decisions.md](findings/bundling_decisions.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
