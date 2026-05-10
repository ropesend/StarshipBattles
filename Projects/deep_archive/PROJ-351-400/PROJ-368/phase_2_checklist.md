# Phase 2: Port instant + simple action orders (Colonize, SelfDestruct)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-368 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Committed)
**Depends on:** phase_1 (verified)
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/order_handlers/colonize.py`
- `game/strategy/engine/order_handlers/self_destruct.py`
- `game/strategy/engine/order_handlers/registry_factory.py`
- `game/strategy/engine/order_handlers/__init__.py`
- `game/strategy/engine/order_processor.py`
- `game/strategy/engine/superweapon_order_processor.py`
- `tests/unit/strategy/engine/order_handlers/test_colonize_handler.py`
- `tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py`

**Objective:** Extract `ColonizeHandler` (today: `OrderProcessor.process_colonize` lines 151-249 + `_deploy_drop_pod` lines 618-652) and `SelfDestructHandler` (today: `SuperweaponOrderProcessor.process_self_destruct` lines 664-740 — the only superweapon `process_*` method that is **not** spec-driven). Register both in the registry. `OrderProcessor.process_colonize` becomes a one-line delegate. New per-handler tests; existing `test_order_processor_colonize.py` (317 LOC) continues to pass. Phase 4 will delete `process_self_destruct` from `superweapon_order_processor.py`; Phase 2 only **lifts** it (parallel copies live for one phase).

---

## Pre-flight

- [ ] Phase 1 status `verified` in `phase_state.json`
- [ ] Sharded suite green at end of Phase 1
- [ ] Run `pytest tests/unit/strategy/engine/test_order_processor_colonize.py -v` — confirm 100% green at HEAD
- [ ] Run `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py -v` — confirm 100% green (these test SELF_DESTRUCT among other superweapons)
- [ ] **Resolve Open Question Q1** (raise vs log+pop on missing `component_registry` for COLONIZE): default is preserve log+pop+False for backward compat.

---

## Tasks

### Task 2.1: Pin existing COLONIZE + SELF_DESTRUCT test behavior (TDD pin) [Simple]

**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_colonize.py tests/unit/strategy/engine/test_superweapon_event_payloads.py tests/unit/strategy/engine/test_superweapon_edge_cases.py -v`

- [ ] Run; assert all pass on Phase 2 day 0.
- [ ] Pin baseline pass count for these files.

**Notes:**

### Task 2.2: Implement `ColonizeHandler` in `order_handlers/colonize.py` [Complex]

**File:** `game/strategy/engine/order_handlers/colonize.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_colonize.py -v`

- [ ] Create `game/strategy/engine/order_handlers/colonize.py` with module docstring
- [ ] `class ColonizeHandler(BaseOrderHandler)`:
  - [ ] `supported_order_types = (OrderType.COLONIZE,)`
  - [ ] `execute_action_order(self, fleet, empire, galaxy, component_registry=None, empires=None) -> OrderExecutionResult` — port `OrderProcessor.process_colonize` body (lines 151-249) verbatim. Replace `ColonizeResult(...)` returns with `OrderExecutionResult(success=..., colonized=..., planet_name=...)`. Preserve every log message verbatim except prefix `OrderProcessor:` → `ColonizeHandler:`.
  - [ ] **Q1 resolution:** if user said "raise", change `if component_registry is None:` to raise `ValueError("ColonizeHandler.execute_action_order requires component_registry")`. Default: preserve log+pop+False.
  - [ ] `_deploy_drop_pod(self, fleet, planet) -> None` — port verbatim from order_processor.py:618-652
  - [ ] Refactor the `if self._event_bus: self._event_bus.log_event(...)` block (lines 235-248) to `self._emit_event(EventType.COLONY_FOUNDED, category=EventCategory.COLONIES, empire_id=empire.id, message=..., **kwargs)`
- [ ] Verify file ≤ 200 LOC
- [ ] **Verify:** import works
- [ ] **Verify:** `pytest tests/unit/strategy/engine/test_order_processor_colonize.py -v` still passes (it still drives `OrderProcessor.process_colonize` — nothing changed there yet)

**Notes:**

### Task 2.3: Implement `SelfDestructHandler` in `order_handlers/self_destruct.py` [Complex]

**File:** `game/strategy/engine/order_handlers/self_destruct.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py tests/unit/strategy/engine/test_superweapon_edge_cases.py -v`

- [ ] Create `game/strategy/engine/order_handlers/self_destruct.py` with module docstring noting the lift from `superweapon_order_processor.py:664-740`
- [ ] `class SelfDestructHandler(BaseOrderHandler)`:
  - [ ] `supported_order_types = (OrderType.SELF_DESTRUCT,)`
  - [ ] `execute_action_order(self, fleet, empire, galaxy, component_registry=None, empires=None) -> OrderExecutionResult` — port `SuperweaponOrderProcessor.process_self_destruct` body (lines 683-740) verbatim. Replace `SuperweaponResult(...)` returns with `OrderExecutionResult(success=..., fleet_consumed=..., message=...)`.
  - [ ] Refactor the `if self._event_bus: self._event_bus.log_event(...)` block (lines 724-734) to `self._emit_event(...)`.
  - [ ] Preserve `EventType.SHIPS_SELF_DESTRUCTED` payload exact-match (every kwarg the same).
- [ ] Verify file ≤ 130 LOC
- [ ] **Verify:** import works
- [ ] **Verify:** existing superweapon tests still pass (still drive `SuperweaponOrderProcessor.process_self_destruct`)

**Notes:**

### Task 2.4: Update `registry_factory.py` to register both handlers [Simple]

**File:** `game/strategy/engine/order_handlers/registry_factory.py`, `game/strategy/engine/order_handlers/__init__.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_base.py -v`

- [ ] In `create_default_order_handler_registry`:
  - [ ] After `JoinFleetHandler` registration, add `ColonizeHandler(event_bus=event_bus)` registered against `OrderType.COLONIZE`
  - [ ] Add `SelfDestructHandler(event_bus=event_bus)` registered against `OrderType.SELF_DESTRUCT`
- [ ] Update `order_handlers/__init__.py` to re-export `ColonizeHandler` and `SelfDestructHandler`
- [ ] **Verify:** `python -c "from game.strategy.engine.order_handlers import create_default_order_handler_registry; from game.strategy.data.order_types import OrderType; r = create_default_order_handler_registry(event_bus=None); assert OrderType.COLONIZE in r; assert OrderType.SELF_DESTRUCT in r"`

**Notes:**

### Task 2.5: Wire `OrderProcessor.process_colonize` to delegate [Medium]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_colonize.py -v`

- [ ] Replace `OrderProcessor.process_colonize` body (lines 151-249) with:
  ```python
  handler = self._handler_registry.get(OrderType.COLONIZE)
  result = handler.execute_action_order(
      fleet, empire, galaxy,
      component_registry=component_registry,
  )
  return ColonizeResult(colonized=result.colonized, planet_name=result.planet_name)
  ```
- [ ] **DO NOT** delete `_deploy_drop_pod` from `OrderProcessor` yet (Phase 4 deletion); the live copy is in `ColonizeHandler`. Mark with a comment: `# PROJ-368: kept until Phase 4 deletion. Live copy in order_handlers/colonize.py.`
- [ ] **DO NOT** modify `execute_action_order`'s COLONIZE branch yet (Phase 4 will route everything through the registry). The current dispatch still calls `self.process_colonize(...)` which now delegates.
- [ ] **Verify:** `pytest tests/unit/strategy/engine/test_order_processor_colonize.py -v` — every test passes
- [ ] **Verify:** `pytest tests/integration/strategy/test_multi_pod_colonization.py -v` passes

**Notes:**

### Task 2.6: Update `execute_action_order`'s SELF_DESTRUCT routing to use registry [Medium]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py tests/unit/strategy/engine/test_superweapon_edge_cases.py -v`

- [ ] In `OrderProcessor.execute_action_order` (lines 655-732), find the SELF_DESTRUCT entry in the `superweapon_handlers` dict (line 722-724)
- [ ] Replace it with: `OrderType.SELF_DESTRUCT: lambda: self._handler_registry.get(OrderType.SELF_DESTRUCT).execute_action_order(fleet, empire, galaxy)` — reshape the result so the existing `result.fleet_consumed` access (line 730) still works (the `OrderExecutionResult` already has `fleet_consumed`, so this is mechanical).
- [ ] Wrap the return so the lambda's return type matches the others in the dict (a result-with-`.fleet_consumed`-attr)
- [ ] **DO NOT** delete `SuperweaponOrderProcessor.process_self_destruct` yet; Phase 4 deletion. The new path goes through `SelfDestructHandler`; the old method remains live but unused.
- [ ] **Verify:** existing superweapon tests pass; SHIPS_SELF_DESTRUCTED event payload is bit-identical

**Notes:**

### Task 2.7: Add focused unit tests for `ColonizeHandler` [Medium]

**File:** `tests/unit/strategy/engine/order_handlers/test_colonize_handler.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_colonize_handler.py -v`

- [ ] Lift fixture helpers from `test_order_processor_colonize.py:24-90` into `tests/unit/strategy/engine/order_handlers/conftest.py`
- [ ] Write ≥ 7 focused tests against `ColonizeHandler` directly:
  - [ ] `test_no_order_returns_uncolonized`
  - [ ] `test_validation_failure_pops_and_returns_false`
  - [ ] `test_any_planet_sentinel_resolves_first_unowned`
  - [ ] `test_no_drop_pod_pops_and_returns_false`
  - [ ] `test_happy_path_claims_planet_and_deploys_pod` — verify `empire.add_colony` called, `Planet.facilities` appended, `ship.carried_items` popped, drop pod's `initial_stockpile` seeded
  - [ ] `test_emits_colony_founded_event_payload_exact_match` — including `system_name`, `local_hex`
  - [ ] `test_missing_component_registry_logs_and_pops` (or raises, per Q1 resolution)

**Notes:**

### Task 2.8: Add focused unit tests for `SelfDestructHandler` [Medium]

**File:** `tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py -v`

- [ ] Write ≥ 5 focused tests against `SelfDestructHandler` directly:
  - [ ] `test_no_order_returns_failure`
  - [ ] `test_empty_ship_id_list_pops_and_returns_failure`
  - [ ] `test_happy_path_removes_specified_ships`
  - [ ] `test_fleet_emptied_triggers_empire_remove_fleet` — SG-003 check
  - [ ] `test_emits_ships_self_destructed_event_payload_exact_match`

**Notes:**

### Task 2.9: Run sharded suite + LOC check [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ Phase 1 baseline + new tests
- [ ] `wc -l game/strategy/engine/order_processor.py` — expected ~780 (down ~100 from Phase 1 end)
- [ ] **Verify:** zero regressions; the existing `test_order_processor_colonize.py` (317 LOC) and superweapon test files all pass

**Notes:**

### Task 2.10: Run `phase_complete.py` [Simple]

- [ ] Commit message: `feat(PROJ-368): Phase 2 — extract ColonizeHandler + SelfDestructHandler`
- [ ] Sign-off
- [ ] Run `phase_complete.py PROJ-368 phase_2`
- [ ] **Verify:** state shows phase_2 `committed`; cumulative review dispatched covering phase_1 + phase_2.

**Notes:**

---

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] `ColonizeHandler` and `SelfDestructHandler` modules exist
- [ ] `OrderProcessor.process_colonize` is a one-line delegate
- [ ] `OrderProcessor.execute_action_order`'s SELF_DESTRUCT entry routes through the registry
- [ ] `SuperweaponOrderProcessor.process_self_destruct` is **still defined** (deleted in Phase 4)
- [ ] All pre-existing tests pass; new per-handler tests added
- [ ] Sharded suite green
- [ ] Update phase status to `Complete (Committed)`
- [ ] Update plan.md
