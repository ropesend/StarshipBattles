"""
BuildQueueSource - Abstraction for discovering build queues at a hex location.

Each build queue source represents a single construction queue from either:
- A planet's base queue (complexes only)
- A planetary shipyard facility queue (ships + complexes)
- A fleet space yard queue (ships + complexes)

Created as part of PROJ-69 Phase 1.
Updated in PROJ-97: build_rate is now Dict[str, float] for per-resource rates.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.core.json_utils import load_json

if TYPE_CHECKING:
    from game.strategy.data.planet import PlanetaryFacility


# Module-level cache for production rates JSON
_production_rates_cache: Optional[Dict[str, Dict[str, float]]] = None


def _load_production_rates() -> Dict[str, Dict[str, float]]:
    """Load production rates from JSON file with caching.

    Returns:
        Dict mapping yard type to per-resource rates.
    """
    global _production_rates_cache
    if _production_rates_cache is None:
        try:
            _production_rates_cache = load_json("data/production_rates.json")
        except (FileNotFoundError, ValueError):
            _production_rates_cache = {}
    return _production_rates_cache


def get_default_production_rates(yard_type: str) -> Dict[str, float]:
    """Get default per-resource production rates for a yard type.

    Args:
        yard_type: One of "planetary_yard", "space_shipyard", "fleet_space_yard".

    Returns:
        Dict mapping resource name to max units per turn.
        Empty dict if yard_type unknown or file missing.
    """
    rates = _load_production_rates()
    return dict(rates.get(yard_type, {}))


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
        build_rate: Per-resource production rates (units per turn).
        planet_id: Planet ID for planet-based queues, None for fleet queues.
    """
    queue_id: str
    display_name: str
    owner_entity: Any
    construction_queue: List[Dict[str, Any]]
    can_build_ships: bool
    can_build_complexes: bool
    context_type: str
    build_rate: Dict[str, float] = field(default_factory=dict)
    planet_id: Optional[int] = None


def _get_facility_production_rates(facility: 'PlanetaryFacility') -> Dict[str, float]:
    """Extract per-resource production rates from a shipyard facility's design_data.

    Reads production_rates from the SpaceShipyard ability data if present,
    otherwise falls back to default rates. Applies construction_speed_bonus
    as a multiplier to all rates.

    Args:
        facility: The planetary facility to check.

    Returns:
        Dict mapping resource name to max units per turn.
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
                    # Check for explicit production_rates in ability data
                    explicit_rates = shipyard_data.get("production_rates", {})
                    if explicit_rates:
                        # Apply bonus to explicit rates
                        return {res: rate * bonus for res, rate in explicit_rates.items()}
                    # Fall back to default space_shipyard rates with bonus
                    base_rates = get_default_production_rates("space_shipyard")
                    return {res: rate * bonus for res, rate in base_rates.items()}
    # Default if no SpaceShipyard ability found
    return get_default_production_rates("space_shipyard")


def _facility_is_shipyard(facility: 'PlanetaryFacility') -> bool:
    """Check if a planetary facility is a space shipyard.

    Delegates to PlanetaryFacility.is_shipyard property which checks
    design_data layers for component id 'space_shipyard' or SpaceShipyard ability.

    Args:
        facility: The planetary facility to check.

    Returns:
        True if the facility is an operational space shipyard.
    """
    return facility.is_shipyard


def _collect_planet_sources(planet, sources: List[BuildQueueSource]) -> None:
    """Collect build queue sources from a single planet.

    Adds the base planetary yard queue and any shipyard facility queues
    to the provided sources list.

    Args:
        planet: Planet instance to collect queues from.
        sources: List to append BuildQueueSource objects to.
    """
    # Base queue (complexes only)
    sources.append(BuildQueueSource(
        queue_id=f"planet_{planet.id}_base",
        display_name=f"{planet.name} - Planetary Yard",
        owner_entity=planet,
        construction_queue=planet.construction_queue,
        can_build_ships=False,
        can_build_complexes=True,
        context_type="planet",
        build_rate=get_default_production_rates("planetary_yard"),
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
                build_rate=_get_facility_production_rates(facility),
                planet_id=planet.id,
            ))


def _collect_fleet_sources(fleet, sources: List[BuildQueueSource]) -> None:
    """Collect build queue sources from a single fleet.

    Adds one queue source per space yard component in the fleet.

    Args:
        fleet: Fleet instance to collect queues from.
        sources: List to append BuildQueueSource objects to.
    """
    yard_count = fleet.space_shipyard_count
    for yard_idx in range(yard_count):
        yard_num = yard_idx + 1
        display_suffix = f" - Shipyard {yard_num}" if yard_count > 1 else " - Shipyard"
        sources.append(BuildQueueSource(
            queue_id=f"fleet_{fleet.id}_yard_{yard_num}",
            display_name=f"{fleet.name}{display_suffix}",
            owner_entity=fleet,
            construction_queue=fleet.construction_queue,
            can_build_ships=True,
            can_build_complexes=True,
            context_type="fleet",
            build_rate=get_default_production_rates("fleet_space_yard"),
            planet_id=None,
        ))


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
        _collect_planet_sources(planet, sources)

    # Fleet queues (one entry per space yard component)
    for fleet in empire.fleets:
        if fleet.location != hex_coord:
            continue
        _collect_fleet_sources(fleet, sources)

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
        _collect_planet_sources(planet, sources)

    # Fleet queues (one entry per space yard component)
    for fleet in empire.fleets:
        _collect_fleet_sources(fleet, sources)

    return sources
