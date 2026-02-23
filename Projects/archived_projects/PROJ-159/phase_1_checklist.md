# Phase 1: Create Test Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-159 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create reusable fixtures and helper functions for transfer validation tests

---

## Tasks

### Task 1.1: Create transfer test conftest [Simple]
**File:** `tests/integration/strategy/transfer/conftest.py` (NEW)
**Tests:** N/A - fixture file

- [x] Create directory `tests/integration/strategy/transfer/`
- [x] Create `conftest.py` with imports:
  ```python
  import pytest
  from game.strategy.data.planet import Planet, SpeciesPopulation
  from game.strategy.data.fleet import Fleet
  from game.strategy.data.ship_instance import ShipInstance
  from game.core.hex_math import HexCoord
  ```
- [x] Add `create_test_planet()` factory function:
  ```python
  def create_test_planet(
      name: str = "Test Colony",
      owner_id: int = 0,
      population_count: int = 1000,
      location: HexCoord = HexCoord(0, 0),
      species_id: str = "human"
  ) -> Planet:
      """Create a minimal Planet for integration tests."""
      return Planet(
          name=name,
          location=location,
          orbit_distance=1,
          mass=5.972e24,
          radius=6.371e6,
          surface_area=5.1e14,
          density=5514.0,
          surface_gravity=9.81,
          surface_pressure=101325.0,
          surface_temperature=288.0,
          surface_water=0.71,
          tectonic_activity=0.3,
          magnetic_field=1.0,
          owner_id=owner_id,
          populations=[SpeciesPopulation(race_id=species_id, count=population_count)]
      )
  ```
- [x] Add `create_transport_ship()` factory:
  ```python
  def create_transport_ship(
      name: str = "Transport-1",
      owner_id: int = 0,
      cargo_capacity: int = 100,
      current_cargo: int = 0
  ) -> ShipInstance:
      """Create a ship with passenger cargo capacity."""
      design = {
          "name": name,
          "hull_id": "test_hull",
          "layers": {
              "internal": [{
                  "id": "passenger_quarters",
                  "abilities": {"CargoStorage": {"cargo_type": "passengers", "capacity": cargo_capacity}}
              }]
          }
      }
      ship = ShipInstance.create(design, owner_id=owner_id, name=name)
      if current_cargo > 0:
          ship.cargo_contents["passengers"] = current_cargo
      return ship
  ```
- [x] Add `create_transport_fleet()`:
  ```python
  def create_transport_fleet(
      fleet_id: int = 1,
      owner_id: int = 0,
      location: HexCoord = HexCoord(0, 0),
      cargo_capacity: int = 100,
      current_cargo: int = 0
  ) -> Fleet:
      """Create a fleet with a transport ship."""
      fleet = Fleet(fleet_id, owner_id, location)
      ship = create_transport_ship(
          name=f"Transport-{fleet_id}",
          owner_id=owner_id,
          cargo_capacity=cargo_capacity,
          current_cargo=current_cargo
      )
      fleet.add_ship(ship)
      return fleet
  ```
- [x] Add `MockGalaxy` class:
  ```python
  class MockGalaxy:
      """Minimal galaxy for transfer validation tests."""
      def __init__(self):
          self.systems = {}

      def add_system(self, system):
          self.systems[system.global_location] = system

      def get_system_at_location(self, location: HexCoord):
          return self.systems.get(location)
  ```
- [x] Add `MockSystem` class:
  ```python
  class MockSystem:
      def __init__(self, global_location: HexCoord, planets: list):
          self.global_location = global_location
          self.planets = planets
  ```
- [x] Verify: Imports work without errors

**Notes:** Created conftest.py with all factories and fixtures in a single pass.

---

### Task 1.2: Add pytest fixtures [Simple]
**File:** `tests/integration/strategy/transfer/conftest.py`
**Tests:** N/A - fixture file

- [x] Add `colonized_planet` fixture:
  ```python
  @pytest.fixture
  def colonized_planet() -> Planet:
      """A colonized planet with population."""
      return create_test_planet(name="Alpha Colony", owner_id=0, population_count=1000)
  ```
- [x] Add `uncolonized_planet` fixture:
  ```python
  @pytest.fixture
  def uncolonized_planet() -> Planet:
      """An uncolonized planet."""
      return create_test_planet(name="Beta", owner_id=None, population_count=0)
  ```
- [x] Add `transport_fleet` fixture:
  ```python
  @pytest.fixture
  def transport_fleet() -> Fleet:
      """Fleet with empty transport capacity."""
      return create_transport_fleet(cargo_capacity=100, current_cargo=0)
  ```
- [x] Add `loaded_fleet` fixture:
  ```python
  @pytest.fixture
  def loaded_fleet() -> Fleet:
      """Fleet with passengers loaded."""
      return create_transport_fleet(cargo_capacity=100, current_cargo=50)
  ```
- [x] Add `mock_galaxy` fixture:
  ```python
  @pytest.fixture
  def mock_galaxy(colonized_planet) -> MockGalaxy:
      """Galaxy with planet at origin system."""
      galaxy = MockGalaxy()
      system = MockSystem(HexCoord(0, 0), [colonized_planet])
      galaxy.add_system(system)
      return galaxy
  ```
- [x] Verify: `pytest tests/integration/strategy/transfer/ --collect-only` shows fixtures

**Notes:** Combined with Task 1.1. All fixtures added to conftest.py.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `tests/integration/strategy/transfer/conftest.py` exists with all fixtures
- [ ] `pytest tests/integration/strategy/transfer/ --collect-only` runs without errors
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
