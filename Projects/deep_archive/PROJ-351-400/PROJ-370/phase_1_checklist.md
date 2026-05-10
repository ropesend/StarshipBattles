# Phase 1: Mutator-protocol foundation + AST guard harness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-370 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** —
**Review Mode:** standard
**Files (planned):** `game/core/protocols/strategy_mutators.py`, `game/core/protocols/__init__.py`, `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py`, `tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py`, `docs/02_PATTERNS.md`

**Objective:** Stand up the mutator-protocol module and the AST-guard harness. Zero behavior change. AST-guard tests are GREEN with empty disallowlists; the harness is itself unit-tested with synthetic fixtures.

---

## Tasks

### Task 1.1: Create `game/core/protocols/strategy_mutators.py` skeleton [Simple]
**File:** `game/core/protocols/strategy_mutators.py` (NEW)
**Tests:** `pytest tests/unit/core/protocols/ -v --testmon`

- [ ] Create the new module file. Module docstring explains: "Strategy-layer mutator protocols. Pair with the read protocols in `strategy_entities.py`. Engines depend on these to seam writes."
- [ ] Declare `IFleetMutator(Protocol)` at the top. Use `@runtime_checkable`. Methods:
  - `set_location(self, fleet, new_location: HexCoord) -> None`
  - `set_path(self, fleet, new_path: list[HexCoord]) -> None`
  - `append_order(self, fleet, order) -> None`
  - `insert_order(self, fleet, index: int, order) -> None`
  - `pop_order(self, fleet, index: int = 0) -> "Order | None"`
  - `clear_orders(self, fleet) -> None`
  - `add_ship(self, fleet, ship) -> None`
  - `remove_ship(self, fleet, ship) -> bool`
  - `set_display_name(self, fleet, name: str) -> None`
  - `set_fleet_policy(self, fleet, policy) -> None`
  - `append_construction_item(self, fleet, item: dict) -> None`
  - `pop_construction_item(self, fleet, index: int = 0) -> dict`
  - `set_construction_queue_paused(self, fleet, paused: bool) -> None`
  - `add_task_force(self, fleet, tf) -> None`
  - `remove_task_force(self, fleet, tf) -> bool`
- [ ] Declare `IPlanetMutator(Protocol)` similarly. Methods cover: `populations` (`add_species_population`, `remove_species_population`, `update_population_count`), `facilities` (`add_facility`, `remove_facility`), `stockpile` (`set_stockpile_amount`), `staging_yard` (`add_staging_item`, `pop_staging_item`), `construction_queue` (`append_construction_item`, `pop_construction_item`), `orders` (`append_order`, `pop_order`, `insert_order`, `clear_orders`), plus scalar fields (`set_owner_id`, `set_atmosphere`, `set_atmosphere_target`, `set_energy`, `set_energy_capacity`, `set_energy_generation`, `set_gravity_target`, `set_water_target`, `set_radiation_shielding_target`, `set_radiation_shielding`).
- [ ] Declare `IEmpireMutator(Protocol)` similarly. Methods: `add_colony`, `remove_colony`, `add_fleet`, `remove_fleet`, `set_max_storage_amount`, `set_fleet_resource_amount`, `add_built_design`, `prune_empty_fleets`.
- [ ] Declare `IShipInstanceMutator(Protocol)`. Methods: `set_is_alive`, `set_is_derelict`, `set_current_hp`, `replace_components`, `set_cargo_amount`, `add_carried_item`, `pop_carried_item`, `set_consumable_level`, `set_component_toggle`, `set_activation_state`, `increment_battles_survived`, `add_experience`, `add_kill`.
- [ ] Add `__all__` listing the four protocol names.
- [ ] Run `python -c "from game.core.protocols.strategy_mutators import IFleetMutator, IPlanetMutator, IEmpireMutator, IShipInstanceMutator; print('OK')"`. Verify clean import.
- [ ] Verify: file is < 250 LOC.

**Notes:**

### Task 1.2: Re-export from `game/core/protocols/__init__.py` [Simple]
**File:** `game/core/protocols/__init__.py`
**Tests:** `pytest tests/unit/core/protocols/ -v --testmon`

- [ ] Open the file; locate the existing re-export block.
- [ ] Add `from game.core.protocols.strategy_mutators import IFleetMutator, IPlanetMutator, IEmpireMutator, IShipInstanceMutator`.
- [ ] Append the four names to `__all__` if `__all__` is defined.
- [ ] Verify `from game.core.protocols import IFleetMutator` works at the REPL.

**Notes:**

### Task 1.3: Build the AST-guard harness self-test [Medium]
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py -v`

- [ ] Write the AST-walker as a helper function `find_attribute_writes(source: str, target_attrs: set[str]) -> list[tuple[int, str]]` that returns `[(line_no, offending_pattern)]`. Patterns to detect:
  - `Assign` to `Attribute` (`obj.attr = X`)
  - `AugAssign` to `Attribute` (`obj.attr += X`)
  - `Subscript`-target `Assign` against `Attribute` (`obj.attr[k] = X`)
  - `Call` of `Attribute(value=Attribute)` for the methods `append`, `pop`, `remove`, `extend`, `clear`, `insert` (`obj.attr.append(X)`).
- [ ] Write 8 synthetic fixture strings (multi-line Python) — 4 should match (one per detection pattern), 4 should not (legal access patterns: read, function call without dotted attr, etc.).
- [ ] Test that the helper catches all 4 illegal cases and rejects all 4 legal cases.
- [ ] Run the test; should be GREEN.
- [ ] Verify: helper handles multi-line strings and comments correctly (no false positives).

**Notes:**

### Task 1.4: Build the parameterized AST-guard test [Medium]
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py -v`

- [ ] Use the helper from Task 1.3.
- [ ] Define `BOUNDARIES: list[BoundarySpec]` where each `BoundarySpec` carries: `data_class_name`, `target_attributes: frozenset[str]`, `allowlist_paths: frozenset[str]`, `description: str`.
- [ ] Phase 1 Boundaries (all 4 with EMPTY `target_attributes` for now — this lets the test be wired and green from day one):
  - `Fleet`: `target_attributes=frozenset()`, `allowlist=frozenset({"game/strategy/data/fleet.py"})` (placeholder).
  - `Planet`: same shape, empty disallowlist.
  - `Empire`: same.
  - `ShipInstance`: same.
- [ ] Parameterize the test over `BOUNDARIES`. Walk every `*.py` under `game/`, parse each with `ast.parse`, run the helper, fail if any disallowed write is found outside the allowlist. With Phase 1's empty `target_attributes`, the test is structurally green.
- [ ] Add a docstring atop the test file: "Phase N (where N is the phase that owns the data class) flips on the disallowlist for that class. See manifest.md for which phase owns which class. The harness is intentionally trivial in Phase 1."
- [ ] Run the test; should be GREEN.

**Notes:**

### Task 1.5: Document the new pattern [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual — read the rendered markdown.

- [ ] Add a new section near the existing Pattern §2 (Protocol + TypeGuard) titled "Read/Write Protocol Pair". Body:
  - One-paragraph explanation: read protocols (`IFleet`, `IPlanet`, etc.) define what to read; mutator protocols (`IFleetMutator`, etc.) define what to write. They live as siblings: `game/core/protocols/strategy_entities.py` for reads, `game/core/protocols/strategy_mutators.py` for writes.
  - Code example mirroring the existing Protocol example, with both `IFleet` and `IFleetMutator` shown.
  - "When to use": any data class that is mutated from > 2 outside files.
  - "When NOT to use": value objects (frozen dataclasses), single-writer state (already encapsulated), and types that are write-once at construction.
  - Cross-link to PROJ-370.
- [ ] Update the patterns count in `docs/02_PATTERNS.md` header (currently 33, becomes 34).
- [ ] Update `docs/README.md` patterns count if it appears there.
- [ ] Add the `> **Last verified:**` blockquote per `docs/03_CONVENTIONS.md` §9.

**Notes:**

### Task 1.6: Verify Phase 1 baseline [Simple]
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the sharded suite. Capture the pass count.
- [ ] Compare to the project-start baseline. Difference should be exactly +N where N = number of new tests added in Phase 1 (~ 4-6 tests: AST-guard parametrized cases + self-test cases).
- [ ] Verify: NO existing tests broke. NO behavior change.
- [ ] Update plan.md `Current State` with the new pass count.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard.py -v` is GREEN
- [ ] `pytest tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py -v` is GREEN
- [ ] `python Tools/test_sharded/test_sharded.py` is GREEN; pass count grew by exactly the new test count
- [ ] No production code under `game/strategy/` was modified (only `game/core/protocols/`)
- [ ] `docs/02_PATTERNS.md` has the new "Read/Write Protocol Pair" section
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
