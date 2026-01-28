"""Planet Data Transfer Objects.

Immutable DTOs representing planet data for the UI layer.
"""
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from game.strategy.data.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet


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
    """

    planet_id: int
    name: str
    planet_type: str
    location: HexCoord
    orbit_distance: int
    owner_id: Optional[int] = None
    is_colonized: bool = False
    has_space_shipyard: bool = False

    @classmethod
    def from_planet(cls, planet: 'Planet') -> 'PlanetInfo':
        """Create a PlanetInfo DTO from a Planet domain object.

        Args:
            planet: The Planet domain object to convert

        Returns:
            An immutable PlanetInfo DTO
        """
        return cls(
            planet_id=planet.id,
            name=planet.name,
            planet_type=planet.planet_type.name,
            location=planet.location,
            orbit_distance=planet.orbit_distance,
            owner_id=planet.owner_id,
            is_colonized=planet.owner_id is not None,
            has_space_shipyard=planet.has_space_shipyard,
        )
