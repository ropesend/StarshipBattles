"""
Battle Mode Handlers - Strategy pattern for battle mode-specific behavior.

Provides specialized handlers for each battle mode:
- ManualBattleModeHandler: Battle Setup screen (visual, no fleet effects)
- TestBattleModeHandler: Combat Lab (headless, no persistence)
- StrategyBattleModeHandler: Strategy layer fleet combat (retreat, reinforce, fleet effects)
- HypotheticalBattleModeHandler: Planning simulations (isolated, ship cloning)

This implements the Strategy pattern to eliminate mode-specific conditionals
scattered throughout BattleController (CQ-024 Open/Closed violation fix).
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.simulation.battle_config import BattleConfig, BattleMode

if TYPE_CHECKING:
    from game.simulation.battle_controller import BattleController
    from game.simulation.battle_state import BattleResults


class BattleModeHandler(ABC):
    """
    Abstract base class for battle mode handlers.

    Each mode handler encapsulates mode-specific behavior including:
    - Configuration setup
    - Retreat/reinforcement permissions
    - Ship cloning requirements
    - Result application to fleets
    """

    @abstractmethod
    def configure(self, controller: 'BattleController', config: 'BattleConfig') -> None:
        """
        Configure the handler for a battle.

        Called during BattleController.configure() to set up mode-specific state.

        Args:
            controller: The BattleController being configured
            config: The BattleConfig with mode-specific settings
        """
        pass

    @abstractmethod
    def can_retreat(self) -> bool:
        """
        Check if retreat is allowed in this mode.

        Returns:
            True if ships can retreat, False otherwise
        """
        pass

    @abstractmethod
    def can_reinforce(self) -> bool:
        """
        Check if reinforcements are allowed in this mode.

        Returns:
            True if reinforcements can be added mid-battle, False otherwise
        """
        pass

    @abstractmethod
    def should_clone_ships(self) -> bool:
        """
        Check if ships should be cloned for isolation.

        Returns:
            True if ships should be deep-cloned to prevent mutation, False otherwise
        """
        pass

    @abstractmethod
    def is_headless_default(self) -> bool:
        """
        Check if this mode runs headless by default.

        Returns:
            True if mode is typically headless, False for visual
        """
        pass

    def apply_results(self, controller: 'BattleController', results: 'BattleResults') -> None:
        """Apply post-battle results. Override if mode needs it."""
        pass


class ManualBattleModeHandler(BattleModeHandler):
    """
    Handler for manual battles (Battle Setup screen).

    Characteristics:
    - Visual mode (not headless by default)
    - No retreat allowed
    - No reinforcements
    - No ship cloning
    - No fleet effects (results not applied back)
    """

    def configure(self, controller: 'BattleController', config: 'BattleConfig') -> None:
        """No special configuration needed for manual mode."""
        pass

    def can_retreat(self) -> bool:
        """Manual mode does not allow retreat."""
        return False

    def can_reinforce(self) -> bool:
        """Manual mode does not allow reinforcements."""
        return False

    def should_clone_ships(self) -> bool:
        """Manual mode uses ships directly (no cloning)."""
        return False

    def is_headless_default(self) -> bool:
        """Manual mode is visual by default."""
        return False


class TestBattleModeHandler(BattleModeHandler):
    """
    Handler for test battles (Combat Lab).

    Characteristics:
    - Headless by default
    - No retreat allowed
    - No reinforcements
    - No ship cloning (scenario provides ships)
    - No persistence (results not saved)
    """

    def configure(self, controller: 'BattleController', config: 'BattleConfig') -> None:
        """No special configuration needed for test mode."""
        pass

    def can_retreat(self) -> bool:
        """Test mode does not allow retreat."""
        return False

    def can_reinforce(self) -> bool:
        """Test mode does not allow reinforcements."""
        return False

    def should_clone_ships(self) -> bool:
        """Test mode uses scenario-provided ships (no cloning)."""
        return False

    def is_headless_default(self) -> bool:
        """Test mode is headless by default."""
        return True


class StrategyBattleModeHandler(BattleModeHandler):
    """
    Handler for strategy layer fleet battles.

    Characteristics:
    - Headless by default
    - Retreat allowed
    - Reinforcements allowed
    - No ship cloning (uses actual fleet ships)
    - Fleet effects (results applied back to source fleets)
    """

    def configure(self, controller: 'BattleController', config: 'BattleConfig') -> None:
        """No special configuration needed for strategy mode."""
        pass

    def can_retreat(self) -> bool:
        """Strategy mode allows retreat."""
        return True

    def can_reinforce(self) -> bool:
        """Strategy mode allows reinforcements."""
        return True

    def should_clone_ships(self) -> bool:
        """Strategy mode uses actual fleet ships (no cloning)."""
        return False

    def is_headless_default(self) -> bool:
        """Strategy mode is headless by default."""
        return True


class HypotheticalBattleModeHandler(BattleModeHandler):
    """
    Handler for hypothetical (what-if) battles.

    Characteristics:
    - Headless by default
    - No retreat allowed
    - No reinforcements
    - Ships always cloned (isolation)
    - No fleet effects (isolated simulation)
    """

    def configure(self, controller: 'BattleController', config: 'BattleConfig') -> None:
        """No special configuration needed for hypothetical mode."""
        pass

    def can_retreat(self) -> bool:
        """Hypothetical mode does not allow retreat."""
        return False

    def can_reinforce(self) -> bool:
        """Hypothetical mode does not allow reinforcements."""
        return False

    def should_clone_ships(self) -> bool:
        """Hypothetical mode always clones ships for isolation."""
        return True

    def is_headless_default(self) -> bool:
        """Hypothetical mode is headless by default."""
        return True


def get_handler_for_mode(mode: BattleMode) -> BattleModeHandler:
    """
    Factory function to get the appropriate handler for a battle mode.

    Args:
        mode: The BattleMode to get a handler for

    Returns:
        The appropriate BattleModeHandler instance

    Raises:
        ValidationException: If mode is not recognized
    """
    handlers = {
        BattleMode.MANUAL: ManualBattleModeHandler,
        BattleMode.TEST: TestBattleModeHandler,
        BattleMode.STRATEGY: StrategyBattleModeHandler,
        BattleMode.HYPOTHETICAL: HypotheticalBattleModeHandler,
    }

    handler_class = handlers.get(mode)
    if handler_class is None:
        raise ValidationException(
            f"Unknown battle mode: {mode}",
            code=ErrorCode.VALIDATION_FAILED.value,
            context={"mode": str(mode)}
        )

    return handler_class()
