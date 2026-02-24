# Phase 2: Encapsulation & Performance Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-179 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix from_dict() encapsulation violation and make get_system_at_location() O(1).

---

## Tasks

### Task 2.1: Add restore_planet() to GalaxyEntityRegistry [Medium]
**Files:** `game/strategy/data/galaxy_entity_registry.py`, `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/unit/strategy/data/test_galaxy_cleanup.py -x`

- [ ] Add `restore_planet(self, system, planet)` method to `GalaxyEntityRegistry` (after `register_planet`, ~line 58):
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
- [ ] In `Galaxy.from_dict()` (`galaxy.py` lines 567-583), replace manual index rebuilding loop body with:
  ```python
  for planet in system.planets:
      galaxy._registry.restore_planet(system, planet)
  ```
- [ ] Write test: deserialize galaxy, verify planet IDs are preserved (not reassigned)
- [ ] Write test: deserialize galaxy, verify `get_system_of_planet()` works for all restored planets
- [ ] Write test: deserialize galaxy, verify `get_planets_at_global_hex()` returns correct planets
- [ ] Verify: `pytest tests/ --testmon` all pass

**Notes:**

### Task 2.2: Add zone-to-system index and refactor get_system_at_location() to O(1) [Medium]
**Files:** `game/strategy/data/galaxy.py`, `game/strategy/data/galaxy_entity_registry.py`, `game/strategy/data/galaxy_spatial_index.py`
**Tests:** `pytest tests/unit/strategy/data/ tests/integration/strategy/facade/test_system_queries.py tests/unit/strategy/validation/ -x`

- [ ] Add `self._zone_to_system = {}` to `Galaxy.__init__()` (`galaxy.py`, after line 164)
- [ ] Update `GalaxyEntityRegistry.register_zone()` to also set `self._galaxy._zone_to_system[obj] = system`
- [ ] Update `GalaxyEntityRegistry.unregister_zone()` to also do `self._galaxy._zone_to_system.pop(obj, None)`
- [ ] Add `self._global_hex_warp_points = {}` to `Galaxy.__init__()` (HexCoord → StarSystem)
- [ ] Add warp point registration in `Galaxy.add_system()` (after star zone registration, ~line 190):
  ```python
  for wp in system.warp_points:
      global_hex = system.global_location + wp.location
      self._global_hex_warp_points[global_hex] = system
  ```
- [ ] Add warp point registration in `Galaxy.from_dict()` (after star zone registration, ~line 565):
  ```python
  for wp in system.warp_points:
      global_hex = coord + wp.location
      galaxy._global_hex_warp_points[global_hex] = system
  ```
- [ ] Refactor `GalaxySpatialIndex.get_system_at_location()` to use O(1) lookups:
  ```python
  def get_system_at_location(self, location):
      # O(1) direct system lookup
      if location in self._galaxy.systems:
          return self._galaxy.systems[location]
      # O(1) planet lookup
      planets = self._galaxy._global_hex_planets.get(location, [])
      if planets:
          return self._galaxy._planet_to_system.get(planets[0])
      # O(1) zone lookup (stars, Dyson Spheres)
      zones = self._galaxy._global_hex_zones.get(location, [])
      if zones:
          return self._galaxy._zone_to_system.get(zones[0])
      # O(1) warp point lookup
      wp_system = self._galaxy._global_hex_warp_points.get(location)
      if wp_system:
          return wp_system
      return None
  ```
- [ ] Write test: `get_system_at_location()` finds system via planet global hex
- [ ] Write test: `get_system_at_location()` finds system via star/zone global hex
- [ ] Write test: `get_system_at_location()` finds system via warp point global hex
- [ ] Write test: `get_system_at_location()` returns None for deep space hex
- [ ] Verify: All 14 production callers still work correctly
- [ ] Verify: `pytest tests/ --testmon` all pass

**Notes:** The `_global_hex_warp_points` index is new. Warp point registration needs to be added to both `add_system()` and `from_dict()`. Also update `create_warp_link()` if it creates warp points after system registration.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
