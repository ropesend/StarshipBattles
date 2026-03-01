# PROJ-207: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-27_153151_general_fleet-order-systems](../../Reviews/results/2026-02-27_153151_general_fleet-order-systems/)
- **Type:** General Review (focused deep-dive)
- **Date:** 2026-02-27
- **Report:** [View Full Report](../../Reviews/results/2026-02-27_153151_general_fleet-order-systems/report.md)
- **Agents:** 5 review agents + 3 validators

## Initial Analysis
The fleet order system has a clean input pipeline (UI → Command → Handler → FleetOrder) but a
fragmented execution layer. 63 raw findings across 5 agents, validated down to 45 confirmed.
15 Critical/Major findings selected for this project.

- **Critical:** 3 (ODM-001, VC-001, VC-002)
- **Major:** 12 (ODM-003, EP-001, EP-002, EP-004, EP-005, CP-001, CP-002, CP-003, CP-005, AU-002, AU-004, AU-005)
- **Selected for remediation:** 15

## Architecture: Current Fleet Order Pipeline

```
USER ACTION (click on map)
    ↓
UI Layer (strategy_fleet_ops, fleet_orders_window, etc.)
    ↓
Command Object (IssueMoveCommand, IssueColonizeCommand, etc.)
    ↓
GameSession.dispatch_command()
    ↓
CommandHandlerRegistry.dispatch()
    ↓
Handler.execute() [validates, creates FleetOrder(s)]
    ↓
Fleet.orders queue [List[FleetOrder]]
    ↓
TurnEngine tick loop
    ↓
┌─────────────────────────────────────────────┐
│  Phase 1: process_instant_orders()          │ ← JOIN_FLEET when co-located
│  Phase 1.5: ActionExecutionEngine           │ ← Tick-based (COLONIZE, TRANSFER, superweapons)
│  Phase 2-3: FleetMovementEngine             │ ← Path-based (MOVE, WARP, MOVE_TO_FLEET)
└─────────────────────────────────────────────┘
    ↓
Order completion / fleet state changes
```

## Selected Findings Summary

### Phase 1: Save/Load Data Integrity
| ID | Title | Severity | Effort |
|----|-------|----------|--------|
| ODM-001 | _fleet_ref/_planet_ref markers never resolved after deserialization | Critical | Medium |
| ODM-003 | Planet target serializes as full dict, from_dict can't parse it back | Major | Simple |

### Phase 2: Superweapon Validation & Execution
| ID | Title | Severity | Effort |
|----|-------|----------|--------|
| VC-001 | Direct superweapon handlers skip ability validation (no component_registry) | Critical | Simple |
| VC-002 | Mission superweapon handlers skip ALL validation | Critical | Simple |
| CP-005 | (Same as VC-002 — duplicate finding from different agent) | Major | Simple |
| VC-007 | Superweapon processors fallback to fleet.ships[0] when ability not found | Major | Simple |

### Phase 3: Execution Path Cleanup
| ID | Title | Severity | Effort |
|----|-------|----------|--------|
| EP-001 | JOIN_FLEET processed in both instant and tick-based paths | Major | Simple |
| EP-005 | Movement failures clear all orders; action failures pop single order | Major | Medium |

### Phase 4: Command Pipeline Consistency
| ID | Title | Severity | Effort |
|----|-------|----------|--------|
| CP-002 | BUILD orders bypass command pipeline entirely (no Command/Handler) | Major | Medium |
| CP-001 | FleetOrdersWindow Clear All bypasses command pipeline | Major | Simple |
| CP-003 | Auto-load population logic copy-pasted in two colonize handlers | Major | Simple |

### Phase 5: Code Hygiene & Dead Code
| ID | Title | Severity | Effort |
|----|-------|----------|--------|
| EP-002 | complete_order()/cancel_order() are dead code (never called) | Major | Medium |
| EP-004 | Duplicate BUILD auto-pop in ActionExecutionEngine and FleetOrderProcessor | Major | Simple |
| AU-005 | SuperweaponOrderProcessor: 6 methods repeat 350 lines of boilerplate | Major | Medium |
| AU-002 | process_end_turn_orders() is a 94-line if/elif dispatch god-method | Major | Medium |
| AU-004 | Mission move+action chaining duplicated (3 separate implementations) | Major | Simple |

## Key Patterns to Reuse
- **CommandHandlerRegistry**: `command_handlers.py:514-562` — successful dispatch registry pattern, model for AU-002
- **BaseCommandHandler helpers**: `_resolve_fleet()`, `_resolve_planet()` — consistent resolution utilities
- **add_move_order_if_needed()**: `command_handlers.py:27-60` — extracted move helper, target pattern for AU-004
- **ValidationResult**: consistent validation reporting pattern

## Dependencies & Risks
1. **Phase ordering matters** — Phase 5 tasks depend on Phase 3 removing branches first
2. **Superweapon validation changes** — May cause previously-passing invalid orders to fail. This is correct behavior but could surface in tests that assume the gap.
3. **Movement error handling change** — Phase 3 Task 3.2 differentiates movement failures: stranded (no fuel) keeps `clear_orders()` since fleet can't move at all; warp failures use `pop_order()` since fleet can still move normally. This changes player-visible behavior for warp failures only.
4. **Save/load format change** — Phase 1 changes Planet serialization from full dict to `_planet_ref`. Per project policy, old saves are disposable — no backward compatibility shim is needed. The old format was broken (produced `None` targets), so there are no valid saves to preserve.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
