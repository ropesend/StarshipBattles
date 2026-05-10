# Phase 4: Port superweapon dispatch and delete legacy methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-368 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Committed)
**Depends on:** phase_2 (verified) AND phase_3 (verified)
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/order_handlers/superweapons.py`
- `game/strategy/engine/order_handlers/registry_factory.py`
- `game/strategy/engine/order_handlers/__init__.py`
- `game/strategy/engine/order_processor.py`
- `game/strategy/engine/superweapon_order_processor.py`
- `tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py`

**Objective:** Replace the inline 6-lambda dict at `order_processor.py:706-725` with a registry-driven loop that iterates `superweapon_registry.SUPERWEAPON_SPECS` and registers a thin `SuperweaponHandlerAdapter` per spec. **5 adapters** (SELF_DESTRUCT was lifted in Phase 2). After registration, **delete** all the legacy methods on `OrderProcessor` that Phases 1–3 left as parallel copies. `OrderProcessor` ends as a ~150-LOC facade.

This is the highest-risk phase (R8). One conceptual change, one commit. The cumulative review at the boundary catches anything that slipped through.

---

## Pre-flight

- [ ] Phase 2 AND Phase 3 status both `verified`
- [ ] Sharded suite green at end of Phase 3
- [ ] Run `pytest tests/unit/strategy/engine/test_superweapon_*.py -v` — confirm 100% green
- [ ] Re-read `game/strategy/engine/superweapon_order_processor.py:137-319` (the `execute_superweapon` dispatcher) and `game/strategy/services/superweapon_registry.py` (the `SUPERWEAPON_SPECS` table)
- [ ] List the 5 specs in `SUPERWEAPON_SPECS` (expected: IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE; SELF_DESTRUCT is **not** in SUPERWEAPON_SPECS — it was always a separate path)

---

## Tasks

### Task 4.1: Pin existing superweapon test behavior (TDD pin) [Simple]

**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py tests/unit/strategy/engine/test_superweapon_edge_cases.py tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py tests/unit/strategy/engine/test_superweapon_stabilizers.py -v`

- [ ] Run all 5 superweapon test files
- [ ] Pin pass count

**Notes:**

### Task 4.2: Implement `SuperweaponHandlerAdapter` in `order_handlers/superweapons.py` [Medium]

**File:** `game/strategy/engine/order_handlers/superweapons.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py -v` (Task 4.4)

- [ ] Create `game/strategy/engine/order_handlers/superweapons.py` with module docstring
- [ ] `class SuperweaponHandlerAdapter(BaseOrderHandler)`:
  - [ ] `__init__(self, *, spec: SuperweaponSpec, processor: SuperweaponOrderProcessor) -> None`
  - [ ] `supported_order_types` returns `(self._spec.order_type,)`
  - [ ] `execute_action_order(self, fleet, empire, galaxy, component_registry=None, empires=None) -> OrderExecutionResult`:
    - [ ] Build method name: `f"process_{self._spec.order_type.name.lower()}"`
    - [ ] Call: `result: SuperweaponResult = getattr(self._processor, method_name)(fleet, empire, galaxy, empires or [], component_registry)`
    - [ ] Reshape: `return OrderExecutionResult(success=result.success, fleet_consumed=result.fleet_consumed, message=result.message)`
- [ ] `def build_superweapon_handlers(processor: SuperweaponOrderProcessor) -> list[SuperweaponHandlerAdapter]`:
  - [ ] Iterate `SUPERWEAPON_SPECS`
  - [ ] Skip any spec whose order_type == `OrderType.SELF_DESTRUCT` (defensive — shouldn't be in SUPERWEAPON_SPECS but explicit guard)
  - [ ] Yield one adapter per spec
- [ ] Verify file ≤ 100 LOC
- [ ] **Verify:** import works

**Notes:**

### Task 4.3: Update `registry_factory.py` to register superweapon adapters [Medium]

**File:** `game/strategy/engine/order_handlers/registry_factory.py`, `game/strategy/engine/order_handlers/__init__.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_base.py -v`

- [ ] In `create_default_order_handler_registry`:
  - [ ] Add a kwarg `superweapon_processor: SuperweaponOrderProcessor | None = None`. If None, construct internally.
  - [ ] After `TransferHandler` registrations, loop `for adapter in build_superweapon_handlers(superweapon_processor): registry.register(adapter.supported_order_types[0], adapter)`
- [ ] Update `__init__.py` re-exports to include `SuperweaponHandlerAdapter`
- [ ] **Verify:** `python -c "from game.strategy.engine.order_handlers import create_default_order_handler_registry; from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor; from game.strategy.data.order_types import OrderType; r = create_default_order_handler_registry(event_bus=None, superweapon_processor=SuperweaponOrderProcessor()); assert OrderType.IMPLODE_PLANET in r; assert OrderType.STELLERATE_STAR in r; assert OrderType.OPEN_WARP_POINT in r; assert OrderType.CLOSE_WARP_POINT in r; assert OrderType.CREATE_DYSON_SPHERE in r"`

**Notes:**

### Task 4.4: Add focused unit tests for the superweapon adapter dispatch [Medium]

**File:** `tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py -v`

- [ ] Write ≥ 6 tests:
  - [ ] `test_adapter_supported_order_types_matches_spec`
  - [ ] `test_adapter_dispatches_to_correct_method` for each of the 5 specs (parametrize)
  - [ ] `test_adapter_reshapes_superweapon_result_to_order_execution_result`
  - [ ] `test_adapter_passes_empires_or_empty_list_to_processor`
  - [ ] `test_build_superweapon_handlers_yields_5_adapters` — count check (no SELF_DESTRUCT)
  - [ ] `test_build_superweapon_handlers_skips_self_destruct_defensive` — even if hypothetically added to SUPERWEAPON_SPECS

**Notes:**

### Task 4.5: Rewrite `OrderProcessor.execute_action_order` as a registry lookup [Medium]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/ -v`

- [ ] Replace `OrderProcessor.execute_action_order` body (lines 655-732) with:
  ```python
  def execute_action_order(
      self,
      fleet: Fleet,
      empire: 'Empire',
      galaxy: 'Galaxy',
      component_registry: Optional[Dict[str, Any]] = None,
      empires: Optional[List['Empire']] = None,
  ) -> bool:
      order = fleet.get_current_order()
      if order is None:
          return False
      handler = self._handler_registry.get(order.type)
      if handler is None:
          return False
      result = handler.execute_action_order(
          fleet, empire, galaxy,
          component_registry=component_registry,
          empires=empires,
      )
      return result.fleet_consumed
  ```
- [ ] **DELETE** the inline `superweapon_handlers = {OrderType.IMPLODE_PLANET: lambda: ...}` dict (lines 706-725)
- [ ] **DELETE** the COLONIZE branch (lines 689-697)
- [ ] **DELETE** the TRANSFER/LOAD/UNLOAD branch (lines 699-702)
- [ ] **Verify:** every superweapon test still passes; `test_order_processor_colonize.py` and `test_order_processor_transfer.py` still pass

**Notes:**

### Task 4.6: Delete the legacy private methods on `OrderProcessor` [Medium]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** Full sharded suite

- [ ] **DELETE** `_execute_fleet_merge` (lines 86-108) — moved to `JoinFleetHandler` in Phase 1
- [ ] **DELETE** `_execute_fleet_transfer` (lines 366-396) — moved to `TransferHandler` in Phase 3
- [ ] **DELETE** `_execute_load` (lines 398-467) — moved to `TransferHandler` in Phase 3
- [ ] **DELETE** `_execute_unload` (lines 469-530) — moved to `TransferHandler` in Phase 3
- [ ] **DELETE** `_load_pod_from_staging_yard` (lines 532-585) — moved to `TransferHandler` in Phase 3
- [ ] **DELETE** `_unload_pod_to_staging_yard` (lines 587-616) — moved to `TransferHandler` in Phase 3
- [ ] **DELETE** `_deploy_drop_pod` (lines 618-652) — moved to `ColonizeHandler` in Phase 2
- [ ] **DELETE** `_validate_tick_inputs` (lines 734-743) — moved to `JoinFleetHandler` in Phase 1
- [ ] **DELETE** `_elect_canonical_merges` (lines 823-883) — moved to `JoinFleetHandler` in Phase 1
- [ ] **DELETE** `_emit_join_cancelled` (lines 885-910) — moved to `JoinFleetHandler` in Phase 1
- [ ] **KEEP** `process_join_fleet`, `process_colonize`, `process_transfer`, `process_instant_orders`, `execute_action_order`, `__init__` — these are public surface or facade-required
- [ ] **KEEP** `JoinFleetResult`, `ColonizeResult`, `TransferResult` dataclasses (lines 40-59) — public types, used by callers / tests
- [ ] **KEEP** `_superweapon_processor` attribute and its construction — adapter still delegates to it
- [ ] **Verify:** `wc -l game/strategy/engine/order_processor.py` ≤ 200
- [ ] **Verify:** sharded suite green

**Notes:**

### Task 4.7: Delete `SuperweaponOrderProcessor.process_self_destruct` [Simple]

**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py tests/unit/strategy/engine/test_superweapon_edge_cases.py -v`

- [ ] **DELETE** `SuperweaponOrderProcessor.process_self_destruct` (lines 664-740)
- [ ] **Verify:** existing superweapon tests pass — `SelfDestructHandler` is now the sole live path for SELF_DESTRUCT
- [ ] **Verify:** `wc -l game/strategy/engine/superweapon_order_processor.py` — expected ~705 (down ~76)

**Notes:**

### Task 4.8: Run sharded suite + integration smoke [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py` and `pytest tests/integration/strategy/ -v`

- [ ] Run full sharded suite
- [ ] Run all `tests/integration/strategy/` tests
- [ ] Pass count ≥ Phase 3 baseline + new Phase 4 tests
- [ ] **Verify:** zero regressions across the entire 15405-test suite

**Notes:**

### Task 4.9: Run `phase_complete.py` [Simple]

- [ ] Commit message: `feat(PROJ-368): Phase 4 — superweapon adapter registry; delete legacy OrderProcessor methods`
- [ ] Sign-off
- [ ] Run `phase_complete.py PROJ-368 phase_4`
- [ ] **Verify:** state shows phase_4 `committed`; cumulative review dispatched covering all 4 phases.

**Notes:**

### Task 4.10: Registry-completeness test [Medium]

**File:** `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py -v`

- [ ] Create the file with imports for `create_default_order_handler_registry`, `SuperweaponOrderProcessor`, and `OrderType`.
- [ ] Assert every `OrderType` value handled by `OrderProcessor` has a registered handler:
  ```python
  from game.strategy.engine.order_handlers.registry_factory import create_default_order_handler_registry
  from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
  from game.strategy.data.order_types import (
      ACTION_ORDER_TYPES, PLANET_ACTION_ORDER_TYPES, OrderType,
  )
  registry = create_default_order_handler_registry(
      event_bus=None,
      superweapon_processor=SuperweaponOrderProcessor(),
  )
  expected = (ACTION_ORDER_TYPES - PLANET_ACTION_ORDER_TYPES) | {OrderType.JOIN_FLEET}
  registered = registry.all_registered()
  missing = expected - registered
  assert not missing, f"OrderTypes missing handlers: {missing}"
  ```
- [ ] **Verify:** test passes; failing this test BLOCKS Phase 4 sign-off.

**Notes:** This task pulls Phase 5's registry-completeness coverage forward into Phase 4 so the gate fires at the deletion-and-switchover commit, not after the doc/test polish phase.

### Task 4.11: No-legacy-helper AST guard [Medium]

**File:** `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py -v`

- [ ] Create the file with `ast` + `pathlib` imports.
- [ ] AST scan of `game/strategy/engine/order_processor.py` to assert no `_process_*` private helpers remain on `OrderProcessor`. Allowlist: public facade methods only.
  ```python
  import ast, pathlib
  ORDER_PROCESSOR = pathlib.Path(__file__).parent.parent.parent.parent / "game/strategy/engine/order_processor.py"

  def test_no_legacy_private_helpers_on_order_processor():
      tree = ast.parse(ORDER_PROCESSOR.read_text())
      forbidden = {
          "_execute_fleet_merge", "_execute_fleet_transfer", "_execute_load",
          "_execute_unload", "_load_pod_from_staging_yard",
          "_unload_pod_to_staging_yard", "_deploy_drop_pod",
          "_validate_tick_inputs", "_elect_canonical_merges",
          "_emit_join_cancelled",
      }
      offenders = []
      for node in ast.walk(tree):
          if isinstance(node, ast.FunctionDef) and node.name in forbidden:
              offenders.append(node.name)
          if isinstance(node, ast.FunctionDef) and node.name.startswith("_process_"):
              offenders.append(node.name)
      assert not offenders, f"Legacy private helpers must be deleted: {offenders}"
  ```
- [ ] **Verify:** test passes; failing this test BLOCKS Phase 4 sign-off.

**Notes:** This task pulls Phase 5's no-legacy-helper coverage forward into Phase 4. Together with Task 4.10, the two gates ensure the Phase 4 deletion commit cannot be merged with stragglers or unrouted OrderTypes.

---

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] `SuperweaponHandlerAdapter` exists; 5 adapters registered for {IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE}
- [ ] All 11 OrderType values handled by `OrderProcessor` route through the registry
- [ ] `OrderProcessor` ≤ 200 LOC (verified by `wc -l`)
- [ ] `SuperweaponOrderProcessor.process_self_destruct` is deleted
- [ ] All pre-existing tests pass; new per-handler test count grew
- [ ] Sharded suite green
- [ ] Update phase status to `Complete (Committed)`
- [ ] Update plan.md
