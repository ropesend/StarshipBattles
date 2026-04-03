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

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet
    from game.strategy.data.planetary_facility import PlanetaryFacility


def get_strategic_generation_info(comp, resource_type: str, registries: Optional[GameRegistries] = None) -> Optional[dict]:
    """Extract StrategicResourceGeneration info for a specific resource from a component.

    Scans for StrategicResourceGeneration ability entries matching the given
    resource type. Supports both inline abilities and registry lookup.

    Args:
        comp: Component entry from design_data layers (dict or str).
        resource_type: Resource type to match (e.g. value from resources.json).
        registries: Optional GameRegistries for component lookup.

    Returns:
        Dict with 'generation_rate' and 'resource', or None.
    """
    abilities = _extract_abilities(comp, registries)
    gen_data = abilities.get('StrategicResourceGeneration')
    if gen_data is None:
        return None
    # Can be a list (multiple resources) or a single dict
    entries = gen_data if isinstance(gen_data, list) else [gen_data]
    for entry in entries:
        if isinstance(entry, dict) and entry.get('resource') == resource_type:
            return entry
    return None


def get_resource_storage_info(comp, resource_type: str, registries: Optional[GameRegistries] = None) -> Optional[dict]:
    """Extract ResourceStorage info for a specific resource from a component.

    Scans for ResourceStorage ability entries matching the given resource type.

    Args:
        comp: Component entry from design_data layers (dict or str).
        resource_type: Resource type to match.
        registries: Optional GameRegistries for component lookup.

    Returns:
        Dict with 'amount' (capacity) and 'resource', or None.
    """
    abilities = _extract_abilities(comp, registries)
    storage_data = abilities.get('ResourceStorage')
    if storage_data is None:
        return None
    entries = storage_data if isinstance(storage_data, list) else [storage_data]
    for entry in entries:
        if isinstance(entry, dict) and entry.get('resource') == resource_type:
            return entry
    return None


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
    """Check if an activatable ability is active on a planet."""
    active_dict = getattr(planet, 'active_abilities', {})
    if isinstance(active_dict, dict):
        return active_dict.get(ability_key, False)
    return False


def _set_ability_active(planet, ability_key: str, active: bool):
    """Set an activatable ability's active state on a planet."""
    if not hasattr(planet, 'active_abilities'):
        planet.active_abilities = {}
    planet.active_abilities[ability_key] = active


class PlanetEnergyEngine:
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
        resource = self.ENERGY_RESOURCE

        # 1. Recalculate capacity and generation from current facilities
        new_capacity = 0.0
        new_generation = 0.0
        total_drain = 0.0
        has_shield_facility = False
        _active_facilities = {}  # ability_key -> True if facility exists

        for facility in planet.facilities:
            if not facility.is_operational:
                continue
            for comp in iter_components(facility.design_data):
                # Check for resource storage
                # Extract abilities once per component (optimization)
                abilities = _extract_abilities(comp, self._registries)

                # Check for resource storage
                storage_entries = abilities.get('ResourceStorage')
                if storage_entries:
                    entries = storage_entries if isinstance(storage_entries, list) else [storage_entries]
                    for entry in entries:
                        if isinstance(entry, dict) and entry.get('resource') == resource:
                            new_capacity += entry.get('amount', 0.0)

                # Check for strategic resource generation
                gen_entries = abilities.get('StrategicResourceGeneration')
                if gen_entries:
                    entries = gen_entries if isinstance(gen_entries, list) else [gen_entries]
                    for entry in entries:
                        if isinstance(entry, dict) and entry.get('resource') == resource:
                            new_generation += entry.get('generation_rate', 0.0)

                # Check for shield (to compute drain)
                shield_data = abilities.get('PlanetaryShield')
                if isinstance(shield_data, dict):
                    has_shield_facility = True
                    if planet.shield_active:
                        total_drain += shield_data.get('energy_drain_rate', 0.0)

                # Check for other activatable abilities (stabilizers)
                for ability_key in _ACTIVATABLE_ABILITIES:
                    ability_data = abilities.get(ability_key)
                    if isinstance(ability_data, dict):
                        _active_facilities[ability_key] = True
                        if _is_ability_active(planet, ability_key):
                            total_drain += ability_data.get('energy_drain_rate', 0.0)

        planet.energy_capacity = new_capacity
        planet.energy_generation = new_generation

        # 2. Generate energy (1/100th per tick)
        if new_generation > 0:
            planet.energy += new_generation / 100.0

        # 3. Consume energy for active abilities (1/100th per tick)
        if total_drain > 0:
            drain_per_tick = total_drain / 100.0
            if planet.energy >= drain_per_tick:
                planet.energy -= drain_per_tick
            else:
                # Insufficient energy — auto-deactivate all active energy-draining abilities
                planet.energy = 0.0
                if planet.shield_active:
                    planet.shield_active = False
                    self._deactivate_shield_components(planet)
                    logger.info(f"Planet {planet.name}: shield auto-deactivated (energy depleted)")
                for ability_key in _ACTIVATABLE_ABILITIES:
                    if _is_ability_active(planet, ability_key):
                        _set_ability_active(planet, ability_key, False)
                        self._deactivate_ability_components(planet, ability_key)
                        logger.info(f"Planet {planet.name}: {ability_key} auto-deactivated (energy depleted)")

        # 4. If shield facility was destroyed while shield was active, deactivate
        if planet.shield_active and not has_shield_facility:
            planet.shield_active = False
            logger.info(
                f"Planet {planet.name}: shield deactivated (facility destroyed)"
            )

        # 4b. If activatable ability facility destroyed while active, deactivate
        for ability_key in _ACTIVATABLE_ABILITIES:
            if _is_ability_active(planet, ability_key) and not _active_facilities.get(ability_key, False):
                _set_ability_active(planet, ability_key, False)
                logger.info(f"Planet {planet.name}: {ability_key} deactivated (facility destroyed)")

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

    def _deactivate_ability_components(self, planet: 'Planet', ability_key: str) -> None:
        """Deactivate all components providing a specific ability on a planet."""
        for facility in planet.facilities:
            for comp in iter_components(facility.design_data):
                info = get_activatable_ability_info(comp, ability_key, self._registries)
                if info is not None:
                    comp_id = comp.get('id', '') if isinstance(comp, dict) else str(comp)
                    if comp_id:
                        facility.set_component_active(comp_id, False)
