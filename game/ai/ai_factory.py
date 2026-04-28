"""
AIControllerFactory - Creates AI controllers for ships.

PROJ-126: Moved from game/simulation/factories/ to correct the layer violation.
AI layer can depend on simulation, but simulation should not import from AI.

This factory creates AIController instances for the simulation layer, which
interacts with them via the IAIController protocol defined in simulation.

The factory uses a two-phase initialization:
1. Factory is created (without grid)
2. set_grid() is called when BattleEngine's grid is available

Usage:
    factory = AIControllerFactory()
    # Later, when BattleEngine is created:
    factory.set_grid(engine.grid)
    controller = factory.create_for_ship(ship, enemy_team_id=1)
    controllers = factory.create_for_ships([ship1, ship2], enemy_team_id=1)
"""
import random
from typing import List, Optional, TYPE_CHECKING

from game.core.exceptions import StateException
from game.core.error_codes import ErrorCode
from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
from game.simulation.interfaces.ai_controller import IAIController

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.engine.spatial import SpatialGrid


class AIControllerFactory:
    """
    Factory for creating AI controllers.

    Lives in the AI layer (game/ai/) to maintain proper layer dependencies:
    - AI layer can import from simulation layer
    - Simulation layer uses IAIControllerFactory protocol (doesn't import AI)

    The factory uses a two-phase initialization pattern:
    1. Factory is created without dependencies
    2. set_grid() and set_rng() are called when the grid + RNG become
       available (PROJ-312: seeded RNG is required for replay determinism)

    This allows the factory to be created before BattleEngine exists, then
    configured once the engine's grid and per-battle RNG are available.
    """

    def __init__(self):
        """Create an AI controller factory (without grid or rng)."""
        self._grid: Optional['SpatialGrid'] = None
        self._rng: Optional[random.Random] = None

    def set_grid(self, grid: 'SpatialGrid') -> None:
        """
        Set the spatial grid for AI queries.

        Called by BattleEngine after the grid is created, before any
        AI controllers are needed.

        Args:
            grid: The spatial grid for spatial queries
        """
        self._grid = grid

    def set_rng(self, rng: random.Random) -> None:
        """Set the per-battle seeded RNG forwarded to AI controllers.

        PROJ-312: replay determinism requires that every RNG consumer in
        the battle hot path receive ``BattleEngine.rng`` (a seeded
        ``random.Random`` instance) via DI. The factory threads this rng
        into each ``AIController`` it builds.

        Called by ``BattleEngine.start_teams`` after
        ``_initialize_start_state(seed)`` constructs the per-battle RNG and
        BEFORE controllers are created.
        """
        self._rng = rng

    def create_for_ship(self, ship: 'Ship', enemy_team_id: int) -> IAIController:
        """
        Create an AI controller for a single ship.

        Args:
            ship: The ship to control
            enemy_team_id: The ID of the enemy team (0 or 1)

        Returns:
            An AIController instance that implements IAIController

        Raises:
            StateException: If set_grid() or set_rng() hasn't been called
        """
        if self._grid is None:
            raise StateException(
                "AIControllerFactory grid not initialized",
                code=ErrorCode.NOT_INITIALIZED.value,
                context={"state": "grid_missing"}
            )
        if self._rng is None:
            raise StateException(
                "AIControllerFactory rng not initialized",
                code=ErrorCode.NOT_INITIALIZED.value,
                context={"state": "rng_missing"}
            )
        adapter = ShipControllableAdapter(ship)
        return AIController(adapter, self._grid, enemy_team_id, rng=self._rng)

    def create_for_ships(self, ships: List['Ship'], enemy_team_id: int) -> List[IAIController]:
        """
        Create AI controllers for multiple ships.

        Args:
            ships: List of ships to control
            enemy_team_id: The ID of the enemy team (0 or 1)

        Returns:
            List of AIController instances, one per ship
        """
        return [self.create_for_ship(ship, enemy_team_id) for ship in ships]
