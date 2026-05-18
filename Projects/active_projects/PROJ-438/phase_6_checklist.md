# Phase 6: Issuer-aware execution contract cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 5 (typed planet intents landed)
**Objective:** Replace `ActionExecutionEngine._execute_planet_action`'s private `OrderProcessor._handler_registry` reach-in + `TypeError` fallback with one explicit unified issuer-aware execution contract. Reconcile the launch/recovery handler signature split so a single canonical call works for both.

---

## Tasks

### Task 6.1: Failing test for the unified contract
**Files:** `tests/unit/strategy/engine/test_issuer_execution_contract.py` (new)

- [x] Pin that `IOrderHandler` Protocol declares `execute_for_issuer`.
- [x] Pin that `RecoverFightersOrderHandler.execute_for_issuer` and `RecoverSatellitesOrderHandler.execute_for_issuer` accept `galaxy` + `registries` kwargs (and may ignore them).
- [x] Pin that `LaunchFightersOrderHandler.execute_for_issuer` retains its existing 5-kwarg signature.
- [x] Pin that `OrderProcessor.get_handler(order_type)` exists as a public accessor.
- [x] Pin that `action_execution_engine.py` source no longer contains `_handler_registry` (no private reach-in) and that `_execute_planet_action` source no longer contains `except TypeError`.
- [x] Confirm 8/8 tests fail before any production change.

### Task 6.2: Unify the contract
**Files:** `game/strategy/engine/order_handlers/base.py`, `game/strategy/engine/order_handlers/recover_fighters.py`, `game/strategy/engine/order_handlers/recover_satellites.py`, `game/strategy/engine/order_processor.py`

- [x] Add `execute_for_issuer(*, issuer, order_owner, empire, galaxy=None, registries=None) -> OrderExecutionResult` to `IOrderHandler` Protocol with docstring pointing at the planet-FMS path.
- [x] Update `RecoverFightersOrderHandler.execute_for_issuer` to accept `galaxy` + `registries` (ignored via `del`); update docstring + comment.
- [x] Update `RecoverSatellitesOrderHandler.execute_for_issuer` to accept `galaxy` + `registries` (ignored via `del`).
- [x] Add `OrderProcessor.get_handler(order_type) -> IOrderHandler | None` as the public accessor (imports `IOrderHandler` from `order_handlers.base`).

### Task 6.3: Update `ActionExecutionEngine._execute_planet_action`
**Files:** `game/strategy/engine/action_execution_engine.py`

- [x] Replace `getattr(self._order_processor, "_handler_registry", None)` + `registry.get(order.type)` with `self._order_processor.get_handler(order.type)`.
- [x] Delete the `try / except TypeError` fallback — one canonical call with all 5 kwargs.
- [x] Update the docstring to reference PROJ-438 Phase 6 and explain the unified contract.

### Task 6.4: Sweep + sharded suite
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] 153 affected tests green (action_execution_engine + order_handlers + new contract).
- [x] Run the canonical sharded suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 0 baseline)
- [x] Game still runnable / savable / loadable (semantics unchanged: same handler dispatched with same kwargs; the TypeError fallback was never reached during normal operation)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 7
- [x] `python Projects/scripts/validate_phase.py PROJ-438 6` passes
