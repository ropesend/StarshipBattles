"""
IAIController protocol for BattleEngine.

PROJ-43 Phase 8: Defines the interface for AI controllers used by BattleEngine.
This decouples BattleEngine from the concrete AIController implementation,
enabling:
- Testing BattleEngine with mock AI controllers
- Custom AI implementations
- Clear layer boundaries (simulation ↔ AI)

The protocol is intentionally minimal - it only includes methods that
BattleEngine actually calls on AI controllers.
"""
from typing import Any, Protocol, runtime_checkable


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
