# Phase 3: Port Transfer family (TRANSFER, LOAD_POPULATION, UNLOAD_POPULATION)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-368 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1 (verified)
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/order_handlers/transfer.py`
- `game/strategy/engine/order_handlers/registry_factory.py`
- `game/strategy/engine/order_handlers/__init__.py`
- `game/strategy/engine/order_processor.py`
- `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py`

**Objective:** Extract `TransferHandler` covering `process_transfer` (lines 251-364), `_execute_load` (lines 398-467), `_execute_unload` (lines 469-530), `_execute_fleet_transfer` (lines 366-396), `_load_pod_from_staging_yard` (lines 532-585), `_unload_pod_to_staging_yard` (lines 587-616). Decompose the 5 implicit branches in `process_transfer` into 7 explicit `_dispatch_*` private methods (planet load × {resource, passengers, drop_pod}, planet unload × {resource, passengers, drop_pod}, fleet-to-fleet). Register `TRANSFER`, `LOAD_POPULATION`, `UNLOAD_POPULATION` against the same handler instance. `OrderProcessor.process_transfer` becomes a one-line delegate. Existing `test_order_processor_transfer.py` (424 LOC) and integration tests continue to pass.

**This is the most complex phase.** Single largest LOC migration (~280 LOC); largest single new file (~400 LOC); preserves the 3 transitive bug fixes (BUG-70 LOAD_POPULATION auto-resolve, PROJ-343 T1.1 target_fleet_id persistence, BUG-122 fleet-to-fleet co-location validator skip).

---

## Pre-flight

- [ ] Phase 1 status `verified` (Phase 3 does NOT depend on Phase 2; can run parallel-with-Phase-2 in 03c)
- [ ] Sharded suite green at end of Phase 1
- [ ] Run `pytest tests/unit/strategy/engine/test_order_processor_transfer.py tests/unit/strategy/engine/test_fleet_order_transfer.py tests/unit/strategy/engine/test_fleet_transfer_extended.py tests/unit/strategy/engine/test_pod_transfer.py -v` — confirm 100% green at HEAD
- [ ] Read all 7 dispatch branches in `process_transfer` and the helpers carefully — this is the longest single piece of work in PROJ-368

---

## Tasks

### Task 3.1: Pin existing TRANSFER test behavior (TDD pin) [Simple]

**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_transfer.py tests/unit/strategy/engine/test_fleet_order_transfer.py tests/unit/strategy/engine/test_fleet_transfer_extended.py tests/unit/strategy/engine/test_pod_transfer.py tests/integration/strategy/test_pod_transfer.py tests/integration/strategy/test_fleet_order_transfer.py -v`

- [ ] Run all 6 files; pin pass count
- [ ] **Verify:** zero failures

**Notes:**

### Task 3.2: Implement `TransferHandler` skeleton with `execute_action_order` + 7 `_dispatch_*` stubs [Medium]

**File:** `game/strategy/engine/order_handlers/transfer.py` (new)
**Tests:** N/A yet (skeleton)

- [ ] Create `game/strategy/engine/order_handlers/transfer.py` with module docstring referencing the 7 dispatch branches and the 3 preserved bug fixes
- [ ] `class TransferHandler(BaseOrderHandler)`:
  - [ ] `supported_order_types = (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION)`
  - [ ] `execute_action_order(self, fleet, empire, galaxy, component_registry=None, empires=None) -> OrderExecutionResult` — skeleton with docstring + 7-branch dispatch table comment
  - [ ] Stub each `_dispatch_*` method with a `raise NotImplementedError("filled in next task")`
  - [ ] Stub `_resolve_target_fleet_by_id(self, target_fleet_id, empire, galaxy)` private method
  - [ ] Stub `_load_pod_from_staging_yard`, `_unload_pod_to_staging_yard` as private methods
- [ ] **Verify:** import works

**Notes:**

### Task 3.3: Port `execute_action_order` body and BUG-70 + target resolution logic [Complex]

**File:** `game/strategy/engine/order_handlers/transfer.py`
**Tests:** N/A yet (`process_transfer` test file still drives `OrderProcessor`; full validation at Task 3.5)

- [ ] In `TransferHandler.execute_action_order`, port the prologue from `OrderProcessor.process_transfer` lines 274-326:
  - [ ] Order shape validation (lines 274-282)
  - [ ] Param extraction (lines 284-289)
  - [ ] Target resolution including BUG-70 LOAD_POPULATION auto-resolve (lines 292-326)
  - [ ] Validator call (lines 329-346)
- [ ] Implement `_resolve_target_fleet_by_id(self, target_fleet_id, empire, galaxy) -> Fleet | None` — port lines 308-326 verbatim (the `getattr(galaxy, 'empires', [])` + `empire.fleets` fallback). Comment: `# PROJ-368: brittle. PROJ-343 T1.1 fixed at handler level; resolver brittleness is future work.`
- [ ] After validation passes, dispatch to one of 7 `_dispatch_*` methods:
  ```python
  from game.core.protocols import is_planet, is_fleet
  if is_planet(target):
      if direction == "load":
          if cargo_type == "drop_pod":
              transferred = self._dispatch_drop_pod_load(fleet, target, params)
          elif cargo_type == "passengers":
              transferred = self._dispatch_load_planet_passengers(fleet, target, params)
          else:
              transferred = self._dispatch_load_planet_resource(fleet, target, params)
      else:  # unload
          if cargo_type == "drop_pod":
              transferred = self._dispatch_drop_pod_unload(fleet, target, params)
          elif cargo_type == "passengers":
              transferred = self._dispatch_unload_planet_passengers(fleet, target, empire, params)
          else:
              transferred = self._dispatch_unload_planet_resource(fleet, target, params)
  elif is_fleet(target):
      transferred = self._dispatch_fleet_to_fleet(fleet, target, params)
  ```
- [ ] Pop the order; return `OrderExecutionResult(success=True, amount_transferred=transferred)`

**Notes:**

### Task 3.4: Implement the 7 `_dispatch_*` methods (port from `_execute_load`/`_execute_unload`/`_execute_fleet_transfer`) [Complex]

**File:** `game/strategy/engine/order_handlers/transfer.py`
**Tests:** Will be validated at Task 3.5

- [ ] `_dispatch_load_planet_resource(fleet, planet, params) -> int` — port `_execute_load` lines 449-467 (resource branch)
- [ ] `_dispatch_load_planet_passengers(fleet, planet, params) -> int` — port `_execute_load` lines 413-446 (passengers branch)
- [ ] `_dispatch_drop_pod_load(fleet, planet, params) -> int` — port `_execute_load` line 411 + `_load_pod_from_staging_yard`. Make `_load_pod_from_staging_yard` a private method on the handler (port from order_processor.py:532-585 verbatim).
- [ ] `_dispatch_unload_planet_resource(fleet, planet, params) -> int` — port `_execute_unload` lines 519-530 (resource branch)
- [ ] `_dispatch_unload_planet_passengers(fleet, planet, empire, params) -> int` — port `_execute_unload` lines 484-517 (passengers branch). The `empire.race_config.race_id` fallback at line 502 requires the `empire` arg.
- [ ] `_dispatch_drop_pod_unload(fleet, planet, params) -> int` — port `_execute_unload` line 482 + `_unload_pod_to_staging_yard`. Port `_unload_pod_to_staging_yard` (order_processor.py:587-616).
- [ ] `_dispatch_fleet_to_fleet(fleet, target_fleet, params) -> int` — port `_execute_fleet_transfer` (order_processor.py:366-396) verbatim
- [ ] Each dispatcher: replace `self._execute_*` and `_load/unload_pod_*` calls with `self._dispatch_*` / private method calls
- [ ] Verify file ≤ 400 LOC
- [ ] **Verify:** import + module-level checks

**Notes:**

### Task 3.5: Update `registry_factory.py` to register `TransferHandler` against 3 OrderType keys [Simple]

**File:** `game/strategy/engine/order_handlers/registry_factory.py`, `game/strategy/engine/order_handlers/__init__.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_base.py -v`

- [ ] In `create_default_order_handler_registry`:
  - [ ] Construct one `TransferHandler(event_bus=event_bus)` instance
  - [ ] Register the **same instance** against `OrderType.TRANSFER`, `OrderType.LOAD_POPULATION`, `OrderType.UNLOAD_POPULATION`
- [ ] Update `__init__.py` re-exports
- [ ] **Verify:** all 3 OrderType values present in registry; same handler instance for each

**Notes:**

### Task 3.6: Wire `OrderProcessor.process_transfer` to delegate [Medium]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_transfer.py -v`

- [ ] Replace `OrderProcessor.process_transfer` body (lines 251-364) with:
  ```python
  handler = self._handler_registry.get(order.type) if (order := fleet.get_current_order()) else None
  # Note: order may be None (test sets up fleet with no order) — handler.execute_action_order
  # itself handles the no-order case by returning success=False, message="No TRANSFER order".
  # But tests assert on TransferResult, so handle null-order at the facade.
  if handler is None:
      return TransferResult(success=False, message="No TRANSFER order")
  result = handler.execute_action_order(fleet, empire, galaxy)
  return TransferResult(success=result.success, amount_transferred=result.amount_transferred, message=result.message)
  ```
- [ ] **DO NOT** delete `_execute_load`/`_execute_unload`/`_execute_fleet_transfer`/`_load_pod_from_staging_yard`/`_unload_pod_to_staging_yard` yet — Phase 4 deletes them. The live copies are in `TransferHandler`.
- [ ] **Verify:** `pytest tests/unit/strategy/engine/test_order_processor_transfer.py tests/unit/strategy/engine/test_fleet_order_transfer.py tests/unit/strategy/engine/test_fleet_transfer_extended.py tests/unit/strategy/engine/test_pod_transfer.py -v` — every test passes
- [ ] **Verify:** `pytest tests/integration/strategy/test_pod_transfer.py tests/integration/strategy/test_fleet_order_transfer.py -v` passes

**Notes:**

### Task 3.7: Update `execute_action_order`'s TRANSFER branch to use registry [Medium]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py -v`

- [ ] In `OrderProcessor.execute_action_order`, find the TRANSFER/LOAD/UNLOAD branch (lines 700-702)
- [ ] The current code is `self.process_transfer(fleet, empire, galaxy)`. Since `process_transfer` is now a delegate to the registry, this already works correctly.
- [ ] **Verify:** existing tests pass

**Notes:**

### Task 3.8: Add focused unit tests for `TransferHandler` [Complex]

**File:** `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_transfer_handler.py -v`

- [ ] Lift fixture helpers from `test_order_processor_transfer.py` into `tests/unit/strategy/engine/order_handlers/conftest.py`
- [ ] Write ≥ 12 focused tests against `TransferHandler` directly:
  - [ ] `test_no_order_returns_failure`
  - [ ] `test_invalid_params_pops_and_returns_failure`
  - [ ] `test_validation_failure_pops_and_returns_failure`
  - [ ] `test_dispatch_load_planet_resource` — assert int returned, planet stockpile decreased, fleet cargo increased
  - [ ] `test_dispatch_load_planet_passengers` — assert pop.count decreased, fleet cargo increased
  - [ ] `test_dispatch_load_planet_passengers_specific_species` — `species_id` filter works
  - [ ] `test_dispatch_drop_pod_load_reverse_iteration` — staging yard reverse-iteration semantics preserved
  - [ ] `test_dispatch_unload_planet_resource` — fleet cargo decreased, planet stockpile increased
  - [ ] `test_dispatch_unload_planet_passengers_creates_species_population` — append branch covered
  - [ ] `test_dispatch_unload_planet_passengers_existing_species_increments` — happy path
  - [ ] `test_dispatch_drop_pod_unload`
  - [ ] `test_dispatch_fleet_to_fleet_load_direction`
  - [ ] `test_dispatch_fleet_to_fleet_unload_direction`
  - [ ] `test_bug_70_load_population_auto_resolves_owned_colony_at_fleet_hex` — BUG-70 preservation
  - [ ] `test_bug_70_no_owned_colony_skips_silently` — BUG-70 no-op path
  - [ ] `test_target_fleet_resolves_via_galaxy_empires` — happy path
  - [ ] `test_target_fleet_resolves_via_empire_fleets_fallback` — fallback path
  - [ ] `test_target_fleet_id_persisted_in_transfer_params` — PROJ-343 T1.1 preservation
- [ ] All event-payload tests use exact-dict-equality

**Notes:**

### Task 3.9: Run sharded suite + LOC check [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ Phase 2 baseline + new tests
- [ ] `wc -l game/strategy/engine/order_processor.py` — expected ~500 (down ~280 from Phase 2 end)
- [ ] **Verify:** zero regressions

**Notes:**

### Task 3.10: Run `phase_complete.py` [Simple]

- [ ] Commit message: `feat(PROJ-368): Phase 3 — extract TransferHandler with 7 explicit dispatch branches`
- [ ] Sign-off
- [ ] Run `phase_complete.py PROJ-368 phase_3`
- [ ] **Verify:** state shows phase_3 `committed`; cumulative review dispatched.

**Notes:**

---

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] `TransferHandler` exists with 7 `_dispatch_*` methods
- [ ] `OrderProcessor.process_transfer` is a one-line delegate
- [ ] All TRANSFER tests pass (4 unit files + 2 integration files)
- [ ] BUG-70 + PROJ-343 T1.1 preservation verified
- [ ] Sharded suite green
- [ ] Update phase status to `Complete (Committed)`
- [ ] Update plan.md
