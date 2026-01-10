import unittest
from unittest.mock import MagicMock, patch
from pygame.math import Vector2

from game.simulation.projectile_manager import ProjectileManager

class DummyProjectile:
    def __init__(self, **kwargs):
        self.type = 'projectile'
        self.position = kwargs.get('position', Vector2(0,0))
        self.velocity = kwargs.get('velocity', Vector2(0,0))
        self.radius = kwargs.get('radius', 5)
        self.damage = kwargs.get('damage', 10)
        self.is_alive = True
        self.team_id = kwargs.get('team_id', 0)
        self.target = kwargs.get('target', None)
        self.source_weapon = None
        self.status = 'active'
    
    def update(self):
        self.position += self.velocity
        
    def take_damage(self, amount):
        pass

class TestProjectileManager(unittest.TestCase):
    def setUp(self):
        self.manager = ProjectileManager()
        
    def test_projectile_movement(self):
        # Mock projectiles
        p_vel = Vector2(10, 0)
        
        # We need a projectile with update method
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = p_vel
        proj.is_alive = True
        
        self.manager.add_projectile(proj)
        
        grid = MagicMock()
        grid.query_radius.return_value = []
        
        self.manager.update(grid)
        
        proj.update.assert_called()
        
    def test_projectile_collision(self):
        # Setup
        target_ship = MagicMock()
        target_ship.position = Vector2(100, 0)
        target_ship.velocity = Vector2(0, 0)
        target_ship.radius = 10
        target_ship.is_alive = True
        target_ship.team_id = 1
        
        proj = MagicMock()
        proj.team_id = 0
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.damage = 20
        proj.is_alive = True
        proj.type = 'projectile'
        proj.source_weapon = None  # No source weapon, use static damage
        proj.distance_traveled = 5  # Projectile has traveled some distance
        
        self.manager.add_projectile(proj)
        
        grid = MagicMock()
        grid.query_radius.return_value = [target_ship]
        
        self.manager.update(grid)
        
        target_ship.take_damage.assert_called_with(20)
        self.assertFalse(proj.is_alive)
        self.assertEqual(proj.status, 'hit')

    def test_missile_interception(self):
        missile = DummyProjectile(
            position=Vector2(50, 50),
            velocity=Vector2(10, 0),
            radius=2,
            damage=10,
            team_id=0
        )
        missile.type = 'missile'
        
        target_missile = DummyProjectile(
            position=Vector2(60, 50),
            radius=2,
            team_id=1
        )
        target_missile.type = 'missile'
        
        missile.target = target_missile
        
        self.manager.add_projectile(missile)
        self.manager.add_projectile(target_missile)
        
        grid = MagicMock()
        grid.query_radius.return_value = [] 
        
        # Patch take_damage on target to verify call
        with patch.object(target_missile, 'take_damage') as mock_dmg:
             self.manager.update(grid)
             mock_dmg.assert_called_with(10)

if __name__ == '__main__':
    unittest.main()
