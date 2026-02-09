"""
BuildQueueSource - Abstraction for discovering build queues at a hex location.

Each build queue source represents a single construction queue from either:
- A planet's base queue (complexes only)
- A planetary shipyard facility queue (ships + complexes)
- A fleet space yard queue (ships + complexes)

Created as part of PROJ-69 Phase 1.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.planet import PlanetaryFacility


@dataclass
class BuildQueueSource:
    """A single build queue source from a planet facility or fleet.

    Attributes:
        queue_id: Unique identifier for this queue source.
        display_name: Human-readable name for UI display.
        owner_entity: Reference to the Planet or Fleet that owns this queue.
        construction_queue: Reference to the actual queue list (mutable).
        can_build_ships: Whether ships/fighters/satellites can be queued.
        can_build_complexes: Whether complexes can be queued.
        context_type: "planet" or "fleet" for UI branching.
    """
    queue_id: str
    display_name: str
    owner_entity: Any
    construction_queue: List[Dict[str, Any]]
    can_build_ships: bool
    can_build_complexes: bool
    context_type: str
    build_rate: float = 2000.0
    planet_id: Optional[int] = None


def _get_facility_build_rate(facility: 'PlanetaryFacility') -> float:
    """Extract build rate from a shipyard facility's design_data.

    Shipyards build at 3000 units/turn * construction_speed_bonus.

    Args:
        facility: The planetary facility to check.

    Returns:
        Build rate in units per turn.
    """
    for layer_data in facility.design_data.get("layers", {}).values():
        if not isinstance(layer_data, list):
            continue
        for comp in layer_data:
            if isinstance(comp, dict):
                abilities = comp.get("abilities", {})
                shipyard_data = abilities.get("SpaceShipyard", {})
                if isinstance(shipyard_data, dict):
                    bonus = shipyard_data.get("construction_speed_bonus", 1.0)
                    return 3000.0 * bonus
    return 3000.0  # Default shipyard rate


def _facility_is_shipyard(facility: PlanetaryFacility) -> bool:
    """Check if a planetary facility is a space shipyard.

    Reuses the same detection logic as Planet.has_space_shipyard:
    scans design_data layers for component id 'space_shipyard' or
    SpaceShipyard ability.

    Args:
        facility: The planetary facility to check.

    Returns:
        True if the facility is an operational space shipyard.
    """
    if not facility.is_operational:
        return False

    for layer_data in facility.design_data.get("layers", {}).values():
        if not isinstance(layer_data, list):
            continue
        for comp in layer_data:
            if isinstance(comp, dict):
                if comp.get("id") == "space_shipyard":
                    return True
                if "SpaceShipyard" in comp.get("abilities", {}):
                    return True
    return False


def collect_build_queues_at_hex(hex_coord, galaxy, empire) -> List[BuildQueueSource]:
    """Gather all build queue sources at a hex for the given empire.

    Returns a list of BuildQueueSource objects representing every active
    build queue at the specified hex coordinate. This includes:
    - One base queue per owned planet (complexes only)
    - One queue per operational shipyard facility on each planet
    - One queue per fleet with a space yard at the hex

    Args:
        hex_coord: The hex coordinate to query.
        galaxy: Galaxy instance for planet lookup.
        empire: Empire instance for ownership check and fleet access.

    Returns:
        List of BuildQueueSource objects at the hex.
    """
    sources: List[BuildQueueSource] = []

    # Planet queues
    for planet in galaxy.get_planets_at_global_hex(hex_coord):
        if planet.owner_id != empire.id:
            continue

        # Base queue (complexes only)
        sources.append(BuildQueueSource(
            queue_id=f"planet_{planet.id}_base",
            display_name=f"{planet.name} - Planetary Yard",
            owner_entity=planet,
            construction_queue=planet.construction_queue,
            can_build_ships=False,
            can_build_complexes=True,
            context_type="planet",
            build_rate=2000.0,
            planet_id=planet.id,
        ))

        # Shipyard facility queues
        shipyard_index = 0
        for facility in planet.facilities:
            if _facility_is_shipyard(facility):
                shipyard_index += 1
                sources.append(BuildQueueSource(
                    queue_id=facility.instance_id,
                    display_name=f"{planet.name} - Shipyard {shipyard_index}",
                    owner_entity=planet,
                    construction_queue=facility.construction_queue,
                    can_build_ships=True,
                    can_build_complexes=True,
                    context_type="planet",
                    build_rate=_get_facility_build_rate(facility),
                    planet_id=planet.id,
                ))

    # Fleet queues
    for fleet in empire.fleets:
        if fleet.location != hex_coord:
            continue
        if not fleet.has_space_shipyard:
            continue
        sources.append(BuildQueueSource(
            queue_id=f"fleet_{fleet.id}",
            display_name=f"{fleet.name} - Shipyard",
            owner_entity=fleet,
            construction_queue=fleet.construction_queue,
            can_build_ships=True,
            can_build_complexes=True,
            context_type="fleet",
            build_rate=3000.0,
            planet_id=None,
        ))

    return sources


def collect_all_build_queues_for_empire(empire) -> List[BuildQueueSource]:
    """Gather all build queue sources across the entire empire.

    Iterates all colonies and fleets owned by the empire to produce a
    comprehensive list of every active construction queue. This includes:
    - One base queue per colony (complexes only)
    - One queue per operational shipyard facility on each colony
    - One queue per fleet with a space yard

    Args:
        empire: Empire instance whose queues to collect.

    Returns:
        List of BuildQueueSource objects for the whole empire.
    """
    sources: List[BuildQueueSource] = []

    # Planet queues
    for planet in empire.colonies:
        # Base queue (complexes only)
        sources.append(BuildQueueSource(
            queue_id=f"planet_{planet.id}_base",
            display_name=f"{planet.name} - Planetary Yard",
            owner_entity=planet,
            construction_queue=planet.construction_queue,
            can_build_ships=False,
            can_build_complexes=True,
            context_type="planet",
            build_rate=2000.0,
            planet_id=planet.id,
        ))

        # Shipyard facility queues
        shipyard_index = 0
        for facility in planet.facilities:
            if _facility_is_shipyard(facility):
                shipyard_index += 1
                sources.append(BuildQueueSource(
                    queue_id=facility.instance_id,
                    display_name=f"{planet.name} - Shipyard {shipyard_index}",
                    owner_entity=planet,
                    construction_queue=facility.construction_queue,
                    can_build_ships=True,
                    can_build_complexes=True,
                    context_type="planet",
                    build_rate=_get_facility_build_rate(facility),
                    planet_id=planet.id,
                ))

    # Fleet queues
    for fleet in empire.fleets:
        if not fleet.has_space_shipyard:
            continue
        sources.append(BuildQueueSource(
            queue_id=f"fleet_{fleet.id}",
            display_name=f"{fleet.name} - Shipyard",
            owner_entity=fleet,
            construction_queue=fleet.construction_queue,
            can_build_ships=True,
            can_build_complexes=True,
            context_type="fleet",
            build_rate=3000.0,
            planet_id=None,
        ))

    return sources
