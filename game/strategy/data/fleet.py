from game.strategy.data.hex_math import HexCoord
from enum import Enum, auto
from typing import List, Union, Optional, Tuple, TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance
    from game.simulation.entities.ship import Ship


class OrderType(Enum):
    MOVE = auto()
    COLONIZE = auto()
    MOVE_TO_FLEET = auto()
    JOIN_FLEET = auto()


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
            if hasattr(self.target, 'to_dict'):
                target_data = self.target.to_dict()
            elif hasattr(self.target, 'id'):
                # Fleet reference - store ID
                target_data = {'type': 'fleet_ref', 'id': self.target.id}
            elif isinstance(self.target, tuple):
                target_data = {'type': 'coord', 'value': list(self.target)}
            else:
                target_data = {'type': 'raw', 'value': str(self.target)}

        return {
            'type': self.type.name,
            'target': target_data,
        }


class Fleet:
    """
    Represents a fleet of ships on the Strategy Map.

    Ships can be stored as:
    - Strings (legacy): Simple ship class names like "Scout", "Destroyer"
    - ShipInstance objects: Full ship instances with state tracking

    The fleet supports both formats for backward compatibility during migration.
    """

    def __init__(self, fleet_id, owner_id, location, speed=5.0):
        self.id = fleet_id
        self.owner_id = owner_id  # 0=Player, 1=Enemy, etc
        self.location = location  # HexCoord
        self.ships: List[Union[str, 'ShipInstance']] = []

        # Movement & Orders
        self.speed = float(speed)
        self.orders: List[FleetOrder] = []
        self.path: List[HexCoord] = []  # Current movement path for the ACTIVE Move order

    def add_ship(self, ship: Union[str, 'ShipInstance']):
        """Add a ship to the fleet (string name or ShipInstance)."""
        self.ships.append(ship)

    def add_ship_instance(self, instance: 'ShipInstance'):
        """Add a ShipInstance to the fleet."""
        self.ships.append(instance)

    def remove_ship(self, ship: Union[str, 'ShipInstance']) -> bool:
        """Remove a ship from the fleet. Returns True if found and removed."""
        if ship in self.ships:
            self.ships.remove(ship)
            return True
        return False

    def get_ship_instances(self) -> List['ShipInstance']:
        """Get all ShipInstance objects (filters out legacy strings)."""
        from game.strategy.data.ship_instance import ShipInstance
        return [s for s in self.ships if isinstance(s, ShipInstance)]

    def get_ship_names(self) -> List[str]:
        """Get all ship names (works with both strings and ShipInstances)."""
        result = []
        for s in self.ships:
            if isinstance(s, str):
                result.append(s)
            elif hasattr(s, 'name'):
                result.append(s.name)
        return result

    def get_combat_capable_ships(self) -> List['ShipInstance']:
        """Get ships capable of combat (not destroyed or derelict)."""
        from game.strategy.data.ship_instance import ShipInstance
        return [
            s for s in self.ships
            if isinstance(s, ShipInstance) and s.is_combat_capable()
        ]

    def has_ship_instances(self) -> bool:
        """Check if fleet contains any ShipInstance objects."""
        from game.strategy.data.ship_instance import ShipInstance
        return any(isinstance(s, ShipInstance) for s in self.ships)

    def to_battle_ships(
        self,
        team_id: int,
        formation_positions: Optional[List[Tuple[float, float]]] = None
    ) -> List['Ship']:
        """
        Convert fleet ships to simulation Ship objects for battle.

        Only works with ShipInstance objects - legacy strings cannot be converted.

        Args:
            team_id: Team assignment for battle (0 or 1)
            formation_positions: Optional list of (x, y) positions for ships

        Returns:
            List of Ship objects ready for battle
        """
        from game.strategy.data.ship_instance import ShipInstance

        ships = []
        instances = self.get_ship_instances()

        if not instances:
            return []

        # Generate default positions if not provided
        if formation_positions is None:
            formation_positions = self._default_formation_positions(len(instances), team_id)

        for i, instance in enumerate(instances):
            if not instance.is_combat_capable():
                continue

            pos = formation_positions[i] if i < len(formation_positions) else (0, 0)
            ship = instance.to_ship(pos, team_id)
            ships.append(ship)

        return ships

    def _default_formation_positions(
        self,
        count: int,
        team_id: int
    ) -> List[Tuple[float, float]]:
        """Generate default formation positions for ships."""
        positions = []

        # Team 0 starts on the left, Team 1 on the right
        base_x = 20000 if team_id == 0 else 80000
        base_y = 50000

        # Simple line formation
        spacing = 2000

        for i in range(count):
            y = base_y + (i - count // 2) * spacing
            positions.append((base_x, y))

        return positions

    def update_from_battle_results(
        self,
        surviving_ships: List['Ship'],
    ) -> None:
        """
        Update fleet ships from battle results.

        Args:
            surviving_ships: Ships that survived the battle
        """
        from game.strategy.data.ship_instance import ShipInstance

        # Build lookup for surviving ships by name
        survivors_by_name = {s.name: s for s in surviving_ships}

        # Update each ShipInstance
        new_ships = []
        for s in self.ships:
            if isinstance(s, ShipInstance):
                if s.name in survivors_by_name:
                    # Update state from battle
                    s.update_from_ship(survivors_by_name[s.name])
                    new_ships.append(s)
                # else: ship was destroyed, don't include
            else:
                # Legacy string - keep as is
                new_ships.append(s)

        self.ships = new_ships

    def add_order(self, order, index=None):
        """Add an order to the queue."""
        if index is None:
            self.orders.append(order)
        else:
            self.orders.insert(index, order)

    def clear_orders(self):
        self.orders.clear()
        self.path = []

    def get_current_order(self):
        if not self.orders:
            return None
        return self.orders[0]

    def pop_order(self):
        if self.orders:
            finished = self.orders.pop(0)
            self.path = []  # Clear path associated with that order
            return finished
        return None

    def merge_with(self, other_fleet: 'Fleet'):
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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        ships_data = []
        for s in self.ships:
            if isinstance(s, str):
                ships_data.append({'type': 'string', 'value': s})
            elif hasattr(s, 'to_dict'):
                ships_data.append({'type': 'instance', 'value': s.to_dict()})

        location_data = None
        if hasattr(self.location, 'to_dict'):
            location_data = self.location.to_dict()
        elif isinstance(self.location, tuple):
            location_data = list(self.location)

        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'location': location_data,
            'speed': self.speed,
            'ships': ships_data,
            'orders': [o.to_dict() for o in self.orders],
            'path': [list(p) if isinstance(p, tuple) else p for p in self.path],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fleet':
        """Deserialize from save game."""
        from game.strategy.data.ship_instance import ShipInstance

        location = data.get('location')
        if isinstance(location, list):
            location = HexCoord(location[0], location[1])

        fleet = cls(
            fleet_id=data['id'],
            owner_id=data['owner_id'],
            location=location,
            speed=data.get('speed', 5.0),
        )

        # Restore ships
        for ship_data in data.get('ships', []):
            if ship_data['type'] == 'string':
                fleet.ships.append(ship_data['value'])
            elif ship_data['type'] == 'instance':
                fleet.ships.append(ShipInstance.from_dict(ship_data['value']))

        # Restore path
        for p in data.get('path', []):
            if isinstance(p, list):
                fleet.path.append(HexCoord(p[0], p[1]))
            else:
                fleet.path.append(p)

        # Orders need special handling for fleet references - skip for now
        # TODO: Restore orders with proper reference resolution

        return fleet

    def __repr__(self):
        ship_count = len(self.ships)
        return f"Fleet({self.id}, Owner:{self.owner_id}, Loc:{self.location}, Ships:{ship_count}, Spd:{self.speed})"

    def __eq__(self, other):
        if not isinstance(other, Fleet):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
