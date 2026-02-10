"""Tests for StrategySessionFacade system and planet query methods."""
import pytest
from unittest.mock import Mock, MagicMock
from game.core.hex_math import HexCoord


class TestGetAllSystems:
    """Tests for get_all_systems query."""

    def test_get_all_systems_returns_system_infos(self):
        """get_all_systems returns list of SystemInfo DTOs."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import SystemInfo

        # Create mock systems
        mock_star = MagicMock()
        mock_star.name = "Alpha"
        mock_star.star_type = MagicMock()
        mock_star.star_type.name = "MAIN_SEQUENCE"
        mock_star.color = (255, 255, 0)
        mock_star.location = HexCoord(0, 0)

        mock_system1 = MagicMock()
        mock_system1.name = "Sol"
        mock_system1.global_location = HexCoord(0, 0)
        mock_system1.primary_star = mock_star
        mock_system1.planets = []
        mock_system1.warp_points = []

        mock_system2 = MagicMock()
        mock_system2.name = "Proxima"
        mock_system2.global_location = HexCoord(10, 10)
        mock_system2.primary_star = None
        mock_system2.planets = []
        mock_system2.warp_points = []

        # Create mock galaxy with systems dict
        mock_galaxy = MagicMock()
        mock_galaxy.systems = {
            HexCoord(0, 0): mock_system1,
            HexCoord(10, 10): mock_system2,
        }

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_all_systems()

        assert len(result) == 2
        assert all(isinstance(s, SystemInfo) for s in result)
        names = [s.name for s in result]
        assert "Sol" in names
        assert "Proxima" in names

    def test_get_all_systems_returns_empty_for_no_systems(self):
        """get_all_systems returns empty list when no systems exist."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_all_systems()

        assert result == []


class TestGetSystemAtHex:
    """Tests for get_system_at_hex query."""

    def test_get_system_at_hex_returns_system_when_exists(self):
        """get_system_at_hex returns SystemInfo for existing system."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import SystemInfo

        target_hex = HexCoord(5, 5)

        mock_system = MagicMock()
        mock_system.name = "Alpha Centauri"
        mock_system.global_location = target_hex
        mock_system.primary_star = None
        mock_system.planets = []
        mock_system.warp_points = []

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {target_hex: mock_system}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_system_at_hex(target_hex)

        assert result is not None
        assert isinstance(result, SystemInfo)
        assert result.name == "Alpha Centauri"
        assert result.global_location == target_hex

    def test_get_system_at_hex_returns_none_when_not_exists(self):
        """get_system_at_hex returns None when no system at hex."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_system_at_hex(HexCoord(99, 99))

        assert result is None


class TestGetPlanet:
    """Tests for get_planet query."""

    def test_get_planet_returns_planet_info_when_found(self):
        """get_planet returns PlanetInfo DTO for existing planet."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import PlanetInfo

        mock_planet = MagicMock()
        mock_planet.id = 42
        mock_planet.name = "Earth"
        mock_planet.planet_type = MagicMock()
        mock_planet.planet_type.name = "CONTINENTAL"
        mock_planet.location = HexCoord(1, 0)
        mock_planet.orbit_distance = 3
        mock_planet.owner_id = 0
        mock_planet.has_space_shipyard = True

        mock_system = MagicMock()
        mock_system.planets = [mock_planet]

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {HexCoord(0, 0): mock_system}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
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

        mock_system = MagicMock()
        mock_system.planets = []

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {HexCoord(0, 0): mock_system}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_planet(9999)

        assert result is None

    def test_get_planet_searches_all_systems(self):
        """get_planet searches planets across all systems."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import PlanetInfo

        # Planet in second system
        mock_planet = MagicMock()
        mock_planet.id = 55
        mock_planet.name = "Mars"
        mock_planet.planet_type = MagicMock()
        mock_planet.planet_type.name = "ARID"
        mock_planet.location = HexCoord(2, 0)
        mock_planet.orbit_distance = 4
        mock_planet.owner_id = None
        mock_planet.has_space_shipyard = False

        mock_system1 = MagicMock()
        mock_system1.planets = []

        mock_system2 = MagicMock()
        mock_system2.planets = [mock_planet]

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {
            HexCoord(0, 0): mock_system1,
            HexCoord(10, 10): mock_system2,
        }

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_planet(55)

        assert result is not None
        assert result.planet_id == 55
        assert result.name == "Mars"


class TestGetPlanetsAtHex:
    """Tests for get_planets_at_hex query."""

    def test_get_planets_at_hex_returns_planets_at_location(self):
        """get_planets_at_hex returns all planets at given hex."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        from game.strategy.facade.dto import PlanetInfo

        system_hex = HexCoord(5, 5)

        # Create two planets at different local hexes
        mock_planet1 = MagicMock()
        mock_planet1.id = 1
        mock_planet1.name = "Planet A"
        mock_planet1.planet_type = MagicMock()
        mock_planet1.planet_type.name = "CONTINENTAL"
        mock_planet1.location = HexCoord(1, 0)
        mock_planet1.orbit_distance = 2
        mock_planet1.owner_id = None
        mock_planet1.has_space_shipyard = False

        mock_planet2 = MagicMock()
        mock_planet2.id = 2
        mock_planet2.name = "Planet B"
        mock_planet2.planet_type = MagicMock()
        mock_planet2.planet_type.name = "JOVIAN"
        mock_planet2.location = HexCoord(2, 0)
        mock_planet2.orbit_distance = 5
        mock_planet2.owner_id = None
        mock_planet2.has_space_shipyard = False

        mock_system = MagicMock()
        mock_system.global_location = system_hex
        mock_system.planets = [mock_planet1, mock_planet2]

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {system_hex: mock_system}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_planets_at_hex(system_hex)

        assert len(result) == 2
        assert all(isinstance(p, PlanetInfo) for p in result)

    def test_get_planets_at_hex_returns_empty_when_no_system(self):
        """get_planets_at_hex returns empty list when no system at hex."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_planets_at_hex(HexCoord(99, 99))

        assert result == []

    def test_get_planets_at_hex_returns_empty_for_system_without_planets(self):
        """get_planets_at_hex returns empty list for system without planets."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        system_hex = HexCoord(5, 5)

        mock_system = MagicMock()
        mock_system.global_location = system_hex
        mock_system.planets = []

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {system_hex: mock_system}

        mock_session = Mock()
        mock_session.galaxy = mock_galaxy

        facade = StrategySessionFacade(mock_session)
        result = facade.get_planets_at_hex(system_hex)

        assert result == []
