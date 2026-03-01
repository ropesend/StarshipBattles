import unittest
from unittest.mock import MagicMock
from game.core.hex_math import HexCoord
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.galaxy import Galaxy, StarSystem

class TestFacadeColonyRetrieval(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_galaxy = MagicMock()
        self.mock_session._session.galaxy = self.mock_galaxy # Correctly mock facade internals
        self.facade = StrategySessionFacade(self.mock_session._session)

    def test_get_planets_at_hex_system_center(self):
        """Test retrieving planets when clicking the system center."""
        system_loc = HexCoord(10, 10)
        
        system = MagicMock()
        system.global_location = system_loc
        system.name = "TestSystem"
        
        planet = MagicMock()
        planet.id = "p1"
        planet.name = "TestPlanet"
        planet.owner_id = 0
        planet.location = HexCoord(0, 0) # At center
        # Mock other needed attributes for DTO
        planet.planet_type = PlanetType.CONTINENTAL
        planet.image_id = "test_img"
        planet.image_rotation = 0
        planet.radius_hexes = 1
        planet.construction_queue = []
        planet.facilities = {}
        planet.resources = {}
        
        system.planets = [planet]
        
        # Mock Galaxy.get_system_at_location
        self.mock_galaxy.get_system_at_location.return_value = system
        
        result = self.facade.get_planets_at_hex(system_loc)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "TestPlanet")
        self.assertEqual(result[0].owner_id, 0)
        
    def test_get_planets_at_hex_offset_planet(self):
        """Test retrieving planets when clicking a planet at an offset."""
        system_loc = HexCoord(10, 10)
        offset = HexCoord(1, -1)
        click_loc = system_loc + offset
        
        system = MagicMock()
        system.global_location = system_loc
        system.name = "TestSystem"
        
        planet = MagicMock()
        planet.id = "p1"
        planet.name = "TestPlanet"
        planet.owner_id = 0
        planet.location = offset # Offset from center
        planet.planet_type = PlanetType.CONTINENTAL
        planet.image_id = "test_img"
        planet.image_rotation = 0
        planet.radius_hexes = 1
        planet.construction_queue = []
        planet.facilities = {}
        planet.resources = {}

        system.planets = [planet]
        
        # Mock Galaxy behavior: return system if location matches system + planet.location
        def get_system_side_effect(loc):
            if loc == system_loc or loc == (system_loc + offset):
                return system
            return None
            
        self.mock_galaxy.get_system_at_location.side_effect = get_system_side_effect
        
        # Test 1: Click on planet -> Should return planet
        result = self.facade.get_planets_at_hex(click_loc)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "TestPlanet")
        self.assertEqual(result[0].planet_type, "CONTINENTAL")

        # Test 2: Click on system center (where planet is NOT) -> Should return empty list
        result_empty = self.facade.get_planets_at_hex(system_loc)
        self.assertEqual(len(result_empty), 0)


if __name__ == '__main__':
    unittest.main()
