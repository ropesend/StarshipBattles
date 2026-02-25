# PROJ-192: AI Behavior Protocols - Duck Typing Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-192` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-192 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. AI Protocols (Foundation) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Controller + Target Evaluator Cleanup | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Formation + Adapter Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. combat_utils.py Refactoring | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Final Audit + Type Annotations | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-24 21:10
**Active Phase:** Planning
**Last Action:** Plan created and approved
**Next Action:** Begin Phase 1 — create `game/ai/protocols.py`
**Blockers:** None
**Context for Next Agent:** Baseline is 12705 passed, 1 skipped. The `game/core/protocols.py` file has the established pattern to follow (`@runtime_checkable` + `TypeGuard`). Bug confirmed: `target_evaluator.py:184` uses `getattr(c, 'hp', 0)` but Component has no `.hp` — fix to `c.current_hp` in Phase 2.

## Overview
Eliminate ~45 `hasattr()`/`getattr()` duck typing instances across 5 files in `game/ai/` by introducing explicit `@runtime_checkable` Protocol types. This makes AI type contracts visible to developers and static checkers, fixes one confirmed bug, and follows the established protocol patterns in `game/core/protocols.py`.

## Goals
- Replace all implicit duck typing in `game/ai/` with explicit Protocol-based typing
- Fix the `_eval_least_armor_rule` bug (always returns 0 due to `getattr(c, 'hp', 0)` on Component which has no `.hp`)
- Create reusable AI-layer protocols for grid entities, projectiles, formation masters, and component health
- Maintain zero test regressions (12705+ tests passing)

## Scope
**In:**
- `game/ai/behaviors.py` — 5 instances
- `game/ai/combat_utils.py` — 12 instances
- `game/ai/controller.py` — 8 instances
- `game/ai/target_evaluator.py` — 5 instances
- `game/ai/interfaces/controllable.py` — 4 instances
- New: `game/ai/protocols.py`
- New: `tests/unit/ai/test_ai_protocols.py`

**Out:**
- Duck typing in other layers (ui/, strategy/, simulation/) — those are separate projects
- Modifying Ship, Projectile, or Component classes themselves
- Changes to `game/core/protocols.py` (we create AI-layer protocols, not core)

## Key Files
| Component | File Path |
|-----------|-----------|
| AI Protocols (NEW) | `game/ai/protocols.py` |
| Core Protocols (reference) | `game/core/protocols.py` |
| AI Controller | `game/ai/controller.py` |
| Target Evaluator | `game/ai/target_evaluator.py` |
| Behaviors | `game/ai/behaviors.py` |
| Combat Utils | `game/ai/combat_utils.py` |
| Controllable Interface | `game/ai/interfaces/controllable.py` |
| Ship | `game/simulation/entities/ship.py` |
| Projectile | `game/simulation/entities/projectile.py` |
| Component | `game/simulation/components/component.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Audit passed (zero hasattr/getattr in target files)
- [ ] User verified
