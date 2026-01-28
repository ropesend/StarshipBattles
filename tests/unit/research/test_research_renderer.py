"""
Unit tests for ResearchRenderer.

PROJ-40/NEW-RES-002: Tests for font cache bounds and related functionality.

Note: This file is separate from test_research_scene.py to avoid issues with
the ensure_fresh_research_scene_import autouse fixture that can corrupt
pygame module state when running in parallel.

KNOWN ISSUE: These tests may fail when run as part of the full test suite
with pytest-xdist due to pygame/pygame_gui module state corruption from
test_research_controls.py mocking. They pass when run in isolation.
"""
import pytest
from unittest.mock import MagicMock
import os


def _is_running_in_xdist():
    """Check if running under pytest-xdist."""
    return os.environ.get('PYTEST_XDIST_WORKER') is not None


@pytest.fixture(autouse=True)
def reload_renderer_module():
    """Reload the renderer module before each test to ensure clean state.

    This is needed because other research tests may mock pygame_gui which
    can corrupt the module's pygame imports.
    """
    import importlib
    import game.research.ui.research_renderer as renderer_module
    importlib.reload(renderer_module)
    yield


@pytest.mark.skipif(
    _is_running_in_xdist(),
    reason="Skipped under xdist due to pygame module state corruption from other tests"
)
class TestRendererFontCacheBounds:
    """Tests for font cache bounds in ResearchRenderer.

    PROJ-40/NEW-RES-002: Font cache should not grow unbounded.
    """

    def test_font_cache_bounded_with_many_sizes(self, reload_renderer_module):
        """Font cache should not exceed reasonable size with many zoom levels.

        PROJ-40/NEW-RES-002: Requesting fonts at many different sizes
        should not create unbounded cache growth.
        """
        from game.research.ui.research_renderer import ResearchRenderer

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

    def test_font_cache_quantizes_similar_sizes(self, reload_renderer_module):
        """Similar font sizes should map to the same cached font.

        PROJ-40/NEW-RES-002: Sizes 14 and 15 should both use the same
        quantized font entry.
        """
        from game.research.ui.research_renderer import ResearchRenderer

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
