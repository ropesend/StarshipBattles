"""Tests for Galaxy cleanup methods and PlanetType.DYSON_SPHERE.

PROJ-102 Phase 3 tests for data model extensions.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.star_system import StarSystem, WarpPoint
from tests.fixtures.galaxy_fixtures import make_galaxy_stub


class TestDysonSpherePlanetType:
    """Tests for PlanetType.DYSON_SPHERE enum value."""

    def test_dyson_sphere_exists_in_enum(self):
        """DYSON_SPHERE should be a valid PlanetType."""
        assert hasattr(PlanetType, 'DYSON_SPHERE')
        assert PlanetType.DYSON_SPHERE is not None

    def test_dyson_sphere_is_distinct_from_other_types(self):
        """DYSON_SPHERE should have a unique value."""
        all_types = list(PlanetType)
        dyson_value = PlanetType.DYSON_SPHERE.value
        other_values = [t.value for t in all_types if t != PlanetType.DYSON_SPHERE]
        assert dyson_value not in other_values

    def test_dyson_sphere_serialization(self):
        """DYSON_SPHERE should serialize/deserialize correctly."""
        # Create minimal planet with DYSON_SPHERE type
        planet = Planet(
            name="Sol Dyson Sphere",
            location=HexCoord(0, 0),
            orbit_distance=1,
            mass=1e30,
            radius=1.5e11,
            surface_area=2.83e23,
            density=0.001,
            surface_gravity=0.01,
            surface_pressure=0,
            surface_temperature=300,
            surface_water=0.0,
            tectonic_activity=0.0,
            magnetic_field=0.0,
            planet_type=PlanetType.DYSON_SPHERE
        )

        data = planet.to_dict()
        assert data['planet_type'] == 'DYSON_SPHERE'

        restored = Planet.from_dict(data)
        assert restored.planet_type == PlanetType.DYSON_SPHERE


class TestGalaxyUnregisterPlanet:
    """Tests for Galaxy.unregister_planet() method."""

    @pytest.fixture
    def galaxy_with_planet(self):
        """Create a galaxy with a registered planet."""
        galaxy = make_galaxy_stub()

        # Create system and planet
        system = StarSystem("TestSys", HexCoord(10, 20))
        planet = Planet(
            name="TestPlanet",
            location=HexCoord(2, 3),
            orbit_distance=1,
            mass=1e24,
            radius=6e6,
            surface_area=5e14,
            density=5000,
            surface_gravity=10,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.5,
            magnetic_field=1.0,
        )

        # Register manually (simulating galaxy.register_planet)
        planet.id = 1
        galaxy.state.next_planet_id = 2
        galaxy.planets_by_id[planet.id] = planet
        galaxy.state.planet_to_system[planet] = system
        global_hex = system.global_location + planet.location
        galaxy.state.global_hex_planets[global_hex] = [planet]
        system.planets.append(planet)
        galaxy.systems[system.global_location] = system
        galaxy.name_map[system.name] = system

        return galaxy, system, planet

    def test_unregister_planet_removes_from_planets_by_id(self, galaxy_with_planet):
        """Planet should be removed from planets_by_id dict."""
        galaxy, system, planet = galaxy_with_planet

        galaxy.unregister_planet(planet)

        assert planet.id not in galaxy.planets_by_id

    def test_unregister_planet_removes_from_planet_to_system(self, galaxy_with_planet):
        """Planet should be removed from _planet_to_system dict."""
        galaxy, system, planet = galaxy_with_planet

        galaxy.unregister_planet(planet)

        assert planet not in galaxy.state.planet_to_system

    def test_unregister_planet_removes_from_global_hex_planets(self, galaxy_with_planet):
        """Planet should be removed from _global_hex_planets dict."""
        galaxy, system, planet = galaxy_with_planet
        global_hex = system.global_location + planet.location

        galaxy.unregister_planet(planet)

        # Should either be empty list or key removed
        planets_at_hex = galaxy.state.global_hex_planets.get(global_hex, [])
        assert planet not in planets_at_hex

    def test_unregister_planet_removes_from_system_planets_list(self, galaxy_with_planet):
        """Planet should be removed from the system's planets list."""
        galaxy, system, planet = galaxy_with_planet

        galaxy.unregister_planet(planet)

        assert planet not in system.planets

    def test_unregister_planet_handles_missing_planet_gracefully(self, galaxy_with_planet):
        """Unregistering a non-existent planet should not raise errors."""
        galaxy, system, _ = galaxy_with_planet

        # Create an unregistered planet
        fake_planet = Planet(
            name="FakePlanet",
            location=HexCoord(5, 5),
            orbit_distance=2,
            mass=1e24, radius=6e6, surface_area=5e14, density=5000,
            surface_gravity=10, surface_pressure=0, surface_temperature=200,
            surface_water=0.0, tectonic_activity=0.0, magnetic_field=0.0,
        )
        fake_planet.id = 999

        # Should not raise
        galaxy.unregister_planet(fake_planet)


class TestGalaxyRemoveWarpLink:
    """Tests for Galaxy.remove_warp_link() method."""

    @pytest.fixture
    def galaxy_with_warp_link(self):
        """Create a galaxy with two systems linked by warp points."""
        galaxy = make_galaxy_stub()

        # Create two systems
        system_a = StarSystem("Alpha", HexCoord(0, 0))
        system_b = StarSystem("Beta", HexCoord(50, 50))

        # Add mutual warp points
        system_a.warp_points.append(WarpPoint("Beta", HexCoord(5, 0)))
        system_b.warp_points.append(WarpPoint("Alpha", HexCoord(-5, 0)))

        galaxy.systems[system_a.global_location] = system_a
        galaxy.systems[system_b.global_location] = system_b
        galaxy.name_map["Alpha"] = system_a
        galaxy.name_map["Beta"] = system_b

        return galaxy, system_a, system_b

    def test_remove_warp_link_removes_from_both_systems(self, galaxy_with_warp_link):
        """Warp points should be removed from both systems."""
        galaxy, system_a, system_b = galaxy_with_warp_link

        galaxy.remove_warp_link("Alpha", "Beta")

        # Check system_a has no warp point to Beta
        a_to_b = [wp for wp in system_a.warp_points if wp.destination_id == "Beta"]
        assert len(a_to_b) == 0

        # Check system_b has no warp point to Alpha
        b_to_a = [wp for wp in system_b.warp_points if wp.destination_id == "Alpha"]
        assert len(b_to_a) == 0

    def test_remove_warp_link_order_independent(self, galaxy_with_warp_link):
        """Should work regardless of argument order."""
        galaxy, system_a, system_b = galaxy_with_warp_link

        galaxy.remove_warp_link("Beta", "Alpha")  # Reversed order

        assert len(system_a.warp_points) == 0
        assert len(system_b.warp_points) == 0

    def test_remove_warp_link_handles_missing_system(self, galaxy_with_warp_link):
        """Should not raise if a system doesn't exist."""
        galaxy, _, _ = galaxy_with_warp_link

        # Should not raise
        galaxy.remove_warp_link("Alpha", "NonExistent")
        galaxy.remove_warp_link("NonExistent", "Beta")

    def test_remove_warp_link_preserves_other_warp_points(self, galaxy_with_warp_link):
        """Other warp points in the system should remain."""
        galaxy, system_a, system_b = galaxy_with_warp_link

        # Add a third system and link
        system_c = StarSystem("Gamma", HexCoord(100, 0))
        system_a.warp_points.append(WarpPoint("Gamma", HexCoord(0, 5)))
        system_c.warp_points.append(WarpPoint("Alpha", HexCoord(0, -5)))
        galaxy.systems[system_c.global_location] = system_c
        galaxy.name_map["Gamma"] = system_c

        # Remove Alpha-Beta link
        galaxy.remove_warp_link("Alpha", "Beta")

        # Alpha should still have warp to Gamma
        a_to_gamma = [wp for wp in system_a.warp_points if wp.destination_id == "Gamma"]
        assert len(a_to_gamma) == 1


class TestGalaxyGetAllFleetsInSystem:
    """Tests for Galaxy.get_all_fleets_in_system() method."""

    @pytest.fixture
    def galaxy_with_fleets(self):
        """Create a galaxy with a system and fleets from multiple empires."""
        galaxy = make_galaxy_stub()

        # Create a system at (10, 10)
        system = StarSystem("TestSys", HexCoord(10, 10))

        # Add a planet at local (2, 0)
        planet = MagicMock()
        planet.location = HexCoord(2, 0)
        planet.radius_hexes = 0  # PROJ-378: _spatial reads this; 0 = no extra occupied hexes
        system.planets.append(planet)

        # Add a warp point at local (-3, 0)
        wp = WarpPoint("OtherSys", HexCoord(-3, 0))
        system.warp_points.append(wp)

        galaxy.systems[system.global_location] = system
        galaxy.name_map[system.name] = system

        # Create mock empires with fleets
        empire1 = MagicMock()
        empire1.id = 1
        fleet1 = MagicMock()
        fleet1.id = 101
        fleet1.location = HexCoord(10, 10)  # At system center
        empire1.fleets = [fleet1]

        empire2 = MagicMock()
        empire2.id = 2
        fleet2 = MagicMock()
        fleet2.id = 102
        fleet2.location = HexCoord(12, 10)  # At planet (10,10) + (2,0)
        fleet3 = MagicMock()
        fleet3.id = 103
        fleet3.location = HexCoord(7, 10)   # At warp point (10,10) + (-3,0)
        empire2.fleets = [fleet2, fleet3]

        empires = [empire1, empire2]

        return galaxy, system, empires

    def test_get_all_fleets_at_system_center(self, galaxy_with_fleets):
        """Should find fleets at the system's global_location."""
        galaxy, system, empires = galaxy_with_fleets

        result = galaxy.get_all_fleets_in_system(system, empires)

        # Fleet at (10, 10) = system center
        fleet_ids = [f.id for _, f in result]
        assert 101 in fleet_ids

    def test_get_all_fleets_at_planet_locations(self, galaxy_with_fleets):
        """Should find fleets at planet locations within system."""
        galaxy, system, empires = galaxy_with_fleets

        result = galaxy.get_all_fleets_in_system(system, empires)

        # Fleet at (12, 10) = system (10,10) + planet (2,0)
        fleet_ids = [f.id for _, f in result]
        assert 102 in fleet_ids

    def test_get_all_fleets_at_warp_point_locations(self, galaxy_with_fleets):
        """Should find fleets at warp point locations within system."""
        galaxy, system, empires = galaxy_with_fleets

        result = galaxy.get_all_fleets_in_system(system, empires)

        # Fleet at (7, 10) = system (10,10) + warp (-3,0)
        fleet_ids = [f.id for _, f in result]
        assert 103 in fleet_ids

    def test_get_all_fleets_returns_empire_fleet_tuples(self, galaxy_with_fleets):
        """Should return (empire, fleet) tuples."""
        galaxy, system, empires = galaxy_with_fleets

        result = galaxy.get_all_fleets_in_system(system, empires)

        # Should be list of tuples
        assert all(isinstance(item, tuple) for item in result)
        assert all(len(item) == 2 for item in result)

        # Check empire-fleet association
        for empire, fleet in result:
            assert fleet in empire.fleets

    def test_get_all_fleets_excludes_fleets_outside_system(self, galaxy_with_fleets):
        """Should not return fleets at unrelated locations."""
        galaxy, system, empires = galaxy_with_fleets

        # Add a fleet far away
        distant_fleet = MagicMock()
        distant_fleet.id = 999
        distant_fleet.location = HexCoord(100, 100)
        empires[0].fleets.append(distant_fleet)

        result = galaxy.get_all_fleets_in_system(system, empires)

        fleet_ids = [f.id for _, f in result]
        assert 999 not in fleet_ids

    def test_get_all_fleets_empty_system(self, galaxy_with_fleets):
        """Should return empty list if no fleets in system."""
        galaxy, system, empires = galaxy_with_fleets

        # Move all fleets away
        for empire in empires:
            for fleet in empire.fleets:
                fleet.location = HexCoord(500, 500)

        result = galaxy.get_all_fleets_in_system(system, empires)

        assert result == []
