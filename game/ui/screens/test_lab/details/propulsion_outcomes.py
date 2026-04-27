"""Propulsion outcomes for the test-run-details panel.

PROJ-309 sub-phase 3.6 — extracted verbatim from `test_run_details.py`.
Test-id-prefix-driven: only renders for `PROP-###` test ids. Three
sub-renderers (turn / motion / stationary) selected by metrics-based
heuristic.

Behaviour preserved exactly — no format-string changes.
"""
from __future__ import annotations

import pygame

from game.ui.screens.test_lab import theme

from .draw_context import DetailsDrawContext, OutcomePalette


def is_propulsion_test(run_record) -> bool:
    """True if this run record is from a propulsion test (PROP-### prefix)."""
    test_id = run_record.metrics.get('test_id', '')
    return test_id.startswith('PROP-')


def draw_propulsion_outcomes(
    ctx: DetailsDrawContext,
    run_record,
    y_offset: int,
) -> int:
    """Draw propulsion test outcomes section."""
    surface = ctx.surface
    metrics = run_record.metrics

    # Section header
    outcomes_title = ctx.header_font.render("TEST OUTCOMES", True, ctx.header_color)
    surface.blit(outcomes_title, (ctx.x + 10, y_offset))
    y_offset += 25

    # Draw separator line
    pygame.draw.line(surface, theme.SEPARATOR_LINE,
                    (ctx.x + 10, y_offset), (ctx.x + ctx.width - 20, y_offset))
    y_offset += 8

    # Determine test type based on metrics
    is_turn_test = (
        metrics.get('angle_change', 0) > 0.01 and
        metrics.get('turn_speed', 0) > 0
    )
    has_motion = metrics.get('final_velocity_magnitude', 0) > 0.1

    # Define palette
    palette = OutcomePalette(
        label_color=theme.TEXT_LABEL,
        value_color=theme.TEXT_EXPECTED,
        highlight_color=theme.STATUS_HIGHLIGHT,
        indent=15,
        label_width=75,  # propulsion uses a wider 75px gutter (+75 in original)
    )

    if is_turn_test:
        # Turn test outcomes
        y_offset = _draw_turn_outcomes(ctx, metrics, y_offset, palette)
    elif has_motion:
        # Motion test outcomes
        y_offset = _draw_motion_outcomes(ctx, metrics, y_offset, palette)
    else:
        # Stationary test
        y_offset = _draw_stationary_outcomes(ctx, metrics, y_offset, palette)

    return y_offset


def _draw_motion_outcomes(
    ctx: DetailsDrawContext,
    metrics,
    y_offset: int,
    palette: OutcomePalette,
) -> int:
    """Draw motion test outcomes (velocity, position, distance)."""
    surface = ctx.surface
    label_color = palette.label_color
    value_color = palette.value_color
    highlight_color = palette.highlight_color
    indent = palette.indent

    # Velocity
    start_vel = metrics.get('initial_velocity_magnitude', 0)
    end_vel = metrics.get('final_velocity_magnitude', 0)
    max_speed = metrics.get('expected_max_speed')

    vel_label = ctx.small_font.render("Velocity:", True, label_color)
    surface.blit(vel_label, (ctx.x + indent, y_offset))

    vel_text = f"{start_vel:.1f} -> {end_vel:.2f}"
    if max_speed is not None:
        vel_text += f" (max: {max_speed:.2f})"
    vel_surf = ctx.small_font.render(vel_text, True, value_color)
    surface.blit(vel_surf, (ctx.x + indent + 75, y_offset))
    y_offset += 18

    # Position
    start_pos = metrics.get('initial_position')
    end_pos = metrics.get('final_position')
    if start_pos and end_pos:
        pos_label = ctx.small_font.render("Position:", True, label_color)
        surface.blit(pos_label, (ctx.x + indent, y_offset))

        start_str = f"({start_pos[0]:.1f}, {start_pos[1]:.1f})"
        end_str = f"({end_pos[0]:.1f}, {end_pos[1]:.1f})"
        pos_text = f"{start_str} -> {end_str}"
        pos_surf = ctx.small_font.render(pos_text, True, value_color)
        surface.blit(pos_surf, (ctx.x + indent + 75, y_offset))
        y_offset += 18

    # Distance
    distance = metrics.get('distance_traveled')
    if distance is not None:
        dist_label = ctx.small_font.render("Distance:", True, label_color)
        surface.blit(dist_label, (ctx.x + indent, y_offset))

        dist_surf = ctx.small_font.render(f"{distance:.1f} px", True, highlight_color)
        surface.blit(dist_surf, (ctx.x + indent + 75, y_offset))
        y_offset += 18

    return y_offset


def _draw_turn_outcomes(
    ctx: DetailsDrawContext,
    metrics,
    y_offset: int,
    palette: OutcomePalette,
) -> int:
    """Draw turn test outcomes (angles, expected vs actual)."""
    surface = ctx.surface
    label_color = palette.label_color
    value_color = palette.value_color
    highlight_color = palette.highlight_color
    indent = palette.indent

    # Angle change
    start_angle = metrics.get('initial_angle', 0)
    end_angle = metrics.get('final_angle', 0)
    angle_change = metrics.get('angle_change', 0)

    angle_label = ctx.small_font.render("Angle:", True, label_color)
    surface.blit(angle_label, (ctx.x + indent, y_offset))

    angle_text = f"{start_angle:.1f} -> {end_angle:.1f} deg (change: {angle_change:.2f})"
    angle_surf = ctx.small_font.render(angle_text, True, value_color)
    surface.blit(angle_surf, (ctx.x + indent + 75, y_offset))
    y_offset += 18

    # Expected vs actual angle change
    expected_angle = metrics.get('expected_angle_change')
    if expected_angle is not None:
        exp_label = ctx.small_font.render("Expected:", True, label_color)
        surface.blit(exp_label, (ctx.x + indent, y_offset))

        exp_text = f"{expected_angle:.2f} deg"
        exp_surf = ctx.small_font.render(exp_text, True, value_color)
        surface.blit(exp_surf, (ctx.x + indent + 75, y_offset))
        y_offset += 18

        act_label = ctx.small_font.render("Actual:", True, label_color)
        surface.blit(act_label, (ctx.x + indent, y_offset))

        # Color code based on accuracy
        error = abs(angle_change - expected_angle)
        actual_color = ctx.pass_color if error < 0.1 else ctx.fail_color
        act_text = f"{angle_change:.2f} deg"
        act_surf = ctx.small_font.render(act_text, True, actual_color)
        surface.blit(act_surf, (ctx.x + indent + 75, y_offset))
        y_offset += 18

        # Show error
        err_label = ctx.small_font.render("Error:", True, label_color)
        surface.blit(err_label, (ctx.x + indent, y_offset))

        err_text = f"{error:.4f} deg"
        err_color = ctx.pass_color if error < 0.1 else ctx.fail_color
        err_surf = ctx.small_font.render(err_text, True, err_color)
        surface.blit(err_surf, (ctx.x + indent + 75, y_offset))
        y_offset += 18

    # Turn speed
    turn_speed = metrics.get('turn_speed')
    if turn_speed is not None:
        ts_label = ctx.small_font.render("Turn Speed:", True, label_color)
        surface.blit(ts_label, (ctx.x + indent, y_offset))

        ts_text = f"{turn_speed:.4f} deg/100 ticks"
        ts_surf = ctx.small_font.render(ts_text, True, highlight_color)
        surface.blit(ts_surf, (ctx.x + indent + 75, y_offset))
        y_offset += 18

    return y_offset


def _draw_stationary_outcomes(
    ctx: DetailsDrawContext,
    metrics,
    y_offset: int,
    palette: OutcomePalette,
) -> int:
    """Draw stationary test outcomes (no motion)."""
    surface = ctx.surface
    label_color = palette.label_color
    value_color = palette.value_color
    indent = palette.indent

    # Show that velocity is zero
    vel_label = ctx.small_font.render("Velocity:", True, label_color)
    surface.blit(vel_label, (ctx.x + indent, y_offset))

    vel_surf = ctx.small_font.render("0.0 (stationary)", True, value_color)
    surface.blit(vel_surf, (ctx.x + indent + 75, y_offset))
    y_offset += 18

    # Distance should be zero
    distance = metrics.get('distance_traveled', 0)
    dist_label = ctx.small_font.render("Distance:", True, label_color)
    surface.blit(dist_label, (ctx.x + indent, y_offset))

    dist_surf = ctx.small_font.render(f"{distance:.1f} px", True, value_color)
    surface.blit(dist_surf, (ctx.x + indent + 75, y_offset))
    y_offset += 18

    return y_offset
