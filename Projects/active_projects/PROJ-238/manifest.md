# PROJ-238 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/order_types.py` | Production | Merge PlanetOrderType values into OrderType, rename FleetOrder → Order |
| `game/strategy/data/planet_order_types.py` | Production (DELETE) | Merge into order_types.py then delete |
| `game/strategy/data/fleet.py` | Production | Update FleetOrder references to Order |
| `game/strategy/data/planet.py` | Production | Rename planet_orders → orders, rename queue methods |
| `game/strategy/data/fleet_order_serializer.py` | Production (RENAME) | Rename to order_serializer.py, update class name |
| `game/strategy/engine/action_execution_engine.py` | Production | Merge planet action logic, handle both entity types |
| `game/strategy/engine/planet_action_engine.py` | Production (DELETE) | Merge into action_execution_engine.py |
| `game/strategy/engine/fleet_order_processor.py` | Production (RENAME) | Rename to order_processor.py |
| `game/strategy/services/action_time_resolver.py` | Production | Merge planet time resolution mappings |
| `game/strategy/services/planet_action_time_resolver.py` | Production (DELETE) | Merge into action_time_resolver.py |
| `game/strategy/engine/turn_engine.py` | Production | Update engine references, consolidate phases |
| `game/strategy/engine/command_handlers.py` | Production | Update FleetOrder → Order, register planet order handlers |
| `game/strategy/engine/planet_command_handlers.py` | Production | Update PlanetOrder → Order |
| `game/strategy/engine/superweapon_command_handlers.py` | Production | Update FleetOrder → Order |
| `game/strategy/engine/commands.py` | Production | Rename ClearFleetOrdersCommand → ClearOrdersCommand, etc. |
| `game/strategy/interfaces/engines.py` | Production | Remove IPlanetActionEngine (merged), update interface names |
| `game/strategy/validation/planet_order_validator.py` | Production | Update PlanetOrderType → OrderType |
| `game/strategy/validation/colonize_validator.py` | Production | Update FleetOrder → Order |
| `game/strategy/data/fleet_pursuer_tracker.py` | Production | Update FleetOrder references |
| `game/strategy/events/event_types.py` | Production | Already updated (PROJ-237) |
| `game/core/protocols.py` | Production | Add IOrderable protocol |
| `game/ui/screens/fleet_orders_window.py` | Production (RENAME) | Rename to orders_window.py, generalize for IOrderable |
| `game/ui/screens/strategy_window_manager.py` | Production | Support opening orders window for planets |
| `game/ui/screens/strategy_fleet_command_router.py` | Production | Add planet command routing |
| `game/ui/screens/strategy_event_router.py` | Production | Handle planet orders button clicks |
| `game/ui/screens/strategy_detail_formatter.py` | Production | Add btn_planet_orders visibility for planets |
| `game/ui/screens/strategy_panel_manager.py` | Production | Create btn_planet_orders button |
| `game/ui/screens/strategy_input_handler.py` | Production | Add planet context for hotkeys |
| `game/core/input_actions.py` | Production | Add SHIELD_TOGGLE, DETAIL_PANEL_PLANET_ORDERS |
| `data/default_keybindings.json` | Data | Add H and O bindings for planet actions |
| `tests/unit/strategy/data/test_planet_order_types.py` | Test (UPDATE) | Update PlanetOrderType → OrderType |
| `tests/unit/strategy/engine/test_planet_action_engine.py` | Test (UPDATE) | Update after engine merge |
| `tests/unit/strategy/engine/test_planet_energy_engine.py` | Test (UPDATE) | Update order references |
| `tests/unit/strategy/engine/test_action_execution_engine.py` | Test (UPDATE) | Update FleetOrder → Order |
| `tests/unit/strategy/engine/test_superweapon_order_processor.py` | Test (UPDATE) | Update FleetOrder → Order |
| `tests/unit/strategy/fleet/test_serialization.py` | Test (UPDATE) | Update class references |
| `tests/unit/strategy/fleet/test_basics.py` | Test (UPDATE) | Update class references |
| `tests/integration/save_load/test_roundtrip_orders.py` | Test (UPDATE) | Update class references |
| `tests/unit/quickstart/test_quickstart_builder.py` | Test (UPDATE) | Update class references |
| ~60 additional test files | Test (UPDATE) | Mechanical FleetOrder → Order rename |
