# PROJ-391: Legacy removal — Underscore-prefixed legacy pair consolidations (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-391` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-391 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Three small consolidations | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220621_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Three small consolidations: replace local `_get_harvester_info` and `_iter_components` helpers with their canonical equivalents, and move duplicated `_formation_to_dict`/`_formation_from_dict` into `FormationSpec` itself. All three are MINOR-severity, single-call-site or low-call-site cleanups discovered by the audit's name-pair-drift detector and cross-system review.

## Goals
- Replace 1 call site of `_get_harvester_info` with canonical `get_harvester_info`, delete the local function (LEG-04-007).
- Replace 1 call site of `_iter_components` with canonical `iter_components`, plus secondary cleanup of manual layer iteration in `planet_economy_projector.py:220-231`; delete the local `_iter_components` (LEG-01-011 / LEG-04-008).
- Move `_formation_to_dict`/`_formation_from_dict` serialization onto `FormationSpec` (or a shared utility), delete the duplicates in `task_force.py` and `replay_serialization.py` (LEG-01-017 — UNCERTAIN, user opted in during Phase D Step 3 with the Pattern-17 (`Serializable Protocol`) shape).

## Scope
**In:** LEG-04-007, LEG-01-011 / LEG-04-008 (dedup'd as one cluster), LEG-01-017 (UNCERTAIN — user-included).
**Out:** Other clusters from the same audit (siblings PROJ-383..PROJ-390, PROJ-392, PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md). The audit's INTENTIONAL-SPLIT pairs (`ModifierManager`/`ModifierService`, etc.) are excluded by the audit's own cross-system verifier.

## Key Files
| Component | File Path |
|-----------|-----------|
| Harvester legacy | `game/strategy/services/planet_economy_projector.py` |
| Harvester canonical | `game/strategy/engine/harvesting_engine.py` |
| Iter legacy | `game/ui/screens/battle_setup/spec_compiler.py` |
| Iter canonical | `game/core/patterns/layer_iterator.py` |
| Formation serialize (dup) | `game/strategy/data/task_force.py` |
| Formation serialize (dup) | `game/simulation/replay/replay_serialization.py` |
| Formation owner | `game/simulation/combat/formation.py` (`FormationSpec`) |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No remaining references to `_get_harvester_info`, `_iter_components`, or the duplicated `_formation_to_dict/_formation_from_dict` helpers (`grep -rn -E "_get_harvester_info|_iter_components|_formation_(to|from)_dict" .`)
- [ ] User verified
