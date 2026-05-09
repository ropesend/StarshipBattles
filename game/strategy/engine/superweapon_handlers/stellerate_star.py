"""STELLERATE_STAR superweapon handler (PROJ-396 Phase 3, ex Task 5.4).

Suicide weapon: destroys all stars and planets in the system and
destroys ALL fleets within the 50-hex system radius (including the
acting fleet) via SystemDestroyer. Warp points preserved.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

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


def process_stellerate_star(
    processor: "SuperweaponOrderProcessor",
    fleet: Fleet,
    empire: "Empire",
    galaxy: Galaxy,
    empires: List["Empire"],
    component_registry: Optional[Dict[str, Any]] = None,
) -> "SuperweaponResult":
    """Process a STELLERATE_STAR order via spec-driven dispatch.

    Spec ``ability_name=None``; the ability-ship lookup is skipped.
    Spec ``consume_ship=True``; the dispatcher emits the STAR_DESTROYED
    event ad-hoc and skips ``_finalize_superweapon`` (the fleet is
    already gone, and the order MUST stay un-popped to match the
    pre-refactor semantics pinned by Phase 1 characterization tests).
    """
    from game.strategy.engine.superweapon_order_processor import SuperweaponResult

    spec = find_superweapon_spec(OrderType.STELLERATE_STAR)

    def _precheck(*, fleet, empire, galaxy, empires, order, component_registry):
        if processor._get_system_at_hex(galaxy, fleet.location) is None:
            return SuperweaponResult(
                success=False, message="Fleet not at a star system"
            )
        return None

    def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
        system = processor._get_system_at_hex(galaxy, fleet.location)
        system_name = system.name

        # PROJ-277: SystemDestroyer collects-then-mutates so every fleet
        # within the 50-hex radius is destroyed.
        from game.strategy.services.system_destroyer import (
            collect_system_contents,
            destroy_system,
        )
        plan = collect_system_contents(system, galaxy, empires)
        destroy_system(plan, galaxy, empires, event_bus=processor._event_bus)

        return {
            "event_message": f"Star system {system_name} destroyed",
            "log_message": (
                f"Star system {system_name} stellerated by fleet {fleet.id}"
            ),
            "system_name": system_name,
            "location_name": system_name,
        }

    return processor.execute_superweapon(
        fleet, empire, galaxy, empires, spec, _effect, component_registry,
        precheck_fn=_precheck,
    )
