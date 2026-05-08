# Orders System Compact Reference

> Last verified: 2026-05-07 - compared `docs/systems/orders_system.md`, `AgentCoordination/Scratchpad/reports/systems_orders_system_ALT_compact.md`, and current strategy order source files.

Audience: agents working on the strategy-layer orders system. This is a compact replacement: keep current contracts, paths, invariants, extension recipes, and tests; omit release-note archaeology.

## System Scope

The strategy orders system uses one `Order` model for fleet and planet queues. Fleet orders cover movement, joins, colonization, transfers, construction, and superweapons. Planet orders currently use generic ability toggles.

Core model: `game/strategy/data/order_types.py`

```python
class Order:
    type: OrderType
    target: Any
    execution_progress: int
```

`execution_progress` counts completed fleet action intervals for the active order. It is serialized only when greater than zero and defaults to `0` when absent. Clearing or removing an order discards its progress. Planet ability orders are different: they dispatch instantly into `ComponentActivationState`, and `ComponentActivationEngine` ticks the activation timer afterward.

Both fleets and planets are orderable through the shared queue shape. Use the current names directly: `Order`, `OrderType`, `OrderProcessor`, `OrderSerializer`, and `OrdersWindow`. Old `FleetOrder`, `PlanetOrderType`, `FleetOrderProcessor`, `FleetOrderSerializer`, and `FleetOrdersWindow` compatibility names are deleted.

## Lifecycle

1. Queue: command handlers create `Order(type, target)` and append it to `orders`.
2. Wait: only the queue head is active; later orders do nothing.
3. Tick: the active order is processed by the owning engine at its cadence.
4. Complete: movement completes when its path is exhausted; fleet actions complete when `execution_progress >= action_time`; planet toggles complete when dispatched.
5. Pop: the completed order is removed and the next queued order becomes active.

Fleet action cadence:

```text
TICKS_PER_TURN = 100
tick_interval = max(1, int(100 // fleet.speed))
```

Examples: speed `5.0` acts on ticks `20, 40, 60, 80, 100`; speed `10.0` acts every 10 ticks; speed `2.0` acts on ticks `50, 100`. Fleets with speed `<= 0` do not act in movement/action engines.

Relevant turn phases are data-driven in `game/strategy/engine/turn_phase_registry.py` and executed by `TurnEngine._run_phases()`:

| Phase | Key | Contract |
|---|---|---|
| 0e | `production` | Construction queues tick before orders. |
| 1 | `instant_orders` | `JOIN_FLEET` batch processing. |
| 1.5 | `actions` | Fleet action orders: colonize, transfer, superweapons. |
| 1.6 | `planet_actions` | Planet ability toggle orders dispatch and pop. |
| 1.7 | `activation_timers` | Component activation/deactivation timers advance. |
| 1.8 | `planet_modifier_effects` | Active planet modifier effects apply after timers. |
| 2/3 | `movement_calc` / `movement_apply` | Movement runs after action phases. |
| 4 | `combat` | Conflicts resolve after movement. |

## Processing Contracts

| Engine or service | Contract |
|---|---|
| `game/strategy/engine/fleet_movement_engine.py` | Handles `MOVE`, `MOVE_TO_FLEET`, `WARP`; skips `ACTION_ORDER_TYPES` and `BUILD`; moves one step per eligible tick except warp traversal. |
| `game/strategy/engine/action_execution_engine.py` | Handles fleet action orders; increments `execution_progress`; delegates completed actions to `OrderProcessor.execute_action_order()`. |
| `game/strategy/engine/order_processor.py` | Thin facade over `game.strategy.engine.order_handlers`; keeps legacy public methods only as shims for tests/callers. |
| `game/strategy/engine/order_handlers/` | Canonical per-`OrderType` action/instant execution handlers. |
| `game/strategy/engine/planet_action_engine.py` | Dispatches consecutive planet ability orders instantly and creates activation/deactivation state. |
| `game/strategy/engine/component_activation_engine.py` | Ticks component activation state each turn tick. |
| `game/strategy/engine/production_engine.py` | Handles construction queues; `BUILD` persists until the fleet queue empties. |

`BUILD` is not in `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, or `PLANET_ACTION_ORDER_TYPES`. The action engine only auto-pops `BUILD` when `fleet.construction_queue` is empty.

## Order Categories

Definitions and frozensets live in `game/strategy/data/order_types.py`. The self-registering command metadata in `game/strategy/engine/commands/registry.py` is the canonical declaration of command category, but the frozensets stay as plain constants to keep `game.strategy.data` a leaf package. `tests/unit/strategy/engine/test_command_specs_contract.py` pins equality between the constants and the registry-derived views.

### Movement Orders

`MOVEMENT_ORDER_TYPES`

| Type | Target | Behavior |
|---|---|---|
| `MOVE` | `HexCoord` | Pathfinds to destination and stops at warp points. |
| `MOVE_TO_FLEET` | `Fleet` | Pursues the target fleet's current location. |
| `WARP` | `HexCoord` warp point sector | Explicit warp traversal. |

### Fleet Action Orders

`ACTION_ORDER_TYPES - PLANET_ACTION_ORDER_TYPES`

| Type | Target | Execution handler |
|---|---|---|
| `COLONIZE` | `Planet`, `None`, or colonize params dict | `order_handlers/colonize.py` |
| `TRANSFER` | params dict | `order_handlers/transfer.py` |
| `LOAD_POPULATION` | params dict | same `TransferHandler` instance as `TRANSFER` |
| `UNLOAD_POPULATION` | params dict | same `TransferHandler` instance as `TRANSFER` |
| `IMPLODE_PLANET` | `Planet` | `SuperweaponHandlerAdapter` -> `SuperweaponOrderProcessor` |
| `STELLERATE_STAR` | `None` | `SuperweaponHandlerAdapter` -> `SuperweaponOrderProcessor` |
| `OPEN_WARP_POINT` | warp params dict | `SuperweaponHandlerAdapter` -> `SuperweaponOrderProcessor` |
| `CLOSE_WARP_POINT` | warp params dict | `SuperweaponHandlerAdapter` -> `SuperweaponOrderProcessor` |
| `CREATE_DYSON_SPHERE` | `None` | `SuperweaponHandlerAdapter` -> `SuperweaponOrderProcessor` |
| `SELF_DESTRUCT` | ship id list | `order_handlers/self_destruct.py` |

`OrderHandlerRegistry` must register every fleet action order plus `JOIN_FLEET`, excluding planet-only actions. The completeness gate is `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`.

### Instant Orders

| Type | Behavior |
|---|---|
| `JOIN_FLEET` | Queued after `MOVE_TO_FLEET`, processed during `instant_orders` when fleets are co-located; not progress-based. |

### Planet Action Orders

`PLANET_ACTION_ORDER_TYPES` is a subset of `ACTION_ORDER_TYPES`:

| Type | Target | Behavior |
|---|---|---|
| `ACTIVATE_ABILITY` | dict with `facility_instance_id`, `ability_name`, optional `component_key` | Starts component activation state. |
| `DEACTIVATE_ABILITY` | same target shape | Starts deactivation or cancels an in-progress activation. |

These are deliberately not registered in `OrderHandlerRegistry`. `PlanetActionEngine` handles them and stops processing at the first non-planet-action order, so all consecutive ability toggles queued for the same tick start with equal activation timing.

## Command Dispatch

Command DTOs live in `game/strategy/engine/commands/__init__.py`. Runtime command handlers live mostly under `game/strategy/engine/handlers/`, with current holdouts in `game/strategy/engine/planet_command_handlers.py` and `game/strategy/engine/superweapon_command_handlers.py`.

Canonical metadata: `game/strategy/engine/commands/registry.py`

- `@command_spec(...)` is metadata-only. It attaches `__command_spec_kwargs__` and must not register at import time.
- Each handler module exposes `register(registry)` and builds `CommandSpec(handler_class=..., **metadata)`.
- `seed_default_commands(command_registry)` imports handler modules and calls their `register()` functions.
- `game/strategy/engine/handlers/registry_factory.py::create_default_registry()` builds the runtime `CommandHandlerRegistry` from `command_registry.all()`.

Stale path correction: `game/strategy/engine/commands/specs.py` was deleted. Do not add entries there. `game/strategy/engine/command_handlers.py` is a transitional re-export shim for the decomposed `handlers/` package; do not add new symbols to the shim.

Command authorization invariant: command DTOs do not carry trusted empire identity. Fleet and planet handlers resolve ownership from `session.active_empire` through `_resolve_player_fleet()` / `_resolve_player_planet()`.

## Action Execution Dispatch

`OrderProcessor` constructs `create_default_order_handler_registry()` and delegates all execution through registry lookup:

| Handler | Registered order types |
|---|---|
| `JoinFleetHandler` | `JOIN_FLEET` |
| `ColonizeHandler` | `COLONIZE` |
| `TransferHandler` | `TRANSFER`, `LOAD_POPULATION`, `UNLOAD_POPULATION` |
| `SelfDestructHandler` | `SELF_DESTRUCT` |
| `SuperweaponHandlerAdapter` | the 5 `SUPERWEAPONS` specs |

Internal handlers return `OrderExecutionResult`; `OrderProcessor` reshapes a few public facade methods back into legacy result dataclasses (`JoinFleetResult`, `ColonizeResult`, `TransferResult`) for existing tests/callers.

Do not reintroduce central `elif order.type == ...` dispatch in `OrderProcessor`. Add a handler and register it in `game/strategy/engine/order_handlers/registry_factory.py`.

## Action Time Resolution

Resolver: `game/strategy/services/action_time_resolver.py`

`ORDER_TO_ABILITY_MAP` is derived from `command_registry.order_to_ability_map()`, which reads `action_ability_name` from `@command_spec` metadata. For new fleet actions, set `action_ability_name` on the command spec instead of editing `ORDER_TO_ABILITY_MAP` by hand.

Fleet action lookup:

1. Get ability name from `ORDER_TO_ABILITY_MAP`.
2. Walk ships and design components with `iterate_design_components(...)`.
3. Read `action_time` from the first matching ability dict.
4. Default to `1` when no ability or numeric time is found.

Planet toggle lookup:

1. Read `ability_name` from `order.target`.
2. Use `activation_time` for `ACTIVATE_ABILITY` or `deactivation_time` for `DEACTIVATE_ABILITY`.
3. Search the target facility's operational components.
4. Default to `1` if the time cannot be resolved.

Ability data examples:

```json
"DestroyPlanet": {"action_time": 3}
"ColonizePlanet": true
"PlanetaryShield": {"activation_time": 50, "deactivation_time": 10, "energy_drain_rate": 25.0}
```

Current component-driven durations in `data/components.json`:

| Ability/order | Current duration |
|---|---:|
| `ColonizePlanet` | `1` default |
| `DestroyPlanet` | `3` action intervals |
| `DestroyStar` | `5` action intervals |
| `OpenWarpPoint` | `3` action intervals |
| `CloseWarpPoint` | `3` action intervals |
| `CreateDysonSphere` | `5` action intervals |
| `SelfDestruct` | `1` default |
| `TRANSFER` / population transfer | `1` default |

At fleet speed 5, one progress increment is 20 ticks, so action times 3 and 5 consume 60 and 100 ticks respectively.

## Serialization

Simple `Order.to_dict()` lives on `Order`; fleet save/load reference resolution lives in `game/strategy/data/order_serializer.py::OrderSerializer`.

Supported target codecs:

| Codec | Shape | Used by |
|---|---|---|
| `hex_coord` | `{"q": q, "r": r}` | `MOVE`, `WARP` |
| `fleet_ref` | `{"type": "fleet_ref", "id": id}` | `MOVE_TO_FLEET`, `JOIN_FLEET` |
| `planet_ref` | `{"type": "planet_ref", "id": id}` | `COLONIZE`, `IMPLODE_PLANET` |
| `colonize_params` | planet id plus population/cargo amounts | colonize targets with explicit amounts |
| `transfer` | `{"type": "transfer", "value": {...}}` | transfer family |
| `warp_params` | `{"type": "warp_params", "value": {...}}` | open/close warp point |
| `ship_id_list` | `{"type": "ship_id_list", "value": [...]}` | `SELF_DESTRUCT` |
| `dict` / raw fallback | direct marker dict or string fallback | planet orders and unknown shapes |

`OrderSerializer.deserialize_orders()` is strict: corrupt entries raise `PersistenceException` with `ErrorCode.CORRUPT_DATA`. After deserialization, unresolved fleet/planet references are removed from the order queue with a warning. Do not add save-file migrations; old saves are disposable.

## Movement and Warp Invariants

- Use sector precision (`HexCoord`) for order targets. A star system contains many sectors; validating only "same system" is not enough for warp points, planets, or execution locations.
- `MOVE` is general pathfinding. It consumes movement resources, may span many sectors, and stops at warp points.
- `WARP` is explicit traversal. It consumes warp resources and represents the jump itself.
- `IssueWarpCommand` queues an auto-`MOVE` to the warp point when needed, then queues `WARP`.
- `add_move_order_if_needed()` is chain-aware: if there are existing `MOVE` orders, it starts from the last `MOVE` target rather than the fleet's current sector.
- `MOVE_TO_FLEET` and `JOIN_FLEET` register pursuers on the target fleet so removals/merges can redirect or cancel stale orders.
- `FleetMovementEngine._filter_jump_past_collisions()` prevents mutual-pursuit fleets from swapping past each other forever; the larger fleet delays, with smaller id as the tie-breaker.

## Join Fleet Contract

Implementation: `game/strategy/engine/order_handlers/join_fleet.py`

`JoinFleetHandler.process_instant_orders()` runs a three-phase batch:

1. Collect `(empire, source, target)` candidates for co-located fleets whose head order is `JOIN_FLEET`.
2. Canonicalize mutual `A<->B` pairs into one deterministic merge: most ships wins, smaller id breaks ties.
3. Execute with re-validation that both source and target are still present in `empire.fleets`.

Cycles of three or more are not pre-collapsed; per-candidate aliveness checks decide which merge wins and which candidates skip. This prevents writing ships into stale fleet references after an earlier merge absorbed either side.

Structured `FLEET_JOIN_CANCELLED` reasons:

| Reason | Emitter | Meaning |
|---|---|---|
| `absorbed_by_other_merge` | `JoinFleetHandler` | Source was already absorbed earlier in the same tick. |
| `target_absorbed_mid_iteration` | `JoinFleetHandler` | Target was already absorbed; stale source order is popped. |
| `self_target_after_redirect` | `Fleet.merge_with` | Redirecting pursuers would create a self-targeting join; stale pursuit orders are dropped. |
| unstructured | `Empire.remove_fleet` | Target fleet was removed/destroyed; pursuer orders are cancelled. |

`Fleet.merge_with()` must exclude the absorbing fleet from pursuer redirection. Otherwise the absorbing fleet can become a pursuer of itself on the next tick.

## Colonization and Transfer

`ColonizeHandler` validates with `ColonizeValidator`, claims the final planet, pops the order, and deploys a carried drop pod as a `PlanetaryFacility`. Population and cargo are not moved by colonization; they require explicit transfer orders. The ship carrying the pod stays in the fleet. Drop-pod removal and facility addition route through mutator services.

Current warning: `ColonizeHandler` requires `component_registry`. If missing, it logs, pops the order, and returns failure for backward compatibility. New call sites should pass registries instead of relying on that behavior.

Transfer target params:

```python
{
    "direction": "load" | "unload",
    "cargo_type": "passengers" | "drop_pod" | resource_id,
    "amount": int,
    "planet_id": int | None,
    "target_fleet_id": int | None,
    "species_id": str | None,
}
```

`TransferCommandHandler` supports fleet-to-planet and fleet-to-fleet transfer. Fleet-to-fleet transfer must preserve `target_fleet_id` in the order target so `TransferHandler` can resolve the destination at execution time. `LOAD_POPULATION` with no target auto-resolves an owned populated colony at the fleet's current sector and skips as a successful no-op if none exists.

## Planet Ability Orders

Command handler: `game/strategy/engine/planet_command_handlers.py::IssuePlanetOrderCommandHandler`

Validation uses `PlanetOrderValidator`, and facility ability checks must use registry-backed component lookup. Facility `design_data` stores component ids; abilities live in `data/components.json`. Do not check only inline `comp["abilities"]`, or loaded designs will silently miss abilities.

Order target keys:

| Key | Purpose |
|---|---|
| `facility_instance_id` | Facility being activated/deactivated. |
| `ability_name` | Generic ability name, e.g. `PlanetaryShield`. |
| `component_key` | Preferred precise component target: `LAYER:INDEX:COMP_ID`. |
| `component_id` | Legacy component identifier when available. |

`PlanetActionEngine` cancels an order if its target facility no longer exists. Activation starts only from `INACTIVE`; deactivation cancels `ACTIVATING` immediately or starts a timer from `ACTIVE`.

## UI Order Editing

Orders UI file: `game/ui/screens/orders_window.py`

`EDITABLE_ORDER_TYPES`:

| Type | Edit behavior |
|---|---|
| `MOVE` | Enters `EDIT_MOVE`; old destination is shown as a yellow ghost hex; click updates `order.target` in place. If editing index 0, fleet path is invalidated through `fleet_mutator`. |
| `TRANSFER` | Removes old order and opens Transfer Dialog at the projected execution sector. |
| `LOAD_POPULATION` | Same as `TRANSFER`. |
| `UNLOAD_POPULATION` | Same as `TRANSFER`. |

Relevant files:

| Responsibility | File/API |
|---|---|
| Row descriptions and editable set | `game/ui/screens/orders_window.py` |
| Window control callbacks | `game/ui/screens/strategy_windows/orders_window_ctrl.py` |
| Edit state transitions | `game/ui/screens/strategy_screen_order_editing.py` |
| StrategyScreen delegation methods | `game/ui/screens/strategy_screen.py::on_edit_order`, `complete_edit_move`, `_start_edit_transfer` |
| `EDIT_MOVE` click handling | `game/ui/screens/strategy_click_dispatcher.py` |
| Ghost hex rendering | `game/ui/screens/strategy_renderer.py` |
| ESC/right-click cancel | `game/ui/screens/strategy_fleet_command_router.py` |
| Projected transfer location | `game/strategy/services/cargo_transfer_service.py::project_fleet_position` |

## Key Files

| Concern | File |
|---|---|
| Order enum, model, category constants | `game/strategy/data/order_types.py` |
| Order save/load reference resolution | `game/strategy/data/order_serializer.py` |
| Command DTOs | `game/strategy/engine/commands/__init__.py` |
| Command metadata registry | `game/strategy/engine/commands/registry.py` |
| Runtime command handler registry | `game/strategy/engine/handlers/registry_factory.py` |
| Command handler infrastructure | `game/strategy/engine/handlers/base.py` |
| Movement command handlers | `game/strategy/engine/handlers/movement.py` |
| Transfer command handler | `game/strategy/engine/handlers/transfer.py` |
| Planet command handlers | `game/strategy/engine/planet_command_handlers.py` |
| Superweapon command handlers | `game/strategy/engine/superweapon_command_handlers.py` |
| Fleet action tick loop | `game/strategy/engine/action_execution_engine.py` |
| Fleet movement | `game/strategy/engine/fleet_movement_engine.py` |
| Order execution facade | `game/strategy/engine/order_processor.py` |
| Per-order execution handlers | `game/strategy/engine/order_handlers/` |
| Superweapon specs | `game/strategy/services/superweapon_registry.py` |
| Action duration lookup | `game/strategy/services/action_time_resolver.py` |
| Planet ability order dispatch | `game/strategy/engine/planet_action_engine.py` |
| Activation timer engine | `game/strategy/engine/component_activation_engine.py` |
| Component ability data | `data/components.json` |
| Orders window | `game/ui/screens/orders_window.py` |

## Extension Recipes

Use strict TDD for code changes: write or identify a failing test first, run it to confirm failure, then implement the smallest root-cause change.

### Add a Normal Fleet Order

1. Add the `OrderType` member in `game/strategy/data/order_types.py`.
2. Add it to the correct category constant. If command metadata should derive the same category, update both surfaces and let `test_command_specs_contract.py` pin equality.
3. Add or update a command DTO in `game/strategy/engine/commands/__init__.py`.
4. Add a command handler in the appropriate `game/strategy/engine/handlers/` module, or create a new module with `@command_spec(...)` and `register(registry)`. If it is a new module, add it to `seed_default_commands()`.
5. For action-time lookup, set `action_ability_name` in `@command_spec`. Do not manually edit `ORDER_TO_ABILITY_MAP`.
6. Add fleet execution logic as an `IOrderHandler` under `game/strategy/engine/order_handlers/` and register it in `create_default_order_handler_registry()`. Skip this only for orders owned by a dedicated engine such as `BUILD` or planet ability toggles.
7. Add serializer support if the target shape is new.
8. Add or update facade/UI dispatch helpers if the player can issue the command.
9. Add component data in `data/components.json` if the order is ability-driven.
10. Add tests for command creation/validation, execution, category/registry contracts, serialization, and tick timing when speed or `action_time` matters.

### Add a Strategic Superweapon

1. Add a direct command and any mission command DTOs.
2. Add command handlers with `category='superweapon'`, `execution_model='action'` or `'mission'`, and `action_ability_name` for action-time lookup.
3. Add a `SuperweaponSpec` row in `game/strategy/services/superweapon_registry.py` unless the weapon is structurally outside the spec-driven superweapon path like `SELF_DESTRUCT`.
4. Implement the effect on `SuperweaponOrderProcessor` and ensure `build_superweapon_handlers()` adapts it.
5. Add validator coverage, stabilizer behavior if blockable, event payload tests, order-handler registry completeness, and integration tests.

### Add a Planet Ability Toggle

Usually do not add a new `OrderType`. Use `ACTIVATE_ABILITY` / `DEACTIVATE_ABILITY` with `ability_name`, `facility_instance_id`, and preferably `component_key`. Add ability data fields (`activation_time`, `deactivation_time`, `energy_drain_rate`) to component data and extend `PlanetOrderValidator` only if the validation contract changes.

## Test Commands

Primary commands:

```bash
pytest tests/ --testmon
python Tools/test_sharded/test_sharded.py
```

Focused order-system checks:

```bash
pytest tests/unit/strategy/data/test_order_types_characterization.py
pytest tests/unit/strategy/data/test_order_serializer.py
pytest tests/unit/strategy/engine/test_command_registry_seeding.py
pytest tests/unit/strategy/engine/test_command_specs_contract.py
pytest tests/unit/strategy/engine/test_no_specs_tuple_literal.py
pytest tests/unit/strategy/engine/order_handlers/
pytest tests/unit/strategy/engine/test_action_execution_engine.py
pytest tests/unit/strategy/engine/test_planet_action_engine.py
pytest tests/unit/strategy/services/test_action_time_resolver.py
pytest tests/integration/save_load/test_roundtrip_orders.py
pytest tests/integration/strategy/test_warp_orders.py
pytest tests/integration/colonization/test_explicit_orders.py
```

## Design Invariants

- One order queue per orderable entity; only the head order is active.
- Fleet movement and fleet actions share speed-based cadence.
- Movement consumes path steps; fleet actions consume `execution_progress`.
- Planet action orders dispatch instantly; component activation timers are separate state.
- Action duration should come from command metadata plus component ability data, not hardcoded type lists.
- Fleet and planet order validation must use precise sectors (`HexCoord`) for target locations.
- Command handlers must authorize from `session.active_empire`, not request-body identity.
- Facility ability checks must use registry lookup for loaded designs.
- Long fleet actions are interruptible by clearing/removing orders.
- Save/load preserves meaningful in-progress fleet actions without writing default progress noise.
- New order behavior should use registries, protocols, and handlers; avoid fallback aliases, monkey patches, and central string/type lists.

## Stale References Fixed

- `game/strategy/engine/commands/specs.py` no longer exists; use `commands/registry.py`.
- `COMMAND_SPECS` is now `tuple(command_registry.all())` in tests, not a production tuple literal.
- `game/strategy/engine/command_handlers.py` is a transitional re-export shim; canonical command handlers are under `game/strategy/engine/handlers/`.
- `OrderProcessor` no longer owns large private execution helpers; live logic is in `game/strategy/engine/order_handlers/`.
- `ACTIVATE_ABILITY` and `DEACTIVATE_ABILITY` are action-category members for consistency but are handled by `PlanetActionEngine`, not the order-handler registry.
- Planet ability order progress no longer lives on `Order.execution_progress`; orders initiate `ComponentActivationState`, then `ComponentActivationEngine` ticks it.
