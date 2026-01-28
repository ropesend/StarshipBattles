"""Data Transfer Objects for the Strategy Session Facade.

All DTOs are frozen dataclasses to ensure immutability.
The UI layer receives DTOs instead of domain objects.
"""

from game.strategy.facade.dto.fleet_dto import FleetOrderInfo, ShipInfo, FleetInfo
from game.strategy.facade.dto.system_dto import StarInfo, WarpPointInfo, SystemInfo
from game.strategy.facade.dto.planet_dto import PlanetInfo
from game.strategy.facade.dto.empire_dto import ColonySummary, FleetSummary, EmpireInfo

__all__ = [
    "FleetOrderInfo",
    "ShipInfo",
    "FleetInfo",
    "StarInfo",
    "WarpPointInfo",
    "SystemInfo",
    "PlanetInfo",
    "ColonySummary",
    "FleetSummary",
    "EmpireInfo",
]
