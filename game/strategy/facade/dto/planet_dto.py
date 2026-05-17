"""Planet Data Transfer Objects.

Immutable DTOs representing planet data for the UI layer.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple, TYPE_CHECKING

from game.core.hex_math import HexCoord
from game.strategy.services.ability_metadata import (
    StrategicKind,
    abilities_with_kind_tag,
)

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet


def _is_any_planetary_shield_active(active_abilities: object) -> bool:
    """True iff any PLANETARY_SHIELD-tagged ability is active on the planet.

    PROJ-429 / TD-07 Phase 8 (Codex follow-up): the ability name
    (``"PlanetaryShield"``) is no longer hardcoded here; it comes from
    ``abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)``. Mirrors
    the migration in ``planet_energy_engine.get_shield_info``.
    """
    if not isinstance(active_abilities, dict):
        return False
    for shield_name in abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD):
        if active_abilities.get(shield_name, False):
            return True
    return False


def _dict_to_tuple(d) -> Tuple[Tuple[str, float], ...]:
    """Convert a dict to a frozen tuple of (key, value) pairs.

    Returns empty tuple if d is None, not a dict, or not iterable.
    """
    if isinstance(d, dict):
        return tuple((k, v) for k, v in d.items())
    return ()


@dataclass(frozen=True)
class PlanetInfo:
    """Immutable DTO representing a planet.

    Attributes:
        planet_id: Unique identifier for the planet
        name: Planet name
        planet_type: Classification (e.g., "TERRESTRIAL", "GAS_GIANT")
        location: Hex coordinate relative to system center
        orbit_distance: Distance from star in orbit rings
        owner_id: Empire ID of the owner (None if unclaimed)
        is_colonized: Whether the planet has a colony
        has_space_shipyard: Whether the planet has an orbital shipyard
        total_population: Total population units across all species
        max_population: Maximum population capacity based on surface area
        population_details: Tuple of (race_id, count, happiness) for each species
    """

    planet_id: int
    name: str
    planet_type: str
    location: HexCoord
    orbit_distance: int
    owner_id: Optional[int] = None
    is_colonized: bool = False
    has_space_shipyard: bool = False
    total_population: int = 0
    max_population: int = 0
    population_details: Tuple[Tuple[str, int, float], ...] = field(default_factory=tuple)
    # PROJ-237: Energy and shield state
    energy: float = 0.0
    energy_capacity: float = 0.0
    shield_active: bool = False
    # Local resource stockpile
    stockpile: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    max_stockpile: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    # Staging yard items: tuple of (name, vehicle_type, mass, count)
    staging_yard_summary: Tuple[Tuple[str, str, float, int], ...] = field(default_factory=tuple)

    @classmethod
    def from_planet(cls, planet: 'Planet') -> 'PlanetInfo':
        """Create a PlanetInfo DTO from a Planet domain object.

        Args:
            planet: The Planet domain object to convert

        Returns:
            An immutable PlanetInfo DTO
        """
        # Build population details tuple
        pop_details = tuple(
            (p.race_id, p.count, p.happiness)
            for p in planet.populations
        )

        # Aggregate staging yard items by name
        staging_counts: dict = {}
        staging_yard = getattr(planet, 'staging_yard', None)
        for item in (staging_yard if isinstance(staging_yard, list) else []):
            name = item.get('name', 'Unknown')
            vtype = item.get('vehicle_type', 'unknown')
            mass = item.get('mass', 0.0)
            key = (name, vtype, mass)
            staging_counts[key] = staging_counts.get(key, 0) + 1
        staging_summary = tuple(
            (name, vtype, mass, count)
            for (name, vtype, mass), count in staging_counts.items()
        )

        return cls(
            planet_id=planet.id,
            name=planet.name,
            planet_type=planet.planet_type.name,
            location=planet.location,
            orbit_distance=planet.orbit_distance,
            owner_id=planet.owner_id,
            is_colonized=planet.owner_id is not None,
            has_space_shipyard=planet.has_space_shipyard,
            total_population=planet.total_population,
            max_population=planet.max_population,
            population_details=pop_details,
            energy=getattr(planet, 'energy', 0.0),
            energy_capacity=getattr(planet, 'energy_capacity', 0.0),
            shield_active=_is_any_planetary_shield_active(
                getattr(planet, 'active_abilities', {})
            ),
            stockpile=_dict_to_tuple(getattr(planet, 'stockpile', None)),
            max_stockpile=_dict_to_tuple(getattr(planet, 'max_stockpile', None)),
            staging_yard_summary=staging_summary,
        )
