"""
Unit tests for battle_coordinator module.

Tests the battle coordination logic including:
- Headless battle simulation
- Visual battle updates with timing
- HUD rendering
- Tick rate calculation
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import pygame


# === Fixtures ===

@pytest.fixture
def mock_game():
    """Create a mock Game object."""
    game = Mock()
    game._battle_accumulator = 0.0
    return game


@pytest.fixture
def mock_battle_scene():
    """Create a mock BattleScreen object."""
    scene = Mock()
    scene.sim_tick_counter = 0
    scene.sim_paused = False
    scene.sim_speed_multiplier = 1.0
    scene.headless_mode = True
    scene.test_mode = False
    scene.is_battle_over.return_value = False
    scene.ships = []
    scene.tick_rate_count = 0
    scene.tick_rate_timer = 0.0
    scene.current_tick_rate = 0

    # Camera
    scene.camera = Mock()
    scene.camera.zoom = 1.0

    # UI
    scene.ui = Mock()
    scene.ui.seeker_panel = Mock()
    scene.ui.seeker_panel.rect = Mock()
    scene.ui.seeker_panel.rect.width = 200

    # Engine
    scene.engine = Mock()

    return scene


@pytest.fixture
def mock_screen():
    """Create a mock pygame screen surface."""
    screen = Mock()
    screen.get_width.return_value = 1920
    screen.get_height.return_value = 1080
    return screen


@pytest.fixture
def mock_font():
    """Create a mock pygame font."""
    font = Mock()
    font.render.return_value = Mock()
    return font


# === Update Battle Headless Tests ===

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


# === Update Battle Visual Tests ===

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


# === Draw Battle HUD Tests ===

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


# === Update Tick Rate Tests ===

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


# === Integration Tests for Coordinator Functions ===

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
