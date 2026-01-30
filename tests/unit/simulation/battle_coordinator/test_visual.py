"""Tests for update_battle_visual function."""
import pytest
from unittest.mock import Mock


class TestUpdateBattleVisual:
    """Tests for update_battle_visual function."""

    def test_updates_visuals_every_frame(self, mock_game, mock_battle_scene):
        """Visual update always updates visuals once per frame."""
        from game.battle_coordinator import update_battle_visual

        frame_time = 0.016  # ~60 FPS
        events = []

        update_battle_visual(mock_game, mock_battle_scene, frame_time, events)

        mock_battle_scene.update_visuals.assert_called_once_with(frame_time, events)

    def test_skips_simulation_when_paused(self, mock_game, mock_battle_scene):
        """Visual update skips simulation when paused."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_paused = True
        frame_time = 0.016
        events = []

        update_battle_visual(mock_game, mock_battle_scene, frame_time, events)

        # Should update visuals but not call update
        mock_battle_scene.update_visuals.assert_called_once()
        mock_battle_scene.update.assert_not_called()

    def test_turbo_mode_runs_fixed_ticks(self, mock_game, mock_battle_scene):
        """Visual update runs fixed ticks in turbo mode (speed > 10)."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 100.0  # Turbo mode
        frame_time = 0.016
        events = []

        update_battle_visual(mock_game, mock_battle_scene, frame_time, events)

        # Should run 100 ticks
        assert mock_battle_scene.update.call_count == 100
        assert mock_battle_scene.tick_rate_count == 100

    def test_normal_mode_uses_accumulator(self, mock_game, mock_battle_scene):
        """Visual update uses time accumulator in normal mode."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 1.0
        frame_time = 0.02  # 50 FPS - should allow 2 ticks at 100 TPS

        # Ensure accumulator is initialized
        mock_game._battle_accumulator = 0.0

        update_battle_visual(mock_game, mock_battle_scene, frame_time, [])

        # At 1x speed, 0.02s frame should allow 2 ticks (0.01s each)
        assert mock_battle_scene.update.call_count == 2

    def test_accumulator_caps_at_1_second(self, mock_game, mock_battle_scene):
        """Visual update caps accumulator at 1 second."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 1.0
        frame_time = 2.0  # Very long frame (lag spike)

        mock_game._battle_accumulator = 0.0

        update_battle_visual(mock_game, mock_battle_scene, frame_time, [])

        # Accumulator should be capped, limiting ticks run
        # At 0.01s per tick, max 100 ticks from 1 second accumulator
        assert mock_battle_scene.update.call_count <= 100

    def test_first_tick_gets_events(self, mock_game, mock_battle_scene):
        """Visual update passes events only to first tick."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 100.0  # Turbo mode
        frame_time = 0.016
        events = [Mock()]  # Some event

        update_battle_visual(mock_game, mock_battle_scene, frame_time, events)

        # First call should get events, rest get empty list
        calls = mock_battle_scene.update.call_args_list
        assert calls[0][0][0] == events  # First call has events
        for call in calls[1:]:
            assert call[0][0] == []  # Subsequent calls have empty list

    def test_slow_mode_uses_multiplier(self, mock_game, mock_battle_scene):
        """Visual update uses speed multiplier correctly in slow mode."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 0.5  # Half speed
        frame_time = 0.02  # Would normally allow 2 ticks

        mock_game._battle_accumulator = 0.0

        update_battle_visual(mock_game, mock_battle_scene, frame_time, [])

        # At 0.5x speed, 0.02s frame gives 0.01s accumulator = 1 tick
        assert mock_battle_scene.update.call_count == 1

    def test_fast_mode_uses_multiplier(self, mock_game, mock_battle_scene):
        """Visual update uses speed multiplier correctly in fast mode."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 2.0  # Double speed
        frame_time = 0.01  # Would normally allow 1 tick

        mock_game._battle_accumulator = 0.0

        update_battle_visual(mock_game, mock_battle_scene, frame_time, [])

        # At 2x speed, 0.01s frame gives 0.02s accumulator = 2 ticks
        assert mock_battle_scene.update.call_count == 2

    def test_tick_rate_count_updated_turbo(self, mock_game, mock_battle_scene):
        """Visual update updates tick rate count in turbo mode."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 50.0
        mock_battle_scene.tick_rate_count = 0
        frame_time = 0.016

        update_battle_visual(mock_game, mock_battle_scene, frame_time, [])

        assert mock_battle_scene.tick_rate_count == 50

    def test_tick_rate_count_updated_normal(self, mock_game, mock_battle_scene):
        """Visual update updates tick rate count in normal mode."""
        from game.battle_coordinator import update_battle_visual

        mock_battle_scene.sim_speed_multiplier = 1.0
        mock_battle_scene.tick_rate_count = 10  # Starting count
        frame_time = 0.03  # 3 ticks worth at 0.01s/tick

        mock_game._battle_accumulator = 0.0

        update_battle_visual(mock_game, mock_battle_scene, frame_time, [])

        # Should add ticks to existing 10 (at least 2, up to 3 depending on timing)
        # Accumulator: 0.03 at TICK_RATE 0.01 = 3 ticks max, but may leave small remainder
        assert mock_battle_scene.tick_rate_count >= 12  # At least 2 added
        assert mock_battle_scene.tick_rate_count <= 13  # At most 3 added
