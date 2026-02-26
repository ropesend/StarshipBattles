# PROJ-187: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Turn Architecture
The turn engine (`game/strategy/engine/turn_engine.py`) processes turns as 100 sub-ticks:

```
process_turn(empires, galaxy):
  1. SUBTURN LOOP (ticks 1-100):
     Phase 0:   Harvesting (1/100th per tick)
     Phase 0a:  Maintenance (1/100th per tick)
     Phase 0b:  Per-turn resource consumption
     Phase 0c:  Fuel generation at facilities
     Phase 0d:  Fleet resupply from facilities
     Phase 0e:  Construction resource consumption
     Phase 1:   Instant orders (JOIN_FLEET when co-located)
     Phase 2:   Calculate moves (FleetMovementEngine.collect_movements)
     Phase 3:   Apply moves (FleetMovementEngine.apply_movements)
     Phase 4:   Combat (ConflictResolutionEngine)

  2. END-OF-TURN ORDERS (FleetOrderProcessor.process_end_turn_orders):
     COLONIZE, TRANSFER, LOAD/UNLOAD_POP, JOIN_FLEET, superweapons

  3. POPULATION GROWTH
```

**The problem:** Movement is tick-based (fleet with speed 5 moves every 20 ticks), but all other actions execute instantly at end-of-turn. This is inconsistent — a speed-5 fleet and a speed-1 fleet colonize at the same time.

### Movement Tick Schedule
- `interval = int(100 // fleet.speed)` — ticks between moves
- Speed 5 → every 20 ticks (5 moves/turn)
- Speed 3 → every 33 ticks (3 moves/turn)
- Speed 1 → every 100 ticks (1 move/turn)
- Speed 0 → skipped entirely (stations, satellites, planetary complexes)

### Fleet Order Queue
- `Fleet.orders: List[FleetOrder]` — simple FIFO list
- `FleetOrder(order_type, target)` — no duration or progress fields
- `get_current_order()` → `orders[0]` or None
- `pop_order()` → removes first, clears path
- Order transitions happen: during movement (MOVE completes), at end-of-turn (actions execute), during instant processing (JOIN_FLEET when co-located)

### Order Types
```python
class OrderType(Enum):
    MOVE, COLONIZE, MOVE_TO_FLEET, JOIN_FLEET, BUILD, TRANSFER,
    IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT,
    CREATE_DYSON_SPHERE, SELF_DESTRUCT, LOAD_POPULATION, UNLOAD_POPULATION
```

No WARP order type exists — warp is handled transparently by `find_hybrid_path()` inside MOVE.

### Command Handler Architecture
- `CommandHandlerRegistry` with 20+ handlers dispatched by command name
- Mission handlers already auto-queue multi-step sequences (LOAD_POP → MOVE → COLONIZE)
- `_setup_mission_move()` helper adds MOVE if fleet is not at target
- All handlers in `command_handlers.py` and `superweapon_command_handlers.py`

### Component Ability Pattern
Strategic abilities use marker pattern:
- `ColonizePlanet`: string shorthand `"CONTINENTAL"` or dict `{"planet_type": "CONTINENTAL"}`
- `SuperweaponMarker` subclasses: boolean `true` or dict format
- All are `AbilityLayer.STRATEGIC`, `AbilityScope.SELF`, no stat bindings
- Loaded via `ABILITY_REGISTRY` in `abilities/__init__.py`

### Existing Precedent: Per-Tick Construction
`ProductionEngine` already does per-tick resource consumption with:
- `cost_per_tick` and `ticks_in_current_turn` on queue items
- Mid-turn completion with carry-over capacity
- This validates that tick-based execution works well in the engine

## Swarm Findings Summary

### Architecture
- **Clean DI pattern**: TurnEngine accepts all sub-engines via constructor, lazy-creates defaults
- **Delegated engines**: Each concern has its own engine class with interface
- **Pure navigation service**: `FleetNavigationService` uses stateless pure functions for both UI projection and turn execution
- **CQRS-lite**: All mutations go through command objects → handler registry → game session

### Key Patterns to Reuse
- **Lazy engine property**: `turn_engine.py:200-250` — pattern for adding new engine with optional DI
- **collect_movements interval logic**: `fleet_movement_engine.py:168-175` — reuse same interval calculation for action ticks
- **ProductionEngine per-tick pattern**: `production_engine.py:87-180` — precedent for tick-based processing
- **SuperweaponOrderProcessor delegation**: `superweapon_order_processor.py` — existing action execution methods to reuse

### Dependencies & Risks
1. **Phase 4 is the critical integration point** — `_process_end_turn_orders()` deletion + new Phase 1.5 in tick loop. Must be done atomically with test migration.
2. **46+ files reference OrderType.MOVE** — adding WARP means checking these for WARP handling needs
3. **Speed-0 edge case**: `int(100 // 0)` causes ZeroDivisionError. Movement engine already has `if fleet.speed <= 0: continue` guard. Action engine must replicate this.
4. **Fleet consumption during iteration**: When a superweapon consumes a fleet mid-tick, the empire's fleet list is modified. Must iterate copy of list.
5. **BUILD order completion**: Currently auto-popped at end-of-turn when `construction_queue` is empty. Needs new home in tick loop.

### Opportunities Discovered
- `FleetMovementEngine.collect_movements()` already skips BUILD orders — extend to skip all action orders
- `FleetOrderProcessor` individual methods (`process_colonize`, `process_transfer`, superweapons) are self-contained — can be called from ActionExecutionEngine without modification
- Navigation path projection can be enhanced to show action timing in the UI

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## New Architecture (After Refactor)

```
process_turn(empires, galaxy):
  1. SUBTURN LOOP (ticks 1-100):
     Phase 0-0e: [UNCHANGED - harvesting, maintenance, resources, production]
     Phase 1:    Instant orders (JOIN_FLEET when co-located) [UNCHANGED]
     Phase 1.5:  Action orders (ActionExecutionEngine)  ← NEW
     Phase 2:    Calculate moves [UNCHANGED]
     Phase 3:    Apply moves [UNCHANGED]
     Phase 4:    Combat [UNCHANGED]

  2. [DELETED - no more end-of-turn order processing]

  3. POPULATION GROWTH [UNCHANGED]
```

### Action Tick Contract
- Action ticks fire on the same schedule as movement: `tick % (100 // fleet.speed) == 0`
- Each action tick increments `FleetOrder.execution_progress` by 1
- When `execution_progress >= action_time`, the action executes (delegates to existing processor methods)
- `action_time` is resolved from the component ability that enables the action
- Default `action_time = 1` for any action without explicit configuration

### Order Type Categories
```python
MOVEMENT_ORDER_TYPES = frozenset({MOVE, MOVE_TO_FLEET, WARP})
ACTION_ORDER_TYPES = frozenset({COLONIZE, TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION,
                                 JOIN_FLEET, IMPLODE_PLANET, STELLERATE_STAR,
                                 OPEN_WARP_POINT, CLOSE_WARP_POINT,
                                 CREATE_DYSON_SPHERE, SELF_DESTRUCT})
# BUILD is neither — handled by ProductionEngine
```
