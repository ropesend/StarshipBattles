# PROJ-190: Core Simulation Duck Typing Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-190` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-190 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Define Protocols | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Initialize Lazy Fields | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace Ability Duck Typing | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Replace Combat/Entity Duck Typing | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Test Mocks | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Final Verification | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete. Created 15 protocols (9 ability, 1 component, 5 entity) + 14 TypeGuards across 3 new files.
**Next Action:** Begin Phase 2 - Initialize lazy fields.
**Blockers:** None
**Context for Next Agent:** Phase 1 created ability_protocols.py, component_protocols.py, entity_protocols.py. All 2594 simulation unit tests passing. Next phase addresses lazy init patterns (hasattr self guards) to use direct initialization.

## Overview
Replace all implicit duck typing (`hasattr`/`getattr`) in `game/simulation/` with explicit `typing.Protocol` definitions. This makes every object contract visible to type checkers, enables IDE autocomplete, and creates a direct mapping to C# interfaces / Rust traits for future language portability.

## Goals
- Eliminate all 97 `hasattr`/`getattr` calls in `game/simulation/` (except formula_system.py builtins introspection)
- Define 15 `@runtime_checkable` Protocol classes across 3 new files
- Maintain full test suite passing (12,705 tests)
- Create 1:1 mapping to C# interfaces / Rust traits

## Scope
**In:** All duck-typed access in `game/simulation/` (30 files, 97 instances)
**Out:** Duck typing in `game/ai/`, `game/strategy/`, `game/ui/`, `game/engine/` (separate future projects). No mypy/pyright CI enforcement. No runtime behavior changes.

## Key Files
| Component | File Path |
|-----------|-----------|
| Ability protocols (NEW) | `game/simulation/interfaces/ability_protocols.py` |
| Component protocol (NEW) | `game/simulation/interfaces/component_protocols.py` |
| Entity protocols (NEW) | `game/simulation/interfaces/entity_protocols.py` |
| Interfaces __init__ | `game/simulation/interfaces/__init__.py` |
| Existing protocols (pattern ref) | `game/core/protocols.py` |
| Existing interface (pattern ref) | `game/simulation/interfaces/ai_controller.py` |
| Ship class | `game/simulation/entities/ship.py` |
| Component class | `game/simulation/components/component.py` |
| Projectile class | `game/simulation/entities/projectile.py` |
| Ship stats | `game/simulation/entities/ship_stats.py` |
| Targeting system | `game/simulation/combat/targeting_system.py` |
| Battle state | `game/simulation/battle_state.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, protocol hierarchy design, C#/Rust portability mapping
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12` → 12,705 passed)
- [ ] `grep -rn "getattr\|hasattr" game/simulation/ | grep -v formula_system | wc -l` → 0
- [ ] Audit passed
- [ ] User verified
