"""
Unit tests for ResearchRenderer.

PROJ-40/NEW-RES-002: Tests for font cache bounds and related functionality.
PROJ-147: Updated module path from game/research/ui to game/ui/research.

Note: This file is separate from test_research_scene.py to avoid issues with
the ensure_fresh_research_scene_import autouse fixture that can corrupt
pygame module state when running in parallel.

The renderer module is loaded directly by file path using importlib.util,
bypassing the game.ui.research package __init__.py (which imports pygame_gui
via research_scene). This makes these tests immune to pygame_gui module
state corruption from other tests mocking pygame_gui under xdist.
"""
import pytest
from unittest.mock import MagicMock
import importlib.util
from pathlib import Path


@pytest.fixture(autouse=True, scope="module")
def renderer_module():
    """Load the renderer module directly by file path, bypassing package __init__.py.

    PROJ-479 Task 2.10: scope=module — the importlib.util load is the
    expensive operation and the resulting module is read-only across the
    test suite. Session scope would be wrong (could leak into unrelated
    modules under xdist).
    """
    import pygame
    if not pygame.font.get_init():
        pygame.font.init()

    renderer_path = Path(__file__).resolve().parents[3] / "game" / "ui" / "research" / "research_renderer.py"
    spec = importlib.util.spec_from_file_location("research_renderer_isolated", str(renderer_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module


class TestRendererFontQuantization:
    """Tests for font size quantization in ResearchRenderer.

    PROJ-40/NEW-RES-002: Font sizes should be quantized to bound cache growth.
    PROJ-196: Private font cache removed - now uses central get_font().
    """

    def test_font_quantizes_similar_sizes(self, renderer_module):
        """Similar font sizes should map to the same quantized font.

        PROJ-40/NEW-RES-002: Sizes 14 and 15 should both use the same
        quantized font entry (quantization to nearest 2).
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

    # PROJ-494 T3.15 cluster 1: 9 viewport-visibility tests parametrized on
    # `(pos, expected)`. Multi-position tests (left/right/above/below/diagonal)
    # contribute one parametrize case per checked position.
    @pytest.mark.parametrize(
        "pos,expected",
        [
            # In-viewport
            pytest.param((400, 300), True, id='center'),
            pytest.param((0, 0), True, id='origin'),
            pytest.param((800, 0), True, id='top_right_corner'),
            pytest.param((0, 600), True, id='bottom_left_corner'),
            pytest.param((800, 600), True, id='bottom_right_corner'),
            # Outside left
            pytest.param((-1, 300), False, id='left_near'),
            pytest.param((-100, 300), False, id='left_far'),
            # Outside right
            pytest.param((801, 300), False, id='right_near'),
            pytest.param((1000, 300), False, id='right_far'),
            # Outside above
            pytest.param((400, -1), False, id='above_near'),
            pytest.param((400, -50), False, id='above_far'),
            # Outside below
            pytest.param((400, 601), False, id='below_near'),
            pytest.param((400, 1000), False, id='below_far'),
            # Diagonally outside
            pytest.param((-10, -10), False, id='diag_tl'),
            pytest.param((900, 700), False, id='diag_br'),
            pytest.param((-50, 700), False, id='diag_bl'),
            pytest.param((900, -50), False, id='diag_tr'),
        ],
    )
    def test_is_visible_no_margin(self, renderer_module, pos, expected):
        """_is_visible without margin correctly classifies positions inside vs outside viewport."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        assert renderer._is_visible(pos) is expected

    # --- Tests with margin ---

    # PROJ-494 T5.2: 4 directional margin tests parametrized on
    # `(near_outside_pos, far_outside_pos, margin)`. The body asserts:
    # without margin near_outside is False; with margin near_outside is True;
    # if far_outside_pos provided, with margin far_outside is False.
    # left/right originally checked the far-outside case; top/bottom did not.
    # Added symmetric far-outside cases for top/bottom (51 px past edge,
    # mirroring the left/right pattern).
    @pytest.mark.parametrize(
        "near_outside_pos,far_outside_pos,margin",
        [
            pytest.param((-10, 300), (-51, 300), 50, id='left'),
            pytest.param((810, 300), (851, 300), 50, id='right'),
            pytest.param((400, -10), (400, -51), 50, id='top'),
            pytest.param((400, 610), (400, 651), 50, id='bottom'),
        ],
    )
    def test_margin_extends_visibility_directional(
        self, renderer_module, near_outside_pos, far_outside_pos, margin
    ):
        """Margin allows partial visibility on each edge but not beyond it."""
        renderer = self._create_renderer(renderer_module, 800, 600)
        # Without margin, near_outside is not visible.
        assert renderer._is_visible(near_outside_pos, margin=0) is False
        # With margin, near_outside is visible.
        assert renderer._is_visible(near_outside_pos, margin=margin) is True
        # With margin, far_outside (beyond the margin) is still not visible.
        assert renderer._is_visible(far_outside_pos, margin=margin) is False

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
