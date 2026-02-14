"""
Tests for ResearchTreeScene initialization and layout.

Covers:
- Scene initialization and configuration
- Node layout calculation
- Layout constants
"""
import pytest
from unittest.mock import MagicMock, patch


class TestResearchTreeSceneInitialization:
    """Tests for scene initialization."""

    def test_scene_stores_dimensions(self):
        """Scene stores screen dimensions."""
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            # Setup mocks
            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            assert scene.screen_width == 1920
            assert scene.screen_height == 1080

    def test_canvas_width_excludes_sidebar(self):
        """Canvas width is screen width minus sidebar."""
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            expected_canvas_width = 1920 - ResearchTreeScene.SIDEBAR_WIDTH
            assert scene.canvas_width == expected_canvas_width

    def test_callback_stored(self):
        """Close callback is stored."""
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            callback = MagicMock()
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080, on_close_callback=callback)

            assert scene.on_close_callback is callback

    def test_tech_tree_loaded(self):
        """Tech tree is loaded on initialization."""
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            MockTechTree.load_from_json.assert_called_once()
            assert scene.tech_tree is mock_tree

    def test_fuzzy_requirements_resolved(self):
        """Fuzzy requirements are resolved with tracker seed."""
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            mock_tree.resolve_all_requirements.assert_called_once_with(12345)


class TestLayoutCalculation:
    """Tests for node layout calculation logic."""

    def test_layout_calculates_positions_for_all_nodes(self):
        """Layout calculation creates positions for all nodes."""
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            # Create mock nodes
            node_a = MagicMock()
            node_a.id = 'node_a'
            node_a.name = 'Alpha'

            node_b = MagicMock()
            node_b.id = 'node_b'
            node_b.name = 'Beta'

            mock_tree = MagicMock()
            mock_tree.nodes = {'node_a': node_a, 'node_b': node_b}
            mock_tree.get_max_depth.return_value = 1
            mock_tree.get_nodes_at_depth.side_effect = [
                [node_a],  # depth 0
                [node_b],  # depth 1
            ]
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            assert 'node_a' in scene.node_positions
            assert 'node_b' in scene.node_positions

    def test_layout_positions_nodes_by_depth(self):
        """Nodes at different depths have different x positions."""
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            node_a = MagicMock()
            node_a.id = 'node_a'
            node_a.name = 'Alpha'

            node_b = MagicMock()
            node_b.id = 'node_b'
            node_b.name = 'Beta'

            mock_tree = MagicMock()
            mock_tree.nodes = {'node_a': node_a, 'node_b': node_b}
            mock_tree.get_max_depth.return_value = 1
            mock_tree.get_nodes_at_depth.side_effect = [
                [node_a],  # depth 0
                [node_b],  # depth 1
            ]
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

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
        with patch('game.ui.research.research_scene.TechTree') as MockTechTree, \
             patch('game.ui.research.research_scene.ResearchTracker') as MockTracker, \
             patch('game.ui.research.research_scene.Camera'), \
             patch('game.ui.research.research_scene.pygame_gui'), \
             patch('game.ui.research.research_scene.ResearchRenderer'), \
             patch('game.ui.research.research_scene.ResearchControlPanel'):

            # Create nodes with names that would sort differently
            node_z = MagicMock()
            node_z.id = 'node_z'
            node_z.name = 'Zeta'

            node_a = MagicMock()
            node_a.id = 'node_a'
            node_a.name = 'Alpha'

            mock_tree = MagicMock()
            mock_tree.nodes = {'node_z': node_z, 'node_a': node_a}
            mock_tree.get_max_depth.return_value = 0
            # Return in reverse alphabetical order - should be sorted
            mock_tree.get_nodes_at_depth.return_value = [node_z, node_a]
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Alpha should be above Zeta (lower y)
            y_a = scene.node_positions['node_a'][1]
            y_z = scene.node_positions['node_z'][1]
            assert y_a < y_z


class TestLayoutConstants:
    """Tests for layout constant values."""

    def test_sidebar_width_is_positive(self):
        """Sidebar width constant is positive."""
        from game.ui.research.research_scene import ResearchTreeScene
        assert ResearchTreeScene.SIDEBAR_WIDTH > 0

    def test_column_spacing_is_positive(self):
        """Column spacing constant is positive."""
        from game.ui.research.research_scene import ResearchTreeScene
        assert ResearchTreeScene.COLUMN_SPACING > 0

    def test_row_spacing_is_positive(self):
        """Row spacing constant is positive."""
        from game.ui.research.research_scene import ResearchTreeScene
        assert ResearchTreeScene.ROW_SPACING > 0

    def test_node_dimensions_are_positive(self):
        """Node width and height constants are positive."""
        from game.ui.research.research_scene import ResearchTreeScene
        assert ResearchTreeScene.NODE_WIDTH > 0
        assert ResearchTreeScene.NODE_HEIGHT > 0
