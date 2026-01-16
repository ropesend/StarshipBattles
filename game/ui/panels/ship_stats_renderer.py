"""Ship stats rendering utilities for battle panels.

This module provides rendering functions for ship statistics, resources,
weapons, and components display in the battle UI.
"""
import pygame
from game.simulation.components.component import ComponentStatus
from game.simulation.entities.ship import LayerType
from game.ai.controller import StrategyManager
from game.core.config import UIConfig


# Define standard colors for known resources (fallback to gray)
RESOURCE_COLORS = {
    'fuel': (255, 165, 0),      # Orange
    'energy': (100, 200, 255),  # Blue
    'ammo': (200, 200, 100),    # Yellow-ish
    'biomass': (100, 255, 100), # Green
    'shield': (0, 200, 255)     # Cyan
}

# Resource display order priority
RESOURCE_ORDER_PRIORITY = {'fuel': 0, 'energy': 1, 'ammo': 2}


def draw_stat_bar(surface, x, y, width, height, pct, color):
    """Draw a progress bar.

    Args:
        surface: Pygame surface to draw on
        x, y: Position of the bar
        width, height: Dimensions of the bar
        pct: Fill percentage (0.0 to 1.0)
        color: Fill color tuple (r, g, b)
    """
    pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
    if pct > 0:
        fill_w = int(width * min(1.0, pct))
        pygame.draw.rect(surface, color, (x, y, fill_w, height))
    pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height), 1)


def get_component_status_display(comp):
    """Get status text and color for a component.

    Args:
        comp: The component to check

    Returns:
        Tuple of (status_text, status_color)
    """
    status_text = ""
    status_color = (200, 200, 200)

    if not comp.is_active:
        status = getattr(comp, 'status', ComponentStatus.ACTIVE)
        if status == ComponentStatus.DAMAGED:
            status_text = "[DMG]"
            status_color = (255, 50, 50)
        elif status == ComponentStatus.NO_CREW:
            status_text = "[CREW]"
            status_color = (255, 165, 0)
        elif status == ComponentStatus.NO_POWER:
            status_text = "[PWR]"
            status_color = (255, 255, 0)
        elif status == ComponentStatus.NO_FUEL:
            status_text = "[FUEL]"
            status_color = (255, 100, 0)

    return status_text, status_color


def get_hp_bar_color(hp_pct, is_active=True):
    """Get the appropriate color for an HP bar.

    Args:
        hp_pct: HP percentage (0.0 to 1.0)
        is_active: Whether the component is active

    Returns:
        Color tuple (r, g, b)
    """
    if not is_active:
        return (100, 50, 50)
    if hp_pct > 0.5:
        return (0, 200, 0)
    elif hp_pct > 0.2:
        return (200, 200, 0)
    return (200, 50, 50)


def draw_ship_resources(surface, ship, x_indent, y, bar_w, bar_h, font):
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
    if not hasattr(ship, 'resources'):
        return y

    # Access underlying dictionary
    all_res = []
    if hasattr(ship.resources, '_resources'):
        all_res = list(ship.resources._resources.values())

    # Sort: Priority first, then alphabetical
    all_res.sort(key=lambda r: (RESOURCE_ORDER_PRIORITY.get(r.name, 99), r.name))

    for res in all_res:
        if res.max_value > 0:
            pct = res.current_value / res.max_value

            # Title case the name
            label = res.name.title()
            color = RESOURCE_COLORS.get(res.name, (180, 180, 180))

            text = font.render(f"{label}: {int(res.current_value)}/{int(res.max_value)}", True, (180, 180, 180))
            surface.blit(text, (x_indent, y))
            draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, pct, color)
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
    c_color = (200, 200, 200) if comp.is_active else (150, 50, 50)
    if not comp.is_active and getattr(comp, 'status', ComponentStatus.ACTIVE) != ComponentStatus.ACTIVE:
        c_color = (255, 100, 100)

    name_str = comp.name
    if len(name_str) > 12:
        name_str = name_str[:12] + ".."

    c_text = font.render(name_str, True, c_color)
    surface.blit(c_text, (x_indent + 5, y))

    hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
    hp_val = font.render(hp_text, True, c_color)
    surface.blit(hp_val, (x_indent + 95, y))

    hp_pct = comp.current_hp / comp.max_hp
    hp_col = get_hp_bar_color(hp_pct, comp.is_active)
    if comp.is_active and hp_pct < 0.5:
        hp_col = (200, 200, 0)

    draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, hp_col)

    status_text, status_color = get_component_status_display(comp)
    if status_text:
        st = font.render(status_text, True, status_color)
        surface.blit(st, (x_indent + 230, y))

    stats_str = f"S:{getattr(comp, 'shots_fired', 0)} H:{getattr(comp, 'shots_hit', 0)}"
    s_text = font.render(stats_str, True, (150, 150, 255))
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
    color = (150, 150, 150)
    bar_color = get_hp_bar_color(hp_pct, comp.is_active)

    if not comp.is_active:
        color = (100, 50, 50)
        bar_color = (100, 50, 50)

    name = comp.name[:10] + ".." if len(comp.name) > 12 else comp.name
    hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"

    text = font.render(name, True, color)
    surface.blit(text, (x_indent + 5, y))

    hp_val = font.render(hp_text, True, color)
    surface.blit(hp_val, (x_indent + 95, y))

    draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, bar_color)

    status_text, status_color = get_component_status_display(comp)
    if status_text:
        stat_render = font.render(status_text, True, status_color)
        surface.blit(stat_render, (x_indent + 230, y))

    return y + 14


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
        text = font.render(f"File: {ship.source_file}", True, (150, 150, 200))
        surface.blit(text, (x_indent, y))
        y += UIConfig.ELEMENT_SPACING

    strat_name = StrategyManager.instance().strategies.get(ship.ai_strategy, {}).get('name', ship.ai_strategy)
    text = font.render(f"AI: {strat_name}", True, (150, 200, 150))
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    return y


def draw_ship_vitals(surface, ship, x_indent, y, bar_w, bar_h, font):
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
        text = font.render(f"Shield: {int(ship.current_shields)}/{int(ship.max_shields)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, shield_pct, (0, 200, 255))
        y += UIConfig.ELEMENT_SPACING

    # HP
    hp_pct = ship.hp / ship.max_hp if ship.max_hp > 0 else 0
    hp_color = (0, 255, 0) if hp_pct > 0.5 else ((255, 200, 0) if hp_pct > 0.2 else (255, 50, 50))
    text = font.render(f"HP: {int(ship.hp)}/{int(ship.max_hp)}", True, (180, 180, 180))
    surface.blit(text, (x_indent, y))
    draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, hp_pct, hp_color)
    y += UIConfig.ELEMENT_SPACING

    return y


def draw_ship_combat_stats(surface, ship, x_indent, y, font):
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
    text = font.render(f"Speed: {ship.current_speed:.0f}/{ship.max_speed:.0f}", True, (180, 180, 180))
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    # Shots
    text = font.render(f"Shots: {ship.total_shots_fired}", True, (255, 200, 100))
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    # Crew
    crew_req = getattr(ship, 'crew_required', 0)
    crew_cur = getattr(ship, 'crew_onboard', 0)
    crew_color = (180, 180, 180)
    if crew_cur < crew_req:
        crew_color = (255, 100, 100)
    text = font.render(f"Crew: {crew_cur}/{crew_req}", True, crew_color)
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    # Target
    target_name = "None"
    if ship.current_target and ship.current_target.is_alive:
        target_name = getattr(ship.current_target, 'name', getattr(ship.current_target, 'type', 'Target').title())
    text = font.render(f"Target: {target_name}", True, (180, 180, 180))
    surface.blit(text, (x_indent, y))
    y += 18

    # Secondary Targets
    sec_targets = getattr(ship, 'secondary_targets', [])
    if sec_targets:
        for i, st in enumerate(sec_targets):
            if st.is_alive:
                st_name = getattr(st, 'name', getattr(st, 'type', 'Target').title())
                text = font.render(f"  T{i+2}: {st_name}", True, (150, 150, 150))
                surface.blit(text, (x_indent, y))
                y += UIConfig.ELEMENT_SPACING

    # Targeting Cap
    max_targets = getattr(ship, 'max_targets', 1)
    cap_text = "Single" if max_targets == 1 else f"Multi ({max_targets})"
    text = font.render(f"Sys: {cap_text}", True, (150, 150, 150))
    surface.blit(text, (x_indent + 200, y - 18))

    return y


def draw_ship_weapons(surface, ship, x_indent, y, panel_w, font):
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
    text = font.render("Weapons:", True, (200, 200, 150))
    surface.blit(text, (x_indent, y))
    y += 18

    for layer_type in [LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
        layer = ship.layers.get(layer_type)
        if not layer:
            continue

        for comp in layer['components']:
            if comp.has_ability('WeaponAbility'):
                y = draw_weapon_entry(surface, comp, x_indent, y, panel_w, font)

    return y + 8


def draw_ship_components(surface, ship, x_indent, y, font):
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
    text = font.render("Components:", True, (200, 200, 100))
    surface.blit(text, (x_indent, y))
    y += UIConfig.ELEMENT_SPACING

    for layer_type in [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
        layer = ship.layers.get(layer_type)
        if not layer:
            continue

        for comp in layer['components']:
            if comp.has_ability('WeaponAbility'):
                continue
            y = draw_component_entry(surface, comp, x_indent, y, font)

    return y + 5
