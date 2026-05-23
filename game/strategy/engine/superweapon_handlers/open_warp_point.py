"""OPEN_WARP_POINT superweapon handler (PROJ-396 Phase 3, ex Task 5.4).

Creates bidirectional warp points between current system and target
system. Ship preserved for reuse.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import WarpPoint
from game.strategy.data.order_types import OrderType
from game.strategy.services.superweapon_registry import find_superweapon_spec

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.engine.superweapon_order_processor import (
        SuperweaponOrderProcessor,
        SuperweaponResult,
    )


def process_open_warp_point(
    processor: "SuperweaponOrderProcessor",
    fleet: Fleet,
    empire: "Empire",
    galaxy: Galaxy,
    empires: list["Empire"] | None = None,
    component_registry: dict[str, Any] | None = None,
) -> "SuperweaponResult":
    """Process an OPEN_WARP_POINT order via spec-driven dispatch."""
    from game.strategy.engine.superweapon_order_processor import SuperweaponResult

    spec = find_superweapon_spec(OrderType.OPEN_WARP_POINT)

    def _precheck(*, fleet, empire, galaxy, empires, order, component_registry) -> "SuperweaponResult | None":
        if processor._get_system_at_hex(galaxy, fleet.location) is None:
            return SuperweaponResult(
                success=False, message="Fleet not at a star system"
            )
        # Pre-refactor parity: target-system existence is validated
        # BEFORE ability-ship lookup, so "Target system not found" beats
        # "No ship with OpenWarpPoint ability" when both would fail.
        target_system_name = order.target.get("target_system_name", "")
        if galaxy.name_map.get(target_system_name) is None:
            return SuperweaponResult(
                success=False,
                message=f"Target system '{target_system_name}' not found",
            )
        return None

    def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry) -> dict[str, str]:
        params = order.target  # dispatcher already validated isinstance(dict)
        target_system_name = params.get("target_system_name", "")

        current_system = processor._get_system_at_hex(galaxy, fleet.location)
        target_system = galaxy.name_map[target_system_name]

        # Calculate warp point locations.
        # Near-end: at fleet's local position within current system.
        fleet_local = fleet.location - current_system.global_location
        near_wp = WarpPoint(target_system.name, fleet_local)

        # Far-end: direction from target back toward current, scaled to
        # typical orbit distance (6 hexes).
        direction_q = (
            current_system.global_location.q - target_system.global_location.q
        )
        direction_r = (
            current_system.global_location.r - target_system.global_location.r
        )
        dist = max(abs(direction_q), abs(direction_r), 1)
        orbit_distance = 6
        far_q = round(direction_q / dist * orbit_distance)
        far_r = round(direction_r / dist * orbit_distance)
        far_wp = WarpPoint(current_system.name, HexCoord(far_q, far_r))

        # Issue #31: route both endpoints through ``Galaxy.add_warp_point`` so
        # the ``global_hex_warp_points`` index stays in sync with the live
        # ``system.warp_points`` lists. Without this, ``IssueWarpCommand``
        # validation, ``compute_path_for_warp``, hex outline rendering, and
        # the spatial index all silently misbehave around the new lane.
        galaxy.add_warp_point(current_system, near_wp)
        galaxy.add_warp_point(target_system, far_wp)

        # Issue #31: clear baked-in fleet paths so the next movement tick
        # re-pathfinds against the new warp graph. Without this invalidation,
        # fleets in flight would walk the stale path to completion.
        processor._get_nav_service().invalidate_paths_for_graph_change(empires or [])

        return {
            "event_message": f"Warp point opened to {target_system.name}",
            "log_message": (
                f"Warp point opened between {current_system.name} "
                f"and {target_system.name}"
            ),
            "source_system": current_system.name,
            "target_system": target_system.name,
        }

    return processor.execute_superweapon(
        fleet, empire, galaxy, empires or [], spec, _effect, component_registry,
        precheck_fn=_precheck,
    )
