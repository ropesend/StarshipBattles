
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
        
        result = facade.systems.containing_fleet(1)
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
        
        result = facade.systems.containing_fleet(1)
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
        
        result = facade.systems.containing_fleet(1)
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
        result = facade.systems.near_hex(HexCoord(13, 13))
        assert result is not None
        assert result.name == "System C"
        
        # Test far miss
        result = facade.systems.near_hex(HexCoord(100, 100))
        assert result is None

    def test_systems_by_name(self, facade, mock_session):
        """PROJ-477 Phase 2: ``facade.systems.by_name`` projects the named
        system to a ``SystemInfo``; ``None`` for an unknown name."""
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(5, 5)
        system.name = "Sol"
        system.planets = []
        system.warp_points = []
        system.stars = []
        system.primary_star = None

        mock_session.galaxy.get_system_by_name.side_effect = (
            lambda name: system if name == "Sol" else None
        )

        result = facade.systems.by_name("Sol")
        assert result is not None and result.name == "Sol"
        assert facade.systems.by_name("Nowhere") is None

    def test_systems_of_object(self, facade, mock_session):
        """PROJ-477 Phase 2: ``facade.systems.of_object`` projects the
        containing system to a ``SystemInfo``."""
        planet = object()
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(5, 5)
        system.name = "Home"
        system.planets = []
        system.warp_points = []
        system.stars = []
        system.primary_star = None

        mock_session.galaxy.get_system_of_object.side_effect = (
            lambda obj: system if obj is planet else None
        )

        result = facade.systems.of_object(planet)
        assert result is not None and result.name == "Home"
        assert facade.systems.of_object(object()) is None

    def test_systems_at_map_hex_radius_50_semantics(self, facade, mock_session):
        """PROJ-477 Phase 2: ``facade.systems.at_map_hex`` routes through the
        pathfinder at radius=50 (NOT near_hex max_dist=8)."""
        system = MagicMock(spec=StarSystem)
        system.global_location = HexCoord(10, 10)
        system.name = "Owner"
        system.planets = []
        system.warp_points = []
        system.stars = []
        system.primary_star = None

        captured = {}

        def at_hex(hex_c, radius):
            captured["radius"] = radius
            return system

        mock_session.galaxy._pathfinder.get_system_at_hex.side_effect = at_hex

        result = facade.systems.at_map_hex(HexCoord(0, 0))
        assert result is not None and result.name == "Owner"
        assert captured["radius"] == 50
