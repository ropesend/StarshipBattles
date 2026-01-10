import unittest
import sys
import os
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.builder.weapons_panel import WeaponsReportPanel

class TestBug13Fix(unittest.TestCase):
    def setUp(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        self.surface = pygame.display.set_mode((800, 600))
        self.manager = pygame_gui.UIManager((800, 600))
        
        self.builder = MagicMock()
        self.builder.ship = MagicMock()
        self.sprite_mgr = MagicMock()
        self.rect = pygame.Rect(0, 0, 800, 600)
        
        self.panel = WeaponsReportPanel(self.builder, self.manager, self.rect, self.sprite_mgr)
        self.panel._max_range = 1000

    def tearDown(self):
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()
        
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()

    def test_unified_drawing_structure(self):
        """Verify the unified drawing method exists and old ones are gone."""
        self.assertTrue(hasattr(self.panel, '_draw_unified_weapon_bar'))
        self.assertFalse(hasattr(self.panel, '_draw_beam_weapon_bar'))
        self.assertFalse(hasattr(self.panel, '_draw_projectile_weapon_bar'))

    def test_get_points_of_interest_projectile(self):
        """Verify points of interest for a projectile weapon."""
        weapon = MagicMock()
        # Mocking has_ability for ProjectileWeaponAbility
        weapon.has_ability.side_effect = lambda a: a == 'ProjectileWeaponAbility' or a == 'WeaponAbility'
        
        ab = MagicMock()
        ab.range = 500
        ab.damage = 50
        weapon.get_ability.return_value = ab
        
        points = self.panel._get_points_of_interest(weapon, self.builder.ship)
        
        # Should have 6 points from INTEREST_POINTS_RANGE (0.0 to 1.0)
        self.assertEqual(len(points), 6)
        self.assertEqual(points[0]['range'], 0)
        self.assertEqual(points[0]['priority'], 0)
        self.assertEqual(points[-1]['range'], 500)
        self.assertEqual(points[-1]['priority'], 0)
        self.assertEqual(points[1]['range'], 100) # 20%
        self.assertEqual(points[1]['priority'], 2)

    def test_get_points_of_interest_beam(self):
        """Verify points of interest for a beam weapon including accuracy thresholds."""
        weapon = MagicMock()
        weapon.has_ability.side_effect = lambda a: a in ['BeamWeaponAbility', 'WeaponAbility']
        
        ab = MagicMock()
        ab.range = 1000
        ab.damage = 100
        ab.base_accuracy = 2.0
        ab.accuracy_falloff = 0.005 # Steep falloff for testing thresholds
        weapon.get_ability.return_value = ab
        
        # Mock ship to return baseline sensor score
        self.builder.ship.get_total_sensor_score.return_value = 0.0
        self.panel.target_defense_mod = 0.0
        
        points = self.panel._get_points_of_interest(weapon, self.builder.ship)
        
        # Verify we have both types
        has_acc = any(p['type'] == 'accuracy' for p in points)
        has_range = any(p['type'] == 'range' for p in points)
        
        self.assertTrue(has_acc, "Should have accuracy based points for beams")
        self.assertTrue(has_range, "Should have range percentage points")
        
        # Check order
        ranges = [p['range'] for p in points]
        self.assertEqual(ranges, sorted(ranges), "Points should be sorted by range")

    def test_prioritization_logic(self):
        """Verify that high priority points (0 and Max range) are kept even if crowded."""
        # We can't easily test the drawing, but we can test the filtering logic if we extract it
        # or mock the list of points.
        
        # For now, let's just run the drawing method with a mock screen to ensure no crashes
        weapon = MagicMock()
        weapon.has_ability.side_effect = lambda a: a in ['BeamWeaponAbility', 'WeaponAbility']
        ab = MagicMock()
        ab.range = 100
        ab.damage = 10
        ab.base_accuracy = 2.0
        ab.accuracy_falloff = 0.001
        weapon.get_ability.return_value = ab
        
        # Mock ship to return baseline sensor score
        self.builder.ship.get_total_sensor_score.return_value = 0.0
        self.panel.target_defense_mod = 0.0
        
        # This will test the collision logic path
        # Use a real surface to avoid TypeError in pygame.draw
        self.panel._draw_unified_weapon_bar(self.surface, weapon, self.builder.ship, 0, 0, 100, 10, 100)

if __name__ == '__main__':
    unittest.main()
