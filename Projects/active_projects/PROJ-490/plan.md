# PROJ-490: Legacy removal — stale-comment cleanup sweep (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-490` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-490 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Remove / tighten 9 stale comments | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phase 1
**Last Action:** Project created from `Reviews/results/2026-05-20_210635_legacy-audit/` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
The 2026-05-20 legacy audit surfaced 9 stale or misleading comments scattered across `ship_instance.py`, `ship_instance_serializer.py`, `strategy_detail_fmt.py`, `mine_group_service.py`, `ship_stat_querier.py`, `build_context.py`, and `design_metadata.py`. Each is either an orphan reference to a deleted property, a leftover TODO without a removal plan, or a stale historical reference to an archived PROJ. The verifier confirmed each comment is factually stale today.

## Goals
- Remove or update each stale comment so the code's narrative reflects today's reality.
- Where a fallback path stays (e.g. `mine_group_service.py`), add a dated TODO + PROJ reference rather than removing.

## Scope
**In:** the 9 comment locations identified by the audit's verifier.
**Out:**
- The underlying code being commented on — no behavioral changes.
- The serializer comment at `ship_instance_serializer.py:62` may be kept (verifier: "acceptable to keep as-is") — treat as optional.
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).
- Other legacy-audit clusters: see siblings PROJ-484, PROJ-485, PROJ-486, PROJ-487, PROJ-488, PROJ-489.

## Key Files
| Component | File Path |
|-----------|-----------|
| `carried_items` stale comments [EDIT] | `game/strategy/data/ship_instance.py` |
| `carried_items` serializer comment [EDIT (optional)] | `game/strategy/data/ship_instance_serializer.py` |
| "legacy projection" comment [EDIT] | `game/ui/screens/strategy_detail_fmt.py` |
| "legacy test stub" comment [EDIT] | `game/strategy/services/mine_group_service.py` |
| PROJ-225 comment [EDIT] | `game/simulation/entities/ship_stat_querier.py` |
| PROJ-67 module docstring [EDIT] | `game/strategy/data/build_context.py` |
| PROJ-218 comment [EDIT] | `game/strategy/data/design_metadata.py` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/verification_report.md](findings/verification_report.md)
- [findings/source_audit.md](findings/source_audit.md)
- [findings/bundling_decisions.md](findings/bundling_decisions.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (no behavioral risk — pure comment edits)
- [ ] Audit passed
- [ ] User verified
