# Phase 1: Protocol + registry skeleton + JoinFleet PoC

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-368 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Committed)
**Depends on:** (none — root phase)
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/order_handlers/__init__.py`
- `game/strategy/engine/order_handlers/base.py`
- `game/strategy/engine/order_handlers/registry_factory.py`
- `game/strategy/engine/order_handlers/join_fleet.py`
- `game/strategy/engine/order_processor.py`
- `game/strategy/interfaces/engines.py`
- `tests/unit/strategy/engine/order_handlers/__init__.py`
- `tests/unit/strategy/engine/order_handlers/conftest.py`
- `tests/unit/strategy/engine/order_handlers/test_base.py`
- `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py`

**Objective:** Stand up the `IOrderHandler` Protocol, `OrderHandlerRegistry`, `BaseOrderHandler`, and `OrderExecutionResult` in a new `game/strategy/engine/order_handlers/` package. Extract `JoinFleetHandler` covering both single-fleet `process_join_fleet` (lines 110-149) and the BUG-122 three-phase `process_instant_orders` flow (lines 745-821) plus its helpers (`_execute_fleet_merge`, `_validate_tick_inputs`, `_elect_canonical_merges`, `_emit_join_cancelled`). `OrderProcessor.process_join_fleet` and `process_instant_orders` become one-line delegates. Existing `test_order_processor_instant.py` (282 LOC) and `test_order_processor_fleet_merge.py` (88 LOC) remain green throughout.

---

## Pre-flight (TDD baseline)

- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count and pin in plan.md Current State (expected: 15405 passed, 2 skipped per MEMORY.md)
- [ ] Run `pytest tests/unit/strategy/engine/test_order_processor_instant.py tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v` — confirm 100% green at HEAD; pin pass count
- [ ] Run `wc -l game/strategy/engine/order_processor.py` — pin starting LOC (expected: 910)
- [ ] **Resolve Open Question Q3** (is `process_join_fleet` dead code?): run `grep -rn 'process_join_fleet' game/` and report. If zero production hits, mark for deletion in Task 1.10. If hits exist, preserve.
- [ ] **Resolve Open Question Q5** (`order_handlers/` placement): default is `game/strategy/engine/order_handlers/`; confirm with user before creating directory.

---

## Tasks

### Task 1.1: Pin existing JOIN_FLEET test behavior (TDD pin) [Simple]

**File:** `tests/unit/strategy/engine/test_order_processor_instant.py`, `tests/unit/strategy/engine/test_order_processor_fleet_merge.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_instant.py tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v`

- [ ] Run both test files; assert all tests pass on day 0 (no edits yet).
- [ ] Capture baseline pass count for these two files (will be re-verified after every task in this phase).
- [ ] **Verify:** zero failures. If any fail, STOP — investigate before proceeding.

**Notes:**

### Task 1.2: Create `order_handlers/__init__.py` and `order_handlers/base.py` skeleton [Medium]

**File:** `game/strategy/engine/order_handlers/__init__.py` (new), `game/strategy/engine/order_handlers/base.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_base.py -v`

- [ ] Create empty `game/strategy/engine/order_handlers/__init__.py` (Python package marker)
- [ ] Create `game/strategy/engine/order_handlers/base.py` with:
  - [ ] Module docstring referencing PROJ-368 and the parallel with `engine/handlers/base.py`
  - [ ] `from __future__ import annotations` at top
  - [ ] `OrderExecutionResult` dataclass (frozen=False) with fields: `success: bool`, `fleet_consumed: bool = False`, `message: str = ""`, `merged: bool = False`, `cancelled: bool = False`, `colonized: bool = False`, `planet_name: str | None = None`, `amount_transferred: int = 0`
  - [ ] `@runtime_checkable class IOrderHandler(Protocol)`:
    - [ ] `supported_order_types` property returning `tuple[OrderType, ...]`
    - [ ] `execute_action_order(self, fleet, empire, galaxy, component_registry=None, empires=None) -> OrderExecutionResult` method
  - [ ] `class BaseOrderHandler` mixin with:
    - [ ] `__init__(self, *, event_bus=None)` storing `self._event_bus`
    - [ ] `_emit_event(self, event_type, *, category, empire_id, message, **kwargs)` that null-checks `self._event_bus` and calls `self._event_bus.log_event(event_type, category=category, empire_id=empire_id, message=message, **kwargs)`
  - [ ] `class OrderHandlerRegistry`:
    - [ ] `__init__(self) -> None: self._by_type: dict[OrderType, IOrderHandler] = {}`
    - [ ] `register(self, order_type: OrderType, handler: IOrderHandler) -> None` (rejects duplicate via `ValueError`)
    - [ ] `get(self, order_type: OrderType) -> IOrderHandler | None`
    - [ ] `__contains__(self, order_type: OrderType) -> bool`
    - [ ] `all_registered(self) -> frozenset[OrderType]`
- [ ] Import `OrderType` from `game.strategy.data.order_types`
- [ ] **Verify:** `python -c "from game.strategy.engine.order_handlers.base import IOrderHandler, OrderHandlerRegistry, OrderExecutionResult, BaseOrderHandler"` succeeds with no import errors

**Notes:**

### Task 1.3: Add `tests/unit/strategy/engine/order_handlers/test_base.py` [Medium]

**File:** `tests/unit/strategy/engine/order_handlers/__init__.py` (new), `tests/unit/strategy/engine/order_handlers/test_base.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_base.py -v`

- [ ] Create empty `tests/unit/strategy/engine/order_handlers/__init__.py`
- [ ] Write `test_base.py` with ≥ 6 tests:
  - [ ] `test_registry_register_and_get` — register a `MagicMock(spec=IOrderHandler)` for `OrderType.JOIN_FLEET`; `registry.get(OrderType.JOIN_FLEET)` returns it
  - [ ] `test_registry_get_unknown_returns_none` — `registry.get(OrderType.MOVE)` returns `None` on empty registry
  - [ ] `test_registry_register_duplicate_raises` — registering the same `OrderType` twice raises `ValueError`
  - [ ] `test_registry_contains_operator` — `OrderType.JOIN_FLEET in registry` after registration
  - [ ] `test_registry_all_registered_returns_frozenset` — type and contents
  - [ ] `test_order_execution_result_default_values` — assert all default field values
  - [ ] `test_base_order_handler_emit_event_with_no_bus` — `BaseOrderHandler(event_bus=None)._emit_event(...)` is a no-op (no exception)
  - [ ] `test_base_order_handler_emit_event_with_bus` — bus's `log_event` is called with the right kwargs
- [ ] **Verify:** all tests pass

**Notes:**

### Task 1.4: Decide handler-method shape for `process_instant_orders` [Simple]

**File:** Document the decision inline in `game/strategy/engine/order_handlers/join_fleet.py` (will be created in Task 1.5)
**Tests:** N/A (architectural decision)

- [ ] Choose ONE of two options (either is acceptable per `decisions.md` row 8):
  - **Option A:** Add `process_instant_orders(self, empires) -> List[Tuple[Empire, Fleet]]` to the `IOrderHandler` Protocol; default implementation in `BaseOrderHandler` raises `NotImplementedError("instant order processing not supported for this handler")`. Only `JoinFleetHandler` overrides.
  - **Option B:** Make `process_instant_orders` a `JoinFleetHandler`-only public method; the facade calls `registry.get(OrderType.JOIN_FLEET).process_instant_orders(empires)` with an `isinstance` or `hasattr` check.
- [ ] Document the choice and rationale as a comment at the top of `join_fleet.py`. Update `decisions.md` with a new row resolving row 8.
- [ ] **Verify:** decision is consistent with the Phase 1 task structure below (Tasks 1.5 and 1.7 may need minor adjustment).

**Notes:**

### Task 1.5: Implement `JoinFleetHandler` in `order_handlers/join_fleet.py` [Complex]

**File:** `game/strategy/engine/order_handlers/join_fleet.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_instant.py tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v`

- [ ] Create `game/strategy/engine/order_handlers/join_fleet.py` with module docstring referencing PROJ-368 and BUG-122
- [ ] `class JoinFleetHandler(BaseOrderHandler)`:
  - [ ] `supported_order_types = (OrderType.JOIN_FLEET,)` as a class-level property
  - [ ] `execute_action_order(self, fleet, empire, galaxy, component_registry=None, empires=None) -> OrderExecutionResult` — port the body of `OrderProcessor.process_join_fleet` (order_processor.py:110-149) verbatim. Replace returns of `JoinFleetResult(merged=...)` with `OrderExecutionResult(success=..., merged=..., cancelled=...)`. Preserve every log message verbatim except prefix `OrderProcessor:` → `JoinFleetHandler:` (per decisions.md row 10).
  - [ ] `process_instant_orders(self, empires) -> List[Tuple[Empire, Fleet]]` — port the body of `OrderProcessor.process_instant_orders` (order_processor.py:745-821) verbatim. Includes the BUG-122 three-phase pipeline.
  - [ ] `_validate_tick_inputs(self, empires) -> None` — port verbatim from order_processor.py:734-743
  - [ ] `_execute_fleet_merge(self, fleet, target_fleet, empire) -> None` — port verbatim from order_processor.py:86-108
  - [ ] `_elect_canonical_merges(self, candidates) -> List[Tuple]` — port verbatim from order_processor.py:823-883
  - [ ] `_emit_join_cancelled(self, fleet, target_fleet, empire, *, reason: str) -> None` — port verbatim from order_processor.py:885-910. Refactor to use `self._emit_event(...)` from `BaseOrderHandler`.
- [ ] All public + private methods must have return-type annotations per docs/03_CONVENTIONS.md §8 (modern PEP 604 syntax)
- [ ] Verify file ≤ 250 LOC
- [ ] **Verify:** `python -c "from game.strategy.engine.order_handlers.join_fleet import JoinFleetHandler"` succeeds
- [ ] **Verify:** the existing tests at `test_order_processor_instant.py` and `test_order_processor_fleet_merge.py` still pass (they still call `OrderProcessor.process_*`; nothing has changed there yet — the green status confirms no import-time side effects broke things)

**Notes:**

### Task 1.6: Add `registry_factory.py` [Simple]

**File:** `game/strategy/engine/order_handlers/registry_factory.py` (new)
**Tests:** N/A (covered by Task 1.7's facade tests)

- [ ] Create `game/strategy/engine/order_handlers/registry_factory.py`
- [ ] Module docstring referencing PROJ-368 and the parallel with `engine/handlers/registry_factory.py`
- [ ] `def create_default_order_handler_registry(*, event_bus) -> OrderHandlerRegistry`:
  - [ ] Construct `OrderHandlerRegistry()`
  - [ ] Construct `JoinFleetHandler(event_bus=event_bus)`; register against `OrderType.JOIN_FLEET`
  - [ ] Phase 1: only one handler. (Phases 2–4 will append.)
  - [ ] Return the registry
- [ ] Update `order_handlers/__init__.py` to re-export `JoinFleetHandler`, `create_default_order_handler_registry`, plus the names from `base.py`
- [ ] **Verify:** `python -c "from game.strategy.engine.order_handlers import create_default_order_handler_registry; r = create_default_order_handler_registry(event_bus=None); from game.strategy.data.order_types import OrderType; assert OrderType.JOIN_FLEET in r"` succeeds

**Notes:**

### Task 1.7: Wire facade — `OrderProcessor` builds the registry and delegates [Medium]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_instant.py tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v` then full `pytest tests/unit/strategy/engine/ tests/integration/strategy/ -v`

- [ ] In `OrderProcessor.__init__`, after `self._superweapon_processor = ...`:
  - [ ] Add: `from game.strategy.engine.order_handlers import create_default_order_handler_registry`
  - [ ] Add: `self._handler_registry = create_default_order_handler_registry(event_bus=event_bus)`
- [ ] Replace `OrderProcessor.process_join_fleet` body (lines 110-149) with:
  ```python
  handler = self._handler_registry.get(OrderType.JOIN_FLEET)
  result = handler.execute_action_order(fleet, empire, galaxy)
  return JoinFleetResult(merged=result.merged, cancelled=result.cancelled)
  ```
- [ ] Replace `OrderProcessor.process_instant_orders` body (lines 745-821) with:
  ```python
  handler = self._handler_registry.get(OrderType.JOIN_FLEET)
  return handler.process_instant_orders(empires)
  ```
- [ ] Keep `_execute_fleet_merge`, `_validate_tick_inputs`, `_elect_canonical_merges`, `_emit_join_cancelled` defined on `OrderProcessor` for now (Phase 4 deletes them); the live code path is the handler's copies.
- [ ] **Verify:** `pytest tests/unit/strategy/engine/test_order_processor_instant.py tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v` — every pre-existing test passes
- [ ] **Verify:** `pytest tests/integration/strategy/test_mutual_join_rendezvous.py -v` — BUG-122 end-to-end smoke passes

**Notes:**

### Task 1.8: Add focused unit tests for `JoinFleetHandler` [Medium]

**File:** `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py -v`

- [ ] Lift fixture helpers from `test_order_processor_instant.py:24-52` and `test_order_processor_fleet_merge.py` (use `_real_fleet`, `_empire_with`, `_captured` patterns) into `tests/unit/strategy/engine/order_handlers/conftest.py`
- [ ] Write ≥ 8 focused tests against `JoinFleetHandler` directly (no `OrderProcessor`):
  - [ ] `test_execute_action_order_no_order_returns_unmerged`
  - [ ] `test_execute_action_order_target_destroyed_pops_and_cancels` — covers `target_fleet is None` branch
  - [ ] `test_execute_action_order_co_located_merges`
  - [ ] `test_execute_action_order_not_co_located_pops_without_merge`
  - [ ] `test_process_instant_orders_validates_orders_not_none` — `ValidationException`
  - [ ] `test_process_instant_orders_collects_co_located_candidates_only`
  - [ ] `test_process_instant_orders_mutual_pair_canonicalization_most_ships_wins` — BUG-122 election rule
  - [ ] `test_process_instant_orders_mutual_pair_tie_smaller_id_wins` — BUG-122 deterministic tiebreak
  - [ ] `test_process_instant_orders_phase_c_aliveness_skip_absorbed_source` — `absorbed_by_other_merge` reason
  - [ ] `test_process_instant_orders_phase_c_aliveness_skip_absorbed_target` — `target_absorbed_mid_iteration` reason; verify the now-stale order is popped
  - [ ] `test_process_instant_orders_emits_fleet_joined_event_payload` — exact payload dict equality
  - [ ] `test_process_instant_orders_emits_fleet_join_cancelled_with_reason_field`
- [ ] All event-payload tests use exact-dict-equality (not `.assert_called`) for risk R2
- [ ] **Verify:** all new tests pass

**Notes:**

### Task 1.9: Update `IOrderProcessor` ABC docstring [Simple]

**File:** `game/strategy/interfaces/engines.py:168-230`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v`

- [ ] Update the class docstring at line 169 to reference PROJ-368: "PROJ-368: implementation now uses a per-OrderType handler registry. See `game.strategy.engine.order_handlers`."
- [ ] **DO NOT** change any method signatures.
- [ ] **Verify:** `test_turn_engine_lazy_properties.py` still passes; the IOrderProcessor isinstance check at line 182 still holds.

**Notes:**

### Task 1.10: (Conditional on Q3) Delete `process_join_fleet` if dead production code [Simple]

**File:** `game/strategy/engine/order_processor.py`, `tests/unit/strategy/engine/test_order_processor_fleet_merge.py`
**Tests:** Full sharded suite

- [ ] **Conditional:** only execute if Pre-flight grep showed zero production callers.
- [ ] Delete the `OrderProcessor.process_join_fleet` method entirely (it's a one-line delegate after Task 1.7; safe to delete if no production callers exist)
- [ ] Delete `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` (88 LOC, sole consumer)
- [ ] **Verify:** sharded suite green
- [ ] **Verify:** no remaining grep hit for `process_join_fleet` in the entire repo

**Notes:** If user resolved Q3 as "preserve", skip this task entirely.

### Task 1.11: Run sharded suite + LOC check [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ baseline (Pre-flight) + new tests added in Task 1.3 + Task 1.8
- [ ] Run `wc -l game/strategy/engine/order_processor.py` — pin LOC. Expected: ~880 (down from 910 if Task 1.10 ran; flat otherwise). Phase 4 will drop it to ≤ 200.
- [ ] **Verify:** zero regressions

**Notes:**

### Task 1.12: Run `phase_complete.py` [Simple]

**Tests:** Per 03c protocol step 6

- [ ] Stage only files in this checklist (`git status --short`)
- [ ] Commit message: `feat(PROJ-368): Phase 1 — IOrderHandler protocol + OrderHandlerRegistry + JoinFleetHandler PoC`
- [ ] Sign-off: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-368 phase_1 --repo .worktrees/phases/PROJ-368/phase_1` (or working dir if running inline)
- [ ] **Verify:** state file shows phase_1 status `committed`; cumulative review dispatched.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `game/strategy/engine/order_handlers/` package exists with 4 modules (`__init__.py`, `base.py`, `registry_factory.py`, `join_fleet.py`)
- [ ] `OrderProcessor.process_join_fleet` and `process_instant_orders` are one-line delegates (or deleted, per Q3)
- [ ] All pre-existing JOIN_FLEET tests still pass; new per-handler tests pass
- [ ] BUG-122 mutual-pair canonicalization, Phase C aliveness, both cancellation reasons preserved
- [ ] Sharded suite green; pass count grew by ≥ 14 (the new tests in Tasks 1.3 + 1.8)
- [ ] Update status at top of this file to `Complete (Committed)` after `phase_complete.py` succeeds
- [ ] Update plan.md phase table row to `Complete (Committed)`
- [ ] Update plan.md Current State to point to Phase 2
