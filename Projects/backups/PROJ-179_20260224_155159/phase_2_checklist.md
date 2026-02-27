# Phase 2: Encapsulation & Performance Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-179 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix from_dict() encapsulation violation and make get_system_at_location() O(1).

---

## Tasks

### Task 2.1: Add restore_planet() to GalaxyEntityRegistry [Medium]
**Files:** `game/strategy/data/galaxy_entity_registry.py`, `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py -x`

- [x] Add `restore_planet(self, system, planet)` method to `GalaxyEntityRegistry` (after `register_planet`, ~line 58):
  ```python
  def restore_planet(self, system: 'StarSystem', planet: 'Planet') -> None:
      """Register a planet with pre-existing ID (for deserialization).

      Unlike register_planet(), this does NOT assign a new ID.
      The planet.id must already be set (from Planet.from_dict()).

      Args:
          system: StarSystem containing the planet.
          planet: Planet to register (must have id already set).
      """
      self._galaxy.planets_by_id[planet.id] = planet
      self._galaxy._planet_to_system[planet] = system
      global_hex = system.global_location + planet.location
      if global_hex not in self._galaxy._global_hex_planets:
          self._galaxy._global_hex_planets[global_hex] = []
      self._galaxy._global_hex_planets[global_hex].append(planet)
      if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
          self.register_zone(system, planet)
  ```
- [x] In `Galaxy.from_dict()` (`galaxy.py` lines 567-583), replace manual index rebuilding loop body with:
  ```python
  for planet in system.planets:
      galaxy._registry.restore_planet(system, planet)
  ```
- [x] Write test: deserialize galaxy, verify planet IDs are preserved (not reassigned)
- [x] Write test: deserialize galaxy, verify `get_system_of_planet()` works for all restored planets
- [x] Write test: deserialize galaxy, verify `get_planets_at_global_hex()` returns correct planets
- [x] Verify: `pytest tests/ --testmon` all pass

**Notes:** Added 8 tests in TestRestorePlanet class

### Task 2.2: Add zone-to-system index and refactor get_system_at_location() to O(1) [Medium]
**Files:** `game/strategy/data/galaxy.py`, `game/strategy/data/galaxy_entity_registry.py`, `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/ tests/integration/strategy/facade/test_system_queries.py tests/unit/strategy/validation/ -x`

- [x] Add `self._zone_to_system = {}` to `Galaxy.__init__()` (`galaxy.py`, after line 164)
- [x] Update `GalaxyEntityRegistry.register_zone()` to also set `self._galaxy._zone_to_system[id(obj)] = system`
- [x] Update `GalaxyEntityRegistry.unregister_zone()` to also do `self._galaxy._zone_to_system.pop(id(obj), None)`
- [x] Add `self._global_hex_warp_points = {}` to `Galaxy.__init__()` (HexCoord -> StarSystem)
- [x] Add warp point registration in `Galaxy.add_system()` (after star zone registration, ~line 190)
- [x] Add warp point registration in `Galaxy.from_dict()` (after star zone registration, ~line 565)
- [x] Update `Galaxy.create_vars_link()` to register warp points in index
- [x] Update `Galaxy.remove_warp_link()` to remove warp points from index
- [x] Update `Galaxy.generate_warp_lanes()` to rebuild warp point index after generation
- [x] Refactor `GalaxySpatialIndex.get_system_at_location()` to use O(1) lookups
- [x] Write test: `get_system_at_location()` finds system via planet global hex
- [x] Write test: `get_system_at_location()` finds system via star/zone global hex
- [x] Write test: `get_system_at_location()` finds system via warp point global hex
- [x] Write test: `get_system_at_location()` returns None for deep space hex
- [x] Write test: warp point index updated on remove_warp_link()
- [x] Write test: from_dict() rebuilds warp point index
- [x] Verify: All 14 production callers still work correctly
- [x] Verify: `pytest tests/` all pass (12358 passed, 1 skipped)

**Notes:** Used `id(obj)` instead of `obj` as dict key for `_zone_to_system` because Star objects are not hashable. Added 9 tests in TestGetSystemAtLocationO1 class.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
