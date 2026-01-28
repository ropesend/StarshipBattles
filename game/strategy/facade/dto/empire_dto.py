"""Empire Data Transfer Objects.

Immutable DTOs representing empire data for the UI layer.
"""
from dataclasses import dataclass
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet
    from game.strategy.data.fleet import Fleet


@dataclass(frozen=True)
class ColonySummary:
    """Immutable DTO representing a colony summary.

    Attributes:
        planet_id: Unique identifier for the planet
        planet_name: Planet name
        has_shipyard: Whether the colony has an orbital shipyard
    """

    planet_id: int
    planet_name: str
    has_shipyard: bool

    @classmethod
    def from_planet(cls, planet: 'Planet') -> 'ColonySummary':
        """Create a ColonySummary DTO from a Planet domain object.

        Args:
            planet: The Planet domain object (must be colonized)

        Returns:
            An immutable ColonySummary DTO
        """
        return cls(
            planet_id=planet.id,
            planet_name=planet.name,
            has_shipyard=planet.has_space_shipyard,
        )


@dataclass(frozen=True)
class FleetSummary:
    """Immutable DTO representing a fleet summary.

    Attributes:
        fleet_id: Unique identifier for the fleet
        ship_count: Number of ships in the fleet
        has_orders: Whether the fleet has any orders queued
    """

    fleet_id: int
    ship_count: int
    has_orders: bool

    @classmethod
    def from_fleet(cls, fleet: 'Fleet') -> 'FleetSummary':
        """Create a FleetSummary DTO from a Fleet domain object.

        Args:
            fleet: The Fleet domain object to convert

        Returns:
            An immutable FleetSummary DTO
        """
        return cls(
            fleet_id=fleet.id,
            ship_count=len(fleet.ships),
            has_orders=len(fleet.orders) > 0,
        )


@dataclass(frozen=True)
class EmpireInfo:
    """Immutable DTO representing an empire.

    Attributes:
        empire_id: Unique identifier for the empire
        name: Empire name
        color: RGB color tuple for UI rendering
        theme_id: Ship design theme identifier
        flag_id: Flag/emblem identifier
        colony_count: Number of colonies owned
        fleet_count: Number of fleets owned
    """

    empire_id: int
    name: str
    color: Tuple[int, int, int]
    theme_id: str
    flag_id: str
    colony_count: int = 0
    fleet_count: int = 0

    @classmethod
    def from_empire(cls, empire: 'Empire') -> 'EmpireInfo':
        """Create an EmpireInfo DTO from an Empire domain object.

        Args:
            empire: The Empire domain object to convert

        Returns:
            An immutable EmpireInfo DTO
        """
        return cls(
            empire_id=empire.id,
            name=empire.name,
            color=empire.color,
            theme_id=empire.empire_theme_id,
            flag_id=empire.flag_id,
            colony_count=len(empire.colonies),
            fleet_count=len(empire.fleets),
        )
