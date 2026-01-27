"""
BattleOrchestrator - UI-layer orchestration for battle setup.

This class handles AI controller creation, which requires importing from
the AI layer. By placing this in the UI layer instead of Simulation,
we maintain proper layer boundaries:
  - Simulation depends on Core only
  - UI coordinates between all layers

PROJ-17: Created as part of layer boundary enforcement.
"""
from typing import List, TYPE_CHECKING

from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
from game.engine.spatial import SpatialGrid

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class BattleOrchestrator:
    """
    Orchestrates battle setup in the UI layer.

    Responsibilities:
    - Creating AIController instances for ships
    - Wrapping ships with ShipControllableAdapter
    - Providing pre-configured AI list to BattleEngine
    """

    def __init__(self, grid: SpatialGrid):
        """
        Initialize the orchestrator.

        Args:
            grid: Spatial grid for AI target queries
        """
        self.grid = grid

    def create_ai_controllers(
        self,
        team0_ships: List['Ship'],
        team1_ships: List['Ship']
    ) -> List[AIController]:
        """
        Create AI controllers for all ships in a battle.

        Args:
            team0_ships: Ships for team 0
            team1_ships: Ships for team 1

        Returns:
            List of AIController instances ready to use
        """
        controllers = []

        # Team 0 ships target team 1
        for ship in team0_ships:
            adapter = ShipControllableAdapter(ship)
            controller = AIController(adapter, self.grid, enemy_team_id=1)
            controllers.append(controller)

        # Team 1 ships target team 0
        for ship in team1_ships:
            adapter = ShipControllableAdapter(ship)
            controller = AIController(adapter, self.grid, enemy_team_id=0)
            controllers.append(controller)

        return controllers

    def create_ai_for_ship(
        self,
        ship: 'Ship',
        enemy_team_id: int
    ) -> AIController:
        """
        Create a single AI controller for a ship (e.g., for reinforcements).

        Args:
            ship: Ship to control
            enemy_team_id: ID of the enemy team to target

        Returns:
            Configured AIController
        """
        adapter = ShipControllableAdapter(ship)
        return AIController(adapter, self.grid, enemy_team_id)
