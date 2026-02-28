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

    Transfers cargo (passengers, etc.) between a fleet and a colony,
    or between two fleets.

    Args:
        fleet_id: The fleet to transfer cargo to/from (primary fleet)
        planet_id: The planet/colony to transfer cargo to/from (optional)
        cargo_type: Type of cargo (e.g., 'passengers')
        direction: 'load' (target→fleet) or 'unload' (fleet→target)
        amount: Units to transfer (0 = transfer all available)
        species_id: Optional species ID for population transfers
        target_fleet_id: The other fleet to transfer cargo to/from (optional)
    """
    fleet_id: int
    planet_id: Optional[int]
    cargo_type: str
    direction: str  # "load" or "unload"
    amount: int  # 0 = all
    species_id: Optional[str] = None
    target_fleet_id: Optional[int] = None

    def __init__(
        self,
        fleet_id: int,
        planet_id: Optional[int] = None,
        cargo_type: str = "passengers",
        direction: str = "load",
        amount: int = 0,
        species_id: Optional[str] = None,
        target_fleet_id: Optional[int] = None
    ):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.planet_id = planet_id
        self.cargo_type = cargo_type
        self.direction = direction
        self.amount = amount
        self.species_id = species_id
        self.target_fleet_id = target_fleet_id


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


# =============================================================================
# WARP Commands (PROJ-187)
# =============================================================================

@dataclass
class IssueWarpCommand(Command):
    """Command to issue a WARP order to traverse a specific warp point.

    PROJ-187: Explicit warp point traversal. If the fleet is not at the
    warp point, automatically queues a MOVE order first.

    Args:
        fleet_id: The fleet to issue the warp order to
        warp_point_hex: The global hex coordinate of the warp point to enter
    """
    fleet_id: int
    warp_point_hex: HexCoord

    def __init__(self, fleet_id: int, warp_point_hex: HexCoord):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.warp_point_hex = warp_point_hex


# =============================================================================
# BUILD Order Commands (PROJ-207)
# =============================================================================

@dataclass
class IssueBuildOrderCommand(Command):
    """Command to issue a BUILD order to a fleet with space shipyard.

    PROJ-207 Phase 4: Routes fleet BUILD orders through command pipeline.
    The BUILD order tells the fleet to execute its construction queue.
    """
    fleet_id: int

    def __init__(self, fleet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id


@dataclass
class RemoveBuildOrderCommand(Command):
    """Command to remove BUILD orders from a fleet.

    PROJ-207 Phase 4: Used when construction queue is emptied.
    """
    fleet_id: int

    def __init__(self, fleet_id: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id


# =============================================================================
# Fleet Management Commands (PROJ-208)
# =============================================================================

@dataclass
class SplitFleetCommand(Command):
    """Command to remove ships from a fleet and create a new fleet.

    PROJ-208 Phase 1: Routes fleet splitting through command pipeline.
    The removed ships are placed into a newly created fleet at the same location.

    Args:
        fleet_id: Source fleet to remove ships from.
        ship_instance_ids: List of ship instance_id strings to move to new fleet.
    """
    fleet_id: int
    ship_instance_ids: List[str]

    def __init__(self, fleet_id: int, ship_instance_ids: List[str]):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.ship_instance_ids = ship_instance_ids


@dataclass
class DeleteFleetOrderCommand(Command):
    """Command to remove a specific order from a fleet's order queue.

    PROJ-208 Phase 1: Routes order deletion through command pipeline.

    Args:
        fleet_id: Fleet whose order queue to modify.
        order_index: Index of the order to remove (0-based).
    """
    fleet_id: int
    order_index: int

    def __init__(self, fleet_id: int, order_index: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.order_index = order_index


@dataclass
class ReorderFleetOrderCommand(Command):
    """Command to move a fleet order up or down in the queue.

    PROJ-208 Phase 1: Routes order reordering through command pipeline.

    Args:
        fleet_id: Fleet whose order queue to modify.
        order_index: Index of the order to move.
        direction: -1 for up (earlier), +1 for down (later).
    """
    fleet_id: int
    order_index: int
    direction: int

    def __init__(self, fleet_id: int, order_index: int, direction: int):
        self.type = CommandType.ISSUE_ORDER
        self.fleet_id = fleet_id
        self.order_index = order_index
        self.direction = direction


# =============================================================================
# Construction Queue Commands (PROJ-208 Phase 2)
# =============================================================================

@dataclass
class AddToConstructionQueueCommand(Command):
    """Command to add a design to a planet or fleet construction queue.

    PROJ-208 Phase 2: Routes construction queue additions through command pipeline.

    Args:
        entity_id: Planet or fleet ID.
        entity_type: "planet" or "fleet".
        design_id: ID of the design to build.
        category: Design category ("complex", "ship", "satellite", "fighter").
        index: Optional insertion index. None = append to end.
        target_planet_id: For complexes built at fleet yards, the target planet.
    """
    entity_id: int
    entity_type: str
    design_id: str
    category: str
    index: Optional[int] = None
    target_planet_id: Optional[int] = None

    def __init__(
        self,
        entity_id: int,
        entity_type: str,
        design_id: str,
        category: str,
        index: Optional[int] = None,
        target_planet_id: Optional[int] = None
    ):
        self.type = CommandType.ISSUE_ORDER
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.design_id = design_id
        self.category = category
        self.index = index
        self.target_planet_id = target_planet_id


@dataclass
class RemoveFromConstructionQueueCommand(Command):
    """Command to remove an item from a construction queue.

    PROJ-208 Phase 2: Routes construction queue removals through command pipeline.

    Args:
        entity_id: Planet or fleet ID.
        entity_type: "planet" or "fleet".
        item_index: Index of the item to remove.
    """
    entity_id: int
    entity_type: str
    item_index: int

    def __init__(self, entity_id: int, entity_type: str, item_index: int):
        self.type = CommandType.ISSUE_ORDER
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.item_index = item_index


@dataclass
class ReorderConstructionQueueCommand(Command):
    """Command to move a construction queue item to a new position.

    PROJ-208 Phase 2: Routes construction queue reordering through command pipeline.

    Args:
        entity_id: Planet or fleet ID.
        entity_type: "planet" or "fleet".
        from_index: Current index of the item.
        to_index: Target index for the item.
    """
    entity_id: int
    entity_type: str
    from_index: int
    to_index: int

    def __init__(self, entity_id: int, entity_type: str, from_index: int, to_index: int):
        self.type = CommandType.ISSUE_ORDER
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.from_index = from_index
        self.to_index = to_index
