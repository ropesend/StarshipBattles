import unittest
import pygame
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from builder_gui import BuilderSceneGUI
from components import Component

class TestTooltips(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.builder = MagicMock(spec=BuilderSceneGUI)
        self.builder.width = 800
        self.builder.height = 600
        self.builder.sprite_mgr = MagicMock()
        self.builder.sprite_mgr.get_sprite.return_value = pygame.Surface((32, 32))

    def call_draw_tooltip(self, comp):
        screen = MagicMock()
        
        # Patch fonts and drawing
        with patch('pygame.font.SysFont') as mock_font_cls, \
             patch('pygame.draw.rect'), \
             patch('pygame.draw.line'), \
             patch('pygame.mouse.get_pos', return_value=(100, 100)):
            
            mock_font = MagicMock()
            mock_font.size.return_value = (100, 20)
            mock_font_cls.return_value = mock_font
            
            BuilderSceneGUI._draw_tooltip(self.builder, screen, comp)
                
            return screen, mock_font

    def test_bridge_tooltip(self):
        # Use SimpleNamespace so hasattr works correctly and missing attrs raise AttributeError (or just return False for hasattr)
        # Actually hasattr on SimpleNamespace returns False if not present.
        comp = SimpleNamespace(
            name="Bridge", type_str="Bridge", mass=50.0, max_hp=200, 
            allowed_layers=[SimpleNamespace(name="CORE")],
            sprite_index=0, modifiers=[], abilities={"CommandAndControl": True, "CrewCapacity": -5},
            data={'major_classification': 'Command'}
        )
        # Needed for image loading if sprite_index is used? Yes.
        
        screen, font = self.call_draw_tooltip(comp)
        
        rendered_texts = [call.args[0] for call in font.render.call_args_list]
        
        self.assertIn("Bridge", rendered_texts)
        self.assertIn("Mass: 50.0t", rendered_texts)
        self.assertIn("HP: 200", rendered_texts)
        self.assertIn("  • Command & Control", rendered_texts)
        self.assertIn("  • Crew Required: 5", rendered_texts)

    def test_weapon_tooltip(self):
        comp = SimpleNamespace(
            name="Railgun", type_str="ProjectileWeapon", mass=100.0, max_hp=150,
            allowed_layers=[SimpleNamespace(name="OUTER")],
            sprite_index=0, modifiers=[], abilities={},
            damage=40, range=2400, reload_time=2.0, ammo_cost=1, firing_arc=45,
            data={'major_classification': 'Weapon'}
        )
        
        screen, font = self.call_draw_tooltip(comp)
        
        rendered_texts = [call.args[0] for call in font.render.call_args_list]
        
        self.assertIn("Damage: 40", rendered_texts)
        self.assertIn("Range: 2400", rendered_texts)
        self.assertIn("Reload: 2.0s", rendered_texts)
        self.assertIn("Ammo Cost: 1", rendered_texts)
        self.assertIn("Arc: 45°", rendered_texts)

    def test_shield_tooltip(self):
        comp = SimpleNamespace(
            name="Shield Regen", type_str="ShieldRegenerator", mass=40.0, max_hp=80,
            allowed_layers=[], sprite_index=0, modifiers=[], abilities={},
            shield_capacity=0, regen_rate=5.0, energy_cost=2.0,
            data={'major_classification': 'Defense'}
        )
        
        screen, font = self.call_draw_tooltip(comp)
        
        rendered_texts = [call.args[0] for call in font.render.call_args_list]
        
        self.assertIn("Shield Regen: 5.0/s", rendered_texts)
        self.assertIn("Regen Cost: 2.0/s", rendered_texts)

if __name__ == '__main__':
    unittest.main()
