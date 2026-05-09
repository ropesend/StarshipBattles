"""CLOSE_WARP_POINT superweapon handler (PROJ-396 Phase 3, ex Task 5.4).

Removes both ends of the warp link; ship preserved for reuse. Strictly
validates the fleet is at the exact warp-point sector (hex) — not just
the right system — to defend against reordered moves that would close
the wrong warp point.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.order_types import OrderType
from game.strategy.services.superweapon_registry import find_superweapon_spec

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.engine.superweapon_order_processor import (
        SuperweaponOrderProcessor,
        SuperweaponResult,
    )

logger = logging.getLogger(__name__)


def _parse_close_target(target: Any) -> Tuple[str, Optional[HexCoord]]:
    """Parse target into ``(destination_id, expected_hex)``.

    Legacy back-compat: a plain string target was the pre-PROJ-228 form.
    """
    if isinstance(target, dict):
        destination_id = target.get("destination_id", "")
        hex_data = target.get("target_hex")
        expected_hex = (
            HexCoord(hex_data["q"], hex_data["r"]) if hex_data else None
        )
    else:
        destination_id = target
        expected_hex = None
    return destination_id, expected_hex


def process_close_warp_point(
    processor: "SuperweaponOrderProcessor",
    fleet: Fleet,
    empire: "Empire",
    galaxy: Galaxy,
    empires: Optional[List["Empire"]] = None,
    component_registry: Optional[Dict[str, Any]] = None,
) -> "SuperweaponResult":
    """Process a CLOSE_WARP_POINT order via spec-driven dispatch."""
    from game.strategy.engine.superweapon_order_processor import SuperweaponResult

    spec = find_superweapon_spec(OrderType.CLOSE_WARP_POINT)

    def _precheck(*, fleet, empire, galaxy, empires, order, component_registry):
        destination_id, _expected_hex = _parse_close_target(order.target)
        if not destination_id:
            return SuperweaponResult(
                success=False, message="No destination specified"
            )
        if processor._get_system_at_hex(galaxy, fleet.location) is None:
            return SuperweaponResult(
                success=False, message="Fleet not at a star system"
            )
        return None

    def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
        destination_id, expected_hex = _parse_close_target(order.target)
        current_system = processor._get_system_at_hex(galaxy, fleet.location)

        # Strict sector-level validation: fleet must be AT the warp
        # point hex, not just somewhere in the system.
        if expected_hex and fleet.location != expected_hex:
            logger.warning(
                f"Fleet {fleet.id}: Expected to be at sector {expected_hex} "
                f"but is at sector {fleet.location}, canceling "
                f"CLOSE_WARP_POINT order"
            )
            return SuperweaponResult(
                success=False,
                message=(
                    f"Fleet is at sector {fleet.location} but order targets "
                    f"warp point at sector {expected_hex}"
                ),
            )

        galaxy.remove_warp_link(current_system.name, destination_id)

        return {
            "event_message": f"Warp point to {destination_id} closed",
            "log_message": (
                f"Warp point closed between {current_system.name} "
                f"and {destination_id}"
            ),
            "source_system": current_system.name,
            "target_system": destination_id,
        }

    return processor.execute_superweapon(
        fleet, empire, galaxy, empires or [], spec, _effect, component_registry,
        precheck_fn=_precheck,
    )
