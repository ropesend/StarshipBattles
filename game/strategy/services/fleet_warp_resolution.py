"""Warp-path resolution helpers for FleetNavigationService.

PROJ-382 Phase 5: extracted from ``FleetNavigationService`` to bring the
parent module under the 500 LOC ceiling.  Two pure functions implement
``compute_path_for_warp`` (compose the path-to-WP + exit hex) and
``resolve_warp_exit`` (look up the reciprocal warp point on the
destination system).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from game.core.hex_math import HexCoord
from game.strategy.data.pathfinding import find_hybrid_path

if TYPE_CHECKING:
    from game.strategy.services.fleet_navigation_service import NavigationState


logger = logging.getLogger(__name__)


def compute_path_for_warp(
    state: "NavigationState",
    warp_point_hex: HexCoord,
    galaxy,
) -> list:
    """Compute path for explicit WARP order — path-to-WP + reciprocal exit.

    PROJ-187: Returns the path to the warp point plus the exit hex on the
    other side of the warp connection.
    """
    path: list = []

    # 1. If not at warp point, compute path to it.
    if state.location != warp_point_hex:
        path_to_wp = find_hybrid_path(galaxy, state.location, warp_point_hex)
        if path_to_wp:
            # Remove start if matches current location.
            if path_to_wp and path_to_wp[0] == state.location:
                path_to_wp = path_to_wp[1:]
            path.extend(path_to_wp)

    # 2. Look up warp point and resolve exit hex.
    exit_hex = resolve_warp_exit(warp_point_hex, galaxy)
    if exit_hex:
        path.append(exit_hex)

    return path


def resolve_warp_exit(
    warp_point_hex: HexCoord,
    galaxy,
) -> Optional[HexCoord]:
    """Resolve the exit hex for a warp point.

    Looks up the source system, finds the local warp point, then the
    reciprocal warp point on the destination system, and returns its
    global hex coord.  Falls back to the destination system center when
    the reciprocal pair is missing (logged as a warning).
    """
    # Look up source system from warp point index.
    source_system = galaxy.state.global_hex_warp_points.get(warp_point_hex)
    if not source_system:
        logger.warning(f"No warp point found at {warp_point_hex}")
        return None

    # Find the warp point at this hex within the system.
    local_offset = warp_point_hex - source_system.global_location
    source_wp = None
    for wp in source_system.warp_points:
        if wp.location == local_offset:
            source_wp = wp
            break

    if not source_wp:
        logger.warning(f"Warp point not found at local offset {local_offset} in {source_system.name}")
        return None

    # Get destination system.
    dest_system = galaxy.get_system_by_name(source_wp.destination_id)
    if not dest_system:
        logger.warning(f"Destination system '{source_wp.destination_id}' not found")
        return None

    # Find reciprocal warp point in destination system.
    for wp in dest_system.warp_points:
        if wp.destination_id == source_system.name:
            exit_hex = dest_system.global_location + wp.location
            return exit_hex

    # Fallback: use destination system center.
    logger.warning("No reciprocal warp point found, using system center")
    return dest_system.global_location
