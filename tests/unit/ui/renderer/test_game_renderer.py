"""Unit tests for game/ui/renderer/game_renderer.py

PROJ-142: TCG-UI2-001 - Tests for ship rendering functions and constants.
All tests mock pygame to avoid display initialization.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import math


class TestRenderingConstants:
    """Tests for rendering constants exported by game_renderer module.

    PROJ-157: Removed trivial positivity checks, keeping relationship/semantic tests.
    """

    def test_min_zoom_for_image_positive(self):
        """MIN_ZOOM_FOR_IMAGE should be positive and small."""
        from game.ui.renderer.game_renderer import MIN_ZOOM_FOR_IMAGE
        assert 0 < MIN_ZOOM_FOR_IMAGE < 1

    def test_min_zoom_for_components_greater_than_image_zoom(self):
        """MIN_ZOOM_FOR_COMPONENTS should be greater than MIN_ZOOM_FOR_IMAGE."""
        from game.ui.renderer.game_renderer import MIN_ZOOM_FOR_IMAGE, MIN_ZOOM_FOR_COMPONENTS
        assert MIN_ZOOM_FOR_COMPONENTS > MIN_ZOOM_FOR_IMAGE

    def test_image_rotation_offset_is_minus_90(self):
        """IMAGE_ROTATION_OFFSET should be -90 (ship images point up)."""
        from game.ui.renderer.game_renderer import IMAGE_ROTATION_OFFSET
        assert IMAGE_ROTATION_OFFSET == -90


class TestLayerColors:
    """Tests for LAYER_COLORS mapping."""

    def test_layer_colors_has_renderable_layer_types(self):
        """LAYER_COLORS should have entries for renderable LayerTypes (ARMOR, OUTER, INNER, CORE)."""
        from game.ui.renderer.game_renderer import LAYER_COLORS
        from game.core.constants import LayerType

        # Only renderable layers (not HULL which is internal)
        renderable_layers = [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]
        for layer_type in renderable_layers:
            assert layer_type in LAYER_COLORS, f"Missing {layer_type}"

    def test_layer_colors_are_rgb_tuples(self):
        """All layer colors should be RGB tuples."""
        from game.ui.renderer.game_renderer import LAYER_COLORS

        for layer_type, color in LAYER_COLORS.items():
            assert isinstance(color, tuple), f"{layer_type} color is not a tuple"
            assert len(color) == 3, f"{layer_type} color has {len(color)} components"

    def test_layer_colors_components_in_range(self):
        """All color components should be in [0, 255]."""
        from game.ui.renderer.game_renderer import LAYER_COLORS

        for layer_type, color in LAYER_COLORS.items():
            for i, component in enumerate(color):
                assert isinstance(component, int), f"{layer_type}[{i}] is not int"
                assert 0 <= component <= 255, f"{layer_type}[{i}]={component} out of range"


class TestDrawShipCulling:
    """Tests for draw_ship culling behavior."""

    @pytest.fixture
    def mock_surface(self):
        """Create a mock pygame surface."""
        return Mock()

    @pytest.fixture
    def mock_camera(self):
        """Create a mock camera with typical settings."""
        camera = Mock()
        camera.zoom = 1.0
        camera.width = 1920
        camera.height = 1080

        # world_to_screen returns a mock Vector2
        def world_to_screen(pos):
            result = Mock()
            result.x = pos.x
            result.y = pos.y
            return result
        camera.world_to_screen = world_to_screen
        camera.show_overlay = False
        return camera

    @pytest.fixture
    def mock_ship(self):
        """Create a mock ship for testing."""
        ship = Mock()
        ship.is_alive = True
        ship.position = Mock()
        ship.position.x = 500.0
        ship.position.y = 500.0
        ship.radius = 20.0
        ship.angle = 0.0
        ship.color = (100, 100, 200)
        ship.ship_class = "Destroyer"
        ship.layers = {}
        return ship

    def test_dead_ship_not_drawn(self, mock_surface, mock_camera, mock_ship):
        """Dead ships should not be rendered."""
        from game.ui.renderer.game_renderer import draw_ship

        mock_ship.is_alive = False

        with patch('game.ui.renderer.game_renderer.ShipThemeManager'):
            draw_ship(mock_surface, mock_ship, mock_camera)

        # Should not have called any pygame.draw methods
        mock_surface.blit.assert_not_called()

    def test_ship_culled_when_off_screen_left(self, mock_surface, mock_camera, mock_ship):
        """Ships far off screen left should be culled."""
        from game.ui.renderer.game_renderer import draw_ship, CULLING_MAX_RADIUS

        # Position ship far off screen to the left
        mock_ship.position.x = -1000.0
        mock_ship.position.y = 500.0

        with patch('game.ui.renderer.game_renderer.ShipThemeManager'):
            with patch('game.ui.renderer.game_renderer.pygame'):
                draw_ship(mock_surface, mock_ship, mock_camera)

        # Should be culled - no drawing calls
        mock_surface.blit.assert_not_called()

    def test_ship_culled_when_off_screen_right(self, mock_surface, mock_camera, mock_ship):
        """Ships far off screen right should be culled."""
        from game.ui.renderer.game_renderer import draw_ship

        # Position ship far off screen to the right
        mock_ship.position.x = 5000.0
        mock_ship.position.y = 500.0

        with patch('game.ui.renderer.game_renderer.ShipThemeManager'):
            with patch('game.ui.renderer.game_renderer.pygame'):
                draw_ship(mock_surface, mock_ship, mock_camera)

        mock_surface.blit.assert_not_called()

    def test_ship_culled_when_off_screen_top(self, mock_surface, mock_camera, mock_ship):
        """Ships far off screen top should be culled."""
        from game.ui.renderer.game_renderer import draw_ship

        mock_ship.position.x = 500.0
        mock_ship.position.y = -1000.0

        with patch('game.ui.renderer.game_renderer.ShipThemeManager'):
            with patch('game.ui.renderer.game_renderer.pygame'):
                draw_ship(mock_surface, mock_ship, mock_camera)

        mock_surface.blit.assert_not_called()

    def test_ship_culled_when_off_screen_bottom(self, mock_surface, mock_camera, mock_ship):
        """Ships far off screen bottom should be culled."""
        from game.ui.renderer.game_renderer import draw_ship

        mock_ship.position.x = 500.0
        mock_ship.position.y = 5000.0

        with patch('game.ui.renderer.game_renderer.ShipThemeManager'):
            with patch('game.ui.renderer.game_renderer.pygame'):
                draw_ship(mock_surface, mock_ship, mock_camera)

        mock_surface.blit.assert_not_called()


class TestDrawShipRendering:
    """Tests for draw_ship rendering behavior."""

    @pytest.fixture
    def mock_surface(self):
        """Create a mock pygame surface."""
        return Mock()

    @pytest.fixture
    def mock_camera(self):
        """Create a mock camera with typical settings."""
        camera = Mock()
        camera.zoom = 1.0
        camera.width = 1920
        camera.height = 1080

        def world_to_screen(pos):
            result = Mock()
            result.x = pos.x
            result.y = pos.y
            return result
        camera.world_to_screen = world_to_screen
        camera.show_overlay = False
        return camera

    @pytest.fixture
    def mock_ship(self):
        """Create a mock ship for testing."""
        ship = Mock()
        ship.is_alive = True
        ship.position = Mock()
        ship.position.x = 500.0
        ship.position.y = 500.0
        ship.radius = 20.0
        ship.angle = 0.0
        ship.color = (100, 100, 200)
        ship.ship_class = "Destroyer"
        ship.layers = {}
        return ship

    def test_ship_image_drawn_when_available(self, mock_surface, mock_camera, mock_ship):
        """Ship image should be blitted when theme image is available."""
        from game.ui.renderer.game_renderer import draw_ship

        mock_image = Mock()
        mock_image.get_size.return_value = (64, 64)

        mock_theme_manager = Mock()
        mock_theme_manager.load_image.return_value = mock_image
        mock_theme_manager.get_image_metrics.return_value = None
        mock_theme_manager.get_manual_scale.return_value = 1.0

        mock_rotated = Mock()
        mock_rotated.get_size.return_value = (64, 64)
        mock_rotated.get_rect.return_value = Mock(center=(500, 500))

        with patch('game.ui.renderer.game_renderer.ShipThemeManager') as mock_stm:
            mock_stm.instance.return_value = mock_theme_manager
            with patch('game.ui.renderer.game_renderer.scale_and_rotate_image', return_value=mock_rotated):
                with patch('game.ui.renderer.game_renderer.calculate_ship_image_scale', return_value=1.0):
                    with patch('pygame.draw.circle'):  # Always-drawn fallback dot
                        draw_ship(mock_surface, mock_ship, mock_camera)

        # Surface.blit should have been called to draw the ship image
        mock_surface.blit.assert_called()

    def test_fallback_dot_drawn_when_no_image(self, mock_surface, mock_camera, mock_ship):
        """Fallback dot should be drawn when no theme image available."""
        from game.ui.renderer.game_renderer import draw_ship

        mock_theme_manager = Mock()
        mock_theme_manager.load_image.return_value = None

        with patch('game.ui.renderer.game_renderer.ShipThemeManager') as mock_stm:
            mock_stm.instance.return_value = mock_theme_manager
            with patch('game.ui.renderer.game_renderer.pygame') as mock_pygame:
                draw_ship(mock_surface, mock_ship, mock_camera)

        # pygame.draw.circle should have been called for fallback
        mock_pygame.draw.circle.assert_called()

    def test_no_image_at_low_zoom(self, mock_surface, mock_camera, mock_ship):
        """Ship images should not be drawn at very low zoom levels."""
        from game.ui.renderer.game_renderer import draw_ship, MIN_ZOOM_FOR_IMAGE

        # Set zoom below threshold
        mock_camera.zoom = MIN_ZOOM_FOR_IMAGE / 2

        mock_image = Mock()
        mock_image.get_size.return_value = (64, 64)

        mock_theme_manager = Mock()
        mock_theme_manager.load_image.return_value = mock_image

        with patch('game.ui.renderer.game_renderer.ShipThemeManager') as mock_stm:
            mock_stm.instance.return_value = mock_theme_manager
            with patch('game.ui.renderer.game_renderer.pygame') as mock_pygame:
                draw_ship(mock_surface, mock_ship, mock_camera)

        # Image should not be blitted, only fallback dot
        mock_surface.blit.assert_not_called()
        mock_pygame.draw.circle.assert_called()


class TestDrawShipOverlay:
    """Tests for draw_ship overlay rendering (collision circles, components)."""

    @pytest.fixture
    def mock_surface(self):
        """Create a mock pygame surface."""
        return Mock()

    @pytest.fixture
    def mock_camera(self):
        """Create a mock camera with overlay enabled."""
        camera = Mock()
        camera.zoom = 1.0
        camera.width = 1920
        camera.height = 1080

        def world_to_screen(pos):
            result = Mock()
            # Try to extract x, y from the position
            result.x = getattr(pos, 'x', 500.0)
            result.y = getattr(pos, 'y', 500.0)
            return result
        camera.world_to_screen = world_to_screen
        camera.show_overlay = True  # Enable overlay
        return camera

    @pytest.fixture
    def mock_ship_with_layers(self):
        """Create a mock ship with layer data for overlay testing."""
        from game.core.constants import LayerType
        import pygame

        ship = Mock()
        ship.is_alive = True

        # Use real Vector2 for position to handle math correctly
        ship.position = pygame.math.Vector2(500.0, 500.0)
        ship.radius = 20.0
        ship.angle = 0.0
        ship.color = (100, 100, 200)
        ship.ship_class = "Destroyer"

        # Create mock layers with components
        mock_component = Mock()
        mock_component.is_active = True
        mock_component.has_ability = Mock(return_value=False)
        mock_component.major_classification = "Electronics"

        mock_layer_data = Mock()
        mock_layer_data.components = [mock_component]

        ship.layers = {
            LayerType.CORE: mock_layer_data,
        }

        # Return real Vector2 for forward_vector to support multiplication
        ship.forward_vector = Mock(return_value=pygame.math.Vector2(1.0, 0.0))

        return ship

    def test_overlay_circles_drawn_when_enabled(self, mock_surface, mock_camera, mock_ship_with_layers):
        """Overlay circles should be drawn when show_overlay is True."""
        from game.ui.renderer.game_renderer import draw_ship

        mock_theme_manager = Mock()
        mock_theme_manager.load_image.return_value = None

        with patch('game.ui.renderer.game_renderer.ShipThemeManager') as mock_stm:
            mock_stm.instance.return_value = mock_theme_manager
            with patch('game.ui.renderer.game_renderer.pygame') as mock_pygame:
                # Need to preserve Vector2 for math operations
                import pygame
                mock_pygame.math.Vector2 = pygame.math.Vector2
                draw_ship(mock_surface, mock_ship_with_layers, mock_camera)

        # Multiple circles should be drawn for layers
        assert mock_pygame.draw.circle.call_count >= 4  # Collision + 4 layer circles

    def test_direction_line_drawn_in_overlay(self, mock_surface, mock_camera, mock_ship_with_layers):
        """Direction indicator line should be drawn in overlay mode."""
        from game.ui.renderer.game_renderer import draw_ship

        mock_theme_manager = Mock()
        mock_theme_manager.load_image.return_value = None

        with patch('game.ui.renderer.game_renderer.ShipThemeManager') as mock_stm:
            mock_stm.instance.return_value = mock_theme_manager
            with patch('game.ui.renderer.game_renderer.pygame') as mock_pygame:
                # Need to preserve Vector2 for math operations
                import pygame
                mock_pygame.math.Vector2 = pygame.math.Vector2
                draw_ship(mock_surface, mock_ship_with_layers, mock_camera)

        # Direction line should be drawn
        mock_pygame.draw.line.assert_called()
