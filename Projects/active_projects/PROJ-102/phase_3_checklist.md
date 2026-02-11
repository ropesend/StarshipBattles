# Phase 3: Data Model Extensions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add PlanetType.DYSON_SPHERE, Galaxy cleanup methods, and new event types.

---

## Tasks

### Task 3.1: Add PlanetType.DYSON_SPHERE [Simple]
**File:** `game/strategy/data/planet.py` (PlanetType enum)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_cleanup.py`

- [ ] Add `DYSON_SPHERE = auto()` to PlanetType enum (after the last existing value)

**Notes:**

### Task 3.2: Add Galaxy Cleanup Methods [Medium]
**File:** `game/strategy/data/galaxy.py` (Galaxy class)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_cleanup.py`

- [ ] Add `Galaxy.unregister_planet(self, planet)`:
  - Remove from `self.planets_by_id` (by planet.id)
  - Remove from `self._planet_to_system` (by planet object)
  - Remove from `self._global_hex_planets` (compute global hex from system location + planet.location)
  - Remove planet from the system's `planets` list
  - Handle missing keys gracefully (no KeyError)

- [ ] Add `Galaxy.remove_warp_link(self, system_a_name: str, system_b_name: str)`:
  - Find both systems via `self.name_map`
  - Remove warp points in system_a whose `destination_id == system_b_name`
  - Remove warp points in system_b whose `destination_id == system_a_name`
  - Handle missing systems gracefully

- [ ] Add `Galaxy.get_all_fleets_in_system(self, system, empires)`:
  - For STELLERATE_STAR: find all fleets from all empires at any hex within the system
  - System hexes = system.global_location + each star/planet/warp_point location
  - Also check system.global_location itself
  - Return list of (empire, fleet) tuples

**Notes:**

### Task 3.3: Add Event Types [Simple]
**File:** `game/strategy/events/event_types.py`
**Tests:** Existing event tests should still pass

- [ ] Add to EventType enum:
  ```python
  PLANET_DESTROYED = "planet_destroyed"
  STAR_DESTROYED = "star_destroyed"
  WARP_POINT_OPENED = "warp_point_opened"
  WARP_POINT_CLOSED = "warp_point_closed"
  DYSON_SPHERE_CREATED = "dyson_sphere_created"
  SHIPS_SELF_DESTRUCTED = "ships_self_destructed"
  ```
- [ ] Add to EventCategory enum:
  ```python
  SUPERWEAPONS = "superweapons"
  ```

**Notes:**

### Task 3.4: Dyson Sphere Image Registration [Simple]
**File:** `game/strategy/generation/planet_image_registry.py`
**Tests:** Manual verification

- [ ] Verify `assets/Images/Stellar Objects/Sphere world/Sphereworld_Portrait.png` exists
- [ ] In `PlanetImageRegistry._load_classifications()` or `__init__()`:
  - Add `self._type_to_images[PlanetType.DYSON_SPHERE] = ["Sphereworld_Portrait.png"]`
  - Ensure PlanetType import is available

**Notes:**

### Task 3.5: Write Phase 3 Unit Tests [Simple]
**New File:** `tests/unit/strategy/data/test_galaxy_cleanup.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_cleanup.py -v`

- [ ] Test `PlanetType.DYSON_SPHERE` exists in enum
- [ ] Test `Galaxy.unregister_planet()`:
  - Create galaxy with registered planet
  - Call unregister_planet()
  - Verify removed from `planets_by_id`, `_planet_to_system`, `_global_hex_planets`
  - Verify removed from system.planets list
- [ ] Test `Galaxy.remove_warp_link()`:
  - Create 2 systems with mutual warp points
  - Call remove_warp_link()
  - Verify warp points removed from both systems
- [ ] Test `Galaxy.get_all_fleets_in_system()`:
  - Create system with fleets from multiple empires
  - Verify all are found
- [ ] Verify: all tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
