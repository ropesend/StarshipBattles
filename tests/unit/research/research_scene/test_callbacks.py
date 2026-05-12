"""
Tests for ResearchTreeScene callback handling.

Covers:
- Turn processing callbacks
- Reset functionality
- Close callback handling
- Auto-spread callback handling
"""
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest


def _make_default_tree():
    tree = MagicMock()
    tree.nodes = {}
    tree.get_max_depth.return_value = 0
    tree.validate_requirements.return_value = []
    return tree


def _make_default_tracker(seed=12345, **overrides):
    tracker = MagicMock()
    tracker.session_seed = seed
    tracker.auto_spread_enabled = False
    tracker.turn_number = 1
    tracker.get_all_tech_levels.return_value = {}
    for key, value in overrides.items():
        setattr(tracker, key, value)
    return tracker


@contextmanager
def _patched_research_scene(*, with_service=False):
    """Patch the standard set of research_scene module attributes used by ResearchTreeScene.

    Yields a dict of the active patcher mocks keyed by short names so individual
    tests can customize behavior or assert on call sites.
    """
    patches = {
        'TechTree': patch('game.ui.research.research_scene.TechTree'),
        'Tracker': patch('game.ui.research.research_scene.ResearchTracker'),
        'Camera': patch('game.ui.research.research_scene.Camera'),
        'StarshipUIManager': patch('game.ui.research.research_scene.StarshipUIManager'),
        'Renderer': patch('game.ui.research.research_scene.ResearchRenderer'),
        'Panel': patch('game.ui.research.research_scene.ResearchControlPanel'),
    }
    if with_service:
        patches['Service'] = patch('game.ui.research.research_scene.ResearchService')

    started = {name: p.start() for name, p in patches.items()}
    try:
        yield started
    finally:
        for p in patches.values():
            p.stop()


class TestTurnProcessingCallback:
    """Tests for _on_next_turn callback."""

    def test_on_next_turn_processes_turn(self):
        """Next turn callback calls ResearchService.process_turn."""
        with _patched_research_scene(with_service=True) as mocks:
            mocks['TechTree'].load_from_json.return_value = _make_default_tree()
            mocks['Tracker'].return_value = _make_default_tracker()
            mocks['Service'].process_turn.return_value = []

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene._on_next_turn()

            mocks['Service'].process_turn.assert_called_once()

    def test_on_next_turn_updates_log(self):
        """Next turn callback updates control panel log."""
        with _patched_research_scene(with_service=True) as mocks:
            mocks['TechTree'].load_from_json.return_value = _make_default_tree()
            mocks['Tracker'].return_value = _make_default_tracker(turn_number=5)

            events = [{'event': 'test'}]
            mocks['Service'].process_turn.return_value = events

            mock_panel_instance = MagicMock()
            mocks['Panel'].return_value = mock_panel_instance

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene._on_next_turn()

            mock_panel_instance.update_turn_log.assert_called_with(events, 5)

    def test_on_next_turn_with_auto_spread(self):
        """Next turn callback spreads RP when auto-spread is enabled."""
        with _patched_research_scene(with_service=True) as mocks:
            mocks['TechTree'].load_from_json.return_value = _make_default_tree()
            tracker = _make_default_tracker(auto_spread_enabled=True)
            mocks['Tracker'].return_value = tracker
            mocks['Service'].process_turn.return_value = []
            mocks['Panel'].return_value = MagicMock()

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            scene._on_next_turn()

            tracker.spread_rp_evenly.assert_called_once()


class TestResetCallback:
    """Tests for _on_reset callback."""

    def test_on_reset_creates_new_tracker(self):
        """Reset creates a new ResearchTracker."""
        with _patched_research_scene() as mocks:
            mocks['TechTree'].load_from_json.return_value = _make_default_tree()

            mock_tracker1 = _make_default_tracker(seed=12345)
            mock_tracker2 = _make_default_tracker(seed=67890)
            mocks['Tracker'].side_effect = [mock_tracker1, mock_tracker2]

            mocks['Panel'].return_value = MagicMock()

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Verify initial tracker
            assert scene.tracker is mock_tracker1

            # Reset
            scene._on_reset()

            # Should have new tracker
            assert scene.tracker is mock_tracker2

    def test_on_reset_clears_selection(self):
        """Reset clears node selection."""
        with _patched_research_scene() as mocks:
            mocks['TechTree'].load_from_json.return_value = _make_default_tree()
            mocks['Tracker'].return_value = _make_default_tracker()

            mock_panel_instance = MagicMock()
            mocks['Panel'].return_value = mock_panel_instance

            from game.ui.research.research_scene import ResearchTreeScene
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
        with _patched_research_scene() as mocks:
            tree = _make_default_tree()
            mocks['TechTree'].load_from_json.return_value = tree

            mock_tracker1 = _make_default_tracker(seed=12345)
            mock_tracker2 = _make_default_tracker(seed=67890)
            mocks['Tracker'].side_effect = [mock_tracker1, mock_tracker2]

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Reset the mock call count
            tree.resolve_all_requirements.reset_mock()

            # Reset
            scene._on_reset()

            # Should resolve with new seed
            tree.resolve_all_requirements.assert_called_with(67890)


class TestCloseCallback:
    """Tests for _on_close callback."""

    def test_on_close_calls_callback(self):
        """Close calls the provided callback."""
        with _patched_research_scene() as mocks:
            mocks['TechTree'].load_from_json.return_value = _make_default_tree()
            mocks['Tracker'].return_value = _make_default_tracker()

            close_callback = MagicMock()
            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080, on_close_callback=close_callback)

            scene._on_close()

            close_callback.assert_called_once()

    def test_on_close_without_callback(self):
        """Close with no callback doesn't crash."""
        with _patched_research_scene() as mocks:
            mocks['TechTree'].load_from_json.return_value = _make_default_tree()
            mocks['Tracker'].return_value = _make_default_tracker()

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)  # No callback

            # Should not crash
            scene._on_close()


class TestAutoSpreadCallback:
    """Tests for _on_auto_spread_changed callback."""

    def test_auto_spread_changed_updates_selected_node(self):
        """Auto-spread change updates selected node display."""
        with _patched_research_scene() as mocks:
            mock_node = MagicMock()
            mock_node.id = 'selected_node'

            tree = _make_default_tree()
            tree.nodes = {'selected_node': mock_node}
            tree.get_node.return_value = mock_node
            mocks['TechTree'].load_from_json.return_value = tree

            mocks['Tracker'].return_value = _make_default_tracker()

            mock_panel_instance = MagicMock()
            mocks['Panel'].return_value = mock_panel_instance

            from game.ui.research.research_scene import ResearchTreeScene
            scene = ResearchTreeScene(1920, 1080)

            # Set selection
            scene.selected_node_id = 'selected_node'

            # Trigger auto-spread change
            scene._on_auto_spread_changed(True)

            mock_panel_instance.update_selected_node.assert_called()
