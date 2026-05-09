"""IMPLODE_PLANET superweapon handler (PROJ-396 Phase 3, ex Task 5.4).

Extracted from ``superweapon_order_processor.py`` per review MAJ-005.
The closures previously closed over ``self`` from
``SuperweaponOrderProcessor``; they now receive the processor as an
explicit ``processor`` parameter (Option B / state-bag approach).
"""
from __future__ import annotations

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


def process_implode_planet(
    processor: "SuperweaponOrderProcessor",
    fleet: Fleet,
    empire: "Empire",
    galaxy: Galaxy,
    empires: List["Empire"],
    component_registry: Optional[Dict[str, Any]] = None,
) -> "SuperweaponResult":
    """Process an IMPLODE_PLANET order via spec-driven dispatch.

    Destroys the target planet; ship preserved for reuse.
    """
    spec = find_superweapon_spec(OrderType.IMPLODE_PLANET)

    def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
        target_planet = order.target
        # Remove planet from colony list if owned (iterate all empires
        # to catch enemy planets).
        if target_planet.owner_id is not None:
            # PROJ-370 Phase 4: route through IEmpireMutator.
            mutator = processor._get_empire_mutator()
            for emp in empires:
                mutator.remove_colony(emp, target_planet)
        galaxy.unregister_planet(target_planet)
        return {
            "event_message": f"Planet {target_planet.name} destroyed",
            "log_message": (
                f"Planet {target_planet.name} destroyed by fleet {fleet.id}"
            ),
            "planet_id": target_planet.id,
            "planet_name": target_planet.name,
        }

    return processor.execute_superweapon(
        fleet, empire, galaxy, empires, spec, _effect, component_registry
    )
