from game.strategy.data.hex_math import HexCoord

class Fleet:
    """
    Represents a fleet of ships on the Strategy Map.
    """
    def __init__(self, fleet_id, owner_id, location):
        self.id = fleet_id
        self.owner_id = owner_id # 0=Player, 1=Enemy, etc
        self.location = location # HexCoord (current location)
        
        self.ships = [] # List of Ship objects (or ship data dicts if decoupled)
        
        # Movement
        self.destination = None # HexCoord or System Name?
        self.path = [] # List[HexCoord]
        self.movement_points = 10.0 # Base speed
        
    def add_ship(self, ship):
        self.ships.append(ship)
        
    def set_destination(self, target_hex, path):
        """Set a movement target and path."""
        self.destination = target_hex
        self.path = path
        
    def update(self, dt):
        """
        Update fleet movement.
        note: Strategy layer might be turn-based or real-time.
        If real-time (like Paradox games), we move along the path.
        """
        # Placeholder for real-time movement interpolation
        pass
        
    def __repr__(self):
        return f"Fleet({self.id}, Owner:{self.owner_id}, Loc:{self.location}, Ships:{len(self.ships)})"
