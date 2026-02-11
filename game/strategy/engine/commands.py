from dataclasses import dataclass
from typing import Optional, List
from enum import Enum, auto

from game.core.hex_math import HexCoord

class CommandType(Enum):
    ISSUE_ORDER = auto()
    # Add other types as needed (e.g., GAME_SETTINGS, CHEAT_CODE)

@dataclass
class Command:
    """Base class for all game commands."""
    type: CommandType
    
    @property
    def name(self) -> str:
        return self.__class__.__name__

@dataclass
class IssueColonizeCommand(Command):
    """Command to issue a colonization order to a fleet."""
    fleet_id: int
    planet_id: Optional[int] # None for 'Any Planet'
    
    def __init__(self, fleet_id: int, planet_id: Optional[int] = None):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.planet_id = planet_id

@dataclass
class IssueMoveCommand(Command):
    """Command to move a fleet to a target hex."""
    fleet_id: int
    target_hex: HexCoord
    
    def __init__(self, fleet_id: int, target_hex: HexCoord):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex

@dataclass
class IssueBuildShipCommand(Command):
    """Command to build a ship at a colony."""
    planet_id: int
    design_name: str

    def __init__(self, planet_id: int, design_name: str):
        self.type = CommandType.ISSUE_ORDER
        self.planet_id = planet_id
        self.design_name = design_name


@dataclass
class IssueInterceptCommand(Command):
    """Command to issue an intercept order to a fleet.

    The fleet will move toward the target fleet's position.
    """
    fleet_id: int
    target_fleet_id: int

    def __init__(self, fleet_id: int, target_fleet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_fleet_id = target_fleet_id


@dataclass
class IssueJoinFleetCommand(Command):
    """Command to issue a join fleet order.

    The fleet will move to and merge with the target fleet.
    """
    fleet_id: int
    target_fleet_id: int

    def __init__(self, fleet_id: int, target_fleet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_fleet_id = target_fleet_id


@dataclass
class QueueColonizeMissionCommand(Command):
    """Command to queue a colonize mission (move + colonize).

    The fleet will move to the target hex and then colonize the planet.
    If planet_id is None, the fleet will colonize the largest available
    planet when it arrives at the target hex.
    """
    fleet_id: int
    target_hex: HexCoord
    planet_id: Optional[int]  # None for 'colonize any/largest available planet'

    def __init__(self, fleet_id: int, target_hex: HexCoord, planet_id: Optional[int] = None):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex
        self.planet_id = planet_id


@dataclass
class ClearFleetOrdersCommand(Command):
    """Command to clear all orders from a fleet."""
    fleet_id: int

    def __init__(self, fleet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id


@dataclass
class IssueTransferCommand(Command):
    """
    Command to issue a TRANSFER order for cargo operations.

    Transfers cargo (passengers, etc.) between a fleet and a colony.

    Args:
        fleet_id: The fleet to transfer cargo to/from
        planet_id: The planet/colony to transfer cargo to/from
        cargo_type: Type of cargo (e.g., 'passengers')
        direction: 'load' (colony→fleet) or 'unload' (fleet→colony)
        amount: Units to transfer (0 = transfer all available)
        species_id: Optional species ID for population transfers (PROJ-68)
    """
    fleet_id: int
    planet_id: int
    cargo_type: str
    direction: str  # "load" or "unload"
    amount: int  # 0 = all
    species_id: Optional[str] = None

    def __init__(
        self,
        fleet_id: int,
        planet_id: int,
        cargo_type: str,
        direction: str,
        amount: int = 0,
        species_id: Optional[str] = None
    ):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.planet_id = planet_id
        self.cargo_type = cargo_type
        self.direction = direction
        self.amount = amount
        self.species_id = species_id


# =============================================================================
# Superweapon Commands (PROJ-102)
# =============================================================================

@dataclass
class IssueImplodePlanetCommand(Command):
    """Command to issue an IMPLODE_PLANET order to destroy a planet."""
    fleet_id: int
    planet_id: int

    def __init__(self, fleet_id: int, planet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.planet_id = planet_id


@dataclass
class IssueStellerateStarCommand(Command):
    """Command to issue a STELLERATE_STAR order to destroy the star at fleet location."""
    fleet_id: int

    def __init__(self, fleet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id


@dataclass
class IssueOpenWarpPointCommand(Command):
    """Command to issue an OPEN_WARP_POINT order to create a warp link."""
    fleet_id: int
    target_hex: HexCoord
    target_system_name: str

    def __init__(self, fleet_id: int, target_hex: HexCoord, target_system_name: str):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex
        self.target_system_name = target_system_name


@dataclass
class IssueCloseWarpPointCommand(Command):
    """Command to issue a CLOSE_WARP_POINT order to destroy a warp link."""
    fleet_id: int
    warp_point_destination_id: str

    def __init__(self, fleet_id: int, warp_point_destination_id: str):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.warp_point_destination_id = warp_point_destination_id


@dataclass
class IssueCreateDysonSphereCommand(Command):
    """Command to issue a CREATE_DYSON_SPHERE order to create a Dyson Sphere."""
    fleet_id: int

    def __init__(self, fleet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id


@dataclass
class IssueSelfDestructCommand(Command):
    """Command to issue a SELF_DESTRUCT order to destroy selected ships."""
    fleet_id: int
    ship_ids: List[int]

    def __init__(self, fleet_id: int, ship_ids: List[int]):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.ship_ids = ship_ids


# =============================================================================
# Superweapon Mission Commands (Move + Action) (PROJ-102)
# =============================================================================

@dataclass
class QueueImplodePlanetMissionCommand(Command):
    """Command to queue a move-to-hex then implode planet mission."""
    fleet_id: int
    target_hex: HexCoord
    planet_id: int

    def __init__(self, fleet_id: int, target_hex: HexCoord, planet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex
        self.planet_id = planet_id


@dataclass
class QueueStellerateStarMissionCommand(Command):
    """Command to queue a move-to-hex then stellerate star mission."""
    fleet_id: int
    target_hex: HexCoord

    def __init__(self, fleet_id: int, target_hex: HexCoord):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex


@dataclass
class QueueOpenWarpPointMissionCommand(Command):
    """Command to queue a move-to-hex then open warp point mission."""
    fleet_id: int
    target_hex: HexCoord
    target_system_name: str

    def __init__(self, fleet_id: int, target_hex: HexCoord, target_system_name: str):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex
        self.target_system_name = target_system_name


@dataclass
class QueueCloseWarpPointMissionCommand(Command):
    """Command to queue a move-to-hex then close warp point mission."""
    fleet_id: int
    target_hex: HexCoord
    warp_point_destination_id: str

    def __init__(self, fleet_id: int, target_hex: HexCoord, warp_point_destination_id: str):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex
        self.warp_point_destination_id = warp_point_destination_id


@dataclass
class QueueCreateDysonSphereMissionCommand(Command):
    """Command to queue a move-to-hex then create Dyson Sphere mission."""
    fleet_id: int
    target_hex: HexCoord

    def __init__(self, fleet_id: int, target_hex: HexCoord):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.target_hex = target_hex
