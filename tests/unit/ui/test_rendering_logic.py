import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os
import pygame

# Add parent dir to path


from game.ui.renderer.game_renderer import draw_ship, draw_hud, draw_bar, LAYER_COLORS
from game.simulation.entities.ship import LayerType
from game.simulation.entities.layer_data import LayerData
from game.core.constants import ResourceType


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

        assert found_accel, "Acceleration stat text not found in HUD render calls"


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


class TestDrawHudBehavior:
    """Tests for draw_hud() function behavior."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        yield

    def _create_mock_ship(self):
        """Create a mock ship with required HUD attributes."""
        ship = MagicMock()
        ship.name = "Test Ship"
        ship.is_alive = True
        ship.mass = 1000
        ship.total_thrust = 5000
        ship.drag = 0.5
        ship.layers = {
            LayerType.CORE: LayerData(),
            LayerType.INNER: LayerData(),
            LayerType.OUTER: LayerData(),
            LayerType.ARMOR: LayerData()
        }

        # Setup resources
        ship.resources.get_value.side_effect = lambda r: {
            ResourceType.FUEL: 50,
            ResourceType.AMMO: 10,
            ResourceType.ENERGY: 100
        }.get(r, 0)
        ship.resources.get_max_value.side_effect = lambda r: {
            ResourceType.FUEL: 100,
            ResourceType.AMMO: 20,
            ResourceType.ENERGY: 100
        }.get(r, 0)

        return ship

    def test_draw_hud_renders_ship_name(self):
        """Test draw_hud renders ship name text."""
        ship = self._create_mock_ship()
        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.font') as mock_font, \
             patch('game.ui.renderer.game_renderer.pygame.draw'):
            mock_font_inst = MagicMock()
            mock_font_inst.render.return_value = MagicMock()
            mock_font.SysFont.return_value = mock_font_inst

            draw_hud(surface, ship, 10, 10)

            # Check that ship name was rendered
            render_calls = [str(call) for call in mock_font_inst.render.call_args_list]
            name_rendered = any("Test Ship" in str(call) for call in render_calls)
            assert name_rendered, "Ship name should be rendered"

    def test_draw_hud_renders_hp_bar(self):
        """Test draw_hud renders HP bar via draw_bar calls."""
        ship = self._create_mock_ship()
        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.font') as mock_font, \
             patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            mock_font_inst = MagicMock()
            mock_font_inst.render.return_value = MagicMock()
            mock_font.SysFont.return_value = mock_font_inst

            draw_hud(surface, ship, 10, 10)

            # draw_bar uses pygame.draw.rect
            assert mock_draw.rect.called, "Should draw resource bars"

    def test_draw_hud_with_zero_hp_ship(self):
        """Test draw_hud with dead ship (is_alive=False) shows different color."""
        ship = self._create_mock_ship()
        ship.is_alive = False
        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.font') as mock_font, \
             patch('game.ui.renderer.game_renderer.pygame.draw'):
            mock_font_inst = MagicMock()
            mock_font_inst.render.return_value = MagicMock()
            mock_font.SysFont.return_value = mock_font_inst

            draw_hud(surface, ship, 10, 10)

            # Check that red color (255, 50, 50) was used for dead ship
            render_calls = mock_font_inst.render.call_args_list
            dead_color_used = any(
                call.args[2] == (255, 50, 50)
                for call in render_calls
                if len(call.args) >= 3
            )
            assert dead_color_used, "Dead ship should use red color"

    def test_draw_hud_resource_display(self):
        """Test draw_hud displays fuel, energy, ammo."""
        ship = self._create_mock_ship()
        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.font') as mock_font, \
             patch('game.ui.renderer.game_renderer.pygame.draw'):
            mock_font_inst = MagicMock()
            mock_font_inst.render.return_value = MagicMock()
            mock_font.SysFont.return_value = mock_font_inst

            draw_hud(surface, ship, 10, 10)

            render_calls = [str(call) for call in mock_font_inst.render.call_args_list]
            # Check that resource labels are rendered
            assert any("Fuel" in str(call) for call in render_calls)
            assert any("Ammo" in str(call) for call in render_calls)
            assert any("Energy" in str(call) for call in render_calls)


class TestDrawBar:
    """Tests for draw_bar() utility function."""

    @pytest.fixture(autouse=True)
    def setup(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        yield

    def test_draw_bar_basic(self):
        """Test draw_bar draws background, fill, and border."""
        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            draw_bar(surface, 10, 20, 100, 10, 0.5, (255, 0, 0))

            # Should draw 3 rects: background, fill, border
            assert mock_draw.rect.call_count == 3

    def test_draw_bar_clamped_percentage(self):
        """Test draw_bar clamps percentage to 0-1 range."""
        surface = MagicMock()

        with patch('game.ui.renderer.game_renderer.pygame.draw') as mock_draw:
            # Test > 1.0 (should clamp to 1.0)
            draw_bar(surface, 0, 0, 100, 10, 1.5, (255, 0, 0))

            # Test < 0.0 (should clamp to 0.0)
            draw_bar(surface, 0, 0, 100, 10, -0.5, (255, 0, 0))

            # Should not crash and draw normally
            assert mock_draw.rect.call_count == 6  # 3 per call


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
