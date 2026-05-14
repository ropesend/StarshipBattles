
import pytest
from unittest.mock import MagicMock, patch
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
from game.core.hex_math import HexCoord
from game.strategy.data.star_system import StarSystem
class TestFacadeSystemProximity:
    @pytest.fixture
    def mock_session(self):
        return MagicMock()

    @pytest.fixture
    def facade(self, mock_session):
        return StrategySessionFacade(mock_session)

    def test_get_system_containing_fleet_strict(self, facade, mock_session):
        """Test finding system when fleet is exactly at system location (or planet)."""
        fleet = MagicMock()
        fleet.location = HexCoord(10, 10)
        mock_session._get_fleet_by_id.return_value = fleet
        
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.name = "System A"
        system.planets = []
        system.warp_points = []
        system.stars = []
        
        # Mocking Galaxy.get_system_at_location for strict check logic
        mock_session.galaxy.get_system_at_location.return_value = system
        
        result = facade.get_system_containing_fleet(1)
        assert result is not None
        assert result.name == "System A"

    def test_get_system_containing_fleet_proximity(self, facade, mock_session):
        """Test finding system when fleet is near but not at exact system location."""
        fleet = MagicMock()
        fleet.location = HexCoord(12, 12) # Close to (10,10)
        mock_session._get_fleet_by_id.return_value = fleet
        
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.name = "System B"
        system.planets = []
        system.warp_points = []
        system.stars = []
        
        # Strict check returns None
        mock_session.galaxy.get_system_at_location.return_value = None
        
        # Setup galaxy systems for proximity scan
        mock_session.galaxy.systems = {HexCoord(10, 10): system}
        
        result = facade.get_system_containing_fleet(1)
        assert result is not None
        assert result.name == "System B"

    def test_get_system_containing_fleet_too_far(self, facade, mock_session):
        """Test ensuring too-far fleets are not associated with system."""
        fleet = MagicMock()
        fleet.location = HexCoord(50, 50) # Far from (10,10)
        mock_session._get_fleet_by_id.return_value = fleet
        
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.planets = []
        system.warp_points = []
        system.stars = []
        
        mock_session.galaxy.get_system_at_location.return_value = None
        mock_session.galaxy.systems = {HexCoord(10, 10): system}
        
        result = facade.get_system_containing_fleet(1)
        assert result is None

    def test_get_system_near_hex(self, facade, mock_session):
        """Test getting system near a hex coordinate directly."""
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.name = "System C"
        system.planets = []
        system.warp_points = []
        system.stars = []
        
        # Strict locations returns None
        mock_session.galaxy.get_system_at_location.return_value = None
        
        # Setup galaxy
        mock_session.galaxy.systems = {HexCoord(10, 10): system}
        
        # Test near hit
        result = facade.get_system_near_hex(HexCoord(13, 13))
        assert result is not None
        assert result.name == "System C"
        
        # Test far miss
        result = facade.get_system_near_hex(HexCoord(100, 100))
        assert result is None
