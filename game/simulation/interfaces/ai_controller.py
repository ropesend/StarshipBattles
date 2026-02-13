"""
AI Controller interfaces for BattleEngine.

PROJ-43 Phase 8: Defines interfaces for AI controllers used by BattleEngine.
PROJ-126: Added IAIControllerFactory protocol for layer-clean AI creation.

This decouples BattleEngine from concrete AI implementations, enabling:
- Testing BattleEngine with mock AI controllers
- Custom AI implementations
- Clear layer boundaries (simulation ↔ AI)

The protocols are intentionally minimal - they only include methods that
BattleEngine actually calls.
"""
from typing import Any, List, Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.engine.spatial import SpatialGrid


@runtime_checkable
class IAIController(Protocol):
    """
    Protocol for AI controllers used by BattleEngine.

    BattleEngine interacts with AI controllers through this interface:
    - Calls update() each tick to let AI make decisions
    - Accesses ship property to identify which ship a controller manages

    This is a structural (duck-typed) protocol - any class with matching
    methods/properties is compatible without explicit inheritance.

    Example implementation:
        class MyAIController:
            def __init__(self, ship):
                self._ship = ship

            @property
            def ship(self) -> Any:
                return self._ship

            def update(self) -> None:
                # AI decision logic here
                pass
    """

    @property
    def ship(self) -> Any:
        """
        Access the controlled ship/adapter for identification.

        Used by BattleEngine.remove_ship() to find the controller
        for a specific ship. The ship property typically returns
        a ShipControllableAdapter that wraps the actual Ship.

        Returns:
            The controllable entity (typically ShipControllableAdapter)
        """
        ...

    def update(self) -> None:
        """
        Execute one AI update cycle.

        Called once per tick by BattleEngine. The controller should:
        - Check if ship is alive
        - Acquire/update targets
        - Select and execute movement behavior
        - Control weapons (trigger_pulled)

        The implementation should be idempotent and handle edge cases
        like dead ships gracefully.
        """
        ...


@runtime_checkable
class IAIControllerFactory(Protocol):
    """
    Protocol for AI controller factories.

    PROJ-126: Defines the interface for creating AI controllers. The factory
    is implemented in the AI layer (game/ai/) and injected into the simulation
    layer, maintaining proper layer dependencies:
    - AI layer depends on simulation (allowed)
    - Simulation layer uses this protocol (doesn't import AI)

    The factory is initialized without a grid, then set_grid() is called
    when the BattleEngine's grid is available.

    Example implementation:
        class AIControllerFactory:
            def __init__(self):
                self._grid = None

            def set_grid(self, grid: SpatialGrid) -> None:
                self._grid = grid

            def create_for_ship(self, ship, enemy_team_id) -> IAIController:
                return AIController(ShipControllableAdapter(ship), self._grid, enemy_team_id)
    """

    def set_grid(self, grid: 'SpatialGrid') -> None:
        """
        Set the spatial grid for AI queries.

        Called by BattleEngine after the grid is created, before any
        AI controllers are needed.

        Args:
            grid: The spatial grid for spatial queries
        """
        ...

    def create_for_ship(self, ship: 'Ship', enemy_team_id: int) -> 'IAIController':
        """
        Create an AI controller for a single ship.

        Args:
            ship: The ship to control
            enemy_team_id: The ID of the enemy team (0 or 1)

        Returns:
            An IAIController instance for the ship
        """
        ...

    def create_for_ships(self, ships: List['Ship'], enemy_team_id: int) -> List['IAIController']:
        """
        Create AI controllers for multiple ships.

        Args:
            ships: List of ships to control
            enemy_team_id: The ID of the enemy team (0 or 1)

        Returns:
            List of IAIController instances, one per ship
        """
        ...
