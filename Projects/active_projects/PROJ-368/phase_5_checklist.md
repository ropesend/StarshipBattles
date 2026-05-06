# Phase 5: Per-handler unit tests + AST static-guard regression

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-368 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4 (verified)
**Review Mode:** standard
**Files (planned):**
- `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py` (extend)
- `tests/unit/strategy/engine/order_handlers/test_colonize_handler.py` (extend)
- `tests/unit/strategy/engine/order_handlers/test_self_destruct_handler.py` (extend)
- `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py` (extend)
- `tests/unit/strategy/engine/order_handlers/test_superweapon_dispatch.py` (extend)
- `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` (new)
- `docs/systems/strategy_layer.md`
- `docs/02_PATTERNS.md`
- `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md`

**Objective:** Audit each handler's per-test coverage; backfill anything thin (target: ≥ 5 tests per handler covering happy path, wrong order type, missing target, validation failure, event emission, plus handler-specific edge cases). Add the AST static-guard regression test. Update documentation. Cross-link the source review.

---

## Pre-flight

- [ ] Phase 4 status `verified`
- [ ] Sharded suite green at end of Phase 4
- [ ] `wc -l game/strategy/engine/order_processor.py` confirmed ≤ 200

---

## Tasks

### Task 5.1: Audit per-handler test coverage [Medium]

**File:** `tests/unit/strategy/engine/order_handlers/`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/ -v --collect-only`

- [ ] Run `pytest --collect-only` and tally tests per file
- [ ] Document the count per handler in this checklist's Notes
- [ ] Identify any handler with < 5 tests; backfill in subsequent tasks

**Notes:** Expected coverage after Phases 1-4: JoinFleet ≥ 8 (Task 1.8), Colonize ≥ 7 (Task 2.7), SelfDestruct ≥ 5 (Task 2.8), Transfer ≥ 12 (Task 3.8), Superweapon adapter ≥ 6 (Task 4.4). All meet the ≥ 5 target. Phase 5 verifies this and **adds** missing edge cases.

### Task 5.2: Backfill missing per-handler edge case tests [Medium]

**File:** Whichever handler test file has gaps (likely none if Phases 1-4 met spec)
**Tests:** Per file

- [ ] **JoinFleetHandler:** add `test_invalid_order_type_returns_unmerged` (covers `order.type != OrderType.JOIN_FLEET` early-out)
- [ ] **ColonizeHandler:** add `test_no_planet_at_location_returns_uncolonized`, `test_pod_initial_stockpile_seeded_correctly`
- [ ] **SelfDestructHandler:** add `test_target_not_a_list_pops_and_returns_failure` (line 689 branch)
- [ ] **TransferHandler:** add `test_unknown_cargo_type_validation_path` (defensive)
- [ ] **SuperweaponHandlerAdapter:** add `test_adapter_propagates_component_registry_kwarg`

**Notes:**

### Task 5.3: Implement AST static-guard test [Complex]

**File:** `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py -v`

- [ ] Create the file with imports for `ast`, `pathlib`
- [ ] `def test_order_processor_facade_under_200_loc()`:
  ```python
  path = pathlib.Path(__file__).parent.parent.parent.parent.parent / "game/strategy/engine/order_processor.py"
  loc = len(path.read_text().splitlines())
  assert loc < 200, f"order_processor.py is {loc} LOC; PROJ-368 facade target is < 200"
  ```
- [ ] `def test_order_processor_no_order_type_branching()`:
  ```python
  # Walk the AST. Allow: at most ONE OrderType reference (the registry lookup
  # `self._handler_registry.get(order.type)`). Disallow: `if order.type ==
  # OrderType.X`, `order.type in (OrderType.X, ...)`, etc.
  tree = ast.parse(path.read_text())
  ordertype_refs = [
      node for node in ast.walk(tree)
      if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
      and node.value.id == "OrderType"
  ]
  # Allow ≤ 1 OrderType reference (the registry key).
  assert len(ordertype_refs) <= 1, f"Found {len(ordertype_refs)} OrderType references; facade target is ≤ 1"
  ```
- [ ] `def test_every_action_order_type_has_a_handler()`:
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
- [ ] `def test_no_legacy_private_helpers_on_order_processor()`:
  ```python
  # AST-walk OrderProcessor's class body; assert none of the deleted-Phase-4
  # method names exist as definitions.
  tree = ast.parse(path.read_text())
  forbidden = {
      "_execute_fleet_merge", "_execute_fleet_transfer", "_execute_load",
      "_execute_unload", "_load_pod_from_staging_yard",
      "_unload_pod_to_staging_yard", "_deploy_drop_pod",
      "_validate_tick_inputs", "_elect_canonical_merges",
      "_emit_join_cancelled",
  }
  for node in ast.walk(tree):
      if isinstance(node, ast.FunctionDef):
          assert node.name not in forbidden, f"{node.name} should have been deleted in Phase 4"
  ```
- [ ] **Verify:** all 4 tests pass

**Notes:**

### Task 5.4: Update `docs/systems/strategy_layer.md` [Medium]

**File:** `docs/systems/strategy_layer.md`
**Tests:** N/A (documentation)

- [ ] Locate the section that describes order processing (likely under "Order lifecycle" or "Tick phases")
- [ ] Add a new subsection "Order handlers (PROJ-368)" describing:
  - The `IOrderHandler` Protocol
  - The `OrderHandlerRegistry`
  - The `create_default_order_handler_registry` factory
  - The 6 handler classes (`JoinFleetHandler`, `ColonizeHandler`, `TransferHandler`, `SelfDestructHandler`, `SuperweaponHandlerAdapter` × 5 specs)
  - The parallel with `engine/handlers/` (command handlers)
- [ ] Update `> **Last verified:**` blockquote at the top per docs/03_CONVENTIONS.md §9 / PROJ-307
- [ ] **Verify:** doc reads correctly; no broken file references

**Notes:**

### Task 5.5: Update `docs/02_PATTERNS.md` [Simple]

**File:** `docs/02_PATTERNS.md`
**Tests:** N/A

- [ ] Add a new pattern entry (or extend an existing "Registry-based dispatch" pattern) noting:
  - Strategy layer has TWO registry-based dispatch systems
  - `engine/handlers/` — UI Command DTO → Order creation (PROJ-309 sub-phase 3.5)
  - `engine/order_handlers/` — Action tick → State mutation (PROJ-368)
  - Same Protocol idiom, same `create_default_*_registry()` factory shape, same per-handler test colocation
- [ ] Update `> **Last verified:**` blockquote
- [ ] **Verify:** cross-reference is accurate

**Notes:**

### Task 5.6: Cross-link the source review [Simple]

**File:** `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md`
**Tests:** N/A

- [ ] Edit the "OrderProcessor Giant-Method Syndrome" section (target #1)
- [ ] Add a footer line: `**Status:** Resolved by PROJ-368, commit `<sha>` (final commit hash from Phase 5 close).`

**Notes:**

### Task 5.7: Run sharded suite [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ Phase 4 baseline + Phase 5 backfill tests
- [ ] **Verify:** zero regressions

**Notes:**

### Task 5.8: User end-to-end smoke [Medium]

**Tests:** Manual

- [ ] Load a savegame
- [ ] End turn — observe at least one of each: JOIN_FLEET, COLONIZE, TRANSFER, a superweapon (e.g., IMPLODE_PLANET if the save has the ability)
- [ ] Verify event log entries match pre-PROJ-368 format
- [ ] **Verify:** no crashes, no log warnings introduced by PROJ-368

**Notes:**

### Task 5.9: Run final audit gate [Medium]

**Tests:** Per 03c protocol step 8

- [ ] Run `validate_audit_ready.py` per `claude-proj-audit`
- [ ] Verify: no `open` or `addressed_pending_review` findings; latest review's `coverage_set` includes all 5 phases; project tip SHA matches audited SHA
- [ ] If clean: merge `proj/PROJ-368/main` to `main`; record `audit.merge_to_main_sha`
- [ ] Hand off to `claude-proj-archive`

**Notes:**

### Task 5.10: Run `phase_complete.py` (final) [Simple]

- [ ] Commit message: `feat(PROJ-368): Phase 5 — per-handler tests, AST static guard, docs`
- [ ] Sign-off
- [ ] Run `phase_complete.py PROJ-368 phase_5`
- [ ] **Verify:** state shows phase_5 `committed`; final cumulative review dispatched covering all 5 phases.

**Notes:**

---

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Each handler has ≥ 5 focused unit tests
- [ ] AST static guard at `test_order_processor_facade.py` passes (4 tests)
- [ ] `docs/systems/strategy_layer.md` updated
- [ ] `docs/02_PATTERNS.md` updated
- [ ] Source review cross-linked
- [ ] Sharded suite green
- [ ] User end-to-end smoke verified
- [ ] Final audit clean; merged to main
- [ ] Update phase status to `Complete (Verified)`
- [ ] Update plan.md to project complete state
