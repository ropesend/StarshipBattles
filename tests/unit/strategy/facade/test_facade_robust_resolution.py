
import pytest
from unittest.mock import MagicMock, patch
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import StarSystem
from game.strategy.data.planet import Planet

class TestFacadeRobustResolution:
    @pytest.fixture
    def mock_session(self):
        return MagicMock()

    @pytest.fixture
    def facade(self, mock_session):
        return StrategySessionFacade(mock_session)

    def test_get_planets_at_hex_strict_match(self, facade, mock_session):
        """Test finding planets when strict lookup succeeds."""
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        p1 = MagicMock(spec=Planet)
        p1.name = "Test Planet"
        p1.id = 1
        p1.location = HexCoord(1, 0)  # Planet at local (1, 0)
        p1.planet_type = MagicMock()
        p1.planet_type.name = "CONTINENTAL"
        p1.orbit_distance = 1
        p1.owner_id = None
        p1.populations = []
        p1.has_space_shipyard = False
        p1.total_population = 0
        p1.max_population = 100
        # Required for PlanetInfo.from_planet
        p1.resources = {}
        system.planets = [p1]

        # Strict lookup succeeds
        mock_session.galaxy.get_system_at_location.return_value = system

        # Query planet's global position: system.global_location + planet.location = (10,10) + (1,0) = (11,10)
        planet_global_hex = HexCoord(11, 10)
        result = facade.get_planets_at_hex(planet_global_hex)
        assert len(result) == 1
        
    def test_get_planets_at_hex_radius_match(self, facade, mock_session):
        """Test finding planets when strict lookup fails but radius search succeeds."""
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        p1 = MagicMock(spec=Planet)
        p1.name = "Test Planet"
        p1.id = 1
        p1.location = HexCoord(1, 0)  # Planet at local (1, 0) -> global (11, 10)
        p1.planet_type = MagicMock()
        p1.planet_type.name = "CONTINENTAL"
        p1.orbit_distance = 1
        p1.owner_id = None
        p1.populations = []
        p1.has_space_shipyard = False
        p1.total_population = 0
        p1.max_population = 100
        # Required for PlanetInfo.from_planet
        p1.resources = {}
        system.planets = [p1]

        # Planet's global position: (10,10) + (1,0) = (11, 10)
        planet_global_hex = HexCoord(11, 10)

        # Strict lookup fails
        mock_session.galaxy.get_system_at_location.return_value = None

        # Radius lookup succeeds (mocking pathfinding import)
        with patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex') as mock_pathfinding:
            mock_pathfinding.return_value = system

            result = facade.get_planets_at_hex(planet_global_hex)

            assert len(result) == 1
            mock_pathfinding.assert_called_once()
            
    def test_get_planets_at_hex_no_match(self, facade, mock_session):
        """Test when no system is found strictly or by radius."""
        # Strict lookup fails
        mock_session.galaxy.get_system_at_location.return_value = None
        
        # Radius lookup fails
        with patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex') as mock_pathfinding:
            mock_pathfinding.return_value = None
            
            result = facade.get_planets_at_hex(HexCoord(100, 100))
            
            assert len(result) == 0
