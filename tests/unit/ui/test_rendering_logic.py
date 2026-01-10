
import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import pygame

# Add parent dir to path


from game.ui.renderer.game_renderer import draw_ship, draw_hud
from game.simulation.entities.ship import LayerType

class TestRenderingLogic(unittest.TestCase):

    def setUp(self):
        # Patch Pygame specifically in the module under test to ensure full isolation
        self.patcher_draw = patch('game.ui.renderer.game_renderer.pygame.draw')
        self.mock_draw = self.patcher_draw.start()
        
        self.patcher_font = patch('game.ui.renderer.game_renderer.pygame.font')
        self.mock_font = self.patcher_font.start()
        
        # Setup common mocks
        self.mock_surface = MagicMock()
        self.mock_camera = MagicMock()
        self.mock_camera.zoom = 1.0
        self.mock_camera.width = 800
        self.mock_camera.height = 600
        
        self.ship = MagicMock()
        self.ship.is_alive = True
        self.ship.position = pygame.math.Vector2(400, 300)
        self.ship.radius = 20
        self.ship.angle = 0
        self.ship.scale = 1.0
        self.ship.forward_vector.return_value = pygame.math.Vector2(1, 0)
        
        self.ship.layers = {
            LayerType.CORE: {'components': []},
            LayerType.INNER: {'components': []},
            LayerType.OUTER: {'components': []},
            LayerType.ARMOR: {'components': []}
        }
        
        self.mock_camera.world_to_screen.side_effect = lambda pos: pos 
        
    def tearDown(self):
        self.patcher_draw.stop()
        self.patcher_font.stop()
        
        # Add missing cleanup to fix parallel execution failures
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()

    def test_draw_ship_culling(self):
        """Verify ship is skipped if out of camera bounds."""
        self.ship.position = pygame.math.Vector2(-1000, -1000)
        
        draw_ship(self.mock_surface, self.ship, self.mock_camera)
        
        self.mock_draw.circle.assert_not_called()
        
    @patch('game.simulation.ship_theme.ShipThemeManager') 
    def test_component_color_coding(self, mock_theme_mgr_cls):
        """Verify components are colored based on abilities."""
        mock_theme_instance = MagicMock()
        mock_theme_mgr_cls.get_instance.return_value = mock_theme_instance
        mock_theme_instance.get_image.return_value = None 
        
        comp_weapon = MagicMock()
        comp_weapon.is_active = True
        comp_weapon.name = "Weapon"
        comp_weapon.has_ability.side_effect = lambda x: True if x == 'WeaponAbility' else False
        
        comp_engine = MagicMock()
        comp_engine.is_active = True
        comp_engine.name = "Engine"
        comp_engine.has_ability.side_effect = lambda x: True if x == 'CombatPropulsion' else False
        
        start_comps = [comp_weapon, comp_engine]
        self.ship.layers[LayerType.OUTER]['components'] = start_comps
        
        self.mock_camera.zoom = 1.0
        self.mock_camera.show_overlay = True
        
        draw_ship(self.mock_surface, self.ship, self.mock_camera)
        
        found_weapon_color = False
        found_engine_color = False
        
        for call_args in self.mock_draw.circle.call_args_list:
            if len(call_args.args) >= 2:
                color = call_args.args[1]
                if color == (255, 50, 50):
                    found_weapon_color = True
                elif color == (50, 255, 100):
                    found_engine_color = True
                    
        self.assertTrue(found_weapon_color, "Weapon color (Red) not found")
        self.assertTrue(found_engine_color, "Engine color (Green) not found")

    def test_draw_hud_stats(self):
        """Verify HUD pulls stats from ship properties."""
        mock_font_inst = MagicMock()
        mock_text_surf = MagicMock()
        mock_font_inst.render.return_value = mock_text_surf
        self.mock_font.SysFont.return_value = mock_font_inst
        
        self.ship.mass = 1000
        self.ship.total_thrust = 5000 
        self.ship.drag = 0.5
        # Configure resources mock to return values
        resources_data = {
            'fuel': {'current': 50, 'max': 100},
            'ammo': {'current': 10, 'max': 20},
            'energy': {'current': 100, 'max': 100}
        }
        
        def get_value_side_effect(name):
            return resources_data.get(name, {}).get('current', 0)
            
        def get_max_value_side_effect(name):
            return resources_data.get(name, {}).get('max', 0)
            
        self.ship.resources.get_value.side_effect = get_value_side_effect
        self.ship.resources.get_max_value.side_effect = get_max_value_side_effect

        
        draw_hud(self.mock_surface, self.ship, 10, 10)
        
        calls = mock_font_inst.render.call_args_list
        found_accel = False
        
        for c in calls:
            if len(c.args) > 0:
                text = c.args[0]
                if "Accel: 5.0" in text:
                    found_accel = True
                    break
        
        self.assertTrue(found_accel, "Acceleration stat text not found in HUD render calls")

if __name__ == '__main__':
    unittest.main()
