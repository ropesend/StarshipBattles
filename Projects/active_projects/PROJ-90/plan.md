# PROJ-90: Untangle Circular Dependencies and Layer Violations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-90` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-90 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins — Dead Code & Config Extraction | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Core → Simulation Violation Fix | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Ship.py Late Import Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategy-Simulation Boundary Protocol | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Documentation & Audit | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 3 — Ship.py Late Import Cleanup
**Last Action:** Phase 2 complete. Extracted reload_registries_from_directory() to simulation layer, fixing Core→Simulation violation.
**Next Action:** Start Phase 3 — Clean up late imports in ship.py
**Blockers:** None
**Context for Next Agent:** 7540 tests passing. Phase 2 created registry_loader.py (113 lines), removed 94-line method from RegistryManager. game/core/registry.py now has zero imports from game.simulation.

## Overview
A code review audit flagged pervasive circular dependencies managed through TYPE_CHECKING guards. Deep analysis by 6 swarm agents revealed the codebase is in much better shape than the audit suggested — no true import cycles exist at runtime, and the layer architecture is fundamentally sound. This project fixes 5 concrete issues: a Core→Simulation layer violation in registry.py, BattleConfig/BattleMode placement causing a circular import workaround, dead code in ship.py, unnecessary late imports in ship.py (verified NOT to be real cycles), and formalizing the ShipInstance→Ship coupling with a protocol.

## Goals
- Fix the only real layer violation: Core → Simulation imports in `registry.py`
- Extract BattleConfig/BattleMode to eliminate circular import workaround
- Remove dead code (no-op TYPE_CHECKING block)
- Move 4 unnecessary late imports in ship.py to module level (all verified safe)
- Formalize the strategy-simulation boundary with `IPostBattleShip` protocol
- Update ARCHITECTURE.md to reflect the cleaned state

## Scope
**In:**
- Core → Simulation layer violation in `registry.py`
- BattleConfig/BattleMode extraction from `battle_controller.py`
- Ship.py no-op TYPE_CHECKING block removal
- Ship.py late import cleanup (WeaponAbility, ModifierService, ShipCombatEngine, ShipSerializer)
- ShipComponentManager late import cleanup (same ModifierService pattern)
- IPostBattleShip protocol definition
- ShipInstance and Fleet type annotation updates
- BattleResult DTO typing strengthening
- ARCHITECTURE.md updates

**Out:**
- TurnEngine lazy properties (verified as legitimate service locator pattern)
- App.py lazy imports (legitimate startup optimization)
- UI TYPE_CHECKING imports (legitimate downward dependencies)
- Fleet.py late imports of FleetNavigationService/FleetSpeedCalculator (documented edge operations)
- ShipInstance.to_ship() / from_ship() late import of ShipSerializer (intentional cross-layer, allowed direction)
- Any changes to Galaxy.py internal imports

## Key Files
| Component | File Path |
|-----------|-----------|
| Ship class | `game/simulation/entities/ship.py` |
| ShipCombatEngine | `game/simulation/entities/ship_combat_engine.py` |
| ShipSerializer | `game/simulation/entities/ship_serialization.py` |
| ShipComponentManager | `game/simulation/entities/ship_component_manager.py` |
| BattleController | `game/simulation/battle_controller.py` |
| BattleStateManager | `game/simulation/managers/battle_state_manager.py` |
| BattleModeHandler | `game/simulation/combat/battle_mode_handler.py` |
| Registry (Core) | `game/core/registry.py` |
| Protocols (Core) | `game/core/protocols.py` |
| ShipInstance (Strategy) | `game/strategy/data/ship_instance.py` |
| Fleet (Strategy) | `game/strategy/data/fleet.py` |
| BattleResolver interface | `game/strategy/interfaces/battle_resolver.py` |
| SimulationAdapter | `game/strategy/adapters/simulation_adapter.py` |
| Architecture docs | `docs/architecture/ARCHITECTURE.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (7353+ passed, 0 failed)
- [ ] `game/core/registry.py` has no imports from `game.simulation`
- [ ] `game/simulation/entities/ship.py` has no late imports
- [ ] `game/simulation/managers/battle_state_manager.py` has no late imports
- [ ] `game/strategy/data/ship_instance.py` no longer TYPE_CHECKING imports Ship
- [ ] ARCHITECTURE.md updated
- [ ] Audit passed
- [ ] User verified
