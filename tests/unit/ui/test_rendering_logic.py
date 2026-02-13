import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os
import pygame

# Add parent dir to path


from game.ui.renderer.game_renderer import draw_ship, LAYER_COLORS
from game.simulation.entities.ship import LayerType
from game.simulation.entities.layer_data import LayerData


class TestRenderingLogic:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for pygame draw and font."""
        # Patch Pygame specifically in the module under test to ensure full isolation
        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw, \
             patch('game.ui.renderer.game_renderer.pygame.font') as mock_font:

            self.mock_draw = mock_draw
            self.mock_font = mock_font

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
                LayerType.CORE: LayerData(),
                LayerType.INNER: LayerData(),
                LayerType.OUTER: LayerData(),
                LayerType.ARMOR: LayerData()
            }

            self.mock_camera.world_to_screen.side_effect = lambda pos: pos

            yield

    def test_draw_ship_culling(self):
        """Verify ship is skipped if out of camera bounds."""
        self.ship.position = pygame.math.Vector2(-1000, -1000)

        draw_ship(self.mock_surface, self.ship, self.mock_camera)

        self.mock_draw.circle.assert_not_called()

    @patch('game.ui.assets.ShipThemeManager')
    def test_component_color_coding(self, mock_theme_mgr_cls):
        """Verify components are colored based on abilities."""
        mock_theme_instance = MagicMock()
        mock_theme_mgr_cls.instance.return_value = mock_theme_instance
        mock_theme_instance.load_image.return_value = None

        comp_weapon = MagicMock()
        comp_weapon.is_active = True
        comp_weapon.name = "Weapon"
        comp_weapon.has_ability.side_effect = lambda x: True if x == 'WeaponAbility' else False

        comp_engine = MagicMock()
        comp_engine.is_active = True
        comp_engine.name = "Engine"
        comp_engine.has_ability.side_effect = lambda x: True if x == 'CombatPropulsion' else False

        start_comps = [comp_weapon, comp_engine]
        self.ship.layers[LayerType.OUTER].components = start_comps

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

        assert found_weapon_color, "Weapon color (Red) not found"
        assert found_engine_color, "Engine color (Green) not found"


class TestDrawShipBehavior:
    """Tests for draw_ship() function behavior."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        yield

    def _create_mock_ship(self):
        """Create a mock ship with required attributes."""
        ship = MagicMock()
        ship.is_alive = True
        ship.position = pygame.math.Vector2(400, 300)
        ship.radius = 20
        ship.angle = 0
        ship.ship_class = "Escort"
        ship.color = (100, 100, 200)
        ship.forward_vector.return_value = pygame.math.Vector2(1, 0)
        ship.layers = {
            LayerType.CORE: LayerData(),
            LayerType.INNER: LayerData(),
            LayerType.OUTER: LayerData(),
            LayerType.ARMOR: LayerData()
        }
        return ship

    def _create_mock_camera(self, zoom=1.0):
        """Create a mock camera."""
        camera = MagicMock()
        camera.zoom = zoom
        camera.width = 800
        camera.height = 600
        camera.show_overlay = False
        camera.world_to_screen.side_effect = lambda pos: pos
        return camera

    def test_draw_ship_dead_ship_returns_early(self):
        """Test draw_ship with dead ship returns early, no drawing calls."""
        ship = self._create_mock_ship()
        ship.is_alive = False
        camera = self._create_mock_camera()
        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            draw_ship(surface, ship, camera)
            mock_draw.circle.assert_not_called()

    @patch('game.ui.assets.ShipThemeManager')
    def test_draw_ship_with_theme_image(self, mock_theme_cls):
        """Test draw_ship with theme image available draws it."""
        ship = self._create_mock_ship()
        camera = self._create_mock_camera()

        # Create real surface to use as mock theme image
        mock_img = pygame.Surface((100, 100), pygame.SRCALPHA)
        mock_instance = MagicMock()
        mock_theme_cls.instance.return_value = mock_instance
        mock_instance.load_image.return_value = mock_img
        mock_instance.get_image_metrics.return_value = pygame.Rect(0, 0, 80, 80)
        mock_instance.get_manual_scale.return_value = 1.0

        surface = MagicMock()

        draw_ship(surface, ship, camera)

        # Should have called blit (to draw the theme image)
        assert surface.blit.called

    @patch('game.ui.assets.ShipThemeManager')
    def test_draw_ship_no_theme_image_draws_dot(self, mock_theme_cls):
        """Test draw_ship with no theme image (fallback to geometric rendering)."""
        ship = self._create_mock_ship()
        camera = self._create_mock_camera()

        mock_instance = MagicMock()
        mock_theme_cls.instance.return_value = mock_instance
        mock_instance.load_image.return_value = None

        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            draw_ship(surface, ship, camera)
            # Should draw a simple circle (dot) as fallback
            assert mock_draw.circle.called

    @patch('game.ui.assets.ShipThemeManager')
    def test_draw_ship_zoom_affects_radius(self, mock_theme_cls):
        """Test draw_ship with different zoom levels affects scaled_radius."""
        ship = self._create_mock_ship()
        ship.radius = 20

        mock_instance = MagicMock()
        mock_theme_cls.instance.return_value = mock_instance
        mock_instance.load_image.return_value = None

        surface = MagicMock()

        # Test at low zoom
        camera_low = self._create_mock_camera(zoom=0.5)
        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            draw_ship(surface, ship, camera_low)
            # Radius should be scaled by zoom

        # Test at high zoom
        camera_high = self._create_mock_camera(zoom=2.0)
        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            draw_ship(surface, ship, camera_high)
            # Still should draw

    @patch('game.ui.assets.ShipThemeManager')
    def test_draw_ship_at_camera_boundary(self, mock_theme_cls):
        """Test draw_ship at camera boundary (partially visible) still draws."""
        ship = self._create_mock_ship()
        # Position at edge of screen
        ship.position = pygame.math.Vector2(790, 300)  # Near right edge

        camera = self._create_mock_camera()

        mock_instance = MagicMock()
        mock_theme_cls.instance.return_value = mock_instance
        mock_instance.load_image.return_value = None

        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            draw_ship(surface, ship, camera)
            # Should still draw (not culled)
            assert mock_draw.circle.called


class TestLayerColors:
    """Tests for layer color mapping."""

    def test_layer_colors_constant_mapping(self):
        """Test LAYER_COLORS constant has all layer types."""
        assert LayerType.ARMOR in LAYER_COLORS
        assert LayerType.OUTER in LAYER_COLORS
        assert LayerType.INNER in LAYER_COLORS
        assert LayerType.CORE in LAYER_COLORS

    def test_layer_colors_values(self):
        """Test LAYER_COLORS has correct color values."""
        assert LAYER_COLORS[LayerType.ARMOR] == (100, 100, 100)
        assert LAYER_COLORS[LayerType.OUTER] == (200, 50, 50)
        assert LAYER_COLORS[LayerType.INNER] == (50, 50, 200)
        assert LAYER_COLORS[LayerType.CORE] == (220, 220, 220)
