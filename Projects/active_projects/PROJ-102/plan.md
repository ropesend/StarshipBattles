# PROJ-102: Strategic Superweapons and Special Orders

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-102` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-102 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Ability Classes & Components | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Order Types & Commands | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Data Model Extensions | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Validators | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Command Handlers | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Order Processing (Turn Execution) | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Input Actions & Key Bindings | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. UI Module - Superweapon Operations | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Integration Tests | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 2 - Order Types & Commands
**Last Action:** Phase 1 complete - Created 6 superweapon abilities + 6 components + 55 tests
**Next Action:** Begin Phase 2 - Add OrderType enum values and command dataclasses
**Blockers:** None
**Context for Next Agent:** Baseline is 7870 tests passing. Phase 1 added superweapons.py, updated abilities/__init__.py, added 6 components to components.json. Follow existing OrderType patterns in fleet.py and commands.py.

## Overview
Add 7 strategic superweapon abilities to the game: Destroy Planet, Destroy Star, Open Warp Point, Close Warp Point, Create Dyson Sphere, and Self-Destruct. Each feature includes a new ability class, component JSON definition, keyboard shortcut, strategy map order, command handler, and turn execution processing. These are galaxy-altering powers that follow the existing ability/component/order/command pipeline.

## Goals
- Add 6 new strategic marker abilities (DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct)
- Add 6 new components to `data/components.json`
- Add 6 new OrderTypes with full serialization
- Add 11 command dataclasses (6 direct + 5 mission/queued)
- Add keyboard shortcuts (Ctrl+I, Ctrl+Shift+S, Ctrl+W, Ctrl+L, Ctrl+D, X)
- Add turn execution logic for each superweapon effect
- Add UI workflows with confirmation dialogs, system picker, and ship picker
- Full test coverage for all new code

## Scope
**In:**
- All 7 superweapon features (abilities, components, commands, orders, processing, UI, input)
- Save/load serialization for new order types
- Event logging for superweapon actions
- PlanetType.DYSON_SPHERE enum value and image registration
- Galaxy cleanup methods (unregister_planet, remove_warp_link)
- Confirmation dialogs for destructive actions
- System picker dialog for Open Warp Point
- Multi-select ship picker dialog for Self-Destruct

**Out:**
- Research system gating (future project)
- Defensive measures/countermeasures (future project)
- AI usage of superweapons (future project)
- Diplomatic consequences of superweapon use
- Visual effects/animations for superweapon execution

## Key Decisions Summary
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Key bindings | Ctrl+ prefix for stellar manipulation | Avoids conflicts with existing unmodified keys |
| Stellerate key | Ctrl+Shift+S | Ctrl+S already bound to Save Game |
| Open Warp key | Ctrl+W (W for Warp) | Avoids O/Ctrl+O confusion with Fleet Orders |
| Star destruction scope | Suicide: ALL ships die | User preference - true superweapon |
| Component constraints | None | Research system not yet implemented |
| Self-destruct UX | Multi-select ship picker | User wants to pick multiple ships from fleet |
| Component consumption | Remove entire ship carrying component | Follows colonization pattern |

## Key Files
| Component | File Path |
|-----------|-----------|
| Ability base class | `game/simulation/components/abilities/base.py` |
| ColonizePlanet (pattern) | `game/simulation/components/abilities/colonize.py` |
| Ability registry | `game/simulation/components/abilities/__init__.py` |
| Component data | `data/components.json` |
| OrderType enum | `game/strategy/data/fleet.py` |
| Command dataclasses | `game/strategy/engine/commands.py` |
| Command handler registry | `game/strategy/engine/command_handlers.py` |
| Order processor | `game/strategy/engine/fleet_order_processor.py` |
| InputAction enum | `game/core/input_actions.py` |
| Key bindings | `data/default_keybindings.json` |
| Input handler | `game/ui/screens/strategy_input_handler.py` |
| Galaxy data | `game/strategy/data/galaxy.py` |
| Planet data | `game/strategy/data/planet.py` |
| Star data | `game/strategy/data/stars.py` |
| Event types | `game/strategy/events/event_types.py` |
| Validation | `game/strategy/validation/__init__.py` |
| Fleet capabilities | `game/strategy/data/fleet_capability_calculator.py` |
| Planet images | `game/strategy/generation/planet_image_registry.py` |
| Dyson Sphere image | `assets/Images/Stellar Objects/Sphere world/Sphereworld_Portrait.png` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No import errors or circular dependencies

### Final Verification
- [ ] Run `pytest tests/ -n 12` - full suite passes (7689+ tests)
- [ ] Manual test: Ship with Planet Imploder -> Ctrl+I -> select planet -> confirm -> planet removed
- [ ] Manual test: Ship with Stellerator -> Ctrl+Shift+S -> select star -> confirm suicide -> system cleared
- [ ] Manual test: Ship with QTI -> Ctrl+W -> select hex -> pick system -> warp points created
- [ ] Manual test: Ship with QTD -> Ctrl+L -> select warp point -> confirm -> both ends removed
- [ ] Manual test: Ship with DSC -> Ctrl+D -> select star -> confirm -> Dyson Sphere created
- [ ] Manual test: Ship with SDD -> X -> pick ships -> confirm -> ships destroyed next turn
- [ ] All phase checklists complete
- [ ] Audit passed
- [ ] User verified
