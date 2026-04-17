"""
RetreatManager - Handles retreat and escape mechanics for battles.

Extracted from BattleController (PROJ-29 SIM-03) to separate concerns.
Manages:
- Retreat requests (edge navigation or warp charging)
- Retreat state tracking and updates
- Ship escape detection
- Escape callbacks

PROJ-270 Task 5.4: accepts a `BoundaryRegion` (origin-centered ADT)
instead of the legacy corner-rooted `map_bounds=(min_x, min_y, max_x,
max_y)` tuple. `UnboundedRegion` disables edge retreat (warp retreat
still works).
"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Callable, Tuple, List, TYPE_CHECKING

from game.core.constants import SimulationConstants
from game.core.math import Vector2
from game.simulation.combat.boundary import BoundaryRegion, UnboundedRegion

logger = logging.getLogger(__name__)

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
    required_ticks: int = SimulationConstants.WARP_CHARGE_TICKS
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
    DEFAULT_EDGE_THRESHOLD = SimulationConstants.DEFAULT_MAP_EDGE_THRESHOLD

    def __init__(self, boundary: BoundaryRegion):
        """
        Initialize RetreatManager.

        Args:
            boundary: `BoundaryRegion` ADT (origin-centered rect, circle,
                or unbounded). Used by edge-retreat logic to find the
                closest edge and detect when a ship has arrived there.
                `UnboundedRegion` disables EDGE retreat (no edge to
                reach); WARP retreat continues to work.
        """
        self.boundary = boundary
        self.retreating_ships: Dict[str, RetreatState] = {}
        self.escaped_ships: List[str] = []
        self._on_ship_escaped: Optional[Callable[['Ship'], None]] = None

    def request_retreat(
        self,
        ship: 'Ship',
        ship_id_map: Dict[str, str],
        method: RetreatMethod = RetreatMethod.EDGE
    ) -> Tuple[bool, Optional[str]]:
        """
        Request a ship to retreat.

        Args:
            ship: Ship to retreat
            ship_id_map: Mapping of ship.id to battle state ship_id
            method: Retreat method (EDGE or WARP)

        Returns:
            Tuple of (success, error_message)
        """
        if not ship.is_alive:
            return False, "Ship is not alive"

        ship_id = ship_id_map.get(ship.id)
        if not ship_id:
            return False, "Ship not found in battle"

        if ship_id in self.retreating_ships:
            return False, "Ship already retreating"

        if method == RetreatMethod.EDGE:
            if isinstance(self.boundary, UnboundedRegion):
                return False, "Cannot edge-retreat in unbounded arena — no edge to reach"
            target = self.find_nearest_edge(ship)
            self.retreating_ships[ship_id] = RetreatState(
                method=RetreatMethod.EDGE,
                target=target,
            )
            logger.debug(f"Ship {ship.name} retreating to edge at {target}")

        elif method == RetreatMethod.WARP:
            self.retreating_ships[ship_id] = RetreatState(
                method=RetreatMethod.WARP,
                charge_ticks=0,
                required_ticks=SimulationConstants.WARP_CHARGE_TICKS,
                interruptible=True,
            )
            logger.debug(f"Ship {ship.name} charging warp drive")

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
            ship_id_map: Mapping of ship.id to battle state ship_id

        Returns:
            Tuple of (success, error_message)
        """
        ship_id = ship_id_map.get(ship.id)
        if ship_id and ship_id in self.retreating_ships:
            del self.retreating_ships[ship_id]
            logger.debug(f"Ship {ship.name} retreat cancelled")
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
        ship.retreat_status = "escaped"

        self.escaped_ships.append(ship_id)

        logger.info(f"Ship {ship.name} escaped via retreat")

        if self._on_ship_escaped:
            self._on_ship_escaped(ship)

    def find_nearest_edge(self, ship: 'Ship') -> Tuple[float, float]:
        """
        Find the nearest boundary edge for retreat.

        Args:
            ship: Ship to find edge for

        Returns:
            (x, y) target position on the nearest boundary edge

        Raises:
            NotImplementedError: if boundary is `UnboundedRegion` (no edge
                exists). Callers should check `isinstance(self.boundary,
                UnboundedRegion)` before invoking this method.
        """
        edge = self.boundary.closest_edge_point(Vector2(ship.x, ship.y))
        return (edge.x, edge.y)

    def at_map_edge(
        self,
        ship: 'Ship',
        threshold: float = DEFAULT_EDGE_THRESHOLD
    ) -> bool:
        """
        Check if ship is at boundary edge.

        Args:
            ship: Ship to check
            threshold: Distance from edge to consider "at edge"

        Returns:
            True if ship is within `threshold` of the boundary edge.
            `UnboundedRegion` always returns False (its
            `distance_to_edge` is `math.inf`).
        """
        dist = self.boundary.distance_to_edge(Vector2(ship.x, ship.y))
        return dist <= threshold

    def is_retreating(
        self,
        ship: 'Ship',
        ship_id_map: Dict[int, str]
    ) -> bool:
        """
        Check if a ship is currently retreating.

        Args:
            ship: Ship to check
            ship_id_map: Mapping of ship.id to battle state ship_id

        Returns:
            True if ship is retreating
        """
        ship_id = ship_id_map.get(ship.id)
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
            ship_id_map: Mapping of ship.id to battle state ship_id

        Returns:
            RetreatState if retreating, None otherwise
        """
        ship_id = ship_id_map.get(ship.id)
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
