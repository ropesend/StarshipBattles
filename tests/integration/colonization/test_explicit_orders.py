import unittest
from unittest.mock import MagicMock, patch
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.engine.command_handlers import ColonizeCommandHandler, ColonizeMissionCommandHandler
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
from game.core.hex_math import HexCoord

class TestExplicitColonizeOrders(unittest.TestCase):
    def setUp(self):
        self.processor = FleetOrderProcessor()
        self.session = MagicMock()
        self.fleet = Fleet(1, 0, HexCoord(0, 0))
        self.empire = MagicMock()
        self.empire.fleets = [self.fleet]
        self.session.empires = [self.empire]
        self.galaxy = MagicMock()
        
        # Mock facade
        self.session.facade = MagicMock()
        self.session.turn_engine = MagicMock()

    def test_colonize_command_adds_load_order(self):
        """ColonizeCommandHandler should add LOAD_POPULATION if at a colony."""
        colony = MagicMock()
        colony.id = 10
        colony.populations = [MagicMock(race_id="human")]

        # Mock fleet resolution via BaseCommandHandler._resolve_fleet
        self.session._get_fleet_by_id.return_value = self.fleet
        self.session._get_planet_by_id.return_value = colony  # planet_id=10 resolves to colony
        self.session._find_colony_at_fleet.return_value = colony
        self.session.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=True)
        self.session.galaxy.get_planet_global_hex.return_value = HexCoord(0, 0)

        handler = ColonizeCommandHandler()
        from game.strategy.engine.commands import IssueColonizeCommand
        cmd = IssueColonizeCommand(fleet_id=1, planet_id=10)
        
        handler.execute(self.session, cmd)
        
        # Should have 2 orders: LOAD_POPULATION and COLONIZE
        self.assertEqual(len(self.fleet.orders), 2)
        self.assertEqual(self.fleet.orders[0].type, OrderType.LOAD_POPULATION)
        self.assertEqual(self.fleet.orders[1].type, OrderType.COLONIZE)
        self.assertEqual(self.fleet.orders[0].target['species_id'], "human")

    def test_processor_handles_load_population_as_transfer(self):
        """FleetOrderProcessor should recognize LOAD_POPULATION as a valid transfer order."""
        self.fleet.add_order(FleetOrder(OrderType.LOAD_POPULATION, {'direction': 'load', 'cargo_type': 'passengers', 'amount': 100, 'planet_id': 10}))
        
        from game.core.validation import ValidationResult
        with patch('game.strategy.validation.TransferValidator.validate', return_value=ValidationResult.success()):
            with patch.object(self.processor, '_execute_load', return_value=100):
                result = self.processor.process_transfer(self.fleet, self.empire, self.galaxy)
                self.assertTrue(result.success)

if __name__ == '__main__':
    unittest.main()
