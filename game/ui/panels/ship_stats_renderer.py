"""Ship stats rendering utilities for battle panels.

This module provides rendering functions for ship statistics, resources,
weapons, and components display in the battle UI.

PROJ-40: Import LayerType from core/constants (canonical location).
ComponentStatus import from simulation layer is acceptable for status display.
StrategyMetadataService is used for strategy name display - core layer access.
"""
from typing import TYPE_CHECKING

import pygame
from game.simulation.components.component_constants import ComponentStatus

if TYPE_CHECKING:
    from game.core.protocols import ICombatShip
from game.core.strategy_metadata import StrategyMetadataService
from game.ui.config import UIConfig
from game.ui.colors import (
    RESOURCE_FUEL, RESOURCE_ENERGY, RESOURCE_AMMO, RESOURCE_SHIELD, RESOURCE_BIOMASS,
    HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, TEXT_MUTED, TEXT_SECONDARY, TEXT_ITEM,
    BAR_BG, BAR_BORDER, COMPONENT_NO_POWER, COMPONENT_NO_FUEL, COMPONENT_INACTIVE_BG,
    STATUS_DERELICT, WEAPON_STATS_TEXT, SECTION_HEADER_WEAPONS, SECTION_HEADER_COMPONENTS,
    AI_STRATEGY_TEXT, METADATA_FILE_TEXT, SEEKER_TITLE, WEAPON_INACTIVE, WEAPON_INACTIVE_STATUS,
    CREW_LOW
)
from game.ui.utils.formatters import get_damage_color
from game.core.constants import CombatConstants


# Define standard colors for known resources (fallback to gray)
RESOURCE_COLORS = {
    "fuel": RESOURCE_FUEL,
    "energy": RESOURCE_ENERGY,
    "ammo": RESOURCE_AMMO,
    'biomass': RESOURCE_BIOMASS,
    'shield': RESOURCE_SHIELD
}

# Resource display order priority
RESOURCE_ORDER_PRIORITY = {"fuel": 0, "energy": 1, "ammo": 2}


def draw_stat_bar(surface, x, y, width, height, pct, color):
    """Draw a progress bar.

    Args:
        surface: Pygame surface to draw on
        x, y: Position of the bar
        width, height: Dimensions of the bar
        pct: Fill percentage (0.0 to 1.0)
        color: Fill color tuple (r, g, b)
    """
    pygame.draw.rect(surface, BAR_BG, (x, y, width, height))
    if pct > 0:
        fill_w = int(width * min(1.0, pct))
        pygame.draw.rect(surface, color, (x, y, fill_w, height))
    pygame.draw.rect(surface, BAR_BORDER, (x, y, width, height), 1)


def get_component_status_display(comp):
    """Get status text and color for a component.

    Args:
        comp: The component to check

    Returns:
        Tuple of (status_text, status_color)
    """
    status_text = ""
    status_color = TEXT_ITEM

    if not comp.is_active:
        status = getattr(comp, 'status', ComponentStatus.ACTIVE)
        if status == ComponentStatus.DAMAGED:
            status_text = "[DMG]"
            status_color = HP_CRITICAL
        elif status == ComponentStatus.NO_CREW:
            status_text = "[CREW]"
            status_color = STATUS_DERELICT
        elif status == ComponentStatus.NO_POWER:
            status_text = "[PWR]"
            status_color = COMPONENT_NO_POWER
        elif status == ComponentStatus.NO_FUEL:
            status_text = "[FUEL]"
            status_color = COMPONENT_NO_FUEL

    return status_text, status_color


def get_hp_bar_color(hp_pct, is_active=True):
    """Get the appropriate color for an HP bar.

    Delegates to the shared ``get_damage_color`` utility for HP-based
    color mapping, but returns ``COMPONENT_INACTIVE_BG`` for inactive
    components (specific to combat HP bar rendering).

    Args:
        hp_pct: HP percentage (0.0 to 1.0)
        is_active: Whether the component is active

    Returns:
        Color tuple (r, g, b)
    """
    if not is_active:
        return COMPONENT_INACTIVE_BG
    return get_damage_color(hp_pct)


def draw_ship_resources(surface, ship: 'ICombatShip', x_indent, y, bar_w, bar_h, font):
    """Draw resource bars for a ship.

    Args:
        surface: Pygame surface to draw on
        ship: The ship whose resources to display
        x_indent: X indentation for drawing
        y: Starting Y position
        bar_w: Width of resource bars
        bar_h: Height of resource bars
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    # ICombatShip.resources can be None for ships without consumables
    if not ship.resources:
        return y

    # Get all resources via public API
    all_res = ship.resources.get_all_resources()

    # Sort: Priority first, then alphabetical
    all_res.sort(key=lambda r: (RESOURCE_ORDER_PRIORITY.get(r.name, 99), r.name))

    for res in all_res:
        if res.max_value > 0:
            pct = res.current_value / res.max_value

            # Title case the name
            label = res.name.title()
            color = RESOURCE_COLORS.get(res.name, TEXT_SECONDARY)

            text = font.render(f"{label}: {int(res.current_value)}/{int(res.max_value)}", True, TEXT_SECONDARY)
            surface.blit(text, (x_indent, y))
            draw_stat_bar(surface, x_indent + 300, y, bar_w, bar_h, pct, color)
            y += UIConfig.ELEMENT_SPACING

    return y


def draw_weapon_entry(surface, comp, x_indent, y, panel_w, font):
    """Draw a single weapon component entry.

    Args:
        surface: Pygame surface to draw on
        comp: Weapon component to display
        x_indent: X indentation for drawing
        y: Y position
        panel_w: Panel width for layout
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    c_color = TEXT_ITEM if comp.is_active else WEAPON_INACTIVE
    if not comp.is_active and getattr(comp, 'status', ComponentStatus.ACTIVE) != ComponentStatus.ACTIVE:
        c_color = WEAPON_INACTIVE_STATUS

    name_str = comp.name
    if len(name_str) > 25:
        name_str = name_str[:25] + ".."

    c_text = font.render(name_str, True, c_color)
    surface.blit(c_text, (x_indent + 5, y))

    hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
    hp_val = font.render(hp_text, True, c_color)
    surface.blit(hp_val, (x_indent + 200, y))

    hp_pct = comp.current_hp / comp.max_hp
    hp_col = get_hp_bar_color(hp_pct, comp.is_active)
    if comp.is_active and hp_pct < 0.5:
        hp_col = HP_DAMAGED

    draw_stat_bar(surface, x_indent + 420, y, 120, 8, hp_pct, hp_col)

    status_text, status_color = get_component_status_display(comp)
    if status_text:
        st = font.render(status_text, True, status_color)
        surface.blit(st, (x_indent + 560, y))

    stats_str = f"S:{getattr(comp, 'shots_fired', 0)} H:{getattr(comp, 'shots_hit', 0)}"
    s_text = font.render(stats_str, True, WEAPON_STATS_TEXT)
    s_x = panel_w - s_text.get_width() - 10
    surface.blit(s_text, (s_x, y))

    return y + UIConfig.ELEMENT_SPACING


def draw_component_entry(surface, comp, x_indent, y, font):
    """Draw a single non-weapon component entry.

    Args:
        surface: Pygame surface to draw on
        comp: Component to display
        x_indent: X indentation for drawing
        y: Y position
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    hp_pct = comp.current_hp / comp.max_hp if comp.max_hp > 0 else 1.0
    color = TEXT_MUTED
    bar_color = get_hp_bar_color(hp_pct, comp.is_active)

    if not comp.is_active:
        color = COMPONENT_INACTIVE_BG
        bar_color = COMPONENT_INACTIVE_BG

    name = comp.name[:23] + ".." if len(comp.name) > 25 else comp.name
    hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"

    text = font.render(name, True, color)
    surface.blit(text, (x_indent + 5, y))

    hp_val = font.render(hp_text, True, color)
    surface.blit(hp_val, (x_indent + 200, y))

    draw_stat_bar(surface, x_indent + 420, y, 120, 8, hp_pct, bar_color)

    status_text, status_color = get_component_status_display(comp)
    if status_text:
        stat_render = font.render(status_text, True, status_color)
        surface.blit(stat_render, (x_indent + 560, y))

    return y + UIConfig.ELEMENT_SPACING


def draw_ship_info_header(surface, ship, x_indent, y, font):
    """Draw ship info header (file, AI strategy).

    Args:
        surface: Pygame surface to draw on
        ship: The ship to display info for
        x_indent: X indentation for drawing
        y: Starting Y position
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    if hasattr(ship, 'source_file') and ship.source_file:
        text = font.render(f"File: {ship.source_file}", True, METADATA_FILE_TEXT)
        surface.blit(text, (x_indent, y))
        y += UIConfig.ELEMENT_SPACING

    strat_name = StrategyMetadataService.instance().strategies.get(ship.ai_strategy, {}).get('name', ship.ai_strategy)
    text = font.render(f"AI: {strat_name}", True, AI_STRATEGY_TEXT)
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    return y


def draw_ship_vitals(surface, ship: 'ICombatShip', x_indent, y, bar_w, bar_h, font):
    """Draw ship vital stats (shield, HP).

    Args:
        surface: Pygame surface to draw on
        ship: The ship to display
        x_indent: X indentation for drawing
        y: Starting Y position
        bar_w: Width of stat bars
        bar_h: Height of stat bars
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    # Shield
    if ship.max_shields > 0:
        shield_pct = ship.current_shields / ship.max_shields
        text = font.render(f"Shield: {int(ship.current_shields)}/{int(ship.max_shields)}", True, TEXT_SECONDARY)
        surface.blit(text, (x_indent, y))
        draw_stat_bar(surface, x_indent + 300, y, bar_w, bar_h, shield_pct, RESOURCE_SHIELD)
        y += UIConfig.ELEMENT_SPACING

    # HP
    hp_pct = ship.hp / ship.max_hp if ship.max_hp > 0 else 0
    hp_color = HP_HEALTHY if hp_pct > 0.5 else (HP_DAMAGED if hp_pct > 0.2 else HP_CRITICAL)
    text = font.render(f"HP: {int(ship.hp)}/{int(ship.max_hp)}", True, TEXT_SECONDARY)
    surface.blit(text, (x_indent, y))
    draw_stat_bar(surface, x_indent + 300, y, bar_w, bar_h, hp_pct, hp_color)
    y += UIConfig.ELEMENT_SPACING

    return y


def draw_ship_combat_stats(surface, ship: 'ICombatShip', x_indent, y, font):
    """Draw ship combat stats (speed, shots, crew, target).

    Args:
        surface: Pygame surface to draw on
        ship: The ship to display
        x_indent: X indentation for drawing
        y: Starting Y position
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    # Speed
    text = font.render(f"Speed: {ship.current_speed:.0f}/{ship.max_speed:.0f}", True, TEXT_SECONDARY)
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    # Shots
    text = font.render(f"Shots: {ship.total_shots_fired}", True, SEEKER_TITLE)
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    # Crew
    crew_req = getattr(ship, 'crew_required', 0)
    crew_cur = getattr(ship, 'crew_onboard', 0)
    crew_color = TEXT_SECONDARY
    if crew_cur < crew_req:
        crew_color = CREW_LOW
    text = font.render(f"Crew: {crew_cur}/{crew_req}", True, crew_color)
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    # Target (uses DTO string fields, not entity references)
    target_name = ship.current_target_name or "None"
    text = font.render(f"Target: {target_name}", True, TEXT_SECONDARY)
    surface.blit(text, (x_indent, y))
    y += 18

    # Secondary Targets (uses DTO name list)
    sec_target_names = ship.secondary_target_names
    if sec_target_names:
        for i, st_name in enumerate(sec_target_names):
            text = font.render(f"  T{i+2}: {st_name}", True, TEXT_MUTED)
            surface.blit(text, (x_indent, y))
            y += UIConfig.ELEMENT_SPACING

    # Targeting Cap
    max_targets = ship.max_targets
    cap_text = "Single" if max_targets == CombatConstants.DEFAULT_MAX_TARGETS else f"Multi ({max_targets})"
    text = font.render(f"Sys: {cap_text}", True, TEXT_MUTED)
    surface.blit(text, (x_indent + 400, y - 18))

    return y


def draw_ship_weapons(surface, ship: 'ICombatShip', x_indent, y, panel_w, font):
    """Draw all weapon components for a ship.

    Args:
        surface: Pygame surface to draw on
        ship: The ship to display
        x_indent: X indentation for drawing
        y: Starting Y position
        panel_w: Panel width for layout
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    text = font.render("Weapons:", True, SECTION_HEADER_WEAPONS)
    surface.blit(text, (x_indent, y))
    y += 18

    for comp in ship.components:
        if comp.has_weapon:
            y = draw_weapon_entry(surface, comp, x_indent, y, panel_w, font)

    return y + 8


def draw_ship_components(surface, ship: 'ICombatShip', x_indent, y, font):
    """Draw all non-weapon components for a ship.

    Args:
        surface: Pygame surface to draw on
        ship: The ship to display
        x_indent: X indentation for drawing
        y: Starting Y position
        font: Font for text rendering

    Returns:
        Updated Y position after drawing
    """
    text = font.render("Components:", True, SECTION_HEADER_COMPONENTS)
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    for comp in ship.components:
        if not comp.has_weapon:
            y = draw_component_entry(surface, comp, x_indent, y, font)

    return y + 5
