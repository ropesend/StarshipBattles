import unittest
from unittest.mock import MagicMock
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord

class TestColonizePopulation(unittest.TestCase):
    def test_colonize_with_zero_passengers_yields_zero_pop(self):
        processor = OrderProcessor()
        
        # Mock Fleet
        fleet = MagicMock(spec=Fleet)
        fleet.id = 1
        fleet.location = HexCoord(0, 0)
        fleet.orders = []
        fleet.get_current_order.return_value = FleetOrder(OrderType.COLONIZE, None)
        # Mock cargo: 0 passengers
        fleet.resources.get_fleet_cargo_current.return_value = 0
        fleet.unload_cargo_from_fleet = MagicMock()

        # Mock Empire with Race Config
        empire = MagicMock()
        empire.id = 0
        empire.race_config = MagicMock()
        empire.race_config.race_id = "human"
        empire.add_colony = MagicMock()
        empire.remove_fleet = MagicMock()

        # Mock Planet
        planet = MagicMock()
        planet.owner_id = None
        planet.name = "New World"
        planet.populations = []
        
        # Test direct call to _transfer_founding_population since that's where the logic was
        # (We can also test process_colonize but that requires more mocking of validation)
        
        added_pop = processor._transfer_founding_population(fleet, planet, empire)
        
        print(f"Added Population: {added_pop}")
        
        # Assertions
        self.assertEqual(added_pop, 0, "Should add 0 population if fleet has 0 passengers")
        self.assertEqual(len(planet.populations), 0, "Planet should have no population added")

if __name__ == '__main__':
    unittest.main()
