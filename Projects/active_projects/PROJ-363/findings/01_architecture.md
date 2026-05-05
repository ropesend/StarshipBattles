# PROJ-353 Architecture Analysis

## 1. Command count and OrderType enum
- **31 command classes** at `game/strategy/engine/commands.py:44-456`.
- **OrderType enum: 14 members** at `game/strategy/data/order_types.py:18-37` (MOVE, WARP, COLONIZE, MOVE_TO_FLEET, JOIN_FLEET, BUILD, TRANSFER, IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE, SELF_DESTRUCT, LOAD_POPULATION, UNLOAD_POPULATION, ACTIVATE_ABILITY, DEACTIVATE_ABILITY).
- **31 registrations** in `create_default_registry()` at `registry_factory.py:64-125`.

## 2. Categories in use
| Category | Members | File:Lines |
|----------|---------|-----------|
| MOVEMENT_ORDER_TYPES | MOVE, MOVE_TO_FLEET, WARP | order_types.py:42-46 |
| ACTION_ORDER_TYPES | COLONIZE, TRANSFER, LOAD/UNLOAD_POPULATION, all 5 superweapons, SELF_DESTRUCT, ACTIVATE/DEACTIVATE_ABILITY | order_types.py:51-64 |
| PLANET_ACTION_ORDER_TYPES | ACTIVATE_ABILITY, DEACTIVATE_ABILITY | order_types.py:67-70 |
| BUILD orders (implicit) | BUILD | action_time_resolver / order_processor |
| Superweapon orders (cluster) | 6 immediate + 5 mission variants | registry_factory.py:92-105 |

## 3. Edit footprint for adding one command (~7 files, ~45 lines)
1. `commands.py` — add command DTO (~12 lines).
2. `order_types.py` — add OrderType enum + category set update (~3 lines).
3. `registry_factory.py:64-125` — import + `register()` call (~2 lines).
4. New `handlers/<module>.py` — handler class (~30-50 lines).
5. `services/action_time_resolver.py:33-41` — ORDER_TO_ABILITY_MAP (~2 lines).
6. `engine/order_processor.py:706-725` — superweapon dispatch lambda if applicable (~3 lines).
7. `facade/slices/command_dispatch_slice.py:50-219` — dispatch helper method (~6-8 lines).

## 4. Proposed CommandSpec dataclass
```python
@dataclass(frozen=True)
class CommandSpec:
    command_class: Type[Command]
    order_type: OrderType | None       # None for mission commands
    handler_class: Type[ICommandHandler]
    category: str                      # 'movement' | 'action' | 'superweapon' | 'planet' | 'build' | 'instant'
    subcategories: frozenset[str]
    action_ability_name: str | None    # Maps to ORDER_TO_ABILITY_MAP entry
    execution_model: str = 'action'    # 'action' | 'production' | 'instant' | 'mission'
    facade_helper_name: str | None = None
    serializer_codec: str | None = None
```
**Why each field:**
- `command_class` + `handler_class` for runtime dispatch.
- `order_type` for OrderType↔command mapping (None for missions).
- `category` + `subcategories` to derive frozensets like MOVEMENT_ORDER_TYPES at import time.
- `action_ability_name` to derive ORDER_TO_ABILITY_MAP.
- `execution_model` distinguishes action-tick vs production vs instant vs mission decomposition.
- `facade_helper_name` for the auto-generated facade dispatch.

## 5. Spec table placement
**File:** `game/strategy/engine/commands/specs.py` (new module, sibling of commands.py).
**Import order:**
1. `commands.py` (DTOs)
2. `handlers/*.py` (handler leaves)
3. `engine/commands/specs.py` (the table — imports both)
4. `handlers/registry_factory.py` (consumes specs to populate the runtime registry)

This avoids circular imports since handlers don't import specs and specs.py is the top of the chain.

## 6. Facade helper deduplication
**Current:** 31 `dispatch_*_command()` methods at `command_dispatch_slice.py:50-219`, ~6-8 lines each, **~200 LOC total**.

**Proposed:** Replace with `__getattr__` that resolves `dispatch_<command_name>` against the spec table, drops to ~20 LOC, all 31 callers continue to work unchanged.

## 7. Risks (commands resisting spec-driven generation)

| Risk | Detail | Mitigation |
|------|--------|------------|
| Mission commands | `Queue*MissionCommand` family (commands.py:82-217) decompose into MOVE+ACTION orders; no single OrderType | Allow `order_type=None`, mark `execution_model='mission'`, skip ORDER_TO_ABILITY_MAP hookup |
| BUILD vs construction queue | BUILD is persistent (ProductionEngine), not action-tick | `execution_model='production'`, skip action_time_resolver |
| Fleet vs planet split | ClearOrders, DeleteOrder, ReorderOrder accept `entity_type='fleet'\|'planet'` | Keep single command DTO, route via spec subcategory; may want explicit split commands long-term |
| Serialization asymmetry | Commands not yet persisted (only Orders are); OrderSerializer is separate | Leave `serializer_codec=None`; design as separate phase |

**Conclusion:** Spec table is orthogonal to runtime dispatch — registry remains; specs populate it at import time. All 4 risks are absorbed via additional spec fields, not by carve-outs.
