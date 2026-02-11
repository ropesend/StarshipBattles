# Phase 6: Order Processing (Turn Execution)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Implement the actual game effects when superweapon orders execute during turn processing.

---

## Tasks

### Task 6.1: Create SuperweaponOrderProcessor [Complex]
**New File:** `game/strategy/engine/superweapon_order_processor.py`
**Pattern:** Follow `game/strategy/engine/fleet_order_processor.py` (process_colonize at line 158)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [ ] Create `SuperweaponOrderProcessor` class

- [ ] `process_implode_planet(self, fleet, empire, galaxy, component_registry=None)`:
  - Get target planet from fleet's current order
  - Find ship with DestroyPlanet ability via `SuperweaponValidator.find_ship_with_ability()`
  - Remove planet from system.planets list
  - Call `galaxy.unregister_planet(planet)` to clean indexes
  - If planet has `owner_id`, find owning empire and remove from colonies
  - Remove the ship carrying the Planet Imploder from fleet
  - If fleet empty, flag for removal
  - `log_event(EventType.PLANET_DESTROYED, category=EventCategory.SUPERWEAPONS, ...)`
  - Return result dataclass indicating if fleet was consumed

- [ ] `process_stellerate_star(self, fleet, empire, galaxy, empires, component_registry=None)`:
  - Find star system at fleet location
  - Collect ALL planets in system -> unregister each, remove from empire colonies
  - Collect ALL fleets in system from ALL empires (including actor): `galaxy.get_all_fleets_in_system(system, empires)`
  - Remove each fleet from its owning empire, unregister from galaxy
  - Remove all stars: `system.stars = []`
  - Keep warp points intact
  - `log_event(EventType.STAR_DESTROYED, ...)`
  - Return True (fleet always consumed - suicide weapon)

- [ ] `process_open_warp_point(self, fleet, empire, galaxy, component_registry=None)`:
  - Get order target dict: `{'target_hex': HexCoord, 'target_system_name': str}`
  - Find current system and target system
  - Near-end warp point: create `WarpPoint(destination_id=target_system_name, location=fleet_local_hex)`
  - Far-end: calculate direction vector from target system to current system
    - Normalize direction, multiply by typical orbit distance (4-8 hexes from star)
    - Create `WarpPoint(destination_id=current_system_name, location=calculated_hex)`
  - Add warp points to both systems
  - Remove ship with OpenWarpPoint ability from fleet
  - `log_event(EventType.WARP_POINT_OPENED, ...)`

- [ ] `process_close_warp_point(self, fleet, empire, galaxy, component_registry=None)`:
  - Get warp_point_destination_id from order target
  - Find current system at fleet location
  - Find the warp point in current system matching destination_id
  - Call `galaxy.remove_warp_link(current_system.name, destination_id)`
  - Remove ship with CloseWarpPoint ability from fleet
  - `log_event(EventType.WARP_POINT_CLOSED, ...)`

- [ ] `process_create_dyson_sphere(self, fleet, empire, galaxy, component_registry=None)`:
  - Find star system at fleet location
  - Calculate which planets are within 9 hexes of primary star
    - Use hex distance: `abs(p.location.q - star.location.q) + abs(p.location.r - star.location.r)` or proper hex_distance
  - Remove qualifying planets (unregister each, remove from empire colonies)
  - Remove star(s): `system.stars = []`
  - Create Dyson Sphere planet:
    ```python
    dyson = Planet(
        name=f"Dyson Sphere ({system.name})",
        location=HexCoord(0, 0),  # System center
        orbit_distance=0,
        planet_type=PlanetType.DYSON_SPHERE,
        image_id="Sphereworld_Portrait.png",
        # Set very high surface_area for massive population capacity
        surface_area=1e16,  # ~20x Earth surface area
        mass=2e30,  # ~1 solar mass
        radius=1.5e11,  # ~1 AU
        # Other fields: reasonable defaults for artificial world
    )
    ```
  - Add to system.planets
  - Register with galaxy: `galaxy.register_planet(system, dyson)`
  - Remove ship with CreateDysonSphere ability
  - `log_event(EventType.DYSON_SPHERE_CREATED, ...)`

- [ ] `process_self_destruct(self, fleet, empire, galaxy)`:
  - Get ship ID list from order target
  - For each ship_id, find ship in fleet.ships
  - Remove each matching ship from fleet via `fleet.remove_ship(ship)`
  - If fleet now empty, flag for removal
  - `log_event(EventType.SHIPS_SELF_DESTRUCTED, ...)`

**Notes:**

### Task 6.2: Integrate into FleetOrderProcessor [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py` (process_end_turn_orders at line 474)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [ ] Add optional `empires` parameter to `process_end_turn_orders()` signature:
  ```python
  def process_end_turn_orders(self, fleet, empire, galaxy, component_registry=None, empires=None):
  ```

- [ ] Add order type routing in `process_end_turn_orders()` (after TRANSFER case):
  ```python
  elif order.type in (OrderType.IMPLODE_PLANET, OrderType.STELLERATE_STAR,
                      OrderType.OPEN_WARP_POINT, OrderType.CLOSE_WARP_POINT,
                      OrderType.CREATE_DYSON_SPHERE):
      from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
      proc = SuperweaponOrderProcessor()
      # Dispatch to appropriate method
      ...
  ```

- [ ] Route each order type to the correct processor method
- [ ] Pass `empires` to `process_stellerate_star()` (needed for destroying all ships)
- [ ] Return True if fleet was consumed, False otherwise

- [ ] Handle SELF_DESTRUCT separately: it should execute at START of turn, not end
  - Add `process_self_destruct_orders(empires)` method that runs before movement
  - Or: add to process_end_turn_orders but with a comment noting timing difference
  - **Decision needed during implementation**: simplest approach that matches spec

- [ ] Update TurnEngine to pass `empires` when calling `process_end_turn_orders()`
  - Find the call site in turn engine and add the parameter

**Notes:**

### Task 6.3: Write Phase 6 Unit Tests [Complex]
**New File:** `tests/unit/strategy/engine/test_superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py -v`

- [ ] Test `process_implode_planet()`:
  - Planet removed from system.planets
  - Planet removed from galaxy indexes (planets_by_id)
  - Ship carrying DestroyPlanet ability removed from fleet
  - PLANET_DESTROYED event logged

- [ ] Test `process_stellerate_star()`:
  - All stars removed (system.stars = [])
  - All planets removed and unregistered
  - ALL fleets in system destroyed (including actor - suicide)
  - Warp points preserved
  - STAR_DESTROYED event logged

- [ ] Test `process_open_warp_point()`:
  - Near-end warp point created in current system
  - Far-end warp point created in target system
  - Both point to each other (destination_ids match)
  - Ship consumed
  - WARP_POINT_OPENED event logged

- [ ] Test `process_close_warp_point()`:
  - Both ends of warp link removed
  - Ship consumed
  - WARP_POINT_CLOSED event logged

- [ ] Test `process_create_dyson_sphere()`:
  - Star removed
  - Planets within 9 hexes removed
  - Planets beyond 9 hexes preserved
  - New DYSON_SPHERE planet created at system center
  - Dyson Sphere is colonizable (owner_id=None)
  - Ship consumed
  - DYSON_SPHERE_CREATED event logged

- [ ] Test `process_self_destruct()`:
  - Specified ships removed from fleet
  - Other ships in fleet preserved
  - Fleet removed from empire if empty
  - SHIPS_SELF_DESTRUCTED event logged

- [ ] Test component consumption pattern: ship removed, fleet not removed if other ships remain

- [ ] Verify: all tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
