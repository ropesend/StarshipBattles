"""
AIControllerFactory - Creates AI controllers for ships.

PROJ-43 Phase 8: Isolates AI layer imports from BattleEngine by providing
a factory that creates AIController instances. This enables:
- BattleEngine to remain decoupled from game.ai
- Testing BattleEngine with mock AI controllers
- Centralized AI creation logic

Usage:
    factory = AIControllerFactory(grid)
    controller = factory.create_for_ship(ship, enemy_team_id=1)
    controllers = factory.create_for_ships([ship1, ship2], enemy_team_id=1)
"""
from typing import List, TYPE_CHECKING

from game.simulation.interfaces.ai_controller import IAIController

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.engine.spatial import SpatialGrid


class AIControllerFactory:
    """
    Factory for creating AI controllers.

    Encapsulates the import and instantiation of AIController from game.ai,
    isolating this cross-layer dependency to a single class.

    The factory requires a SpatialGrid at construction, which is passed to
    all created controllers for spatial queries during AI updates.
    """

    def __init__(self, grid: 'SpatialGrid'):
        """
        Create an AI controller factory.

        Args:
            grid: The spatial grid for AI to use for target queries.
                  This is typically the BattleEngine's grid.
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
        """
        # Import from game.ai layer - isolated to this factory
        from game.ai.controller import AIController
        from game.ai.interfaces import ShipControllableAdapter

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
