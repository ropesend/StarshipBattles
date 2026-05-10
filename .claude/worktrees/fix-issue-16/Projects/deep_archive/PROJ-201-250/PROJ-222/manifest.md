# PROJ-222 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/fleet_pursuer_tracker.py` | Production | NEW — FleetPursuerTracker delegate class |
| `game/strategy/data/fleet.py` | Production | Add pursuer tracker delegate, remove_order_at(), remove_orders_by_type(), _unregister_from_target(), merge_with() redirect hook |
| `game/strategy/data/empire.py` | Production | Add pursuer cancel in remove_fleet() |
| `game/strategy/events/event_types.py` | Production | Add 3 EventType + 1 EventCategory |
| `game/strategy/engine/command_handlers.py` | Production | Refactor 3 handlers to use Fleet API, add pursuer registration + validation in Join/Intercept handlers |
| `game/strategy/engine/fleet_order_processor.py` | Production | Add FLEET_JOINED event logging |
| `game/strategy/engine/game_session.py` | Production | Add pursuer rebuild loop in from_dict() |
| `game/strategy/data/order_types.py` | Production | Read-only reference (no changes expected) |
| `game/strategy/data/fleet_order_serializer.py` | Production | Read-only reference (no changes expected) |
| `tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py` | Test | NEW — Unit tests for FleetPursuerTracker |
| `tests/unit/strategy/fleet/test_basics.py` | Test | Add tests for new Fleet methods |
| `tests/unit/strategy/events/test_event_types.py` | Test | Update member count assertions |
| `tests/unit/strategy/test_command_handlers.py` | Test | Add pursuer registration + validation tests |
| `tests/unit/strategy/test_fleet_order_processor.py` | Test | Add event logging tests |
| `tests/unit/strategy/data/test_empire_fleet_registration.py` | Test | Add pursuer cancel tests |
| `tests/integration/strategy/test_fleet_join_redirect.py` | Test | NEW — Integration tests for full redirect/cancel flow |
