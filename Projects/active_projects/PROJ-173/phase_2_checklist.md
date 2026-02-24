# Phase 2: Galaxy Internal Delegation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Decompose Galaxy (928 lines) into a thin facade with 4 internal delegates using the facade/delegation pattern. Galaxy keeps all public method signatures and direct dict access (`systems`, `name_map`). Internal logic moves to specialized modules. Zero external API changes — all 50+ dependent files unchanged.

---

## Tasks

### Task 2.1: Extract GalaxyWarpGenerator [Medium]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_warp_generator.py`
**Tests:** `pytest tests/integration/strategy/test_galaxy_gen.py tests/unit/strategy/data/test_galaxy.py -v`

- [ ] Read `galaxy.py` fully, identify warp generation methods:
  - [ ] `_calculate_warp_distance()` (lines 537-552, ~16L)
  - [ ] `_is_angle_clear()` (lines 554-580, ~27L)
  - [ ] `create_vars_link()` (lines 582-615, ~34L)
  - [ ] `_build_edge_candidates()` (lines 617-657, ~41L)
  - [ ] `_apply_mst_edges()` (lines 659-691, ~33L)
  - [ ] `_should_add_density_edge()` (lines 693-778, ~86L)
  - [ ] `_add_density_edges()` (lines 780-817, ~38L)
  - [ ] `generate_warp_lanes()` (lines 819-861, ~43L) — orchestrator
- [ ] Create `game/strategy/data/galaxy_warp_generator.py`:
  - [ ] `GalaxyWarpGenerator` class
  - [ ] Constructor: `__init__(self)` — stateless, receives galaxy as method parameter
  - [ ] Main method: `generate_warp_lanes(galaxy, rng)` — replaces Galaxy.generate_warp_lanes()
  - [ ] Move all 8 methods listed above
  - [ ] Adjust `self.` references to use `galaxy.` parameter
  - [ ] Import dependencies: hex_math, SpatialIndex, math, random
- [ ] Update `galaxy.py`:
  - [ ] In `__init__`: `self._warp_gen = GalaxyWarpGenerator()`
  - [ ] `generate_warp_lanes()` becomes: `self._warp_gen.generate_warp_lanes(self, rng)`
  - [ ] Remove all 8 moved methods
- [ ] Run tests: `pytest tests/integration/strategy/test_galaxy_gen.py tests/unit/strategy/data/test_galaxy.py -v`

**Notes:**

---

### Task 2.2: Extract GalaxySystemGenerator [Simple]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_system_generator.py`
**Tests:** `pytest tests/integration/strategy/test_galaxy_gen.py tests/integration/strategy/test_planet_gen.py -v`

- [ ] Identify system generation methods:
  - [ ] `generate_systems()` (lines 461-535, ~75L)
  - [ ] `generate_planets()` (lines 447-459, ~11L) — wrapper
- [ ] Create `game/strategy/data/galaxy_system_generator.py`:
  - [ ] `GalaxySystemGenerator` class
  - [ ] Constructor: `__init__(self, star_generator, planet_generator, naming, image_registry)`
  - [ ] Main method: `generate_systems(galaxy, count, min_dist, strategy, rng)`
  - [ ] Move system placement algorithm + planet generation
  - [ ] Adjust references: `self.add_system()` → `galaxy.add_system()`
- [ ] Update `galaxy.py`:
  - [ ] In `__init__`: `self._sys_gen = GalaxySystemGenerator(star_gen, planet_gen, naming, image_registry)`
  - [ ] `generate_systems()` becomes facade: `self._sys_gen.generate_systems(self, ...)`
  - [ ] Remove moved methods
- [ ] Run tests: `pytest tests/integration/strategy/test_galaxy_gen.py tests/integration/strategy/test_planet_gen.py -v`

**Notes:**

---

### Task 2.3: Extract GalaxyEntityRegistry [Medium]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_entity_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py -v`

- [ ] Identify entity lifecycle methods:
  - [ ] `register_planet()` (lines 172-192, ~21L)
  - [ ] `get_planet_by_id()` (lines 194-196, ~3L)
  - [ ] `unregister_planet()` (lines 296-325, ~30L)
  - [ ] `register_fleet()` (lines 269-275, ~7L)
  - [ ] `unregister_fleet()` (lines 277-283, ~7L)
  - [ ] `get_fleet_by_id()` (lines 285-294, ~10L)
  - [ ] `register_zone()` (lines 222-236, ~15L)
  - [ ] `unregister_zone()` (lines 238-254, ~18L)
- [ ] Create `game/strategy/data/galaxy_entity_registry.py`:
  - [ ] `GalaxyEntityRegistry` class
  - [ ] Constructor: `__init__(self, galaxy)` — receives Galaxy reference for shared state
  - [ ] Owns: `_next_planet_id` counter
  - [ ] Accesses through galaxy: `planets_by_id`, `fleets_by_id`, `_planet_to_system`, spatial dicts
  - [ ] Move all 8 lifecycle methods
  - [ ] Handle cross-references: `unregister_planet()` calls zone operations
- [ ] Update `galaxy.py`:
  - [ ] In `__init__`: `self._registry = GalaxyEntityRegistry(self)`
  - [ ] All public methods become facades: `def register_planet(self, ...): return self._registry.register_planet(...)`
  - [ ] Remove moved methods
- [ ] Run tests: `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py -v`

**Notes:**

---

### Task 2.4: Extract GalaxySpatialIndex [Medium]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v`

- [ ] Identify spatial query methods:
  - [ ] `get_system_at_location()` (lines 352-396, ~45L)
  - [ ] `get_all_fleets_in_system()` (lines 398-445, ~48L)
  - [ ] `get_planets_at_global_hex()` (lines 202-204, ~3L)
  - [ ] `get_planet_global_hex()` (lines 206-218, ~13L)
  - [ ] `get_zones_at_global_hex()` (lines 256-265, ~10L)
  - [ ] `get_system_of_object()` (lines 134-170, ~37L)
  - [ ] `get_system_of_planet()` (lines 198-200, ~3L)
- [ ] Create `game/strategy/data/galaxy_spatial_index.py`:
  - [ ] `GalaxySpatialIndex` class
  - [ ] Constructor: `__init__(self, galaxy)` — receives Galaxy reference
  - [ ] Owns: `_global_hex_planets`, `_global_hex_zones`, `_planet_to_system` dicts
  - [ ] Move all 7 spatial query methods
  - [ ] Adjust references from `self.systems` to `self._galaxy.systems`
- [ ] Update `galaxy.py`:
  - [ ] In `__init__`: `self._spatial = GalaxySpatialIndex(self)`
  - [ ] All public methods become facades
  - [ ] Move dict ownership to spatial index (or share via Galaxy.__init__)
  - [ ] Remove moved methods
- [ ] Run tests: `pytest tests/unit/strategy/data/test_galaxy.py -v`
- [ ] Run integration tests: `pytest tests/integration/strategy/ -v`

**Notes:**

---

### Task 2.5: Refactor Galaxy facade + serialization [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/integration/strategy/ -v`

- [ ] Verify Galaxy is now thin facade:
  - [ ] `__init__()` — creates shared state + 4 delegates
  - [ ] Properties/dicts: `systems`, `name_map` (external access)
  - [ ] System management: `add_system()`, `get_system_by_name()` (stay in Galaxy, simple)
  - [ ] Facade methods: all public methods delegate to appropriate sub-module
  - [ ] `to_dict()` / `from_dict()` — serialization orchestration (stays in Galaxy)
  - [ ] `remove_warp_link()` — stays in Galaxy (bilateral, needs systems access)
- [ ] Update `from_dict()` to rebuild delegates after deserialization:
  - [ ] Recreate entity registry with deserialized state
  - [ ] Recreate spatial index with deserialized state
  - [ ] Generators don't need deserialization (stateless)
- [ ] Run all galaxy-related tests: `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py tests/integration/strategy/test_galaxy_gen.py tests/integration/strategy/test_planet_gen.py tests/integration/strategy/test_planet_serialization.py -v`
- [ ] Verify: Galaxy < 400 lines

**Notes:**

---

### Task 2.6: Phase 2 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `galaxy.py` < 400 lines
  - [ ] `galaxy_warp_generator.py` exists (~220 lines)
  - [ ] `galaxy_system_generator.py` exists (~86 lines)
  - [ ] `galaxy_entity_registry.py` exists (~70+ lines)
  - [ ] `galaxy_spatial_index.py` exists (~120+ lines)
- [ ] Verify: All 50+ dependent files unchanged (no import changes needed)
- [ ] Verify: Galaxy public API identical (same method signatures)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
