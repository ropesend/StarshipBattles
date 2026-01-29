"""
MockAIController for testing BattleEngine without real AI.

PROJ-43 Phase 8: Provides a test double for IAIController that:
- Tracks method calls for verification
- Returns configurable responses
- Can simulate errors for edge case testing
"""
from typing import Any, List, Optional


class MockAIController:
    """
    Mock implementation of IAIController for testing.

    Implements the IAIController protocol without importing from game.ai.
    Tracks all method calls for test verification.

    Example usage:
        mock = MockAIController(ship)
        engine = BattleEngine()
        engine.start(team1, team2, ai_controllers=[mock])

        # Verify AI was updated
        assert mock.update_call_count == 1

        # Configure behavior
        mock.should_raise_on_update = True
        engine.update()  # Will raise RuntimeError
    """

    def __init__(self, ship: Any, enemy_team_id: int = 1):
        """
        Create a mock AI controller.

        Args:
            ship: The ship/adapter this controller manages
            enemy_team_id: The enemy team ID (for compatibility)
        """
        self._ship = ship
        self.enemy_team_id = enemy_team_id

        # Call tracking
        self.update_call_count = 0
        self.update_calls: List[dict] = []

        # Configurable behavior
        self.should_raise_on_update = False
        self.update_error_message = "MockAIController configured to raise"

    @property
    def ship(self) -> Any:
        """Access the controlled ship/adapter."""
        return self._ship

    def update(self) -> None:
        """
        Mock update method - tracks call and optionally raises.

        Raises:
            RuntimeError: If should_raise_on_update is True
        """
        self.update_call_count += 1
        self.update_calls.append({
            'call_number': self.update_call_count
        })

        if self.should_raise_on_update:
            raise RuntimeError(self.update_error_message)

    def reset_tracking(self) -> None:
        """Reset call tracking counters."""
        self.update_call_count = 0
        self.update_calls = []

    def __repr__(self) -> str:
        ship_name = getattr(self._ship, 'name', str(self._ship))
        return f"MockAIController(ship={ship_name}, updates={self.update_call_count})"
