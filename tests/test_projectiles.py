"""Tests for Projectile class behavior."""
import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projectiles import Projectile
from ship import Ship, LayerType, initialize_ship_data
from components import load_components, create_component


class TestProjectileBasics(unittest.TestCase):
    """Test basic projectile initialization and properties."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        # Create a simple owner ship
        self.owner = Ship("Shooter", 0, 0, (255, 255, 255), team_id=0)
        self.owner.add_component(create_component('bridge'), LayerType.CORE)
        self.owner.recalculate_stats()
    
    def test_projectile_initialization(self):
        """Projectile should initialize with correct stats."""
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(100, 100),
            velocity=pygame.math.Vector2(10, 0),
            damage=50,
            range_val=1000,
            endurance=5.0,
            proj_type='projectile'
        )
        
        self.assertEqual(proj.damage, 50)
        self.assertEqual(proj.max_range, 1000)
        self.assertEqual(proj.endurance, 5.0)
        from ship_combat import AttackType
        self.assertEqual(proj.type, AttackType.PROJECTILE.value)
        self.assertEqual(proj.team_id, 0)
        self.assertTrue(proj.is_alive)
        self.assertEqual(proj.status, 'active')
        self.assertEqual(proj.distance_traveled, 0)
    
    def test_projectile_inherits_team_from_owner(self):
        """Projectile team_id should match owner's team_id."""
        self.owner.team_id = 2
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )
        self.assertEqual(proj.team_id, 2)


class TestProjectileMovement(unittest.TestCase):
    """Test projectile movement and lifecycle."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.owner = Ship("Shooter", 0, 0, (255, 255, 255), team_id=0)
        self.owner.add_component(create_component('bridge'), LayerType.CORE)
        self.owner.recalculate_stats()
    
    def test_projectile_update_moves_position(self):
        """Projectile should move by velocity each update."""
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(10, 5),
            damage=10,
            range_val=10000,
            endurance=100.0,
            proj_type='projectile'
        )
        
        initial_pos = pygame.math.Vector2(proj.position)
        proj.update()
        
        # Position should change by velocity
        self.assertAlmostEqual(proj.position.x, initial_pos.x + 10, places=1)
        self.assertAlmostEqual(proj.position.y, initial_pos.y + 5, places=1)
    
    def test_projectile_range_limit(self):
        """Projectile should die when max range exceeded."""
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),  # 100 units per tick
            damage=10,
            range_val=250,  # Max range of 250
            endurance=100.0,
            proj_type='projectile'
        )
        
        # First update: 100 distance
        proj.update()
        self.assertTrue(proj.is_alive)
        
        # Second update: 200 distance
        proj.update()
        self.assertTrue(proj.is_alive)
        
        # Third update: 300 distance > 250 range
        proj.update()
        self.assertFalse(proj.is_alive)
        self.assertEqual(proj.status, 'miss')
    
    def test_projectile_endurance_limit(self):
        """Projectile should die when endurance depleted."""
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(1, 0),
            damage=10,
            range_val=100000,
            endurance=0.02,  # Only 2 ticks of life
            proj_type='projectile'
        )
        
        # First tick
        proj.update()
        self.assertTrue(proj.is_alive)
        
        # Second tick - should deplete
        proj.update()
        self.assertFalse(proj.is_alive)
        self.assertEqual(proj.status, 'miss')


class TestProjectileDamage(unittest.TestCase):
    """Test projectile damage mechanics (for PDC interception)."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.owner = Ship("Shooter", 0, 0, (255, 255, 255), team_id=0)
        self.owner.add_component(create_component('bridge'), LayerType.CORE)
        self.owner.recalculate_stats()
    
    def test_projectile_take_damage(self):
        """Projectile should take damage and die at 0 HP."""
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(1, 0),
            damage=100,
            range_val=1000,
            endurance=10.0,
            proj_type='missile',
            hp=10  # Missile with 10 HP
        )
        
        self.assertEqual(proj.hp, 10)
        
        # Take partial damage
        proj.take_damage(5)
        self.assertEqual(proj.hp, 5)
        self.assertTrue(proj.is_alive)
        
        # Take lethal damage
        proj.take_damage(10)
        self.assertEqual(proj.hp, -5)
        self.assertFalse(proj.is_alive)
        self.assertEqual(proj.status, 'destroyed')
    
    def test_projectile_status_tracking(self):
        """Projectile status should reflect lifecycle state."""
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(1, 0),
            damage=10,
            range_val=1000,
            endurance=10.0,
            proj_type='projectile'
        )
        
        # Initial status
        self.assertEqual(proj.status, 'active')
        
        # After destruction
        proj.take_damage(100)
        self.assertEqual(proj.status, 'destroyed')


class TestMissileGuidance(unittest.TestCase):
    """Test guided missile tracking behavior."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.owner = Ship("Shooter", 0, 0, (255, 255, 255), team_id=0)
        self.owner.add_component(create_component('bridge'), LayerType.CORE)
        self.owner.recalculate_stats()
        
        self.target = Ship("Target", 1000, 0, (255, 0, 0), team_id=1)
        self.target.add_component(create_component('bridge'), LayerType.CORE)
        self.target.recalculate_stats()
    
    def test_missile_guidance_tracks_target(self):
        """Missile should turn toward target position."""
        # Missile starts going up, target is to the right
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(0, -100),  # Going up
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,  # 90 deg/sec turn rate
            max_speed=100,
            target=self.target,
            hp=5
        )
        
        initial_vel = pygame.math.Vector2(proj.velocity)
        
        # After several updates, should be turning toward target (to the right)
        for _ in range(20):
            proj.update()
        
        # Velocity x-component should have increased (turning right toward target)
        # Velocity x-component should have increased (turning right toward target)
        # Note: If turn_speed is low or dt is simulated internal to update, check mechanics.
        # Projectile.update() uses global dt or clock.
        
        # Manually force some turning logic check if strictly unit testing internal logic
        # Or verify 'target' is actually set on the projectile instance created above.
        
        # We need to simulate time passing for the missile to turn.
        # Check if proj velocity x has moved positively from 0.
        self.assertGreater(proj.velocity.x, initial_vel.x)
    
    def test_missile_stops_tracking_dead_target(self):
        """Missile should continue straight if target dies."""
        proj = Projectile(
            owner=self.owner,
            position=pygame.math.Vector2(0, 0),
            velocity=pygame.math.Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=self.target,
            hp=5
        )
        
        # Kill target
        self.target.is_alive = False
        
        initial_vel = pygame.math.Vector2(proj.velocity)
        proj.update()
        
        # Velocity should remain unchanged (no guidance adjustment)
        self.assertAlmostEqual(proj.velocity.x, initial_vel.x, places=1)
        self.assertAlmostEqual(proj.velocity.y, initial_vel.y, places=1)


if __name__ == '__main__':
    unittest.main()
