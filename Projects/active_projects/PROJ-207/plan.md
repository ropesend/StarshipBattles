# PROJ-207: Fleet Order System Unification

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-207` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-207 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Save/Load Data Integrity | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Superweapon Validation & Execution | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Execution Path Cleanup | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Command Pipeline Consistency | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Code Hygiene & Dead Code | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-27
**Active Phase:** Audit
**Last Agent Action:** Phase 5 complete - All 5 tasks done
**Next Action:** Run audit to verify project completion
**Blockers:** None
**Test Baseline:** 12,866 passed, 4 pre-existing failures (bug_13_colony_flags), 1 skipped
**Context for Next Agent:** Phase 5 complete. Deleted dead lifecycle methods (complete_order, cancel_order, cancel_all_orders). Removed duplicate BUILD auto-pop code. Extracted _finalize_superweapon() helper and added SG-003 fleet cleanup. Renamed process_end_turn_orders to execute_action_order with registry pattern. Enhanced add_move_order_if_needed() with chain-aware start_hex auto-detection. All 5 phases complete - ready for audit.

## Overview
Systematic unification and remediation of the fleet order system based on deep code review
(Review: 2026-02-27_153151_general_fleet-order-systems). The review found that the command
input layer is well-structured but the execution layer is fragmented — multiple dispatch paths,
duplicated boilerplate, inconsistent error handling, and validation gaps.

**15 validated findings** across 5 review agents (3 Critical, 12 Major) organized into
5 implementation phases by functional area.

## Goals
- Fix save/load data loss bugs (ODM-001, ODM-003)
- Close superweapon validation gaps that allow invalid orders (VC-001, VC-002, VC-007)
- Eliminate dual execution paths and inconsistent error handling (EP-001, EP-005)
- Bring BUILD orders and FleetOrdersWindow into the command pipeline (CP-001, CP-002)
- Remove duplicated code and dead lifecycle methods (CP-003, EP-002, EP-004, AU-002, AU-004, AU-005)

## Scope
**In:**
- `game/strategy/data/fleet.py` — FleetOrder serialization, order queue management
- `game/strategy/engine/command_handlers.py` — Command handlers, auto-load duplication
- `game/strategy/engine/commands.py` — Command classes (IssueBuildOrderCommand for Task 4.1)
- `game/strategy/engine/fleet_order_processor.py` — Order lifecycle, dispatch god-method
- `game/strategy/engine/fleet_movement_engine.py` — Movement error handling
- `game/strategy/engine/action_execution_engine.py` — Tick-based action processing
- `game/strategy/engine/superweapon_order_processor.py` — Superweapon execution boilerplate
- `game/strategy/engine/superweapon_command_handlers.py` — Superweapon validation calls
- `game/strategy/engine/game_session.py` — resolve_order_references() call site in from_dict() (Task 1.1)
- `game/strategy/interfaces/engines.py` — IOrderProcessor interface rename (Task 5.4)
- `game/strategy/validation/superweapon_validator.py` — Ability validation guards
- `game/ui/screens/fleet_orders_window.py` — Direct fleet manipulation bypass
- `game/ui/screens/strategy_build_queue_manager.py` — BUILD order bypass

**Out:**
- New order types or features
- Combat AI strategic order generation
- UI rendering/drawing code
- Galaxy generation
- Ship component definitions (except action_time)

## Key Files
| Component | File Path | Key Areas |
|-----------|-----------|-----------|
| Order Data Model | `game/strategy/data/fleet.py` | FleetOrder.to_dict/from_dict, OrderType categories |
| Command Handlers | `game/strategy/engine/command_handlers.py` | ColonizeCommandHandler, ColonizeMissionCommandHandler, add_move_order_if_needed |
| Order Processor | `game/strategy/engine/fleet_order_processor.py` | process_end_turn_orders (L574-668), process_instant_orders (L670-704), complete_order/cancel_order (L76-127) |
| Movement Engine | `game/strategy/engine/fleet_movement_engine.py` | clear_orders() on failure (L153, 165, 170) |
| Action Engine | `game/strategy/engine/action_execution_engine.py` | BUILD auto-pop (L140-145) |
| Superweapon Processor | `game/strategy/engine/superweapon_order_processor.py` | 6 process_* methods (592 lines), ships[0] fallback |
| Superweapon Handlers | `game/strategy/engine/superweapon_command_handlers.py` | Direct handlers (L46-170), Mission handlers (L223-344) |
| Superweapon Validator | `game/strategy/validation/superweapon_validator.py` | component_registry guard (L58) |
| Fleet Orders UI | `game/ui/screens/fleet_orders_window.py` | clear_orders bypass (L386) |
| Build Queue UI | `game/ui/screens/strategy_build_queue_manager.py` | Direct FleetOrder creation (L138) |
| Command Classes | `game/strategy/engine/commands.py` | IssueBuildOrderCommand (Task 4.1) |
| Engine Interfaces | `game/strategy/interfaces/engines.py` | IOrderProcessor.process_end_turn_orders rename (Task 5.4) |
| Game Session | `game/strategy/engine/game_session.py` | from_dict() resolve_order_references call site (Task 1.1) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Review Report](../../Reviews/results/2026-02-27_153151_general_fleet-order-systems/report.md)
- [Review Findings](../../Reviews/results/2026-02-27_153151_general_fleet-order-systems/findings/)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (12,827+ baseline)
- [ ] Audit passed
- [ ] User verified
