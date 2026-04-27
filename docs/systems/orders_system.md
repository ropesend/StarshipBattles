# Strategy Orders System Architecture

> **Last verified:** 2026-04-07

> **PROJ-187**: Strategy Orders Tick-Based Action System

This document describes the unified tick-based orders system for the strategy layer. All fleet orders—movement, colonization, transfers, and superweapons—execute through a consistent tick-based mechanism.

---

## Order Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORDER LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. QUEUE         User issues order via command handler         │
│       │           → Creates Order with type and target     │
│       │           → Adds to fleet.orders queue                  │
│       ▼                                                         │
│  2. WAIT          Order sits in queue until it's first          │
│       │           → Earlier orders must complete first          │
│       ▼                                                         │
│  3. TICK          Engine processes order each tick interval     │
│       │           → Movement: move one hex                      │
│       │           → Actions: increment execution_progress       │
│       ▼                                                         │
│  4. COMPLETE      Order finishes when:                          │
│       │           → Movement: path exhausted                    │
│       │           → Actions: execution_progress >= action_time  │
│       ▼                                                         │
│  5. POP           Order removed from queue                      │
│                   → Next order becomes active                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Order Data Structure

```python
class Order:
    type: OrderType           # MOVE, COLONIZE, etc.
    target: Any               # HexCoord, Planet, Fleet, or params dict
    execution_progress: int   # Ticks spent executing (0 at start)
```

**Serialization**: Only non-zero `execution_progress` is saved to keep save files clean. Orders load with `execution_progress=0` by default for backward compatibility.

---

## Turn Loop & Tick Mechanics

Each turn consists of 100 ticks. Fleet speed determines how often a fleet acts:

```
Tick Interval = 100 / fleet.speed

Examples:
- Speed 5.0 → acts every 20 ticks (ticks 20, 40, 60, 80, 100)
- Speed 10.0 → acts every 10 ticks (ticks 10, 20, 30, ...)
- Speed 2.0 → acts every 50 ticks (ticks 50, 100)
```

### Engine Responsibilities

| Engine | Orders Handled | Mechanism |
|--------|---------------|-----------|
| **FleetMovementEngine** | MOVE, MOVE_TO_FLEET, WARP | Move one hex per tick interval |
| **ActionExecutionEngine** | COLONIZE, TRANSFER, superweapons | Increment progress per tick interval |
| **ProductionEngine** | BUILD | Persistent until queue empty |

---

## Order Type Categories

Orders are categorized in `game/strategy/data/order_types.py`:

### Movement Orders (`MOVEMENT_ORDER_TYPES`)

Handled by `FleetMovementEngine`. One hex movement per tick interval.

| OrderType | Target | Behavior |
|-----------|--------|----------|
| `MOVE` | HexCoord | Path to destination, stop at warp points |
| `MOVE_TO_FLEET` | Fleet | Path to fleet's current location |
| `WARP` | HexCoord (warp exit) | Single-tick warp traversal |

### Action Orders (`ACTION_ORDER_TYPES`)

Handled by `ActionExecutionEngine`. Progress accumulates until `action_time` reached.

| OrderType | Target | action_time Source |
|-----------|--------|-------------------|
| `COLONIZE` | Planet | Default (1). Only deploys pod and claims planet. Population/cargo transferred via explicit TRANSFER orders. Drop pod deployed from `ship.carried_items`; full design becomes `PlanetaryFacility`. Ship stays in fleet. |
| `TRANSFER` | params dict | Default (1) |
| `LOAD_POPULATION` | params dict | Default (1). Explicit order issued by the player via the transfer dialog (not auto-inserted). |
| `UNLOAD_POPULATION` | params dict | Default (1) |
| `IMPLODE_PLANET` | Planet | DestroyPlanet ability |
| `STELLERATE_STAR` | (none) | DestroyStar ability |
| `OPEN_WARP_POINT` | warp params | OpenWarpPoint ability |
| `CLOSE_WARP_POINT` | WarpPoint | CloseWarpPoint ability |
| `CREATE_DYSON_SPHERE` | (none) | CreateDysonSphere ability |
| `SELF_DESTRUCT` | ship IDs | SelfDestruct ability |

### Instant Orders

| OrderType | Behavior |
|-----------|----------|
| `JOIN_FLEET` | Processed instantly by `OrderProcessor` (not tick-based); merges fleet into target fleet |

### Planet Action Orders (`PLANET_ACTION_ORDER_TYPES`)

Handled by `PlanetActionEngine`. All consecutive planet action orders dispatch instantly
on the same tick (zero-tick dispatch). Processing stops at the first non-planet-action
order in the queue. This ensures multiple activations queued on the same turn all begin
with equal progress.

| OrderType | Target | Behavior |
|-----------|--------|----------|
| `ACTIVATE_ABILITY` | ability name | Activates a planetary ability (e.g., PlanetaryShield) |
| `DEACTIVATE_ABILITY` | ability name | Deactivates a planetary ability |

These are generic ability toggles issued via the planet orders UI. Both Fleet and Planet
implement the `IOrderable` protocol, so the unified `Order` class is used for both.

### Special: BUILD Order

- **Not** in either category
- Handled by `ProductionEngine` independently
- Persists until `fleet.construction_queue` is empty
- Auto-pops when queue empties

---

## Action Time Resolution

`ActionTimeResolver` looks up `action_time` from component abilities:

```python
# Mapping from OrderType to ability name
OrderType.COLONIZE       → 'ColonizePlanet'
OrderType.IMPLODE_PLANET → 'DestroyPlanet'
OrderType.STELLERATE_STAR → 'DestroyStar'
OrderType.OPEN_WARP_POINT → 'OpenWarpPoint'
OrderType.CLOSE_WARP_POINT → 'CloseWarpPoint'
OrderType.CREATE_DYSON_SPHERE → 'CreateDysonSphere'
OrderType.SELF_DESTRUCT → 'SelfDestruct'
```

### Resolution Algorithm

1. Get ability name for OrderType
2. Search fleet ships for first component with that ability
3. Extract `action_time` from ability data
4. Default to 1 if not found

### Ability Data Formats

```json
// Dict with action_time (superweapons)
"DestroyPlanet": {"action_time": 3}

// String shorthand (colony pods) → defaults to 1
"ColonizePlanet": "CONTINENTAL"

// Boolean marker → defaults to 1
"SomeAbility": true
```

---

## Moddability via components.json

Action times are defined on component abilities in `data/components.json`:

```json
{
    "id": "stellar_converter",
    "name": "Stellar Converter",
    "abilities": {
        "DestroyStar": {"action_time": 5}
    }
}
```

**Current action_time values:**

| Ability | action_time | Ticks at Speed 5 |
|---------|-------------|------------------|
| ColonizePlanet | 1 (default) | 20 ticks |
| DestroyPlanet | 3 | 60 ticks |
| DestroyStar | 5 | 100 ticks |
| OpenWarpPoint | 3 | 60 ticks |
| CloseWarpPoint | 3 | 60 ticks |
| CreateDysonSphere | 5 | 100 ticks |
| TRANSFER | 1 (default) | 20 ticks |

---

## Execution Progress Tracking

`execution_progress` on `Order` tracks ticks spent on current action:

```
Turn 1, Tick 20: COLONIZE order, progress 0 → 1
Turn 1, Tick 40: COLONIZE order, progress 1 → 2
Turn 1, Tick 60: COLONIZE order, progress 2 >= action_time(2) → EXECUTE
```

### Progress Persistence

- Only saved when `> 0` (keeps saves clean)
- Loads with default `0` for backward compatibility
- **Discarded** when orders cleared (`ClearOrdersCommandHandler`)

---

## WARP vs MOVE Distinction

| Aspect | MOVE | WARP |
|--------|------|------|
| Purpose | General pathfinding | Explicit warp traversal |
| Stops at warp? | Yes, auto-stops | No, executes traversal |
| Path length | Multi-hex | Single step |
| Resource cost | Per-hex fuel | Per-jump warp cost |
| When generated | User destination | Manual or auto-queued |

### Auto-Queuing WARP

When a MOVE order's path reaches a warp point, the movement engine:
1. Stops at the warp point hex
2. Completes the MOVE order
3. Command handlers may auto-queue: `WARP` → `MOVE` to continue

---

## Timing Diagrams

### Example: Colonization with Speed 5 Fleet

```
Turn 1:
  Tick  0: Turn starts
  Tick 20: TRANSFER (load population/cargo from colony) → COMPLETE
  Tick 40: MOVE (move 1 hex)
  Tick 60: MOVE (move 1 hex)
  Tick 80: MOVE (move 1 hex)
  Tick 100: MOVE (move 1 hex)

Turn 2:
  Tick 20: MOVE (arrive at planet)
  Tick 40: COLONIZE (progress 0→1, action_time=1) → COMPLETE → Colony founded!
  Tick 60: TRANSFER (unload population/cargo to new colony) → COMPLETE
```

**Typical colonization order chain:** `TRANSFER(load)` → `MOVE` → `COLONIZE` → `TRANSFER(unload)`

### Example: Superweapon with Speed 5 Fleet

```
Turn 1:
  Tick 20: STELLERATE_STAR (progress 0→1, action_time=5)
  Tick 40: STELLERATE_STAR (progress 1→2)
  Tick 60: STELLERATE_STAR (progress 2→3)
  Tick 80: STELLERATE_STAR (progress 3→4)
  Tick 100: STELLERATE_STAR (progress 4→5) → COMPLETE → Star explodes!
```

### Example: Cancelled Mid-Progress

```
Turn 1:
  Tick 20: STELLERATE_STAR (progress 0→1)
  Tick 40: STELLERATE_STAR (progress 1→2)

User clears orders → execution_progress DISCARDED

Turn 2:
  (Fleet has no orders, star survives)
```

---

## Order Editing (UI)

**File:** `game/ui/screens/orders_window.py`

The Orders Window shows an "E" (Edit) button on order rows whose type is in
`EDITABLE_ORDER_TYPES`:

| Editable Type | Edit Action |
|---------------|------------|
| `MOVE` | Enters `EDIT_MOVE` input mode: camera pans to old destination, yellow ghost hex outline shows the original target, player clicks new destination, order target updates in-place |
| `TRANSFER` | Removes the old order, opens the Transfer Dialog at the resolved transfer location (determined by walking preceding MOVE/WARP orders), player creates replacement order(s) |
| `LOAD_POPULATION` | Same as TRANSFER |
| `UNLOAD_POPULATION` | Same as TRANSFER |

### EDIT_MOVE Flow

1. Player clicks "E" on a MOVE order row
2. `StrategyScreen._start_edit_move()` stores the old hex as ghost state, pans camera
3. `StrategyRenderer` draws ghost hex outline (yellow) and preview line to cursor
4. Player clicks new destination → `complete_edit_move()` updates `order.target` in-place
5. If editing the active order (index 0), `fleet.path` is invalidated
6. Right-click or ESC cancels edit, restoring SELECT mode

### EDIT_TRANSFER Flow

1. Player clicks "E" on a TRANSFER/LOAD/UNLOAD order row
2. `StrategyScreen._start_edit_transfer()` walks preceding orders to find the hex
   where this transfer will execute
3. Old order is removed from the queue
4. Transfer Dialog opens at the resolved hex — player creates replacement order(s)

**Key files:**
- `game/ui/screens/orders_window.py` — E button, `EDITABLE_ORDER_TYPES`
- `game/ui/screens/strategy_screen.py` — `on_edit_order()`, `_start_edit_move()`, `complete_edit_move()`, `_start_edit_transfer()`
- `game/ui/screens/strategy_click_dispatcher.py` — `EDIT_MOVE` click handler
- `game/ui/screens/strategy_renderer.py` — ghost hex rendering
- `game/ui/screens/strategy_fleet_command_router.py` — ESC cancel for EDIT_MOVE

---

## Adding a New Order Type

Follow these steps to add a new order type to the system:

### 1. Add to OrderType Enum

```python
# game/strategy/data/order_types.py
class OrderType(Enum):
    MOVE = auto()
    # ... existing types ...
    YOUR_NEW_ORDER = auto()  # Add here
```

### 2. Categorize as Movement or Action

```python
# game/strategy/data/order_types.py
# Movement orders (one hex per tick)
MOVEMENT_ORDER_TYPES: frozenset = frozenset({
    OrderType.MOVE,
    OrderType.MOVE_TO_FLEET,
    OrderType.WARP,
    # OrderType.YOUR_NEW_ORDER,  # If movement-based
})

# Action orders (progress-based)
ACTION_ORDER_TYPES: frozenset = frozenset({
    OrderType.COLONIZE,
    # ... existing ...
    # OrderType.YOUR_NEW_ORDER,  # If progress-based
})
```

### 3. Define action_time (for Action Orders)

Option A: Default (1 tick interval)
- No changes needed, defaults to 1

Option B: Ability-based
```python
# game/strategy/services/action_time_resolver.py
# Add to the module-level constant:
ORDER_TO_ABILITY_MAP = {
    # ... existing ...
    OrderType.YOUR_NEW_ORDER: 'YourAbilityName',
}
```

Then in `data/components.json`:
```json
{
    "id": "your_component",
    "abilities": {
        "YourAbilityName": {"action_time": 2}
    }
}
```

### 4. Add Processing Method

For action orders, add to `OrderProcessor` or `SuperweaponOrderProcessor`:

```python
def process_your_new_order(self, fleet, empire, galaxy, ...):
    """Process YOUR_NEW_ORDER."""
    order = fleet.get_current_order()
    if not order or order.type != OrderType.YOUR_NEW_ORDER:
        return YourResult(success=False)

    # Validate
    # Execute
    # Pop order
    fleet.pop_order()
    return YourResult(success=True)
```

Wire into `execute_action_order()`:
```python
elif order.type == OrderType.YOUR_NEW_ORDER:
    result = self.process_your_new_order(fleet, empire, galaxy)
    return result.some_consumed_flag
```

### 5. Add Command Handler

```python
# game/strategy/engine/command_handlers.py
class YourNewOrderCommandHandler(BaseCommandHandler):
    def execute(self, session: 'GameSession', cmd: 'YourNewOrderCommand') -> ValidationResult:
        # 1. Resolve fleet
        fleet, error = self._resolve_fleet(session, cmd.fleet_id)
        if error:
            return error
        # 2. Validate
        # 3. Create order
        order = Order(OrderType.YOUR_NEW_ORDER, target=...)
        fleet.add_order(order)
        return ValidationResult.success()
```

Register in `create_default_registry()`:
```python
registry.register('YourNewOrderCommand', YourNewOrderCommandHandler())
```

### 6. Add Tests

- Unit tests for the processing method
- Integration tests for command handler
- Tick timing tests if complex action_time

---

## Key Files

| Component | File |
|-----------|------|
| OrderType enum | `game/strategy/data/order_types.py` |
| Order class | `game/strategy/data/order_types.py` |
| Order categories | `game/strategy/data/order_types.py` |
| ActionExecutionEngine | `game/strategy/engine/action_execution_engine.py` |
| ActionTimeResolver | `game/strategy/services/action_time_resolver.py` |
| OrderProcessor | `game/strategy/engine/order_processor.py` |
| FleetMovementEngine | `game/strategy/engine/fleet_movement_engine.py` |
| SuperweaponOrderProcessor | `game/strategy/engine/superweapon_order_processor.py` |
| Command Handlers | `game/strategy/engine/command_handlers.py` |
| Superweapon Handlers | `game/strategy/engine/superweapon_command_handlers.py` |
| Component abilities | `data/components.json` |
| Orders Window (UI) | `game/ui/screens/orders_window.py` |
| Fleet Position Projection | `game/strategy/services/cargo_transfer_service.py` (`project_fleet_position()`) |

---

## Design Rationale

### Why Unified Tick-Based Execution?

1. **Predictability**: All actions follow the same timing model
2. **Moddability**: Action durations controlled via data files
3. **Fairness**: Same fleet acts at same intervals regardless of order type
4. **Interruptibility**: Multi-tick actions can be cancelled mid-progress
5. **Simplicity**: One loop, one model, one set of rules

### Why execution_progress on Order?

1. **State locality**: Progress belongs to the order being executed
2. **Clean cancellation**: Clearing orders discards progress automatically
3. **Serialization**: Progress survives save/load
4. **UI feedback**: Can show progress bars for long actions

### Why Separate Movement and Action Engines?

1. **Different mechanics**: Movement consumes path hexes; actions consume progress
2. **Different resources**: Movement uses fuel; actions may use nothing
3. **Single responsibility**: Each engine does one thing well
4. **Testability**: Can test movement and action logic independently
