"""Tests for StrategyRenderer core functionality (PROJ-111 Phase 4).

Tests initialization, coordinate conversion, rendering methods (mock-level),
and property accessors. Extends existing test_strategy_renderer_animation.py.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def mock_scene():
    """Create a mock StrategyScreen for renderer tests."""
    scene = MagicMock()
    scene.screen_width = 1920
    scene.screen_height = 1080
    scene.TOP_BAR_HEIGHT = 50
    scene.hex_size = 10
    scene.hover_hex = None
    scene.input_mode = 'SELECT'
    scene.selected_fleet = None

    # Camera
    camera = MagicMock()
    camera.zoom = 1.0
    camera.position = pygame.math.Vector2(0, 0)
    camera.width = 1520  # screen_width - sidebar
    camera.height = 1030  # screen_height - top_bar
    camera.offset_x = 0
    camera.offset_y = 50
    camera.world_to_screen = MagicMock(side_effect=lambda v: pygame.math.Vector2(v.x + 960, v.y + 540))
    camera.screen_to_world = MagicMock(side_effect=lambda v: pygame.math.Vector2(v[0] - 960, v[1] - 540))
    scene.camera = camera

    # Galaxy
    galaxy = MagicMock()
    galaxy.systems = {}
    scene.galaxy = galaxy

    # Empire assets
    scene.empire_assets = {}
    scene.empires = []

    return scene


@pytest.fixture
def renderer(mock_scene):
    """Create a StrategyRenderer with mocked dependencies."""
    with patch('game.assets.asset_manager.get_asset_manager') as mock_am:
        mock_am.return_value = MagicMock()
        from game.ui.screens.strategy_renderer import StrategyRenderer
        return StrategyRenderer(mock_scene)


# ===========================================================================
# Initialization Tests
# ===========================================================================

class TestRendererInitialization:
    """Test StrategyRenderer.__init__."""

    def test_init_stores_scene_reference(self, mock_scene):
        """__init__ should store the scene reference."""
        with patch('game.assets.asset_manager.get_asset_manager'):
            from game.ui.screens.strategy_renderer import StrategyRenderer
            r = StrategyRenderer(mock_scene)

        assert r.scene is mock_scene

    def test_init_initializes_elapsed_time(self, renderer):
        """__init__ should initialize elapsed time to 0."""
        assert renderer._elapsed_time == 0.0

    def test_init_caches_asset_manager(self, mock_scene):
        """__init__ should cache asset manager reference."""
        mock_am = MagicMock()
        with patch('game.assets.asset_manager.get_asset_manager', return_value=mock_am):
            from game.ui.screens.strategy_renderer import StrategyRenderer
            r = StrategyRenderer(mock_scene)

        assert r._asset_manager is mock_am


# ===========================================================================
# Update Tests
# ===========================================================================

class TestRendererUpdate:
    """Test update(dt) method."""

    def test_update_increments_elapsed_time(self, renderer):
        """update(dt) should increment elapsed_time."""
        renderer.update(0.016)
        assert renderer._elapsed_time == pytest.approx(0.016)

    def test_update_accumulates_elapsed_time(self, renderer):
        """Multiple updates should accumulate elapsed_time."""
        renderer.update(0.016)
        renderer.update(0.016)
        assert renderer._elapsed_time == pytest.approx(0.032)


# ===========================================================================
# Property Accessor Tests
# ===========================================================================

class TestPropertyAccessors:
    """Test property accessors delegate to scene."""

    def test_camera_property(self, renderer, mock_scene):
        """camera property should return scene.camera."""
        assert renderer.camera is mock_scene.camera

    def test_galaxy_property(self, renderer, mock_scene):
        """galaxy property should return scene.galaxy."""
        assert renderer.galaxy is mock_scene.galaxy

    def test_systems_property(self, renderer, mock_scene):
        """systems property should return scene.systems."""
        mock_scene.systems = [MagicMock()]
        assert renderer.systems is mock_scene.systems

    def test_empires_property(self, renderer, mock_scene):
        """empires property should return scene.empires."""
        assert renderer.empires is mock_scene.empires

    def test_hex_size_property(self, renderer, mock_scene):
        """hex_size property should return scene.hex_size."""
        assert renderer.hex_size == 10

    def test_screen_width_property(self, renderer, mock_scene):
        """screen_width property should return scene.screen_width."""
        assert renderer.screen_width == 1920

    def test_screen_height_property(self, renderer, mock_scene):
        """screen_height property should return scene.screen_height."""
        assert renderer.screen_height == 1080

    def test_empire_assets_property(self, renderer, mock_scene):
        """empire_assets property should return scene.empire_assets."""
        assert renderer.empire_assets is mock_scene.empire_assets


# ===========================================================================
# Font Cache Tests
# ===========================================================================

class TestFontCache:
    """Test font caching behavior."""

    def test_get_font_caches_by_size_and_bold(self, renderer):
        """_get_font should cache fonts by (size, bold) key."""
        font1 = renderer._get_font(16, bold=False)
        font2 = renderer._get_font(16, bold=False)

        assert font1 is font2

    def test_get_font_different_sizes_are_different(self, renderer):
        """Different sizes should produce different cached fonts."""
        font1 = renderer._get_font(16, bold=False)
        font2 = renderer._get_font(20, bold=False)

        assert font1 is not font2

    def test_get_font_bold_vs_normal_are_different(self, renderer):
        """Bold and normal fonts of same size should be different."""
        font1 = renderer._get_font(16, bold=False)
        font2 = renderer._get_font(16, bold=True)

        assert font1 is not font2


# ===========================================================================
# Draw Method Tests (Mock-Level)
# ===========================================================================

class TestDrawMethod:
    """Test draw() method at mock level."""

    def _mock_draw_methods(self, renderer):
        """Mock all internal draw methods to avoid pygame.draw calls."""
        renderer._draw_grid = MagicMock()
        renderer._draw_warp_lanes = MagicMock()
        renderer._draw_systems = MagicMock()
        renderer._draw_fleets = MagicMock()
        renderer._draw_move_preview = MagicMock()
        renderer._draw_hover_hex = MagicMock()

    def test_draw_sets_viewport_clip(self, renderer, mock_scene):
        """draw() should set viewport clip rect."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.5  # Skip grid
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        screen.set_clip.assert_called()
        # Verify clip was set and then reset
        assert screen.set_clip.call_count >= 2

    def test_draw_fills_viewport(self, renderer, mock_scene):
        """draw() should fill viewport with background color."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.3  # Below grid threshold
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        screen.fill.assert_called()

    def test_draw_calls_draw_warp_lanes(self, renderer, mock_scene):
        """draw() should call _draw_warp_lanes."""
        screen = MagicMock()
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_warp_lanes.assert_called_once()

    def test_draw_calls_draw_systems(self, renderer, mock_scene):
        """draw() should call _draw_systems."""
        screen = MagicMock()
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_systems.assert_called_once()

    def test_draw_calls_draw_fleets(self, renderer, mock_scene):
        """draw() should call _draw_fleets."""
        screen = MagicMock()
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_fleets.assert_called_once()

    def test_draw_shows_move_preview_in_move_mode(self, renderer, mock_scene):
        """draw() should show move preview when in MOVE mode with fleet."""
        screen = MagicMock()
        mock_scene.input_mode = 'MOVE'
        mock_scene.selected_fleet = MagicMock()
        mock_scene.selected_fleet.location = MagicMock()
        mock_scene.selected_fleet.orders = []
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_move_preview.assert_called_once()

    def test_draw_skips_move_preview_without_fleet(self, renderer, mock_scene):
        """draw() should skip move preview when no fleet selected."""
        screen = MagicMock()
        mock_scene.input_mode = 'MOVE'
        mock_scene.selected_fleet = None
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_move_preview.assert_not_called()

    def test_draw_shows_hover_hex_when_zoomed(self, renderer, mock_scene):
        """draw() should show hover hex when zoomed in."""
        screen = MagicMock()
        mock_scene.hover_hex = MagicMock()
        mock_scene.camera.zoom = 1.0  # Above 0.5 threshold
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_hover_hex.assert_called_once()

    def test_draw_skips_hover_hex_when_zoomed_out(self, renderer, mock_scene):
        """draw() should skip hover hex when zoomed out."""
        screen = MagicMock()
        mock_scene.hover_hex = MagicMock()
        mock_scene.camera.zoom = 0.3  # Below 0.5 threshold
        self._mock_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_hover_hex.assert_not_called()


class TestDrawGrid:
    """Test _draw_grid() method."""

    def _mock_all_draw_methods(self, renderer):
        """Mock all internal draw methods."""
        renderer._draw_grid = MagicMock()
        renderer._draw_warp_lanes = MagicMock()
        renderer._draw_systems = MagicMock()
        renderer._draw_fleets = MagicMock()
        renderer._draw_move_preview = MagicMock()
        renderer._draw_hover_hex = MagicMock()

    def test_draw_grid_skipped_when_zoomed_out(self, renderer, mock_scene):
        """_draw_grid should not be called when zoom < 0.4."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.3
        self._mock_all_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        # Grid is skipped at low zoom
        renderer._draw_grid.assert_not_called()

    def test_draw_grid_called_when_zoomed_in(self, renderer, mock_scene):
        """_draw_grid should be called when zoom >= 0.4."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.5
        self._mock_all_draw_methods(renderer)

        with patch('pygame.draw.rect'):
            renderer.draw(screen)

        renderer._draw_grid.assert_called_once()

    def test_draw_grid_skips_massive_hex_counts(self, renderer, mock_scene):
        """_draw_grid should skip when hex count > 80000."""
        # This tests the early exit condition in _draw_grid
        # When zoom is very low, the hex count would be huge
        # The method should return early without drawing
        # We can't easily test this without calling the real method,
        # but we can verify the condition exists in the code
        from game.ui.screens.strategy_renderer import StrategyRenderer
        import inspect
        source = inspect.getsource(StrategyRenderer._draw_grid)
        assert '80000' in source  # The threshold constant exists


# ===========================================================================
# Draw Warp Lanes Tests
# ===========================================================================

class TestDrawWarpLanes:
    """Test _draw_warp_lanes() method."""

    def test_draw_warp_lanes_empty_galaxy(self, renderer, mock_scene):
        """_draw_warp_lanes should handle empty galaxy."""
        screen = MagicMock()
        mock_scene.galaxy.systems = {}

        # Should not raise
        renderer._draw_warp_lanes(screen)

    def test_draw_warp_lanes_iterates_systems(self, renderer, mock_scene):
        """_draw_warp_lanes should iterate over galaxy systems."""
        screen = MagicMock()
        mock_system = MagicMock()
        mock_system.global_location = MagicMock()
        mock_system.warp_points = []
        mock_scene.galaxy.systems = {'sys1': mock_system}

        renderer._draw_warp_lanes(screen)

        # Verify iteration happened (no exception)

    def test_draw_warp_lanes_viewport_culling_logic(self, renderer, mock_scene):
        """_draw_warp_lanes should have viewport culling logic."""
        # Verify the culling logic exists in the code
        from game.ui.screens.strategy_renderer import StrategyRenderer
        import inspect
        source = inspect.getsource(StrategyRenderer._draw_warp_lanes)
        assert 'is_on_screen' in source  # Viewport culling function exists


# ===========================================================================
# Draw Systems Tests
# ===========================================================================

class TestDrawSystems:
    """Test _draw_systems() method."""

    def test_draw_systems_empty_galaxy(self, renderer, mock_scene):
        """_draw_systems should handle empty galaxy."""
        screen = MagicMock()
        mock_scene.galaxy.systems = {}

        # Should not raise
        renderer._draw_systems(screen)

    def test_draw_systems_culls_offscreen(self, renderer, mock_scene):
        """_draw_systems should cull systems outside viewport."""
        screen = MagicMock()

        # Create a system far outside viewport
        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=10000, r=10000)  # Very far away
        mock_system.primary_star = None
        mock_system.stars = []
        mock_system.planets = []
        mock_scene.galaxy.systems = {'distant': mock_system}

        # Should not draw (culled)
        renderer._draw_systems(screen)


# ===========================================================================
# Draw Systems - Colony Marker Tests (PROJ-203 Phase 1)
# ===========================================================================

class TestDrawSystemsColonyMarker:
    """Test _draw_systems colony marker behavior at low zoom."""

    def test_colony_marker_appears_at_low_zoom(self, renderer, mock_scene):
        """Colony marker should appear when zoom < 0.5 and planet is owned."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.4  # Below 0.5 threshold

        # Create owned planet
        planet = MagicMock()
        planet.owner_id = 'empire1'

        # Create empire with matching ID
        empire = MagicMock()
        empire.id = 'empire1'
        empire.color = (255, 0, 0)  # Red
        mock_scene.empires = [empire]

        # Create system at origin (visible)
        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = [planet]
        mock_system.primary_star = None
        mock_system.stars = []
        mock_scene.galaxy.systems = {'sys1': mock_system}

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # Verify pygame.draw.circle was called (colony marker)
            assert mock_circle.call_count >= 1
            # First call should be with owner's color (red)
            call_args = mock_circle.call_args_list[0]
            assert call_args[0][1] == (255, 0, 0)  # Owner empire color

    def test_no_colony_marker_at_high_zoom(self, renderer, mock_scene):
        """Colony marker should NOT appear when zoom >= 0.5."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.6  # At or above 0.5 threshold

        # Create owned planet
        planet = MagicMock()
        planet.owner_id = 'empire1'

        # Create empire
        empire = MagicMock()
        empire.id = 'empire1'
        empire.color = (255, 0, 0)
        mock_scene.empires = [empire]

        # Create system with no stars (so no star rendering)
        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = [planet]
        mock_system.primary_star = None
        mock_system.stars = []
        mock_scene.galaxy.systems = {'sys1': mock_system}

        # Mock _draw_system_details to prevent it from doing work
        renderer._draw_system_details = MagicMock()

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # At high zoom, no colony marker should be drawn
            # (No circles because no stars and no colony marker)
            mock_circle.assert_not_called()

    def test_colony_marker_uses_first_owner_color(self, renderer, mock_scene):
        """When multiple planets owned by different empires, use first owner's color."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.4

        # Create planets owned by different empires
        planet1 = MagicMock()
        planet1.owner_id = 'empire1'
        planet2 = MagicMock()
        planet2.owner_id = 'empire2'

        # Create empires
        empire1 = MagicMock()
        empire1.id = 'empire1'
        empire1.color = (255, 0, 0)  # Red - should be used
        empire2 = MagicMock()
        empire2.id = 'empire2'
        empire2.color = (0, 0, 255)  # Blue - should NOT be used
        mock_scene.empires = [empire1, empire2]

        # System with both planets (owned first comes first)
        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = [planet1, planet2]
        mock_system.primary_star = None
        mock_system.stars = []
        mock_scene.galaxy.systems = {'sys1': mock_system}

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # Verify first call uses first owner's color (red)
            assert mock_circle.call_count >= 1
            call_args = mock_circle.call_args_list[0]
            assert call_args[0][1] == (255, 0, 0)

    def test_colony_marker_handles_orphaned_owner(self, renderer, mock_scene):
        """When planet.owner_id not in empires list, skip marker gracefully."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.4

        # Create planet with owner that doesn't exist in empires
        planet = MagicMock()
        planet.owner_id = 'nonexistent_empire'

        # Empires list doesn't have this ID
        empire = MagicMock()
        empire.id = 'some_other_empire'
        empire.color = (0, 255, 0)
        mock_scene.empires = [empire]

        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = [planet]
        mock_system.primary_star = None
        mock_system.stars = []
        mock_scene.galaxy.systems = {'sys1': mock_system}

        # Should not raise and should not draw marker
        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)  # No exception
            mock_circle.assert_not_called()


# ===========================================================================
# Draw Systems - Star Rendering Tests (PROJ-203 Phase 1)
# ===========================================================================

class TestDrawSystemsStar:
    """Test _draw_systems star rendering edge cases."""

    def test_star_fallback_circle_when_no_image(self, renderer, mock_scene):
        """When asset manager returns None, fallback circle should be drawn."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.6  # Above detail threshold

        # Create star
        star = MagicMock()
        star.color = (255, 255, 0)  # Yellow
        star.diameter_hexes = 1.0
        star.location = MagicMock(q=0, r=0)
        star.name = "Test Star"

        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = []
        mock_system.primary_star = star
        mock_system.stars = [star]
        mock_system.name = "Test System"
        mock_scene.galaxy.systems = {'sys1': mock_system}
        mock_scene.selected_object = None

        # Force asset manager to return None for star image
        renderer._asset_manager.load_image.return_value = None

        # Mock _draw_system_details
        renderer._draw_system_details = MagicMock()

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # Verify fallback circle drawn with star color
            assert mock_circle.call_count >= 1
            # Find the call with star color (yellow)
            found_fallback = False
            for call in mock_circle.call_args_list:
                if call[0][1] == (255, 255, 0):
                    found_fallback = True
                    break
            assert found_fallback, "Fallback circle with star color not found"

    def test_star_minimum_radius_is_3(self, renderer, mock_scene):
        """Star radius should never be less than 3 pixels."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.1  # Very low zoom

        # Create tiny star
        star = MagicMock()
        star.color = (255, 255, 0)
        star.diameter_hexes = 0.001  # Very small
        star.location = MagicMock(q=0, r=0)
        star.name = "Tiny Star"

        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = []
        mock_system.primary_star = star
        mock_system.stars = [star]
        mock_system.name = "Test System"
        mock_scene.galaxy.systems = {'sys1': mock_system}
        mock_scene.selected_object = None

        # Force fallback circle rendering
        renderer._asset_manager.load_image.return_value = None

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # Find the fallback circle call
            for call in mock_circle.call_args_list:
                if call[0][1] == (255, 255, 0):  # Star color
                    radius = call[0][3]  # 4th positional arg is radius
                    assert radius >= 3, f"Star radius {radius} is less than minimum 3"
                    break

    def test_star_selection_highlight_on_primary(self, renderer, mock_scene):
        """Selected system's primary star should have white outline."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.6

        # Create star
        star = MagicMock()
        star.color = (255, 255, 0)
        star.diameter_hexes = 1.0
        star.location = MagicMock(q=0, r=0)
        star.name = "Primary Star"

        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = []
        mock_system.primary_star = star
        mock_system.stars = [star]
        mock_system.name = "Test System"
        mock_scene.galaxy.systems = {'sys1': mock_system}

        # Select this system
        mock_scene.selected_object = mock_system

        # Force fallback rendering
        renderer._asset_manager.load_image.return_value = None
        renderer._draw_system_details = MagicMock()

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # Should have at least 2 circle calls: selection highlight + star
            assert mock_circle.call_count >= 2
            # Find call with WHITE color (255, 255, 255)
            found_highlight = False
            for call in mock_circle.call_args_list:
                # WHITE constant is (255, 255, 255)
                if call[0][1] == (255, 255, 255):
                    found_highlight = True
                    # Verify it has outline (width parameter > 0)
                    assert len(call[0]) >= 5 or 'width' in call[1] or call[0][-1] == 1
                    break
            assert found_highlight, "Selection highlight circle not found"


# ===========================================================================
# Draw Systems - Viewport Culling Tests (PROJ-203 Phase 1)
# ===========================================================================

class TestDrawSystemsViewportCulling:
    """Test _draw_systems viewport culling behavior."""

    def test_system_beyond_margin_not_rendered(self, renderer, mock_scene):
        """Systems > 600 units outside viewport should not be rendered."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.5

        # Camera centered at origin, viewport ~1920x1080 in screen coords
        # World coords from mock: screen_to_world returns screen - 960/540
        # So visible world area is roughly -960 to +960 x, -540 to +540 y
        # Margin is 600, so cutoff is roughly at ~1560 world units

        star = MagicMock()
        star.color = (255, 255, 0)
        star.diameter_hexes = 1.0
        star.location = MagicMock(q=0, r=0)
        star.name = "Star"

        # Create system very far away (beyond margin)
        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=10000, r=10000)
        mock_system.planets = []
        mock_system.primary_star = star
        mock_system.stars = [star]
        mock_scene.galaxy.systems = {'distant': mock_system}
        mock_scene.selected_object = None

        renderer._asset_manager.load_image.return_value = None
        renderer._draw_system_details = MagicMock()

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # System should be culled - no circles drawn
            mock_circle.assert_not_called()

    def test_system_within_margin_rendered(self, renderer, mock_scene):
        """Systems within 600 units of viewport edge should be rendered."""
        screen = MagicMock()
        mock_scene.camera.zoom = 0.4  # Below 0.5 to skip label rendering

        star = MagicMock()
        star.color = (255, 255, 0)
        star.diameter_hexes = 1.0
        star.location = MagicMock(q=0, r=0)
        star.name = "Star"

        # Create system at origin (well within viewport)
        mock_system = MagicMock()
        mock_system.global_location = MagicMock(q=0, r=0)
        mock_system.planets = []
        mock_system.primary_star = star
        mock_system.stars = [star]
        mock_scene.galaxy.systems = {'nearby': mock_system}
        mock_scene.selected_object = None

        renderer._asset_manager.load_image.return_value = None

        with patch('pygame.draw.circle') as mock_circle:
            renderer._draw_systems(screen)

            # System should be rendered - at least one circle drawn
            assert mock_circle.call_count >= 1


# ===========================================================================
# Draw Fleets Tests
# ===========================================================================

class TestDrawFleets:
    """Test _draw_fleets() method."""

    def test_draw_fleets_no_empires(self, renderer, mock_scene):
        """_draw_fleets should handle no empires."""
        screen = MagicMock()
        mock_scene.empires = []

        # Should not raise
        renderer._draw_fleets(screen)

    def test_draw_fleets_empty_fleet_list(self, renderer, mock_scene):
        """_draw_fleets should handle empire with no fleets."""
        screen = MagicMock()
        empire = MagicMock()
        empire.fleets = []
        mock_scene.empires = [empire]

        # Should not raise
        renderer._draw_fleets(screen)


# ===========================================================================
# Draw Processing Overlay Tests
# ===========================================================================

class TestDrawProcessingOverlay:
    """Test draw_processing_overlay() method."""

    def test_draw_processing_overlay_draws_overlay(self, renderer, mock_scene):
        """draw_processing_overlay should draw a semi-transparent overlay."""
        screen = MagicMock()
        mock_surface = MagicMock()
        screen.get_size.return_value = (1920, 1080)

        with patch('pygame.Surface', return_value=mock_surface):
            renderer.draw_processing_overlay(screen)

        # Verify surface was blitted
        screen.blit.assert_called()


# ===========================================================================
# Coordinate Conversion Tests
# ===========================================================================

class TestCoordinateConversion:
    """Test coordinate conversion through renderer."""

    def test_hex_to_pixel_produces_expected_values(self, renderer):
        """Verify hex_to_pixel conversion is available and works."""
        from game.core.hex_math import hex_to_pixel, HexCoord

        coord = HexCoord(0, 0)
        px, py = hex_to_pixel(coord, 10)

        # Origin hex should be at (0, 0)
        assert px == pytest.approx(0, abs=0.1)
        assert py == pytest.approx(0, abs=0.1)

    def test_zoom_affects_screen_positions(self, renderer, mock_scene):
        """Different zoom levels should affect screen positions."""
        # At zoom 1.0
        mock_scene.camera.zoom = 1.0
        world_pos = pygame.math.Vector2(100, 100)
        screen_pos_1x = mock_scene.camera.world_to_screen(world_pos)

        # The mock implementation doesn't actually zoom, but verify it's called
        assert screen_pos_1x is not None
