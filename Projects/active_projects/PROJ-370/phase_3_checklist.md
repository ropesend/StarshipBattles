# Phase 3: Planet — `IPlanetMutator` + route engine writes + AST guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-370 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** see manifest.md "Phase 3: Planet" section

**Sequencing precondition:** PROJ-368 must have landed (so Phase 3 targets `order_handlers/` rather than the legacy monolith). If PROJ-369 has landed, wire via `TurnEngineConfig`; otherwise wire via direct constructor kwargs and migrate to `TurnEngineConfig` when PROJ-369 closes.

**Objective:** `IPlanetMutator` is a working Protocol implemented by `PlanetWriteService` (new). Engines, handlers, and post-PROJ-368 `order_handlers/` route Planet writes through it. The Planet AST guard goes hot. Zero behavior change.

---

## Tasks

### Task 3.1: Implement `PlanetWriteService` [Medium]
**File:** `game/strategy/services/planet_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_planet_write_service.py -v`

- [ ] Create the new file. Implement `PlanetWriteService` with every method declared in `IPlanetMutator`. Delegate to existing Planet methods where they exist (`add_to_stockpile`, `consume_from_stockpile`, `add_to_staging_yard`, `remove_from_staging_yard`, `add_order`, `pop_order`, `clear_orders`).
- [ ] For attributes without existing methods (`populations`, `facilities`, scalar atmospheric/energy/modifier fields, `owner_id`, `species_configs`), implement direct assignment / collection mutation inside the service.
- [ ] **Critical invariant:** `set_owner_id(planet, empire_id)` — when `owner_id` changes, the planet may need to be added/removed from an empire's `colonies` list. The mutator does NOT cross the boundary into Empire writes; that's the caller's responsibility (and Phase 4 routes those callers through `EmpireWriteService.add_colony` / `remove_colony`). Document this in the docstring.
- [ ] Verify: file is < 250 LOC.

**Notes:**

### Task 3.2: Wire `IPlanetMutator` at `GameSession.__init__` [Simple]
**File:** `game/strategy/engine/game_session.py` (construction point — see `game/strategy/engine/game_session.py:99-108`). If PROJ-369 has landed, also `game/strategy/engine/turn_engine_config.py` (default-population point in `TurnEngineConfig.create_default()`).
**Tests:** `pytest tests/integration/strategy/test_game_session_strategy.py -v --testmon`

- [ ] Construct `PlanetWriteService()` inside `GameSession.__init__`.
- [ ] **If PROJ-369 has landed:** add `planet_mutator: IPlanetMutator` to `TurnEngineConfig`; populate via `TurnEngineConfig.create_default()`; engines pull from `config.planet_mutator`.
- [ ] **If PROJ-369 has NOT landed:** pass `PlanetWriteService` directly into the engines / hooks that need it via constructor kwargs from `GameSession`. Migrate to `TurnEngineConfig`-routed wiring when PROJ-369 closes.

**Notes:**

### Task 3.3: Route `OrderProcessor` / `order_handlers/` Planet writes [Complex]
**File:** `game/strategy/engine/order_processor.py` AND/OR `game/strategy/engine/order_handlers/colonize.py`, `transfer.py` (post-PROJ-368)
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_*.py tests/unit/strategy/engine/order_handlers/ -v --testmon`

- [ ] **Coordination check:** has PROJ-368 landed? If yes, target `order_handlers/`. If no, target `order_processor.py` and add a TODO to revisit at PROJ-368 merge.
- [ ] Routed writes:
  - `planet.populations.append(species_pop)` (line 514) → `planet_mutator.add_species_population(planet, species_pop)`.
  - `planet.facilities.append(facility)` (line 645) → `planet_mutator.add_facility(planet, facility)`.
  - `planet.staging_yard.pop(i)` (line 555-style) → `planet_mutator.pop_staging_item(planet, index=i)`.
  - `pop.count -= to_load` (line 432-style) — this is a per-population mutation, NOT a per-planet attribute. Consider whether to add `update_population_count(planet, race_id, new_count)` to the mutator. **Decision:** yes; keeps the AST guard from triggering on `pop.count -=`. Add the method.
  - Other staging-yard / population manipulations: route similarly.

**Notes:**

### Task 3.4: Route `production_engine.py` and `production_spawner.py` [Medium]
**File:** `game/strategy/engine/production_engine.py`, `production_spawner.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_*.py tests/unit/strategy/engine/test_production_spawner.py -v --testmon`

- [ ] Both engines accept `planet_mutator` ctor kwarg.
- [ ] `production_spawner.py:202` — `planet.facilities.append(facility)` → `planet_mutator.add_facility(planet, facility)`.
- [ ] `production_engine.py` — locate any direct `colony.stockpile[...] -= ...` or `colony.construction_queue.append/pop` writes. Route them.

**Notes:**

### Task 3.5: Route `harvesting_engine.py`, `planet_energy_engine.py`, `atmosphere_engine.py`, `organics_consumption_engine.py`, `planet_modifier_effect_engine.py` [Complex]
**File:** Five engine files
**Tests:** `pytest tests/unit/strategy/engine/test_*_engine.py -v --testmon`

- [ ] Each engine takes `planet_mutator` ctor kwarg.
- [ ] `harvesting_engine.py` — stockpile additions go through `planet_mutator.set_stockpile_amount(planet, resource, new_amount)` or a higher-level `add_to_stockpile_via_mutator(planet, resource, amount)`.
- [ ] `planet_energy_engine.py` — 5 sites mutating `energy`/`energy_capacity`/`energy_generation`. Route through `set_energy`, `set_energy_capacity`, `set_energy_generation`.
- [ ] `atmosphere_engine.py` — atmosphere/atmosphere_target writes routed.
- [ ] `organics_consumption_engine.py:107` — `colony.stockpile[resource_id] = available - supplied` routed.
- [ ] `planet_modifier_effect_engine.py` — gravity/water/radiation_shielding writes routed.

**Notes:**

### Task 3.6: Route `planet_command_handlers.py` and remaining sites [Medium]
**File:** `game/strategy/engine/planet_command_handlers.py`, `game/strategy/engine/game_initializer.py`, `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_handlers.py tests/unit/strategy/engine/test_game_session*.py -v --testmon`

- [ ] `planet_command_handlers.py:134` — `removed = planet.orders.pop(cmd.order_index)` routed to `planet_mutator.pop_order(planet, index=cmd.order_index)`.
- [ ] `game_initializer.py:344` — `home_planet.populations.append(initial_pop)` routed to `add_species_population`.
- [ ] `quickstart_builder.py:309` — `home_planet.facilities.append(facility)` routed to `add_facility`.
- [ ] **UI touchpoints:** `ui/screens/planet_list_*.py`, `ui/panels/planet_report_panel.py`, `ui/panels/build_queue_controller.py`, `ui/screens/strategy_build_queue_manager.py` — verify any planet writes; route or whitelist if they're UI-state-only.

**Notes:**

### Task 3.7: Flip on the Planet AST guard [Medium]
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py`
**Tests:** `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_planet_boundary -v`

- [ ] Update the `Planet` BoundarySpec:
  - `target_attributes = frozenset({"populations", "facilities", "stockpile", "max_stockpile", "staging_yard", "construction_queue", "construction_queue_paused", "orders", "owner_id", "atmosphere", "atmosphere_target", "gravity_target", "gravity_original", "water_target", "radiation_shielding", "radiation_shielding_target", "energy", "energy_capacity", "energy_generation", "species_configs", "intrinsic_abilities"})`.
  - `allowlist_paths = frozenset({"game/strategy/data/planet.py", "game/strategy/services/planet_write_service.py"})`.
- [ ] Run the Planet boundary test. Expect failures initially; address each.
- [ ] Re-run; expect GREEN.

**Notes:**

### Task 3.8: Phase 3 unit-test pass [Medium]
**File:** `tests/unit/strategy/services/test_planet_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_planet_write_service.py -v`

- [ ] Write ≥ 10 unit tests, one per mutator method category. At minimum:
  - stockpile add / consume
  - population add / remove / count update
  - facility add / remove
  - staging-yard add / pop
  - construction queue append / pop
  - orders append / pop / clear
  - scalar fields (`set_owner_id`, `set_energy`, `set_atmosphere_target`)
- [ ] Run; expect GREEN.

**Notes:**

### Task 3.9: Phase 3 verification [Medium]
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the sharded suite. Verify GREEN.
- [ ] Run `pytest tests/integration/strategy/ -v --testmon`; expect green.
- [ ] Update plan.md `Current State`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] AST-guard test for Planet is GREEN
- [ ] `git grep -nE "planet\.(populations|facilities|stockpile|staging_yard)\." game/strategy/engine/` shows zero `.append/.pop/.remove/.clear/.insert` results
- [ ] `python Tools/test_sharded/test_sharded.py` is GREEN
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State
