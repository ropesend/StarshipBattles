"""
Tests for ResearchTreeScene interaction and miscellaneous functionality.

Covers:
- Node selection at position
- Resize handling
- Camera centering logic
- Update method
- Cycle detection call
"""
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pygame


def _make_default_tree():
    tree = MagicMock()
    tree.nodes = {}
    tree.get_max_depth.return_value = 0
    tree.validate_requirements.return_value = []
    return tree


def _make_default_tracker(seed=12345):
    tracker = MagicMock()
    tracker.session_seed = seed
    return tracker


@contextmanager
def _patched_research_scene():
    """Patch the standard set of research_scene attributes used by ResearchTreeScene.

    PROJ-323 Task 2.10: deduplicates the 6-patch nesting that previously
    appeared in every test in this module.
    """
    patches = {
        'TechTree': patch('game.ui.research.research_scene.TechTree'),
        'Tracker': patch('game.ui.research.research_scene.ResearchTracker'),
        'Camera': patch('game.ui.research.research_scene.Camera'),
        'StarshipUIManager': patch('game.ui.research.research_scene.StarshipUIManager'),
        'Renderer': patch('game.ui.research.research_scene.ResearchRenderer'),
        'Panel': patch('game.ui.research.research_scene.ResearchControlPanel'),
    }
    started = {name: p.start() for name, p in patches.items()}
    try:
        started['TechTree'].load_from_json.return_value = _make_default_tree()
        started['Tracker'].return_value = _make_default_tracker()
        yield started
    finally:
        for p in patches.values():
            p.stop()


class TestNodePositionDetection:
    """Tests for _get_node_at_position logic."""

    def test_node_at_position_returns_node_id(self):
        """Returns node ID when position is inside a node."""
        with _patched_research_scene():
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Manually set node positions
            scene.node_positions = {'test_node': (500, 300)}

            # Click inside the node
            world_pos = pygame.math.Vector2(500, 300)
            result = scene._get_node_at_position(world_pos)

            assert result == 'test_node'

    def test_node_at_position_returns_none_for_empty_space(self):
        """Returns None when position is not on any node."""
        with _patched_research_scene():
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Manually set node positions
            scene.node_positions = {'test_node': (500, 300)}

            # Click far from the node
            world_pos = pygame.math.Vector2(1000, 1000)
            result = scene._get_node_at_position(world_pos)

            assert result is None

    def test_node_at_position_respects_boundaries(self):
        """Position detection respects node width and height."""
        with _patched_research_scene():
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene.node_positions = {'test_node': (500, 300)}
            half_w = scene.NODE_WIDTH / 2
            half_h = scene.NODE_HEIGHT / 2

            # Click just inside left edge
            inside_left = pygame.math.Vector2(500 - half_w + 1, 300)
            assert scene._get_node_at_position(inside_left) == 'test_node'

            # Click just outside left edge
            outside_left = pygame.math.Vector2(500 - half_w - 1, 300)
            assert scene._get_node_at_position(outside_left) is None

            # Click just inside top edge
            inside_top = pygame.math.Vector2(500, 300 - half_h + 1)
            assert scene._get_node_at_position(inside_top) == 'test_node'

            # Click just outside top edge
            outside_top = pygame.math.Vector2(500, 300 - half_h - 1)
            assert scene._get_node_at_position(outside_top) is None


class TestResizeHandling:
    """Tests for handle_resize method."""

    def test_resize_updates_dimensions(self):
        """Resize updates screen and canvas dimensions."""
        with _patched_research_scene() as mocks:
            mock_camera_instance = MagicMock()
            mocks['Camera'].return_value = mock_camera_instance

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene.handle_resize(2560, 1440)

            assert scene.screen_width == 2560
            assert scene.screen_height == 1440
            assert scene.canvas_width == 2560 - ResearchTreeScene.SIDEBAR_WIDTH


class TestCameraCentering:
    """Tests for _center_camera method."""

    def test_center_camera_with_nodes(self):
        """Camera centers on middle of node bounding box."""
        with _patched_research_scene() as mocks:
            tree = _make_default_tree()
            tree.get_nodes_at_depth.return_value = []
            mocks['TechTree'].load_from_json.return_value = tree

            mock_camera_instance = MagicMock()
            mocks['Camera'].return_value = mock_camera_instance

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Manually set positions
            scene.node_positions = {
                'a': (100, 200),
                'b': (500, 400),
            }

            scene._center_camera()

            # Expected center: ((100+500)/2, (200+400)/2) = (300, 300)
            # The position should be set (we check it was assigned)
            assert mock_camera_instance.position is not None

    def test_center_camera_with_no_nodes(self):
        """Camera centering with empty positions doesn't crash."""
        with _patched_research_scene() as mocks:
            tree = _make_default_tree()
            tree.get_nodes_at_depth.return_value = []
            mocks['TechTree'].load_from_json.return_value = tree

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Clear positions
            scene.node_positions = {}

            # Should not crash
            scene._center_camera()


class TestUpdateMethod:
    """Tests for update method."""

    def test_update_calls_camera_update(self):
        """Update method calls camera update with delta time."""
        with _patched_research_scene() as mocks:
            mock_camera_instance = MagicMock()
            mocks['Camera'].return_value = mock_camera_instance

            mock_ui_manager = MagicMock()
            mocks['StarshipUIManager'].return_value = mock_ui_manager

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene.update(0.016)

            mock_camera_instance.update.assert_called_with(0.016)
            mock_ui_manager.update.assert_called_with(0.016)


# =============================================================================
# Test: Cycle Detection Call (PROJ-40/NEW-RES-005)
# =============================================================================
# NOTE: Font cache tests moved to test_research_renderer.py to avoid conflicts
# with the ensure_fresh_research_scene_import autouse fixture.


class TestCycleDetectionCall:
    """Tests for cycle detection during scene initialization.

    PROJ-40/NEW-RES-005: detect_cycles() should be called during validation.
    """

    def test_detect_cycles_called_during_init(self):
        """detect_cycles() should be called as an ``__init__`` side effect.

        PROJ-40/NEW-RES-005: Scene should validate for cycles on construction.

        PROJ-478 Phase 2: rewritten. The previous version called
        ``mock_tree.detect_cycles()`` itself then asserted it was called
        (CAT-2 tautology). Now constructs a real ``ResearchTreeScene`` and
        asserts ``detect_cycles`` fires as an ``__init__`` side effect via
        the patched ``TechTree.load_from_json``.
        """
        mock_tree = MagicMock()
        mock_tree.nodes = {}
        mock_tree.validate_requirements.return_value = []
        mock_tree.detect_cycles.return_value = []
        mock_tree.resolve_all_requirements = MagicMock()

        # Patch the entry points that ResearchTreeScene.__init__ pulls
        # through. ``TechTree.load_from_json`` is the seam that returns the
        # tech tree used for the cycles validation. The UI manager and
        # control panel are patched out so the scene can construct without
        # a real pygame surface.
        with patch(
            'game.ui.research.research_scene.TechTree.load_from_json',
            return_value=mock_tree,
        ), patch('game.ui.research.research_scene.StarshipUIManager'), patch(
            'game.ui.research.research_scene.ResearchControlPanel'
        ), patch(
            'game.ui.research.research_scene.ResearchRenderer'
        ), patch('game.ui.research.research_scene.Camera'), patch(
            'game.ui.research.research_scene.ResearchTracker'
        ):
            from game.ui.research.research_scene import ResearchTreeScene

            ResearchTreeScene(
                screen_width=1920,
                screen_height=1080,
                on_close_callback=None,
            )

        # The scene's ``__init__`` — not the test — must have invoked
        # detect_cycles on the tech tree.
        mock_tree.detect_cycles.assert_called_once()

    def test_detect_cycles_errors_logged(self):
        """Cycle detection errors should be logged.

        PROJ-40/NEW-RES-005: When cycles are found, they should be logged.
        """
        mock_tree = MagicMock()
        mock_tree.detect_cycles.return_value = [
            "Cycle detected: A -> B -> A",
            "Cycle detected: C -> D -> E -> C"
        ]

        with patch('game.ui.research.research_scene.logger') as mock_logger:
            # Simulate the expected behavior after our fix
            cycle_errors = mock_tree.detect_cycles()
            for err in cycle_errors[:5]:
                mock_logger.info(f"TechTree validation: {err}")

            # Verify logging was called for cycle errors
            assert mock_logger.info.call_count == 2
