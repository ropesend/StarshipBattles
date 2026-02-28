# PROJ-102: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Baseline
- **7689 tests passing**, 2 pre-existing UI test failures (unrelated)
- Test command: `pytest tests/ -n 12`

### Existing Pipeline (Colonization as Pattern)
The colonization system is the closest analogy for all 7 superweapon features. It demonstrates the full pipeline:

1. **Ability** (`ColonizePlanet` in `game/simulation/components/abilities/colonize.py`)
   - Strategic marker ability: `layer = AbilityLayer.STRATEGIC`, `STAT_BINDINGS = []`
   - Accepts string or dict data format
   - Returns UI rows for display

2. **Component** (colony pods in `data/components.json`)
   - JSON entry with `"ColonizePlanet": "CONTINENTAL"` ability
   - Standard fields: id, name, type, mass, hp, abilities, resource_cost

3. **OrderType** (`COLONIZE` in `game/strategy/data/fleet.py`)
   - Enum value in `OrderType`
   - `FleetOrder(OrderType.COLONIZE, target=planet)` with serialization

4. **Commands** (`IssueColonizeCommand` + `QueueColonizeMissionCommand` in `game/strategy/engine/commands.py`)
   - Direct command (already at location) + mission command (move + execute)

5. **Command Handler** (`ColonizeCommandHandler` in `game/strategy/engine/command_handlers.py`)
   - Resolves fleet/planet, validates, creates FleetOrder(s), adds to queue
   - Registered in `create_default_registry()`

6. **Validator** (`ColonizeValidator` in `game/strategy/validation/`)
   - Static validation methods
   - Returns `ValidationResult`

7. **Order Processing** (`process_colonize()` in `game/strategy/engine/fleet_order_processor.py`)
   - Called by `process_end_turn_orders()` when fleet has COLONIZE order
   - Executes effect, consumes ship, logs event

8. **Input** (`InputAction.FLEET_COLONIZE` in `game/core/input_actions.py`)
   - Key binding in `data/default_keybindings.json`
   - Input mode `COLONIZE_TARGET` in `strategy_input_handler.py`

9. **UI Module** (`ColonizationSystem` in `game/ui/screens/strategy_colonization.py`)
   - Handles target designation clicks
   - Shows planet selection prompts
   - Issues commands via facade

10. **Events** (`EventType.COLONY_FOUNDED` in `game/strategy/events/event_types.py`)

## Architecture

### Layer Diagram
```
Input Layer (Phase 7)
  InputAction enum + KeyBindings + StrategyInputHandler
       |
UI Layer (Phase 8)
  SuperweaponOperations module + Dialogs (confirm, system picker, ship picker)
       |
Command Layer (Phase 5)
  Command dataclasses -> CommandHandlerRegistry -> Handlers
       |
Validation Layer (Phase 4)
  SuperweaponValidator - static validation methods
       |
Data Layer (Phases 1-3)
  Abilities, Components, OrderTypes, PlanetType, Galaxy methods, EventTypes
       |
Execution Layer (Phase 6)
  SuperweaponOrderProcessor - end-of-turn effects
```

### New Files Created
| File | Layer | Purpose |
|------|-------|---------|
| `game/simulation/components/abilities/superweapons.py` | Data | 6 ability classes |
| `game/strategy/validation/superweapon_validator.py` | Validation | Business rules |
| `game/strategy/engine/superweapon_command_handlers.py` | Command | 11 handlers |
| `game/strategy/engine/superweapon_order_processor.py` | Execution | Turn effects |
| `game/ui/screens/strategy_superweapons.py` | UI | Workflow module |
| `game/ui/screens/strategy_system_picker.py` | UI | System selection dialog |
| `game/ui/screens/strategy_ship_picker.py` | UI | Ship multi-select dialog |

### Modified Files
| File | Changes |
|------|---------|
| `game/simulation/components/abilities/__init__.py` | Register 6 abilities |
| `data/components.json` | Add 6 superweapon components |
| `game/strategy/data/fleet.py` | 6 OrderTypes + serialization |
| `game/strategy/data/planet.py` | PlanetType.DYSON_SPHERE |
| `game/strategy/data/galaxy.py` | unregister_planet(), remove_warp_link() |
| `game/strategy/engine/commands.py` | 11 command dataclasses |
| `game/strategy/engine/command_handlers.py` | Register in factory |
| `game/strategy/engine/fleet_order_processor.py` | Route new orders |
| `game/strategy/validation/__init__.py` | Export validator |
| `game/strategy/events/event_types.py` | 6 event types + category |
| `game/core/input_actions.py` | 6 InputAction values |
| `data/default_keybindings.json` | 6 key bindings |
| `game/ui/screens/strategy_input_handler.py` | 5 new input modes |
| `game/strategy/data/fleet_capability_calculator.py` | Generic has_ability() |

## Key Patterns to Reuse

### Strategic Marker Ability Pattern
- **Source**: `game/simulation/components/abilities/colonize.py` (ColonizePlanet)
- `layer = AbilityLayer.STRATEGIC`, `STAT_BINDINGS = []`
- Accept `true`, scalar, or dict data in `__init__`
- Implement `get_ui_rows()` and `get_primary_value() -> 0.0`

### Command Handler Pattern
- **Source**: `game/strategy/engine/command_handlers.py` (ColonizeCommandHandler)
- Resolve fleet via `session._get_fleet_by_id(cmd.fleet_id)`
- Validate via dedicated validator
- Create `FleetOrder(OrderType.X, target=...)` and add to fleet

### Mission Command Pattern (Move + Execute)
- **Source**: `game/strategy/engine/command_handlers.py` (ColonizeMissionCommandHandler)
- Calculate path via `find_hybrid_path(galaxy, start_hex, target_hex)`
- Add MOVE order first, then action order
- Set fleet.path if it's the active order

### Order Processing Pattern
- **Source**: `game/strategy/engine/fleet_order_processor.py` (process_colonize)
- Called from `process_end_turn_orders()` dispatch
- Execute effect, consume component/ship, log event
- Return result indicating if fleet was consumed

### Ability Lookup Pattern
- **Source**: `game/strategy/data/fleet_capability_calculator.py`
- Iterate ship design_data -> layers -> components -> abilities dict
- Check for ability name key

### Fleet Order Serialization Pattern
- **Source**: `game/strategy/data/fleet.py` (FleetOrder.to_dict, Fleet.from_dict)
- Use type tags: `{'type': 'superweapon', 'value': ...}`

## Dependencies & Risks

1. **Stellerate Star needs all empires** - `process_end_turn_orders()` currently receives only `(fleet, empire, galaxy)`. Must add optional `empires` parameter for STELLERATE_STAR to destroy all fleets in system.
   - **Mitigation**: Add optional `empires` param; TurnEngine already has empires in scope.

2. **Galaxy index cleanup** - Removing planets requires updating 3 indexes (`planets_by_id`, `_planet_to_system`, `_global_hex_planets`). Missing any causes stale references.
   - **Mitigation**: Create `Galaxy.unregister_planet()` method that handles all 3.

3. **Warp point bidirectionality** - Opening/closing warp points must update BOTH connected systems. Partial updates leave orphaned warp points.
   - **Mitigation**: Atomic operations that modify both systems or roll back.

4. **Self-Destruct timing** - Specified as "start of next turn", which is different from other superweapons (end of turn). Needs special handling in TurnEngine.
   - **Mitigation**: Process SELF_DESTRUCT orders at start of turn before movement.

5. **Dyson Sphere as Planet** - A Dyson Sphere is fundamentally different from a natural planet (15 hex diameter vs point). May affect rendering, hit-testing, and colonization.
   - **Mitigation**: Use PlanetType.DYSON_SPHERE for conditional logic where needed. Start with point representation (single hex) and enhance later if needed.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
