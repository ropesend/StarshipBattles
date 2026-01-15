from game.strategy.data.hex_math import HexCoord
from enum import Enum, auto

class OrderType(Enum):
    MOVE = auto()
    COLONIZE = auto()
    MOVE_TO_FLEET = auto()
    JOIN_FLEET = auto()

class FleetOrder:
    def __init__(self, order_type, target=None):
        self.type = order_type
        self.target = target # HexCoord for MOVE, Planet for COLONIZE, Fleet for MOVE_TO_FLEET/JOIN_FLEET
    
    def __repr__(self):
        return f"FleetOrder({self.type.name}, {self.target})"

class Fleet:
    """
    Represents a fleet of ships on the Strategy Map.
    """
    def __init__(self, fleet_id, owner_id, location, speed=5.0):
        self.id = fleet_id
        self.owner_id = owner_id # 0=Player, 1=Enemy, etc
        self.location = location # HexCoord
        self.ships = [] 
        
        # Movement & Orders
        self.speed = float(speed)
        self.orders = [] # List[Order]
        self.path = [] # Current movement path (HexCoords) for the ACTIVE Move order
        
    def add_ship(self, ship):
        self.ships.append(ship)
        
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
            self.path = [] # Clear path associated with that order
            return finished
        return None

    def merge_with(self, other_fleet):
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

    def __repr__(self):
        return f"Fleet({self.id}, Owner:{self.owner_id}, Loc:{self.location}, Spd:{self.speed})"

    def __eq__(self, other):
        if not isinstance(other, Fleet):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
