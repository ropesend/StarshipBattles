import unittest
from unittest.mock import MagicMock, patch
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.command_handlers import ColonizeCommandHandler, ColonizeMissionCommandHandler
from game.strategy.engine.order_processor import OrderProcessor
from game.core.hex_math import HexCoord


class TestExplicitColonizeOrders(unittest.TestCase):
    def setUp(self):
        self.processor = OrderProcessor()
        self.session = MagicMock()
        self.fleet = Fleet(1, 0, HexCoord(0, 0))
        self.empire = MagicMock()
        self.empire.id = 0
        self.empire.fleets = [self.fleet]
        self.session.empires = [self.empire]
        # BUG-125: align active_empire with the test fleet's owner so authorization passes.
        self.session.active_empire = self.empire
        self.galaxy = MagicMock()

        # Mock facade
        self.session.facade = MagicMock()
        self.session.turn_engine = MagicMock()

    def test_colonize_command_does_not_add_load_order(self):
        """ColonizeCommandHandler should NOT auto-insert LOAD_POPULATION.

        Colonize commands now only queue COLONIZE. Population loading is
        handled separately by the player.
        """
        colony = MagicMock()
        colony.id = 10
        colony.populations = [MagicMock(race_id="human")]

        self.session._get_fleet_by_id.return_value = self.fleet
        self.session._get_planet_by_id.return_value = colony
        self.session.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=True)
        self.session.galaxy.get_planet_global_hex.return_value = HexCoord(0, 0)

        handler = ColonizeCommandHandler()
        from game.strategy.engine.commands import IssueColonizeCommand
        cmd = IssueColonizeCommand(fleet_id=1, planet_id=10)

        handler.execute(self.session, cmd)

        # Should have 1 order: COLONIZE only (no LOAD_POPULATION)
        self.assertEqual(len(self.fleet.orders), 1)
        self.assertEqual(self.fleet.orders[0].type, OrderType.COLONIZE)
        # No LOAD_POPULATION order should be present
        order_types = [o.type for o in self.fleet.orders]
        self.assertNotIn(OrderType.LOAD_POPULATION, order_types)

    def test_processor_handles_load_population_as_transfer(self):
        """OrderProcessor should recognize LOAD_POPULATION as a valid transfer order."""
        self.fleet.add_order(Order(OrderType.LOAD_POPULATION, {'direction': 'load', 'cargo_type': 'passengers', 'amount': 100, 'planet_id': 10}))

        from game.core.validation import ValidationResult
        # PROJ-368 Phase 4: live transfer logic moved to TransferHandler;
        # patch the handler's passenger-load dispatcher to short-circuit.
        transfer_handler = self.processor._handler_registry.get(OrderType.TRANSFER)
        with patch('game.strategy.validation.TransferValidator.validate', return_value=ValidationResult.success()):
            with patch.object(transfer_handler, '_dispatch_load_planet_passengers', return_value=100):
                result = self.processor.process_transfer(self.fleet, self.empire, self.galaxy)
                self.assertTrue(result.success)

    def test_generic_load_population_auto_resolves_colony(self):
        """Generic LOAD_POPULATION (no planet_id) auto-resolves colony at fleet hex (BUG-70)."""
        colony = MagicMock()
        colony.id = 10
        colony.name = "Earth"
        colony.owner_id = 0  # Matches empire.id
        colony.populations = [MagicMock(race_id="human", count=5000)]
        colony.total_population = 5000

        # Generic order — no planet_id
        self.fleet.add_order(Order(OrderType.LOAD_POPULATION, {
            'direction': 'load', 'cargo_type': 'passengers', 'amount': 0
        }))

        # Galaxy returns colony at fleet's hex
        self.galaxy.get_planets_at_global_hex.return_value = [colony]

        from game.core.validation import ValidationResult
        # PROJ-368 Phase 4: short-circuit the passenger-load dispatcher on
        # the live TransferHandler.
        transfer_handler = self.processor._handler_registry.get(OrderType.TRANSFER)
        with patch('game.strategy.validation.TransferValidator.validate', return_value=ValidationResult.success()):
            with patch.object(transfer_handler, '_dispatch_load_planet_passengers', return_value=1000):
                result = self.processor.process_transfer(self.fleet, self.empire, self.galaxy)
                self.assertTrue(result.success)
                self.assertEqual(result.amount_transferred, 1000)

    def test_generic_load_population_skips_when_no_colony(self):
        """Generic LOAD_POPULATION is a no-op when fleet is not at an owned colony (BUG-70)."""
        # Generic order — no planet_id
        self.fleet.add_order(Order(OrderType.LOAD_POPULATION, {
            'direction': 'load', 'cargo_type': 'passengers', 'amount': 0
        }))

        # No planets at fleet's hex
        self.galaxy.get_planets_at_global_hex.return_value = []

        result = self.processor.process_transfer(self.fleet, self.empire, self.galaxy)
        # Should succeed (no-op) and pop the order
        self.assertTrue(result.success)
        self.assertEqual(len(self.fleet.orders), 0)  # Order was popped


if __name__ == '__main__':
    unittest.main()
