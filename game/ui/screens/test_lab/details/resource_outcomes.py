"""Resource consumption outcomes for the test-run-details panel.

PROJ-309 sub-phase 3.6 — extracted verbatim from `test_run_details.py`.
Test-id-prefix-driven: only renders for `RESOURCE-###` test ids. Three
sub-renderers (fuel / energy / ammo) keyed off the test id range.

Behaviour preserved exactly — no format-string changes.
"""
from __future__ import annotations

import pygame

from game.ui.screens.test_lab import theme

from .draw_context import DetailsDrawContext, OutcomePalette


def is_resource_test(run_record) -> bool:
    """True if this run record is from a resource test (RESOURCE-### prefix)."""
    test_id = run_record.metrics.get('test_id', '')
    return test_id.startswith('RESOURCE-')


def draw_resource_outcomes(
    ctx: DetailsDrawContext,
    run_record,
    y_offset: int,
) -> int:
    """Draw resource test outcomes section (detailed view)."""
    surface = ctx.surface
    metrics = run_record.metrics
    test_id = metrics.get('test_id', '')

    # Section header
    outcomes_title = ctx.header_font.render("RESOURCE CONSUMPTION", True, ctx.header_color)
    surface.blit(outcomes_title, (ctx.x + 10, y_offset))
    y_offset += 25

    # Draw separator line
    pygame.draw.line(surface, theme.SEPARATOR_LINE,
                    (ctx.x + 10, y_offset), (ctx.x + ctx.width - 20, y_offset))
    y_offset += 8

    # Define palette (was 5 separate positional args in the original)
    palette = OutcomePalette(
        label_color=theme.TEXT_LABEL,
        value_color=theme.TEXT_EXPECTED,
        highlight_color=theme.STATUS_HIGHLIGHT,
        indent=15,
        label_width=100,
    )

    # Determine resource type and draw appropriate outcomes
    if 'RESOURCE-001' <= test_id <= 'RESOURCE-003':
        # Fuel tests
        y_offset = _draw_fuel_outcomes(ctx, metrics, y_offset, palette)
    elif 'RESOURCE-004' <= test_id <= 'RESOURCE-005a':
        # Energy tests
        y_offset = _draw_energy_outcomes(ctx, metrics, y_offset, palette)
    else:
        # Ammo tests (RESOURCE-006 to RESOURCE-008)
        y_offset = _draw_ammo_outcomes(ctx, metrics, y_offset, palette, test_id)

    return y_offset


def _draw_fuel_outcomes(
    ctx: DetailsDrawContext,
    metrics,
    y_offset: int,
    palette: OutcomePalette,
) -> int:
    """Draw fuel test outcomes."""
    surface = ctx.surface
    label_color = palette.label_color
    value_color = palette.value_color
    highlight_color = palette.highlight_color
    indent = palette.indent
    label_width = palette.label_width

    initial_fuel = metrics.get('initial_fuel', 0)
    final_fuel = metrics.get('final_fuel', 0)
    fuel_consumed = initial_fuel - final_fuel
    expected_consumed = metrics.get('expected_fuel_consumed', fuel_consumed)

    # Initial Fuel
    label = ctx.small_font.render("Initial Fuel:", True, label_color)
    value = ctx.small_font.render(f"{initial_fuel:.1f} units", True, value_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Final Fuel
    label = ctx.small_font.render("Final Fuel:", True, label_color)
    value = ctx.small_font.render(f"{final_fuel:.1f} units", True, value_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Consumed
    label = ctx.small_font.render("Consumed:", True, label_color)
    value = ctx.small_font.render(f"{fuel_consumed:.2f} units", True, highlight_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Expected
    label = ctx.small_font.render("Expected:", True, label_color)
    expected_text = f"{expected_consumed:.2f} units"
    value = ctx.small_font.render(expected_text, True, value_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Tolerance check
    tolerance = abs(fuel_consumed - expected_consumed)
    if tolerance < 0.5:
        status_text = "Within tolerance"
        status_color = ctx.pass_color
    else:
        status_text = f"Difference: {tolerance:.2f}"
        status_color = ctx.fail_color
    status_surf = ctx.small_font.render(status_text, True, status_color)
    surface.blit(status_surf, (ctx.x + indent, y_offset))
    y_offset += 18

    # Velocity status
    final_velocity = metrics.get('final_velocity', 0)
    label = ctx.small_font.render("Final Velocity:", True, label_color)
    if final_velocity > 0.1:
        vel_text = f"{final_velocity:.2f} (moving)"
        vel_color = ctx.pass_color
    else:
        vel_text = "0 (stopped)"
        vel_color = theme.STATUS_WARNING
    value = ctx.small_font.render(vel_text, True, vel_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    return y_offset


def _draw_energy_outcomes(
    ctx: DetailsDrawContext,
    metrics,
    y_offset: int,
    palette: OutcomePalette,
) -> int:
    """Draw energy test outcomes."""
    surface = ctx.surface
    label_color = palette.label_color
    value_color = palette.value_color
    highlight_color = palette.highlight_color
    indent = palette.indent
    label_width = palette.label_width

    initial_energy = metrics.get('initial_energy', 0)
    final_energy = metrics.get('final_energy', 0)
    energy_consumed = initial_energy - final_energy
    shots_fired = metrics.get('shots_fired', 0)
    damage_dealt = metrics.get('damage_dealt', 0)

    # Initial Energy
    label = ctx.small_font.render("Initial Energy:", True, label_color)
    value = ctx.small_font.render(f"{initial_energy:.1f} units", True, value_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Final Energy
    label = ctx.small_font.render("Final Energy:", True, label_color)
    if final_energy <= 0:
        energy_text = "0 (depleted)"
        energy_color = theme.STATUS_WARNING
    else:
        energy_text = f"{final_energy:.1f} units"
        energy_color = value_color
    value = ctx.small_font.render(energy_text, True, energy_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Energy Consumed
    label = ctx.small_font.render("Consumed:", True, label_color)
    value = ctx.small_font.render(f"{energy_consumed:.1f} units", True, highlight_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Shots Fired
    label = ctx.small_font.render("Shots Fired:", True, label_color)
    value = ctx.small_font.render(f"{shots_fired}", True, value_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Damage Dealt
    label = ctx.small_font.render("Damage Dealt:", True, label_color)
    value = ctx.small_font.render(f"{damage_dealt:.0f}", True, highlight_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Efficiency (energy per damage)
    if damage_dealt > 0:
        efficiency = energy_consumed / damage_dealt
        label = ctx.small_font.render("Energy/Damage:", True, label_color)
        value = ctx.small_font.render(f"{efficiency:.2f}", True, value_color)
        surface.blit(label, (ctx.x + indent, y_offset))
        surface.blit(value, (ctx.x + indent + label_width, y_offset))
        y_offset += 18

    return y_offset


def _draw_ammo_outcomes(
    ctx: DetailsDrawContext,
    metrics,
    y_offset: int,
    palette: OutcomePalette,
    test_id: str,
) -> int:
    """Draw ammo test outcomes."""
    surface = ctx.surface
    label_color = palette.label_color
    value_color = palette.value_color
    highlight_color = palette.highlight_color
    indent = palette.indent
    label_width = palette.label_width

    initial_ammo = metrics.get('initial_ammo', 0)
    final_ammo = metrics.get('final_ammo', 0)
    ammo_consumed = initial_ammo - final_ammo

    is_seeker = test_id == 'RESOURCE-008'
    shots_fired = metrics.get('launches' if is_seeker else 'shots_fired', 0)

    # Initial Ammo
    label = ctx.small_font.render("Initial Ammo:", True, label_color)
    value = ctx.small_font.render(f"{initial_ammo:.0f} units", True, value_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Final Ammo
    label = ctx.small_font.render("Final Ammo:", True, label_color)
    if final_ammo <= 0:
        ammo_text = "0 (depleted)"
        ammo_color = theme.STATUS_WARNING
    else:
        ammo_text = f"{final_ammo:.0f} units"
        ammo_color = value_color
    value = ctx.small_font.render(ammo_text, True, ammo_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Ammo Consumed
    label = ctx.small_font.render("Consumed:", True, label_color)
    value = ctx.small_font.render(f"{ammo_consumed:.0f} units", True, highlight_color)
    surface.blit(label, (ctx.x + indent, y_offset))
    surface.blit(value, (ctx.x + indent + label_width, y_offset))
    y_offset += 18

    # Shots/Launches
    if is_seeker:
        label = ctx.small_font.render("Launches:", True, label_color)
        value = ctx.small_font.render(f"{shots_fired}", True, value_color)
        surface.blit(label, (ctx.x + indent, y_offset))
        surface.blit(value, (ctx.x + indent + label_width, y_offset))
        y_offset += 18

        # Note about seeker hits
        note = ctx.small_font.render("(Hits not tracked - seekers in flight)", True, theme.TEXT_DIM_BLUE)
        surface.blit(note, (ctx.x + indent, y_offset))
        y_offset += 18
    else:
        # Shots Fired
        label = ctx.small_font.render("Shots Fired:", True, label_color)
        value = ctx.small_font.render(f"{shots_fired}", True, value_color)
        surface.blit(label, (ctx.x + indent, y_offset))
        surface.blit(value, (ctx.x + indent + label_width, y_offset))
        y_offset += 18

        # Damage Dealt
        damage_dealt = metrics.get('damage_dealt', 0)
        label = ctx.small_font.render("Damage Dealt:", True, label_color)
        value = ctx.small_font.render(f"{damage_dealt:.0f}", True, highlight_color)
        surface.blit(label, (ctx.x + indent, y_offset))
        surface.blit(value, (ctx.x + indent + label_width, y_offset))
        y_offset += 18

    return y_offset
