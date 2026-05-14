"""
Unit tests for colonization population transfer (PROJ-68 Phase 7).

Tests that:
- Passengers from fleet cargo transfer to colony as founding population
- No passengers seeds minimum population if empire has race_config
- No race_config means no population seeded
- Ship passengers are unloaded during transfer

PROJ-211: Updated to use ship_factory fixture for DI compliance.
"""

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_processor import OrderProcessor, ColonizeResult
from game.core.registry import GameRegistries


def _make_planet(location: HexCoord, name: str = "Test Planet") -> Planet:
    """Create a test planet at location."""
    return Planet(
        name=name,
        location=location,
        orbit_distance=1,
        mass=5.97e24,
        radius=6.37e6,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.8,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )


def _make_ship_with_cargo(
    name: str,
    cargo_capacity: int = 100,
    current_cargo: int = 0,
    registries: GameRegistries = None,
) -> ShipInstance:
    """Create a ship with passenger cargo capacity and a drop pod.

    Phase 3: Drop pod is a carried item, not cargo.
    """
    design = {
        "name": name,
        "hull_id": "test_hull",
        "layers": {
            "internal": [
                {
                    "id": "passenger_quarters",
                    "abilities": {"CargoStorage": {"cargo_type": "passengers", "capacity": cargo_capacity}}
                }
            ]
        }
    }
    ship = ShipInstance.create(design, owner_id=0, name=name, registries=registries)
    # Load drop pod as carried item
    ship.carried_items.append({
        "vehicle_type": "drop_pod",
        "design_id": "continental_drop_pod",
        "name": "Drop Pod (Continental)",
        "design_data": {"layers": {"CORE": []}},
        "mass": 500,
    })
    # Load passengers if specified
    if current_cargo > 0:
        ship.cargo_contents["passengers"] = current_cargo
    return ship


def _make_ship_with_colony_pod(
    name: str,
    planet_type: str = "continental",
    registries: GameRegistries = None,
) -> ShipInstance:
    """Create a ship with a drop pod in carried_items (no passenger capacity).

    Phase 3: Drop pod is a carried item.
    """
    design = {
        "name": name,
        "hull_id": "test_hull",
        "layers": {
            "internal": []
        }
    }
    ship = ShipInstance.create(design, owner_id=0, name=name, registries=registries)
    # Load drop pod as carried item
    ship.carried_items.append({
        "vehicle_type": "drop_pod",
        "design_id": f"{planet_type}_drop_pod",
        "name": f"Drop Pod ({planet_type})",
        "design_data": {"layers": {"CORE": []}},
        "mass": 500,
    })
    return ship


def _make_component_registry() -> dict:
    """Create component registry with colony pod definitions for CONTINENTAL planets."""
    return {
        "colony_pod": {
            "id": "colony_pod",
            "abilities": {"ColonizePlanet": "CONTINENTAL"}
        },
        "passenger_quarters": {
            "id": "passenger_quarters",
            "abilities": {"CargoStorage": {"cargo_type": "passengers", "capacity": 100}}
        },
    }


class MockGalaxy:
    """Mock galaxy for processor tests."""
    def __init__(self, planets: list):
        self._planets = {p.id: p for p in planets if p.id >= 0}
        self._planets_by_loc = {}
        for p in planets:
            self._planets_by_loc.setdefault(p.location, []).append(p)

    def get_planet_by_id(self, planet_id: int):
        return self._planets.get(planet_id)

    def get_planets_at_global_hex(self, location: HexCoord):
        return self._planets_by_loc.get(location, [])

    def get_zones_at_global_hex(self, location: HexCoord):
        """Return zone objects at location (empty for these tests)."""
        return []


class MockRaceConfig:
    """Mock race config with just race_id."""
    def __init__(self, race_id: str = "humans"):
        self.race_id = race_id


class TestColonizeDoesNotTransfer:
    """Colonization claims planet and deploys pod only — no population/cargo transfer."""

    def test_colonize_does_not_transfer_passengers(self, fresh_registries):
        """Passengers stay on fleet — transfer happens via separate TRANSFER orders."""
        # Setup
        location = HexCoord(0, 0)
        planet = _make_planet(location)
        planet.id = 1
        galaxy = MockGalaxy([planet])

        # Empire with race config
        empire = Empire(0, "Test Empire", (100, 100, 100))
        empire.race_config = MockRaceConfig("humans")

        # Fleet with passengers
        fleet = Fleet(1, empire.id, location)
        ship = _make_ship_with_cargo("Colony Ship", cargo_capacity=100, current_cargo=50, registries=fresh_registries)
        fleet.ships.append(ship)
        fleet.add_order(Order(OrderType.COLONIZE, target=planet))
        empire.add_fleet(fleet)

        # Process colonization
        processor = OrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=_make_component_registry()
        )

        # Verify planet claimed
        assert result.colonized is True
        assert planet.owner_id == empire.id

        # Colony should have NO population (transferred via separate TRANSFER orders)
        assert len(planet.populations) == 0

    def test_colonize_keeps_passengers_on_fleet(self, fresh_registries):
        """Ship cargo stays intact during colonization — no auto-transfer."""
        location = HexCoord(0, 0)
        planet = _make_planet(location)
        planet.id = 1
        galaxy = MockGalaxy([planet])

        empire = Empire(0, "Test Empire", (100, 100, 100))
        empire.race_config = MockRaceConfig("humans")

        fleet = Fleet(1, empire.id, location)
        ship = _make_ship_with_cargo("Colony Ship", cargo_capacity=100, current_cargo=75, registries=fresh_registries)
        fleet.ships.append(ship)
        fleet.add_order(Order(OrderType.COLONIZE, target=planet))
        empire.add_fleet(fleet)

        assert fleet.resources.get_fleet_cargo_current("passengers") == 75

        processor = OrderProcessor()
        processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=_make_component_registry()
        )

        # Passengers remain on fleet, planet has no population
        assert planet.total_population == 0
        assert fleet.resources.get_fleet_cargo_current("passengers") == 75


class TestColonizeWithoutPassengers:
    """Test colonization when no passengers on board."""

    # NOTE: test_colonize_without_passengers_seeds_minimum was removed because
    # the auto-seeding feature was intentionally disabled per user request.
    # See order_processor.py:545-547 for the commented-out code.

    def test_colonize_no_race_config_no_population(self, fresh_registries):
        """No race_config means no population is seeded."""
        location = HexCoord(0, 0)
        planet = _make_planet(location)
        planet.id = 1
        galaxy = MockGalaxy([planet])

        empire = Empire(0, "Test Empire", (100, 100, 100))
        # No race_config set

        fleet = Fleet(1, empire.id, location)
        ship = _make_ship_with_colony_pod("Colony Ship", registries=fresh_registries)
        fleet.ships.append(ship)
        fleet.add_order(Order(OrderType.COLONIZE, target=planet))
        empire.add_fleet(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=_make_component_registry()
        )

        assert result.colonized is True
        assert planet.owner_id == empire.id
        # No population seeded
        assert len(planet.populations) == 0


class TestColonizeMultipleShips:
    """Test colonization with multiple ships — passengers stay on fleet."""

    def test_colonize_does_not_auto_transfer_passengers(self, fresh_registries):
        """Colonization claims planet but does not move passengers."""
        location = HexCoord(0, 0)
        planet = _make_planet(location)
        planet.id = 1
        galaxy = MockGalaxy([planet])

        empire = Empire(0, "Test Empire", (100, 100, 100))
        empire.race_config = MockRaceConfig("humans")

        fleet = Fleet(1, empire.id, location)
        ship1 = _make_ship_with_cargo("Transport 1", cargo_capacity=100, current_cargo=30, registries=fresh_registries)
        ship2 = _make_ship_with_cargo("Transport 2", cargo_capacity=100, current_cargo=45, registries=fresh_registries)
        ship3 = _make_ship_with_colony_pod("Colony Ship", registries=fresh_registries)
        fleet.ships.extend([ship1, ship2, ship3])
        fleet.add_order(Order(OrderType.COLONIZE, target=planet))
        empire.add_fleet(fleet)

        assert fleet.resources.get_fleet_cargo_current("passengers") == 75

        processor = OrderProcessor()
        processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=_make_component_registry()
        )

        # Planet claimed but no population transferred
        assert planet.owner_id == empire.id
        assert planet.total_population == 0
        assert fleet.resources.get_fleet_cargo_current("passengers") == 75


class TestExistingColonizationBehavior:
    """Verify existing colonization functionality still works."""

    def test_colonize_still_assigns_ownership(self, fresh_registries):
        """Basic colonization still assigns planet ownership."""
        location = HexCoord(0, 0)
        planet = _make_planet(location)
        planet.id = 1
        galaxy = MockGalaxy([planet])

        empire = Empire(0, "Test Empire", (100, 100, 100))

        fleet = Fleet(1, empire.id, location)
        ship = _make_ship_with_colony_pod("Colony Ship", registries=fresh_registries)
        fleet.ships.append(ship)
        fleet.add_order(Order(OrderType.COLONIZE, target=planet))
        empire.add_fleet(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=_make_component_registry()
        )

        assert result.colonized is True
        assert result.planet_name == "Test Planet"
        assert planet.owner_id == empire.id
        assert planet in empire.colonies

    def test_colonize_ship_stays_in_fleet(self, fresh_registries):
        """Phase 2: Colony ship stays in fleet after colonization (reusable)."""
        location = HexCoord(0, 0)
        planet = _make_planet(location)
        planet.id = 1
        galaxy = MockGalaxy([planet])

        empire = Empire(0, "Test Empire", (100, 100, 100))

        fleet = Fleet(1, empire.id, location)
        colony_ship = _make_ship_with_colony_pod("Colony Ship", registries=fresh_registries)
        escort = ShipInstance.create({
            "name": "Escort",
            "hull_id": "small_hull",
            "layers": {}
        }, owner_id=0, name="Escort", registries=fresh_registries)
        fleet.ships.extend([colony_ship, escort])
        fleet.add_order(Order(OrderType.COLONIZE, target=planet))
        empire.add_fleet(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        # Phase 3: Both ships stay in fleet
        assert fleet in empire.fleets
        assert len(fleet.ships) == 2
        # Drop pod consumed from carried_items
        drop_pods = [i for i in colony_ship.carried_items if i.get("vehicle_type") == "drop_pod"]
        assert len(drop_pods) == 0
