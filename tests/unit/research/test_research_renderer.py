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
