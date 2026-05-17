"""Fleet Data Transfer Objects.

Immutable DTOs representing fleet data for the UI layer.
"""
from dataclasses import dataclass, field
from typing import Tuple, Optional

from game.core.hex_math import HexCoord

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
    name: str
    composition_summary: str
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
    # Cargo resource amounts and capacities (all resource types)
    cargo_resources: Tuple[Tuple[str, int], ...] = field(default_factory=tuple)
    cargo_capacities: Tuple[Tuple[str, int], ...] = field(default_factory=tuple)
    # Carried items summary: tuple of (name, vehicle_type, mass, count)
    carried_items_summary: Tuple[Tuple[str, str, float, int], ...] = field(default_factory=tuple)
    # PROJ-FMS-A Phase 3: per-vehicle-type count breakdown of carried items.
    # Tuple of (vehicle_type, count). Only counts entries whose
    # ``vehicle_type`` is one of {"mine", "fighter", "satellite"}.
    carried_vehicles_by_type: Tuple[Tuple[str, int], ...] = field(default_factory=tuple)
    # Pod storage capacity and usage
    pod_storage_capacity: float = 0.0
    pod_storage_used: float = 0.0
    # PROJ-FMS-A Phase 3: vehicle-bay capacity (current/max mass) across
    # all combat-capable ships in this fleet.
    vehicle_bay_capacity_used: float = 0.0
    vehicle_bay_capacity_max: float = 0.0
    # PROJ-431 Phase 3 (2026-05-17): ``group_kind`` deleted. Every
    # FleetInfo describes a real Fleet — deployed mines / fighters /
    # satellites flow through their own DTO surfaces.

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
                # Target is a HexCoord, Planet, or dict with planet
                if isinstance(order.target, HexCoord):
                    target_hex = order.target
                    target_description = f"({order.target.q}, {order.target.r})"
                elif isinstance(order.target, dict) and 'planet' in order.target:
                    # Dict target with population/cargo amounts
                    planet_obj = order.target['planet']
                    if planet_obj:
                        target_description = planet_obj.name
                        target_hex = planet_obj.location
                    else:
                        target_description = "Any Planet"
                elif isinstance(order.target, Planet):
                    # Planet target - has name and location
                    target_description = order.target.name
                    target_hex = order.target.location
            elif order.type.name in ("MOVE_TO_FLEET", "JOIN_FLEET"):
                # Target is a Fleet
                if isinstance(order.target, Fleet):
                    target_id = order.target.id
                    target_description = order.target.name
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
            name=fleet.name,
            composition_summary=fleet.composition_summary,
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
            cargo_resources=tuple(
                (res, fleet.resources.get_fleet_cargo_current(res))
                for res in ("metals", "organics", "vapors", "radioactives", "exotics",
                            "fuel", "energy", "ammo")
            ),
            cargo_capacities=tuple(
                (res, fleet.resources.get_fleet_cargo_capacity(res))
                for res in ("metals", "organics", "vapors", "radioactives", "exotics",
                            "fuel", "energy", "ammo")
            ),
            carried_items_summary=cls._aggregate_carried_items(fleet),
            carried_vehicles_by_type=cls._aggregate_carried_vehicles_by_type(fleet),
            pod_storage_capacity=fleet.resources.get_fleet_pod_capacity(),
            pod_storage_used=fleet.resources.get_fleet_pod_mass_used(),
            vehicle_bay_capacity_used=cls._sum_vehicle_bay_used(fleet),
            vehicle_bay_capacity_max=cls._sum_vehicle_bay_max(fleet),
        )

    @staticmethod
    def _aggregate_carried_vehicles_by_type(
        fleet: 'Fleet',
    ) -> Tuple[Tuple[str, int], ...]:
        """PROJ-FMS-A Phase 3: per-type count of CarriedVehicle entries.

        PROJ-431 Phase 1e: reads through ``ship.bay_inventory.bay`` —
        the homogeneous typed slot for design-backed carried vehicles.
        Drop pods live in ``bay_inventory.pods`` and are not counted
        here.
        """
        types = ("mine", "fighter", "satellite")
        counts: dict = {t: 0 for t in types}
        for ship in fleet.ships:
            inventory = getattr(ship, 'bay_inventory', None)
            if inventory is None:
                continue
            for cv in getattr(inventory, 'bay', ()) or ():
                vt = str(getattr(cv, 'vehicle_type', 'unknown')).lower()
                if vt in counts:
                    counts[vt] += 1
        return tuple((vt, counts[vt]) for vt in types if counts[vt] > 0)

    @staticmethod
    def _sum_vehicle_bay_used(fleet: 'Fleet') -> float:
        total = 0.0
        for ship in fleet.ships:
            cargo_mgr = getattr(ship, "_cargo_mgr", None)
            if cargo_mgr is None or not hasattr(cargo_mgr, "get_vehicle_bay_capacity"):
                continue
            try:
                used, _max = cargo_mgr.get_vehicle_bay_capacity()
            except Exception:  # Intentional broad catch: mock fleets in tests return non-tuple values; treat as zero.
                continue
            total += used
        return total

    @staticmethod
    def _sum_vehicle_bay_max(fleet: 'Fleet') -> float:
        total = 0.0
        for ship in fleet.ships:
            cargo_mgr = getattr(ship, "_cargo_mgr", None)
            if cargo_mgr is None or not hasattr(cargo_mgr, "get_vehicle_bay_capacity"):
                continue
            try:
                _used, max_mass = cargo_mgr.get_vehicle_bay_capacity()
            except Exception:  # Intentional broad catch: same as above; treat unreadable bays as zero.
                continue
            total += max_mass
        return total

    @staticmethod
    def _aggregate_carried_items(fleet: 'Fleet') -> Tuple[Tuple[str, str, float, int], ...]:
        """Aggregate carried items across all ships by (name, vehicle_type, mass).

        PROJ-431 Phase 1e: reads through the typed ``bay_inventory``
        substrate. Design-backed carried vehicles come from
        ``bay_inventory.bay`` (their ``name`` lives in
        ``design_data['name']``); drop pods come from
        ``bay_inventory.pods`` (their ``name`` / ``vehicle_type`` were
        tucked into ``payload`` by the legacy projection — falling back
        to ``'Unknown'`` / ``'unknown'``).
        """
        counts: dict = {}
        for ship in fleet.ships:
            inventory = getattr(ship, 'bay_inventory', None)
            if inventory is None:
                continue
            for cv in getattr(inventory, 'bay', ()) or ():
                design_data = getattr(cv, 'design_data', None) or {}
                name = design_data.get('name', 'Unknown')
                vtype = str(getattr(cv, 'vehicle_type', 'unknown'))
                mass = float(getattr(cv, 'mass', 0.0) or 0.0)
                key = (name, vtype, mass)
                counts[key] = counts.get(key, 0) + 1
            for pod in getattr(inventory, 'pods', ()) or ():
                payload = getattr(pod, 'payload', None) or {}
                name = payload.get('name', 'Unknown')
                vtype = payload.get('vehicle_type', 'unknown')
                mass = float(getattr(pod, 'mass', 0.0) or 0.0)
                key = (name, vtype, mass)
                counts[key] = counts.get(key, 0) + 1
        return tuple(
            (name, vtype, mass, count)
            for (name, vtype, mass), count in counts.items()
        )
