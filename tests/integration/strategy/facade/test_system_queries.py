"""Tests for StrategySessionFacade system and planet query methods.

Uses real StarSystem domain objects with a thin Galaxy mock so that
DTO conversion is exercised against real data and the tests don't
couple to which internal Galaxy method the facade calls.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.star_system import StarSystem
from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility


# ---------------------------------------------------------------------------
# Helpers – lightweight factories for real domain objects
# ---------------------------------------------------------------------------

def _make_star(name="Alpha", location=None, star_type=StarType.MAIN_SEQUENCE,
               color=(255, 255, 0)):
    """Create a minimal real Star for testing."""
    if location is None:
        location = HexCoord(0, 0)
    return Star(
        name=name,
        mass=1.0,
        radius_hexes=1,
        temperature=5778,
        luminosity=1.0,
        spectrum=Spectrum(0, 0, 0, 0.3, 0.4, 0.3, 0, 0, 0),
        star_type=star_type,
        color=color,
        age=4.6e9,
        location=location,
    )


def _make_planet(name="TestPlanet", planet_id=1, location=None,
                 orbit_distance=1, planet_type=PlanetType.BARREN,
                 owner_id=None):
    """Create a minimal real Planet for testing."""
    if location is None:
        location = HexCoord(0, 0)
    p = Planet(
        name=name,
        location=location,
        orbit_distance=orbit_distance,
        mass=5.972e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=planet_type,
    )
    p.id = planet_id
    p.owner_id = owner_id
    return p


def _make_shipyard_facility():
    """Create a minimal PlanetaryFacility that counts as a shipyard."""
    return PlanetaryFacility(
        instance_id="shipyard-1",
        design_id="space_shipyard",
        name="Orbital Shipyard",
        design_data={"layers": {"core": [{"id": "space_shipyard"}]}},
    )


def _make_system(name="TestSystem", global_location=None, stars=None,
                 planets=None):
    """Create a real StarSystem with optional stars/planets."""
    if global_location is None:
        global_location = HexCoord(0, 0)
    system = StarSystem(name=name, global_location=global_location,
                        stars=stars or [])
    if planets:
        system.planets = planets
    return system


def _mock_galaxy_with_systems(systems_dict):
    """Create a mock Galaxy backed by a real systems dict.

    The mock's ``get_system_at_location`` performs a simple dict lookup
    (equivalent to the fast-path in the real Galaxy). This is sufficient
    for facade tests that query at system-center coordinates, and avoids
    coupling to the Galaxy's internal multi-stage search logic.
    """
    mock_galaxy = MagicMock()
    mock_galaxy.systems = systems_dict
    mock_galaxy.get_system_at_location = Mock(
        side_effect=lambda loc: systems_dict.get(loc)
    )
    return mock_galaxy


def _mock_session(galaxy):
    """Create a mock GameSession wrapping a (mock) galaxy."""
    session = Mock()
    session.galaxy = galaxy
    return session


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetAllSystems:
    """Tests for get_all_systems query."""

    def test_get_all_systems_returns_system_infos(self):
        """get_all_systems returns list of SystemInfo DTOs."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import SystemInfo

        star = _make_star(name="Alpha")
        system1 = _make_system("Sol", HexCoord(0, 0), stars=[star])
        system2 = _make_system("Proxima", HexCoord(10, 10))

        galaxy = _mock_galaxy_with_systems({
            HexCoord(0, 0): system1,
            HexCoord(10, 10): system2,
        })

        facade = StrategySessionFacade(_mock_session(galaxy))
        result = facade.get_all_systems()

        assert len(result) == 2
        assert all(isinstance(s, SystemInfo) for s in result)
        names = [s.name for s in result]
        assert "Sol" in names
        assert "Proxima" in names

    def test_get_all_systems_returns_empty_for_no_systems(self):
        """get_all_systems returns empty list when no systems exist."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        galaxy = _mock_galaxy_with_systems({})
        facade = StrategySessionFacade(_mock_session(galaxy))

        assert facade.get_all_systems() == []


class TestGetSystemAtHex:
    """Tests for get_system_at_hex query."""

    def test_get_system_at_hex_returns_system_when_exists(self):
        """get_system_at_hex returns SystemInfo for existing system."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import SystemInfo

        target_hex = HexCoord(5, 5)
        system = _make_system("Alpha Centauri", target_hex)

        galaxy = _mock_galaxy_with_systems({target_hex: system})
        facade = StrategySessionFacade(_mock_session(galaxy))

        result = facade.get_system_at_hex(target_hex)

        assert result is not None
        assert isinstance(result, SystemInfo)
        assert result.name == "Alpha Centauri"
        assert result.global_location == target_hex

    def test_get_system_at_hex_returns_none_when_not_exists(self):
        """get_system_at_hex returns None when no system at hex."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        galaxy = _mock_galaxy_with_systems({})
        facade = StrategySessionFacade(_mock_session(galaxy))

        assert facade.get_system_at_hex(HexCoord(99, 99)) is None


class TestGetPlanet:
    """Tests for get_planet query."""

    def test_get_planet_returns_planet_info_when_found(self):
        """get_planet returns PlanetInfo DTO for existing planet."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import PlanetInfo

        planet = _make_planet(
            "Earth", planet_id=42, location=HexCoord(1, 0),
            orbit_distance=3, planet_type=PlanetType.CONTINENTAL,
            owner_id=0,
        )
        planet.facilities.append(_make_shipyard_facility())
        system = _make_system("Sol", HexCoord(0, 0), planets=[planet])
        galaxy = _mock_galaxy_with_systems({HexCoord(0, 0): system})

        facade = StrategySessionFacade(_mock_session(galaxy))
        result = facade.get_planet(42)

        assert result is not None
        assert isinstance(result, PlanetInfo)
        assert result.planet_id == 42
        assert result.name == "Earth"
        assert result.is_colonized is True
        assert result.has_space_shipyard is True

    def test_get_planet_returns_none_when_not_found(self):
        """get_planet returns None for non-existent planet ID."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        system = _make_system("Empty", HexCoord(0, 0))
        galaxy = _mock_galaxy_with_systems({HexCoord(0, 0): system})

        facade = StrategySessionFacade(_mock_session(galaxy))
        assert facade.get_planet(9999) is None

    def test_get_planet_searches_all_systems(self):
        """get_planet searches planets across all systems."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import PlanetInfo

        planet = _make_planet(
            "Mars", planet_id=55, location=HexCoord(2, 0),
            orbit_distance=4, planet_type=PlanetType.ARID,
        )
        system1 = _make_system("Sol", HexCoord(0, 0))
        system2 = _make_system("Proxima", HexCoord(10, 10), planets=[planet])

        galaxy = _mock_galaxy_with_systems({
            HexCoord(0, 0): system1,
            HexCoord(10, 10): system2,
        })

        facade = StrategySessionFacade(_mock_session(galaxy))
        result = facade.get_planet(55)

        assert result is not None
        assert result.planet_id == 55
        assert result.name == "Mars"


class TestGetPlanetsAtHex:
    """Tests for get_planets_at_hex query."""

    def test_get_planets_at_hex_returns_planets_at_location(self):
        """get_planets_at_hex returns only planets whose global position matches the queried hex."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import PlanetInfo

        system_hex = HexCoord(5, 5)
        target_hex = HexCoord(6, 5)  # system_hex + HexCoord(1, 0)

        planet_a = _make_planet("Planet A", planet_id=1,
                                location=HexCoord(1, 0), orbit_distance=2,
                                planet_type=PlanetType.CONTINENTAL)
        planet_b = _make_planet("Planet B", planet_id=2,
                                location=HexCoord(1, 0), orbit_distance=2,
                                planet_type=PlanetType.JOVIAN)

        system = _make_system("TestSys", system_hex,
                              planets=[planet_a, planet_b])
        galaxy = _mock_galaxy_with_systems({system_hex: system})

        facade = StrategySessionFacade(_mock_session(galaxy))
        result = facade.get_planets_at_hex(target_hex)

        assert len(result) == 2
        assert all(isinstance(p, PlanetInfo) for p in result)

    def test_get_planets_at_hex_excludes_planets_at_other_hexes(self):
        """get_planets_at_hex does NOT return planets at different hexes within the same system."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        system_hex = HexCoord(5, 5)

        # Planet at local (1, 0) → global (6, 5), NOT at (5, 5)
        planet = _make_planet("Distant Planet", planet_id=1,
                              location=HexCoord(1, 0), orbit_distance=3,
                              planet_type=PlanetType.ARID)

        system = _make_system("TestSys", system_hex, planets=[planet])
        galaxy = _mock_galaxy_with_systems({system_hex: system})

        facade = StrategySessionFacade(_mock_session(galaxy))
        result = facade.get_planets_at_hex(system_hex)

        assert result == []

    def test_get_planets_at_hex_returns_empty_when_no_system(self):
        """get_planets_at_hex returns empty list when no system at hex."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        galaxy = _mock_galaxy_with_systems({})
        facade = StrategySessionFacade(_mock_session(galaxy))

        assert facade.get_planets_at_hex(HexCoord(99, 99)) == []

    def test_get_planets_at_hex_returns_empty_for_system_without_planets(self):
        """get_planets_at_hex returns empty list for system without planets."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        system_hex = HexCoord(5, 5)
        system = _make_system("Empty", system_hex)
        galaxy = _mock_galaxy_with_systems({system_hex: system})

        facade = StrategySessionFacade(_mock_session(galaxy))
        assert facade.get_planets_at_hex(system_hex) == []
