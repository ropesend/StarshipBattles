"""
ShipFormation - Manages formation relationships for a ship.

Extracted from Ship class as part of Ship God Object decomposition.
Uses composition pattern: ship.formation = ShipFormation(self)
"""
from typing import Optional, List, TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .ship import Ship


class ShipFormation:
    """
    Manages formation state for a ship.
    
    A ship can be either:
    - A formation master (has members)
    - A formation member (has a master)
    - Neither (solo ship)
    
    Attributes:
        ship: The ship this formation belongs to
        master: Reference to formation leader (if following)
        offset: Vector2 position offset relative to master
        rotation_mode: 'relative' (rotates with master) or 'fixed' (absolute angle)
        members: List of ships following this ship (if master)
        active: Whether currently holding formation position
    """
    
    def __init__(self, ship: 'Ship'):
        self.ship = ship
        self.master: Optional['Ship'] = None
        self.offset: Optional[pygame.math.Vector2] = None
        self.rotation_mode: str = 'relative'
        self.members: List['Ship'] = []
        self.active: bool = True
    
    @property
    def is_master(self) -> bool:
        """Returns True if this ship has formation members."""
        return len(self.members) > 0
    
    @property
    def is_member(self) -> bool:
        """Returns True if this ship is following a master."""
        return self.master is not None
    
    def join(self, master: 'Ship', offset: pygame.math.Vector2) -> None:
        """
        Join a formation as a follower.
        
        Args:
            master: The ship to follow
            offset: Position offset from master's position
        """
        self.master = master
        self.offset = offset
        self.active = True
        
        # Also register with master's formation
        if master and hasattr(master, 'formation'):
            if self.ship not in master.formation.members:
                master.formation.members.append(self.ship)
    
    def leave(self) -> None:
        """Leave the current formation."""
        # Unregister from master
        if self.master and hasattr(self.master, 'formation'):
            try:
                self.master.formation.members.remove(self.ship)
            except ValueError:
                pass  # Not in members list
        
        self.master = None
        self.active = False
    
    def add_member(self, ship: 'Ship', offset: pygame.math.Vector2) -> None:
        """
        Add a follower to this ship's formation.
        
        Args:
            ship: The ship to add as follower
            offset: Position offset for the follower
        """
        if ship not in self.members:
            self.members.append(ship)
        
        # Set up the follower's formation state
        if hasattr(ship, 'formation'):
            ship.formation.master = self.ship
            ship.formation.offset = offset
            ship.formation.active = True
    
    def remove_member(self, ship: 'Ship') -> None:
        """
        Remove a follower from this ship's formation.
        
        Args:
            ship: The ship to remove
        """
        try:
            self.members.remove(ship)
        except ValueError:
            pass  # Not in list
        
        # Clear the follower's formation state
        if hasattr(ship, 'formation'):
            ship.formation.master = None
            ship.formation.active = False
