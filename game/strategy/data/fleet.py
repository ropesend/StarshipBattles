import logging
from game.core.hex_math import HexCoord
from game.core.validation_helpers import require_keys, validate_enum
from game.strategy.data.ship_instance import ShipInstance

logger = logging.getLogger(__name__)
from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
from enum import Enum, auto
from typing import List, Optional, Tuple, TYPE_CHECKING, Any, Dict

from game.core.protocols import IPostBattleShip

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


class OrderType(Enum):
    MOVE = auto()
    COLONIZE = auto()
    MOVE_TO_FLEET = auto()
    JOIN_FLEET = auto()
    BUILD = auto()
    TRANSFER = auto()
    # Superweapon orders (PROJ-102)
    IMPLODE_PLANET = auto()
    STELLERATE_STAR = auto()
    OPEN_WARP_POINT = auto()
    CLOSE_WARP_POINT = auto()
    CREATE_DYSON_SPHERE = auto()
    SELF_DESTRUCT = auto()
    LOAD_POPULATION = auto()
    UNLOAD_POPULATION = auto()


class FleetOrder:
    def __init__(self, order_type, target=None):
        self.type = order_type
        self.target = target  # HexCoord for MOVE, Planet for COLONIZE, Fleet for MOVE_TO_FLEET/JOIN_FLEET

    def __repr__(self):
        return f"FleetOrder({self.type.name}, {self.target})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        target_data = None
        if self.target is not None:
            if self.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION):
                # TRANSFER and population orders store a dict with direction, cargo_type, amount, planet_id
                target_data = {'type': 'transfer', 'value': self.target}
            elif self.type == OrderType.IMPLODE_PLANET and hasattr(self.target, 'id'):
                # Planet reference for IMPLODE_PLANET (PROJ-102)
                target_data = {'type': 'planet_ref', 'id': self.target.id}
            elif self.type == OrderType.SELF_DESTRUCT and isinstance(self.target, list):
                # Ship ID list for SELF_DESTRUCT (PROJ-102)
                target_data = {'type': 'ship_id_list', 'value': self.target}
            elif self.type == OrderType.OPEN_WARP_POINT and isinstance(self.target, dict):
                # Warp parameters for OPEN_WARP_POINT (PROJ-102)
                target_data = {'type': 'warp_params', 'value': self.target}
            elif hasattr(self.target, 'to_dict'):
                target_data = self.target.to_dict()
            elif hasattr(self.target, 'id'):
                # Fleet reference - store ID
                target_data = {'type': 'fleet_ref', 'id': self.target.id}
            else:
                target_data = {'type': 'raw', 'value': str(self.target)}

        return {
            'type': self.type.name,
            'target': target_data,
        }


class Fleet:
    """
    Represents a fleet of ships on the Strategy Map.

    Ships are stored as ShipInstance objects with full state tracking.
    """

    def __init__(self, fleet_id, owner_id, location, speed=5.0):
        self.id = fleet_id
        self.owner_id = owner_id  # 0=Player, 1=Enemy, etc
        self.location = location  # HexCoord
        self.ships: List[ShipInstance] = []

        # Movement & Orders
        self.speed = float(speed)
        self.orders: List[FleetOrder] = []
        self.path: List[HexCoord] = []  # Current movement path for the ACTIVE Move order

        # Production (for fleets with space yards)
        self.construction_queue: List[Dict[str, Any]] = []

        # Delegate for resource aggregation (PROJ-87 Phase 3)
        self._resource_agg = FleetResourceAggregator(self)

        # Delegate for capability queries (PROJ-87 Phase 4)
        self._capabilities = FleetCapabilityCalculator(self)

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
    def has_space_shipyard(self) -> bool:
        """Check if fleet has an operational space shipyard."""
        return self._capabilities.has_space_shipyard

    @property
    def space_shipyard_count(self) -> int:
        """Count total fleet space yard components across all combat-capable ships."""
        return self._capabilities.space_shipyard_count

    @property
    def is_building(self) -> bool:
        """
        Check if fleet is currently executing a BUILD order.

        Returns True when the current (first) order is BUILD.
        """
        current = self.get_current_order()
        return current is not None and current.type == OrderType.BUILD

    def can_build_type(self, vehicle_type: str, galaxy: Any = None) -> bool:
        """Check if fleet can build the specified vehicle type."""
        return self._capabilities.can_build_type(vehicle_type, galaxy)

    def can_use_warp(self) -> bool:
        """Check if ALL ships in fleet can use warp points."""
        return self._capabilities.can_use_warp()

    def get_warp_limiting_ship(self) -> Optional[ShipInstance]:
        """Get the ship that prevents the fleet from using warp, if any."""
        return self._capabilities.get_warp_limiting_ship()

    # --- Generic Movement Resource Methods (delegated) ---

    def get_movement_resource_costs(self) -> Dict[str, float]:
        """Get total fleet resource costs per hex of movement."""
        return self._resource_agg.get_movement_resource_costs()

    def has_resources_for_movement(self) -> bool:
        """Check if fleet has resources for at least one hex of movement."""
        return self._resource_agg.has_resources_for_movement()

    def consume_movement_resources(self, hexes: int = 1) -> bool:
        """Consume all movement resources from all ships."""
        return self._resource_agg.consume_movement_resources(hexes)

    # --- Warp Resource Methods (delegated) ---

    def get_warp_resource_costs(self) -> Dict[str, float]:
        """Get total fleet resource costs for a warp jump."""
        return self._resource_agg.get_warp_resource_costs()

    def has_resources_for_warp(self) -> bool:
        """Check if fleet has all required resources for a warp jump."""
        return self._resource_agg.has_resources_for_warp()

    def consume_warp_resources(self) -> bool:
        """Consume all required resources from all ships for a warp jump."""
        return self._resource_agg.consume_warp_resources()

    # --- Capability Summary Methods (delegated) ---

    def fuel_endurance(self) -> int:
        """Calculate fleet fuel endurance in hexes."""
        return self._resource_agg.fuel_endurance()

    def warp_jumps_remaining(self) -> int:
        """Calculate how many warp jumps fleet can make."""
        return self._resource_agg.warp_jumps_remaining()

    def get_capability_summary(self) -> Dict[str, Any]:
        """Get comprehensive fleet capability summary for UI."""
        return self._resource_agg.get_capability_summary()

    # --- Cargo Methods (delegated) ---

    def get_fleet_cargo_capacity(self, cargo_type: str) -> int:
        """Get total fleet cargo capacity for a specific cargo type."""
        return self._resource_agg.get_fleet_cargo_capacity(cargo_type)

    def get_fleet_cargo_current(self, cargo_type: str) -> int:
        """Get total current cargo loaded in the fleet for a specific type."""
        return self._resource_agg.get_fleet_cargo_current(cargo_type)

    def load_cargo_to_fleet(self, cargo_type: str, amount: int) -> int:
        """Load cargo to the fleet, distributing across ships with capacity."""
        return self._resource_agg.load_cargo_to_fleet(cargo_type, amount)

    def unload_cargo_from_fleet(self, cargo_type: str, amount: int) -> int:
        """Unload cargo from the fleet, collecting from ships."""
        return self._resource_agg.unload_cargo_from_fleet(cargo_type, amount)

    def to_battle_ships(
        self,
        team_id: int,
        formation_positions: Optional[List[Tuple[float, float]]] = None,
        registries: Optional['GameRegistries'] = None
    ) -> List['Ship']:
        """Convert fleet ships to simulation Ship objects for battle."""
        return self._battle.to_battle_ships(team_id, formation_positions, registries)

    def _default_formation_positions(
        self,
        count: int,
        team_id: int
    ) -> List[Tuple[float, float]]:
        """Generate default formation positions for ships."""
        return self._battle._default_formation_positions(count, team_id)

    def update_from_battle_results(
        self,
        surviving_ships: List[IPostBattleShip],
    ) -> None:
        """Update fleet ships from battle results."""
        self._battle.update_from_battle_results(surviving_ships)

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
    def from_dict(cls, data: Dict[str, Any]) -> 'Fleet':
        """
        Deserialize from save game.

        Args:
            data: Dict with fleet data

        Returns:
            Reconstructed Fleet

        Raises:
            PersistenceException: If required keys missing
        """
        require_keys(data, ['id', 'owner_id'], 'Fleet')
        # ShipInstance imported at module level

        location = data.get('location')
        if isinstance(location, dict) and 'q' in location and 'r' in location:
            location = HexCoord(location['q'], location['r'])
        elif isinstance(location, list):
            location = HexCoord(location[0], location[1])

        fleet = cls(
            fleet_id=data['id'],
            owner_id=data['owner_id'],
            location=location,
            speed=data.get('speed', 5.0),
        )

        # Restore ships (skip corrupt entries with warning)
        for i, ship_data in enumerate(data.get('ships', [])):
            try:
                fleet.ships.append(ShipInstance.from_dict(ship_data))
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

        # Restore orders (skip corrupt entries with warning)
        # Note: Multiple target formats supported:
        # 1. {'q': x, 'r': y} - HexCoord.to_dict() format
        # 2. {'type': 'fleet_ref', 'id': xxx} - Fleet reference for MOVE_TO_FLEET orders
        # 3. {'type': 'raw', 'value': str} - Fallback string representation
        # 4. {'type': 'transfer', 'value': {...}} - TRANSFER order params (PROJ-68)
        # 5. {'type': 'planet_ref', 'id': xxx} - Planet reference (PROJ-102)
        # 6. {'type': 'ship_id_list', 'value': [...]} - Ship IDs (PROJ-102)
        # 7. {'type': 'warp_params', 'value': {...}} - Warp parameters (PROJ-102)
        for i, order_data in enumerate(data.get('orders', [])):
            try:
                order_type = validate_enum(order_data['type'], OrderType, 'type', f'Fleet order[{i}]')
                target = None

                target_data = order_data.get('target')
                if target_data is not None:
                    if isinstance(target_data, dict):
                        if 'q' in target_data and 'r' in target_data:
                            # HexCoord.to_dict() format
                            target = HexCoord(target_data['q'], target_data['r'])
                        elif target_data.get('type') == 'fleet_ref':
                            # Fleet reference - store ID for later resolution
                            target = {'_fleet_ref': target_data['id']}
                        elif target_data.get('type') == 'transfer':
                            # TRANSFER order params dict (PROJ-68)
                            target = target_data['value']
                        elif target_data.get('type') == 'planet_ref':
                            # Planet reference for IMPLODE_PLANET (PROJ-102)
                            target = {'_planet_ref': target_data['id']}
                        elif target_data.get('type') == 'ship_id_list':
                            # Ship ID list for SELF_DESTRUCT (PROJ-102)
                            target = target_data['value']
                        elif target_data.get('type') == 'warp_params':
                            # Warp parameters for OPEN_WARP_POINT (PROJ-102)
                            target = target_data['value']
                        elif target_data.get('type') == 'raw':
                            # Raw string fallback
                            target = target_data['value']

                fleet.orders.append(FleetOrder(order_type, target))
            except Exception as e:
                logger.warning(f"Fleet {data['id']}: skipping corrupt order[{i}]: {e}")

        # Restore construction queue
        fleet.construction_queue = data.get('construction_queue', [])

        return fleet

    def __repr__(self):
        ship_count = len(self.ships)
        return f"Fleet({self.id}, Owner:{self.owner_id}, Loc:{self.location}, Ships:{ship_count}, Spd:{self.speed})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fleet):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
