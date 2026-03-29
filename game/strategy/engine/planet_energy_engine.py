"""
PlanetEnergyEngine - Planetary Energy Generation, Storage & Consumption

PROJ-237: Engine for managing per-planet energy pools.

Responsibilities:
- Scan facilities for PlanetaryEnergyGenerator abilities (sum generation_rate)
- Scan facilities for PlanetaryEnergyStorage abilities (sum capacity)
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
from game.strategy.services.component_inspector import get_component_abilities

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet
    from game.strategy.data.planetary_facility import PlanetaryFacility


def get_energy_generator_info(comp, registries: Optional[GameRegistries] = None) -> Optional[dict]:
    """Extract PlanetaryEnergyGenerator info from a component entry.

    Supports:
    - Dict with inline abilities: {"id": "x", "abilities": {"PlanetaryEnergyGenerator": {...}}}
    - Plain string ID: resolved via registries

    Returns:
        Dict with 'generation_rate', or None
    """
    if isinstance(comp, dict):
        abilities = comp.get('abilities', {})
        gen_data = abilities.get('PlanetaryEnergyGenerator')
        if isinstance(gen_data, dict):
            return gen_data
        comp_id = comp.get('id')
        if comp_id and registries is not None:
            return _get_from_registry(comp_id, 'PlanetaryEnergyGenerator', registries)
    elif isinstance(comp, str) and registries is not None:
        return _get_from_registry(comp, 'PlanetaryEnergyGenerator', registries)
    return None


def get_energy_storage_info(comp, registries: Optional[GameRegistries] = None) -> Optional[dict]:
    """Extract PlanetaryEnergyStorage info from a component entry.

    Returns:
        Dict with 'capacity', or None
    """
    if isinstance(comp, dict):
        abilities = comp.get('abilities', {})
        storage_data = abilities.get('PlanetaryEnergyStorage')
        if isinstance(storage_data, dict):
            return storage_data
        comp_id = comp.get('id')
        if comp_id and registries is not None:
            return _get_from_registry(comp_id, 'PlanetaryEnergyStorage', registries)
    elif isinstance(comp, str) and registries is not None:
        return _get_from_registry(comp, 'PlanetaryEnergyStorage', registries)
    return None


def get_shield_info(comp, registries: Optional[GameRegistries] = None) -> Optional[dict]:
    """Extract PlanetaryShield info from a component entry.

    Returns:
        Dict with 'energy_drain_rate', 'activation_time', 'deactivation_time', or None
    """
    if isinstance(comp, dict):
        abilities = comp.get('abilities', {})
        shield_data = abilities.get('PlanetaryShield')
        if isinstance(shield_data, dict):
            return shield_data
        comp_id = comp.get('id')
        if comp_id and registries is not None:
            return _get_from_registry(comp_id, 'PlanetaryShield', registries)
    elif isinstance(comp, str) and registries is not None:
        return _get_from_registry(comp, 'PlanetaryShield', registries)
    return None


def _get_from_registry(comp_id: str, ability_name: str, registries: GameRegistries) -> Optional[dict]:
    """Look up an ability from the component registry."""
    comp_def = registries.components.get(comp_id)
    if comp_def is None:
        return None
    abilities = get_component_abilities(comp_def)
    data = abilities.get(ability_name)
    if isinstance(data, dict):
        return data
    return None


class PlanetEnergyEngine:
    """
    Engine for processing planetary energy generation and consumption.

    PROJ-237: Scans planetary facilities for energy abilities and manages
    the per-planet energy pool each tick.

    Energy flow per tick:
        1. Recalculate capacity (from PlanetaryEnergyStorage abilities)
        2. Recalculate generation rate (from PlanetaryEnergyGenerator abilities)
        3. Generate energy (generation_rate / 100 per tick)
        4. Consume energy for active shields (drain_rate / 100 per tick)
        5. Auto-deactivate shield if energy insufficient
        6. Clamp energy to [0, capacity]
    """

    def __init__(self, *, registries: Optional[GameRegistries] = None):
        self._registries = registries

    def process_energy_tick(self, tick: int, empires: List) -> None:
        """Process energy generation/consumption for one tick (1/100th of turn).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        for empire in empires:
            for colony in empire.colonies:
                self._process_planet(colony, tick)

    def _process_planet(self, planet: 'Planet', tick: int) -> None:
        """Process energy for a single planet."""
        # 1. Recalculate capacity and generation from current facilities
        new_capacity = 0.0
        new_generation = 0.0
        total_drain = 0.0
        has_shield_facility = False

        for facility in planet.facilities:
            if not facility.is_operational:
                continue
            for comp in iter_components(facility.design_data):
                # Check for energy storage
                storage_info = get_energy_storage_info(comp, self._registries)
                if storage_info is not None:
                    new_capacity += storage_info.get('capacity', 0.0)

                # Check for energy generation
                gen_info = get_energy_generator_info(comp, self._registries)
                if gen_info is not None:
                    new_generation += gen_info.get('generation_rate', 0.0)

                # Check for shield (to compute drain)
                shield_info_data = get_shield_info(comp, self._registries)
                if shield_info_data is not None:
                    has_shield_facility = True
                    if planet.shield_active:
                        total_drain += shield_info_data.get('energy_drain_rate', 0.0)

        planet.energy_capacity = new_capacity
        planet.energy_generation = new_generation

        # 2. Generate energy (1/100th per tick)
        if new_generation > 0:
            planet.energy += new_generation / 100.0

        # 3. Consume energy for active shield (1/100th per tick)
        if planet.shield_active and total_drain > 0:
            drain_per_tick = total_drain / 100.0
            if planet.energy >= drain_per_tick:
                planet.energy -= drain_per_tick
            else:
                # Insufficient energy — auto-deactivate shield
                planet.energy = 0.0
                planet.shield_active = False
                # Deactivate component states on shield facilities
                self._deactivate_shield_components(planet)
                logger.info(
                    f"Planet {planet.name}: shield auto-deactivated (energy depleted)"
                )

        # 4. If shield facility was destroyed while shield was active, deactivate
        if planet.shield_active and not has_shield_facility:
            planet.shield_active = False
            logger.info(
                f"Planet {planet.name}: shield deactivated (facility destroyed)"
            )

        # 5. Clamp energy to [0, capacity]
        if new_capacity > 0:
            planet.energy = max(0.0, min(planet.energy, new_capacity))
        else:
            planet.energy = 0.0

    def _deactivate_shield_components(self, planet: 'Planet') -> None:
        """Deactivate all shield component states on a planet's facilities."""
        for facility in planet.facilities:
            for comp in iter_components(facility.design_data):
                shield_info_data = get_shield_info(comp, self._registries)
                if shield_info_data is not None:
                    comp_id = comp.get('id', '') if isinstance(comp, dict) else str(comp)
                    if comp_id:
                        facility.set_component_active(comp_id, False)
