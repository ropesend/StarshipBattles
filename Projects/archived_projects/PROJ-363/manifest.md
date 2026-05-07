# PROJ-363 File Manifest

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/engine/commands/__init__.py` | Production (new) | 2 | Empty package init |
| `game/strategy/engine/commands/specs.py` | Production (new) | 2 | `CommandSpec` dataclass + `COMMAND_SPECS` table covering all 31 commands |
| `game/strategy/engine/handlers/registry_factory.py` | Production (refactor) | 3 | `create_default_registry()` body becomes spec-driven loop; delete 31 hand-written `register()` calls + imports |
| `game/strategy/data/order_types.py` | Production (refactor) | 3 | `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES` derived from COMMAND_SPECS at import time |
| `game/strategy/services/action_time_resolver.py` | Production (refactor) | 3 | `ORDER_TO_ABILITY_MAP` derived from COMMAND_SPECS at import time |
| `game/strategy/facade/slices/command_dispatch_slice.py` | Production (refactor) | 4 | Replace 31 `dispatch_*_command` methods with `__getattr__` lookup; ~200 LOC → ~30 LOC |
| `tests/unit/strategy/engine/test_command_registry_contract.py` | Test (new) | 1 | Contract tests: spec↔handler, spec↔action-time, spec↔category-sets, spec↔facade-helper, OrderType coverage |
| `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` | Test (new or extend) | 4 | Smoke tests for `__getattr__` AttributeError paths |
| `tests/unit/strategy/test_command_handlers.py` | Test (verify) | 3 | Existing tests must continue to pass; minor adjustments if any directly reference deleted hand-written symbols |
| `tests/unit/strategy/services/test_action_time_resolver.py` | Test (extend) | 3 | Add full-OrderType parametrization per findings/03 §3 |

## Files referenced for context (not modified)

| File | Purpose |
|------|---------|
| `game/strategy/engine/commands.py` | Command DTO definitions; specs reference these classes |
| `game/strategy/engine/handlers/base.py` | `CommandHandlerRegistry` runtime container — unchanged |
| `game/strategy/engine/handlers/movement.py`, `build.py`, `transfer.py`, `order_queue.py`, `construction_queue.py` | Handler classes; specs reference these |
| `game/strategy/engine/superweapon_command_handlers.py` | Superweapon handlers; specs reference these (PROJ-364 will further consume the 'superweapon' category) |
| `game/strategy/engine/planet_command_handlers.py` | Planet handlers |
| `game/strategy/engine/order_processor.py` | Superweapon dispatch lambdas (lines 706-725) — OUT OF SCOPE for PROJ-363; PROJ-364 owns this |
| `game/strategy/data/order_serializer.py` | Order persistence — unchanged in PROJ-363 |
