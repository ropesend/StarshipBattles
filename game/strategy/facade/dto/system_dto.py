"""System Data Transfer Objects.

Immutable DTOs representing star system data for the UI layer.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING

from game.strategy.data.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.stars import Star


@dataclass(frozen=True)
class StarInfo:
    """Immutable DTO representing a star.

    Attributes:
        name: Star designation (e.g., "Alpha Centauri A")
        star_type: Classification (e.g., "MAIN_SEQUENCE", "RED_GIANT")
        color: RGB color tuple for rendering
        location: Hex coordinate relative to system center
    """

    name: str
    star_type: str
    color: Tuple[int, int, int]
    location: HexCoord

    @classmethod
    def from_star(cls, star: 'Star') -> 'StarInfo':
        """Create a StarInfo DTO from a Star domain object.

        Args:
            star: The Star domain object to convert

        Returns:
            An immutable StarInfo DTO
        """
        return cls(
            name=star.name,
            star_type=star.star_type.name,
            color=star.color,
            location=star.location,
        )


@dataclass(frozen=True)
class WarpPointInfo:
    """Immutable DTO representing a warp point.

    Attributes:
        destination_system_name: Name of the destination star system
        location: Hex coordinate relative to system center
    """

    destination_system_name: str
    location: HexCoord


@dataclass(frozen=True)
class SystemInfo:
    """Immutable DTO representing a star system.

    Attributes:
        name: System name
        global_location: Hex coordinate on the galaxy map
        primary_star: StarInfo for the primary star (if any)
        planet_count: Number of planets in the system
        warp_point_count: Number of warp points
        colony_count: Number of colonized planets
    """

    name: str
    global_location: HexCoord
    primary_star: Optional[StarInfo] = None
    planet_count: int = 0
    warp_point_count: int = 0
    colony_count: int = 0

    @classmethod
    def from_star_system(cls, system: 'StarSystem') -> 'SystemInfo':
        """Create a SystemInfo DTO from a StarSystem domain object.

        Args:
            system: The StarSystem domain object to convert

        Returns:
            An immutable SystemInfo DTO
        """
        # Convert primary star if present
        primary_star_info = None
        if system.primary_star:
            primary_star_info = StarInfo.from_star(system.primary_star)

        # Count colonized planets
        colony_count = sum(1 for p in system.planets if p.owner_id is not None)

        return cls(
            name=system.name,
            global_location=system.global_location,
            primary_star=primary_star_info,
            planet_count=len(system.planets),
            warp_point_count=len(system.warp_points),
            colony_count=colony_count,
        )
