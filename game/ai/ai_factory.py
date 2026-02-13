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
from typing import List, Optional, TYPE_CHECKING

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
    2. set_grid() is called when the grid becomes available

    This allows the factory to be created before BattleEngine exists, then
    configured once the engine's grid is available.
    """

    def __init__(self):
        """Create an AI controller factory (without grid)."""
        self._grid: Optional['SpatialGrid'] = None

    def set_grid(self, grid: 'SpatialGrid') -> None:
        """
        Set the spatial grid for AI queries.

        Called by BattleEngine after the grid is created, before any
        AI controllers are needed.

        Args:
            grid: The spatial grid for spatial queries
        """
        self._grid = grid

    def create_for_ship(self, ship: 'Ship', enemy_team_id: int) -> IAIController:
        """
        Create an AI controller for a single ship.

        Args:
            ship: The ship to control
            enemy_team_id: The ID of the enemy team (0 or 1)

        Returns:
            An AIController instance that implements IAIController

        Raises:
            RuntimeError: If set_grid() hasn't been called
        """
        if self._grid is None:
            raise RuntimeError(
                "AIControllerFactory.set_grid() must be called before creating controllers"
            )
        adapter = ShipControllableAdapter(ship)
        return AIController(adapter, self._grid, enemy_team_id)

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
