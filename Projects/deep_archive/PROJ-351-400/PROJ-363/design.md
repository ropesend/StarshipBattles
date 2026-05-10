# PROJ-363: Design Document

## Initial Analysis

The runtime `CommandHandlerRegistry` is fine. The problem is metadata scatter:
- 31 command DTOs in `commands.py:44-456`
- OrderType enum (14 members) + 5 frozenset categories in `order_types.py:18-70`
- 31 hand-written `register()` calls in `registry_factory.py:64-125`
- `ORDER_TO_ABILITY_MAP` (12 entries) in `action_time_resolver.py:33-41`
- 31 `dispatch_*_command` methods in `command_dispatch_slice.py:50-219` (~200 LOC of pure boilerplate)
- Per-superweapon dispatch lambdas in `order_processor.py:706-725` (overlap with PROJ-364)

A new command requires touching all 7 surfaces. PROJ-363 makes the spec table the **single source of truth** for the first 5 surfaces (PROJ-364 handles superweapon dispatch separately).

## Swarm Findings Summary

### Architecture (findings/01_architecture.md)

Proposed `CommandSpec`:
```python
@dataclass(frozen=True)
class CommandSpec:
    command_class: type[Command]
    order_type: OrderType | None       # None for mission commands
    handler_class: type[ICommandHandler]
    category: str                      # 'movement' | 'action' | 'superweapon' | 'planet' | 'build' | 'instant'
    subcategories: frozenset[str]
    action_ability_name: str | None
    execution_model: str = 'action'    # 'action' | 'production' | 'instant' | 'mission'
    facade_helper_name: str | None = None
    serializer_codec: str | None = None
```

Spec table location: `game/strategy/engine/commands/specs.py` — sibling of `commands.py`. Import order:
1. `commands.py` (DTOs)
2. `handlers/*.py` (handler leaves)
3. `engine/commands/specs.py` (the table)
4. `handlers/registry_factory.py` (consumes specs)

This avoids circular imports because handlers don't import specs.

### Dependencies (findings/02_dependencies.md)

- 49 OrderType import sites; mostly data uses (frozenset membership), not switch-cases.
- `CommandHandlerRegistry` registrations are centralized in one factory; no plugin-style external `register()` calls outside it.
- Facade dispatch slice has 31 helper methods following identical 6-8 line pattern; ~200 LOC duplication.

### Test Impact (findings/03_test_impact.md)

- Existing tests cover happy paths but **no contract test** asserts "every CommandSpec entry has a handler + action-time + serializer codec". This is PROJ-363's TDD entry point.
- ActionTimeResolver tests are sampled, not parametrized over all OrderTypes — gap to close in Phase 1.

### Risks

| Risk | Detail | Mitigation |
|------|--------|------------|
| Mission commands | `Queue*MissionCommand` decompose into MOVE+ACTION at runtime; no single OrderType | `order_type=None`, `execution_model='mission'`; skip ORDER_TO_ABILITY_MAP |
| BUILD vs construction queue | BUILD is persistent (ProductionEngine ticks), not action-tick | `execution_model='production'`; skip action_time_resolver hookup |
| Fleet vs planet routing | `ClearOrders/DeleteOrder/ReorderOrder` accept `entity_type='fleet'\|'planet'` | Single command DTO, route via spec subcategory; no decomposition needed |
| Serialization asymmetry | Commands aren't persisted; only Orders are | `serializer_codec=None` is fine for now |
| Import-order regression | Module-import-time computation must work without circular deps | Specs.py is leaf in the chain; tested by Phase 1 contract test that imports the spec table at top of test file |
| Tests pinning facade method names | 31 `dispatch_*` methods must remain callable post-`__getattr__` collapse | Add a coverage test that asserts each spec's `facade_helper_name` resolves through `__getattr__` and returns a callable |

### Key Patterns to Reuse
- **Frozen dataclass + tuple registry** (StabilizerRegistry, EffectAbilityMetadata in PROJ-362).
- **Module-import-time generation** of frozensets from a spec table (e.g. `MOVEMENT_ORDER_TYPES = frozenset(s.order_type for s in COMMAND_SPECS if s.category == 'movement' and s.order_type is not None)`).

## Design Decisions
See [decisions.md](decisions.md) for full log.
