"""
Tests for ResearchTreeScene initialization and layout.

Covers:
- Scene initialization and configuration
- Node layout calculation
- Layout constants
"""
from contextlib import contextmanager
from unittest.mock import MagicMock, patch


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
    """Patch the standard set of research_scene attributes used by ResearchTreeScene."""
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
        # Set defaults; tests may override before instantiating ResearchTreeScene
        started['TechTree'].load_from_json.return_value = _make_default_tree()
        started['Tracker'].return_value = _make_default_tracker()
        yield started
    finally:
        for p in patches.values():
            p.stop()


class TestResearchTreeSceneInitialization:
    """Tests for scene initialization."""

    def test_scene_stores_dimensions(self):
        """Scene stores screen dimensions."""
        with _patched_research_scene():
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            assert scene.screen_width == 1920
            assert scene.screen_height == 1080

    def test_canvas_width_excludes_sidebar(self):
        """Canvas width is screen width minus sidebar."""
        with _patched_research_scene():
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            expected_canvas_width = 1920 - ResearchTreeScene.SIDEBAR_WIDTH
            assert scene.canvas_width == expected_canvas_width

    def test_callback_stored(self):
        """Close callback is stored."""
        with _patched_research_scene():
            callback = MagicMock()
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080, on_close_callback=callback)

            assert scene.on_close_callback is callback

    def test_tech_tree_loaded(self):
        """Tech tree is loaded on initialization."""
        with _patched_research_scene() as mocks:
            tree = _make_default_tree()
            mocks['TechTree'].load_from_json.return_value = tree

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            mocks['TechTree'].load_from_json.assert_called_once()
            assert scene.tech_tree is tree

    def test_fuzzy_requirements_resolved(self):
        """Fuzzy requirements are resolved with tracker seed."""
        with _patched_research_scene() as mocks:
            tree = _make_default_tree()
            mocks['TechTree'].load_from_json.return_value = tree

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            tree.resolve_all_requirements.assert_called_once_with(12345)


class TestLayoutCalculation:
    """Tests for node layout calculation logic."""

    def test_layout_calculates_positions_for_all_nodes(self):
        """Layout calculation creates positions for all nodes."""
        with _patched_research_scene() as mocks:
            node_a = MagicMock(); node_a.id = 'node_a'; node_a.name = 'Alpha'
            node_b = MagicMock(); node_b.id = 'node_b'; node_b.name = 'Beta'

            tree = _make_default_tree()
            tree.nodes = {'node_a': node_a, 'node_b': node_b}
            tree.get_max_depth.return_value = 1
            tree.get_nodes_at_depth.side_effect = [[node_a], [node_b]]
            mocks['TechTree'].load_from_json.return_value = tree

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            assert 'node_a' in scene.node_positions
            assert 'node_b' in scene.node_positions

    def test_layout_positions_nodes_by_depth(self):
        """Nodes at different depths have different x positions."""
        with _patched_research_scene() as mocks:
            node_a = MagicMock(); node_a.id = 'node_a'; node_a.name = 'Alpha'
            node_b = MagicMock(); node_b.id = 'node_b'; node_b.name = 'Beta'

            tree = _make_default_tree()
            tree.nodes = {'node_a': node_a, 'node_b': node_b}
            tree.get_max_depth.return_value = 1
            tree.get_nodes_at_depth.side_effect = [[node_a], [node_b]]
            mocks['TechTree'].load_from_json.return_value = tree

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            x_a = scene.node_positions['node_a'][0]
            x_b = scene.node_positions['node_b'][0]

            # depth 1 should be further right than depth 0
            assert x_b > x_a
            # Position difference should be COLUMN_SPACING
            assert x_b - x_a == ResearchTreeScene.COLUMN_SPACING

    def test_layout_sorts_nodes_alphabetically(self):
        """Nodes at same depth are sorted alphabetically by name."""
        with _patched_research_scene() as mocks:
            node_z = MagicMock(); node_z.id = 'node_z'; node_z.name = 'Zeta'
            node_a = MagicMock(); node_a.id = 'node_a'; node_a.name = 'Alpha'

            tree = _make_default_tree()
            tree.nodes = {'node_z': node_z, 'node_a': node_a}
            tree.get_max_depth.return_value = 0
            # Return in reverse alphabetical order - should be sorted
            tree.get_nodes_at_depth.return_value = [node_z, node_a]
            mocks['TechTree'].load_from_json.return_value = tree

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Alpha should be above Zeta (lower y)
            y_a = scene.node_positions['node_a'][1]
            y_z = scene.node_positions['node_z'][1]
            assert y_a < y_z
