# Phase 3: Extract Spawning to `production_spawner.py`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move ~265 lines of spawn logic to a new sibling module, reducing `production_engine.py` by the largest single chunk.

---

## Tasks

### Task 3.1: Create `ProductionSpawner` class [Medium]
**File:** `game/strategy/engine/production_spawner.py` (new, ~250 lines)
**Tests:** `pytest tests/unit/strategy/production_engine/test_spawning.py -v` (will fail until Task 3.3)

- [ ] Create `game/strategy/engine/production_spawner.py`
- [ ] Add imports: `logging`, `uuid`, `typing`, `log_event`, `EventType`, `EventCategory`, `Fleet`, `PlanetaryFacility`, `ShipInstance`, `DesignLibrary`
- [ ] Create `ProductionSpawner` class with `__init__(self, registries=None)`
- [ ] Move `_load_design(self, design_id, empire, save_path)` from production_engine.py (lines 594-613)
- [ ] Move `_load_and_create_ship(self, design_id, empire, save_path)` from production_engine.py (lines 673-711)
- [ ] Move `_create_and_place_facility(self, planet, design_id, empire, save_path, galaxy, log_prefix)` from production_engine.py (lines 615-671)
- [ ] Move `_spawn_ship(self, planet, design_id, empire, galaxy, save_path)` from production_engine.py (lines 726-778)
- [ ] Move `_spawn_fleet_ship(self, fleet, design_id, empire, save_path)` from production_engine.py (lines 780-816)
- [ ] Move `_spawn_fleet_complex(self, fleet, design_id, empire, galaxy, save_path, target_planet_id)` from production_engine.py (lines 818-864)
- [ ] Do NOT move `_spawn_complex` (lines 713-724) — it's a trivial wrapper; inline its single call site
- [ ] Extract shared `_resolve_planet_location(self, planet, galaxy)` helper method:
  ```python
  def _resolve_planet_location(self, planet, galaxy):
      """Resolve event logging location info for a planet.

      Returns:
          Tuple of (location_hex, system_name, local_hex) where each may be None/empty.
      """
      location_hex = None
      system_name = ""
      local_hex = None
      if galaxy:
          parent_sys = galaxy.get_system_of_planet(planet)
          if parent_sys:
              system_name = parent_sys.name
              if hasattr(planet, 'location') and planet.location is not None:
                  loc = parent_sys.global_location + planet.location
                  location_hex = [loc.q, loc.r]
                  local_hex = [planet.location.q, planet.location.r]
      return location_hex, system_name, local_hex
  ```
- [ ] Update `_create_and_place_facility` to use `_resolve_planet_location` (replaces lines 646-657)
- [ ] Update `_spawn_ship` to use `_resolve_planet_location` (replaces lines 748-757). Note: `_spawn_ship` also computes `spawn_loc` for fleet creation — keep that, but reuse the helper for event logging fields.
- [ ] Add `spawn_completed_item(self, item, empire, colony_or_fleet, galaxy, save_path, tick)` public dispatch:
  ```python
  def spawn_completed_item(self, item, empire, colony_or_fleet, galaxy, save_path, tick):
      """Dispatch to appropriate spawn method based on item type and context."""
      design_id = item['design_id']
      vehicle_type = item.get('type', 'ship')

      if isinstance(colony_or_fleet, Fleet):
          if vehicle_type == 'complex':
              target_planet_id = item.get('target_planet_id')
              self._spawn_fleet_complex(colony_or_fleet, design_id, empire, galaxy, save_path, target_planet_id=target_planet_id)
          else:
              self._spawn_fleet_ship(colony_or_fleet, design_id, empire, save_path)
      else:
          if vehicle_type == 'complex':
              self._create_and_place_facility(colony_or_fleet, design_id, empire, save_path, galaxy)
          else:
              self._spawn_ship(colony_or_fleet, design_id, empire, galaxy, save_path)
  ```
- [ ] Verify: File is ~250 lines and self-contained

**Notes:**

### Task 3.2: Wire ProductionEngine to ProductionSpawner [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ -v` (will fail until Task 3.3)

- [ ] Add import at top of file: `from game.strategy.engine.production_spawner import ProductionSpawner`
- [ ] Update `__init__` to create spawner: `self._spawner = ProductionSpawner(registries=registries)`
- [ ] Simplify `_complete_item()` (lines 560-592) to:
  ```python
  def _complete_item(self, queue, item, empire, colony_or_fleet, galaxy, save_path, tick):
      """Handle completion of a construction item."""
      design_id = item['design_id']
      vehicle_type = item.get('type', 'ship')
      queue.pop(0)
      logger.info(f"Production Complete (tick {tick}): {design_id} ({vehicle_type})")
      self._spawner.spawn_completed_item(item, empire, colony_or_fleet, galaxy, save_path, tick)
  ```
- [ ] Remove all spawn methods from production_engine.py:
  - Delete `_load_design` (lines 594-613)
  - Delete `_create_and_place_facility` (lines 615-671)
  - Delete `_load_and_create_ship` (lines 673-711)
  - Delete `_spawn_complex` (lines 713-724)
  - Delete `_spawn_ship` (lines 726-778)
  - Delete `_spawn_fleet_ship` (lines 780-816)
  - Delete `_spawn_fleet_complex` (lines 818-864)
- [ ] Remove now-unused imports: `uuid`, `Fleet` (line 48), `PlanetaryFacility` (line 50), `ShipInstance` (line 51), `DesignLibrary` (line 52)
  - Note: Keep `OrderType` import (line 49) if still used elsewhere in the file; check before removing
- [ ] Verify: `production_engine.py` is now ~600 lines

**Notes:**

### Task 3.3: Update tests for new module path [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/production/ -v`

#### 3.3a: Update `test_spawning.py` [Simple]
**File:** `tests/unit/strategy/production_engine/test_spawning.py`

- [ ] Update all `patch('game.strategy.engine.production_engine.DesignLibrary')` → `patch('game.strategy.engine.production_spawner.DesignLibrary')`
- [ ] Update all `patch('game.strategy.engine.production_engine.ShipInstance')` → `patch('game.strategy.engine.production_spawner.ShipInstance')`
- [ ] Update all `patch('game.strategy.engine.production_engine.Fleet')` → `patch('game.strategy.engine.production_spawner.Fleet')`
- [ ] Update all `patch('game.strategy.engine.production_engine.logger')` → `patch('game.strategy.engine.production_spawner.logger')` (only for spawn-related tests)
- [ ] Update `engine._spawn_ship(...)` → `engine._spawner._spawn_ship(...)` (3 occurrences in TestShipSpawning)
- [ ] Update `engine._spawn_complex(...)` → `engine._spawner._create_and_place_facility(...)` (2 occurrences in TestComplexSpawning)
  - Note: `_spawn_complex` was inlined; tests now call `_create_and_place_facility` directly
  - Adjust arguments if needed (add `galaxy=None` kwarg where `_spawn_complex` had it as positional)
- [ ] Run: `pytest tests/unit/strategy/production_engine/test_spawning.py -v` — all pass

#### 3.3b: Update `test_engine_event_emission.py` [Simple]
**File:** `tests/unit/strategy/test_engine_event_emission.py`

- [ ] Update all spawn-related patch targets from `game.strategy.engine.production_engine.*` → `game.strategy.engine.production_spawner.*`
- [ ] Update all `engine._spawn_ship(...)` → `engine._spawner._spawn_ship(...)` (6 occurrences)
- [ ] Update all `engine._spawn_fleet_ship(...)` → `engine._spawner._spawn_fleet_ship(...)` (2 occurrences)
- [ ] Update all `engine._spawn_complex(...)` → `engine._spawner._create_and_place_facility(...)` (3 occurrences)
  - Adjust arguments to match `_create_and_place_facility` signature
- [ ] Update all `engine._spawn_fleet_complex(...)` → `engine._spawner._spawn_fleet_complex(...)` (3 occurrences)
- [ ] Run: `pytest tests/unit/strategy/test_engine_event_emission.py -v` — all pass

#### 3.3c: Update `test_production_refactor.py` [Simple]
**File:** `tests/unit/strategy/engine/test_production_refactor.py`

- [ ] Update all `engine._spawn_ship = MagicMock()` → `engine._spawner._spawn_ship = MagicMock()` (6 occurrences at lines 120, 177, 206, 231, 259, 288)
- [ ] Update all `engine._spawn_ship.call_count` → `engine._spawner._spawn_ship.call_count` (6 occurrences at lines 131, 190, 215, 241, 269, 298)
- [ ] Run: `pytest tests/unit/strategy/engine/test_production_refactor.py -v` — all pass

- [ ] **Final**: Run `pytest tests/unit/strategy/ tests/integration/strategy/production/ -v` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
