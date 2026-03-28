"""System Data Transfer Objects.

Immutable DTOs representing star system data for the UI layer.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING

from game.core.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.stars import Star


@dataclass(frozen=True)
class StarInfo:
    """Immutable DTO representing a star with full attributes and system context.

    Attributes:
        name: Star designation (e.g., "Alpha Centauri A")
        star_type: Classification (e.g., "MAIN_SEQUENCE", "RED_GIANT")
        color: RGB color tuple for rendering
        location: Hex coordinate relative to system center
        mass: Mass in solar masses
        radius_hexes: Radius in game hexes (1-6)
        temperature: Surface temperature in Kelvin
        luminosity: Luminosity in solar luminosities
        age: Age in years
        system_name: Name of the containing star system
        system_global_location: Global hex coordinate of the system center
        planet_count: Number of planets in the system
        companion_star_count: Number of other stars in the same system
        spectrum_*: Flattened electromagnetic spectrum band intensities
    """

    name: str
    star_type: str
    color: Tuple[int, int, int]
    location: HexCoord
    mass: float = 0.0
    radius_hexes: int = 1
    temperature: float = 0.0
    luminosity: float = 0.0
    age: float = 0.0
    system_name: str = ""
    system_global_location: Optional[HexCoord] = None
    planet_count: int = 0
    companion_star_count: int = 0
    spectrum_gamma_ray: float = 0.0
    spectrum_xray: float = 0.0
    spectrum_ultraviolet: float = 0.0
    spectrum_blue: float = 0.0
    spectrum_green: float = 0.0
    spectrum_red: float = 0.0
    spectrum_infrared: float = 0.0
    spectrum_microwave: float = 0.0
    spectrum_radio: float = 0.0

    @classmethod
    def from_star(cls, star: 'Star', system_name: str = "",
                  system_global_location: Optional[HexCoord] = None,
                  planet_count: int = 0,
                  total_star_count: int = 1) -> 'StarInfo':
        """Create a StarInfo DTO from a Star domain object.

        Args:
            star: The Star domain object to convert
            system_name: Name of the containing star system
            system_global_location: Global hex of the system center
            planet_count: Number of planets in the system
            total_star_count: Total stars in the system (companions = total - 1)

        Returns:
            An immutable StarInfo DTO
        """
        return cls(
            name=star.name,
            star_type=star.star_type.name,
            color=star.color,
            location=star.location,
            mass=star.mass,
            radius_hexes=star.radius_hexes,
            temperature=star.temperature,
            luminosity=star.luminosity,
            age=star.age,
            system_name=system_name,
            system_global_location=system_global_location,
            planet_count=planet_count,
            companion_star_count=max(0, total_star_count - 1),
            spectrum_gamma_ray=star.spectrum.gamma_ray,
            spectrum_xray=star.spectrum.xray,
            spectrum_ultraviolet=star.spectrum.ultraviolet,
            spectrum_blue=star.spectrum.blue,
            spectrum_green=star.spectrum.green,
            spectrum_red=star.spectrum.red,
            spectrum_infrared=star.spectrum.infrared,
            spectrum_microwave=star.spectrum.microwave,
            spectrum_radio=star.spectrum.radio,
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
