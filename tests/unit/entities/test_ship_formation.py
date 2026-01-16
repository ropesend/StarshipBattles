"""
Tests for ShipFormation class (formation relationship management).
TDD-first approach for ShipFormation extraction from Ship class.
"""
import unittest
import pygame
from unittest import mock

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.entities.ship_formation import ShipFormation
from game.simulation.components.component import load_components
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


class TestShipFormationUnit(unittest.TestCase):
    """Unit tests for ShipFormation class in isolation."""

    def setUp(self):
        """Initialize game data for each test."""
        if not pygame.get_init():
            pygame.init()
        initialize_ship_data()
        load_components(str(get_data_dir() / "components.json"))
    
    def tearDown(self):
        """Clean up after each test."""
        RegistryManager.instance().clear()
        if pygame.get_init():
            pygame.quit()
        mock.patch.stopall()
    
    def test_initialization_defaults(self):
        """ShipFormation initializes with correct default values."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        formation = ShipFormation(ship)
        
        self.assertIs(formation.ship, ship)
        self.assertIsNone(formation.master)
        self.assertIsNone(formation.offset)
        self.assertEqual(formation.rotation_mode, 'relative')
        self.assertEqual(formation.members, [])
        self.assertTrue(formation.active)
    
    def test_is_master_property(self):
        """is_master returns True when ship has members."""
        ship = Ship("MasterShip", 0, 0, (255, 255, 255))
        formation = ShipFormation(ship)
        
        self.assertFalse(formation.is_master)
        
        # Add a dummy member
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        formation.members.append(follower)
        
        self.assertTrue(formation.is_master)
    
    def test_is_member_property(self):
        """is_member returns True when ship has a master."""
        ship = Ship("FollowerShip", 100, 0, (255, 255, 255))
        formation = ShipFormation(ship)
        
        self.assertFalse(formation.is_member)
        
        master = Ship("MasterShip", 0, 0, (200, 200, 200))
        formation.master = master
        
        self.assertTrue(formation.is_member)
    
    def test_join_formation(self):
        """join() sets up the formation relationship correctly."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        
        offset = pygame.math.Vector2(50, 30)
        follower_formation = ShipFormation(follower)
        follower_formation.join(master, offset)
        
        self.assertIs(follower_formation.master, master)
        self.assertEqual(follower_formation.offset, offset)
        self.assertTrue(follower_formation.active)
    
    def test_leave_formation(self):
        """leave() clears the formation relationship."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        
        offset = pygame.math.Vector2(50, 30)
        follower_formation = ShipFormation(follower)
        follower_formation.join(master, offset)
        
        # Now leave
        follower_formation.leave()
        
        self.assertIsNone(follower_formation.master)
        self.assertFalse(follower_formation.active)
    
    def test_add_member(self):
        """add_member() adds a follower to the formation."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        
        master_formation = ShipFormation(master)
        offset = pygame.math.Vector2(-50, 20)
        master_formation.add_member(follower, offset)
        
        self.assertIn(follower, master_formation.members)
        self.assertTrue(master_formation.is_master)
    
    def test_remove_member(self):
        """remove_member() removes a follower from the formation."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        
        master_formation = ShipFormation(master)
        offset = pygame.math.Vector2(-50, 20)
        master_formation.add_member(follower, offset)
        
        # Now remove
        master_formation.remove_member(follower)
        
        self.assertNotIn(follower, master_formation.members)
        self.assertFalse(master_formation.is_master)
    
    def test_rotation_mode_fixed(self):
        """rotation_mode can be set to 'fixed'."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        formation = ShipFormation(ship)
        
        formation.rotation_mode = 'fixed'
        self.assertEqual(formation.rotation_mode, 'fixed')


class TestShipFormationIntegration(unittest.TestCase):
    """Integration tests for ShipFormation with Ship class."""

    def setUp(self):
        """Initialize game data for each test."""
        if not pygame.get_init():
            pygame.init()
        initialize_ship_data()
        load_components(str(get_data_dir() / "components.json"))
    
    def tearDown(self):
        """Clean up after each test."""
        RegistryManager.instance().clear()
        if pygame.get_init():
            pygame.quit()
        mock.patch.stopall()
    
    def test_ship_has_formation_attribute(self):
        """Ship has a formation attribute of type ShipFormation."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        
        self.assertTrue(hasattr(ship, 'formation'))
        self.assertIsInstance(ship.formation, ShipFormation)
    
    def test_backward_compat_formation_master(self):
        """ship.formation_master delegates to ship.formation.master."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        
        # Set via delegation property
        follower.formation_master = master
        
        # Verify via formation object
        self.assertIs(follower.formation.master, master)
        
        # Get via delegation property
        self.assertIs(follower.formation_master, master)
    
    def test_backward_compat_formation_offset(self):
        """ship.formation_offset delegates to ship.formation.offset."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        offset = pygame.math.Vector2(100, 50)
        
        ship.formation_offset = offset
        
        self.assertEqual(ship.formation.offset, offset)
        self.assertEqual(ship.formation_offset, offset)
    
    def test_backward_compat_formation_rotation_mode(self):
        """ship.formation_rotation_mode delegates to ship.formation.rotation_mode."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        
        ship.formation_rotation_mode = 'fixed'
        
        self.assertEqual(ship.formation.rotation_mode, 'fixed')
        self.assertEqual(ship.formation_rotation_mode, 'fixed')
    
    def test_backward_compat_formation_members(self):
        """ship.formation_members delegates to ship.formation.members."""
        master = Ship("MasterShip", 0, 0, (255, 255, 255))
        follower = Ship("FollowerShip", 100, 0, (200, 200, 200))
        
        master.formation_members.append(follower)
        
        self.assertIn(follower, master.formation.members)
        self.assertIn(follower, master.formation_members)
    
    def test_backward_compat_in_formation(self):
        """ship.in_formation delegates to ship.formation.active."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        
        self.assertTrue(ship.in_formation)
        
        ship.in_formation = False
        
        self.assertFalse(ship.formation.active)
        self.assertFalse(ship.in_formation)


if __name__ == '__main__':
    unittest.main()
