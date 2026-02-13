"""
Unit tests for ResearchRenderer.

PROJ-40/NEW-RES-002: Tests for font cache bounds and related functionality.

Note: This file is separate from test_research_scene.py to avoid issues with
the ensure_fresh_research_scene_import autouse fixture that can corrupt
pygame module state when running in parallel.

The renderer module is loaded directly by file path using importlib.util,
bypassing the game.research.ui package __init__.py (which imports pygame_gui
via research_scene). This makes these tests immune to pygame_gui module
state corruption from other tests mocking pygame_gui under xdist.
"""
import pytest
from unittest.mock import MagicMock
import importlib.util
from pathlib import Path


@pytest.fixture(autouse=True)
def renderer_module():
    """Load the renderer module directly by file path, bypassing package __init__.py.

    This uses importlib.util.spec_from_file_location to load research_renderer.py
    without triggering game.research.ui.__init__ (which imports research_scene,
    which imports pygame_gui). This avoids pygame_gui corruption under xdist.
    """
    import pygame
    if not pygame.font.get_init():
        pygame.font.init()

    renderer_path = Path(__file__).resolve().parents[3] / "game" / "research" / "ui" / "research_renderer.py"
    spec = importlib.util.spec_from_file_location("research_renderer_isolated", str(renderer_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module


class TestRendererFontCacheBounds:
    """Tests for font cache bounds in ResearchRenderer.

    PROJ-40/NEW-RES-002: Font cache should not grow unbounded.
    """

    def test_font_cache_bounded_with_many_sizes(self, renderer_module):
        """Font cache should not exceed reasonable size with many zoom levels.

        PROJ-40/NEW-RES-002: Requesting fonts at many different sizes
        should not create unbounded cache growth.
        """
        ResearchRenderer = renderer_module.ResearchRenderer

        # Create minimal mocks
        mock_tree = MagicMock()
        mock_tree.nodes = {}
        mock_tracker = MagicMock()
        mock_camera = MagicMock()
        mock_camera.zoom = 1.0

        renderer = ResearchRenderer(
            tech_tree=mock_tree,
            tracker=mock_tracker,
            node_positions={},
            camera=mock_camera,
            node_width=100,
            node_height=60
        )

        # Request fonts at many different sizes (simulating continuous zoom)
        for i in range(1, 200):
            renderer._get_font(i)

        # Cache should be bounded (quantization limits unique entries)
        # With quantization to nearest 2, max would be ~100 entries
        assert len(renderer._font_cache) <= 100, \
            f"Font cache grew to {len(renderer._font_cache)} entries, should be bounded"

    def test_font_cache_quantizes_similar_sizes(self, renderer_module):
        """Similar font sizes should map to the same cached font.

        PROJ-40/NEW-RES-002: Sizes 14 and 15 should both use the same
        quantized font entry.
        """
        ResearchRenderer = renderer_module.ResearchRenderer

        mock_tree = MagicMock()
        mock_tree.nodes = {}
        mock_tracker = MagicMock()
        mock_camera = MagicMock()

        renderer = ResearchRenderer(
            tech_tree=mock_tree,
            tracker=mock_tracker,
            node_positions={},
            camera=mock_camera,
            node_width=100,
            node_height=60
        )

        # Request fonts at adjacent sizes
        font1 = renderer._get_font(14)
        font2 = renderer._get_font(15)

        # With quantization, these should be the same font object
        assert font1 is font2, "Adjacent sizes should use same quantized font"


# =============================================================================
# TCG-FND-011: ResearchRenderer._is_visible() Pure Function Tests
# =============================================================================

class TestRendererIsVisible:
    """TCG-FND-011: Tests for the _is_visible() pure function.

    The _is_visible method determines if a screen position is within the
    camera viewport with optional margin for partial visibility.
    """

    def _create_renderer(self, renderer_module, camera_width=800, camera_height=600):
        """Helper to create a renderer with a mock camera of given dimensions."""
        ResearchRenderer = renderer_module.ResearchRenderer

        mock_tree = MagicMock()
        mock_tree.nodes = {}
        mock_tracker = MagicMock()
        mock_camera = MagicMock()
        mock_camera.zoom = 1.0
        mock_camera.width = camera_width
        mock_camera.height = camera_height

        return ResearchRenderer(
            tech_tree=mock_tree,
            tracker=mock_tracker,
            node_positions={},
            camera=mock_camera,
            node_width=100,
            node_height=60
        )

    # --- Tests for positions within viewport ---

    def test_center_of_viewport_is_visible(self, renderer_module):
        """Position at center of viewport should be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((400, 300)) is True

    def test_origin_is_visible(self, renderer_module):
        """Position at (0, 0) should be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((0, 0)) is True

    def test_top_right_corner_is_visible(self, renderer_module):
        """Position at top-right corner should be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((800, 0)) is True

    def test_bottom_left_corner_is_visible(self, renderer_module):
        """Position at bottom-left corner should be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((0, 600)) is True

    def test_bottom_right_corner_is_visible(self, renderer_module):
        """Position at bottom-right corner should be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((800, 600)) is True

    # --- Tests for positions outside viewport ---

    def test_position_left_of_viewport_not_visible(self, renderer_module):
        """Position left of viewport (negative x) should not be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((-1, 300)) is False
        assert renderer._is_visible((-100, 300)) is False

    def test_position_right_of_viewport_not_visible(self, renderer_module):
        """Position right of viewport should not be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((801, 300)) is False
        assert renderer._is_visible((1000, 300)) is False

    def test_position_above_viewport_not_visible(self, renderer_module):
        """Position above viewport (negative y) should not be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((400, -1)) is False
        assert renderer._is_visible((400, -50)) is False

    def test_position_below_viewport_not_visible(self, renderer_module):
        """Position below viewport should not be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((400, 601)) is False
        assert renderer._is_visible((400, 1000)) is False

    def test_position_diagonally_outside_not_visible(self, renderer_module):
        """Positions diagonally outside viewport corners should not be visible."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((-10, -10)) is False
        assert renderer._is_visible((900, 700)) is False
        assert renderer._is_visible((-50, 700)) is False
        assert renderer._is_visible((900, -50)) is False

    # --- Tests with margin ---

    def test_margin_extends_visibility_left(self, renderer_module):
        """Margin should allow partial visibility on the left edge."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        # Without margin, -10 is not visible
        assert renderer._is_visible((-10, 300), margin=0) is False
        # With margin of 50, -10 should be visible
        assert renderer._is_visible((-10, 300), margin=50) is True
        # But -51 should still not be visible
        assert renderer._is_visible((-51, 300), margin=50) is False

    def test_margin_extends_visibility_right(self, renderer_module):
        """Margin should allow partial visibility on the right edge."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        # Without margin, 810 is not visible
        assert renderer._is_visible((810, 300), margin=0) is False
        # With margin of 50, 810 should be visible
        assert renderer._is_visible((810, 300), margin=50) is True
        # But 851 should still not be visible
        assert renderer._is_visible((851, 300), margin=50) is False

    def test_margin_extends_visibility_top(self, renderer_module):
        """Margin should allow partial visibility on the top edge."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        # Without margin, -10 y is not visible
        assert renderer._is_visible((400, -10), margin=0) is False
        # With margin of 50, -10 y should be visible
        assert renderer._is_visible((400, -10), margin=50) is True

    def test_margin_extends_visibility_bottom(self, renderer_module):
        """Margin should allow partial visibility on the bottom edge."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        # Without margin, 610 y is not visible
        assert renderer._is_visible((400, 610), margin=0) is False
        # With margin of 50, 610 y should be visible
        assert renderer._is_visible((400, 610), margin=50) is True

    def test_margin_extends_visibility_all_corners(self, renderer_module):
        """Margin should extend visibility in all directions."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        margin = 100

        # Positions just outside each corner that should be visible with margin
        assert renderer._is_visible((-50, -50), margin=margin) is True
        assert renderer._is_visible((850, -50), margin=margin) is True
        assert renderer._is_visible((-50, 650), margin=margin) is True
        assert renderer._is_visible((850, 650), margin=margin) is True

    def test_zero_margin_is_exact_bounds(self, renderer_module):
        """Zero margin should give exact viewport bounds."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        # Exact bounds
        assert renderer._is_visible((0, 0), margin=0) is True
        assert renderer._is_visible((800, 600), margin=0) is True
        # Just outside
        assert renderer._is_visible((-0.001, 300), margin=0) is False
        assert renderer._is_visible((800.001, 300), margin=0) is False

    def test_large_margin_includes_far_positions(self, renderer_module):
        """Large margin should include positions far outside viewport."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        margin = 1000

        assert renderer._is_visible((-500, 300), margin=margin) is True
        assert renderer._is_visible((1300, 300), margin=margin) is True
        assert renderer._is_visible((400, -500), margin=margin) is True
        assert renderer._is_visible((400, 1100), margin=margin) is True

    # --- Edge cases ---

    def test_float_coordinates_work(self, renderer_module):
        """Float coordinates should work correctly."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible((400.5, 300.5)) is True
        assert renderer._is_visible((0.0, 0.0)) is True
        assert renderer._is_visible((799.99, 599.99)) is True

    def test_different_viewport_sizes(self, renderer_module):
        """Different viewport sizes should be handled correctly."""
        # Small viewport
        small_renderer = self._create_renderer(renderer_module, 100, 100)
        assert small_renderer._is_visible((50, 50)) is True
        assert small_renderer._is_visible((101, 50)) is False

        # Large viewport
        large_renderer = self._create_renderer(renderer_module, 1920, 1080)
        assert large_renderer._is_visible((960, 540)) is True
        assert large_renderer._is_visible((1921, 540)) is False
