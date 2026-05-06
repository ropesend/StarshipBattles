# PROJ-368: Strategy: OrderProcessor Decomposition (handler-per-order-type)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-368` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-368 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Protocol + registry skeleton + JoinFleet PoC | Complete (Committed) | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Port instant + simple action orders (Colonize, SelfDestruct) | Complete (Committed) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Port Transfer family (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Port superweapon dispatch and delete legacy methods (includes registry-completeness + no-legacy-helper AST gates) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Per-handler unit tests + AST static-guard regression | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State

**Last Updated:** 2026-05-05
**Active Phase:** Phase 3
**Last Action:** Phase 2 committed. `ColonizeHandler` and `SelfDestructHandler` extracted. `OrderProcessor.process_colonize` is now a one-line delegate. `SELF_DESTRUCT` superweapon entry routes through the registry. 13 new tests added (7 colonize + 6 self_destruct); 4639 strategy tests pass. `OrderProcessor` LOC: 822 -> 744.
**Next Action:** Phase 3 — extract TransferHandler with 7 explicit `_dispatch_*` branches.
**Blockers:** None.

## Overview

`game/strategy/engine/order_processor.py` is a 910-LOC monolith that bundles 11 methods covering 11 distinct `OrderType` values (`JOIN_FLEET`, `COLONIZE`, `TRANSFER`, `LOAD_POPULATION`, `UNLOAD_POPULATION`, plus 6 superweapons that already delegate to a sibling spec-driven processor). `process_transfer()` alone is 114 LOC with five branching paths and inline data mutations against `Planet.populations`, `Fleet.resources`, and the staging yard. There are no per-order-type unit-testable handlers; today's tests (`tests/unit/strategy/engine/test_order_processor_*.py`, 1268 LOC across 5 files) drive the monolith via `MagicMock(spec=Fleet)` and `MagicMock(spec=Planet)` graphs.

PROJ-368 extracts a **per-`OrderType` handler** structure registered against an `OrderType → IOrderHandler` map, mirroring the spec-driven dispatch already proven in `superweapon_order_processor.py` (PROJ-364) and the command-handler decomposition in `engine/handlers/` (PROJ-309 sub-phase 3.5). After the project, `OrderProcessor` becomes a ~150-LOC facade that preserves its public surface (`process_instant_orders`, `execute_action_order`, plus the named per-method shims kept by the existing tests) and delegates to handlers in a new `game/strategy/engine/order_handlers/` package.

## Goals

- **Phase 1:** `IOrderHandler` Protocol + `OrderHandlerRegistry` exist; `JoinFleetHandler` is the proof-of-concept extraction. `OrderProcessor.process_join_fleet` becomes a thin shim that defers to the registry. Existing tests pass unchanged.
- **Phase 2:** `ColonizeHandler` and `SelfDestructHandler` extracted into `order_handlers/`. The `process_instant_orders` Phase A/B/C pipeline is moved into `JoinFleetHandler.process_instant_orders` (class-method) so the instant + per-fleet flows live next to each other; `OrderProcessor.process_instant_orders` becomes a one-line delegate. `_emit_join_cancelled` and `_elect_canonical_merges` move with it.
- **Phase 3:** `TransferHandler` extracted with `_execute_load`, `_execute_unload`, `_execute_fleet_transfer`, `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard`, `_deploy_drop_pod` as private members. The five `process_transfer` branching paths become explicit dispatch within `TransferHandler`. `LOAD_POPULATION` and `UNLOAD_POPULATION` route to the same handler.
- **Phase 4:** Superweapon dispatch (the 6-entry `superweapon_handlers` lambda dict at `order_processor.py:706-725`) becomes a registry registration loop driven by `superweapon_registry.SUPERWEAPON_SPECS`. The legacy `OrderProcessor` methods (`process_join_fleet`, `process_colonize`, `process_transfer`, `_execute_*`, `_load/unload_pod_*`, `_deploy_drop_pod`, `_validate_tick_inputs`, `_elect_canonical_merges`, `_emit_join_cancelled`, `_execute_fleet_merge`) are deleted. `OrderProcessor` is a facade ≤ 200 LOC implementing `IOrderProcessor` by dispatching to the registry.
- **Phase 5:** Each handler has a focused unit test file at `tests/unit/strategy/engine/order_handlers/test_<handler>.py`. The five legacy `test_order_processor_*.py` files are migrated, not replaced — they continue to drive the public `OrderProcessor` API as integration smoke. New AST-walker test asserts no new branching logic accretes inside `OrderProcessor` (max 200 LOC, max one `OrderType` enum reference per file).

Cross-cutting goal: zero behavior change. Every test passes at every phase boundary; the structured event bus payloads (`FLEET_JOINED`, `FLEET_JOIN_CANCELLED`, `COLONY_FOUNDED`, `SHIPS_SELF_DESTRUCTED`, all 6 superweapon events) are bit-identical, including the `reason=` field semantics on `FLEET_JOIN_CANCELLED`.

## Scope

**In:**

- `game/strategy/engine/order_processor.py` — drained to a ~150-LOC facade
- `game/strategy/engine/order_handlers/` (new package):
  - `__init__.py` — exports + `__all__`
  - `base.py` — `IOrderHandler` Protocol, `OrderHandlerRegistry`, `BaseOrderHandler` mixin (with `_emit_event` helper to centralize the `if self._event_bus: self._event_bus.log_event(...)` idiom that appears 7+ times in `order_processor.py`)
  - `join_fleet.py` — `JoinFleetHandler` (Phase 1)
  - `colonize.py` — `ColonizeHandler` (Phase 2)
  - `self_destruct.py` — `SelfDestructHandler` (Phase 2; today inside `superweapon_order_processor.py:664-740` but called via `OrderProcessor.execute_action_order`)
  - `transfer.py` — `TransferHandler` (Phase 3); folds in `_execute_load`, `_execute_unload`, `_execute_fleet_transfer`, `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard`, `_deploy_drop_pod`
  - `superweapons.py` — registry-driven adapter wiring `superweapon_registry.SUPERWEAPON_SPECS` to handler instances (Phase 4)
  - `registry_factory.py` — `create_default_order_handler_registry()` mirroring `engine/handlers/registry_factory.py`
- `game/strategy/interfaces/engines.py` — `IOrderProcessor` docstring updated; signature unchanged
- `tests/unit/strategy/engine/order_handlers/` (new test directory):
  - `test_base.py` — registry contract + protocol conformance
  - `test_join_fleet_handler.py` (Phase 1, derived from `test_order_processor_instant.py`)
  - `test_colonize_handler.py` (Phase 2, derived from `test_order_processor_colonize.py`)
  - `test_self_destruct_handler.py` (Phase 2)
  - `test_transfer_handler.py` (Phase 3, derived from `test_order_processor_transfer.py`)
  - `test_superweapon_dispatch.py` (Phase 4)
  - `test_order_processor_facade.py` (Phase 5 — AST-walker static guard)
- `tests/unit/strategy/engine/test_order_processor_*.py` (5 existing files, 1268 LOC) — preserved as integration smoke; assertions retained, fixtures unchanged
- `docs/systems/strategy_layer.md` — section on the order handler registry added at Phase 5
- `docs/02_PATTERNS.md` — cross-reference to `engine/handlers/` (command-handler) pattern as the parallel for `order_handlers/`

**Out:**

- `game/strategy/engine/superweapon_order_processor.py` (782 LOC) — already spec-driven via PROJ-364; Phase 4 only adapts its existing `process_*` methods into the new dispatch table. **No internal restructuring of `superweapon_order_processor.py` in this project.**
- `game/strategy/engine/handlers/` (the *command* handlers — UI Command → Order creation). Untouched. Naming the new package `order_handlers/` is deliberate to avoid collision.
- `BUILD` order processing (handled by `ProductionEngine`, never reaches `execute_action_order`)
- `MOVE`, `WARP`, `MOVE_TO_FLEET` (handled by `FleetMovementEngine`, never reach `OrderProcessor`)
- `ACTIVATE_ABILITY`, `DEACTIVATE_ABILITY` (handled by `PlanetActionEngine`, never reach `OrderProcessor`)
- The `IOrderProcessor` ABC at `game/strategy/interfaces/engines.py:168-230` — its public method signatures are preserved verbatim
- Save-game compatibility surgery — `Order` serialization through `OrderSerializer` is unchanged
- Re-architecting `process_instant_orders`'s BUG-122 three-phase semantics. The Phase A/B/C structure stays; it just moves into `JoinFleetHandler`.
- Adding new validation. The existing validators (`ColonizeValidator`, `TransferValidator`, `SuperweaponValidator`) keep their current contracts.

## Key Files

| Component | File Path |
|-----------|-----------|
| Monolith being decomposed | `game/strategy/engine/order_processor.py` |
| Already-spec-driven sibling (Phase 4 reference) | `game/strategy/engine/superweapon_order_processor.py` |
| Public interface (signatures preserved) | `game/strategy/interfaces/engines.py:168-230` |
| Caller — instant orders | `game/strategy/engine/turn_phase_registry.py:225-230` |
| Caller — action orders | `game/strategy/engine/action_execution_engine.py:202-221` |
| OrderType enum (canonical taxonomy) | `game/strategy/data/order_types.py:18-37` |
| Order target serialization | `game/strategy/data/order_serializer.py` |
| Pattern reference — command handlers | `game/strategy/engine/handlers/{base.py,registry_factory.py}` |
| Pattern reference — superweapon spec dispatch | `game/strategy/services/superweapon_registry.py` |
| Existing characterization tests (preserved) | `tests/unit/strategy/engine/test_order_processor_{colonize,transfer,instant,fleet_merge}.py` |
| Validators (unchanged) | `game/strategy/validation/{colonize,transfer,superweapon}_validator.py` |

## Related Documents

- [design.md](design.md) — Initial analysis, current vs. target architecture, alternatives considered, risks, open questions
- [decisions.md](decisions.md) — Architectural decisions log (dated 2026-05-05)
- [manifest.md](manifest.md) — Full file table with phase column
- [findings/initial_review.md](findings/initial_review.md) — Top 5 surprising facts from architect's read of `order_processor.py`
- Source review: `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` (target #1)
- Pattern precedent: PROJ-309 sub-phase 3.5 (command-handler decomposition); PROJ-364 (superweapon spec-driven dispatch)

## Today's vs. target dispatch (one-line diff)

**Today** (`order_processor.py:680-731`):

```
def execute_action_order(...):
    if order.type == OrderType.COLONIZE: return self.process_colonize(...).colonized
    if order.type in (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION): self.process_transfer(...); return False
    superweapon_handlers = {OrderType.IMPLODE_PLANET: lambda: ..., ...}  # 6-entry inline dict
    handler = superweapon_handlers.get(order.type)
    if handler: return handler().fleet_consumed
    return False
```

**Target** (Phase 4):

```
def execute_action_order(...):
    handler = ORDER_HANDLER_REGISTRY.get(order.type)
    if handler is None: return False
    return handler.execute_action_order(fleet, empire, galaxy, ...).fleet_consumed
```

`process_instant_orders` follows the same shape — `OrderProcessor.process_instant_orders(empires)` becomes a one-line delegate to `ORDER_HANDLER_REGISTRY[OrderType.JOIN_FLEET].process_instant_orders(empires)`.

## Phases

### Phase 1: Protocol + registry skeleton + JoinFleet PoC [Medium]

Define `IOrderHandler` Protocol and `OrderHandlerRegistry` in `order_handlers/base.py`. Extract `JoinFleetHandler` covering both `process_join_fleet` (single-fleet) and the lift-and-shift of the BUG-122 three-phase `process_instant_orders` flow plus its helpers (`_elect_canonical_merges`, `_emit_join_cancelled`, `_validate_tick_inputs`, `_execute_fleet_merge`). `OrderProcessor.process_join_fleet` and `process_instant_orders` become one-line delegates. New per-handler tests added; existing `test_order_processor_instant.py` and `test_order_processor_fleet_merge.py` continue to pass.

**Status:** Not Started. See [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Port instant + simple action orders (Colonize, SelfDestruct) [Medium]

Extract `ColonizeHandler` (today: `process_colonize` + `_deploy_drop_pod`) and `SelfDestructHandler` (today inside `superweapon_order_processor.process_self_destruct`, but routed via `OrderProcessor.execute_action_order` and the only superweapon order without a `SuperweaponSpec` — see design.md §3.4). Register both in the registry. `OrderProcessor.process_colonize` becomes a one-line delegate. New per-handler tests; existing `test_order_processor_colonize.py` continues to pass.

**Status:** Not Started. See [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Port Transfer family (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION) [Complex]

Extract `TransferHandler`. Subsume `process_transfer`, `_execute_load`, `_execute_unload`, `_execute_fleet_transfer`, `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard`. Decompose `process_transfer`'s 5 branches into explicit `_dispatch_load_planet`, `_dispatch_unload_planet`, `_dispatch_fleet_to_fleet`, `_dispatch_drop_pod_load`, `_dispatch_drop_pod_unload` private methods. The existing `BUG-70` LOAD_POPULATION auto-resolve path stays in `TransferHandler.execute_action_order` (the public entry) so the `direction == 'load' and not planet_id` decision is testable in isolation. Register `OrderType.TRANSFER`, `LOAD_POPULATION`, `UNLOAD_POPULATION` against the same handler. `OrderProcessor.process_transfer` becomes a one-line delegate. Existing `test_order_processor_transfer.py` continues to pass.

**Status:** Not Started. See [phase_3_checklist.md](phase_3_checklist.md).

### Phase 4: Port superweapon dispatch and delete legacy methods [Medium]

Replace the inline 6-lambda dict at `order_processor.py:706-725` with a registry-driven loop that iterates `superweapon_registry.SUPERWEAPON_SPECS` and registers a thin adapter (`SuperweaponHandlerAdapter`) per `OrderType`. The adapter delegates to the existing `SuperweaponOrderProcessor.process_*` methods (their internals are out of scope). After registration, **delete** `OrderProcessor.{process_join_fleet, process_colonize, process_transfer, execute_action_order's hardcoded branches, _execute_load, _execute_unload, _execute_fleet_transfer, _load_pod_from_staging_yard, _unload_pod_to_staging_yard, _deploy_drop_pod, _validate_tick_inputs, _execute_fleet_merge, _elect_canonical_merges, _emit_join_cancelled}`. `OrderProcessor` is now a ~150-LOC facade.

**Status:** Not Started. See [phase_4_checklist.md](phase_4_checklist.md).

### Phase 5: Per-handler unit tests + AST static-guard regression [Medium]

Add focused unit tests under `tests/unit/strategy/engine/order_handlers/` for each handler (≥ 5 tests per handler covering: happy path, invalid order type, missing target, validation failure, event emission). Add an AST-walker regression test (`test_order_processor_facade.py`) that:
1. Asserts `order_processor.py` is < 200 LOC.
2. Asserts the `OrderType` enum is referenced ≤ 1 time in `order_processor.py` (the dispatch lookup).
3. Asserts no `if order.type == OrderType.X` branches exist in `OrderProcessor`.
4. Asserts every `OrderType` in `ACTION_ORDER_TYPES ∪ {JOIN_FLEET}` has a registered handler at module import.

Update `docs/systems/strategy_layer.md` and `docs/02_PATTERNS.md` to document the registry pattern + the parallelism with `engine/handlers/` (command handlers).

**Status:** Not Started. See [phase_5_checklist.md](phase_5_checklist.md).

## Verification Checklist

### Project Start (REQUIRED)

- [ ] Read `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/systems/strategy_layer.md`
- [ ] Read full `game/strategy/engine/order_processor.py` (910 lines)
- [ ] Read all files in `game/strategy/engine/handlers/` (command-handler pattern reference)
- [ ] Read `game/strategy/engine/superweapon_order_processor.py:137-319` (spec-driven dispatch reference)
- [ ] Read PROJ-309 sub-phase 3.5 archive (if available) for the command-handler decomposition rationale
- [ ] Read `Projects/protocols/03c_phase_aware_execution.md`
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count, pin in Current State (expected: 15405 passed, 2 skipped per memory)

### After Each Phase

- [ ] Run `pytest tests/unit/strategy/engine/ -v` — all OrderProcessor + handler tests pass
- [ ] Run `pytest tests/integration/strategy/ -v` — strategy-layer integration tests pass
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically (only growth, no regression)
- [ ] Update `Current State` in this plan with handoff context

### Final Verification

- [ ] Sharded suite green; pass count ≥ baseline + new tests added
- [ ] `wc -l game/strategy/engine/order_processor.py` ≤ 200
- [ ] AST guard in `test_order_processor_facade.py` passes (no `if order.type == OrderType.*` branches)
- [ ] All 11 `OrderType` values handled by `OrderProcessor` (the 5 in `ACTION_ORDER_TYPES` minus `ACTIVATE_ABILITY/DEACTIVATE_ABILITY`, plus `JOIN_FLEET`, plus `LOAD/UNLOAD_POPULATION`, plus 6 superweapons) have a registered handler
- [ ] Event payloads bit-identical: `FLEET_JOINED`, `FLEET_JOIN_CANCELLED` (including `reason=` field), `COLONY_FOUNDED` (including `system_name`, `local_hex`), `SHIPS_SELF_DESTRUCTED`, the 6 superweapon events
- [ ] BUG-122 mutual JOIN_FLEET semantics verified by `test_join_fleet_handler.py::test_mutual_pair_canonicalization` (most-ships-wins; smaller-id tiebreak)
- [ ] BUG-70 LOAD_POPULATION auto-resolve verified by `test_transfer_handler.py::test_load_population_auto_resolves_owned_colony`
- [ ] `docs/systems/strategy_layer.md` updated with the order-handler registry section
- [ ] `docs/02_PATTERNS.md` cross-reference between command-handlers and order-handlers added
- [ ] Final commit message format: `feat(PROJ-368): Phase N — <summary>`; `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`

## Audit Log

| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 |      |          |            |

## Completion Checklist

- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] Audit passed (no significant issues)
- [ ] User verified end-to-end (run a save game, end turn, verify JOIN/COLONIZE/TRANSFER/superweapon orders execute as before)
