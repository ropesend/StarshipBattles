import unittest
from unittest.mock import MagicMock
from game.strategy.data.fleet import Fleet, OrderType, FleetOrder
from game.strategy.engine.command_handlers import ColonizeCommandHandler, ColonizeMissionCommandHandler
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
from game.strategy.data.planet import Planet, SpeciesPopulation
from game.core.hex_math import HexCoord

class TestExplicitColonizationOrders(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.galaxy = MagicMock()
        self.empire = MagicMock()
        self.session.galaxy = self.galaxy
        self.session.empires = [self.empire]
        
        # Setup source planet (colony)
        self.source_planet = MagicMock()
        self.source_planet.id = 1
        self.source_planet.name = "Origin"
        self.source_planet.location = HexCoord(0, 0)
        self.source_planet.populations = [SpeciesPopulation("human", 500)]
        self.source_planet.owner_id = 0
        
        # Setup target planet
        self.target_planet = MagicMock()
        self.target_planet.id = 2
        self.target_planet.name = "Target"
        self.target_planet.location = HexCoord(1, 1)
        self.target_planet.owner_id = None
        self.target_planet.planet_type = MagicMock()
        self.target_planet.planet_type.name = "Terran"
        
        # Setup fleet at origin
        self.fleet = Fleet(101, 0, HexCoord(0, 0))
        self.ship = MagicMock()
        self.ship.is_alive = True
        self.ship.is_derelict = False
        self.ship.get_cargo_capacity.return_value = 1000
        self.ship.get_current_cargo.return_value = 0
        self.ship.has_component_type.return_value = True # Has colony pod
        self.ship.get_calculated_stats.return_value = {
            'mass': 100,
            'movement_points': 5,
            'cargo_storage': {'passengers': 1000}
        }
        self.fleet.add_ship(self.ship)
        
        self.empire.fleets = [self.fleet]
        self.empire.add_colony = MagicMock()
        
        # Registry mock
        self.session._find_colony_at_fleet.return_value = self.source_planet
        self.session._get_fleet_by_id.return_value = self.fleet
        self.session._get_planet_by_id.return_value = self.target_planet
        self.galaxy.get_planet_by_id.return_value = self.target_planet

    def test_direct_colonize_adds_explicit_load_order(self):
        """Test that IssueColonizeCommand adds an explicit LOAD_POPULATION order."""
        cmd = MagicMock()
        cmd.fleet_id = 101
        cmd.planet_id = 2
        
        handler = ColonizeCommandHandler()
        self.session.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=True)
        
        handler.execute(self.session, cmd)
        
        # Should have 2 orders: LOAD_POPULATION then COLONIZE
        self.assertEqual(len(self.fleet.orders), 2)
        self.assertEqual(self.fleet.orders[0].type, OrderType.LOAD_POPULATION)
        self.assertEqual(self.fleet.orders[1].type, OrderType.COLONIZE)
        
        # Verify load order params
        load_params = self.fleet.orders[0].target
        self.assertEqual(load_params['direction'], 'load')
        self.assertEqual(load_params['species_id'], 'human')
        self.assertEqual(load_params['planet_id'], self.source_planet.id)

    def test_colonize_mission_adds_explicit_load_order(self):
        """Test that QueueColonizeMissionCommand adds an explicit LOAD_POPULATION order."""
        cmd = MagicMock()
        cmd.fleet_id = 101
        cmd.planet_id = 2
        cmd.target_hex = HexCoord(1, 1)
        
        # Mock pathfinding and pod validation
        with unittest.mock.patch('game.strategy.data.pathfinding.find_hybrid_path', return_value=[HexCoord(0, 0), HexCoord(1, 1)]), \
             unittest.mock.patch('game.strategy.validation.ColonizeValidator.find_ship_with_colony_pod', return_value=self.ship), \
             unittest.mock.patch('game.strategy.validation.ColonizeValidator.get_available_colony_pods', return_value={'Terran': 1}), \
             unittest.mock.patch('game.strategy.validation.ColonizeValidator.get_committed_colony_pods', return_value={}):
            handler = ColonizeMissionCommandHandler()
            result = handler.execute(self.session, cmd)
            
        self.assertTrue(result.is_valid, f"Validation failed: {result.errors}")
        # Should have LOAD_POPULATION, MOVE, then COLONIZE
        self.assertEqual(len(self.fleet.orders), 3)
        self.assertEqual(self.fleet.orders[0].type, OrderType.LOAD_POPULATION)
        self.assertEqual(self.fleet.orders[1].type, OrderType.MOVE)
        self.assertEqual(self.fleet.orders[2].type, OrderType.COLONIZE)
        
        # Verify species_id is present
        self.assertEqual(self.fleet.orders[0].target['species_id'], 'human')

    def test_process_load_population_order(self):
        """Test that FleetOrderProcessor correctly processes LOAD_POPULATION."""
        processor = FleetOrderProcessor()
        
        # Setup load order
        transfer_params = {
            'direction': 'load',
            'cargo_type': 'passengers',
            'amount': 100,
            'planet_id': self.source_planet.id,
            'species_id': 'human'
        }
        order = FleetOrder(OrderType.LOAD_POPULATION, target=transfer_params)
        self.fleet.add_order(order)
        
        # Mock validation
        with unittest.mock.patch('game.strategy.validation.TransferValidator.validate') as mock_val:
            mock_val.return_value = MagicMock(is_valid=True)
            
            # Execute processor
            with unittest.mock.patch.object(processor, '_execute_load', return_value=100) as mock_exec:
                processor.process_transfer(self.fleet, self.empire, self.galaxy)
                
                # Verify _execute_load was called and order popped
                self.assertTrue(mock_exec.called)
                self.assertEqual(len(self.fleet.orders), 0)

if __name__ == '__main__':
    unittest.main()
