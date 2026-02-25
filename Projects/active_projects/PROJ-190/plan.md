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
| 2. Initialize Lazy Fields | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace Ability Duck Typing | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Replace Combat/Entity Duck Typing | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Test Mocks | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Final Verification | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 5
**Last Action:** Phase 4 complete. Replaced ~35 combat/entity duck typing instances across 14 files.
**Next Action:** Begin Phase 5 - Update test mocks to include required protocol attributes.
**Blockers:** None
**Context for Next Agent:** Phase 4 completed. Updated targeting_system.py, battle_state.py, weapon_firing_system.py, ship_physics.py, ship_formation.py, ship_serialization.py, ship_combat_engine.py, ship_stat_querier.py, projectile_manager.py, battle_engine.py, ship_validator.py, battle_state_manager.py, projectile.py, ship.py. Added total_strategic_movement, warp_max_tonnage, warp_energy_cost to Ship.__init__. 30 test failures due to mocks missing required attributes - fixed in Phase 5. 26 remaining getattr/hasattr calls are legitimate meta-programming.

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
