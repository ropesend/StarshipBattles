"""
PlanetEnergyEngine - Planetary Energy Generation, Storage & Consumption

PROJ-237: Engine for managing per-planet energy pools.
PROJ-238: Updated to use StrategicResourceGeneration and ResourceStorage
          abilities. No hardcoded resource type names.

Responsibilities:
- Scan facilities for StrategicResourceGeneration abilities (sum generation_rate by resource)
- Scan facilities for ResourceStorage abilities (sum capacity by resource)
- Generate energy per tick (generation_rate / 100)
- Consume energy for active shields (energy_drain_rate / 100)
- Auto-deactivate shields when energy runs out
- Clamp energy to [0, capacity] each tick
- Recalculate capacity/generation each tick (handles mid-turn facility destruction)

Called by TurnEngine._process_tick() 100 times per turn.
"""

from typing import List, Optional, TYPE_CHECKING
import logging

from game.core.registry import GameRegistries
from game.core.patterns.layer_iterator import iter_components
from game.strategy.data.component_activation_state import (
    ComponentActivationState,
)
from game.strategy.interfaces.engines import IPlanetEnergyEngine
from game.strategy.events.event_types import EventType, EventCategory

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet
    from game.strategy.data.planetary_facility import PlanetaryFacility



def get_shield_info(comp, registries: Optional[GameRegistries] = None) -> Optional[dict]:
    """Extract PlanetaryShield info from a component entry.

    Returns:
        Dict with 'energy_drain_rate', 'activation_time', 'deactivation_time', or None.
    """
    abilities = _extract_abilities(comp, registries)
    shield_data = abilities.get('PlanetaryShield')
    if isinstance(shield_data, dict):
        return shield_data
    return None


def get_activatable_ability_info(comp, ability_key: str, registries=None) -> Optional[dict]:
    """Extract info for any activatable ability (one with energy_drain_rate).

    Generic helper that works for GeologicStabilizer, StellarStabilizer,
    WarpFieldStabilizer, and any future activatable ability.

    Returns:
        Dict with ability data if found, or None.
    """
    abilities = _extract_abilities(comp, registries)
    data = abilities.get(ability_key)
    if isinstance(data, dict):
        return data
    return None


def _extract_abilities(comp, registries: Optional[GameRegistries] = None) -> dict:
    """Extract abilities dict from a component entry.

    Delegates to the centralized extract_abilities_from_component() in component_inspector.
    """
    from game.strategy.services.component_inspector import extract_abilities_from_component
    return extract_abilities_from_component(comp, registries)


# Activatable strategic abilities that drain energy (beyond PlanetaryShield)
_ACTIVATABLE_ABILITIES = [
    'GeologicStabilizer',
    'StellarStabilizer',
    'WarpFieldStabilizer',
]


def _is_ability_active(planet, ability_key: str) -> bool:
    """Check if an activatable ability is active on a planet.

    Uses Planet.active_abilities derived property (scans facility component_states).
    """
    active_dict = getattr(planet, 'active_abilities', {})
    if isinstance(active_dict, dict):
        return active_dict.get(ability_key, False)
    return False


class PlanetEnergyEngine(IPlanetEnergyEngine):
    """
    Engine for processing planetary energy generation and consumption.

    PROJ-237: Scans planetary facilities for energy abilities and manages
    the per-planet energy pool each tick.
    PROJ-238: Uses StrategicResourceGeneration and ResourceStorage abilities.
              Resource type is determined by what the shield consumes (from
              PlanetaryShield.energy_drain_rate field name implies energy,
              but the engine scans generically).

    Energy flow per tick:
        1. Recalculate capacity (from ResourceStorage abilities for the resource)
        2. Recalculate generation rate (from StrategicResourceGeneration abilities)
        3. Generate energy (generation_rate / 100 per tick)
        4. Consume energy for active shields (drain_rate / 100 per tick)
        5. Auto-deactivate shield if energy insufficient
        6. Clamp energy to [0, capacity]
    """

    # The resource type used for planetary energy. Configurable if needed.
    ENERGY_RESOURCE = "energy"

    def __init__(self, *, registries: GameRegistries, event_bus=None):
        """Initialize planet energy engine.

        Args:
            registries: GameRegistries for component ability lookup. Required.
            event_bus: Optional EventBus for structured event logging.

        Raises:
            ValidationException: If registries is None.
        """
        if registries is None:
            from game.core.exceptions import ValidationException
            from game.core.error_codes import ErrorCode
            raise ValidationException(
                "registries is required for PlanetEnergyEngine",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "PlanetEnergyEngine", "parameter": "registries"}
            )
        self._registries = registries
        self._event_bus = event_bus
        # PROJ-253: Cache for facility scan results per planet
        self._energy_cache: dict = {}  # planet_id -> {capacity, generation, fingerprint}

    def invalidate_energy_cache(self, planet_id: str) -> None:
        """Remove cached energy metadata for a planet (PROJ-253).

        The fingerprint-based cache auto-detects facility additions, removals,
        and operational status changes. This method exists for explicit invalidation
        by callers that modify facility internals without changing the fingerprint
        (e.g., component ability reconfiguration).
        """
        self._energy_cache.pop(planet_id, None)

    def _get_facility_fingerprint(self, planet: 'Planet') -> tuple:
        """Build a fingerprint of facility state for cache invalidation."""
        return tuple(
            (f.instance_id, f.is_operational) for f in planet.facilities
        )

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

    def process_energy_tick(self, tick: int, empires: List) -> None:
        """Process energy generation/consumption for one tick (1/100th of turn).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        self._validate_tick_inputs(empires)
        for empire in empires:
            for colony in empire.colonies:
                self._process_planet(colony, tick, empire_id=empire.id)

    def _process_planet(self, planet: 'Planet', tick: int, empire_id: int = -1) -> None:
        """Process energy for a single planet."""
        resource = self.ENERGY_RESOURCE

        # PROJ-253: Use cached capacity/generation if facility state unchanged
        fingerprint = self._get_facility_fingerprint(planet)
        cached = self._energy_cache.get(planet.id)

        if cached and cached['fingerprint'] == fingerprint:
            new_capacity = cached['capacity']
            new_generation = cached['generation']
        else:
            # Rebuild: scan facilities for energy abilities
            new_capacity = 0.0
            new_generation = 0.0

            for facility in planet.facilities:
                if not facility.is_operational:
                    continue
                for comp in iter_components(facility.design_data):
                    abilities = _extract_abilities(comp, self._registries)

                    # Resource storage
                    storage_entries = abilities.get('ResourceStorage')
                    if storage_entries:
                        entries = storage_entries if isinstance(storage_entries, list) else [storage_entries]
                        for entry in entries:
                            if isinstance(entry, dict) and entry.get('resource') == resource:
                                new_capacity += entry.get('amount', 0.0)

                    # Strategic resource generation
                    gen_entries = abilities.get('StrategicResourceGeneration')
                    if gen_entries:
                        entries = gen_entries if isinstance(gen_entries, list) else [gen_entries]
                        for entry in entries:
                            if isinstance(entry, dict) and entry.get('resource') == resource:
                                new_generation += entry.get('generation_rate', 0.0)

            self._energy_cache[planet.id] = {
                'capacity': new_capacity,
                'generation': new_generation,
                'fingerprint': fingerprint,
            }

        planet.energy_capacity = new_capacity
        planet.energy_generation = new_generation

        # 2. Generate energy (1/100th per tick)
        if new_generation > 0:
            planet.energy += new_generation / 100.0

        # 3. Compute total drain from ComponentActivationState entries
        total_drain = self._compute_activation_drain(planet)

        # 4. Consume energy for draining components (1/100th per tick)
        if total_drain > 0:
            drain_per_tick = total_drain / 100.0
            if planet.energy >= drain_per_tick:
                planet.energy -= drain_per_tick
            else:
                # Insufficient energy — cancel all activating/active components
                planet.energy = 0.0
                self._cancel_all_draining_components(planet, empire_id=empire_id)

        # 5. Clamp energy to [0, capacity]
        if new_capacity > 0:
            planet.energy = max(0.0, min(planet.energy, new_capacity))
        else:
            planet.energy = 0.0

    def _compute_activation_drain(self, planet: 'Planet') -> float:
        """Sum energy_drain_rate from all ComponentActivationState entries that are draining."""
        total = 0.0
        for facility in planet.facilities:
            if not facility.is_operational:
                continue
            for key, state_data in facility.component_states.items():
                if not isinstance(state_data, dict) or 'phase' not in state_data:
                    continue
                state = ComponentActivationState.from_dict(state_data)
                if state.is_draining_energy:
                    total += state.energy_drain_rate
        return total

    def _cancel_all_draining_components(self, planet: 'Planet', empire_id: int = -1) -> None:
        """Cancel all activating/active/deactivating components due to energy depletion."""
        for facility in planet.facilities:
            if not facility.is_operational:
                continue
            for key, state_data in list(facility.component_states.items()):
                if not isinstance(state_data, dict) or 'phase' not in state_data:
                    continue
                state = ComponentActivationState.from_dict(state_data)
                if state.is_draining_energy:
                    ability_name = state.ability_name
                    state.cancel()
                    facility.component_states[key] = state.to_dict()
                    logger.info(
                        f"Planet {planet.name}: {ability_name} cancelled "
                        f"(energy depleted, facility {facility.instance_id})"
                    )
                    if self._event_bus and ability_name:
                        self._event_bus.log_event(
                            EventType.SHIELD_AUTO_DEACTIVATED,
                            category=EventCategory.PLANET_OPERATIONS,
                            empire_id=empire_id,
                            message=(
                                f"{ability_name} auto-deactivated on {planet.name} "
                                f"(energy depleted)"
                            ),
                            planet_name=planet.name,
                            planet_id=planet.id,
                            ability_name=ability_name,
                            facility_id=facility.instance_id,
                        )

