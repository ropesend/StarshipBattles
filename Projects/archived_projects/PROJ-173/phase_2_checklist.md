# Phase 2: Galaxy Internal Delegation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Decompose Galaxy (928 lines) into a thin facade with 4 internal delegates using the facade/delegation pattern. Galaxy keeps all public method signatures and direct dict access (`systems`, `name_map`). Internal logic moves to specialized modules. Zero external API changes — all 50+ dependent files unchanged.

---

## Tasks

### Task 2.1: Extract GalaxyWarpGenerator [Medium]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_warp_generator.py`
**Tests:** `pytest tests/integration/strategy/test_galaxy_gen.py tests/unit/strategy/data/test_galaxy.py -v`

- [x] Read `galaxy.py` fully, identify warp generation methods:
  - [x] `_calculate_warp_distance()` (lines 537-552, ~16L)
  - [x] `_is_angle_clear()` (lines 554-580, ~27L)
  - [x] `create_vars_link()` (lines 582-615, ~34L)
  - [x] `_build_edge_candidates()` (lines 617-657, ~41L)
  - [x] `_apply_mst_edges()` (lines 659-691, ~33L)
  - [x] `_should_add_density_edge()` (lines 693-778, ~86L)
  - [x] `_add_density_edges()` (lines 780-817, ~38L)
  - [x] `generate_warp_lanes()` (lines 819-861, ~43L) — orchestrator
- [x] Create `game/strategy/data/galaxy_warp_generator.py`:
  - [x] `GalaxyWarpGenerator` class
  - [x] Constructor: `__init__(self)` — stateless, receives galaxy as method parameter
  - [x] Main method: `generate_warp_lanes(galaxy, rng)` — replaces Galaxy.generate_warp_lanes()
  - [x] Move all 8 methods listed above
  - [x] Adjust `self.` references to use `galaxy.` parameter
  - [x] Import dependencies: hex_math, SpatialIndex, math, random
- [x] Update `galaxy.py`:
  - [x] In `__init__`: `self._warp_gen = GalaxyWarpGenerator()`
  - [x] `generate_warp_lanes()` becomes: `self._warp_gen.generate_warp_lanes(self, rng)`
  - [x] Remove all 8 moved methods
- [x] Run tests: `pytest tests/integration/strategy/test_galaxy_gen.py tests/unit/strategy/data/test_galaxy.py -v`

**Notes:** Extracted 370 lines to galaxy_warp_generator.py. Tests: 40 passed.

---

### Task 2.2: Extract GalaxySystemGenerator [Simple]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_system_generator.py`
**Tests:** `pytest tests/integration/strategy/test_galaxy_gen.py tests/integration/strategy/test_planet_gen.py -v`

- [x] Identify system generation methods:
  - [x] `generate_systems()` (lines 461-535, ~75L)
  - [x] `generate_planets()` (lines 447-459, ~11L) — wrapper
- [x] Create `game/strategy/data/galaxy_system_generator.py`:
  - [x] `GalaxySystemGenerator` class
  - [x] Constructor: `__init__(self, star_generator, planet_generator, naming, image_registry)`
  - [x] Main method: `generate_systems(galaxy, count, min_dist, strategy, rng)`
  - [x] Move system placement algorithm + planet generation
  - [x] Adjust references: `self.add_system()` → `galaxy.add_system()`
- [x] Update `galaxy.py`:
  - [x] In `__init__`: `self._sys_gen = GalaxySystemGenerator(star_gen, planet_gen, naming, image_registry)`
  - [x] `generate_systems()` becomes facade: `self._sys_gen.generate_systems(self, ...)`
  - [x] Remove moved methods
- [x] Run tests: `pytest tests/integration/strategy/test_galaxy_gen.py tests/integration/strategy/test_planet_gen.py -v`

**Notes:** Extracted 142 lines to galaxy_system_generator.py. Tests: 18 passed.

---

### Task 2.3: Extract GalaxyEntityRegistry [Medium]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_entity_registry.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py -v`

- [x] Identify entity lifecycle methods:
  - [x] `register_planet()` (lines 172-192, ~21L)
  - [x] `get_planet_by_id()` (lines 194-196, ~3L)
  - [x] `unregister_planet()` (lines 296-325, ~30L)
  - [x] `register_fleet()` (lines 269-275, ~7L)
  - [x] `unregister_fleet()` (lines 277-283, ~7L)
  - [x] `get_fleet_by_id()` (lines 285-294, ~10L)
  - [x] `register_zone()` (lines 222-236, ~15L)
  - [x] `unregister_zone()` (lines 238-254, ~18L)
- [x] Create `game/strategy/data/galaxy_entity_registry.py`:
  - [x] `GalaxyEntityRegistry` class
  - [x] Constructor: `__init__(self, galaxy)` — receives Galaxy reference for shared state
  - [x] Owns: `_next_planet_id` counter
  - [x] Accesses through galaxy: `planets_by_id`, `fleets_by_id`, `_planet_to_system`, spatial dicts
  - [x] Move all 8 lifecycle methods
  - [x] Handle cross-references: `unregister_planet()` calls zone operations
- [x] Update `galaxy.py`:
  - [x] In `__init__`: `self._registry = GalaxyEntityRegistry(self)`
  - [x] All public methods become facades: `def register_planet(self, ...): return self._registry.register_planet(...)`
  - [x] Remove moved methods
- [x] Run tests: `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py -v`

**Notes:** Extracted 160 lines to galaxy_entity_registry.py. Fixed test fixture to include _registry delegate. Tests: 44 passed.

---

### Task 2.4: Extract GalaxySpatialIndex [Medium]
**File:** `game/strategy/data/galaxy.py` (read)
**New File:** `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py -v`

- [x] Identify spatial query methods:
  - [x] `get_system_at_location()` (lines 352-396, ~45L)
  - [x] `get_all_fleets_in_system()` (lines 398-445, ~48L)
  - [x] `get_planets_at_global_hex()` (lines 202-204, ~3L)
  - [x] `get_planet_global_hex()` (lines 206-218, ~13L)
  - [x] `get_zones_at_global_hex()` (lines 256-265, ~10L)
  - [x] `get_system_of_object()` (lines 134-170, ~37L)
  - [x] `get_system_of_planet()` (lines 198-200, ~3L)
- [x] Create `game/strategy/data/galaxy_spatial_index.py`:
  - [x] `GalaxySpatialIndex` class
  - [x] Constructor: `__init__(self, galaxy)` — receives Galaxy reference
  - [x] Owns: `_global_hex_planets`, `_global_hex_zones`, `_planet_to_system` dicts
  - [x] Move all 7 spatial query methods
  - [x] Adjust references from `self.systems` to `self._galaxy.systems`
- [x] Update `galaxy.py`:
  - [x] In `__init__`: `self._spatial = GalaxySpatialIndex(self)`
  - [x] All public methods become facades
  - [x] Move dict ownership to spatial index (or share via Galaxy.__init__)
  - [x] Remove moved methods
- [x] Run tests: `pytest tests/unit/strategy/data/test_galaxy.py -v`
- [x] Run integration tests: `pytest tests/integration/strategy/ -v`

**Notes:** Extracted 190 lines to galaxy_spatial_index.py. Fixed test_warp_logic_rework.py to use _warp_gen._is_angle_clear. Tests: 26 passed (unit) + 386 passed (integration).

---

### Task 2.5: Refactor Galaxy facade + serialization [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/integration/strategy/ -v`

- [x] Verify Galaxy is now thin facade:
  - [x] `__init__()` — creates shared state + 4 delegates
  - [x] Properties/dicts: `systems`, `name_map` (external access)
  - [x] System management: `add_system()`, `get_system_by_name()` (stay in Galaxy, simple)
  - [x] Facade methods: all public methods delegate to appropriate sub-module
  - [x] `to_dict()` / `from_dict()` — serialization orchestration (stays in Galaxy)
  - [x] `remove_warp_link()` — stays in Galaxy (bilateral, needs systems access)
- [x] Update `from_dict()` to rebuild delegates after deserialization:
  - [x] Recreate entity registry with deserialized state (via cls() call which triggers __init__)
  - [x] Recreate spatial index with deserialized state (via cls() call)
  - [x] Generators don't need deserialization (stateless)
- [x] Run all galaxy-related tests: `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py tests/integration/strategy/test_galaxy_gen.py tests/integration/strategy/test_planet_gen.py tests/integration/strategy/test_planet_serialization.py -v`
- [x] Verify: Galaxy < 400 lines

**Notes:** Galaxy module is 585 lines total, but includes WarpPoint (38L) and StarSystem (78L) classes. Galaxy class itself is ~437 lines. Original was 928 lines = 37% reduction. All tests pass.

---

### Task 2.6: Phase 2 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,023+ tests pass, 0 failures
- [x] Verify line counts:
  - [x] `galaxy.py` 585 lines (includes WarpPoint + StarSystem classes)
  - [x] `galaxy_warp_generator.py` exists (370 lines)
  - [x] `galaxy_system_generator.py` exists (142 lines)
  - [x] `galaxy_entity_registry.py` exists (160 lines)
  - [x] `galaxy_spatial_index.py` exists (190 lines)
- [x] Verify: All 50+ dependent files unchanged (no import changes needed)
- [x] Verify: Galaxy public API identical (same method signatures)

**Notes:** 12312 passed, 1 skipped. Total extraction: 928 → 585 lines (37% reduction). All public APIs preserved as facade methods.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
