# PROJ-463: Type cleanup — domain (simulation/strategy/ai) (2026-05-19)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-463` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-463 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical (None-guards + GameSession ignores) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major (Any narrowing + ignore removal + missing returns) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strict-mode migration (ai/simulation/strategy) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-19 23:16
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-19_223900_type-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** Foundation baseline (PROJ-462) should land first — the Vector2 fix clears ~65 simulation + ~6 AI `has-type` errors, and core-protocol narrowing unblocks several strategy returns.

## Overview
This project bundles the domain-layer findings (simulation, strategy, ai) from the type-safety audit at `Reviews/results/2026-05-19_223900_type-audit/`, after an independent third-pass re-verification against live source. It holds 24 verified findings plus the 3 domain-layer strict-mode migration items. It is the heaviest of the three bundles and depends on the foundation bundle (PROJ-462) landing first.

## Goals
- Add the missing seeker/targeting None-guards in combat (Phase 1).
- Replace the 10 `# type: ignore[no-untyped-def]` GameSession mutator/service properties with explicit return types (Phase 1) — resolves ~30% of strategy-layer errors.
- Narrow engine lazy-default mutator getters, `handle_command`, `_time_phase`, `get_effective_stat`, simulation protocols, and the AI controllable adapter (Phase 2).
- Remove unjustified type-ignores and add missing public return types (Phase 2).
- Migrate ai, simulation, and strategy layers toward `mypy --strict` (Phase 3).

## Scope
**In:** simulation, strategy, ai layer findings — `missing_none_guard`, `narrowable_any`, `protocol_any_leakage`, `type_ignore`, `missing_return`, `implicit_optional`, `strict_migration` within those layers.
**Out:**
- Foundation-layer findings (core/services/engine/research/assets) — see sibling [PROJ-462](../PROJ-462/plan.md). The Vector2 and core-protocol fixes there are a prerequisite for this bundle's strict-migration phase.
- Presentation-layer findings (UI + top-level) — see sibling [PROJ-464](../PROJ-464/plan.md).
- REJECTED item TYP-APP — see `findings/verification_report.md`.

## Key Files
| Component | File Path |
|-----------|-----------|
| GameSession properties | `game/strategy/engine/game_session.py` |
| Seeker None-guard | `game/simulation/combat/families/seeker.py` |
| Targeting None-guard | `game/simulation/combat/targeting_system.py` |
| Engine mutator getters (9 sites) | `game/strategy/engine/*.py`, `game/strategy/engine/order_handlers/base.py` |
| AI controllable adapter | `game/ai/interfaces/controllable.py` |
| Ability stat getter | `game/simulation/components/abilities/base.py` |
| Sim entity protocols | `game/simulation/interfaces/entity_protocols.py` |
| Design catalog | `game/strategy/systems/design_catalog.py` |
| issuer adapter | `game/strategy/engine/issuer_adapter.py` |
| battle_runner / attack_processor | `game/simulation/battle_runner.py`, `game/simulation/systems/attack_processor.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification of the audit's claims
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source type-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) - How findings were bundled across the 3 projects

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
