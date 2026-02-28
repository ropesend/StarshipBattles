"""Fleet Data Transfer Objects.

Immutable DTOs representing fleet data for the UI layer.
"""
from dataclasses import dataclass, field
from typing import Tuple, Optional, TYPE_CHECKING

from game.core.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet as FleetType

from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet


@dataclass(frozen=True)
class FleetOrderInfo:
    """Immutable DTO representing a fleet order.

    Attributes:
        order_type: Type of order ("MOVE", "COLONIZE", "MOVE_TO_FLEET", "JOIN_FLEET")
        target_description: Human-readable description of the target
        target_hex: Target hex coordinate for movement orders
        target_id: Target entity ID (fleet ID for JOIN_FLEET, planet ID for COLONIZE)
    """

    order_type: str
    target_description: str
    target_hex: Optional[HexCoord] = None
    target_id: Optional[int] = None


@dataclass(frozen=True)
class ShipInfo:
    """Immutable DTO representing a ship in a fleet.

    Attributes:
        instance_id: Unique identifier for this ship instance
        name: Display name of the ship
        design_id: Reference to the ship design
        ship_class: Ship class (e.g., "Frigate", "Cruiser")
        is_combat_capable: Whether the ship can participate in combat
        current_hp_percent: Current HP as percentage of max (0.0-1.0)
    """

    instance_id: str
    name: str
    design_id: str
    ship_class: str
    is_combat_capable: bool
    current_hp_percent: float


@dataclass(frozen=True)
class FleetInfo:
    """Immutable DTO representing a fleet.

    Attributes:
        fleet_id: Unique identifier for the fleet
        owner_id: Empire ID of the fleet owner
        location: Current hex coordinate
        speed: Fleet movement speed
        ship_count: Number of ships in the fleet
        ships: Tuple of ShipInfo DTOs for each ship (immutable)
        orders: Tuple of FleetOrderInfo DTOs for queued orders (immutable)
        has_orders: Whether the fleet has any orders queued
        can_use_warp: Whether all ships in fleet can use warp points
        projected_path: Tuple of movement path coordinates (immutable)
        is_building: Whether the fleet is currently executing a BUILD order
        has_space_shipyard: Whether the fleet has an operational space shipyard
        construction_queue_size: Number of items in the fleet's construction queue
        passenger_capacity: Total passenger cargo capacity across all ships
        passengers_current: Current number of passengers loaded
        capabilities: Tuple of ability names available in this fleet (immutable)
    """

    fleet_id: int
    owner_id: int
    location: HexCoord
    speed: float
    ship_count: int
    ships: Tuple[ShipInfo, ...] = field(default_factory=tuple)
    orders: Tuple[FleetOrderInfo, ...] = field(default_factory=tuple)
    has_orders: bool = False
    can_use_warp: bool = False
    projected_path: Tuple[HexCoord, ...] = field(default_factory=tuple)
    is_building: bool = False
    has_space_shipyard: bool = False
    construction_queue_size: int = 0
    passenger_capacity: int = 0
    passengers_current: int = 0
    capabilities: Tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_fleet(cls, fleet: 'Fleet') -> 'FleetInfo':
        """Create a FleetInfo DTO from a Fleet domain object.

        Args:
            fleet: The Fleet domain object to convert

        Returns:
            An immutable FleetInfo DTO
        """
        # Convert ships to ShipInfo DTOs
        ship_infos = []
        for ship in fleet.ships:
            hp_percent = ship.get_hp_percentage()
            ship_class = ship.design_data.get("ship_class", "Unknown")
            ship_infos.append(
                ShipInfo(
                    instance_id=ship.instance_id,
                    name=ship.name,
                    design_id=ship.design_id,
                    ship_class=ship_class,
                    is_combat_capable=ship.is_combat_capable(),
                    current_hp_percent=hp_percent,
                )
            )

        # Convert orders to FleetOrderInfo DTOs
        order_infos = []
        for order in fleet.orders:
            target_hex = None
            target_id = None
            target_description = ""

            if order.type.name in ("MOVE", "COLONIZE"):
                # Target is a HexCoord or Planet
                if isinstance(order.target, HexCoord):
                    target_hex = order.target
                    target_description = f"({order.target.q}, {order.target.r})"
                elif isinstance(order.target, Planet):
                    # Planet target - has name and location
                    target_description = order.target.name
                    target_hex = order.target.location
            elif order.type.name in ("MOVE_TO_FLEET", "JOIN_FLEET"):
                # Target is a Fleet
                if isinstance(order.target, Fleet):
                    target_id = order.target.id
                    target_description = f"Fleet {order.target.id}"
            elif order.type.name == "BUILD":
                # BUILD order - fleet is constructing
                target_description = f"Building ({len(fleet.construction_queue)} items)"
            elif order.type.name == "TRANSFER":
                # TRANSFER order - loading/unloading cargo
                if isinstance(order.target, dict):
                    direction = order.target.get('direction', '?')
                    cargo_type = order.target.get('cargo_type', '?')
                    amount = order.target.get('amount', '?')
                    dir_str = "Load" if direction == "load" else "Unload"
                    target_description = f"{dir_str} {amount} {cargo_type}"
                else:
                    target_description = "Transfer"

            order_infos.append(
                FleetOrderInfo(
                    order_type=order.type.name,
                    target_description=target_description,
                    target_hex=target_hex,
                    target_id=target_id,
                )
            )

        # Get fleet capabilities (ability names)
        try:
            capabilities = tuple(fleet.capabilities.list_abilities())
        except (ValueError, AttributeError):
            # No registry available or no ships - empty capabilities
            capabilities = ()

        return cls(
            fleet_id=fleet.id,
            owner_id=fleet.owner_id,
            location=fleet.location,
            speed=fleet.speed,
            ship_count=len(fleet.ships),
            ships=tuple(ship_infos),
            orders=tuple(order_infos),
            has_orders=len(fleet.orders) > 0,
            can_use_warp=fleet.capabilities.can_use_warp(),
            projected_path=tuple(fleet.path),
            is_building=fleet.is_building,
            has_space_shipyard=fleet.capabilities.has_space_shipyard,
            construction_queue_size=len(fleet.construction_queue),
            passenger_capacity=fleet.resources.get_fleet_cargo_capacity('passengers'),
            passengers_current=fleet.resources.get_fleet_cargo_current('passengers'),
            capabilities=capabilities,
        )
