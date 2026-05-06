# PROJ-368: Design — OrderProcessor Decomposition

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

`AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` flagged `game/strategy/engine/order_processor.py` (910 LOC) as the strategy layer's #1 maintainability target:

> Bundles 11 methods: order completion, cancellation, JOIN_FLEET, COLONIZE, TRANSFER (fleet↔planet AND fleet↔fleet), superweapons. `process_transfer()` = 114 LOC with 5 branching paths, each with direct data mutations. No unit tests; only integration tests. Full Fleet/Planet/Empire graphs required. Cost per new transfer type: 50 LOC mock setup. Changing `Planet.stockpile` breaks load/unload simultaneously (150+ LOC affected).

The review proposed a 3-phase remediation focused on extracting `TransferStrategy` interfaces. PROJ-368 broadens that to a unified `OrderHandler` decomposition spanning every `OrderType` the processor handles, mirroring two existing patterns in the codebase: the command-handler decomposition at `game/strategy/engine/handlers/` (PROJ-309 sub-phase 3.5) and the spec-driven superweapon dispatch at `game/strategy/engine/superweapon_order_processor.py:137-319` (PROJ-364).

---

## Initial Analysis

### Method inventory of `order_processor.py`

The file is 910 lines, 11 methods on `OrderProcessor`, plus 3 dataclasses and 1 module-level docstring block. LOC counts include docstrings.

| Method | Lines | Order type(s) handled | Mutates |
|---|---|---|---|
| `__init__` | 75-84 | n/a | constructs `SuperweaponOrderProcessor` |
| `_execute_fleet_merge` | 86-108 | JOIN_FLEET (helper) | `Fleet.ships`, `Empire.fleets`, event bus |
| `process_join_fleet` | 110-149 | `JOIN_FLEET` (single) | calls `_execute_fleet_merge`; `Fleet.pop_order` |
| `process_colonize` | 151-249 | `COLONIZE` | `Empire.colonies`, `Fleet.pop_order`, `Planet.facilities`, ship `carried_items`, planet stockpile |
| `process_transfer` | 251-364 | `TRANSFER`, `LOAD_POPULATION`, `UNLOAD_POPULATION` | dispatch only — calls `_execute_*` |
| `_execute_fleet_transfer` | 366-396 | TRANSFER (fleet↔fleet) | both fleets' `resources` |
| `_execute_load` | 398-467 | TRANSFER/LOAD (planet→fleet) | `planet.populations[i].count`, `planet.stockpile`, `fleet.resources`, ship `carried_items` |
| `_execute_unload` | 469-530 | TRANSFER/UNLOAD (fleet→planet) | `fleet.resources`, `planet.populations.append(SpeciesPopulation(...))`, `planet.stockpile`, staging yard |
| `_load_pod_from_staging_yard` | 532-585 | TRANSFER (drop_pod) | reverse-iterates and removes from `planet.staging_yard`; appends to `ship.carried_items` |
| `_unload_pod_to_staging_yard` | 587-616 | TRANSFER (drop_pod) | `ship.carried_items.pop(i)`, `planet.staging_yard` |
| `_deploy_drop_pod` | 618-652 | COLONIZE (helper) | `ship.carried_items.pop`, `planet.facilities.append(PlanetaryFacility(...))`, planet stockpile |
| `execute_action_order` | 655-732 | dispatch for COLONIZE / TRANSFER / 6 superweapons | `Fleet.pop_order` |
| `_validate_tick_inputs` | 734-743 | `process_instant_orders` precondition | none — raises `ValidationException` |
| `process_instant_orders` | 745-821 | `JOIN_FLEET` (tick batch, BUG-122) | calls `_execute_fleet_merge`; pops orders on cancellation |
| `_elect_canonical_merges` | 823-883 | JOIN_FLEET (helper) | none — pure dispatch |
| `_emit_join_cancelled` | 885-910 | JOIN_FLEET (helper, event bus) | event bus only |

### Smells observed

1. **`process_transfer` has five branches in one method.** Lines 291-326 fan out into: planet-id resolve, BUG-70 LOAD_POPULATION auto-resolve, target_fleet_id resolve (galaxy.empires search → empire.fleets fallback), then lines 350-360 dispatch on `is_planet/is_fleet`. Five paths, all mutating different attribute trees.

2. **Inline data mutations against `Planet.populations`.** `_execute_load:439` does `pop.count -= to_load`. `_execute_unload:514` does `planet.populations.append(SpeciesPopulation(...))`. There is no `Planet` API for these — the strategy layer reaches in.

3. **Reverse-iteration over staging yard for safe removal.** `_load_pod_from_staging_yard:552` iterates indices in reverse to safely `pop`. The semantics are correct but isolated to this one method; no `StagingYardManager` abstraction.

4. **6-entry inline lambda dict for superweapon dispatch.** `execute_action_order:706-725` is a literal `dict[OrderType, Callable]` rebuilt every call. The actual dispatch table already lives in `superweapon_registry.SUPERWEAPON_SPECS` — the lambda dict duplicates it.

5. **`process_instant_orders` is a 75-LOC three-phase pipeline (BUG-122).** Phase A collects, Phase B canonicalizes via `_elect_canonical_merges`, Phase C executes with re-validation. This is the most complex routine in the file but is single-OrderType (`JOIN_FLEET`) — natural fit for a dedicated handler.

6. **Double JOIN_FLEET path:** `process_join_fleet` (single fleet, called from where?) and `process_instant_orders` (batch) share `_execute_fleet_merge`. A grep shows `process_join_fleet` has no callers in `game/`; the sole consumer is `tests/unit/strategy/engine/test_order_processor_fleet_merge.py`. **Open question for user:** is `process_join_fleet` dead production code? See § Open Questions Q3.

7. **`SELF_DESTRUCT` is the odd superweapon out.** Six `OrderType` values are in the `superweapon_handlers` dict at `order_processor.py:706-725`. Five of those route to spec-driven `process_*` methods on `SuperweaponOrderProcessor` (which use the unified `execute_superweapon` dispatcher). The sixth, `process_self_destruct` at `superweapon_order_processor.py:664-740`, is **not** spec-driven — it's a 76-LOC standalone method that bypasses the dispatcher entirely. PROJ-368 surfaces this as a `SelfDestructHandler` (§3.4 below).

8. **No `ACTIVATE_ABILITY` / `DEACTIVATE_ABILITY` here.** Despite being `OrderType` enum values, they're handled by `PlanetActionEngine`, not `OrderProcessor`. The `ACTION_ORDER_TYPES` frozenset at `order_types.py:67-80` includes them, but the routing goes through `turn_phase_registry.py:243-251`'s `planet_actions` phase.

### Test coverage today

| Test file | LOC | What it covers |
|---|---|---|
| `test_order_processor_colonize.py` | 317 | Happy/unhappy paths, "Any" planet sentinel, missing drop pod, COLONY_FOUNDED event payload, `execute_action_order` routing, missing-component_registry error |
| `test_order_processor_transfer.py` | 424 | 5 transfer routing paths, BUG-70 auto-resolve, galaxy.empires fallback, owner-empire scan, drop-pod staging-yard reverse-iteration |
| `test_order_processor_instant.py` | 282 | BUG-122 three-phase pipeline, mutual-pair canonicalization, Phase C aliveness re-validation, `absorbed_by_other_merge` / `target_absorbed_mid_iteration` reasons, event payloads |
| `test_order_processor_fleet_merge.py` | 88 | Single-fleet `process_join_fleet` happy/unhappy paths |
| `test_build_order_processor.py` | 157 | `BUILD` order — out of scope (handled by `ProductionEngine`, not `OrderProcessor`) |

**Total in-scope coverage: 1111 LOC across 4 files driving the 910-LOC monolith.** Every test uses `MagicMock(spec=Fleet)` or real `Fleet` instances. None of the tests can drive a single handler in isolation — they always go through `OrderProcessor`.

The PROJ-368 plan **preserves all four files** as integration smoke and **adds** per-handler unit test files in a new `tests/unit/strategy/engine/order_handlers/` directory (Phase 5).

### Cross-cutting concerns

- **Validation:** `ColonizeValidator`, `TransferValidator`, `SuperweaponValidator` already exist. No new validators introduced. Each handler calls the relevant validator the same way today's code does.
- **Logging:** `logger = logging.getLogger(__name__)` per module. Each handler module gets its own logger with `__name__` resolving to e.g. `game.strategy.engine.order_handlers.transfer`. Existing `OrderProcessor: ...` log prefixes change to `TransferHandler: ...` etc. — **acceptable change**, surfaced in decisions.md.
- **Event emission:** 7+ inline `if self._event_bus: self._event_bus.log_event(...)` blocks. `BaseOrderHandler._emit_event(event_type, category, ..., **kwargs)` centralizes the null-check.
- **Save/replay:** `OrderProcessor` is not serialized; `Order` objects are. `OrderSerializer` handles `Order.target` shapes. Decomposition is invisible to save format.
- **Undo:** No undo system in the strategy layer. The action-tick model is forward-only; rolling back an executed order is not supported. Out of scope.

---

## Current architecture

```
                                   ┌──────────────────────┐
                                   │  TickPhaseRegistry   │
                                   │  (turn_phase_registry│
                                   │   .py:225-242)       │
                                   └─────────┬────────────┘
                            ┌────instant─────┼────action─────┐
                            ▼                                ▼
            ┌───────────────────────┐         ┌─────────────────────────┐
            │ OrderProcessor        │         │ ActionExecutionEngine   │
            │  .process_instant_    │         │  ._execute_action       │
            │   orders(empires)     │         │  → OrderProcessor       │
            │                       │         │    .execute_action_     │
            │  (BUG-122 3-phase)    │         │     order(fleet, ...)   │
            └─────────┬─────────────┘         └─────────┬───────────────┘
                      │                                  │
                      ▼                                  ▼
            ┌─────────────────────────────────────────────────────┐
            │   OrderProcessor (910 LOC, 11 methods)              │
            │                                                     │
            │   ┌──────────────────────────────────────────┐      │
            │   │ execute_action_order:  6-entry lambda    │      │
            │   │   if/elif on OrderType                   │      │
            │   │ ├── COLONIZE  → process_colonize         │      │
            │   │ ├── TRANSFER/LOAD/UNLOAD → process_      │      │
            │   │ │   transfer (114 LOC, 5 branches)       │      │
            │   │ └── 6 × superweapon → SuperweaponOrder   │      │
            │   │     Processor.process_*  (already        │      │
            │   │     spec-driven via PROJ-364)            │      │
            │   └──────────────────────────────────────────┘      │
            │                                                     │
            │   process_instant_orders (BUG-122 3-phase, 75 LOC) │
            │   process_join_fleet (single, 40 LOC)              │
            │                                                     │
            │   private helpers: _execute_load/_unload/_fleet_    │
            │   transfer/_load_pod_from_staging_yard/_unload_pod_ │
            │   to_staging_yard/_deploy_drop_pod/_validate_tick_  │
            │   inputs/_elect_canonical_merges/_emit_join_        │
            │   cancelled/_execute_fleet_merge                    │
            └─────────────────────────────────────────────────────┘
```

---

## Target architecture

```
                                   ┌──────────────────────┐
                                   │  TickPhaseRegistry   │
                                   └─────────┬────────────┘
                            ┌────instant─────┼────action─────┐
                            ▼                                ▼
            ┌───────────────────────┐         ┌─────────────────────────┐
            │ OrderProcessor (~150  │         │ ActionExecutionEngine   │
            │ LOC facade)           │         │   (unchanged)           │
            │                       │         │                         │
            │ process_instant_      │         │ → OrderProcessor        │
            │  orders(empires):     │         │   .execute_action_      │
            │   delegate to         │         │    order(fleet, ...)    │
            │   registry[JOIN_FLEET]│         │                         │
            │                       │         │                         │
            │ execute_action_order: │         │                         │
            │   handler = registry  │         │                         │
            │   .get(order.type)    │         │                         │
            │   return handler      │         │                         │
            │   .execute_action_    │         │                         │
            │   order(...)          │         │                         │
            └─────────┬─────────────┘         └─────────────────────────┘
                      │
                      ▼
            ┌─────────────────────────────────────────────────────────┐
            │  game/strategy/engine/order_handlers/                   │
            │                                                         │
            │  base.py                                                │
            │    IOrderHandler  (Protocol)                            │
            │    BaseOrderHandler  (mixin: _emit_event)               │
            │    OrderHandlerRegistry                                 │
            │                                                         │
            │  registry_factory.py                                    │
            │    create_default_order_handler_registry(event_bus)     │
            │                                                         │
            │  join_fleet.py                                          │
            │    JoinFleetHandler                                     │
            │      .process_instant_orders(empires)  (BUG-122 3-phase)│
            │      .execute_action_order(fleet, ...) (single fleet)   │
            │      ._elect_canonical_merges(candidates)               │
            │      ._emit_join_cancelled(...)                         │
            │      ._execute_fleet_merge(fleet, target, empire)       │
            │      ._validate_tick_inputs(empires)                    │
            │                                                         │
            │  colonize.py                                            │
            │    ColonizeHandler                                      │
            │      .execute_action_order(fleet, empire, galaxy, ...)  │
            │      ._deploy_drop_pod(fleet, planet)                   │
            │                                                         │
            │  self_destruct.py                                       │
            │    SelfDestructHandler                                  │
            │      .execute_action_order(fleet, empire, galaxy)       │
            │      (lifted from superweapon_order_processor.py:664)   │
            │                                                         │
            │  transfer.py                                            │
            │    TransferHandler                                      │
            │      .execute_action_order(fleet, ...)  (5 dispatches)  │
            │      ._dispatch_load_planet(...)                        │
            │      ._dispatch_unload_planet(...)                      │
            │      ._dispatch_fleet_to_fleet(...)                     │
            │      ._dispatch_drop_pod_load(...)                      │
            │      ._dispatch_drop_pod_unload(...)                    │
            │                                                         │
            │  superweapons.py                                        │
            │    SuperweaponHandlerAdapter(spec, processor)           │
            │      .execute_action_order(...)  (delegates)            │
            │    _build_superweapon_handlers(processor) → list of     │
            │      adapters from SUPERWEAPON_SPECS                    │
            │                                                         │
            │  __init__.py                                            │
            │    re-exports + __all__                                 │
            └─────────────────────────────────────────────────────────┘
                      │
                      └───→ delegate to SuperweaponOrderProcessor
                            (game/strategy/engine/superweapon_order_processor.py
                             — internal structure unchanged)
```

---

## Phase-by-phase design notes

### Phase 1 — `IOrderHandler` Protocol + JoinFleet PoC

#### Protocol shape

```python
# game/strategy/engine/order_handlers/base.py
from typing import Protocol, runtime_checkable, Optional

@runtime_checkable
class IOrderHandler(Protocol):
    """Per-OrderType handler for the action / instant order pipelines."""

    @property
    def supported_order_types(self) -> tuple[OrderType, ...]:
        """OrderType values this handler claims. Drives registry registration."""
        ...

    def execute_action_order(
        self,
        fleet: 'Fleet',
        empire: 'Empire',
        galaxy: 'Galaxy',
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List['Empire']] = None,
    ) -> OrderExecutionResult:
        """Execute the fleet's current action order.

        Returns OrderExecutionResult with .fleet_consumed, .success, .message.
        """
        ...
```

**Why a Protocol, not an ABC?** Mirrors `engine/handlers/base.py:84-99`'s `ICommandHandler` Protocol — same layer, same pattern. Avoids the import-graph constraint that ABCs from `interfaces/engines.py` impose.

**`OrderExecutionResult`:** unified result type replacing the per-method `JoinFleetResult`, `ColonizeResult`, `TransferResult`, `SuperweaponResult`. Field-compatible superset:

```python
@dataclass
class OrderExecutionResult:
    success: bool
    fleet_consumed: bool = False
    message: str = ""
    # Per-handler extras (kept for backward-compat at the facade layer):
    merged: bool = False              # JoinFleet legacy field
    cancelled: bool = False           # JoinFleet legacy field
    colonized: bool = False           # Colonize legacy field
    planet_name: Optional[str] = None # Colonize legacy field
    amount_transferred: int = 0       # Transfer legacy field
```

**Decision:** keep the legacy result dataclasses (`JoinFleetResult`, `ColonizeResult`, `TransferResult`, `SuperweaponResult`) as thin `from_execution_result` adapters at the `OrderProcessor` facade layer. This means `process_join_fleet` returning `JoinFleetResult` still works for the existing test in `test_order_processor_fleet_merge.py`, and the handler internals work with a single unified type.

#### Registry shape

```python
class OrderHandlerRegistry:
    def __init__(self) -> None:
        self._by_type: dict[OrderType, IOrderHandler] = {}

    def register(self, order_type: OrderType, handler: IOrderHandler) -> None: ...
    def get(self, order_type: OrderType) -> Optional[IOrderHandler]: ...
    def __contains__(self, order_type: OrderType) -> bool: ...
    def all_registered(self) -> frozenset[OrderType]: ...  # for AST guard
```

**Single-handler-per-type:** `LOAD_POPULATION`, `UNLOAD_POPULATION`, and `TRANSFER` all map to the same `TransferHandler` instance. The registry stores one entry per `OrderType` key but the handler instance is shared.

#### JoinFleetHandler — the proof of concept

`JoinFleetHandler` is the natural PoC because it has the most interesting shape:
- Two public entry points (`process_instant_orders` for batch, `execute_action_order` for single — though see Open Question Q3)
- Three private helpers (`_elect_canonical_merges`, `_emit_join_cancelled`, `_execute_fleet_merge`) that move with it
- BUG-122 three-phase pipeline is a self-contained algorithm
- Existing tests (`test_order_processor_instant.py`, `test_order_processor_fleet_merge.py`) pin the behavior precisely — no behavior changes possible, only structural

`OrderProcessor.process_instant_orders` becomes:

```python
def process_instant_orders(self, empires: List['Empire']) -> List[Tuple['Empire', Fleet]]:
    return self._registry.get(OrderType.JOIN_FLEET).process_instant_orders(empires)
```

`JoinFleetHandler` adds a new method `process_instant_orders` to the Protocol (or as a handler-specific extension — see decisions.md). Other handlers raise `NotImplementedError` if called.

### Phase 2 — Colonize + SelfDestruct

#### ColonizeHandler

Lift-and-shift of `process_colonize` (99 lines) + `_deploy_drop_pod` (35 lines). Public method: `execute_action_order(fleet, empire, galaxy, *, component_registry)`. The `component_registry` kwarg is required for COLONIZE; the handler raises `ValueError` if absent (matching today's `logger.error + return False` at `order_processor.py:691-693`, but stronger: turning a silent failure into a contract violation).

**Open question Q1:** Should the missing-`component_registry` case raise or continue to log+return-False? See § Open Questions.

#### SelfDestructHandler

Today, `SELF_DESTRUCT` routes through `OrderProcessor.execute_action_order:721-725` to `SuperweaponOrderProcessor.process_self_destruct` (76 LOC, **not spec-driven**). The handler is the third leg of the dispatch table:
- 5 superweapons → spec-driven `execute_superweapon` dispatcher
- 1 superweapon (`SELF_DESTRUCT`) → standalone method
- All 6 routed via the same lambda dict in `OrderProcessor.execute_action_order`

PROJ-368 lifts `SelfDestructHandler` out of `superweapon_order_processor.py` and into `order_handlers/self_destruct.py`. **The other 5 superweapon `process_*` methods stay in `SuperweaponOrderProcessor`** — they're already spec-driven and out-of-scope for restructuring (see § Out-of-scope).

This split surfaces the asymmetry rather than hiding it. Phase 4's `superweapons.py` module then only has 5 adapters; `SelfDestruct` is a peer handler.

### Phase 3 — Transfer family

#### Five-branch decomposition

`process_transfer:251-364` has these conditional paths that PROJ-368 makes explicit:

| Branch | Today's path | New private method on `TransferHandler` |
|---|---|---|
| 1. Planet target, load, resource cargo | `_execute_load` → resource branch (lines 449-467) | `_dispatch_load_planet_resource` |
| 2. Planet target, load, passengers | `_execute_load` → passengers branch (lines 413-446) | `_dispatch_load_planet_passengers` |
| 3. Planet target, load, drop_pod | `_execute_load` → `_load_pod_from_staging_yard` | `_dispatch_drop_pod_load` |
| 4. Planet target, unload, resource cargo | `_execute_unload` → resource branch (lines 519-530) | `_dispatch_unload_planet_resource` |
| 5. Planet target, unload, passengers | `_execute_unload` → passengers branch (lines 484-517) | `_dispatch_unload_planet_passengers` |
| 6. Planet target, unload, drop_pod | `_execute_unload` → `_unload_pod_to_staging_yard` | `_dispatch_drop_pod_unload` |
| 7. Fleet target | `_execute_fleet_transfer` (lines 366-396) | `_dispatch_fleet_to_fleet` |

The review report counted "5 branching paths" — 7 is the more honest count once cargo type sub-branches are exposed. Phase 3 handlers explicitly enumerate them.

The BUG-70 LOAD_POPULATION auto-resolve (lines 295-307) is the ONLY pre-dispatch branch and stays at the top of `TransferHandler.execute_action_order`.

#### `target_fleet_id` resolution

Today's order_processor.py:308-326 searches `galaxy.empires` (which may not exist on Galaxy — `getattr(galaxy, 'empires', [])`), then falls back to `empire.fleets`. This brittleness was flagged in PROJ-343 T1.1 (the call-site fix in `handlers/transfer.py:41-42`). PROJ-368 keeps the same lookup logic but extracts it into a documented private method `_resolve_target_fleet_by_id`. **Behavior unchanged**; surface area shrinks.

### Phase 4 — Superweapon dispatch + facade collapse

#### Spec-driven adapter

```python
# game/strategy/engine/order_handlers/superweapons.py
class SuperweaponHandlerAdapter(BaseOrderHandler):
    def __init__(
        self,
        spec: SuperweaponSpec,
        processor: SuperweaponOrderProcessor,
    ) -> None:
        self._spec = spec
        self._processor = processor

    @property
    def supported_order_types(self) -> tuple[OrderType, ...]:
        return (self._spec.order_type,)

    def execute_action_order(self, fleet, empire, galaxy, ...):
        method = getattr(self._processor, f"process_{self._spec.order_type.name.lower()}")
        result: SuperweaponResult = method(fleet, empire, galaxy, empires or [], component_registry)
        return OrderExecutionResult(
            success=result.success,
            fleet_consumed=result.fleet_consumed,
            message=result.message,
        )
```

The factory iterates `SUPERWEAPON_SPECS`, instantiates one adapter per spec, registers it. **5 adapters, not 6** — `SELF_DESTRUCT` was lifted to `SelfDestructHandler` in Phase 2.

#### Legacy method deletion

Phase 4 deletes the following from `OrderProcessor`:
- `_execute_fleet_merge` → moved to `JoinFleetHandler`
- `process_join_fleet` → kept as a one-line shim that wraps `OrderExecutionResult` back into `JoinFleetResult` for backward compat (existing test calls `proc.process_join_fleet(...)` directly)
- `process_colonize` → kept as one-line shim (same reasoning) returning `ColonizeResult`
- `process_transfer` → kept as one-line shim returning `TransferResult`
- `_execute_fleet_transfer`, `_execute_load`, `_execute_unload` → moved to `TransferHandler`
- `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard` → moved to `TransferHandler`
- `_deploy_drop_pod` → moved to `ColonizeHandler`
- `_validate_tick_inputs`, `_elect_canonical_merges`, `_emit_join_cancelled` → moved to `JoinFleetHandler`
- `process_instant_orders` → kept as one-line shim
- `execute_action_order` → simplified to registry lookup (1 method, ~15 lines)

After Phase 4, `OrderProcessor` is **public surface preservation only** — every public method exists for backward compat, every method is ≤ 5 lines. Target: ≤ 200 LOC.

### Phase 5 — Tests + AST guard

#### Per-handler unit tests

New directory: `tests/unit/strategy/engine/order_handlers/`. Each handler gets a focused test file that drives it directly (no `OrderProcessor` indirection). Tests use the same `MagicMock(spec=Fleet)` / `MagicMock(spec=Planet)` fixtures as today's tests but instantiate `JoinFleetHandler(event_bus=...)` directly.

Minimum 5 tests per handler:
1. Happy path
2. Wrong order type → no-op or raises
3. Validation failure → pop_order, return failure result
4. Event bus emission (capture and assert payload)
5. Edge case unique to handler (e.g., for `JoinFleetHandler`, the BUG-122 mutual-pair canonicalization; for `TransferHandler`, the BUG-70 auto-resolve)

#### AST static guard

```python
# tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py
import ast, pathlib

ORDER_PROCESSOR = pathlib.Path("game/strategy/engine/order_processor.py")

def test_order_processor_under_200_loc():
    assert len(ORDER_PROCESSOR.read_text().splitlines()) < 200

def test_no_order_type_branching_in_facade():
    tree = ast.parse(ORDER_PROCESSOR.read_text())
    # Walk for `if order.type == OrderType.X` or `order.type in (...)` patterns.
    # Allow exactly one OrderType reference (the dispatch lookup).
    ...

def test_every_action_order_type_has_a_handler():
    from game.strategy.engine.order_handlers.registry_factory import create_default_order_handler_registry
    from game.strategy.data.order_types import ACTION_ORDER_TYPES, OrderType, PLANET_ACTION_ORDER_TYPES
    registry = create_default_order_handler_registry(event_bus=None)
    expected = (ACTION_ORDER_TYPES - PLANET_ACTION_ORDER_TYPES) | {OrderType.JOIN_FLEET}
    assert registry.all_registered() >= expected
```

#### Documentation

`docs/systems/strategy_layer.md` gains a §"Order handlers" subsection mirroring the §"Command handlers" pattern. `docs/02_PATTERNS.md` cross-references the two registry-based dispatch systems in the strategy layer.

---

## Alternatives considered

### A. Leave the monolith and add unit tests against private methods

**Pro:** Smallest scope. No structural changes.

**Con:** The review's primary complaint is testability — you can't unit-test `_execute_load` independently because it's a private method that requires constructing the surrounding `OrderProcessor` and mocking five collaborators. Adding tests doesn't fix that. The 910-LOC ceiling continues to grow with every new order type.

**Rejected.**

### B. Split the file by domain (movement.py, transfer.py, colonize.py) but keep one `OrderProcessor` class

**Pro:** Smaller diff. No new abstraction.

**Con:** This is the structure today's `_execute_load`/`_execute_unload` already approximates — the file is internally cohesive but externally one class. Splitting modules without splitting classes doesn't enable per-handler unit tests; you still need an `OrderProcessor` instance to call anything.

**Rejected.**

### C. Command Pattern with self-dispatching `Order` subclasses

**Pro:** Each `OrderType` becomes its own `Order` subclass with a `.execute(context)` method. Maximally OO.

**Con:** `Order` is a serialized data class. Making it polymorphic complicates `OrderSerializer` (which is already a 7-format adapter) and ties the data layer to behavior. The codebase's existing pattern for command-like dispatch is the registry pattern (see `engine/handlers/`, `superweapon_registry.py`), not subclass dispatch.

**Rejected** — not a fit for this codebase's style.

### D. Per-`OrderType` handler with `OrderHandlerRegistry` (chosen)

**Pro:** Mirrors `engine/handlers/base.py:362-391`'s `CommandHandlerRegistry` exactly. Same Protocol shape (`ICommandHandler` ↔ `IOrderHandler`). Same `create_default_*_registry()` factory. Pattern is already proven at the layer.

**Con:** New package, new tests, and a registry-driven dispatch that's slightly slower than a hardcoded if/elif. Performance impact is negligible — handler dispatch is per-fleet-per-tick, not per-frame.

**Chosen.**

### E. Subsume `superweapon_order_processor.py` entirely

**Pro:** Symmetry — every order routes through the same handler registry.

**Con:** PROJ-364 (recent) just stabilized that file's spec-driven pattern. Re-architecting it now means redoing PROJ-364's audit. The 5 spec-driven `process_*` methods on `SuperweaponOrderProcessor` are already cohesive; adapting them via `SuperweaponHandlerAdapter` gives the symmetry-at-the-registry-level without rewriting the implementations.

**Rejected** — adapter pattern preserves PROJ-364's investment.

### F. Drop the `JoinFleetResult`/`ColonizeResult`/`TransferResult` dataclasses, use `OrderExecutionResult` exclusively

**Pro:** One result type. Smaller cognitive load.

**Con:** The existing test files at `test_order_processor_*.py` (1268 LOC) assert against the typed result fields (`.merged`, `.colonized`, `.amount_transferred`). Changing the public surface requires migrating those tests. Tests-as-spec contracts that PROJ-368 explicitly preserves.

**Rejected** — keep typed results as backward-compat adapters at the facade layer. Internal handlers work with `OrderExecutionResult`.

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| R1 | **Behavior drift in BUG-122 mutual-pair canonicalization.** The Phase A/B/C pipeline is delicate. Moving 75 LOC into `JoinFleetHandler` could introduce subtle ordering bugs. | Phase 1 task 1.1 is a TDD pin: run `test_order_processor_instant.py` first; it must pass on day 0 and at every checkpoint. Phase 5 AST guard prevents new branching from sneaking in. |
| R2 | **Event bus payload regression.** 7+ inline `log_event(...)` calls; subtle key omissions break downstream consumers. | Phase 5 per-handler test must capture and assert exact event payload dict equality, not just `.assert_called()`. Existing `test_order_processor_instant.py` already does this for `FLEET_JOIN_CANCELLED`. |
| R3 | **`process_join_fleet` may be dead code.** Open question Q3. If dead, tests are spec for nothing real. | Surface as open question; user resolves. If dead, delete in Phase 1; if live, preserve the public method. Either way, `JoinFleetHandler` covers both paths. |
| R4 | **`SuperweaponOrderProcessor.process_self_destruct` is not spec-driven** (lifted in Phase 2). The lift requires moving 76 LOC out of `superweapon_order_processor.py`. | Surfaced explicitly in §3.4. The existing `SuperweaponResult` dataclass is preserved. Phase 2 task includes a regression test for the SHIPS_SELF_DESTRUCTED event payload (the only behavioral assertion that exists today is in integration tests). |
| R5 | **Save/replay break.** If `OrderProcessor` is part of replay verification (PROJ-303 et al), changing internals could affect determinism. | `OrderProcessor` is **stateless** between calls — verified by `__init__` accepting only `event_bus`. No mutable state to checkpoint. Safe. |
| R6 | **`getattr(galaxy, 'empires', [])` brittleness.** Today's `process_transfer:314` reaches for an attribute that may not exist. PROJ-368 preserves this. | Out of scope to fix. Document in `decisions.md` row 5. PROJ-343 T1.1 is the related historical fix. |
| R7 | **Test file count grows.** 5 new test files in Phase 5; the existing 5 in `tests/unit/strategy/engine/test_order_processor_*.py` stay. Total: 10 files. | This is the intended outcome — focused per-handler tests + integration smoke. The `--testmon` workflow will pick up the right slice. |
| R8 | **Phase 4 deletion risks.** Deleting 700+ LOC of methods on `OrderProcessor` is the highest-risk single commit in the project. | Phase 4 is a single phase by design — atomic deletion, atomic registry switchover. The cumulative review at the Phase 4 boundary catches any regression before merge to `proj/PROJ-368/main`. |
| R9 | **Logger prefix change** (`OrderProcessor:` → `TransferHandler:` etc.). Log scrapers may rely on the existing prefixes. | Documented in decisions.md row 6. No production log scraper exists in the codebase; user-facing log strings are accepted to change. |
| R10 | **The Order type frozensets at `order_types.py:58-86`** are kept in sync with `COMMAND_SPECS` via `test_command_specs_contract.py`. PROJ-368 doesn't touch these but the AST guard in Phase 5 must use the same canonical source. | Phase 5 AST guard imports `ACTION_ORDER_TYPES` directly. No drift possible. |

---

## Dependencies on prior projects

- **PROJ-309 sub-phase 3.5** (command-handler decomposition): the architectural template for PROJ-368. The plan deliberately mirrors `engine/handlers/`'s structure — `base.py`, `registry_factory.py`, per-domain modules, sibling tests directory.
- **PROJ-364** (superweapon spec-driven dispatch): preserves `SuperweaponOrderProcessor`'s internals; `SuperweaponHandlerAdapter` is the only new surface that touches PROJ-364's work.
- **PROJ-273 / PROJ-278** (registry pattern idioms — ability stat registry, role registry): registry-as-dispatch is the codebase's established mechanism. PROJ-368 follows the same shape (registration-by-key, lookup-by-key, single-handler-per-key).
- **PROJ-259** (phase machinery / `TickPhaseRegistry`): PROJ-368 does not touch the tick-phase layer. `turn_phase_registry.py:228` continues to call `e.order_processor.process_instant_orders` — the lambda binds to the facade method that delegates to `JoinFleetHandler`.
- **PROJ-333** (order-processor characterization tests): the 4 in-scope test files (`test_order_processor_*.py`) were authored by PROJ-333 to pin behavior before refactoring. PROJ-368 is exactly the refactor those tests were paid for. They are the primary regression guard.
- **PROJ-343 T1.1** (transfer handler `target_fleet_id` fix): the existing fix at `handlers/transfer.py:108-113` is preserved verbatim; PROJ-368 doesn't re-touch it.
- **MEMORY.md baseline**: 15405 passed, 2 skipped (one known test-isolation flake `test_colony_owner_id_matches_empire`).

---

## Open questions for the user

**Q1.** When `execute_action_order` receives a `COLONIZE` order without `component_registry` (today: logs error, pops order, returns False at `order_processor.py:691-693`), should the new `ColonizeHandler` raise `ValueError` instead? Raising is more honest — it's a contract violation, not a runtime failure mode — but changes the public-facing failure mode for any caller that constructs orders without a registry. **Recommendation:** Keep log+pop+False for backward compat; add a comment marking it as a tech-debt opportunity for a future project.

**Q2.** Should `SuperweaponOrderProcessor.process_self_destruct` be lifted out into `SelfDestructHandler` (current plan in Phase 2) or stay where it is and just be wrapped by an adapter (like the other 5 superweapons)? The lift is cleaner architecturally — `SELF_DESTRUCT` doesn't fit the spec-driven pattern that `SuperweaponOrderProcessor` is otherwise organized around. The wrap is smaller. **Recommendation:** Lift. Surfaces the asymmetry rather than papering over it. Estimated +30 LOC of net code.

**Q3.** `OrderProcessor.process_join_fleet` (single-fleet, lines 110-149) has **no production callers** — only `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` calls it. Is this dead production code that should be deleted, or is it a public method intentionally kept for future use? **Recommendation:** Verify with `grep -rn 'process_join_fleet' game/`. If no production hits, delete the method entirely in Phase 1 along with the test file. If it's intended future API, keep it as a public method on `JoinFleetHandler` and the facade delegates.

**Q4.** Is `superweapon_order_processor.py` (782 LOC) **in or out of scope**? The plan as drafted treats it as out of scope — Phase 4 only adds an adapter wrapper. The review didn't list it as a target. But if user wants symmetric decomposition, Phase 4 grows significantly. **Recommendation:** Out of scope. PROJ-364 just stabilized it. Open a future follow-up project if the symmetry is wanted later.

**Resolved 2026-05-06 (Codex+Claude joint review):** Out of scope. Adapter wraps preserve PROJ-364's investment.

**Q5.** Where should `order_handlers/` live? `game/strategy/engine/order_handlers/` (plan default — sibling to `engine/handlers/`) or under a different namespace (`game/strategy/engine/handlers/order/`?) to make the relationship explicit? **Recommendation:** `engine/order_handlers/`. Sibling makes the parallel obvious; a sub-namespace inside `handlers/` would conflate two distinct dispatchers (UI command → order vs. action tick → state mutation).

**Q6.** Should the `OrderExecutionResult` unified result type **fully replace** `JoinFleetResult`/`ColonizeResult`/`TransferResult`/`SuperweaponResult` (and migrate the tests), or stay as an internal type with adapters at the facade? Plan default: keep typed results as adapters; preserve test surface. **Alternative:** migrate tests to the unified type — bigger Phase 5 scope but cleaner end state. **Recommendation:** Keep typed results. Tests already pin behavior; rewriting them is risk without architectural reward.

**Q7.** Logger prefix: `OrderProcessor: ...` vs `TransferHandler: ...`. The new prefix is more accurate but is a public-facing log string change. Confirm OK.

---

## Out-of-band: cross-project linkage

When Phase 5 lands, update `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` to mark target #1 as resolved by PROJ-368 commit `<sha>`.
