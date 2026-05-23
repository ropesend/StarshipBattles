# PROJ-462: Type cleanup — foundation (core/services/engine/research/assets) (2026-05-19)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-462` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-462 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical (foundation root causes) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major (core/engine narrowing + ignores) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strict-mode migration (research/services/assets/engine/core) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-19 23:16
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-19_223900_type-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
This project bundles the foundation-layer findings (core, services, engine, research, assets) from the type-safety audit at `Reviews/results/2026-05-19_223900_type-audit/`, after an independent third-pass re-verification against live source. It holds 17 verified code findings plus the 5 foundation-layer strict-mode migration items. These fixes are the dependency root: fixing `Vector2` and the core protocol/registry contracts here resolves ~130 downstream mypy errors in the domain and presentation bundles, so this project should be sequenced first.

## Goals
- Fix the `Vector2` implicit-Optional root cause that cascades ~130 `has-type` errors across 4 layers (Phase 1).
- Narrow `validate_enum`, `formula_evaluator`, `registry.get_validator`, and `state_machine` core public-API `Any` returns (Phase 1/2).
- Add the missing None-guard in `engine/collision.py` (Phase 1).
- Tighten core protocol `Any` returns/params to core types where layer-safe, leaving intentionally polymorphic seams as `Any` (Phase 2).
- Migrate research, services, assets, engine, and core layers toward `mypy --strict` (Phase 3).

## Scope
**In:** core, engine, research, services, assets layer findings — `narrowable_any`, `wrong_annotation`, `type_ignore`, `protocol_any_leakage`, `strict_migration` categories within those layers.
**Out:**
- Domain-layer findings (simulation/strategy/ai) — see sibling [PROJ-463](../PROJ-463/plan.md).
- Presentation-layer findings (UI + top-level) — see sibling [PROJ-464](../PROJ-464/plan.md).
- REJECTED item TYP-APP and the boundary-preserving carve-outs (`ICombatant.position`, `ILocatable.location` stay `Any`) — see `findings/verification_report.md`.

## Key Files
| Component | File Path |
|-----------|-----------|
| Vector2 root cause | `game/core/math.py` |
| Core protocols (entities) | `game/core/protocols/strategy_entities.py` |
| Core protocols (mutators) | `game/core/protocols/strategy_mutators.py` |
| Enum validation | `game/core/validation_helpers.py` |
| Formula AST evaluator | `game/core/formula_evaluator.py` |
| Registry validator getters | `game/core/registry.py` |
| Screen state machine | `game/core/state_machine.py` |
| JSON serialization helper | `game/core/json_utils.py` |
| Beam None-guard | `game/engine/collision.py` |

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
