"""Species selector mixin for planet environment editors.

Provides a dropdown for selecting which species' preferences to use
when multiple species are present on a planet. Used by atmosphere,
gravity, water, and radiation editors.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Any

import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIDropDownMenu

logger = logging.getLogger(__name__)


def build_species_selector(
    planet,
    container,
    manager: pygame_gui.UIManager,
    y: int,
    width: int,
) -> tuple:
    """Build species selector UI elements if multiple species are present.

    Args:
        planet: Planet with populations list.
        container: UI container (window).
        manager: UI manager.
        y: Current y position for layout.
        width: Available width.

    Returns:
        Tuple of (dropdown_or_None, widgets_list, new_y, default_race_id).
        If only one species (or none), dropdown is None and default_race_id
        is the single species' race_id (or None).
    """
    populations = getattr(planet, 'populations', [])
    widgets = []

    if not populations:
        return None, widgets, y, None

    # Sort by count descending (most populous first)
    sorted_pops = sorted(populations, key=lambda p: getattr(p, 'count', 0), reverse=True)
    default_race_id = sorted_pops[0].race_id

    if len(sorted_pops) == 1:
        # Single species — no dropdown needed, just show the name
        return None, widgets, y, default_race_id

    # Multiple species — build dropdown
    lbl = UILabel(
        pygame.Rect(10, y, 60, 25),
        text="Species:",
        manager=manager,
        container=container,
    )
    widgets.append(lbl)

    # Build option strings: "Race Name (Nk)" format
    options = []
    race_id_map = {}  # option_string -> race_id
    for pop in sorted_pops:
        count = getattr(pop, 'count', 0)
        race_id = getattr(pop, 'race_id', 'unknown')
        # Format population count
        if count >= 1000:
            count_str = f"{count / 1000:.0f}M"
        else:
            count_str = f"{count}k"
        option_str = f"{race_id} ({count_str})"
        options.append(option_str)
        race_id_map[option_str] = race_id

    dropdown = UIDropDownMenu(
        options_list=options,
        starting_option=options[0],
        relative_rect=pygame.Rect(75, y, width - 85, 25),
        manager=manager,
        container=container,
    )
    dropdown._race_id_map = race_id_map
    widgets.append(dropdown)

    y += 30
    return dropdown, widgets, y, default_race_id


def get_selected_race_id(dropdown) -> Optional[str]:
    """Get the race_id from the currently selected dropdown option.

    Args:
        dropdown: UIDropDownMenu with _race_id_map attribute, or None.

    Returns:
        race_id string, or None if no dropdown.
    """
    if dropdown is None:
        return None
    selected = dropdown.selected_option
    # Handle pygame_gui returning tuple or string depending on version
    if isinstance(selected, tuple):
        selected = selected[0]
    race_id_map = getattr(dropdown, '_race_id_map', {})
    return race_id_map.get(selected)


def load_race_config(race_id: Optional[str]) -> Any | None:
    """Load a RaceConfig by race_id.

    Args:
        race_id: Race identifier string.

    Returns:
        RaceConfig instance, or None if not found.
    """
    if not race_id:
        return None
    try:
        from game.strategy.systems.race_library import RaceLibrary
        race_lib = RaceLibrary()
        return race_lib.get_race(race_id)
    except Exception:  # Intentional broad catch: RaceLibrary load surfaces I/O, JSON, and schema-validation errors; UI mixin must not crash species selection on bad data
        logger.warning("Failed to load race config for %s", race_id)
        return None
