"""
Tests for ResearchTreeScene callback handling.

Covers:
- Turn processing callbacks
- Reset functionality
- Close callback handling
- Auto-spread callback handling
"""
import pytest
from unittest.mock import MagicMock, patch


class TestTurnProcessingCallback:
    """Tests for _on_next_turn callback."""

    def test_on_next_turn_processes_turn(self):
        """Next turn callback calls ResearchService.process_turn."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel'), \
             patch('game.research.ui.research_scene.ResearchService') as MockService:

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            mock_tracker.auto_spread_enabled = False
            mock_tracker.turn_number = 1
            mock_tracker.get_all_tech_levels.return_value = {}
            MockTracker.return_value = mock_tracker

            MockService.process_turn.return_value = []

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene._on_next_turn()

            MockService.process_turn.assert_called_once()

    def test_on_next_turn_updates_log(self):
        """Next turn callback updates control panel log."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel') as MockPanel, \
             patch('game.research.ui.research_scene.ResearchService') as MockService:

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            mock_tracker.auto_spread_enabled = False
            mock_tracker.turn_number = 5
            mock_tracker.get_all_tech_levels.return_value = {}
            MockTracker.return_value = mock_tracker

            events = [{'event': 'test'}]
            MockService.process_turn.return_value = events

            mock_panel_instance = MagicMock()
            MockPanel.return_value = mock_panel_instance

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene._on_next_turn()

            mock_panel_instance.update_turn_log.assert_called_with(events, 5)

    def test_on_next_turn_with_auto_spread(self):
        """Next turn callback spreads RP when auto-spread is enabled."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel') as MockPanel, \
             patch('game.research.ui.research_scene.ResearchService') as MockService:

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            mock_tracker.auto_spread_enabled = True  # Auto-spread ON
            mock_tracker.turn_number = 1
            mock_tracker.get_all_tech_levels.return_value = {}
            MockTracker.return_value = mock_tracker

            MockService.process_turn.return_value = []
            mock_panel_instance = MagicMock()
            MockPanel.return_value = mock_panel_instance

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene._on_next_turn()

            mock_tracker.spread_rp_evenly.assert_called_once()


class TestResetCallback:
    """Tests for _on_reset callback."""

    def test_on_reset_creates_new_tracker(self):
        """Reset creates a new ResearchTracker."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel') as MockPanel:

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker1 = MagicMock()
            mock_tracker1.session_seed = 12345
            mock_tracker2 = MagicMock()
            mock_tracker2.session_seed = 67890
            MockTracker.side_effect = [mock_tracker1, mock_tracker2]

            mock_panel_instance = MagicMock()
            MockPanel.return_value = mock_panel_instance

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Verify initial tracker
            assert scene.tracker is mock_tracker1

            # Reset
            scene._on_reset()

            # Should have new tracker
            assert scene.tracker is mock_tracker2

    def test_on_reset_clears_selection(self):
        """Reset clears node selection."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel') as MockPanel:

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            mock_panel_instance = MagicMock()
            MockPanel.return_value = mock_panel_instance

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Set a selection
            scene.selected_node_id = 'some_node'

            # Reset
            scene._on_reset()

            # Selection should be cleared
            assert scene.selected_node_id is None
            # Control panel reset() is called (which internally calls clear_selection)
            mock_panel_instance.reset.assert_called()

    def test_on_reset_resolves_requirements_with_new_seed(self):
        """Reset re-resolves fuzzy requirements with new seed."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel'):

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker1 = MagicMock()
            mock_tracker1.session_seed = 12345
            mock_tracker2 = MagicMock()
            mock_tracker2.session_seed = 67890
            MockTracker.side_effect = [mock_tracker1, mock_tracker2]

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Reset the mock call count
            mock_tree.resolve_all_requirements.reset_mock()

            # Reset
            scene._on_reset()

            # Should resolve with new seed
            mock_tree.resolve_all_requirements.assert_called_with(67890)


class TestCloseCallback:
    """Tests for _on_close callback."""

    def test_on_close_calls_callback(self):
        """Close calls the provided callback."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel'):

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            close_callback = MagicMock()
            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080, on_close_callback=close_callback)

            scene._on_close()

            close_callback.assert_called_once()

    def test_on_close_without_callback(self):
        """Close with no callback doesn't crash."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel'):

            mock_tree = MagicMock()
            mock_tree.nodes = {}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)  # No callback

            # Should not crash
            scene._on_close()


class TestAutoSpreadCallback:
    """Tests for _on_auto_spread_changed callback."""

    def test_auto_spread_changed_updates_selected_node(self):
        """Auto-spread change updates selected node display."""
        with patch('game.research.ui.research_scene.TechTree') as MockTechTree, \
             patch('game.research.ui.research_scene.ResearchTracker') as MockTracker, \
             patch('game.research.ui.research_scene.Camera'), \
             patch('game.research.ui.research_scene.pygame_gui'), \
             patch('game.research.ui.research_scene.ResearchRenderer'), \
             patch('game.research.ui.research_scene.ResearchControlPanel') as MockPanel:

            mock_node = MagicMock()
            mock_node.id = 'selected_node'

            mock_tree = MagicMock()
            mock_tree.nodes = {'selected_node': mock_node}
            mock_tree.get_max_depth.return_value = 0
            mock_tree.validate_requirements.return_value = []
            mock_tree.get_node.return_value = mock_node
            MockTechTree.load_from_json.return_value = mock_tree

            mock_tracker = MagicMock()
            mock_tracker.session_seed = 12345
            MockTracker.return_value = mock_tracker

            mock_panel_instance = MagicMock()
            MockPanel.return_value = mock_panel_instance

            from game.research.ui.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Set selection
            scene.selected_node_id = 'selected_node'

            # Trigger auto-spread change
            scene._on_auto_spread_changed(True)

            mock_panel_instance.update_selected_node.assert_called()
