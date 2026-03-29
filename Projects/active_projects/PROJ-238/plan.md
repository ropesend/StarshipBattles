# PROJ-238: Order System Unification & Planet Orders UI

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-238` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-238 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Merge OrderType Enum | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Rename FleetOrder → Order & Unify Queue Interface | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Unify Action Time Resolvers | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Unify Action Execution Engines | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Rename Processors & Serializer | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Generalize OrdersWindow UI | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Planet Orders Button, Hotkeys & Routing | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-03-29
**Active Phase:** Planning — Awaiting User Approval
**Last Action:** Full plan drafted with 7 phases, swarm review complete
**Next Action:** User approves plan → begin Phase 1 implementation
**Blockers:** None
**Test Baseline:** 14016 passed, 19 failed (pre-existing from PROJ-237 session)

## Overview
Unify the fleet and planet order systems into a single entity-agnostic order pipeline. Rename all fleet-specific order code to generic names (FleetOrder → Order, FleetOrdersWindow → OrdersWindow, etc.). Add planet orders button to the detail panel, generalize the orders window to work for both fleets and planets, and add H hotkey for shield toggle.

**Predecessor:** PROJ-237 (Planetary Shield, Energy System & Planet Orders Framework) — implemented the planet order data model, energy engine, and shield mechanics. This project unifies the two parallel order systems created by PROJ-237.

## Goals
- Merge `PlanetOrderType` into `OrderType` — single enum for all entity orders
- Rename `FleetOrder` → `Order`, `FleetOrderProcessor` → `OrderProcessor`, etc.
- Create `IOrderable` protocol shared by Fleet and Planet
- Generalize `FleetOrdersWindow` → `OrdersWindow` for any orderable entity
- Add planet orders button (`btn_planet_orders`) to planet detail panel
- Add `H` hotkey for shield toggle, `O` for planet orders window
- Use generic `entity_id + entity_type` pattern for order targeting
- Incremental approach — test after each rename to prevent regressions

## Scope
**In:**
- Merge PlanetOrderType values (ACTIVATE_SHIELD, DEACTIVATE_SHIELD) into OrderType enum
- Rename FleetOrder → Order (class + all 94+ import sites)
- Rename Planet.planet_orders → Planet.orders, Planet.get_current_planet_order → Planet.get_current_order, etc.
- Create IOrderable protocol (get_current_order, add_order, pop_order, clear_orders)
- Merge ActionTimeResolver and PlanetActionTimeResolver into unified resolver
- Merge or refactor ActionExecutionEngine + PlanetActionEngine to share logic
- Rename FleetOrderProcessor → OrderProcessor
- Rename FleetOrderSerializer → OrderSerializer
- Rename FleetOrdersWindow → OrdersWindow, generalize for IOrderable entities
- Add btn_planet_orders to planet detail panel (strategy_detail_formatter.py, strategy_panel_manager.py)
- Add InputAction.SHIELD_TOGGLE (H key), InputAction.DETAIL_PANEL_PLANET_ORDERS (O key)
- Create planet command routing in strategy input handler
- Update all affected tests

**Out:**
- New order types beyond ACTIVATE_SHIELD/DEACTIVATE_SHIELD (future work)
- Combat integration for shields (PROJ-237 scoped this out)
- Resource conversion, fighter launch, etc. (future order types)
- Refactoring FleetMovementEngine (stays fleet-only — planets don't move)

## Key Files
| Component | File Path |
|-----------|-----------|
| **OrderType enum + Order class** | `game/strategy/data/order_types.py` |
| **PlanetOrderType (to merge)** | `game/strategy/data/planet_order_types.py` (DELETE after merge) |
| **Fleet order queue** | `game/strategy/data/fleet.py` |
| **Planet order queue** | `game/strategy/data/planet.py` |
| **Fleet order serializer** | `game/strategy/data/fleet_order_serializer.py` |
| **Action execution engine** | `game/strategy/engine/action_execution_engine.py` |
| **Planet action engine** | `game/strategy/engine/planet_action_engine.py` |
| **Fleet order processor** | `game/strategy/engine/fleet_order_processor.py` |
| **Action time resolver** | `game/strategy/services/action_time_resolver.py` |
| **Planet action time resolver** | `game/strategy/services/planet_action_time_resolver.py` |
| **Turn engine** | `game/strategy/engine/turn_engine.py` |
| **Command handlers** | `game/strategy/engine/command_handlers.py` |
| **Planet command handlers** | `game/strategy/engine/planet_command_handlers.py` |
| **Superweapon command handlers** | `game/strategy/engine/superweapon_command_handlers.py` |
| **Fleet orders window** | `game/ui/screens/fleet_orders_window.py` |
| **Strategy window manager** | `game/ui/screens/strategy_window_manager.py` |
| **Strategy fleet command router** | `game/ui/screens/strategy_fleet_command_router.py` |
| **Strategy event router** | `game/ui/screens/strategy_event_router.py` |
| **Strategy detail formatter** | `game/ui/screens/strategy_detail_formatter.py` |
| **Strategy panel manager** | `game/ui/screens/strategy_panel_manager.py` |
| **Strategy input handler** | `game/ui/screens/strategy_input_handler.py` |
| **Input actions** | `game/core/input_actions.py` |
| **Default keybindings** | `data/default_keybindings.json` |
| **Engine interfaces** | `game/strategy/interfaces/engines.py` |
| **Commands** | `game/strategy/engine/commands.py` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-29 | Unified OrderType enum (merge planet orders into it) | Fleets, planets, and future stations all share same order types where applicable. Single enum simplifies dispatch. |
| 2026-03-29 | Space stations = immobile fleets | No new entity type needed. Stations are fleets with no strategic movement points. |
| 2026-03-29 | Generic entity_id + entity_type for order targeting | Clean, no import dependencies. Matches BuildEntityType pattern. |
| 2026-03-29 | Rename everything incrementally with testing | User wants clean code — nothing planet-related should be called "fleet_something". Each rename verified by test run. |
| 2026-03-29 | H key for shield toggle | Avoids conflict with existing fleet hotkeys (M, J, C, T, W, D, L, X). |
| 2026-03-29 | Same OrdersWindow for fleets and planets | Reuse FleetOrdersWindow, generalize to accept IOrderable. Less code duplication. |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- PROJ-237 plan — predecessor project

## Swarm Findings Summary

### Architecture
- FleetOrder is deeply embedded: 94+ files import it, all at runtime (no TYPE_CHECKING)
- PlanetOrder has light coupling: 14 files, mostly TYPE_CHECKING
- The two order classes are structurally identical (type, target, execution_progress)
- FleetOrdersWindow uses callback pattern (closures capturing fleet_id) — easily generalizable
- Button visibility controlled by StrategyDetailFormatter based on selection type

### Key Patterns to Reuse
- **Callback closures**: StrategyWindowManager creates command closures at window open time — `strategy_window_manager.py:382-421`
- **InputMapper routing**: Keyboard → InputAction → FleetCommandRouter → action — `strategy_input_handler.py:102-129`
- **Button visibility state machine**: Format method shows/hides buttons based on selection — `strategy_detail_formatter.py:330-350`
- **CQRS command dispatch**: All UI operations → Command → facade.handle_command() — consistent pipeline

### Risks Identified
1. **94+ files reference FleetOrder** (HIGH) — Rename requires touching many files. Mitigate: automated search, test after each batch.
2. **Serialization backward compatibility** (MEDIUM) — FleetOrder has 7 target formats. Merged Order must handle all formats plus planet dict format. Mitigate: keep serializer logic, just rename class.
3. **Test fragility** (MEDIUM) — Many tests construct FleetOrder directly. Mechanical rename but high volume (~66 test files). Mitigate: batch rename, run tests after each phase.
4. **Phase ordering matters** (LOW) — Enum merge must happen before class rename. Class rename before engine unification.

---

## Phases

### Phase 1: Merge OrderType Enum [Medium]
**Objective:** Add ACTIVATE_SHIELD and DEACTIVATE_SHIELD to OrderType enum. Add them to ACTION_ORDER_TYPES. Delete PlanetOrderType enum. Update all PlanetOrderType references to use OrderType.
**Status:** Not Started

### Phase 2: Rename FleetOrder → Order & Unify Queue Interface [Complex]
**Objective:** Rename FleetOrder class to Order. Rename Planet.planet_orders → Planet.orders and planet queue methods. Create IOrderable protocol. Update all 94+ import sites.
**Status:** Not Started

### Phase 3: Unify Action Time Resolvers [Simple]
**Objective:** Merge PlanetActionTimeResolver into ActionTimeResolver. Single mapping dict for all order types. Delete planet_action_time_resolver.py.
**Status:** Not Started

### Phase 4: Unify Action Execution Engines [Complex]
**Objective:** Merge PlanetActionEngine logic into ActionExecutionEngine (or create shared base). Handle fleet speed-based intervals vs planet every-tick. Delete planet_action_engine.py. Update TurnEngine.
**Status:** Not Started

### Phase 5: Rename Processors & Serializer [Medium]
**Objective:** Rename FleetOrderProcessor → OrderProcessor, FleetOrderSerializer → OrderSerializer. Update all references.
**Status:** Not Started

### Phase 6: Generalize OrdersWindow UI [Medium]
**Objective:** Rename FleetOrdersWindow → OrdersWindow. Accept IOrderable entity instead of Fleet. Update StrategyWindowManager to support opening for planets. Rename fleet_orders_window.py → orders_window.py.
**Status:** Not Started

### Phase 7: Planet Orders Button, Hotkeys & Routing [Medium]
**Objective:** Add btn_planet_orders to planet detail panel. Add H hotkey for shield toggle. Add O hotkey for planet orders window. Wire through input handler and command routing.
**Status:** Not Started

---

## Verification

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `python -m pytest tests/ -n 12` — baseline established

### After Each Phase
- [ ] Run `python -m pytest tests/ -n 12` — same pass/fail count as baseline
- [ ] Verify no import errors: `python -c "from game.strategy.engine.turn_engine import TurnEngine"`

### Final Verification
- [ ] Start new quickstart game — planet detail panel shows orders button
- [ ] Press O on selected planet → orders window opens
- [ ] Press H on selected planet → shield activation order queued
- [ ] Orders window shows planet orders with reorder/delete controls
- [ ] Fleet orders window still works unchanged
- [ ] Run full test suite: `python -m pytest tests/ -n 12` — all tests pass

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1-7 tasks checked off
- [ ] All tests passing (14016+ passed)
- [ ] No fleet-specific naming in entity-agnostic order code
- [ ] Planet orders window functional
- [ ] Shield toggle hotkey working
- [ ] Regression tests passing
- [ ] User verified
