"""
Fleet data class.

FleetOrderSerializer extracted to fleet_order_serializer.py (PROJ-210).
"""

import logging
from typing import List, Optional, Tuple, TYPE_CHECKING, Any, Dict

from game.core.hex_math import HexCoord
from game.core.protocols import IPostBattleShip
from game.core.validation_helpers import require_keys
from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
from game.strategy.data.ship_instance import ShipInstance

# PROJ-212: OrderType, FleetOrder, and order type sets extracted to order_types.py
from game.strategy.data.order_types import (
    OrderType,
    FleetOrder,
    MOVEMENT_ORDER_TYPES,
    ACTION_ORDER_TYPES,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.planet import Planet


class Fleet:
    """
    Represents a fleet of ships on the Strategy Map.

    Ships are stored as ShipInstance objects with full state tracking.
    """

    def __init__(
        self,
        fleet_id,
        owner_id,
        location,
        speed=5.0,
        component_registry: Optional[Dict[str, Any]] = None
    ):
        self.id = fleet_id
        self.owner_id = owner_id  # 0=Player, 1=Enemy, etc
        self.location = location  # HexCoord
        self.ships: List[ShipInstance] = []
        self._component_registry = component_registry

        # Movement & Orders
        self.speed = float(speed)
        self.orders: List[FleetOrder] = []
        self.path: List[HexCoord] = []  # Current movement path for the ACTIVE Move order

        # Production (for fleets with space yards)
        self.construction_queue: List[Dict[str, Any]] = []

        # Delegate for resource aggregation (PROJ-87 Phase 3)
        self._resource_agg = FleetResourceAggregator(self)

        # Delegate for capability queries (PROJ-87 Phase 4)
        # PROJ-211: Pass component_registry for DI
        self._capabilities = FleetCapabilityCalculator(self, component_registry)

        # Delegate for battle conversion (PROJ-87 Phase 4)
        self._battle = FleetBattleAdapter(self)

    @property
    def name(self) -> str:
        """
        Display name for the fleet.

        Returns a descriptive name based on fleet composition.
        """
        ship_count = len(self.ships)
        if ship_count == 0:
            return f"Empty Fleet {self.id}"
        elif ship_count == 1:
            return f"Fleet {self.id}: {self.ships[0].name}"
        else:
            return f"Fleet {self.id} ({ship_count} ships)"

    @property
    def context_type(self) -> str:
        """Return 'fleet' for BuildContext protocol compliance."""
        return "fleet"

    def add_ship(self, ship: ShipInstance):
        """Add a ShipInstance to the fleet."""
        self.ships.append(ship)
        self.trigger_speed_recalculation()

    def remove_ship(self, ship: ShipInstance) -> bool:
        """Remove a ship from the fleet. Returns True if found and removed."""
        if ship in self.ships:
            self.ships.remove(ship)
            self.trigger_speed_recalculation()
            return True
        return False

    def trigger_speed_recalculation(self) -> None:
        """
        Trigger fleet speed recalculation based on current ship composition.

        Fleet speed is the minimum of all combat-capable ships' speeds,
        ensuring the fleet moves at the pace of its slowest member.

        This is a public method because external delegates (FleetBattleAdapter)
        need to trigger recalculation after modifying the ship roster.
        """
        # INTENTIONAL LATE IMPORT: Edge operation (only on ship add/remove)
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
        FleetSpeedCalculator.update_fleet_speed(self)

    def get_ship_names(self) -> List[str]:
        """Get names of all ships in the fleet."""
        return [s.name for s in self.ships]

    def get_combat_capable_ships(self) -> List[ShipInstance]:
        """Get ships capable of combat (not destroyed or derelict)."""
        return [s for s in self.ships if s.is_combat_capable()]

    @property
    def capabilities(self) -> 'FleetCapabilityCalculator':
        """Public access to fleet capability queries."""
        return self._capabilities

    @property
    def resources(self) -> 'FleetResourceAggregator':
        """Public access to fleet resource aggregation."""
        return self._resource_agg

    @property
    def battle(self) -> 'FleetBattleAdapter':
        """Public access to fleet battle conversion."""
        return self._battle

    @property
    def is_building(self) -> bool:
        """
        Check if fleet is currently executing a BUILD order.

        Returns True when the current (first) order is BUILD.
        """
        current = self.get_current_order()
        return current is not None and current.type == OrderType.BUILD

    # NOTE: PROJ-210 Phase 2 removed pass-through methods.
    # Use fleet.capabilities.*, fleet.resources.*, fleet.battle.* directly.

    def add_order(self, order: FleetOrder, index: Optional[int] = None) -> None:
        """Add an order to the queue."""
        if index is None:
            self.orders.append(order)
        else:
            self.orders.insert(index, order)

    def clear_orders(self) -> None:
        """Clear all orders and the current path."""
        self.orders.clear()
        self.path = []

    def get_current_order(self) -> Optional[FleetOrder]:
        """Get the current (first) order, or None if queue is empty."""
        if not self.orders:
            return None
        return self.orders[0]

    def pop_order(self) -> Optional[FleetOrder]:
        """Remove and return the current order, or None if queue is empty."""
        if self.orders:
            finished = self.orders.pop(0)
            self.path = []  # Clear path associated with that order
            return finished
        return None

    def merge_with(self, other_fleet: 'Fleet') -> None:
        """
        Merge this fleet into other_fleet.
        Transfers all ships and clears this fleet.
        """
        if not isinstance(other_fleet, Fleet):
            return

        # Transfer ships
        other_fleet.ships.extend(self.ships)
        self.ships.clear()

        # Clear orders (this fleet is effectively gone)
        self.clear_orders()

        # Recalculate speed for the target fleet (new composition)
        other_fleet.trigger_speed_recalculation()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        ships_data = [s.to_dict() for s in self.ships]

        location_data = None
        if isinstance(self.location, HexCoord):
            location_data = {'q': self.location.q, 'r': self.location.r}
        elif isinstance(self.location, tuple):
            location_data = list(self.location)

        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'location': location_data,
            'speed': self.speed,
            'ships': ships_data,
            'orders': [o.to_dict() for o in self.orders],
            'path': [{'q': p.q, 'r': p.r} if isinstance(p, HexCoord) else list(p) if isinstance(p, tuple) else p for p in self.path],
            'construction_queue': self.construction_queue,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None
    ) -> 'Fleet':
        """
        Deserialize from save game.

        Args:
            data: Dict with fleet data
            registries: Optional GameRegistries for DI. If provided, ships
                and FleetCapabilityCalculator will use these registries.

        Returns:
            Reconstructed Fleet

        Raises:
            PersistenceException: If required keys missing
        """
        # PROJ-210: Order deserialization delegated to FleetOrderSerializer
        from game.strategy.data.fleet_order_serializer import FleetOrderSerializer

        require_keys(data, ['id', 'owner_id'], 'Fleet')

        location = data.get('location')
        if isinstance(location, dict) and 'q' in location and 'r' in location:
            location = HexCoord(location['q'], location['r'])
        elif isinstance(location, list):
            location = HexCoord(location[0], location[1])

        # PROJ-211: Extract component_registry from registries for DI
        component_registry = registries.components if registries else None

        fleet = cls(
            fleet_id=data['id'],
            owner_id=data['owner_id'],
            location=location,
            speed=data.get('speed', 5.0),
            component_registry=component_registry,
        )

        # Restore ships (skip corrupt entries with warning)
        for i, ship_data in enumerate(data.get('ships', [])):
            try:
                ship = ShipInstance.from_dict(ship_data, registries=registries)
                fleet.ships.append(ship)
            except Exception as e:
                logger.warning(f"Fleet {data['id']}: skipping corrupt ship[{i}]: {e}")

        # Restore path
        for p in data.get('path', []):
            if isinstance(p, dict) and 'q' in p and 'r' in p:
                fleet.path.append(HexCoord(p['q'], p['r']))
            elif isinstance(p, list):
                fleet.path.append(HexCoord(p[0], p[1]))
            else:
                fleet.path.append(p)

        # PROJ-210: Restore orders using serializer
        fleet.orders = FleetOrderSerializer.deserialize_orders(
            data.get('orders', []),
            data['id']
        )

        # Restore construction queue
        fleet.construction_queue = data.get('construction_queue', [])

        return fleet

    def resolve_order_references(self, galaxy: Any, empires: List[Any]) -> None:
        """
        Resolve order target references after deserialization.

        During from_dict(), order targets that reference Fleets or Planets are stored
        as marker dicts (_fleet_ref, _planet_ref). This method resolves those markers
        to actual object references.

        Orders with unresolvable references (deleted fleets/planets) are removed
        with a warning.

        Args:
            galaxy: Galaxy object with get_planet_by_id() method
            empires: List of Empire objects containing all fleets
        """
        # PROJ-210: Delegate to FleetOrderSerializer
        from game.strategy.data.fleet_order_serializer import FleetOrderSerializer
        FleetOrderSerializer.resolve_order_references(self, galaxy, empires)

    def __repr__(self):
        ship_count = len(self.ships)
        return f"Fleet({self.id}, Owner:{self.owner_id}, Loc:{self.location}, Ships:{ship_count}, Spd:{self.speed})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fleet):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
