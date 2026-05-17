from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum, auto

from game.core.hex_math import HexCoord

class CommandType(Enum):
    ISSUE_ORDER = auto()
    # Add other types as needed (e.g., GAME_SETTINGS, CHEAT_CODE)


class TransferDirection(str, Enum):
    """Direction of cargo transfer between fleet and target."""
    LOAD = "load"
    UNLOAD = "unload"


class BuildEntityType(str, Enum):
    """Entity type for construction queue commands."""
    PLANET = "planet"
    FLEET = "fleet"

@dataclass
class Command:
    """Base class for all game commands.

    BUG-125: commands do NOT carry an empire identifier. Identity is
    session context — handlers gate on ``session.active_empire.id``. The
    UI must never supply identity through a request body; doing so was
    the root cause of the original cross-empire-orders bug (UI passed
    ``empire_id=fleet.owner_id``; handler checked ``cmd.empire_id ==
    fleet.owner_id``, a tautology that authorized any selectable fleet).
    """
    type: CommandType = field(init=False)

    def __post_init__(self):
        self.type = CommandType.ISSUE_ORDER

    @property
    def name(self) -> str:
        return self.__class__.__name__

@dataclass
class IssueColonizeCommand(Command):
    """Command to issue a colonization order to a fleet."""
    fleet_id: int
    planet_id: Optional[int] = None  # None for 'Any Planet'
    population_amount: Optional[int] = None  # None = all passengers
    cargo_amounts: Optional[Dict[str, int]] = None  # None = all cargo

@dataclass
class IssueMoveCommand(Command):
    """Command to move a fleet to a target hex."""
    fleet_id: int
    target_hex: HexCoord

# NOTE: IssueBuildShipCommand removed in PROJ-208 Phase 2 (dead code).
# Use AddToConstructionQueueCommand instead for all build queue operations.


@dataclass
class IssueInterceptCommand(Command):
    """Command to issue an intercept order to a fleet.

    The fleet will move toward the target fleet's position.
    """
    fleet_id: int
    target_fleet_id: int


@dataclass
class IssueJoinFleetCommand(Command):
    """Command to issue a join fleet order.

    The fleet will move to and merge with the target fleet.
    """
    fleet_id: int
    target_fleet_id: int


@dataclass
class QueueColonizeMissionCommand(Command):
    """Command to queue a colonize mission (move + colonize).

    The fleet will move to the target hex and then colonize the planet.
    If planet_id is None, the fleet will colonize the largest available
    planet when it arrives at the target hex.
    """
    fleet_id: int
    target_hex: HexCoord
    planet_id: Optional[int] = None  # None for 'colonize any/largest available planet'
    population_amount: Optional[int] = None  # None = all passengers
    cargo_amounts: Optional[Dict[str, int]] = None  # None = all cargo


@dataclass
class ClearOrdersCommand(Command):
    """Command to clear all orders from a fleet.

    Strictly handles the fleet path. The planet path has its own
    dedicated command, ``ClearPlanetOrdersCommand`` (see
    ``orders_window_ctrl.py``), so no entity_type discriminator is
    needed here. The forward-dead ``entity_type: str = "fleet"`` field
    was removed by PROJ-397 (review F-04) — no handler ever read it.
    """
    fleet_id: int


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
    planet_id: Optional[int] = None
    cargo_type: str = "passengers"
    direction: TransferDirection = TransferDirection.LOAD
    amount: int = 0
    species_id: Optional[str] = None
    target_fleet_id: Optional[int] = None


# =============================================================================
# Superweapon Commands (PROJ-102)
# =============================================================================

@dataclass
class IssueImplodePlanetCommand(Command):
    """Command to issue an IMPLODE_PLANET order to destroy a planet."""
    fleet_id: int
    planet_id: int


@dataclass
class IssueStellerateStarCommand(Command):
    """Command to issue a STELLERATE_STAR order to destroy the star at fleet location."""
    fleet_id: int


@dataclass
class IssueOpenWarpPointCommand(Command):
    """Command to issue an OPEN_WARP_POINT order to create a warp link."""
    fleet_id: int
    target_hex: HexCoord
    target_system_name: str


@dataclass
class IssueCloseWarpPointCommand(Command):
    """Command to issue a CLOSE_WARP_POINT order to destroy a warp link."""
    fleet_id: int
    warp_point_destination_id: str


@dataclass
class IssueCreateDysonSphereCommand(Command):
    """Command to issue a CREATE_DYSON_SPHERE order to create a Dyson Sphere."""
    fleet_id: int


@dataclass
class IssueSelfDestructCommand(Command):
    """Command to issue a SELF_DESTRUCT order to destroy selected ships."""
    fleet_id: int
    ship_ids: List[int]


# =============================================================================
# Superweapon Mission Commands (Move + Action) (PROJ-102)
# =============================================================================

@dataclass
class QueueImplodePlanetMissionCommand(Command):
    """Command to queue a move-to-hex then implode planet mission."""
    fleet_id: int
    target_hex: HexCoord
    planet_id: int


@dataclass
class QueueStellerateStarMissionCommand(Command):
    """Command to queue a move-to-hex then stellerate star mission."""
    fleet_id: int
    target_hex: HexCoord


@dataclass
class QueueOpenWarpPointMissionCommand(Command):
    """Command to queue a move-to-hex then open warp point mission."""
    fleet_id: int
    target_hex: HexCoord
    target_system_name: str


@dataclass
class QueueCloseWarpPointMissionCommand(Command):
    """Command to queue a move-to-hex then close warp point mission."""
    fleet_id: int
    target_hex: HexCoord
    warp_point_destination_id: str


@dataclass
class QueueCreateDysonSphereMissionCommand(Command):
    """Command to queue a move-to-hex then create Dyson Sphere mission."""
    fleet_id: int
    target_hex: HexCoord


# =============================================================================
# WARP Commands (PROJ-187)
# =============================================================================

@dataclass
class IssueLaunchFightersCommand(Command):
    """PROJ-FMS-C Phase 1 + QA Observation B: launch fighters from a
    fleet ship OR a planetary-complex facility.

    Invariant: exactly one of ``fleet_id`` / ``planet_id`` must be set.
    Fleet-issued launches require ``ship_instance_id`` (the carrier);
    planet-issued launches operate on the planet's staging yard and
    leave ``ship_instance_id`` unset.

    Args:
        fleet_id: Source fleet containing the carrier ship (mutually
            exclusive with ``planet_id``).
        ship_instance_id: The carrier ship within the fleet that holds the
            fighters. Required for fleet-issued, unused for planet-issued.
        fighter_design_id: Specific fighter design to launch. Use "auto" or
            an empty string to take any fighter from the bay.
        count: Number of fighters of that design to launch. ``None``
            launches all matching fighters.
        target_hex: Optional target hex. ``None`` => current issuer hex.
        planet_id: Source planet (mutually exclusive with ``fleet_id``);
            launches from the planet's staging yard.
    """

    fleet_id: Optional[int] = None
    ship_instance_id: Optional[str] = None
    fighter_design_id: str = "auto"
    count: Optional[int] = None
    target_hex: Optional[HexCoord] = None
    planet_id: Optional[int] = None


@dataclass
class IssueRecoverFightersCommand(Command):
    """PROJ-FMS-C Phase 3 + QA Observation B: recover fighters into a
    fleet ship's bay OR a planet's staging yard.

    Invariant: exactly one of ``fleet_id`` / ``planet_id`` must be set.

    Args:
        fleet_id: Recovering fleet containing the carrier ship (mutually
            exclusive with ``planet_id``).
        ship_instance_id: The carrier ship that will receive the
            fighters. Required for fleet-issued, unused for planet-issued.
        fighter_group_id: Specific fighter_group fleet id to recover from.
            ``None`` => the first fighter_group at the issuer's hex owned
            by the same empire.
        count: Number of fighters to recover. ``None`` => recover all
            available (capped by bay/staging capacity).
        planet_id: Recovering planet (mutually exclusive with
            ``fleet_id``); fighters land in the planet's staging yard.
    """

    fleet_id: Optional[int] = None
    ship_instance_id: Optional[str] = None
    fighter_group_id: Optional[int] = None
    count: Optional[int] = None
    planet_id: Optional[int] = None


@dataclass
class IssueLaunchSatellitesCommand(Command):
    """PROJ-FMS-D Phase 1 + QA Observation B: launch satellites from a
    fleet ship OR a planetary-complex facility.

    Invariant: exactly one of ``fleet_id`` / ``planet_id`` must be set.

    Args:
        fleet_id: Source fleet containing the carrier ship (mutually
            exclusive with ``planet_id``).
        ship_instance_id: The carrier ship within the fleet that holds the
            satellites. Required for fleet-issued, unused for planet-issued.
        satellite_design_id: Specific satellite design to launch. Use
            "auto" or an empty string to take any satellite from the bay.
        count: Number of satellites of that design to launch. ``None``
            launches all matching satellites.
        target_hex: Optional target hex. ``None`` => current issuer hex.
        planet_id: Source planet (mutually exclusive with ``fleet_id``);
            launches from the planet's staging yard.
    """

    fleet_id: Optional[int] = None
    ship_instance_id: Optional[str] = None
    satellite_design_id: str = "auto"
    count: Optional[int] = None
    target_hex: Optional[HexCoord] = None
    planet_id: Optional[int] = None


@dataclass
class IssueRecoverSatellitesCommand(Command):
    """PROJ-FMS-D Phase 2 + QA Observation B: recover satellites into a
    fleet ship's bay OR a planet's staging yard.

    Invariant: exactly one of ``fleet_id`` / ``planet_id`` must be set.

    Args:
        fleet_id: Recovering fleet containing the carrier ship (mutually
            exclusive with ``planet_id``).
        ship_instance_id: The carrier ship that will receive the
            satellites. Required for fleet-issued, unused for planet-issued.
        satellite_group_id: Specific ``satellite_group`` fleet id to
            recover from. ``None`` => the first satellite_group at the
            issuer's hex owned by the same empire.
        count: Number of satellites to recover. ``None`` => recover all
            available (capped by bay/staging capacity).
        planet_id: Recovering planet (mutually exclusive with
            ``fleet_id``); satellites land in the planet's staging yard.
    """

    fleet_id: Optional[int] = None
    ship_instance_id: Optional[str] = None
    satellite_group_id: Optional[int] = None
    count: Optional[int] = None
    planet_id: Optional[int] = None


@dataclass
class IssueLayMinesCommand(Command):
    """PROJ-FMS-B Phase 1 + QA Observation B: lay mines from a fleet
    ship OR a planetary-complex facility.

    Invariant: exactly one of ``fleet_id`` / ``planet_id`` must be set.

    Args:
        fleet_id: Source fleet containing the carrier ship (mutually
            exclusive with ``planet_id``).
        ship_instance_id: The carrier ship within the fleet that holds
            the mines. Required for fleet-issued, unused for planet-issued.
        mine_design_id: Specific mine design to lay.
        count: Number of mines of that design to lay. ``None`` lays all
            matching mines.
        target_hex: Optional target hex. ``None`` => current issuer hex.
        planet_id: Source planet (mutually exclusive with ``fleet_id``);
            lays mines from the planet's staging yard.
    """

    fleet_id: Optional[int] = None
    ship_instance_id: Optional[str] = None
    mine_design_id: str = ""
    count: Optional[int] = None
    target_hex: Optional[HexCoord] = None
    planet_id: Optional[int] = None


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


@dataclass
class RemoveBuildOrderCommand(Command):
    """Command to remove BUILD orders from a fleet.

    PROJ-207 Phase 4: Used when construction queue is emptied.
    """
    fleet_id: int


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


@dataclass
class DeleteOrderCommand(Command):
    """Command to remove a specific order from a fleet's order queue.

    Strictly handles the fleet path. The planet path has its own
    dedicated command, ``DeletePlanetOrderCommand``. The forward-dead
    ``entity_type: str = "fleet"`` field was removed by PROJ-397
    (review F-04).
    """
    fleet_id: int
    order_index: int


@dataclass
class ReorderOrderCommand(Command):
    """Command to move a fleet order up or down in the queue.

    Strictly handles the fleet path (no equivalent planet command
    exists yet — see ``orders_window_ctrl.py:reorder_order_callback``
    planet branch which is currently a no-op). The forward-dead
    ``entity_type: str = "fleet"`` field was removed by PROJ-397
    (review F-04).
    """
    fleet_id: int
    order_index: int
    direction: int


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
        queue_id: Optional queue identifier for multi-queue entities (e.g., shipyard facility ID).
    """
    entity_id: int
    entity_type: BuildEntityType
    design_id: str
    category: str
    index: Optional[int] = None
    target_planet_id: Optional[int] = None
    queue_id: Optional[str] = None


@dataclass
class RemoveFromConstructionQueueCommand(Command):
    """Command to remove an item from a construction queue.

    PROJ-208 Phase 2: Routes construction queue removals through command pipeline.
    BUG-103: Added queue_id for multi-queue entities (facility queues).

    Args:
        entity_id: Planet or fleet ID.
        entity_type: "planet" or "fleet".
        item_index: Index of the item to remove.
        queue_id: Optional queue identifier for multi-queue entities (e.g., shipyard facility ID).
    """
    entity_id: int
    entity_type: BuildEntityType
    item_index: int
    queue_id: Optional[str] = None


@dataclass
class ReorderConstructionQueueCommand(Command):
    """Command to move a construction queue item to a new position.

    PROJ-208 Phase 2: Routes construction queue reordering through command pipeline.
    BUG-103: Added queue_id for multi-queue entities (facility queues).

    Args:
        entity_id: Planet or fleet ID.
        entity_type: "planet" or "fleet".
        from_index: Current index of the item.
        to_index: Target index for the item.
        queue_id: Optional queue identifier for multi-queue entities (e.g., shipyard facility ID).
    """
    entity_id: int
    entity_type: BuildEntityType
    from_index: int
    to_index: int
    queue_id: Optional[str] = None


@dataclass
class SetBuildQueuePausedCommand(Command):
    """Pause or unpause a construction queue (FEAT-17).

    Targets the same three queue locations as the other construction-queue
    commands: a planet's base queue, a planet shipyard facility queue, or a
    fleet space-yard queue. While paused, ProductionEngine skips ticking
    that queue — no resource draw, no progress increment. The queue list
    itself remains intact so add/remove/reorder still work.

    Args:
        entity_id: Planet or fleet ID.
        entity_type: "planet" or "fleet".
        paused: True to pause, False to resume.
        queue_id: Optional queue identifier for multi-queue entities. None
            (or the planet's base-queue id) targets the entity's main queue;
            a facility instance_id targets that facility's queue.
    """
    entity_id: int
    entity_type: BuildEntityType
    paused: bool
    queue_id: Optional[str] = None


# =============================================================================
# Planet Order Commands (PROJ-237)
# =============================================================================

@dataclass
class IssuePlanetOrderCommand(Command):
    """Command to issue an order to a planet (e.g., activate/deactivate ability).

    Args:
        planet_id: Planet to issue order to.
        order_type: OrderType name (e.g., "ACTIVATE_ABILITY").
        facility_instance_id: Target facility UUID.
        component_id: Optional specific component within facility (legacy).
        ability_name: Ability name for generic ACTIVATE_ABILITY/DEACTIVATE_ABILITY.
        component_key: Composite key (LAYER:INDEX:COMP_ID) targeting a specific component.
    """
    planet_id: int
    order_type: str
    facility_instance_id: str
    component_id: Optional[str] = None
    ability_name: Optional[str] = None
    component_key: Optional[str] = None


@dataclass
class ClearPlanetOrdersCommand(Command):
    """Command to clear all orders from a planet."""
    planet_id: int


@dataclass
class DeletePlanetOrderCommand(Command):
    """Command to remove a specific order from a planet's order queue."""
    planet_id: int
    order_index: int


@dataclass
class SetAtmosphereTargetCommand(Command):
    """Command to set or clear a planet's atmosphere modification target."""
    planet_id: int
    atmosphere_target: Dict[str, float]  # gas formula -> target Pa (empty dict = clear)


@dataclass
class SetGravityTargetCommand(Command):
    """Command to set or clear a planet's gravity modification target."""
    planet_id: int
    gravity_target: Optional[float]  # m/s², None = clear


@dataclass
class SetWaterTargetCommand(Command):
    """Command to set or clear a planet's water modification target."""
    planet_id: int
    water_target: Optional[float]  # 0.0-1.0, None = clear


@dataclass
class SetRadiationShieldTargetCommand(Command):
    """Command to set or clear a planet's radiation shielding target."""
    planet_id: int
    shielding_target: Optional[float]  # 0.0+, None = clear
