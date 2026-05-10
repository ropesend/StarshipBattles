"""ColonizeHandler -- handles `OrderType.COLONIZE` (PROJ-368 Phase 2).

Lifted from `OrderProcessor.process_colonize` (lines 151-249) and
`OrderProcessor._deploy_drop_pod` (lines 618-652). Phase 2 Rework
(retained from PROJ-238): colony pods are cargo items consumed at
colonization; the carrying ship is reusable and stays in the fleet.

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
        self._deploy_drop_pod(fleet, final_planet)

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

    def _deploy_drop_pod(self, fleet: Fleet, planet: Any) -> None:
        """Deploy a drop pod from fleet cargo as a facility on the planet.

        Finds the first drop pod in any ship's carried_items, removes it,
        and creates a PlanetaryFacility from its design_data. The full
        design (all components the player chose) becomes the facility.
        """
        from uuid import uuid4
        from game.strategy.data.planet import PlanetaryFacility
        from game.strategy.validation.colonize_validator import ColonizeValidator

        ship, item_index = ColonizeValidator.find_ship_with_drop_pod(fleet)
        if ship is None:
            logger.warning("_deploy_drop_pod: No drop pod found in fleet")
            return

        # Remove the drop pod from the ship.
        # PROJ-370 Phase 5: route through IShipInstanceMutator.
        drop_pod = self._get_ship_mutator().pop_carried_item(ship, item_index)
        design_data = drop_pod.get('design_data', {})

        facility = PlanetaryFacility(
            instance_id=uuid4().hex,
            design_id=drop_pod.get('design_id', 'drop_pod'),
            name=drop_pod.get('name', 'Colony Drop Pod'),
            design_data=design_data,
            is_operational=True,
        )
        # PROJ-370 Phase 3: route through IPlanetMutator.
        self._get_planet_mutator().add_facility(planet, facility)

        # Seed planet stockpile from design's initial_stockpile if present
        initial_stock = design_data.get("initial_stockpile", {})
        for resource, amount in initial_stock.items():
            planet.add_to_stockpile(resource, float(amount))

        logger.info(f"Deployed drop pod '{facility.name}' on {planet.name}")
