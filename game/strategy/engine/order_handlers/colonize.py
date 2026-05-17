"""ColonizeHandler -- handles `OrderType.COLONIZE` (PROJ-368 Phase 2).

Lifted from `OrderProcessor.process_colonize` (lines 151-249) and
`OrderProcessor._deploy_drop_pod` (lines 618-652). Phase 2 Rework
(retained from PROJ-238): colony pods are cargo items consumed at
colonization; the carrying ship is reusable and stays in the fleet.

PROJ-431 Phase 1d: drop-pod deploy walks ``ship.bay_inventory.pods``
(typed ``DropPod`` entries) instead of the legacy mixed-shape
``carried_items`` list. The consumed pod is removed by rebuilding
``ship.bay_inventory`` with that pod dropped and calling
``ship.set_bay_inventory(...)``.

Q1 resolution (decisions.md): missing `component_registry` continues to
log+pop+False (preserved backward-compat). Stronger ValueError contract
deferred to a future tech-debt project.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple
import logging

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    OrderExecutionResult,
)
from game.strategy.events.event_types import EventCategory, EventType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy


class ColonizeHandler(BaseOrderHandler):
    """Handler for `OrderType.COLONIZE`."""

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        return (OrderType.COLONIZE,)

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        """Execute a COLONIZE order. Lift-and-shift of `process_colonize`."""
        from game.strategy.validation import ColonizeValidator

        order = fleet.get_current_order()
        if not order or order.type != OrderType.COLONIZE:
            return OrderExecutionResult(success=False, colonized=False)

        if component_registry is None:
            # Q1 resolution: preserve log+pop+False for backward compat.
            logger.error("ColonizeHandler: COLONIZE order requires component_registry")
            fleet.pop_order()
            return OrderExecutionResult(success=False, colonized=False)

        # Extract target planet (may be a plain Planet or a dict with planet key)
        raw_target = order.target
        if isinstance(raw_target, dict):
            target_planet = raw_target.get('planet')
        else:
            target_planet = raw_target

        # Validate (skip chain check -- we're executing, not adding)
        validation = ColonizeValidator.validate(
            galaxy, fleet, target_planet, component_registry, skip_chain_check=True
        )
        if not validation.is_valid:
            logger.warning(f"ColonizeHandler: Colonize failed - {validation.message}")
            fleet.pop_order()
            return OrderExecutionResult(success=False, colonized=False)

        # Determine final planet (for "Any" case, pick first unowned)
        if target_planet is not None:
            final_planet = target_planet
        else:
            planets_at_loc = galaxy.get_planets_at_global_hex(fleet.location)
            valid_candidates = [p for p in planets_at_loc if p.owner_id is None]
            final_planet = valid_candidates[0] if valid_candidates else None

            if final_planet is None:
                logger.warning("ColonizeHandler: No candidate planet for colonization")
                fleet.pop_order()
                return OrderExecutionResult(success=False, colonized=False)

        # Pre-check drop pod availability BEFORE any mutation
        if not ColonizeValidator.fleet_has_drop_pod(fleet):
            logger.warning("ColonizeHandler: No drop pod in fleet")
            fleet.pop_order()
            return OrderExecutionResult(success=False, colonized=False)

        # Execute colonization -- claim planet and deploy pod only.
        # Population and cargo transfer is handled by TRANSFER orders queued after COLONIZE.
        empire.add_colony(final_planet)
        fleet.pop_order()

        # Deploy drop pod as facility on the new colony
        self._deploy_drop_pod(fleet, final_planet, empire=empire)

        logger.info(f"ColonizeHandler: Colonization successful. {empire.name} claimed {final_planet.name}")

        # Look up system name and local hex for granular event log columns
        system_name = ""
        local_hex = None
        if galaxy and hasattr(galaxy, 'get_system_of_planet'):
            sys = galaxy.get_system_of_planet(final_planet)
            if sys:
                system_name = sys.name
                if hasattr(final_planet, 'location') and final_planet.location is not None:
                    local_hex = [final_planet.location.q, final_planet.location.r]

        self._emit_event(
            EventType.COLONY_FOUNDED,
            category=EventCategory.COLONIES,
            empire_id=empire.id,
            message=f"Founded colony on {final_planet.name}",
            planet_id=final_planet.id,
            planet_name=final_planet.name,
            fleet_id=fleet.id,
            location_name=final_planet.name,
            location_hex=[fleet.location.q, fleet.location.r],
            system_name=system_name,
            local_hex=local_hex,
        )
        # PROJ-368: legacy execute_action_order's COLONIZE branch returned
        # `result.colonized` as the "fleet consumed" signal -- documented
        # quirk preserved for backward compat with existing characterization
        # tests in test_fleet_order_processor.py.
        return OrderExecutionResult(
            success=True,
            fleet_consumed=True,  # mirror legacy: colonized -> fleet_consumed
            colonized=True,
            planet_name=final_planet.name,
        )

    def _deploy_drop_pod(
        self, fleet: Fleet, planet: Any, *, empire: Optional["Empire"] = None,
    ) -> None:
        """Deploy a drop pod from fleet cargo as a facility on the planet.

        PROJ-431 Phase 1d: finds the first drop pod in any ship's
        ``bay_inventory.pods``, removes it via ``set_bay_inventory(...)``
        (rebuilding the inventory with that pod dropped), and creates a
        PlanetaryFacility from its ``design_data``. The full design (all
        components the player chose) becomes the facility.

        PROJ-412 Phase 5: ``empire`` is forwarded to ``add_facility`` so
        the empire's storage/booster dirty flags flip mid-turn.
        """
        from uuid import uuid4
        from game.strategy.data.bay_inventory import BayInventory
        from game.strategy.data.planetary_facility import PlanetaryFacility
        from game.strategy.validation.colonize_validator import ColonizeValidator

        ship, pod_index = ColonizeValidator.find_ship_with_drop_pod(fleet)
        if ship is None:
            logger.warning("_deploy_drop_pod: No drop pod found in fleet")
            return

        # Remove the drop pod from the ship by rebuilding bay_inventory
        # without that pod. PROJ-431 Phase 1d: typed write-through.
        current_bay = ship.bay_inventory
        if pod_index < 0 or pod_index >= len(current_bay.pods):
            logger.warning(
                "_deploy_drop_pod: pod_index %d out of range (pods=%d)",
                pod_index,
                len(current_bay.pods),
            )
            return
        drop_pod = current_bay.pods[pod_index]
        remaining_pods = [
            p for i, p in enumerate(current_bay.pods) if i != pod_index
        ]
        ship.set_bay_inventory(
            BayInventory(bay=list(current_bay.bay), pods=remaining_pods)
        )

        design_data = drop_pod.design_data or {}
        # The legacy entry preserved a 'name' field in its payload. The
        # typed ``DropPod`` keeps payload-shape extras opaquely so the
        # facility name continues to round-trip through the same slot.
        pod_name = drop_pod.payload.get("name", "Colony Drop Pod")

        facility = PlanetaryFacility(
            instance_id=uuid4().hex,
            design_id=drop_pod.design_id or "drop_pod",
            name=pod_name,
            design_data=design_data,
            is_operational=True,
        )
        # PROJ-370 Phase 3: route through IPlanetMutator.
        # PROJ-412 Phase 5: forward empire so HarvestingEngine's per-turn
        # storage/booster caches see the new facility mid-turn.
        self._get_planet_mutator().add_facility(planet, facility, empire=empire)

        # Seed planet stockpile from design's initial_stockpile if present
        initial_stock = design_data.get("initial_stockpile", {})
        for resource, amount in initial_stock.items():
            planet.add_to_stockpile(resource, float(amount))

        logger.info(f"Deployed drop pod '{facility.name}' on {planet.name}")
