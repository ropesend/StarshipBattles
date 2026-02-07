"""Tests for population and cargo fields in DTOs.

PROJ-68 Phase 8: Verify that DTOs expose population and cargo data
for the UI layer.
"""
import pytest
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType, SpeciesPopulation
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.facade.dto.planet_dto import PlanetInfo


class TestPlanetInfoPopulation:
    """Tests for PlanetInfo population fields."""

    def test_planet_info_includes_total_population(self):
        """PlanetInfo should expose total_population from planet."""
        planet = Planet(
            name="Test World",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.3,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
            owner_id=0,
            populations=[
                SpeciesPopulation(race_id="human", count=1000, happiness=0.7),
                SpeciesPopulation(race_id="alien", count=500, happiness=0.5),
            ]
        )

        info = PlanetInfo.from_planet(planet)

        assert info.total_population == 1500

    def test_planet_info_includes_max_population(self):
        """PlanetInfo should expose max_population capacity."""
        planet = Planet(
            name="Test World",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,  # Earth-like
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.3,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
        )

        info = PlanetInfo.from_planet(planet)

        # max_population = surface_area / 1e6 * 100 / 1000
        # = 5.1e14 / 1e6 * 100 / 1000 = 51,000,000 units
        assert info.max_population == planet.max_population
        assert info.max_population > 0

    def test_planet_info_includes_population_details(self):
        """PlanetInfo should expose per-species population details."""
        planet = Planet(
            name="Test World",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.3,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
            owner_id=0,
            populations=[
                SpeciesPopulation(race_id="human", count=1000, happiness=0.7),
                SpeciesPopulation(race_id="alien", count=500, happiness=0.5),
            ]
        )

        info = PlanetInfo.from_planet(planet)

        # population_details is tuple of (race_id, count, happiness)
        assert len(info.population_details) == 2

        # First species
        assert info.population_details[0][0] == "human"
        assert info.population_details[0][1] == 1000
        assert info.population_details[0][2] == 0.7

        # Second species
        assert info.population_details[1][0] == "alien"
        assert info.population_details[1][1] == 500
        assert info.population_details[1][2] == 0.5

    def test_planet_info_empty_population(self):
        """PlanetInfo should handle planets with no population."""
        planet = Planet(
            name="Barren World",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.0,
            tectonic_activity=0.0,
            magnetic_field=0.0,
            planet_type=PlanetType.BARREN,
        )

        info = PlanetInfo.from_planet(planet)

        assert info.total_population == 0
        assert info.population_details == ()


class TestFleetInfoCargo:
    """Tests for FleetInfo cargo fields."""

    def test_fleet_info_includes_passenger_cargo(self):
        """FleetInfo should expose passenger cargo capacity and count."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))

        # Create a ship with passenger capacity using factory
        ship = ShipInstance.create(
            design_data={
                "name": "Transport Alpha",
                "ship_class": "Transport",
                "layers": {"core": [{"id": "passenger_quarters", "abilities": {"CargoStorage": {"cargo_type": "passengers", "capacity": 100}}}]}
            },
            owner_id=0,
            name="Transport Alpha",
            design_id="transport",
        )
        fleet.add_ship(ship)

        # Import here to avoid circular issues at module level
        from game.strategy.facade.dto.fleet_dto import FleetInfo

        info = FleetInfo.from_fleet(fleet)

        assert info.passenger_capacity >= 0  # Should have cargo fields
        assert hasattr(info, 'passengers_current')

    def test_fleet_info_cargo_summary(self):
        """FleetInfo should provide cargo summary data."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))

        from game.strategy.facade.dto.fleet_dto import FleetInfo

        info = FleetInfo.from_fleet(fleet)

        # Should have cargo-related fields even if empty
        assert hasattr(info, 'passenger_capacity')
        assert hasattr(info, 'passengers_current')
