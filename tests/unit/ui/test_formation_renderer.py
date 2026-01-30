"""Tests for FormationRenderer - extracted rendering logic from FormationEditorScreen."""

import pytest
from unittest.mock import MagicMock, patch
import pygame


@pytest.fixture
def mock_pygame():
    """Mock pygame for headless testing."""
    with patch.dict('sys.modules', {
        'pygame': MagicMock(),
        'pygame.font': MagicMock(),
    }):
        # Create a mock surface
        mock_surface = MagicMock()
        mock_surface.get_width.return_value = 1024
        mock_surface.get_height.return_value = 768
        yield mock_surface


class TestFormationRenderer:
    """Tests for FormationRenderer class."""

    @pytest.fixture
    def renderer(self):
        """Create a FormationRenderer instance for testing."""
        from game.ui.screens.formation.renderer import FormationRenderer
        return FormationRenderer(
            width=1024,
            height=768,
            toolbar_height=80
        )

    def test_init_sets_dimensions(self, renderer):
        """Renderer stores dimensions correctly."""
        assert renderer.width == 1024
        assert renderer.height == 768
        assert renderer.toolbar_height == 80

    def test_init_sets_default_colors(self, renderer):
        """Renderer has default color scheme."""
        assert renderer.col_bg == (30, 30, 40)
        assert renderer.col_grid == (45, 45, 55)
        assert renderer.col_axis == (60, 60, 70)
        assert renderer.col_arrow == (100, 200, 255)
        assert renderer.col_arrow_sel == (255, 255, 100)
        assert renderer.col_box == (100, 255, 100)

    def test_world_to_screen_origin(self, renderer):
        """World origin maps to screen center."""
        renderer.camera_zoom = 1.0
        renderer.camera_pan = [0, 0]
        sx, sy = renderer.world_to_screen(0, 0)
        expected_x = 1024 / 2  # center X
        expected_y = (768 - 80) / 2  # center Y of canvas
        assert sx == expected_x
        assert sy == expected_y

    def test_world_to_screen_with_zoom(self, renderer):
        """Zoom affects world to screen transformation."""
        renderer.camera_zoom = 2.0
        renderer.camera_pan = [0, 0]
        sx, sy = renderer.world_to_screen(100, 100)
        # At 2x zoom, 100 world units = 200 screen units from center
        center_x = 1024 / 2
        center_y = (768 - 80) / 2
        assert sx == center_x + 200
        assert sy == center_y + 200

    def test_world_to_screen_with_pan(self, renderer):
        """Pan offsets world to screen transformation."""
        renderer.camera_zoom = 1.0
        renderer.camera_pan = [50, -30]
        sx, sy = renderer.world_to_screen(0, 0)
        center_x = 1024 / 2
        center_y = (768 - 80) / 2
        assert sx == center_x + 50
        assert sy == center_y - 30

    def test_screen_to_world_inverse(self, renderer):
        """screen_to_world is inverse of world_to_screen."""
        renderer.camera_zoom = 1.5
        renderer.camera_pan = [100, -50]

        # Round trip: world -> screen -> world
        wx, wy = 150, -75
        sx, sy = renderer.world_to_screen(wx, wy)
        wx2, wy2 = renderer.screen_to_world(sx, sy)

        assert wx2 == pytest.approx(wx, abs=0.001)
        assert wy2 == pytest.approx(wy, abs=0.001)

    def test_snap_enabled(self, renderer):
        """Snap rounds to grid when enabled."""
        renderer.snap_enabled = True
        renderer.grid_size = 50

        assert renderer.snap(75) == 100
        assert renderer.snap(25) == 0
        assert renderer.snap(100) == 100

    def test_snap_disabled(self, renderer):
        """Snap returns original value when disabled."""
        renderer.snap_enabled = False
        renderer.grid_size = 50

        assert renderer.snap(75) == 75
        assert renderer.snap(25) == 25

    def test_get_canvas_rect(self, renderer):
        """Canvas rect excludes toolbar area."""
        rect = renderer.get_canvas_rect()
        assert rect.x == 0
        assert rect.y == 0
        assert rect.width == 1024
        assert rect.height == 768 - 80

    def test_handle_resize(self, renderer):
        """Resize updates dimensions and canvas rect."""
        renderer.handle_resize(1280, 1024)
        assert renderer.width == 1280
        assert renderer.height == 1024
        rect = renderer.get_canvas_rect()
        assert rect.width == 1280
        assert rect.height == 1024 - 80


class TestSelectionBounds:
    """Tests for selection bounds calculation."""

    @pytest.fixture
    def renderer(self):
        """Create a FormationRenderer instance."""
        from game.ui.screens.formation.renderer import FormationRenderer
        return FormationRenderer(width=1024, height=768, toolbar_height=80)

    def test_get_selection_bounds_empty(self, renderer):
        """No selection returns None."""
        arrows = [[0, 0], [100, 100]]
        selected = set()

        bounds = renderer.get_selection_bounds(arrows, selected)
        assert bounds is None

    def test_get_selection_bounds_single(self, renderer):
        """Single selection returns point-sized rect."""
        arrows = [[50, 75]]
        selected = {0}
        renderer.snap_enabled = False

        bounds = renderer.get_selection_bounds(arrows, selected)
        assert bounds.x == 50
        assert bounds.y == 75
        assert bounds.width == 0
        assert bounds.height == 0

    def test_get_selection_bounds_multiple(self, renderer):
        """Multiple selections return bounding box."""
        arrows = [[0, 0], [100, 50], [50, 100]]
        selected = {0, 1, 2}
        renderer.snap_enabled = False

        bounds = renderer.get_selection_bounds(arrows, selected)
        assert bounds.x == 0
        assert bounds.y == 0
        assert bounds.width == 100
        assert bounds.height == 100

    def test_get_selection_bounds_with_snap(self, renderer):
        """Selection bounds respect snap setting."""
        arrows = [[23, 37]]  # Will snap to 0, 50 with grid_size=50
        selected = {0}
        renderer.snap_enabled = True
        renderer.grid_size = 50

        bounds = renderer.get_selection_bounds(arrows, selected)
        assert bounds.x == 0  # 23 snaps to 0
        assert bounds.y == 50  # 37 snaps to 50


class TestResizeHandles:
    """Tests for resize handle calculation."""

    @pytest.fixture
    def renderer(self):
        """Create a FormationRenderer instance."""
        from game.ui.screens.formation.renderer import FormationRenderer
        renderer = FormationRenderer(width=1024, height=768, toolbar_height=80)
        renderer.camera_zoom = 1.0
        renderer.camera_pan = [0, 0]
        return renderer

    def test_get_resize_handles_none_bounds(self, renderer):
        """No bounds returns empty handles dict."""
        handles = renderer.get_resize_handles(None)
        assert handles == {}

    def test_get_resize_handles_has_corners(self, renderer):
        """Handles dict contains corner handles."""
        import pygame
        bounds = pygame.Rect(100, 100, 200, 200)
        renderer.grid_size = 50

        handles = renderer.get_resize_handles(bounds)

        assert 'TL' in handles
        assert 'TR' in handles
        assert 'BL' in handles
        assert 'BR' in handles

    def test_get_resize_handles_large_bounds_has_edges(self, renderer):
        """Large bounds include edge handles."""
        import pygame
        # Make bounds large enough for edge handles
        bounds = pygame.Rect(0, 0, 200, 200)
        renderer.grid_size = 50

        handles = renderer.get_resize_handles(bounds)

        # Edge handles appear when width/height > 40 screen units
        # With zoom=1.0, 200 world units = 200 screen units
        assert 'T' in handles
        assert 'B' in handles
        assert 'L' in handles
        assert 'R' in handles
