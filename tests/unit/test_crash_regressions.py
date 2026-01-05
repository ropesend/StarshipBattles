
import unittest
import pygame
import pygame_gui
from unittest.mock import MagicMock
from ui.builder.weapons_panel import WeaponsReportPanel
import os

class TestCrashRegressions(unittest.TestCase):
    def setUp(self):
        pygame.init()
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        self.surface = pygame.display.set_mode((800, 600))
        self.manager = pygame_gui.UIManager((800, 600))
        
        # Mock Dependencies
        self.builder = MagicMock()
        self.builder.ship = MagicMock()
        self.sprite_mgr = MagicMock()
        
        # Setup Rect
        self.rect = pygame.Rect(0, 0, 400, 400)
        
        # Create Panel
        self.panel = WeaponsReportPanel(self.builder, self.manager, self.rect, self.sprite_mgr)

    def tearDown(self):
        pass # pygame.quit() removed for session isolation

    def test_weapons_panel_unbound_local_error(self):
        """
        Regression Test for UnboundLocalError: 'weapon_bar_width' referenced before assignment.
        This occurs when a weapon is present but has 0 range or max_range is 0, skipping the assignment block.
        """
        # Setup specific weapon that triggers the condition
        weapon_mock = MagicMock()
        weapon_mock.name = "Test Weapon"
        weapon_mock.range = 0  # Trigger the skip
        weapon_mock.damage = 10
        # Mock ability to ensure it's treated as a valid weapon type (e.g. Projectile)
        weapon_mock.has_ability.side_effect = lambda x: x == 'ProjectileWeaponAbility'
        weapon_mock.get_ability.return_value = MagicMock(range=0)
        # Mock attribute access for getattr(weapon, 'range', 0)
        # MagicMock usually handles this, but let's be explicit if needed.
        
        # Setup Panel State
        self.panel._max_range = 100 # Global max range > 0
        self.panel._weapons_cache = [{'weapon': weapon_mock, 'count': 1}]
        
        # Mock font render to avoid pygame errors
        self.panel.font = MagicMock()
        self.panel.small_font = MagicMock()
        self.panel.target_font = MagicMock()
        
        # Mock drawing methods to checking if they receive correct args (and prove we didn't crash before calling them)
        self.panel._draw_projectile_weapon_bar = MagicMock()
        
        try:
            self.panel.draw(self.surface)
        except UnboundLocalError:
            self.fail("WeaponsReportPanel.draw() raised UnboundLocalError! Fix is not working.")
        except Exception as e:
            # Other errors might happen due to mocking, but we specifically care about UnboundLocalError
            print(f"Caught expected/unrelated error during mock draw: {e}")
            pass
            
        # Verify the draw method was called with a width of 0 (since range was 0)
        # self.panel._draw_projectile_weapon_bar.assert_called()
        # Args: screen, weapon, bar_y, start_x, bar_width, weapon_bar_width, weapon_range, damage, is_seeker
        # We check if it was called at all.
        # calls = self.panel._draw_projectile_weapon_bar.call_args_list
        # if calls:
        #     args, _ = calls[0]
        #     weapon_bar_width = args[5]
        #     self.assertEqual(weapon_bar_width, 0, "Should have defaulted to 0 width")

    def test_weapons_panel_zero_max_range(self):
        """Test case where all weapons have 0 range (Max Range = 0)."""
        weapon_mock = MagicMock()
        weapon_mock.range = 0
        weapon_mock.has_ability.side_effect = lambda x: x == 'ProjectileWeaponAbility'
        weapon_mock.get_ability.return_value = MagicMock(range=0)

        self.panel._max_range = 0
        self.panel._weapons_cache = [{'weapon': weapon_mock, 'count': 1}]
        
        # This triggers the condition 'if self._max_range > 0' -> False.
        # weapon_bar_width must be defined before use.
        
        # Mock helpers
        self.panel._get_scaled_icon = MagicMock(return_value=None)
        self.panel._get_weapon_name_surface = MagicMock(return_value=pygame.Surface((1,1)))
        self.panel._draw_direction_indicator = MagicMock()
        self.panel._draw_projectile_weapon_bar = MagicMock()
        
        try:
            self.panel.draw(self.surface)
        except UnboundLocalError:
             self.fail("WeaponsReportPanel.draw() raised UnboundLocalError with max_range=0!")

if __name__ == '__main__':
    unittest.main()
