# Phase 2: Fleet — `IFleetMutator` + route engine writes + AST guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-370 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** see manifest.md "Phase 2: Fleet" section

**Sequencing precondition:** PROJ-368 must have landed before Phase 3+ (already a precondition for Planet/Empire/ShipInstance work). If PROJ-369 has landed, wire via `TurnEngineConfig`; otherwise wire via direct constructor kwargs and migrate to `TurnEngineConfig` when PROJ-369 closes.

**Objective:** `IFleetMutator` is a working Protocol implemented by `FleetWriteService` (new) + `FleetNavigationService` (existing). Engines and handlers route Fleet writes through the mutator. The Fleet AST guard goes hot. Zero behavior change.

---

## Tasks

### Task 2.1: Implement `FleetWriteService` [Medium]
**File:** `game/strategy/services/fleet_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_fleet_write_service.py -v`

- [ ] Create the new file with module docstring referencing PROJ-370 and `IFleetMutator`.
- [ ] Implement class `FleetWriteService` with `__init__(self, navigation_service: FleetNavigationService | None = None)`. The nav service is the co-implementer of the navigation slice (`set_location`, `set_path`).
- [ ] Implement every method declared in `IFleetMutator`. Each method delegates to the existing `Fleet` public API (`add_ship`, `remove_ship`, `add_order`, `pop_order`, etc.) where possible. For raw attribute writes that have no method (e.g., `display_name`, `fleet_policy`, `construction_queue_paused`), assign directly inside the service.
- [ ] For `set_location` and `set_path`: forward to `self._nav.set_location(...)` if the nav service is provided; otherwise raise `NotImplementedError("FleetWriteService requires FleetNavigationService for navigation writes")`. (This makes it impossible to construct a half-broken composite by accident.)
- [ ] Verify: file is < 200 LOC.

**Notes:**

### Task 2.2: Add `IFleetMutator` conformance to `FleetNavigationService` [Simple]
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_service_mutator.py -v`

- [ ] Add the two methods that the existing service does not have under those names:
  - `def set_location(self, fleet: Fleet, new_location: HexCoord) -> None: fleet.location = new_location`
  - `def set_path(self, fleet: Fleet, new_path: list[HexCoord]) -> None: fleet.path = list(new_path)`
- [ ] Note: the existing `calculate_fleet_next_hex` (lines 716-759) already does these writes inline. Leave that method as-is; the new explicit methods exist so external callers (engines, AST guard) can route through a single named seam.
- [ ] Run `pytest tests/unit/strategy/services/test_fleet_navigation_service.py -v --testmon` (or whichever existing tests cover this service) to confirm zero behavior change.

**Notes:**

### Task 2.3: Wire `IFleetMutator` at `GameSession.__init__` [Medium]
**File:** `game/strategy/engine/game_session.py` (construction point — see `game/strategy/engine/game_session.py:99-108` where `TurnEngine` is constructed today). If PROJ-369 has landed, also `game/strategy/engine/turn_engine_config.py` (default-population point in `TurnEngineConfig.create_default()`).
**Tests:** `pytest tests/integration/strategy/test_game_session_strategy.py -v --testmon`

- [ ] Construct `FleetWriteService(navigation_service=fleet_nav_service)` inside `GameSession.__init__` (citing `game/strategy/engine/game_session.py:99-108`).
- [ ] **If PROJ-369 has landed:** add `fleet_mutator: IFleetMutator` to `TurnEngineConfig`; populate it in `TurnEngineConfig.create_default()`; pass the config through to `TurnEngine`. Engines that need the mutator pull it via `config.fleet_mutator` or via direct ctor kwargs threaded from `GameSession`.
- [ ] **If PROJ-369 has NOT landed:** pass `FleetWriteService` directly into the engines and hooks that need it (`OrderProcessor`, `PostBattleHook`, `FleetMovementEngine`, etc.) via constructor kwargs from `GameSession`. Migrate to `TurnEngineConfig`-routed wiring when PROJ-369 closes.
- [ ] Verify: integration + facade tests still pass.

**Notes:**

### Task 2.4: Route `fleet_movement_engine.py` through the mutator [Medium]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/fleet_movement_engine/ -v --testmon`

- [ ] Add `fleet_mutator: IFleetMutator | None = None` to the engine constructor. If `None`, fall back to the strategy `ApplicationContext` default (mirrors the pattern PROJ-258 established for the other 10 services).
- [ ] Locate `fleet.location = next_hex` (currently line 182). Replace with `self._fleet_mutator.set_location(fleet, next_hex)`.
- [ ] Re-run the engine's existing tests; expect green.

**Notes:**

### Task 2.5: Route `order_processor.py` Fleet writes [Medium]
**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_*.py -v --testmon`

- [ ] **Coordinate with PROJ-368.** If PROJ-368 has shipped its handler-package decomposition, route writes through the new `order_handlers/` files instead. If not, route through the legacy monolith.
- [ ] Add `fleet_mutator` ctor kwarg.
- [ ] Locate the 2 `fleet.location =` writes; route them.
- [ ] Locate any `fleet.orders.append/.insert/.pop/.clear` calls outside the existing `Fleet.add_order` / `pop_order` / `clear_orders` methods; route them.
- [ ] Re-run the existing 5 order-processor test files. Verify green.

**Notes:**

### Task 2.6: Route remaining Fleet-write call sites [Medium]
**File:** `game/strategy/engine/handlers/movement.py`, `handlers/base.py`, `handlers/order_queue.py`, `handlers/build.py`, `engine/conflict_resolution_engine.py`, `data/order_serializer.py`, `data/fleet_pursuer_tracker.py`
**Tests:** `pytest tests/unit/strategy/engine/ tests/unit/strategy/data/ -v --testmon`

- [ ] For each file in the manifest's Phase 2 list:
  - Add `fleet_mutator` ctor kwarg if the class doesn't already have it via DI.
  - Replace direct attribute writes / collection mutations with the corresponding mutator methods.
- [ ] **Special case `validation/superweapon_validator.py`** — verify whether the `fleet.location` reference there is a *read* or a *write*. If read-only, no change. Add `# Verified read-only` comment with date.
- [ ] **Special case `data/order_serializer.py:231` and `data/fleet_pursuer_tracker.py:141`** — both are "owned by the Fleet's data-class neighborhood". Decide whether they should route through the mutator or whether their writes are legitimately data-class-internal. **Architect recommendation:** they ARE legitimately internal (the serializer and pursuer tracker are co-located with `Fleet` in `data/` and act as data-class extensions). Add them to the AST allowlist.
- [ ] Re-run all affected test files.

**Notes:**

### Task 2.7: Route UI Fleet-write call sites [Medium]
**File:** `game/ui/screens/strategy_screen_order_editing.py`, `strategy_fleet_ops.py`, `strategy_build_queue_manager.py`, `battle_setup/controller.py`, `battle_setup_state.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [ ] UI today calls `fleet.orders.pop(...)` etc. directly (e.g., `strategy_screen_order_editing.py:90`). Route these through the mutator. UI gets the mutator from the facade.
- [ ] **Special case `battle_setup_state.py`** — its `self.fleets.append/.remove` is mutating a UI-state container, NOT the strategy `Empire.fleets`. Verify; if UI-only, no change. Add the file to the UI allowlist (since the AST guard scans `game/`, not `ui/...` only).

**Notes:**

### Task 2.8: Flip on the Fleet AST guard [Medium]
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py`
**Tests:** `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_fleet_boundary -v`

- [ ] Update the `Fleet` `BoundarySpec`:
  - `target_attributes = frozenset({"location", "path", "ships", "orders", "construction_queue", "construction_queue_paused", "display_name", "fleet_policy", "_task_forces", "speed"})` — note `speed` is also written by `FleetSpeedCalculator`, which should be in the allowlist.
  - `allowlist_paths = frozenset({"game/strategy/data/fleet.py", "game/strategy/data/order_serializer.py", "game/strategy/data/fleet_pursuer_tracker.py", "game/strategy/data/fleet_battle_adapter.py", "game/strategy/data/task_force.py", "game/strategy/services/fleet_navigation_service.py", "game/strategy/services/fleet_write_service.py", "game/strategy/services/fleet_speed_calculator.py"})`.
- [ ] Run only the Fleet boundary test. **Expect FAILURES initially** — they identify the remaining unrouted writers. Address each.
- [ ] Re-run; expect GREEN.

**Notes:**

### Task 2.9: Phase 2 unit-test pass [Medium]
**File:** `tests/unit/strategy/services/test_fleet_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_fleet_write_service.py -v`

- [ ] Write ≥ 8 unit tests, each driving ONE mutator method against a real Fleet:
  - `test_set_location_updates_fleet_location`
  - `test_set_path_replaces_path`
  - `test_append_order_appends`
  - `test_insert_order_at_index`
  - `test_pop_order_returns_and_removes`
  - `test_clear_orders_empties_queue`
  - `test_add_ship_triggers_speed_recalc` (verify the existing `trigger_speed_recalculation` invariant holds via the mutator)
  - `test_remove_ship_returns_true_when_present`
  - `test_set_display_name`
- [ ] Run; expect GREEN.

**Notes:**

### Task 2.10: Phase 2 verification [Medium]
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the sharded suite. Compare pass count to baseline + new tests. Difference should equal new tests (~10).
- [ ] Verify NO existing tests broke. If any broke, root-cause and fix; do not silence.
- [ ] Run `pytest tests/integration/strategy/ -v --testmon`; expect green.
- [ ] Update plan.md `Current State`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] AST-guard test for Fleet is GREEN
- [ ] `git grep -nE "fleet\.location\s*=" game/` returns hits only in `data/fleet.py` and `services/fleet_navigation_service.py`
- [ ] `python Tools/test_sharded/test_sharded.py` is GREEN
- [ ] No measurable performance regression on the 3-empire end-turn smoke
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3 (and Phase 5 — they can run in parallel given the DAG)
