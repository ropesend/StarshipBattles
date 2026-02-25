# PROJ-187: Strategy Orders Tick-Based Action System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-187` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-187 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Data Model (FleetOrder + OrderType.WARP) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. action_time on Component Abilities | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ActionExecutionEngine | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Wire Into Turn Loop + Eradicate End-of-Turn | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Test Migration | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. WARP Order Implementation | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Command Handler Review + Path Projection | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Documentation | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 6 (WARP Order Implementation)
**Last Action:** Phase 5 complete - verified all test migration was completed in Phase 4, 12,445 tests passing
**Next Action:** Begin Phase 6 - Implement OrderType.WARP primitive
**Blockers:** None
**Baseline:** 12,445 passed, 1 skipped, 0 failures

## Overview
Convert the strategy layer's order execution from a split model (tick-based movement + instant end-of-turn actions) into a unified tick-based action system where every strategic action (COLONIZE, TRANSFER, superweapons, LOAD/UNLOAD) consumes "action ticks" at the same rate as movement. Also adds explicit WARP order primitive and moddable `action_time` on component abilities.

## Goals
- Unify all order execution into the 100-tick turn loop (eliminate `_process_end_turn_orders()`)
- Make action duration moddable via `action_time` on component abilities in `components.json`
- Add execution_progress tracking to FleetOrder for multi-tick actions
- Add explicit WARP order primitive for manual warp point traversal
- Maintain full backward compatibility for save games (graceful default for missing fields)

## Scope
**In:**
- Tick-based execution for COLONIZE, TRANSFER, LOAD/UNLOAD_POPULATION, JOIN_FLEET, all superweapons
- `execution_progress` field on FleetOrder with serialization
- `action_time` field on ColonizePlanet and SuperweaponMarker abilities
- ActionExecutionEngine as new delegated engine in TurnEngine
- OrderType.WARP primitive with command handler and auto-queuing
- FleetNavigationService path projection updates for action timing
- Documentation at `docs/architecture/orders_system.md`

**Out:**
- Fog-of-war / unexplored warp point system (future project)
- Changes to BUILD order (remains handled by ProductionEngine)
- Changes to movement mechanics (speed, resource consumption unchanged)
- AI order-giving logic updates (future project)

## Key Files
| Component | File Path |
|-----------|-----------|
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Fleet & Orders | `game/strategy/data/fleet.py` |
| Order Processor | `game/strategy/engine/fleet_order_processor.py` |
| Movement Engine | `game/strategy/engine/fleet_movement_engine.py` |
| Superweapon Processor | `game/strategy/engine/superweapon_order_processor.py` |
| Engine Interfaces | `game/strategy/interfaces/engines.py` |
| Command Handlers | `game/strategy/engine/command_handlers.py` |
| Superweapon Handlers | `game/strategy/engine/superweapon_command_handlers.py` |
| Navigation Service | `game/strategy/services/fleet_navigation_service.py` |
| Pathfinding | `game/strategy/data/pathfinding.py` |
| ColonizePlanet Ability | `game/simulation/components/abilities/colonize.py` |
| Superweapon Abilities | `game/simulation/components/abilities/superweapons.py` |
| Components JSON | `data/components.json` |
| Action Engine (NEW) | `game/strategy/engine/action_execution_engine.py` |
| Action Time Resolver (NEW) | `game/strategy/services/action_time_resolver.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual test: colonize distant planet (LOAD -> MOVE -> COLONIZE with tick timing)
- [ ] Manual test: fire superweapon (multi-tick wind-up)
- [ ] Manual test: cancel mid-progress superweapon (progress lost)
- [ ] Manual test: WARP order through warp point
- [ ] Audit passed
- [ ] User verified
