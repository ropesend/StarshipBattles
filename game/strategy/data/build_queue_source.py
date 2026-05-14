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
from game.core.paths import Paths
from game.strategy.services.modifier_resolver import resolve_size_multiplier

if TYPE_CHECKING:
    from game.strategy.data.planetary_facility import PlanetaryFacility



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
            _production_rates_cache = load_json(Paths.PRODUCTION_RATES_FILE)
        except (FileNotFoundError, ValueError):
            _production_rates_cache = {}
    return _production_rates_cache


def get_default_production_rates(yard_type: str) -> Dict[str, float]:
    """Get default per-resource production rates for a yard type.

    Args:
        yard_type: One of "planetary_yard", "space_shipyard".

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
        is_paused: FEAT-17 — mirrors the owning entity's
            `construction_queue_paused` flag at collection time. Canonical
            storage lives on the Planet / PlanetaryFacility / Fleet; this is
            a derived view consumed by Treasury / Planet-detail forecasts and
            the Empire Build Queue Status column to suppress paused yards.
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
    is_paused: bool = False


def get_build_rate_booster_mult(planet, galaxy=None, empire=None, registries=None) -> float:
    """Aggregate BuildRateBooster multipliers affecting a planet.

    Scans for BuildRateBooster abilities at sector and system scope
    and returns the combined multiplier using two-phase stacking.

    Args:
        planet: Planet to check for boosters.
        galaxy: Galaxy for spatial queries (optional).
        empire: Empire owning the planet (optional).
        registries: GameRegistries (optional).

    Returns:
        Combined build rate multiplier (1.0 if no boosters).
    """
    if galaxy is None or empire is None:
        return 1.0

    from game.strategy.services.strategic_ability_scanner import (
        find_abilities_in_scope, aggregate_multipliers,
    )

    all_boosters = []
    for scope in ["planet", "sector", "system", "empire"]:
        entries = find_abilities_in_scope(
            "BuildRateBooster", planet, galaxy, empire, scope,
            registries=registries,
        )
        all_boosters.extend(entries)

    return aggregate_multipliers(all_boosters)


def colony_has_planetary_yard(colony, registries=None) -> bool:
    """Check if a colony has an operational facility with PlanetaryYard ability.

    Scans facility design data for the PlanetaryYard ability key.

    PROJ-239: Moved from production_engine.py to eliminate data/→engine/ dependency.

    Args:
        colony: Planet with facilities to scan.
        registries: Optional GameRegistries for component lookup.

    Returns:
        True if the colony has a PlanetaryYard, False otherwise.
    """
    from game.core.patterns.layer_iterator import iter_components
    from game.strategy.services.component_inspector import get_component_abilities

    for facility in colony.facilities:
        if not facility.is_operational:
            continue
        for comp in iter_components(facility.design_data):
            # Check inline abilities
            if isinstance(comp, dict):
                abilities = comp.get('abilities', {})
                if 'PlanetaryYard' in abilities:
                    return True
                # Check registry
                comp_id = comp.get('id')
                if comp_id and registries:
                    comp_def = registries.components.get(comp_id)
                    if comp_def:
                        reg_abilities = get_component_abilities(comp_def)
                        if 'PlanetaryYard' in reg_abilities:
                            return True
            elif isinstance(comp, str) and registries:
                comp_def = registries.components.get(comp)
                if comp_def:
                    reg_abilities = get_component_abilities(comp_def)
                    if 'PlanetaryYard' in reg_abilities:
                        return True
    return False


def _get_facility_production_rates(facility: 'PlanetaryFacility') -> Dict[str, float]:
    """Extract per-resource production rates from a shipyard facility's design_data.

    Reads production_rates from the SpaceShipyard ability data if present,
    otherwise falls back to default rates. Applies construction_speed_bonus
    and size_mount scaling as multipliers to all rates.

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
                    size_mult = resolve_size_multiplier(comp)
                    # Check for explicit production_rates in ability data
                    explicit_rates = shipyard_data.get("production_rates", {})
                    if explicit_rates:
                        # Apply bonus and size scaling to explicit rates
                        return {res: rate * bonus * size_mult for res, rate in explicit_rates.items()}
                    # Fall back to default space_shipyard rates with bonus
                    base_rates = get_default_production_rates("space_shipyard")
                    return {res: rate * bonus * size_mult for res, rate in base_rates.items()}
    # Default if no SpaceShipyard ability found
    return get_default_production_rates("space_shipyard")


def _get_planetary_yard_size_multiplier(planet, registries=None) -> float:
    """Find the size_mount multiplier of the PlanetaryYard component on a planet.

    Scans all operational facilities for a PlanetaryYard ability and returns
    the size_mount value from the component that provides it.

    Args:
        planet: Planet with facilities to scan.
        registries: Optional GameRegistries for component lookup.

    Returns:
        Size multiplier (default 1.0 if no modifier or no PlanetaryYard found).
    """
    from game.core.patterns.layer_iterator import iter_components
    from game.strategy.services.component_inspector import get_component_abilities

    for facility in planet.facilities:
        if not getattr(facility, 'is_operational', True):
            continue
        for comp in iter_components(facility.design_data):
            if isinstance(comp, dict):
                abilities = comp.get('abilities', {})
                if 'PlanetaryYard' in abilities:
                    return resolve_size_multiplier(comp)
                # Check registry
                comp_id = comp.get('id')
                if comp_id and registries is not None:
                    comp_def = registries.components.get(comp_id)
                    if comp_def:
                        reg_abilities = get_component_abilities(comp_def)
                        if 'PlanetaryYard' in reg_abilities:
                            return resolve_size_multiplier(comp)
    return 1.0


def estimate_build_turns(total_cost: Dict[str, float],
                         production_rate: Dict[str, float]) -> float:
    """Estimate turns to complete a build item given its cost and production rate.

    Uses the limiting-resource formula: max(cost[res] / rate[res]) across all
    resources. This is the single source of truth for initial turn estimates
    (used by AddToConstructionQueueCommandHandler) and matches the per-tick
    calculation in ProductionEngine._calculate_tick_expenditure().

    Args:
        total_cost: Dict mapping resource name to total cost amount.
        production_rate: Dict mapping resource name to units produced per turn.

    Returns:
        Estimated turns, minimum 0.01. Falls back to 1.0 if cost is empty
        or any required resource has zero/missing production rate.
    """
    if not total_cost or not production_rate:
        return 1.0
    max_turns = 0.0
    for res, cost in total_cost.items():
        if cost <= 0:
            continue
        rate = production_rate.get(res, 0.0)
        if rate <= 0:
            return 1.0  # Can't estimate without rate
        turns = cost / rate
        if turns > max_turns:
            max_turns = turns
    return max(0.01, max_turns) if max_turns > 0 else 1.0


def get_production_rate_for_queue(entity, queue_id: Optional[str]) -> Dict[str, float]:
    """Get the production rate for a specific construction queue on an entity.

    Resolves the correct rate based on entity type (planet vs fleet) and
    queue_id (base queue vs facility queue). Uses the same rate-resolution
    logic as _collect_planet_sources / _collect_fleet_sources to ensure
    consistency between queue discovery and turn estimation.

    Args:
        entity: Planet or Fleet that owns the queue.
        queue_id: Queue identifier (facility instance_id, base queue id, or None).

    Returns:
        Dict mapping resource name to units per turn. Empty dict on failure.
    """
    from game.strategy.data.fleet import Fleet

    if isinstance(entity, Fleet):
        yard_count = getattr(entity.capabilities, 'space_shipyard_count', 1)
        base_rate = get_default_production_rates("space_shipyard")
        return {k: v * max(1, yard_count) for k, v in base_rate.items()}

    # Planet: check if queue_id points to a shipyard facility
    if queue_id and hasattr(entity, 'facilities'):
        for facility in entity.facilities:
            if getattr(facility, 'instance_id', None) == queue_id:
                if facility.is_shipyard:
                    return _get_facility_production_rates(facility)
                break

    # Default: planetary yard rate (for base queue / complexes)
    base_rates = get_default_production_rates("planetary_yard")
    if hasattr(entity, 'facilities'):
        yard_size_mult = _get_planetary_yard_size_multiplier(entity)
        return {res: rate * yard_size_mult for res, rate in base_rates.items()}
    return base_rates


def _collect_planet_sources(planet, sources: List[BuildQueueSource],
                            galaxy=None, empire=None, registries=None) -> None:
    """Collect build queue sources from a single planet.

    Adds the base planetary yard queue and any shipyard facility queues
    to the provided sources list.

    Args:
        planet: Planet instance to collect queues from.
        sources: List to append BuildQueueSource objects to.
        galaxy: Optional Galaxy for booster queries.
        empire: Optional Empire for booster queries.
        registries: Optional GameRegistries for component lookup.
    """
    # Base queue (complexes only) — only if colony has PlanetaryYard facility
    if colony_has_planetary_yard(planet, registries):
        base_rates = get_default_production_rates("planetary_yard")
        yard_size_mult = _get_planetary_yard_size_multiplier(planet, registries)
        build_booster = get_build_rate_booster_mult(planet, galaxy, empire, registries)
        scaled_rates = {res: rate * yard_size_mult * build_booster for res, rate in base_rates.items()}
        sources.append(BuildQueueSource(
            queue_id=f"planet_{planet.id}_base",
            display_name=f"{planet.name} - Planetary Yard",
            owner_entity=planet,
            construction_queue=planet.construction_queue,
            can_build_ships=False,
            can_build_complexes=True,
            context_type="planet",
            build_rate=scaled_rates,
            planet_id=planet.id,
            # FEAT-17: propagate the planet's per-base-queue pause flag.
            is_paused=getattr(planet, 'construction_queue_paused', False),
        ))

    # Shipyard facility queues
    shipyard_index = 0
    build_booster = get_build_rate_booster_mult(planet, galaxy, empire, registries) if galaxy and empire else 1.0
    for facility in planet.facilities:
        if facility.is_shipyard:
            shipyard_index += 1
            fac_rates = _get_facility_production_rates(facility)
            boosted_rates = {res: rate * build_booster for res, rate in fac_rates.items()}
            sources.append(BuildQueueSource(
                queue_id=facility.instance_id,
                display_name=f"{planet.name} - Shipyard {shipyard_index}",
                owner_entity=planet,
                construction_queue=facility.construction_queue,
                can_build_ships=True,
                can_build_complexes=True,
                context_type="planet",
                build_rate=boosted_rates,
                planet_id=planet.id,
                # FEAT-17: each facility carries its own pause flag.
                is_paused=getattr(facility, 'construction_queue_paused', False),
            ))


def _collect_fleet_sources(fleet, sources: List[BuildQueueSource]) -> None:
    """Collect build queue sources from a single fleet.

    Adds one queue source per space yard component in the fleet.

    Args:
        fleet: Fleet instance to collect queues from.
        sources: List to append BuildQueueSource objects to.
    """
    yard_count = fleet.capabilities.space_shipyard_count
    # FEAT-17: fleet yards share one queue, so the per-fleet flag applies to
    # every per-yard source we emit.
    fleet_paused = getattr(fleet, 'construction_queue_paused', False)
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
            build_rate=get_default_production_rates("space_shipyard"),
            planet_id=None,
            is_paused=fleet_paused,
        ))


def collect_build_queues_at_hex(hex_coord, galaxy, empire, registries=None) -> List[BuildQueueSource]:
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
        registries: Optional GameRegistries for component lookup.

    Returns:
        List of BuildQueueSource objects at the hex.
    """
    sources: List[BuildQueueSource] = []

    # Planet queues
    for planet in galaxy.get_planets_at_global_hex(hex_coord):
        if planet.owner_id != empire.id:
            continue
        _collect_planet_sources(planet, sources, galaxy=galaxy, empire=empire, registries=registries)

    # Fleet queues (one entry per space yard component)
    for fleet in empire.fleets:
        if fleet.location != hex_coord:
            continue
        _collect_fleet_sources(fleet, sources)

    return sources


def collect_all_build_queues_for_empire(empire, registries=None) -> List[BuildQueueSource]:
    """Gather all build queue sources across the entire empire.

    Iterates all colonies and fleets owned by the empire to produce a
    comprehensive list of every active construction queue. This includes:
    - One base queue per colony (complexes only)
    - One queue per operational shipyard facility on each colony
    - One queue per fleet with a space yard

    Args:
        empire: Empire instance whose queues to collect.
        registries: Optional GameRegistries for component lookup.

    Returns:
        List of BuildQueueSource objects for the whole empire.
    """
    sources: List[BuildQueueSource] = []

    # Planet queues
    for planet in empire.colonies:
        _collect_planet_sources(planet, sources, registries=registries)

    # Fleet queues (one entry per space yard component)
    for fleet in empire.fleets:
        _collect_fleet_sources(fleet, sources)

    return sources
