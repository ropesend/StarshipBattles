# Phase 5: ShipInstance — `IShipInstanceMutator` + post-battle hook + AST guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-370 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2 (PostBattleHook prunes fleets — needs `IFleetMutator` already wired)
**Review Mode:** standard
**Files (planned):** see manifest.md "Phase 5: ShipInstance" section

**Sequencing precondition:** PROJ-368 must have landed (already true at Phase 5). If PROJ-369 has landed, wire via `TurnEngineConfig`; otherwise wire via direct constructor kwargs and migrate to `TurnEngineConfig` when PROJ-369 closes.

**Objective:** `IShipInstanceMutator` is a working Protocol implemented by `ShipInstanceWriteService` (new). The post-battle hook (the canonical battle→strategy write boundary) routes its writes through the mutator. The ShipInstance AST guard goes hot. Zero behavior change.

---

## Tasks

### Task 5.1: Implement `ShipInstanceWriteService` [Medium]
**File:** `game/strategy/services/ship_instance_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_ship_instance_write_service.py -v`

- [ ] Create the new file. Implement `ShipInstanceWriteService` with every method declared in `IShipInstanceMutator`.
- [ ] Status flag mutators (`set_is_alive`, `set_is_derelict`, `set_current_hp`, `replace_components`, `increment_battles_survived`) are direct writes.
- [ ] Cargo / consumable mutators (`set_cargo_amount`, `set_consumable_level`) **forward to** `ShipCargoManager` and `ShipConsumableManager` respectively. Do NOT bypass them — those managers exist to enforce capacity and conversion semantics.
- [ ] `replace_components(instance, new_components: dict[str, ComponentState])` invalidates the stats cache: `instance.invalidate_stats_cache()`. (The post-battle hook does this today inline; keeping it inside the mutator means callers cannot forget.)
- [ ] `add_carried_item` / `pop_carried_item` — direct list mutation on `carried_items`.
- [ ] Verify: file is < 200 LOC.

**Notes:**

### Task 5.2: Refactor `ship_consumable_manager.py` and `ship_cargo_manager.py` to be aware of the mutator [Medium]
**File:** `game/strategy/data/ship_consumable_manager.py`, `game/strategy/data/ship_cargo_manager.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/test_*cargo* -v --testmon`

- [ ] **Decision point:** these managers today directly write `self._instance.cargo_contents[...] = ...` and `self._instance.consumable_levels[...] = ...`. They are co-located with `ShipInstance` in `data/`. Two options:
  - **Option A:** Add the manager file paths to the AST allowlist. The managers are data-class extensions; they're conceptually inside the boundary.
  - **Option B:** Refactor the managers to call back through `IShipInstanceMutator`. Adds a circular dependency (mutator forwards TO the manager forwards TO the mutator).
- [ ] **Architect recommendation: Option A.** The managers are composition partners of `ShipInstance` (assigned in `__post_init__`); they're effectively private internals. Allowlist them.
- [ ] No code change needed in this task IF Option A. Just add to allowlist in Task 5.7.

**Notes:**

### Task 5.3: Wire `IShipInstanceMutator` at `GameSession.__init__` [Simple]
**File:** `game/strategy/engine/game_session.py` (construction point — see `game/strategy/engine/game_session.py:99-108`). If PROJ-369 has landed, also `game/strategy/engine/turn_engine_config.py` (default-population point in `TurnEngineConfig.create_default()`).
**Tests:** `pytest tests/integration/strategy/test_game_session_strategy.py -v --testmon`

- [ ] Construct `ShipInstanceWriteService()` inside `GameSession.__init__`.
- [ ] **If PROJ-369 has landed:** add `ship_mutator: IShipInstanceMutator` to `TurnEngineConfig`; populate via `TurnEngineConfig.create_default()`; engines / hooks pull from `config.ship_mutator`.
- [ ] **If PROJ-369 has NOT landed:** pass `ShipInstanceWriteService` directly into the engines and hooks that need it (`PostBattleHook`, `EnvironmentalHazardEngine`, `OrderProcessor`/`order_handlers/transfer.py`) via constructor kwargs from `GameSession`. Migrate to `TurnEngineConfig`-routed wiring when PROJ-369 closes.

**Notes:**

### Task 5.4: Route `combat/post_battle_hook.py` through the mutator [Complex]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v --testmon`

- [ ] `apply_outcome_to_fleets` signature: add `ship_instance_mutator: IShipInstanceMutator` parameter (resolved from the spec compiler's closure today; same wiring slot).
- [ ] `_apply_single_outcome` body (lines 104-132):
  - `ShipStatus.DESTROYED` branch: `instance.is_alive = False; instance.current_hp = 0` → `mutator.set_is_alive(instance, False); mutator.set_current_hp(instance, 0)`.
- [ ] `_apply_survivor_outcome` body (lines 135-187):
  - `instance.components = new_components` → `mutator.replace_components(instance, new_components)` (which now also invalidates the cache, removing the explicit call below).
  - `instance.is_alive = True` → `mutator.set_is_alive(instance, True)`.
  - `instance.is_derelict = bool(is_derelict)` → `mutator.set_is_derelict(instance, bool(is_derelict))`.
  - `instance.battles_survived += 1` → `mutator.increment_battles_survived(instance)`.
  - `instance.invalidate_stats_cache()` — REMOVE this line; `replace_components` now does it.
- [ ] **Verify** the call to `_remove_ship` (line 192) — it calls `fleet.remove_ship(instance)` which is fleet-internal. That should ROUTE through `IFleetMutator.remove_ship(fleet, instance)` from Phase 2. Update.
- [ ] Run `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v` — every existing test should still pass. The mutator parameter gets a default-constructed `ShipInstanceWriteService` for backward compat in tests, OR each test gets parameterized — pick the lower-friction option.

**Notes:**

### Task 5.5: Route `environmental_hazard_engine.py` through the mutator [Medium]
**File:** `game/strategy/engine/environmental_hazard_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_environmental_hazard_engine.py -v --testmon`

- [ ] Engine ctor accepts `ship_instance_mutator` and `fleet_mutator` (the latter from Phase 2 — already wired but engine may not have it yet).
- [ ] `ship.current_hp = new_hp` (line 196) → `mutator.set_current_hp(ship, new_hp)`.
- [ ] `ship.current_hp = None` (line 198) → `mutator.set_current_hp(ship, None)`.
- [ ] `ship.is_alive = False` (line 202) → `mutator.set_is_alive(ship, False)`.
- [ ] If the engine cascade-removes ships from fleets, route via `fleet_mutator.remove_ship(...)`.

**Notes:**

### Task 5.6: Route `order_processor.py` (or `order_handlers/transfer.py`) carried-items writes [Medium]
**File:** `game/strategy/engine/order_processor.py` AND/OR `game/strategy/engine/order_handlers/transfer.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_transfer.py -v --testmon` or `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py`

- [ ] Locate `target_ship.carried_items.append(removed)` (line 582), `ship.carried_items.pop(i)` (line 613), `drop_pod = ship.carried_items.pop(item_index)` (line 635).
- [ ] Route through `mutator.add_carried_item` / `mutator.pop_carried_item`.

**Notes:**

### Task 5.7: Flip on the ShipInstance AST guard [Medium]
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py`
**Tests:** `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_ship_instance_boundary -v`

- [ ] Update the `ShipInstance` BoundarySpec:
  - `target_attributes = frozenset({"is_alive", "is_derelict", "is_operational", "current_hp", "components", "cargo_contents", "carried_items", "consumable_levels", "component_toggles", "activation_states", "experience", "kills", "battles_survived", "design_role", "role_override", "_cached_stats"})`. Note `_cached_stats` is intentional — it's mutated only via `invalidate_stats_cache()`; AST-guarding it locks that contract.
  - `allowlist_paths = frozenset({"game/strategy/data/ship_instance.py", "game/strategy/services/ship_instance_write_service.py", "game/strategy/data/ship_consumable_manager.py", "game/strategy/data/ship_cargo_manager.py", "game/strategy/data/ship_instance_serializer.py", "game/strategy/data/ship_instance_bridge.py"})`.
- [ ] Run the ShipInstance boundary test. Expect failures initially; address each.
- [ ] Re-run; expect GREEN.

**Notes:**

### Task 5.8: Phase 5 unit-test pass [Medium]
**File:** `tests/unit/strategy/services/test_ship_instance_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_ship_instance_write_service.py -v`

- [ ] Write ≥ 8 unit tests:
  - `test_set_is_alive_flips_flag`
  - `test_set_is_derelict`
  - `test_set_current_hp_sets_value`
  - `test_set_current_hp_none_for_full_hp`
  - `test_replace_components_replaces_dict_and_invalidates_cache`
  - `test_increment_battles_survived`
  - `test_add_carried_item_appends`
  - `test_pop_carried_item_removes_and_returns`
  - **Integration test:** `test_post_battle_hook_round_trip_through_mutator` — drive `apply_outcome_to_fleets` end-to-end with a real outcome and assert that the resulting ShipInstance state matches today's behavior bit-for-bit (snapshot-style).

**Notes:**

### Task 5.9: Phase 5 verification [Medium]
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the sharded suite. Verify GREEN.
- [ ] Run `pytest tests/integration/strategy/ -v --testmon`; expect green.
- [ ] **Final user-smoke step:** load a pre-PROJ-370 savegame on the post-PROJ-370 build. Verify it loads without exception and the strategy screen displays correctly.
- [ ] Run the 3-empire end-turn smoke. Capture wall-time; compare to the Phase 1 baseline. Difference should be ≤ 5 % (the project's stated performance budget).
- [ ] Update plan.md `Current State` to "All 5 phases complete; ready for final audit."

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] AST-guard test for ShipInstance is GREEN
- [ ] `git grep -nE "instance\.(is_alive|is_derelict|components)\s*=" game/` returns hits only inside the allowlist
- [ ] All four AST guards (Fleet, Planet, Empire, ShipInstance) are GREEN
- [ ] `python Tools/test_sharded/test_sharded.py` is GREEN
- [ ] Performance smoke ≤ 5 % regression
- [ ] Pre-PROJ-370 savegame loads cleanly
- [ ] `docs/02_PATTERNS.md`, `docs/01_ARCHITECTURE.md`, `docs/systems/strategy_layer.md` updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All 5 phases complete; awaiting final audit + user verification."
