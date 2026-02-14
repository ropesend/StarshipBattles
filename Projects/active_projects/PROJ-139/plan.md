# PROJ-139: Dyson Sphere Multi-Hex Stellar Objects

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-139` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-139 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Core Zone Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Galaxy Zone Registry | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Dyson Sphere Enhancements | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Zone-Aware Selection & Interaction | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Dyson Sphere Rendering | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Integration & Verification | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-13
**Active Phase:** Phase 2 - Galaxy Zone Registry
**Last Action:** Completed Phase 1: Core Zone Infrastructure
**Next Action:** Begin Phase 2: Galaxy Zone Registry
**Blockers:** None
**Context for Next Agent:** Phase 1 complete: hex_circle_filled (7 tests), IZoneOccupant protocol (5 tests), Star.occupied_hexes (5 tests), Planet.occupied_hexes + diameter_hexes (9 tests). Total: +26 tests. Begin Phase 2: Add zone registry to Galaxy, register/unregister methods, wire into add_system/register_planet.

## Overview
Add a generalized multi-hex zone system so game objects (stars, Dyson Spheres, future objects) can occupy multiple hexes on the galaxy map. Clicking any hex in the zone selects the object. Enhance Dyson Sphere creation to use proper image, scale to 11-hex diameter, be colonizable from any zone hex, and have ideal conditions matching the creator species.

## Goals
- Generalized `IZoneOccupant` protocol for any object that spans multiple hexes
- Stars automatically get zone coverage based on existing `diameter_hexes`
- Dyson Sphere rendered with `Sphereworld_Portrait.png` scaled to 11-hex diameter
- Clicking any hex in a zone selects the zone-owning object
- Dyson Sphere colonizable from any hex in its zone
- Dyson Sphere conditions exactly match creator species' ideal environment

## Scope
**In:**
- `IZoneOccupant` protocol + `hex_circle_filled()` utility
- `occupied_hexes` property on Star and Planet classes
- Galaxy zone registry (`_global_hex_zones`) with register/unregister/query
- Zone-aware selection in `_handle_picking()`
- Zone-aware colonization in `ColonizeValidator`
- Dyson Sphere image rendering at 11-hex diameter
- Dyson Sphere conditions from creator's `race_config`
- Serialization of zone data (Star `occupied_hexes`, Planet `diameter_hexes`)
- Zone index rebuild during `from_dict()`

**Out:**
- Pathfinding changes (zones are passable)
- Warp point placement zone avoidance (future project)
- Binary star zone overlap validation (future project)
- Nebulae, asteroid fields, or other zone types (future)

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Hex math | `game/core/hex_math.py` | `hex_ring()`, new `hex_circle_filled()` |
| Protocols | `game/core/protocols.py` | New `IZoneOccupant` |
| Star | `game/strategy/data/stars.py:77` | `Star` dataclass |
| Planet | `game/strategy/data/planet.py:137` | `Planet` dataclass |
| Galaxy | `game/strategy/data/galaxy.py:95` | `Galaxy` class |
| StarSystem | `game/strategy/data/galaxy.py:43` | `StarSystem` class |
| Input Handler | `game/ui/screens/strategy_input_handler.py:719` | `_handle_picking()` |
| Renderer | `game/ui/screens/strategy_renderer.py:332` | Star/planet rendering |
| Colonize Validator | `game/strategy/validation/colonize_validator.py:50` | `validate()` |
| Superweapon Processor | `game/strategy/engine/superweapon_order_processor.py:381` | `process_create_dyson_sphere()` |
| Colonization UI | `game/ui/screens/strategy_colonization.py` | `on_colonize_click()` |
| Race Config | `game/strategy/data/race_config.py:104` | Environmental preferences |
| Dyson Image | `assets/Images/Stellar Objects/Sphere world/Sphereworld_Portrait.png` | 4.4MB PNG |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Generalized IZoneOccupant protocol | Supports irregular shapes, extensible to any object type |
| 2026-02-13 | Zone data on objects, Galaxy reverse-lookup registry | O(1) lookups, rebuilt on load |
| 2026-02-13 | Star zones passable | No pathfinding changes needed |
| 2026-02-13 | Clearing radius = zone radius (5) | Align to actual Dyson Sphere size |
| 2026-02-13 | Dyson conditions from race_config | Exact match = 1.0 habitability for creator |

See [decisions.md](decisions.md) for full log.

## Initial Analysis
See [design.md](design.md) for full analysis.

## Swarm Findings Summary
### Architecture
- Two-level coordinate system (galaxy-global + system-local)
- `_global_hex_planets` dict provides O(1) spatial lookup pattern
- `get_all_fleets_in_system()` already builds Set[HexCoord] - zone pattern exists
- No `hex_circle_filled()` utility exists yet

### Key Patterns to Reuse
- **Set[HexCoord]**: `galaxy.py:329-342` - system hex set construction
- **Spatial registry**: `_global_hex_planets` dict pattern
- **Protocol system**: `protocols.py` runtime-checkable protocols
- **Star rendering**: `strategy_renderer.py:351` - `diameter_hexes * hex_size * zoom`

### Risks Identified
1. **get_system_at_location() O(n)** - mitigated by zone registry providing O(1) alternative
2. **Performance** - ~3000-6000 zone entries acceptable
3. **Binary star overlap** - out of scope, deferred

---

## Phases

### Phase 1: Core Zone Infrastructure [Medium]
**Objective:** Add hex utility and IZoneOccupant protocol. Add `occupied_hexes` to Star and Planet.
**Status:** Not Started

#### Task 1.1: Add `hex_circle_filled()` to hex_math.py [Simple]
**File:** `game/core/hex_math.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`
- [ ] Add function `hex_circle_filled(center: HexCoord, radius: int) -> FrozenSet[HexCoord]` after `hex_ring()` (after line 195)
- [ ] Implementation: iterate `hex_ring(r)` for r in range(0, radius+1), offset each by center, return frozenset
- [ ] Write tests in `tests/unit/core/test_hex_math_core.py`:
  - `test_hex_circle_filled_radius_0` returns just center
  - `test_hex_circle_filled_radius_1` returns 7 hexes (center + 6 neighbors)
  - `test_hex_circle_filled_radius_2` returns 19 hexes
  - `test_hex_circle_filled_radius_5` returns 91 hexes (Dyson Sphere size)
  - `test_hex_circle_filled_with_offset_center`
**Notes:**

#### Task 1.2: Add `IZoneOccupant` protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/`
- [ ] Add import: `from typing import FrozenSet` (top of file)
- [ ] Add protocol after `IPlanet` (after line 188):
  ```python
  @runtime_checkable
  class IZoneOccupant(Protocol):
      """Protocol for entities that occupy multiple hexes."""
      @property
      def occupied_hexes(self) -> FrozenSet:
          """Set of LOCAL hex coords this object occupies."""
          ...
  ```
- [ ] Write test in `tests/unit/core/test_protocols.py` (or existing protocol test file):
  - `test_star_is_zone_occupant` - verify Star satisfies protocol
  - `test_planet_is_zone_occupant` - verify Planet satisfies protocol
**Notes:**

#### Task 1.3: Add `occupied_hexes` property to Star [Medium]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/`
- [ ] Add import: `from game.core.hex_math import hex_circle_filled` (line 7 area)
- [ ] Add cached property to Star dataclass (after `location` field, around line 89):
  ```python
  @property
  def occupied_hexes(self) -> FrozenSet:
      radius = max(0, int(math.ceil(self.diameter_hexes / 2.0)))
      return hex_circle_filled(self.location, radius)
  ```
- [ ] Add `import math` if not already present
- [ ] No serialization change needed - `occupied_hexes` is computed from `diameter_hexes` + `location`
- [ ] Write tests:
  - `test_star_occupied_hexes_small` (diameter_hexes=1.0 -> radius 1 -> 7 hexes)
  - `test_star_occupied_hexes_large` (diameter_hexes=11.0 -> radius 6 -> 127 hexes)
  - `test_star_occupied_hexes_sub_hex` (diameter_hexes=0.5 -> radius 1 -> 7 hexes)
  - `test_star_occupied_hexes_with_offset_location`
**Notes:**

#### Task 1.4: Add `occupied_hexes` and `diameter_hexes` to Planet [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/`
- [ ] Add import: `from game.core.hex_math import hex_circle_filled` (top of file)
- [ ] Add `diameter_hexes: float = 0.0` field to Planet dataclass (after `image_rotation`, line 196)
- [ ] Add property to Planet class:
  ```python
  @property
  def occupied_hexes(self) -> FrozenSet:
      if self.diameter_hexes > 0:
          radius = max(0, int(math.ceil(self.diameter_hexes / 2.0)))
          return hex_circle_filled(self.location, radius)
      return frozenset({self.location})
  ```
- [ ] Add `import math` if not already present
- [ ] Update `to_dict()` (line 292): add `'diameter_hexes': self.diameter_hexes` to dict
- [ ] Update `from_dict()` (line 372): add `diameter_hexes=data.get('diameter_hexes', 0.0)`
- [ ] Write tests:
  - `test_planet_occupied_hexes_normal` - regular planet returns single hex
  - `test_planet_occupied_hexes_dyson_sphere` - planet with diameter_hexes=11 returns zone
  - `test_planet_serialization_with_diameter_hexes` - round-trip test
**Notes:**

---

### Phase 2: Galaxy Zone Registry [Medium]
**Objective:** Add zone tracking to Galaxy. Register/unregister zones. Update lookups.
**Status:** Not Started

#### Task 2.1: Add zone registry to Galaxy.__init__ [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] Add to `__init__` (after line 107):
  ```python
  self._global_hex_zones = {}  # HexCoord -> List[object] (stars, multi-hex planets)
  ```
**Notes:**

#### Task 2.2: Add `register_zone()` and `unregister_zone()` methods [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] Add `register_zone(self, system, obj)` method (after `register_planet`, ~line 183):
  ```python
  def register_zone(self, system: 'StarSystem', obj) -> None:
      """Register a multi-hex zone object (star, dyson sphere) in the zone index."""
      if not hasattr(obj, 'occupied_hexes'):
          return
      for local_hex in obj.occupied_hexes:
          global_hex = system.global_location + local_hex
          if global_hex not in self._global_hex_zones:
              self._global_hex_zones[global_hex] = []
          if obj not in self._global_hex_zones[global_hex]:
              self._global_hex_zones[global_hex].append(obj)
  ```
- [ ] Add `unregister_zone(self, system, obj)` method:
  ```python
  def unregister_zone(self, system: 'StarSystem', obj) -> None:
      """Remove a multi-hex zone object from the zone index."""
      if not hasattr(obj, 'occupied_hexes'):
          return
      for local_hex in obj.occupied_hexes:
          global_hex = system.global_location + local_hex
          if global_hex in self._global_hex_zones:
              zone_list = self._global_hex_zones[global_hex]
              if obj in zone_list:
                  zone_list.remove(obj)
              if not zone_list:
                  del self._global_hex_zones[global_hex]
  ```
- [ ] Add `get_zones_at_global_hex(self, global_hex)` query method:
  ```python
  def get_zones_at_global_hex(self, global_hex: HexCoord) -> list:
      """O(1) spatial lookup: get all zone objects at a global hex."""
      return self._global_hex_zones.get(global_hex, [])
  ```
- [ ] Write tests:
  - `test_register_zone_adds_to_all_hexes`
  - `test_unregister_zone_removes_from_all_hexes`
  - `test_get_zones_at_global_hex_returns_object`
  - `test_get_zones_at_global_hex_empty_returns_empty_list`
  - `test_register_zone_no_duplicates`
**Notes:**

#### Task 2.3: Register star zones during system setup [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] In `add_system()` (line 119): after adding system, register zones for all stars:
  ```python
  for star in system.stars:
      self.register_zone(system, star)
  ```
- [ ] In `from_dict()` (line 804-826): after rebuilding planet indexes, register star zones:
  ```python
  # After planet index rebuild loop (after line 824):
  for star in system.stars:
      galaxy.register_zone(system, star)
  ```
- [ ] Write tests:
  - `test_add_system_registers_star_zones`
  - `test_from_dict_rebuilds_star_zones`
**Notes:**

#### Task 2.4: Update `register_planet` / `unregister_planet` for zone-aware planets [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] In `register_planet()` (line 166): after existing spatial index update (line 182), add zone registration for multi-hex planets:
  ```python
  # Register zone if planet has multi-hex footprint
  if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
      self.register_zone(system, planet)
  ```
- [ ] In `unregister_planet()` (line 225): before removing from system (line 249), add zone unregistration:
  ```python
  # Unregister zone if planet has multi-hex footprint
  if system is not None and hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
      self.unregister_zone(system, planet)
  ```
- [ ] In `from_dict()` (line 812-824): after planet index rebuild, register planet zones:
  ```python
  if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
      galaxy.register_zone(system, planet)
  ```
- [ ] Write tests:
  - `test_register_dyson_sphere_planet_creates_zones`
  - `test_unregister_dyson_sphere_planet_removes_zones`
**Notes:**

#### Task 2.5: Update `get_system_at_location()` to check zones [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] In `get_system_at_location()` (line 277): after existing slow-path checks (line 311), add zone check before returning None:
  ```python
  # Check zone registry for multi-hex objects
  zone_objects = self._global_hex_zones.get(location, [])
  for zone_obj in zone_objects:
      # Find which system owns this zone object
      for sys_loc, sys in self.systems.items():
          if zone_obj in sys.stars or zone_obj in sys.planets:
              return sys
  ```
- [ ] Write tests:
  - `test_get_system_at_location_finds_system_via_star_zone`
  - `test_get_system_at_location_finds_system_via_dyson_zone`
**Notes:**

#### Task 2.6: Update `get_all_fleets_in_system()` to include zones [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`
- [ ] In `get_all_fleets_in_system()` (line 315): after building system_hexes from stars (line 338), add zone hexes:
  ```python
  # Add star zone hexes
  for star in system.stars:
      if hasattr(star, 'occupied_hexes'):
          for local_hex in star.occupied_hexes:
              system_hexes.add(system.global_location + local_hex)
  # Add planet zone hexes (Dyson Spheres)
  for planet in system.planets:
      if hasattr(planet, 'diameter_hexes') and planet.diameter_hexes > 0:
          for local_hex in planet.occupied_hexes:
              system_hexes.add(system.global_location + local_hex)
  ```
- [ ] Write test: `test_get_all_fleets_in_system_includes_zone_hexes`
**Notes:**

---

### Phase 3: Dyson Sphere Enhancements [Medium]
**Objective:** Update Dyson Sphere creation to use race_config conditions, set diameter_hexes, align clearing radius.
**Status:** Not Started

#### Task 3.1: Update `process_create_dyson_sphere()` conditions from race_config [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`
- [ ] Update `process_create_dyson_sphere()` (line 381): accept empire parameter and extract race_config
- [ ] Replace hardcoded conditions (lines 459-464) with race_config-derived values:
  ```python
  race = empire.race_config if hasattr(empire, 'race_config') else None
  if race:
      gravity = race.gravity_ideal * 9.81
      temperature = race.temperature_ideal
      water = race.water_ideal
      # Build ideal atmosphere from preferences
      atmosphere = {}
      for gas, preference in race.atmosphere_preferences.items():
          if preference > 0:
              atmosphere[gas] = preference * 1013.25  # Scale to partial pressure
  else:
      # Fallback to current defaults
      gravity = 9.8
      temperature = 288.0
      water = 0.3
      atmosphere = {}
  ```
- [ ] Replace `surface_gravity=9.8` with `surface_gravity=gravity` (line 459)
- [ ] Replace `surface_temperature=288.0` with `surface_temperature=temperature` (line 461)
- [ ] Replace `surface_water=0.3` with `surface_water=water` (line 462)
- [ ] Add `atmosphere=atmosphere` to Planet constructor
- [ ] Update tests for race_config-derived conditions
**Notes:**

#### Task 3.2: Set `diameter_hexes` on Dyson Sphere [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`
- [ ] In Dyson Sphere Planet constructor (line 451-467): add `diameter_hexes=11.0` after `image_id`
- [ ] Write test: `test_dyson_sphere_has_diameter_hexes_11`
**Notes:**

#### Task 3.3: Align clearing radius to zone radius [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`
- [ ] Change `dyson_radius = 9` (line 432) to `dyson_radius = 5` (zone radius for 11-hex diameter)
- [ ] Update existing test that checks nearby planet removal radius
**Notes:**

#### Task 3.4: Register Dyson Sphere zone after creation [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`
- [ ] After `galaxy.register_planet(system, dyson)` (line 471): zone is auto-registered by `register_planet` (Task 2.4)
- [ ] Verify in test that zone hexes are registered after Dyson creation
**Notes:** No code change needed if Task 2.4 is complete. Just verify.

---

### Phase 4: Zone-Aware Selection & Interaction [Medium]
**Objective:** Update UI selection and colonization to work with multi-hex zones.
**Status:** Not Started

#### Task 4.1: Update `_handle_picking()` for zone selection [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py`
- [ ] In `_handle_picking()` (line 719): after star collection (line 756), add zone object collection:
  ```python
  # Check zone registry for multi-hex objects at clicked hex
  if hasattr(self.scene, 'galaxy') and self.scene.galaxy:
      zone_objects = self.scene.galaxy.get_zones_at_global_hex(hex_clicked)
      for zone_obj in zone_objects:
          if zone_obj not in sector_contents:
              sector_contents.append(zone_obj)
  ```
- [ ] Alternative: access galaxy through `self.scene.session.galaxy` or similar - check actual scene attribute
- [ ] Write tests:
  - `test_picking_finds_star_via_zone_hex`
  - `test_picking_finds_dyson_sphere_via_zone_hex`
  - `test_picking_priority_fleet_over_zone`
**Notes:** Check how scene exposes galaxy reference.

#### Task 4.2: Update `ColonizeValidator.validate()` for zone colonization [Medium]
**File:** `game/strategy/validation/colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`
- [ ] In `validate()` (line 81): after getting planets at fleet hex, ALSO get planets from zone objects:
  ```python
  all_planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)

  # Also check zone registry - fleet may be in a multi-hex planet's zone
  zone_objects = galaxy.get_zones_at_global_hex(fleet.location)
  for zone_obj in zone_objects:
      if hasattr(zone_obj, 'planet_type') and zone_obj not in all_planets_at_hex:
          all_planets_at_hex = list(all_planets_at_hex) + [zone_obj]
  ```
- [ ] Write tests:
  - `test_validate_colonize_dyson_sphere_from_zone_hex`
  - `test_validate_colonize_dyson_sphere_from_center`
  - `test_validate_colonize_normal_planet_unchanged`
**Notes:**

#### Task 4.3: Update `strategy_colonization.py` for zone targeting [Medium]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/unit/ui/`
- [ ] In `on_colonize_click()` (around line 73-82): update planet lookup to include zone planets:
  - After checking `p.location == loc_local`, also check zone membership
  - Use galaxy's zone registry to find planets whose zone includes the fleet's hex
- [ ] Write test: `test_colonize_click_finds_dyson_sphere_via_zone`
**Notes:**

---

### Phase 5: Dyson Sphere Rendering [Medium]
**Objective:** Render Dyson Sphere with proper image at 11-hex diameter.
**Status:** Not Started

#### Task 5.1: Add Dyson Sphere image loading [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual visual test - launch game, create Dyson Sphere
- [ ] In `_draw_system_details()` (line 372): add special handling for Dyson Sphere planets:
  - Check `if planet.planet_type == PlanetType.DYSON_SPHERE and planet.diameter_hexes > 0:`
  - Load `Sphereworld_Portrait.png` from `assets/Images/Stellar Objects/Sphere world/`
  - Scale to `diameter_hexes * hex_size * camera.zoom` (same as star rendering pattern, line 351)
  - Render centered on planet's hex position
- [ ] Add Dyson Sphere image loading to asset manager or use `load_external_image()`
- [ ] Ensure image is rendered BEHIND smaller objects (draw order: Dyson sphere, then planets/warp points)
**Notes:** The existing `_draw_planet_sprite()` handles normal planets. Dyson Sphere needs a separate branch due to its massive size.

#### Task 5.2: Handle Dyson Sphere in planet rendering pipeline [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual visual test
- [ ] In `_draw_system_details()`: skip Dyson Sphere from normal planet hex groups (it renders separately)
- [ ] Or: render Dyson Sphere first in the planet loop, then overlay smaller planets
**Notes:**

---

### Phase 6: Integration & Verification [Simple]
**Objective:** Full integration testing, serialization round-trips, manual verification.
**Status:** Not Started

#### Task 6.1: Serialization round-trip tests [Medium]
**File:** New test file or extend `tests/unit/strategy/data/test_galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/`
- [ ] Test: Galaxy with star zones -> to_dict() -> from_dict() -> zone index rebuilt correctly
- [ ] Test: Galaxy with Dyson Sphere -> to_dict() -> from_dict() -> zone index rebuilt correctly
- [ ] Test: Planet with diameter_hexes -> to_dict() -> from_dict() -> diameter_hexes preserved
**Notes:**

#### Task 6.2: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite - all 11,906+ tests must pass
- [ ] Fix any regressions
**Notes:**

#### Task 6.3: Manual gameplay verification [Simple]
**Tests:** Manual
- [ ] Launch game, navigate to a star system with a large star
- [ ] Click on hexes around the star - verify star is selected from zone hexes
- [ ] Create Dyson Sphere (if possible in test scenario)
- [ ] Verify Dyson Sphere image renders at correct scale
- [ ] Verify clicking any hex in Dyson zone selects it
- [ ] Verify colonization from a zone hex works
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - 11,906 passed (2026-02-13)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No new warnings introduced

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon)
- [ ] Manual: Click star zone hex -> star selected
- [ ] Manual: Click Dyson Sphere zone hex -> Dyson selected
- [ ] Manual: Colonize Dyson Sphere from non-center hex
- [ ] Manual: Dyson Sphere renders with Sphereworld_Portrait.png at 11-hex scale

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
