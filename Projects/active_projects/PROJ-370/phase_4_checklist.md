# Phase 4: Empire — `IEmpireMutator` + route engine writes + AST guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-370 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_2, phase_3
**Review Mode:** standard
**Files (planned):** see manifest.md "Phase 4: Empire" section

**Sequencing precondition:** PROJ-368 must have landed (already true at Phase 4 since Phases 2 and 3 depend on it). If PROJ-369 has landed, wire via `TurnEngineConfig`; otherwise wire via direct constructor kwargs and migrate to `TurnEngineConfig` when PROJ-369 closes.

**Objective:** `IEmpireMutator` is a working Protocol implemented by `EmpireWriteService` (new). The four post-battle / superweapon / system-destroyer / game-init sites that mutate `empire.colonies` and `empire.fleets` from outside route through it. The Empire AST guard goes hot. Zero behavior change.

---

## Tasks

### Task 4.1: Implement `EmpireWriteService` [Medium]
**File:** `game/strategy/services/empire_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_empire_write_service.py -v`

- [ ] Create the new file. Implement `EmpireWriteService` with every method declared in `IEmpireMutator`. Delegate to existing Empire methods where they exist (`add_colony`, `add_fleet`, `remove_fleet`).
- [ ] `add_colony` already does `planet.owner_id = self.id` inside Empire — keep that semantics by delegating to `empire.add_colony(planet)`. The mutator does NOT bypass this; it forwards.
- [ ] `remove_colony(empire, planet)` is new — Empire today has no `remove_colony` method; the three call sites (`superweapon_order_processor.py:358,606`, `system_destroyer.py:161`) call `emp.colonies.remove(planet)` directly. Add the helper inside `Empire` (1-line method) AND have the mutator forward to it. (This keeps the data-class API symmetric with `add_colony` / `remove_fleet`.)
- [ ] `prune_empty_fleets(empires_by_team_id, fleets_by_team_id)` — port the logic from `combat/post_battle_hook.py:200-218`. The function lives on the mutator; the post-battle hook calls it.
- [ ] Verify: file is < 150 LOC.

**Notes:**

### Task 4.2: Add `Empire.remove_colony` [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/test_empire*.py tests/unit/strategy/empire/ -v --testmon`

- [ ] Add 1-line method:
  ```python
  def remove_colony(self, planet) -> bool:
      if planet in self.colonies:
          self.colonies.remove(planet)
          return True
      return False
  ```
- [ ] Note: do NOT change the planet's `owner_id` here (the Phase 3 `PlanetWriteService.set_owner_id(...)` is the seam for that, and callers of `remove_colony` should set owner_id to None separately if appropriate).
- [ ] Run the existing Empire tests; expect green.

**Notes:**

### Task 4.3: Wire `IEmpireMutator` at `GameSession.__init__` [Simple]
**File:** `game/strategy/engine/game_session.py` (construction point — see `game/strategy/engine/game_session.py:99-108`). If PROJ-369 has landed, also `game/strategy/engine/turn_engine_config.py` (default-population point in `TurnEngineConfig.create_default()`).
**Tests:** `pytest tests/integration/strategy/test_game_session_strategy.py -v --testmon`

- [ ] Construct `EmpireWriteService()` inside `GameSession.__init__`.
- [ ] **If PROJ-369 has landed:** add `empire_mutator: IEmpireMutator` to `TurnEngineConfig`; populate via `TurnEngineConfig.create_default()`; engines pull from `config.empire_mutator`.
- [ ] **If PROJ-369 has NOT landed:** pass `EmpireWriteService` directly into the engines / hooks that need it (`SuperweaponOrderProcessor`, `PostBattleHook`, `SystemDestroyer`, `GameInitializer`, `HarvestingEngine`) via constructor kwargs from `GameSession`. Migrate to `TurnEngineConfig`-routed wiring when PROJ-369 closes.

**Notes:**

### Task 4.4: Route superweapon + system-destroyer + game-init Empire writes [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`, `game/strategy/services/system_destroyer.py`, `game/strategy/engine/game_initializer.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py tests/unit/strategy/services/test_system_destroyer.py tests/unit/strategy/engine/test_game_initializer*.py -v --testmon`

- [ ] Each accepts `empire_mutator` ctor kwarg.
- [ ] `superweapon_order_processor.py:358,606` — `emp.colonies.remove(target_planet)` → `empire_mutator.remove_colony(emp, target_planet)`.
- [ ] `system_destroyer.py:161` — same routing.
- [ ] `game_initializer.py:86` — `empire.colonies.clear()` → `empire_mutator.clear_colonies(empire)`. Add this method to `IEmpireMutator` and `EmpireWriteService`.

**Notes:**

### Task 4.5: Route post-battle empty-fleet pruning through the mutator [Medium]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v --testmon`

- [ ] `_prune_empty_fleets` (lines 200-218) currently does `empire_fleets.remove(fleet)` directly. Replace the body with a call to `empire_mutator.prune_empty_fleets(...)`.
- [ ] The hook signature: `apply_outcome_to_fleets(outcome, *, fleets_by_team_id, empires=None, empire_mutator: IEmpireMutator)` — add the new parameter, default to a context-resolved instance.
- [ ] **Cross-phase:** `Empire.remove_fleet` is a public API today; the mutator's `remove_fleet` forwards to it. The post-battle hook may bypass Empire's event-bus emission (see `Empire.remove_fleet:73-117`) — verify that calling `empire_mutator.remove_fleet(empire, fleet, event_bus=...)` preserves the existing event semantics. If event-bus parameter handling is awkward through the mutator, leave the hook calling `empire.remove_fleet(fleet, event_bus=event_bus)` directly, and confirm `Empire.remove_fleet` is on the AST guard's Empire allowlist (since that's a method on the data class itself).

**Notes:**

### Task 4.6: Route harvesting-engine `max_storage` writes [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py -v --testmon`

- [ ] `empire.max_storage[...] = ...` → `empire_mutator.set_max_storage_amount(empire, resource, amount)`.

**Notes:**

### Task 4.7: Flip on the Empire AST guard [Medium]
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py`
**Tests:** `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_empire_boundary -v`

- [ ] Update the `Empire` BoundarySpec:
  - `target_attributes = frozenset({"colonies", "fleets", "_fleet_resource_pool", "max_storage", "built_ship_designs", "designed_ships"})`.
  - `allowlist_paths = frozenset({"game/strategy/data/empire.py", "game/strategy/services/empire_write_service.py"})`.
- [ ] Run the Empire boundary test. Expect failures initially; address each.
- [ ] Re-run; expect GREEN.

**Notes:**

### Task 4.8: Phase 4 unit-test pass [Medium]
**File:** `tests/unit/strategy/services/test_empire_write_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_empire_write_service.py -v`

- [ ] Write ≥ 6 unit tests:
  - `test_add_colony_assigns_owner_id`
  - `test_remove_colony_returns_true_when_present`
  - `test_remove_colony_returns_false_when_absent`
  - `test_clear_colonies_empties_list`
  - `test_prune_empty_fleets_removes_only_empty`
  - `test_set_max_storage_amount`

**Notes:**

### Task 4.9: Phase 4 verification [Medium]
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the sharded suite. Verify GREEN.
- [ ] Run `pytest tests/integration/strategy/ -v --testmon`; expect green.
- [ ] Update plan.md `Current State`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] AST-guard test for Empire is GREEN
- [ ] `git grep -nE "empire\.(colonies|fleets|max_storage)\." game/` returns zero `.append/.pop/.remove/.clear` results outside the allowlist
- [ ] `python Tools/test_sharded/test_sharded.py` is GREEN
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State
