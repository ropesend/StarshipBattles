# PROJ-375: Audit-shrink cleanup 2026-05-05

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-375` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-375 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dead method removal | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy-layer duplication consolidation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI-layer duplication consolidation | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-05
**Active Phase:** Phase 1 of 3
**Last Action:** Project created from `2026-05-05_185819_audit_shrink` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
This project acts on the verified-safe findings from the shrink-audit at
`Reviews/results/2026-05-05_185819_audit_shrink/` after a fresh independent
re-verification (see [findings/verification_report.md](findings/verification_report.md)).
The audit identified 1 dead method (3 LOC) and 12 CRITICAL/MAJOR duplication
clusters totalling roughly 460 reclaimable LOC; **10 of those items survived
re-verification** and are scoped into this project. Two were excluded:
DUP-X-08 (cross-domain factory base — architectural cost outweighs the
~30 LOC saving) and DEEP-01-004 (`_validate_tick_inputs` boilerplate across
4 engines — verified but the audit and verifier both rate it as
not-worth-the-churn structural duplication).

## Goals
- Phase 1: Remove the 1 verified dead method (`_find_shield_component_id`).
- Phase 2: Consolidate 6 verified strategy-layer duplication clusters
  (~289 LOC reclaimable: DUP-X-01, DUP-X-02+06, DUP-X-05, DUP-X-07/Cluster 11,
  Cluster 5, Cluster 29+30).
- Phase 3: Consolidate 3 verified UI-layer duplication clusters (~150 LOC
  reclaimable: DUP-X-03, DUP-X-04, Cluster 6).

## Scope
**In:**
- 1 dead-function deletion (Tier 3 / DEEP-01-001).
- 9 duplication consolidations from Section 4 CRITICAL/MAJOR rows that
  passed independent verification.

**Out:**
- Anything the source audit tagged `PRODUCT_DECISION`, `UNCERTAIN`, or
  `false_positive` (see [findings/verification_report.md](findings/verification_report.md)).
- Section 5 complexity hotspots (judgement calls, not shrinkage).
- LOC-ceiling splits for `order_processor.py` (910 LOC) and `turn_engine.py`
  (802 LOC) — structural refactors, not consolidation.
- DUP-X-08 (LLM/Image factory shared base) — verified UNCERTAIN, deferred:
  marginal 30 LOC savings vs. cost of a cross-domain shared service base.
- DEEP-01-004 (`_validate_tick_inputs` boilerplate across 4 engines) —
  VERIFIED but the audit and re-verifier both rate it as low-priority
  structural-only duplication; not worth the churn.
- All MINOR / INFO duplication clusters from the source audit.

## Key Files
| Component | File Path |
|-----------|-----------|
| Planet action engine | `game/strategy/engine/planet_action_engine.py` |
| Planet command handlers | `game/strategy/engine/planet_command_handlers.py` |
| Superweapon command handlers | `game/strategy/engine/superweapon_command_handlers.py` |
| Base command handler | `game/strategy/engine/handlers/base.py` |
| Component inspector | `game/strategy/services/component_inspector.py` |
| Race description LLM controller | `game/strategy/services/race_description_llm_controller.py` |
| Harvesting engine | `game/strategy/engine/harvesting_engine.py` |
| Workshop event router | `game/ui/screens/workshop_event_router.py` |
| Planet/Star list windows | `game/ui/screens/planet_list_window.py`, `game/ui/screens/star_list_window.py` |
| Structure list items | `game/ui/screens/builder/structure_list_items.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source audit
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification results

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
