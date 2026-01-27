"""
RetreatManager - Handles retreat and escape mechanics for battles.

Extracted from BattleController (PROJ-29 SIM-03) to separate concerns.
Manages:
- Retreat requests (edge navigation or warp charging)
- Retreat state tracking and updates
- Ship escape detection
- Escape callbacks
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Callable, Tuple, List, Any, TYPE_CHECKING

from game.core.logger import log_debug, log_info

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class RetreatMethod(Enum):
    """Methods for ship retreat."""
    EDGE = "edge"    # Navigate to map edge
    WARP = "warp"    # Charge warp drive


@dataclass
class RetreatState:
    """Tracks retreat progress for a ship."""
    method: RetreatMethod
    target: Optional[Tuple[float, float]] = None  # For edge escape
    charge_ticks: int = 0  # For warp
    required_ticks: int = 500  # Ticks needed for warp (5 seconds at 100 TPS)
    interruptible: bool = True


class RetreatManager:
    """
    Manages retreat and escape mechanics for battles.

    Handles:
    - Retreat requests and tracking
    - Warp charging progression
    - Edge escape detection
    - Escape callbacks
    """

    # Default edge detection threshold in world units
    DEFAULT_EDGE_THRESHOLD = 500

    def __init__(self, map_bounds: Tuple[float, float, float, float]):
        """
        Initialize RetreatManager.

        Args:
            map_bounds: (min_x, min_y, max_x, max_y) map boundaries
        """
        self.map_bounds = map_bounds
        self.retreating_ships: Dict[str, RetreatState] = {}
        self.escaped_ships: List[str] = []
        self._on_ship_escaped: Optional[Callable[['Ship'], None]] = None

    def request_retreat(
        self,
        ship: 'Ship',
        ship_id_map: Dict[int, str],
        method: RetreatMethod = RetreatMethod.EDGE
    ) -> Tuple[bool, Optional[str]]:
        """
        Request a ship to retreat.

        Args:
            ship: Ship to retreat
            ship_id_map: Mapping of object id(ship) to string ship_id
            method: Retreat method (EDGE or WARP)

        Returns:
            Tuple of (success, error_message)
        """
        if not ship.is_alive:
            return False, "Ship is not alive"

        ship_id = ship_id_map.get(id(ship))
        if not ship_id:
            return False, "Ship not found in battle"

        if ship_id in self.retreating_ships:
            return False, "Ship already retreating"

        if method == RetreatMethod.EDGE:
            target = self.find_nearest_edge(ship)
            self.retreating_ships[ship_id] = RetreatState(
                method=RetreatMethod.EDGE,
                target=target,
            )
            log_debug(f"Ship {ship.name} retreating to edge at {target}")

        elif method == RetreatMethod.WARP:
            self.retreating_ships[ship_id] = RetreatState(
                method=RetreatMethod.WARP,
                charge_ticks=0,
                required_ticks=500,  # ~5 seconds at 100 TPS
                interruptible=True,
            )
            log_debug(f"Ship {ship.name} charging warp drive")

        return True, None

    def cancel_retreat(
        self,
        ship: 'Ship',
        ship_id_map: Dict[int, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel a ship's retreat.

        Args:
            ship: Ship to cancel retreat for
            ship_id_map: Mapping of object id(ship) to string ship_id

        Returns:
            Tuple of (success, error_message)
        """
        ship_id = ship_id_map.get(id(ship))
        if ship_id and ship_id in self.retreating_ships:
            del self.retreating_ships[ship_id]
            log_debug(f"Ship {ship.name} retreat cancelled")
            return True, None
        return False, "Ship not retreating"

    def update(
        self,
        get_ship_by_id: Callable[[str], Optional['Ship']]
    ) -> None:
        """
        Process retreat states for one tick.

        Args:
            get_ship_by_id: Function to get ship by string ID
        """
        escaped = []

        for ship_id, state in list(self.retreating_ships.items()):
            ship = get_ship_by_id(ship_id)

            if not ship or not ship.is_alive:
                escaped.append(ship_id)
                continue

            if state.method == RetreatMethod.EDGE:
                if self.at_map_edge(ship):
                    self._handle_ship_escaped(ship, ship_id)
                    escaped.append(ship_id)
                # Note: AI override for edge movement would be handled externally

            elif state.method == RetreatMethod.WARP:
                state.charge_ticks += 1
                if state.charge_ticks >= state.required_ticks:
                    self._handle_ship_escaped(ship, ship_id)
                    escaped.append(ship_id)

        for ship_id in escaped:
            if ship_id in self.retreating_ships:
                del self.retreating_ships[ship_id]

    def _handle_ship_escaped(self, ship: 'Ship', ship_id: str) -> None:
        """Handle a ship successfully escaping."""
        ship.is_alive = False
        if hasattr(ship, 'retreat_status'):
            ship.retreat_status = "escaped"

        self.escaped_ships.append(ship_id)

        log_info(f"Ship {ship.name} escaped via retreat")

        if self._on_ship_escaped:
            self._on_ship_escaped(ship)

    def find_nearest_edge(self, ship: 'Ship') -> Tuple[float, float]:
        """
        Find the nearest map edge for retreat.

        Args:
            ship: Ship to find edge for

        Returns:
            (x, y) target position at nearest edge
        """
        min_x, min_y, max_x, max_y = self.map_bounds

        dist_left = ship.x - min_x
        dist_right = max_x - ship.x
        dist_top = ship.y - min_y
        dist_bottom = max_y - ship.y

        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

        if min_dist == dist_left:
            return (min_x, ship.y)
        elif min_dist == dist_right:
            return (max_x, ship.y)
        elif min_dist == dist_top:
            return (ship.x, min_y)
        else:
            return (ship.x, max_y)

    def at_map_edge(
        self,
        ship: 'Ship',
        threshold: float = DEFAULT_EDGE_THRESHOLD
    ) -> bool:
        """
        Check if ship is at map edge.

        Args:
            ship: Ship to check
            threshold: Distance from edge to consider "at edge"

        Returns:
            True if ship is within threshold of any edge
        """
        min_x, min_y, max_x, max_y = self.map_bounds
        return (
            ship.x <= min_x + threshold or
            ship.x >= max_x - threshold or
            ship.y <= min_y + threshold or
            ship.y >= max_y - threshold
        )

    def is_retreating(
        self,
        ship: 'Ship',
        ship_id_map: Dict[int, str]
    ) -> bool:
        """
        Check if a ship is currently retreating.

        Args:
            ship: Ship to check
            ship_id_map: Mapping of object id(ship) to string ship_id

        Returns:
            True if ship is retreating
        """
        ship_id = ship_id_map.get(id(ship))
        return ship_id is not None and ship_id in self.retreating_ships

    def get_retreat_state(
        self,
        ship: 'Ship',
        ship_id_map: Dict[int, str]
    ) -> Optional[RetreatState]:
        """
        Get the retreat state for a ship.

        Args:
            ship: Ship to get state for
            ship_id_map: Mapping of object id(ship) to string ship_id

        Returns:
            RetreatState if retreating, None otherwise
        """
        ship_id = ship_id_map.get(id(ship))
        if ship_id:
            return self.retreating_ships.get(ship_id)
        return None

    def set_on_ship_escaped(
        self,
        callback: Optional[Callable[['Ship'], None]]
    ) -> None:
        """Set callback for ship escape."""
        self._on_ship_escaped = callback

    def reset(self) -> None:
        """Reset all tracking state."""
        self.retreating_ships.clear()
        self.escaped_ships.clear()
