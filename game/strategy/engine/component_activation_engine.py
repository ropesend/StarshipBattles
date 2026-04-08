"""
ComponentActivationEngine — Tick-based activation timer processing.

Processes ComponentActivationState timers on planet facilities and fleet ships
each tick. States in ACTIVATING or DEACTIVATING phase have their progress
incremented. On phase transitions, updates planet.active_abilities accordingly.

This engine is separate from the order system — orders initiate activation
(setting a component to ACTIVATING), and this engine ticks the timers.

Turn engine integration: Phase 1.7 (after instant orders at Phase 1).
"""
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.planetary_facility import PlanetaryFacility


class ComponentActivationEngine:
    """Engine that ticks component activation timers each turn tick.

    Iterates all facilities on all colonies (and ships on all fleets)
    and advances any ACTIVATING or DEACTIVATING ComponentActivationState
    entries by one tick. On phase transitions, updates the parent entity's
    active_abilities dict.
    """

    def _validate_tick_inputs(self, empires) -> None:
        """PROJ-251: Validate preconditions before mutating state."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for colony in empire.colonies:
                if colony is None:
                    raise ValidationException(
                        f"Empire {empire.id}: colony list contains None entry",
                        context={"empire_id": empire.id}
                    )

    def process_activation_tick(
        self,
        tick: int,
        empires: List,
    ) -> List[Dict[str, Any]]:
        """Process one tick of activation timers across all empires.

        Args:
            tick: Current tick number (1-100).
            empires: List of Empire objects to process.

        Returns:
            List of transition event dicts (for logging/UI).
        """
        self._validate_tick_inputs(empires)
        results = []
        for empire in empires:
            # Planet facilities
            for planet in empire.colonies:
                for facility in planet.facilities:
                    self._tick_facility(facility, planet, results)
            # Fleet ships (future — activation_states on ShipInstance)
            # for fleet in empire.fleets:
            #     for ship in fleet.ships:
            #         self._tick_ship(ship, fleet, results)
        return results

    def _tick_facility(
        self,
        facility: 'PlanetaryFacility',
        planet: 'Planet',
        results: List[Dict[str, Any]],
    ) -> None:
        """Tick all activation states on a facility."""
        if not facility.is_operational:
            return

        for comp_key, state_data in list(facility.component_states.items()):
            if not isinstance(state_data, dict):
                continue

            state = ComponentActivationState.from_dict(state_data)

            if state.phase not in (ActivationPhase.ACTIVATING, ActivationPhase.DEACTIVATING):
                continue

            transitioned = state.tick()
            facility.component_states[comp_key] = state.to_dict()

            if transitioned:
                ability_name = state.ability_name
                if state.phase == ActivationPhase.ACTIVE:
                    logger.info(
                        f"Planet {planet.name}: {ability_name} activation complete "
                        f"(facility {facility.instance_id})"
                    )
                elif state.phase == ActivationPhase.INACTIVE:
                    logger.info(
                        f"Planet {planet.name}: {ability_name} deactivation complete "
                        f"(facility {facility.instance_id})"
                    )

                results.append({
                    'planet_name': planet.name,
                    'facility_id': facility.instance_id,
                    'component_key': comp_key,
                    'ability_name': ability_name,
                    'new_phase': state.phase.value,
                    'transitioned': True,
                })
