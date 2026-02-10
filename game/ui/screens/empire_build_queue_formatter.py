"""Data formatting functions for empire build queue display.

Pure data transform functions with no UI dependencies. These format
BuildQueueSource data into human-readable strings for the
EmpireBuildQueueWindow display.

Created as part of PROJ-89 Phase 2.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.build_queue_source import BuildQueueSource


def get_queue_summary(source: BuildQueueSource) -> str:
    """Return a short summary of queue contents.

    Args:
        source: The build queue source to summarize.

    Returns:
        Dash if empty, otherwise item count string.
    """
    count = len(source.construction_queue)
    if count == 0:
        return "-"
    return f"{count} item{'s' if count != 1 else ''}"


def get_first_item_text(source: BuildQueueSource) -> str:
    """Return the name of the first item being built.

    Args:
        source: The build queue source.

    Returns:
        Design ID of first item with turns, or dash if empty.
    """
    if not source.construction_queue:
        return "-"
    first = source.construction_queue[0]
    design_id = first.get("design_id", "Unknown")
    turns = first.get("turns_remaining", "?")
    return f"{design_id} ({turns}t)"


def get_capabilities_text(source: BuildQueueSource) -> str:
    """Return human-readable capabilities string.

    Args:
        source: The build queue source.

    Returns:
        'Ships', 'Complexes', 'Ships & Complexes', or 'None'.
    """
    if source.can_build_ships and source.can_build_complexes:
        return "Ships & Complexes"
    if source.can_build_ships:
        return "Ships"
    if source.can_build_complexes:
        return "Complexes"
    return "None"


def get_system_name(source: BuildQueueSource, galaxy: Any) -> str:
    """Return the system name for a queue source.

    Args:
        source: The build queue source.
        galaxy: Galaxy instance for system lookups.

    Returns:
        System name string, or dash if unavailable.
    """
    entity = source.owner_entity
    if source.context_type == "planet":
        system = getattr(entity, 'system_name', None)
        if system:
            return str(system)
        # Try galaxy lookup
        if galaxy and hasattr(galaxy, 'get_system_of_planet'):
            sys_obj = galaxy.get_system_of_planet(entity)
            if sys_obj:
                return getattr(sys_obj, 'name', '-')
    elif source.context_type == "fleet":
        location = getattr(entity, 'location', None)
        if location and galaxy and hasattr(galaxy, 'get_system_at_hex'):
            sys_obj = galaxy.get_system_at_hex(location)
            if sys_obj:
                return getattr(sys_obj, 'name', '-')
    return "-"


def get_sector_text(source: BuildQueueSource) -> str:
    """Return sector/hex coordinate text for a queue source.

    Args:
        source: The build queue source.

    Returns:
        Hex coordinate string, or dash if unavailable.
    """
    entity = source.owner_entity
    if source.context_type == "fleet":
        location = getattr(entity, 'location', None)
        if location is not None:
            return str(location)
    elif source.context_type == "planet":
        # Planets may have hex or relative location
        hex_loc = getattr(entity, 'global_hex', None) or getattr(entity, 'location', None)
        if hex_loc is not None:
            return str(hex_loc)
    return "-"


def get_turns_left_text(source: BuildQueueSource) -> str:
    """Return turns remaining for the first item in queue.

    Args:
        source: The build queue source.

    Returns:
        Turns remaining string, or dash if empty.
    """
    if not source.construction_queue:
        return "-"
    first = source.construction_queue[0]
    turns = first.get("turns_remaining", "?")
    return f"{turns}t"
