"""Tests for update_battle_headless function."""
import pytest
from unittest.mock import Mock


class TestUpdateBattleHeadless:
    """Tests for update_battle_headless function."""

    def test_runs_1000_updates_per_call(self, mock_game, mock_battle_scene):
        """Headless mode runs 1000 updates per call."""
        from game.battle_coordinator import update_battle_headless

        update_battle_headless(mock_game, mock_battle_scene)

        # Should call update 1000 times (max loop count)
        assert mock_battle_scene.update.call_count == 1000

    def test_stops_when_battle_over(self, mock_game, mock_battle_scene):
        """Headless mode stops when battle is over."""
        from game.battle_coordinator import update_battle_headless

        # Battle ends after 100 updates
        call_count = [0]
        def update_side_effect(events):
            call_count[0] += 1
        def is_over_side_effect():
            return call_count[0] >= 100
        mock_battle_scene.update.side_effect = update_side_effect
        mock_battle_scene.is_battle_over.side_effect = is_over_side_effect

        result = update_battle_headless(mock_game, mock_battle_scene)

        assert result is True
        assert call_count[0] == 100

    def test_stops_at_tick_limit(self, mock_game, mock_battle_scene):
        """Headless mode stops when tick limit reached."""
        from game.battle_coordinator import update_battle_headless

        mock_battle_scene.sim_tick_counter = 3000000  # At limit

        result = update_battle_headless(mock_game, mock_battle_scene)

        assert result is True

    def test_returns_false_when_not_complete(self, mock_game, mock_battle_scene):
        """Headless mode returns False when battle continues."""
        from game.battle_coordinator import update_battle_headless

        mock_battle_scene.sim_tick_counter = 1000
        mock_battle_scene.is_battle_over.return_value = False

        result = update_battle_headless(mock_game, mock_battle_scene)

        assert result is False

    def test_prints_summary_on_completion(self, mock_game, mock_battle_scene):
        """Headless mode prints summary when complete."""
        from game.battle_coordinator import update_battle_headless

        mock_battle_scene.is_battle_over.return_value = True

        update_battle_headless(mock_game, mock_battle_scene)

        mock_battle_scene.print_headless_summary.assert_called_once()

    def test_shuts_down_engine_on_completion(self, mock_game, mock_battle_scene):
        """Headless mode shuts down engine when complete."""
        from game.battle_coordinator import update_battle_headless

        mock_battle_scene.is_battle_over.return_value = True

        update_battle_headless(mock_game, mock_battle_scene)

        mock_battle_scene.engine.shutdown.assert_called_once()

    def test_disables_headless_mode_on_completion(self, mock_game, mock_battle_scene):
        """Headless mode disables itself when complete."""
        from game.battle_coordinator import update_battle_headless

        mock_battle_scene.is_battle_over.return_value = True

        update_battle_headless(mock_game, mock_battle_scene)

        assert mock_battle_scene.headless_mode is False

    def test_returns_to_test_lab_in_test_mode(self, mock_game, mock_battle_scene):
        """Headless mode returns to test lab when in test mode."""
        from game.battle_coordinator import update_battle_headless

        mock_battle_scene.is_battle_over.return_value = True
        mock_battle_scene.test_mode = True

        update_battle_headless(mock_game, mock_battle_scene)

        assert mock_battle_scene.action_return_to_test_lab is True

    def test_returns_to_battle_setup_when_not_test_mode(self, mock_game, mock_battle_scene):
        """Headless mode returns to battle setup when not in test mode."""
        from game.battle_coordinator import update_battle_headless

        mock_battle_scene.is_battle_over.return_value = True
        mock_battle_scene.test_mode = False

        update_battle_headless(mock_game, mock_battle_scene)

        mock_game.start_battle_setup.assert_called_once_with(preserve_teams=True)

    def test_passes_empty_list_to_update(self, mock_game, mock_battle_scene):
        """Headless mode passes empty event list to update."""
        from game.battle_coordinator import update_battle_headless

        # Run just one iteration before stopping
        mock_battle_scene.is_battle_over.side_effect = [True]

        update_battle_headless(mock_game, mock_battle_scene)

        # First call gets empty list
        mock_battle_scene.update.assert_called_with([])
