"""Tests for draw_battle_hud and update_tick_rate functions."""
import pytest
from unittest.mock import Mock


class TestDrawBattleHUD:
    """Tests for draw_battle_hud function."""

    def test_draws_tick_counter(self, mock_screen, mock_battle_scene, mock_font):
        """HUD draws tick counter."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.sim_tick_counter = 12345

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        # Check that render was called with tick text
        calls = [str(c) for c in mock_font.render.call_args_list]
        assert any("Ticks: 12,345" in c for c in calls)

    def test_draws_tick_rate(self, mock_screen, mock_battle_scene, mock_font):
        """HUD draws tick rate (TPS)."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.current_tick_rate = 100

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        calls = [str(c) for c in mock_font.render.call_args_list]
        assert any("TPS: 100" in c for c in calls)

    def test_draws_zoom_level(self, mock_screen, mock_battle_scene, mock_font):
        """HUD draws zoom level."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.camera.zoom = 1.5

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        calls = [str(c) for c in mock_font.render.call_args_list]
        assert any("Zoom: 1.500x" in c for c in calls)

    def test_draws_speed_indicator(self, mock_screen, mock_battle_scene, mock_font):
        """HUD draws speed indicator."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.sim_speed_multiplier = 2.0

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        calls = [str(c) for c in mock_font.render.call_args_list]
        assert any("Speed: 2x" in c for c in calls)

    def test_draws_max_speed_label(self, mock_screen, mock_battle_scene, mock_font):
        """HUD draws MAX SPEED label in turbo mode."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.sim_speed_multiplier = 100.0

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        calls = [str(c) for c in mock_font.render.call_args_list]
        assert any("MAX SPEED" in c for c in calls)

    def test_draws_paused_indicator(self, mock_screen, mock_battle_scene, mock_font):
        """HUD draws PAUSED indicator when paused."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.sim_paused = True
        mock_battle_scene.sim_speed_multiplier = 1.0

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        calls = [str(c) for c in mock_font.render.call_args_list]
        assert any("PAUSED" in c for c in calls)

    def test_draws_profiler_indicator_when_active(self, mock_screen, mock_battle_scene, mock_font):
        """HUD draws profiler indicator when profiling is active."""
        from game.battle_coordinator import draw_battle_hud

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font, profiler_active=True)

        calls = [str(c) for c in mock_font.render.call_args_list]
        assert any("PROFILING ACTIVE" in c for c in calls)

    def test_no_profiler_indicator_when_inactive(self, mock_screen, mock_battle_scene, mock_font):
        """HUD does not draw profiler indicator when profiling is inactive."""
        from game.battle_coordinator import draw_battle_hud

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font, profiler_active=False)

        calls = [str(c) for c in mock_font.render.call_args_list]
        assert not any("PROFILING" in c for c in calls)

    def test_speed_color_red_when_paused(self, mock_screen, mock_battle_scene, mock_font):
        """HUD uses red color for speed when paused."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.sim_paused = True
        mock_battle_scene.sim_speed_multiplier = 1.0

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        # Look for the speed-related render call with red-ish color
        speed_calls = [c for c in mock_font.render.call_args_list if "PAUSED" in str(c)]
        assert len(speed_calls) > 0
        # Check color tuple - red has high R, low G and B
        color = speed_calls[0][0][2]  # Third positional arg is color
        assert color[0] > 200  # Red channel high

    def test_speed_color_orange_when_slow(self, mock_screen, mock_battle_scene, mock_font):
        """HUD uses orange color for speed when slow motion."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.sim_paused = False
        mock_battle_scene.sim_speed_multiplier = 0.5

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        # Find speed render call
        speed_calls = [c for c in mock_font.render.call_args_list if "Speed:" in str(c)]
        assert len(speed_calls) > 0
        color = speed_calls[0][0][2]
        # Orange: high R, medium G, low B
        assert color[0] > 200 and color[1] > 150 and color[2] < 150

    def test_speed_color_green_when_fast(self, mock_screen, mock_battle_scene, mock_font):
        """HUD uses green color for speed when fast motion."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.sim_paused = False
        mock_battle_scene.sim_speed_multiplier = 2.0

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        # Find speed render call
        speed_calls = [c for c in mock_font.render.call_args_list if "Speed:" in str(c)]
        assert len(speed_calls) > 0
        color = speed_calls[0][0][2]
        # Green: low R, high G, low B
        assert color[1] > 200  # Green channel high

    def test_offsets_from_seeker_panel(self, mock_screen, mock_battle_scene, mock_font):
        """HUD positions text to right of seeker panel."""
        from game.battle_coordinator import draw_battle_hud

        mock_battle_scene.ui.seeker_panel.rect.width = 300

        draw_battle_hud(mock_screen, mock_battle_scene, mock_font)

        # Check blit positions - first blit should be at panel_offset = 310
        blit_calls = mock_screen.blit.call_args_list
        assert len(blit_calls) > 0
        # First text (tick count) should be at x = 310 (300 + 10)
        assert blit_calls[0][0][1][0] == 310


class TestUpdateTickRate:
    """Tests for update_tick_rate function."""

    def test_accumulates_timer(self, mock_battle_scene):
        """Tick rate timer accumulates frame time."""
        from game.battle_coordinator import update_tick_rate

        mock_battle_scene.tick_rate_timer = 0.5
        frame_time = 0.2

        update_tick_rate(mock_battle_scene, frame_time)

        assert mock_battle_scene.tick_rate_timer == 0.7

    def test_updates_rate_after_one_second(self, mock_battle_scene):
        """Tick rate updates after 1 second."""
        from game.battle_coordinator import update_tick_rate

        mock_battle_scene.tick_rate_timer = 0.9
        mock_battle_scene.tick_rate_count = 50
        frame_time = 0.2  # Pushes timer to 1.1

        update_tick_rate(mock_battle_scene, frame_time)

        assert mock_battle_scene.current_tick_rate == 50

    def test_resets_count_after_update(self, mock_battle_scene):
        """Tick count resets after rate update."""
        from game.battle_coordinator import update_tick_rate

        mock_battle_scene.tick_rate_timer = 0.9
        mock_battle_scene.tick_rate_count = 50
        frame_time = 0.2

        update_tick_rate(mock_battle_scene, frame_time)

        assert mock_battle_scene.tick_rate_count == 0

    def test_resets_timer_after_update(self, mock_battle_scene):
        """Tick timer resets after rate update."""
        from game.battle_coordinator import update_tick_rate

        mock_battle_scene.tick_rate_timer = 0.9
        mock_battle_scene.tick_rate_count = 50
        frame_time = 0.2

        update_tick_rate(mock_battle_scene, frame_time)

        assert mock_battle_scene.tick_rate_timer == 0.0

    def test_does_not_update_before_one_second(self, mock_battle_scene):
        """Tick rate does not update before 1 second elapsed."""
        from game.battle_coordinator import update_tick_rate

        mock_battle_scene.tick_rate_timer = 0.0
        mock_battle_scene.tick_rate_count = 50
        mock_battle_scene.current_tick_rate = 100  # Old value
        frame_time = 0.5

        update_tick_rate(mock_battle_scene, frame_time)

        # Current tick rate should not change
        assert mock_battle_scene.current_tick_rate == 100
        # Count should not reset
        assert mock_battle_scene.tick_rate_count == 50

    def test_preserves_count_across_frames(self, mock_battle_scene):
        """Tick count is preserved across frames until 1 second."""
        from game.battle_coordinator import update_tick_rate

        # Multiple frames that don't add up to 1 second
        mock_battle_scene.tick_rate_timer = 0.0
        mock_battle_scene.tick_rate_count = 25
        mock_battle_scene.current_tick_rate = 0

        update_tick_rate(mock_battle_scene, 0.3)
        assert mock_battle_scene.tick_rate_count == 25  # Still preserved

        update_tick_rate(mock_battle_scene, 0.3)
        assert mock_battle_scene.tick_rate_count == 25  # Still preserved

        update_tick_rate(mock_battle_scene, 0.5)  # Now over 1 second
        assert mock_battle_scene.current_tick_rate == 25
        assert mock_battle_scene.tick_rate_count == 0  # Now reset


class TestCoordinatorIntegration:
    """Integration tests for coordinator functions working together."""

    def test_visual_and_tick_rate_work_together(self, mock_game, mock_battle_scene):
        """Visual updates and tick rate calculation work together."""
        from game.battle_coordinator import update_battle_visual, update_tick_rate

        mock_battle_scene.sim_speed_multiplier = 1.0
        mock_battle_scene.tick_rate_count = 0
        mock_battle_scene.tick_rate_timer = 0.0
        mock_battle_scene.current_tick_rate = 0
        mock_game._battle_accumulator = 0.0

        # Simulate several frames
        for _ in range(100):
            update_battle_visual(mock_game, mock_battle_scene, 0.01, [])
            update_tick_rate(mock_battle_scene, 0.01)

        # After 1 second (100 * 0.01), tick rate should be updated
        assert mock_battle_scene.current_tick_rate >= 90  # Approximately 100 TPS

    def test_headless_completes_with_winner(self, mock_game, mock_battle_scene):
        """Headless battle properly completes and reports winner."""
        from game.battle_coordinator import update_battle_headless

        # Setup ships
        team1_ship = Mock()
        team1_ship.team_id = 0
        team1_ship.is_alive = True
        team2_ship = Mock()
        team2_ship.team_id = 1
        team2_ship.is_alive = False

        mock_battle_scene.ships = [team1_ship, team2_ship]
        mock_battle_scene.is_battle_over.return_value = True

        result = update_battle_headless(mock_game, mock_battle_scene)

        assert result is True
        mock_battle_scene.print_headless_summary.assert_called_once()
