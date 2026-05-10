# PROJ-353: Declarative Command/Order Spec Registry — Dependency Map

## 1. OrderType Importers (43 files)

**Data vs. Switch-Case Usage:**
- **Switch-case (conditional branches on `order.type`):** 49 locations across:
  - `order_processor.py`: 12+ if-elif chains (movement vs action routing)
  - `action_execution_engine.py`: 8+ checks (ability lookup by type)
  - `superweapon_order_processor.py`: 6+ for weapon-specific handlers
  - `fleet_movement_engine.py`: 4+ movement order filtering
  - `order_serializer.py`: 12+ target format dispatch (7 formats by type)
  - UI handlers: `strategy_screen_order_editing.py` (OrderType.MOVE, TRANSFER checks)

- **Data usage (category sets, frozensets):**
  - `MOVEMENT_ORDER_TYPES` (MOVE, MOVE_TO_FLEET, WARP): used in movement_engine, action_time_resolver
  - `ACTION_ORDER_TYPES` (COLONIZE, TRANSFER, IMPLODE_PLANET, etc.): action_execution_engine routing
  - `PLANET_ACTION_ORDER_TYPES` (ACTIVATE_ABILITY, DEACTIVATE_ABILITY): planet_action_engine filtering

**Key importers:** order_types.py, order_serializer.py, action_time_resolver.py, order_processor.py, action_execution_engine.py

---

## 2. CommandHandlerRegistry / create_default_registry Importers

**Single importer:** `game/strategy/engine/handlers/__init__.py`

**All 54 handlers registered in `registry_factory.py` lines 44-125:**
- Movement: ColonizeCommandHandler, MoveCommandHandler, InterceptCommandHandler, JoinCommandHandler, WarpCommandHandler
- Build/Construction: BuildOrderCommandHandler, RemoveBuildOrderCommandHandler, 4× queue handlers
- Superweapon: 11 handlers (direct + mission variants for 5 weapon types)
- Planet orders: 8 handlers (IssuePlanetOrderCommand, ability toggles, atmosphere/gravity/water/radiation targets)
- Fleet ops: SplitFleetCommand, DeleteOrderCommand, ReorderOrderCommand, ClearOrdersCommand

**No external plugins found:** all registry.register() calls are in `registry_factory.py` (lines 67–123).

---

## 3. ActionTimeResolver Usage

**Import:** `action_time_resolver.py` (lines 23, 49, 104)

**How used:**
- `ORDER_TO_ABILITY_MAP` (line 33): Maps OrderType → ability name (ColonizePlanet, DestroyPlanet, etc.)
- `PLANET_ACTION_ORDER_TYPES` check (line 104): Routes planet vs. fleet ability lookups
- `resolve_action_time()` (line 61): Called by `action_execution_engine.py` to determine tick cost for each order
- `MOVEMENT_ORDER_TYPES` constant (line 49): Movement orders bypass action engine (return 0)

**Consumers:** `action_execution_engine.py`, `test_action_time_resolver.py`

---

## 4. Category Set Definitions

| Set | File | Line | Consumers |
|-----|------|------|-----------|
| `MOVEMENT_ORDER_TYPES` | order_types.py:42–46 | fleet_movement_engine.py, action_time_resolver.py:49 |
| `ACTION_ORDER_TYPES` | order_types.py:51–64 | action_execution_engine.py (tick-based routing) |
| `PLANET_ACTION_ORDER_TYPES` | order_types.py:67–70 | action_time_resolver.py:104 (facility ability lookup) |

All three are frozensets used for membership tests (O(1) performance), not type dispatch.

---

## 5. Serialization Touch Points

**Order.to_dict() → Order.from_dict() round-trip (order_types.py:92–166):**
- Handles 7 target formats: HexCoord, fleet_ref, planet_ref, transfer, warp_params, ship_id_list, raw
- Routing by `order.type` (12 explicit type checks, lines 100–133)

**OrderSerializer (order_serializer.py:25–150):**
- Deserialize 7 target formats from save game (lines 99–150)
- **No implicit persistence:** Order.from_dict() is called by fleet_order_resolution during load; OrderSerializer is explicit deserialization for complex reference resolution

**Save/Load routes:**
- Fleet save: fleet.orders → [order.to_dict() for order in fleet.orders]
- Fleet load: OrderSerializer.deserialize_orders() → list of Order instances
- Planet save: planet.orders → [order.to_dict() for order in planet.orders]
- Planet load: Order.from_dict() via simple dict unpacking (PROJ-238)

---

## 6. Facade Dispatch Slice: 28 Methods

**File:** `command_dispatch_slice.py` (219 LOC total)

| Method | Lines |
|--------|-------|
| `handle_command` | 1 (42–44) |
| **Fleet-order dispatchers (7)** | ~3 each |
| dispatch_issue_colonize, dispatch_issue_move, dispatch_issue_intercept, dispatch_issue_join_fleet, dispatch_issue_warp, dispatch_issue_transfer, dispatch_clear_orders | 50–83 |
| dispatch_split_fleet, dispatch_delete_order, dispatch_reorder_order, dispatch_issue_self_destruct | 85–103 |
| **Mission queueing (6)** | ~3 each |
| dispatch_queue_colonize_mission, dispatch_queue_implode_planet_mission, dispatch_queue_stellerate_star_mission, dispatch_queue_open_warp_point_mission, dispatch_queue_close_warp_point_mission, dispatch_queue_create_dyson_sphere_mission | 109–137 |
| **Superweapon immediate (5)** | ~3 each |
| dispatch_issue_implode_planet, dispatch_issue_stellerate_star, dispatch_issue_open_warp_point, dispatch_issue_close_warp_point, dispatch_issue_create_dyson_sphere | 143–166 |
| **Build/construction (5)** | ~3 each |
| dispatch_issue_build_order, dispatch_remove_build_order, dispatch_add_to_construction_queue, dispatch_remove_from_construction_queue, dispatch_reorder_construction_queue | 172–195 |
| **Planet-order (5)** | ~3 each |
| dispatch_issue_planet_order, dispatch_clear_planet_orders, dispatch_delete_planet_order, dispatch_set_atmosphere_target, dispatch_set_{gravity,water,radiation} | 201–220 |

**All methods follow same pattern:** import Command class, instantiate from kwargs, call `self._handle_command()`

---

## 7. External Registry Registrations

**None found.** All `registry.register()` calls are **centralized in `registry_factory.py` (lines 67–123).**

No plugins/mods register commands elsewhere. The registry is populated once at session initialization via `create_default_registry()`.

---

## 8. UI Command-Issue Entry Points

**Representative call site:** `game/ui/screens/strategy_colonization.py:216`
```python
cmd = QueueColonizeMissionCommand(fleet.id, target_hex, planet_id, ...)
result = self.facade.handle_command(cmd)
```

**Other UI paths:**
- `strategy_click_dispatcher.py:269`: Direct `IssueWarpCommand` instantiation + `scene.facade.handle_command()`
- `transfer_controller.py`: Opens transfer dialog → issues IssueTransferCommand via facade
- `orders_window_ctrl.py`: delete/reorder buttons → dispatch_delete_order() / dispatch_reorder_order()
- `planet_abilities_controller.py`: UI ability toggles → dispatch_issue_planet_order()

All UI entry points converge at `StrategySessionFacade.handle_command()` (via dispatcher methods or direct Command instantiation).

---

**Summary:** 343 handler lines + 219 facade lines + 150 serializer lines + 194 resolver lines = **906 LOC across core infrastructure.** No external registration; all 54 handlers wired via single registry_factory function.
