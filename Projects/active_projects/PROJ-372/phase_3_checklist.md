# Phase 3: Galaxy query/spatial-aggregation services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-372 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Depends on:** Phase 2 (verified)
**Review Mode:** cumulative (Phases 0-3)
**Files (planned):** see manifest.md Phase 3 row group

**Status:** Not Started
**Objective:** Introduce `GalaxyState` dataclass owning the 11 mutable indexes + 2 ID counters + radius. Refactor the four PROJ-173-Phase-2 delegates (`GalaxyEntityRegistry`, `GalaxySpatialIndex`, `GalaxyWarpGenerator`, `GalaxySystemGenerator`) to take `GalaxyState` instead of `Galaxy`. Move 7 logic-bearing methods off `Galaxy` (3 zone/warp registration, ID-counter `get_next_fleet_id`, `remove_warp_link`, the inline warp-index rebuilds in `create_vars_link` and `generate_warp_lanes`) into the appropriate service. Preserve external API: `galaxy.systems` etc. become `@property` forwarders to `_state.systems`. Save format unchanged.

---

## Reading

- [ ] Phase 2 outcomes — confirm `planet.py` ≤ 350 LOC, sharded green
- [ ] `game/strategy/data/galaxy.py` lines 176-689
- [ ] All 4 PROJ-173-Phase-2 delegate files
- [ ] All 19 external readers of `galaxy.systems` / `galaxy.name_map` / `galaxy.planets_by_id` / `galaxy.fleets_by_id`

---

## Pre-flight

- [ ] Run `pytest tests/unit/strategy/data/test_galaxy*.py -v` — capture baseline
- [ ] `grep -rn 'galaxy\._global_hex_\|galaxy\._planet_to_system\|galaxy\._zone_to_system\|self\._global_hex_\|self\._planet_to_system\|self\._zone_to_system' game/ tests/` — capture every direct private-attr access; confirm Phase 0's AST guard already permits exactly the expected set

---

## Tasks

### Task 3.1: Define `GalaxyState` dataclass [Medium]
**File:** `game/strategy/data/galaxy_state.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_state.py -v` (new)

- [ ] `@dataclass` with the 13 fields per design.md Per-class-extraction-map / Galaxy section. Default factories for all dicts; `next_planet_id: int = 1`, `next_fleet_id: int = 1`, `radius: int` required.
- [ ] **Field renames:** drop the leading underscore on the dict fields (e.g. `_global_hex_planets` → `global_hex_planets`) — they're now public on the state object. The `Galaxy` facade re-exposes them as private (under-prefixed) properties only if external readers expect that name.
- [ ] Module ≤ 150 LOC.
- [ ] Tests: default values, mutability, equality.

**Notes:**

### Task 3.2: Refactor `GalaxyEntityRegistry` to take `GalaxyState` [Medium]
**File:** `game/strategy/data/galaxy_entity_registry.py` (modify)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_entity_registry.py -v`

- [ ] Change `__init__(self, galaxy: 'Galaxy')` to `__init__(self, state: 'GalaxyState')`. Replace every `self._galaxy.X` with `self._state.X`. Field renames per Task 3.1.
- [ ] Add `add_system(self, system: StarSystem) -> None` method (was `Galaxy.add_system` body — moves here).
- [ ] Add `get_next_fleet_id(self) -> int` method (was `Galaxy.get_next_fleet_id` — moves here).
- [ ] Update existing tests to construct `GalaxyState()` directly instead of `Galaxy()`.
- [ ] Module ≤ 250 LOC.

**Notes:**

### Task 3.3: Refactor `GalaxySpatialIndex` to take `GalaxyState` [Medium]
**File:** `game/strategy/data/galaxy_spatial_index.py` (modify)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_spatial_index.py -v`

- [ ] Change `__init__(self, galaxy: 'Galaxy')` to `__init__(self, state: 'GalaxyState')`. Field renames.
- [ ] Receive 3 methods from Galaxy: `_register_zones_from_system`, `_rebuild_warp_point_index`, `_rebuild_all_warp_point_indices`.
- [ ] Update existing tests to construct `GalaxyState()` directly.
- [ ] Module ≤ 250 LOC.

**Notes:**

### Task 3.4: Update `GalaxyWarpGenerator` and `GalaxySystemGenerator` signatures [Simple]
**Files:** `game/strategy/data/galaxy_warp_generator.py`, `game/strategy/data/galaxy_system_generator.py` (modify)
**Tests:** existing tests for both, plus integration `pytest tests/integration/strategy/`

- [ ] `GalaxyWarpGenerator`: methods that take `galaxy: Galaxy` now take `state: GalaxyState`. Inline `state.global_hex_warp_points` updates done locally (currently they are inline in `Galaxy.create_vars_link` and `Galaxy.generate_warp_lanes`).
- [ ] Add `remove_warp_link(self, state, system_a_name, system_b_name)` method (moves from Galaxy).
- [ ] `GalaxySystemGenerator`: same pattern; methods take `state: GalaxyState`.
- [ ] No LOC growth budget (already at 421 / 354).

**Notes:**

### Task 3.5: Wire Galaxy facade to use GalaxyState [Complex]
**File:** `game/strategy/data/galaxy.py` (modify)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v` + sharded

- [ ] Replace plain attributes with `self._state = GalaxyState(radius=radius)`.
- [ ] Add `@property` forwarders for the public surface external readers depend on:
  ```python
  @property
  def systems(self): return self._state.systems
  @property
  def name_map(self): return self._state.name_map
  @property
  def planets_by_id(self): return self._state.planets_by_id
  @property
  def fleets_by_id(self): return self._state.fleets_by_id
  @property
  def radius(self): return self._state.radius
  ```
- [ ] **For private indexes** that external code reads (verify via Phase 0's AST guard's allowed list), expose as `@property _global_hex_planets` etc. forwarding to `self._state.global_hex_planets` — preserves the existing external read surface where it exists. Allowed-list confirms no production code outside `galaxy.py` / `galaxy_entity_registry.py` / `galaxy_spatial_index.py` reads them; the facade still exposes them for these three consumers.
- [ ] Construct services from state: `self._registry = GalaxyEntityRegistry(self._state)`, etc.
- [ ] Methods 3, 4, 5, 16, 21 deleted (moved to services in Tasks 3.2, 3.3, 3.4).
- [ ] Method 26 (`create_vars_link`) and method 27 (`generate_warp_lanes`) bodies become 1-line delegates.
- [ ] **Verify:** `galaxy.py` ≤ 420 LOC after this phase (final ≤ 350 hits at Phase 4).

**Notes:**

### Task 3.6: Sweep callers / tests for renamed state fields [Medium]
**File:** various (search)
**Tests:** `pytest -v` per affected directory

- [ ] `grep -rn 'galaxy\._global_hex_\|galaxy\._planet_to_system\|galaxy\._zone_to_system\|galaxy\._global_hex_warp_points\|galaxy\._global_hex_zones' game/ tests/` — confirm zero hits outside the @property forwarders introduced in Task 3.5.
- [ ] Update test fixtures that construct `Galaxy()` for spatial-index / entity-registry tests to use `GalaxyState()` instead — faster + avoids JSON loading.
- [ ] **Verify:** no test setup loads `data/star_system_names.json` unless it actually exercises naming.

**Notes:**

### Task 3.7: Tighten AST guards [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py`, `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` (modify)
**Tests:** as named

- [ ] Tighten `GALAXY_LOC_CEILING` to 420.
- [ ] Tighten encapsulation guard to allow only `galaxy_entity_registry.py` and `galaxy_spatial_index.py` to read state private fields directly. `galaxy.py` itself reads via `self._state.X` (forwarded to public attrs of the dataclass — these are no longer private after the underscore drop, so the guard simplifies).

**Notes:**

### Task 3.8: Save round-trip regression test [Simple]
**File:** `tests/integration/strategy/test_save_round_trip_phase3.py` (new — temporary)

- [ ] Construct a Galaxy via `generate_systems(10)` + `generate_warp_lanes()` + `register_planet` for a few planets; assert `Galaxy.from_dict(galaxy.to_dict()).to_dict() == galaxy.to_dict()`.
- [ ] **Verify:** equality holds.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/data/test_galaxy*.py -v` green
- [ ] `pytest tests/integration/strategy/ -v` green
- [ ] `python Tools/test_sharded/test_sharded.py` green; pass count ≥ baseline
- [ ] `galaxy.py` ≤ 420 LOC (final ≤ 350 in Phase 4)
- [ ] AST guards green
- [ ] Update status / plan.md / Current State pointing to Phase 4
