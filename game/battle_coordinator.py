"""
Battle coordination logic for the main game loop.

Handles battle simulation updates including speed control, accumulator logic,
headless mode execution, and HUD rendering.
"""
import time
import pygame

from game.core.logger import log_debug, log_warning
from game.core.config import PhysicsConfig


def update_battle_headless(game, battle_scene):
    """
    Run headless battle simulation (fast mode without rendering).

    Args:
        game: Game instance
        battle_scene: BattleScene instance

    Returns:
        True if battle is complete, False otherwise
    """
    for _ in range(1000):
        battle_scene.update([])

        tick_limit_reached = battle_scene.sim_tick_counter >= 3000000

        if battle_scene.is_battle_over() or tick_limit_reached:
            battle_scene.print_headless_summary()
            battle_scene.engine.shutdown()
            battle_scene.headless_mode = False

            if battle_scene.test_mode:
                log_debug("Headless test complete, returning to Combat Lab")
                battle_scene.action_return_to_test_lab = True
            else:
                game.start_battle_setup(preserve_teams=True)
            return True

    # Progress indicator
    if battle_scene.sim_tick_counter % 10000 == 0:
        t1 = sum(1 for s in battle_scene.ships if s.team_id == 0 and s.is_alive)
        t2 = sum(1 for s in battle_scene.ships if s.team_id == 1 and s.is_alive)
        log_debug(f"  Tick {battle_scene.sim_tick_counter}: Team1={t1}, Team2={t2}")

    return False


def update_battle_visual(game, battle_scene, frame_time, events):
    """
    Update visual battle simulation with proper timing.

    Args:
        game: Game instance
        battle_scene: BattleScene instance
        frame_time: Time elapsed this frame
        events: Pygame events list
    """
    # Update visuals (camera, beams) - always run once per frame
    battle_scene.update_visuals(frame_time, events)

    # Update simulation
    if not battle_scene.sim_paused:
        dt = PhysicsConfig.TICK_RATE
        speed_mult = battle_scene.sim_speed_multiplier

        if speed_mult > 10.0:
            # Max Speed / Turbo mode: Run fixed N ticks per frame
            ticks_to_run = int(speed_mult)

            t0 = time.time()
            for i in range(ticks_to_run):
                battle_scene.update(events if i == 0 else [])
            t1 = time.time()

            elapsed = t1 - t0
            if elapsed > 0.05:
                log_warning(f"Slow Frame: {ticks_to_run} ticks took {elapsed*1000:.1f}ms")

            battle_scene.tick_rate_count += ticks_to_run
        else:
            # Time-accurate simulation (slow/normal/fast)
            if not hasattr(game, '_battle_accumulator'):
                game._battle_accumulator = 0.0

            game._battle_accumulator += frame_time * speed_mult

            # Safety cap
            if game._battle_accumulator > 1.0:
                game._battle_accumulator = 1.0

            ticks_run_this_frame = 0
            while game._battle_accumulator >= dt:
                battle_scene.update(events if ticks_run_this_frame == 0 else [])
                game._battle_accumulator -= dt
                ticks_run_this_frame += 1

            battle_scene.tick_rate_count += ticks_run_this_frame


def draw_battle_hud(screen, battle_scene, font_med, profiler_active=False):
    """
    Draw battle HUD elements (tick counters, speed indicator).

    Args:
        screen: Pygame screen surface
        battle_scene: BattleScene instance
        font_med: Font for rendering text
        profiler_active: Whether profiler is active
    """
    width = screen.get_width()

    # Tick counters
    tick_text = f"Ticks: {battle_scene.sim_tick_counter:,}"
    rate_text = f"TPS: {battle_scene.current_tick_rate:,}/s"
    zoom_text = f"Zoom: {battle_scene.camera.zoom:.3f}x"

    # Draw to the right of seeker panel
    panel_offset = battle_scene.ui.seeker_panel.rect.width + 10
    screen.blit(font_med.render(tick_text, True, (180, 180, 180)), (panel_offset, 10))
    screen.blit(font_med.render(rate_text, True, (180, 180, 180)), (panel_offset, 35))
    screen.blit(font_med.render(zoom_text, True, (150, 200, 255)), (panel_offset, 60))

    # Speed indicator
    if battle_scene.sim_speed_multiplier >= 10.0:
        speed_val_text = "MAX SPEED"
    else:
        speed_val_text = f"{battle_scene.sim_speed_multiplier:.4g}x"

    if battle_scene.sim_paused:
        speed_text = f"PAUSED ({speed_val_text})"
    else:
        speed_text = f"Speed: {speed_val_text}"

    speed_color = (255, 100, 100) if battle_scene.sim_paused else (200, 200, 200)
    if battle_scene.sim_speed_multiplier < 1.0:
        speed_color = (255, 200, 100)
    elif battle_scene.sim_speed_multiplier > 1.0:
        speed_color = (100, 255, 100)

    screen.blit(font_med.render(speed_text, True, speed_color), (width // 2 - 50, 10))

    # Profiler indicator
    if profiler_active:
        prof_text = font_med.render("PROFILING ACTIVE", True, (255, 50, 50))
        screen.blit(prof_text, (width - 180, 10))


def update_tick_rate(battle_scene, frame_time):
    """
    Update tick rate calculation for HUD display.

    Args:
        battle_scene: BattleScene instance
        frame_time: Time elapsed this frame
    """
    battle_scene.tick_rate_timer += frame_time
    if battle_scene.tick_rate_timer >= 1.0:
        battle_scene.current_tick_rate = battle_scene.tick_rate_count
        battle_scene.tick_rate_count = 0
        battle_scene.tick_rate_timer = 0.0
