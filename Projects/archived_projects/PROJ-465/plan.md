# PROJ-465: Audit-shrink cleanup 2026-05-20

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-465` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-465 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Duplication consolidation | Complete (7 implemented, 10 deferred) | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Codex-audit remediation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-20
**Active Phase:** Phase 2 of 2 (complete)
**Last Action:** Implemented the 7 byte-identical / trivially-equivalent
mechanical dedups via TDD; deferred the 10 higher-risk / non-mechanical
clusters with rationale in decisions.md (Cluster 2 logged as DI-2026-05-21-005).
Ran a Codex audit (no code regressions; 3 process/coverage findings) and
remediated the two VERIFIED findings: added satellite-path characterization
for Cluster 19's shared helper, and reconciled the project artifacts.
**Next Action:** Orchestrator to commit; user verification.
**Blockers:** None
**Determinism note:** full strategy + simulation unit suites (10,332) green;
battle RNG-isolation + combat suites (415) green; serialization round-trips
(DUP-X-5) preserved byte-for-byte.

## Overview
Created from the code-shrinkage audit `Reviews/results/2026-05-20_060020_audit_shrink`.
Of the audit's verified-safe candidates (1 dead file + 18 CRITICAL/MAJOR duplication
clusters), independent re-verification against the live tree confirmed **17 duplication
clusters** as safe to consolidate (audit-claimed reclaimable ~ **919 LOC** for those
items). The single dead-file candidate (`setup_renderer.py`, 216 LOC) and one
duplication (DUP-X-4) landed UNCERTAIN and are excluded — see
`findings/verification_report.md`.

## Goals
- Consolidate 17 verified duplication clusters into shared helpers / base methods,
  removing duplicate sites and routing all callers through the canonical implementation
  (~919 LOC reclaimable per the audit).

## Scope
**In:** `duplication` consolidations (CRITICAL + MAJOR clusters with concrete sites and
extraction targets that survived independent verification).
**Out:**
- Anything the audit tagged PRODUCT_DECISION, UNCERTAIN, or false_positive (see
  `findings/verification_report.md`) — including the 18 PRODUCT_DECISION dead-code
  items and the `setup_renderer.py` deletion (UNCERTAIN: gated on the `setup_screen.py`
  PRODUCT_DECISION) and DUP-X-4 (UNCERTAIN: claimed scope not present in live code).
- Complexity hotspots from the source audit (Section 5).

## Key Files
| Component | File Path |
|-----------|-----------|
| Command handler base | `game/strategy/engine/handlers/base.py` |
| Order handlers (launch/recover/lay) | `game/strategy/engine/order_handlers/recover_fighters.py` |
| Order handlers (launch/recover) | `game/strategy/engine/order_handlers/recover_satellites.py` |
| Order/command handlers (launch) | `game/strategy/engine/order_handlers/launch_fighters.py` |
| Deployed group data | `game/strategy/data/deployed_group.py` |
| Component abilities service | `game/strategy/services/component_abilities.py` |
| Planetary stat-modifier abilities | `game/simulation/components/abilities/planetary/stat_modifiers.py` |
| Battle engine | `game/simulation/systems/battle_engine.py` |
| Superweapon designation UI | `game/ui/screens/strategy_superweapons.py` |
| Hit-effect rendering | `game/ui/effects/hit_effects.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification of the audit's claims
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source audit

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
