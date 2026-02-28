# Review Scope: Fleet Order Systems

## Metadata
- **Date:** 2026-02-27 15:31
- **Type:** General Review (focused deep-dive)
- **Description:** Fleet order systems — how orders are given, stored, and executed

## Scope Definition

### Target
- [x] Specific module: Fleet order pipeline (strategy + simulation + UI)

### Included Files
- **Data models**: `game/strategy/data/fleet.py` (OrderType, FleetOrder, Fleet.orders)
- **Command layer**: `game/strategy/engine/commands.py` (all Issue*Command, Queue*Command)
- **Command handlers**: `game/strategy/engine/command_handlers.py` (CommandHandlerRegistry, all handlers)
- **Order execution**:
  - `game/strategy/engine/fleet_order_processor.py` (order lifecycle, action dispatch)
  - `game/strategy/engine/fleet_movement_engine.py` (movement orders)
  - `game/strategy/engine/action_execution_engine.py` (tick-based actions)
  - `game/strategy/engine/superweapon_order_processor.py` (superweapon execution)
  - `game/strategy/engine/turn_engine.py` (orchestration)
- **Validation**: `game/strategy/validation/` (colonize, transfer, superweapon validators)
- **Services**: `game/strategy/services/action_time_resolver.py`
- **UI entry points**:
  - `game/ui/screens/fleet_orders_window.py`
  - `game/ui/screens/strategy_fleet_ops.py`
  - `game/ui/screens/strategy_colonization.py`
  - `game/ui/screens/transfer_dialog.py`
  - `game/ui/screens/cargo_quick_dialog.py`
- **Tests**: All tests covering the above files

### Exclusions
- Combat AI (`game/ai/controller.py`) — tactical combat, not strategic orders
- Ship component definitions (except action_time resolution)
- Galaxy generation
- Pure rendering/drawing code

### Priorities
1. **System fragmentation**: Are there parallel/duplicate systems doing similar things?
2. **Consistency**: Do all order types follow the same patterns for validation, creation, execution?
3. **Unification opportunities**: What could be consolidated without losing necessary heterogeneity?
4. **Architecture quality**: Is the command→handler→order→execution pipeline clean?
5. **Code quality**: DRY violations, overly complex dispatch, missing abstractions

## Pre-Review Architecture Understanding

### Order Pipeline
```
UI/AI → Command object → CommandHandlerRegistry → Handler validates → FleetOrder(s) created → Fleet.orders queue
```

### Three Execution Paths
1. **Instant**: JOIN_FLEET when co-located (process_instant_orders)
2. **Movement**: MOVE/WARP/MOVE_TO_FLEET (FleetMovementEngine, per-subtick)
3. **Tick-based Actions**: COLONIZE/TRANSFER/superweapons (ActionExecutionEngine, execution_progress counter)

### Known Complexity Factors
- 16 OrderType enum values
- 7 different FleetOrder.target serialization formats
- Auto-chaining (commands create multiple orders: MOVE + COLONIZE, etc.)
- Separate processors: FleetOrderProcessor, SuperweaponOrderProcessor, FleetMovementEngine, ActionExecutionEngine
- Separate validators per order category (not unified)

## Agent Configuration
**Recommended Agents:** 5
**Confirmed Agent Count:** 5

### Selected Agents
| Agent | Role | Status |
|-------|------|--------|
| order_data_model | Order Data Model Analyst — target polymorphism, serialization, categorization | Pending |
| command_pipeline | Command-to-Order Pipeline Analyst — handler uniformity, DRY, bypasses | Pending |
| execution_paths | Execution Path Analyst — 3 execution paths, dispatcher complexity | Pending |
| validation_consistency | Validation Consistency Analyst — validator patterns, coverage gaps | Pending |
| architecture_unification | Architecture & Unification Analyst — consolidation opportunities | Pending |
