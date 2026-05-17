# Phase 0: Container substrate + design decisions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-436 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/container.py` (new)
- `game/strategy/data/containable.py` (new)
- `game/core/resources.py` (modified — extend `ResourceDefinition` with `mass_per_unit`)
- `data/resources.json` (modified existing canonical file — extend each entry with `mass_per_unit`)
- `tests/unit/strategy/data/test_container.py` (new)
- `tests/unit/strategy/data/test_containable.py` (new)
- `tests/unit/core/test_resource_catalog_mass_per_unit.py` (new)

**Objective:** Land the `Container` / `Containable` / `ContainerPolicy` / `ContainableKind` substrate. Extend the existing Core-layer `ResourceCatalog` / `ResourceDefinition` in `game/core/resources.py` with `mass_per_unit: float`. Extend the existing canonical `data/resources.json` with `mass_per_unit` on each of the 8 entries. **Do NOT create a parallel strategy-local `resource_registry.py` — the existing `ResourceCatalog` is the single source of truth.** No legacy callers migrated this phase; this is pure foundation. Resolve the three deferred design decisions (D1 `PlanetaryFacility.consumable_levels` fold-in scope; D2 `Empire.resource_pool` query-vs-cached; D3 non-fixed `mass_per_unit` initial values) per the defaults documented in `decisions.md` "Phase 0 deferred design decisions" section; if implementation discovers cause to change a default, document the override here AND in `decisions.md`.

---

## Tasks

### Task 0.1: Read foundation docs + reconfirm baseline [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/systems/resource_system.md`, `docs/systems/production_system.md`
**Tests:** none — discovery work

- [ ] Read `docs/README.md`
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
- [ ] Read `docs/systems/resource_system.md` and `docs/systems/production_system.md` for current model
- [ ] Read `AgentCoordination/Scratchpad/reports/unified_container_design_sketch.md` end-to-end
- [ ] Read `Projects/active_projects/PROJ-431/decisions.md` for the substrate-then-sweep migration template
- [ ] Re-run sharded suite as baseline:
  ```
  python Tools/test_sharded/test_sharded.py
  ```
  Confirm 21132/21132 (or current baseline) still passes.

**Notes:** [Filled during implementation]

### Task 0.2: RED — author `test_container.py` [Medium]
**File:** `tests/unit/strategy/data/test_container.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_container.py -q` — MUST fail (module does not exist yet)

- [ ] Test: construct empty `Container(capacity_mass=100, policy=any)` — `mass_used == 0`, `mass_remaining == 100`
- [ ] Test: `add(metals, 5.0)` — resources slice updates; `mass_used == 5.0 * mass_per_unit("metals")`
- [ ] Test: `add(fighter_item, 1)` — items slice grows; mass deducts from remaining
- [ ] Test: `add(population_human, 50)` — population slice updates; mass = 50 * 0.1 = 5.0
- [ ] Test: three-slice mixed contents; `mass_used == sum across all three`
- [ ] Test: `accepts(c)` returns False when c.kind not in policy.allowed_kinds
- [ ] Test: `accepts(c)` returns False when c.type_id not in policy.allowed_type_ids (when not None)
- [ ] Test: `add` returns AddResult.REJECTED_POLICY when not accepted
- [ ] Test: `add` returns AddResult.REJECTED_CAPACITY when would exceed mass cap
- [ ] Test: `remove` returns RemoveResult.NOT_ENOUGH when insufficient quantity
- [ ] Test: `to_dict()` / `from_dict()` round-trip preserves all three slices and policy
- [ ] Test: `contents()` yields one ContainerEntry per non-empty resource/item/population entry
- [ ] Run test; confirm fails because `game.strategy.data.container` does not exist

**Notes:** [Per design sketch §3.]

### Task 0.3: GREEN — implement `container.py` + `containable.py` [Medium]
**Files:** `game/strategy/data/container.py` (new), `game/strategy/data/containable.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_container.py -q` (green)

- [ ] Create `containable.py`:
  - `ContainableKind = Enum('RESOURCE', 'ITEM', 'POPULATION')`
  - `Containable` abstract base (kind, type_id, mass_per_unit)
  - `ResourceContainable`, `ItemContainable`, `PopulationContainable` concrete variants
  - `ItemRef` dataclass for items-slice identity
  - `AddResult`, `RemoveResult` enums
- [ ] Create `container.py`:
  - `ContainerPolicy` dataclass
  - `Container` class with three slices + ops per design.md §"Target data model"
  - `mass_used`, `mass_remaining` computed
  - `accepts()`, `add()`, `remove()`, `contents()`
  - `to_dict()` / `from_dict()` (polymorphic per-slice; legacy load support deferred to phase-specific migrations)
- [ ] Verify: both files under 500 LOC ceiling
- [ ] Run test, all green

**Notes:** [Filled during implementation]

### Task 0.4: RED — author `test_resource_catalog_mass_per_unit.py` [Simple]
**File:** `tests/unit/core/test_resource_catalog_mass_per_unit.py` (new)
**Tests:** `pytest tests/unit/core/test_resource_catalog_mass_per_unit.py -q` — MUST fail (the field/method don't exist yet)

- [ ] Test: existing `ResourceCatalog.from_json()` loads with new `mass_per_unit` field present on each `ResourceDefinition`
- [ ] Test: `ResourceCatalog.get_mass_per_unit("metals") == 0.01`
- [ ] Test: `ResourceCatalog.get_mass_per_unit("energy") == 1.0` (per user directive)
- [ ] Test: `ResourceCatalog.get_mass_per_unit("unknown")` raises (fail-fast — no silent default)
- [ ] Test: backward compat — if a custom `ResourceCatalog.from_data([...])` entry omits `mass_per_unit`, it defaults to 1.0 (per dataclass default)
- [ ] Test: `ResourceDefinition.mass_per_unit` field is part of the frozen-dataclass equality / hash
- [ ] Run test; confirm fails because the field/method don't exist yet

**Notes:** Tests live under `tests/unit/core/` because `ResourceCatalog` is Core-layer; co-locating these tests with the catalog keeps the layer rule intact.

### Task 0.5: GREEN — extend `ResourceDefinition` + `ResourceCatalog` + `data/resources.json` [Simple]
**Files:** `game/core/resources.py`, `data/resources.json`
**Tests:** `pytest tests/unit/core/test_resource_catalog_mass_per_unit.py -q` (green)

- [ ] In `game/core/resources.py`:
  - Add `mass_per_unit: float = 1.0` to `ResourceDefinition` (frozen dataclass)
  - Update `ResourceCatalog.from_data` / `from_json` parsers to read the new field
  - Add `ResourceCatalog.get_mass_per_unit(resource_id) -> float` (fail-fast on unknown)
- [ ] In `data/resources.json`: add `"mass_per_unit": <value>` to each of the 8 existing entries:
  - `metals: 0.01`
  - `organics: 0.01`
  - `vapors: 0.001`
  - `radioactives: 0.005`
  - `exotics: 0.001`
  - `fuel: 0.0001`
  - `ammo: 0.001`
  - `energy: 1.0`
  - Existing fields (`id`, `name`, `description`, `display_group`, `has_quality`) UNCHANGED on every entry
- [ ] Run tests, all green
- [ ] Verify: existing core resource-catalog tests still green (the extension is additive)

**Notes:** [Filled during implementation]

### Task 0.6: RED — author `test_containable.py` integration with `ResourceCatalog` [Simple]
**File:** `tests/unit/strategy/data/test_containable.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_containable.py -q` — MUST fail

- [ ] Test: `ResourceContainable("metals").mass_per_unit == 0.01` (resolved via Core `ResourceCatalog`)
- [ ] Test: `PopulationContainable("human").mass_per_unit == 0.1` (default if race JSON not yet extended)
- [ ] Test: `ItemContainable` from a design reports the design's mass

### Task 0.7: GREEN — wire `Containable` to `ResourceCatalog` + race default [Simple]
**Files:** `game/strategy/data/containable.py`
**Tests:** `pytest tests/unit/strategy/data/test_containable.py -q` (green)

- [ ] `ResourceContainable.mass_per_unit` delegates to the existing `ResourceCatalog.get_mass_per_unit(self.type_id)` (Core layer — strategy consumes through the existing public API; no parallel registry)
- [ ] `PopulationContainable.mass_per_unit` returns 0.1 default for Phase 0 (race JSON extension deferred to Phase 3 or wherever first population transfer integration test lands)
- [ ] `ItemContainable.mass_per_unit` returns the design's mass (existing `ShipInstance.mass` pattern from PROJ-431)
- [ ] Run tests, all green

### Task 0.8: Resolve Phase 0 deferred decisions D1/D2/D3 [Simple]
**File:** `decisions.md`
**Tests:** none — documentation work

- [ ] D1 (`PlanetaryFacility.consumable_levels`): default to **(b) keep as internal state** until Phase 4 evidence forces (a). Document in decisions.md with current rationale.
- [ ] D2 (`Empire.resource_pool` query-vs-cached): default to **(a) pure query**. Document; defer caching decision to Phase 5 close based on profiling.
- [ ] D3 (`mass_per_unit` initial values): defaults landed by Task 0.5 (extending `data/resources.json`). Document that they are balance-placeholders subject to retune.

### Task 0.9: Run sharded suite; confirm zero regression [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite
- [ ] Confirm 0 failures, 0 errors, 0 skipped, count >= baseline
- [ ] Document result in this checklist's Notes

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] D1/D2/D3 decisions logged in decisions.md
- [ ] Full sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
- [ ] Update `phase_state.json` phase_0.status to `complete` and record `phase_head_sha`
