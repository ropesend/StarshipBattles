# PROJ-319: Audit-shrink cleanup 2026-05-02

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-319` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-319 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dead imports / params / unreachable code | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Dead functions | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 4. Duplication consolidation | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

(Phase 3 — dead classes / dead files — skipped: zero verified items in source audit.)

## Current State
**Last Updated:** 2026-05-02
**Active Phase:** Phase 1 (not started)
**Last Action:** Project created from `Reviews/results/2026-05-02_184210_audit_shrink/` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Cleanup project derived from the 2026-05-02 audit-shrink review at
`Reviews/results/2026-05-02_184210_audit_shrink/`. After an independent
skeptical re-verification of every audit-flagged "verified safe" candidate,
**30 items survived** (16 dead-code items + 14 duplication-consolidation
items). The audit's claimed reclaimable LOC for these items is **~733 LOC**
(19 LOC Tier 4 + 57 LOC dead functions + 657 LOC duplication consolidation).

## Goals
- Remove 14 dead imports / unused parameters / unreachable code (~19 LOC).
- Remove 2 dead helper functions (~57 LOC).
- Consolidate 14 verified duplication clusters (~657 LOC reclaimable, with
  several CRITICAL items where silent drift would corrupt gameplay state).

## Scope
**In:**
- Tier 4 dead imports / parameters / unreachable code from Section 3.
- Dead functions from Section 3 Tier 3.
- Section 4 CRITICAL and MAJOR duplications with concrete consolidation
  targets (DUP-X-01 through DUP-X-14).

**Out:**
- Anything the audit tagged `PRODUCT_DECISION`, `UNCERTAIN`, or
  `false_positive` (see [findings/verification_report.md](findings/verification_report.md)
  and the audit's Section 3b).
- Complexity hotspots from the source audit (Section 5).
- MINOR / INFO duplications (DUP-X-15 onwards).

## Key Files
| Component | File Path |
|-----------|-----------|
| Race resolver (NEW) | `game/strategy/services/race_resolver.py` |
| Range slider widget (NEW) | `game/ui/widgets/range_slider_builder.py` |
| Spatial formation utils (NEW) | `game/ai/spatial_behaviors/_formation_utils.py` |
| Happiness engine | `game/strategy/engine/happiness_engine.py` |
| Population engine | `game/strategy/engine/population_engine.py` |
| Galaxy system generator | `game/strategy/data/galaxy_system_generator.py` |
| Superweapon validator | `game/strategy/validation/superweapon_validator.py` |
| Planet/Star list windows | `game/ui/screens/{planet,star}_list_window.py` |
| Battle runner | `game/simulation/battle_runner.py` |
| Strategy detail formatter | `game/ui/screens/strategy_detail_fmt.py` |

## Related Documents
- [design.md](design.md) — Architecture analysis and design rationale
- [decisions.md](decisions.md) — Full decisions log
- [findings/source_audit.md](findings/source_audit.md) — Pointer to source audit
- [findings/verification_report.md](findings/verification_report.md) — Independent verification record
- [manifest.md](manifest.md) — File-by-file action manifest

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
