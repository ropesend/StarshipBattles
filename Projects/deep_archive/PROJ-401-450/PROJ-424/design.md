# PROJ-424: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to [decisions.md](decisions.md).
>
> Canonical specification: [TD-03 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-03_order_metadata_convergence.md).

## Initial Analysis (from TD-03 verification)

Five overlapping truth surfaces encode the same order-metadata facts in `game/strategy/`:

| Surface | Location | What it holds |
|---|---|---|
| Command DTO catalog | `game/strategy/engine/commands/__init__.py:1-587` | 41 `@dataclass` Command DTOs |
| Command spec registry | `game/strategy/engine/commands/registry.py:70-316` | `CommandSpec` + `CommandRegistry`, with derivations `movement_order_types()`, `action_order_types()`, `planet_action_order_types()`, `order_to_ability_map()`, `specs_by_facade_helper()`. Seeded via `seed_default_commands()` / `reset_command_registry()` (registry.py:374-426). |
| Hardcoded category frozensets (3) | `game/strategy/data/order_types.py:52-108` | `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`. Comment (lines 53-67) explicitly says they're hardcoded because runtime derivation would trigger an import cycle. |
| Fourth hardcoded frozenset | `game/strategy/data/order_types.py:110-121` | `PLANET_FMS_ACTION_ORDER_TYPES` — not mentioned in the original audit; same fragmentation pattern. |
| Import-time snapshot map | `game/strategy/services/action_time_resolver.py:35-50` | `ORDER_TO_ABILITY_MAP: Dict[OrderType, str] = _build_order_to_ability_map()` — runs `seed_default_commands()` once at module import, then freezes the dict. Read at `action_time_resolver.py:101`. |

The contract test `test_command_specs_contract.py` pins equality at *test time* but does nothing about *runtime drift* if `command_registry.register(..., replace=True)` is called after import. `register(spec, *, replace=True)` is supported (logs WARN) for mod overlays; no consumer of the duplicated frozensets or `ORDER_TO_ABILITY_MAP` ever re-reads after the snapshot.

## Cycle Analysis

The cycle that justifies the hardcoded frozensets (per `order_types.py:53-67`):

```
order_types.py  -> commands/registry.py  -> seed_default_commands()
                                          -> handlers.{movement, transfer, lay_mines, ...}
                                          -> order_types.py  (handlers import Order, OrderType)
```

The cycle is **real** if `order_types.py` runs the seed eagerly at import time. The fix must be **lazy**: resolve only when a consumer asks. A separate module `order_metadata_view.py` that defers the `seed_default_commands()` call until first read breaks the cycle cleanly. Critically, the duplicated frozensets themselves are not imported by any handler module — `Grep` over `game/strategy/engine/handlers/*.py` shows only `Order, OrderType` — so the view can read through the registry without re-triggering the cycle.

## `OrderMetadataView` Contract

```python
# game/strategy/engine/commands/order_metadata_view.py

from game.strategy.data.order_types import OrderType


class OrderMetadataView:
    """Live, lazy, cycle-safe read facade over command_registry.

    Import-time invariant: importing this module must NOT import
    game.strategy.engine.commands.registry. All registry access happens
    inside _registry(), which is called on first property read.
    """

    @staticmethod
    def _registry():
        from game.strategy.engine.commands.registry import (
            command_registry,
            seed_default_commands,
        )
        if len(command_registry) == 0:
            seed_default_commands(command_registry)
        return command_registry

    @property
    def movement_order_types(self) -> frozenset[OrderType]:
        return self._registry().movement_order_types()

    @property
    def action_order_types(self) -> frozenset[OrderType]:
        return self._registry().action_order_types()

    @property
    def planet_action_order_types(self) -> frozenset[OrderType]:
        return self._registry().planet_action_order_types()

    @property
    def planet_fms_action_order_types(self) -> frozenset[OrderType]:
        return self._registry().planet_fms_action_order_types()

    @property
    def order_to_ability_map(self) -> dict[OrderType, str]:
        return self._registry().order_to_ability_map()


order_metadata = OrderMetadataView()
```

### Required architecture outcomes (end state)
1. `game/strategy/data/order_types.py` keeps `OrderType`, `Order`, and serialization helpers only. No metadata frozensets remain there.
2. `CommandRegistry` owns all metadata derivations: movement, action, planet-action, planet-FMS, and order-to-ability.
3. `order_metadata_view.py` is the only read facade used by engines and services.
4. `action_time_resolver.py` no longer snapshots `ORDER_TO_ABILITY_MAP` at import time.
5. The five FMS handlers carry an explicit `subcategories=frozenset({"planet_fms"})` tag.

### Explicit non-goals
- No caching layer on the view.
- No invalidation API.
- No attempt to eliminate `command_registry.register(..., replace=True)`.
- No module-level compatibility aliases in `order_types.py`.

## Duplicated Frozensets to Delete (Phase 5)

| Constant | Defined at | Status |
|---|---|---|
| `MOVEMENT_ORDER_TYPES` | `game/strategy/data/order_types.py:52-?` | Delete after Phase 4 migration |
| `ACTION_ORDER_TYPES` | `game/strategy/data/order_types.py` | Delete after Phase 4 migration |
| `PLANET_ACTION_ORDER_TYPES` | `game/strategy/data/order_types.py` | Delete after Phase 4 migration |
| `PLANET_FMS_ACTION_ORDER_TYPES` | `game/strategy/data/order_types.py:110-121` | Delete after Phase 4 migration |
| (re-exports of the above) | `game/strategy/data/fleet.py:27-28` | Delete in Phase 5 |

That's **5 surfaces** to demolish (4 frozensets + 1 re-export pair), all post-migration.

## Import-Time Snapshot to Replace (Phase 3)

`game/strategy/services/action_time_resolver.py:35-50` currently:

```python
def _build_order_to_ability_map() -> Dict[OrderType, str]:
    seed_default_commands(command_registry)  # eager, at import time
    return command_registry.order_to_ability_map()

ORDER_TO_ABILITY_MAP: Dict[OrderType, str] = _build_order_to_ability_map()
```

…and at `action_time_resolver.py:101` reads `ORDER_TO_ABILITY_MAP.get(order.type)`.

The Phase 3 replacement removes both `_build_order_to_ability_map` and the module-level `ORDER_TO_ABILITY_MAP`, and rewrites the read site to:

```python
from game.strategy.engine.commands.order_metadata_view import order_metadata
...
ability_id = order_metadata.order_to_ability_map.get(order.type)
```

This is the single most dangerous stale-snapshot in the codebase: any `command_registry.register(..., replace=True)` after import would silently fail to update `ORDER_TO_ABILITY_MAP`. The test `test_resolve_action_time_reflects_registry_replace` is the regression guard.

## Consumer Inventory (from TD-03 verification)

### `MOVEMENT_ORDER_TYPES` — production readers
- `game/strategy/engine/action_execution_engine.py:24,169`
- `game/strategy/engine/fleet_movement_engine.py:21`
- `game/strategy/data/fleet.py:27` (re-export)
- `game/strategy/services/action_time_resolver.py:24,86`
- `game/strategy/services/fleet_path_projection.py:22,76`
- `game/strategy/services/fleet_navigation_service.py:21`
- `game/strategy/services/cargo_transfer_service.py:12,37`

### `ACTION_ORDER_TYPES` — production readers
- `game/strategy/engine/action_execution_engine.py:25,164`
- `game/strategy/engine/fleet_movement_engine.py:21,275`
- `game/strategy/data/fleet.py:28` (re-export)
- `game/strategy/services/fleet_navigation_service.py:21`

### `PLANET_ACTION_ORDER_TYPES` — production readers
- `game/strategy/engine/planet_action_engine.py:19,131`
- `game/strategy/services/action_time_resolver.py:26,110`

### `PLANET_FMS_ACTION_ORDER_TYPES` — production readers
- `game/strategy/engine/action_execution_engine.py:27`

### `ORDER_TO_ABILITY_MAP` — production readers
- `game/strategy/services/action_time_resolver.py:50,101` (only reader, inside the module)

## Risk Register (from TD-03)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Reintroducing the import cycle by importing the registry at module load time | High | Keep the import inside `OrderMetadataView._registry()` and pin it with `test_view_is_lazy_at_import_time`. |
| Weak executor adds a second hardcoded FMS list in the registry | High | Require `subcategories=frozenset({"planet_fms"})` on the five command specs and derive `planet_fms_action_order_types()` from that tag only. |
| Deleting constants before production consumers are migrated | High | Phase 4 finishes production migration first; Phase 5 deletes constants only after focused tests pass. |
| Replacing the live view with cached module-level snapshots | Medium | Explicit non-goal: no caching and no module-level copies of view output. |
| Missing a direct test import of the old constants | Medium | Phase 0 grep, plus `test_order_types_no_duplicated_metadata.py` as the final guard. |

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
