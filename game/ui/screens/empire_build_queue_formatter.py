"""Data formatting functions for empire build queue display.

Pure data transform functions with no UI dependencies. These format
BuildQueueSource data into human-readable strings for the
EmpireBuildQueueWindow display.

Created as part of PROJ-89 Phase 2.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from game.ui.utils.formatters import format_compact_number

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
        # Try galaxy lookup
        if galaxy:
            sys_obj = galaxy.get_system_of_planet(entity)
            if sys_obj:
                return sys_obj.name
    elif source.context_type == "fleet":
        location = entity.location
        if location and galaxy:
            sys_obj = galaxy.get_system_at_hex(location)
            if sys_obj:
                return sys_obj.name
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
        location = entity.location
        if location is not None:
            return str(location)
    elif source.context_type == "planet":
        # Planets have local location within their system
        hex_loc = entity.location
        if hex_loc is not None:
            return str(hex_loc)
    return "-"


def format_turns_remaining(turns: float) -> str:
    """Format turns remaining for display.
    
    Args:
        turns: Number of turns (float)
        
    Returns:
        Formatted string (e.g. "1.25 turns")
    """
    if turns <= 0:
        return "Complete"
    return f"{turns:.2f} turns"


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


def get_resource_rate_text(source: BuildQueueSource, resource_name: str) -> str:
    """Return per-turn resource consumption rate for first queue item.

    Args:
        source: The build queue source.
        resource_name: Name of the resource (e.g. 'metals', 'organics').

    Returns:
        Formatted per-turn rate (cost_per_tick * 100), or '-' if empty/legacy.
    """
    if not source.construction_queue:
        return "-"
    first = source.construction_queue[0]
    cost_per_tick = first.get("cost_per_tick")
    if cost_per_tick is None:
        return "-"
    rate = cost_per_tick.get(resource_name, 0.0)
    per_turn = rate * 100  # 100 ticks per turn
    if per_turn == 0:
        return "0"
    return f"{int(per_turn):,}"


def get_resource_total_text(source: BuildQueueSource, resource_name: str) -> str:
    """Return total resource cost for first queue item with k/M suffix.

    Args:
        source: The build queue source.
        resource_name: Name of the resource (e.g. 'metals', 'organics').

    Returns:
        Formatted total cost with suffix, or '-' if empty/legacy.
    """
    if not source.construction_queue:
        return "-"
    first = source.construction_queue[0]
    total_cost = first.get("total_cost")
    if total_cost is None:
        return "-"
    amount = total_cost.get(resource_name, 0)
    if amount == 0:
        return "0"
    return format_compact_number(amount)
