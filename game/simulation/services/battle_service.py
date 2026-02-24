"""
BattleService - Abstraction layer between UI and BattleEngine.

This service handles battle creation, ship management, and simulation control,
providing a clean interface for battle screens.
"""
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, TYPE_CHECKING

from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
from game.simulation.systems.battle_end_conditions import BattleEndCondition, BattleEndMode
from game.core.exceptions import ValidationException, StateException

logger = logging.getLogger(__name__)

# TYPE_CHECKING imports to avoid simulation->ai import at runtime
# The actual factory is injected by callers from higher layers (UI, strategy)
if TYPE_CHECKING:
    from game.simulation.interfaces.ai_controller import IAIControllerFactory
    from game.simulation.entities.ship import Ship


@dataclass
class BattleServiceResult:
    """
    Result object for battle service operations.

    Note: This class was renamed from BattleResult to BattleServiceResult
    (PROJ-107) to disambiguate from:
    - BattleResults (battle_state.py) - actual battle outcome data
    - BattleResult (strategy layer) - strategy DTO for battle resolution
    """
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    engine: Optional[BattleEngine] = None


class BattleService:
    """
    Service layer for battle operations.

    Provides an abstraction between the UI and BattleEngine,
    encapsulating battle setup, execution, and state queries.
    """

    def __init__(self):
        self._engine: Optional[BattleEngine] = None
        self._team0_ships: List['Ship'] = []
        self._team1_ships: List['Ship'] = []
        self._is_started: bool = False
        self._seed: Optional[int] = None

    def create_battle(
        self,
        seed: Optional[int] = None,
        enable_logging: bool = False,
        ai_factory: Optional['IAIControllerFactory'] = None
    ) -> BattleServiceResult:
        """
        Create a new battle instance.

        Args:
            seed: Random seed for reproducible battles
            enable_logging: Whether to enable battle logging to file
            ai_factory: Optional AIControllerFactory for creating AI controllers.
                       PROJ-126: Must be injected from higher layers (UI/strategy)
                       to maintain proper layer dependencies (AI depends on simulation,
                       not vice versa). If not provided, AI controllers won't be
                       auto-created for fighter launches.

        Returns:
            BattleServiceResult with the created engine
        """
        try:
            logger = BattleLogger(enabled=enable_logging)
            # PROJ-43/PROJ-126: Create engine with optional factory
            # Factory is now injected from callers (UI/strategy layers)
            self._engine = BattleEngine(logger=logger, ai_factory=ai_factory)
            self._team0_ships = []
            self._team1_ships = []
            self._is_started = False
            self._seed = seed

            return BattleServiceResult(
                success=True,
                engine=self._engine
            )

        except (TypeError, ValueError, AttributeError, ValidationException, StateException) as e:
            logger.error(f"Failed to create battle: {e}")
            return BattleServiceResult(
                success=False,
                errors=[str(e)]
            )

    def add_ship(
        self,
        ship: 'Ship',
        team_id: int
    ) -> BattleServiceResult:
        """
        Add a ship to the battle.

        Args:
            ship: Ship to add
            team_id: Team identifier (0 or 1)

        Returns:
            BattleServiceResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle - call create_battle() first")
            return BattleServiceResult(success=False, errors=errors)

        if self._is_started:
            errors.append("Cannot add ships after battle has started")
            return BattleServiceResult(success=False, errors=errors)

        # Update ship's team_id
        ship.team_id = team_id

        # Add to appropriate team list
        if team_id == 0:
            self._team0_ships.append(ship)
        else:
            self._team1_ships.append(ship)

        return BattleServiceResult(success=True, engine=self._engine)

    def remove_ship(
        self,
        ship: 'Ship'
    ) -> BattleServiceResult:
        """
        Remove a ship from the battle (before start).

        Args:
            ship: Ship to remove

        Returns:
            BattleServiceResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle")
            return BattleServiceResult(success=False, errors=errors)

        if self._is_started:
            errors.append("Cannot remove ships after battle has started")
            return BattleServiceResult(success=False, errors=errors)

        removed = False
        if ship in self._team0_ships:
            self._team0_ships.remove(ship)
            removed = True
        elif ship in self._team1_ships:
            self._team1_ships.remove(ship)
            removed = True

        if not removed:
            errors.append(f"Ship '{ship.name}' not found in battle")
            return BattleServiceResult(success=False, errors=errors)

        return BattleServiceResult(success=True, engine=self._engine)

    def start_battle(
        self,
        end_mode: BattleEndMode = BattleEndMode.HP_BASED,
        max_ticks: Optional[int] = None
    ) -> BattleServiceResult:
        """
        Start the battle simulation.

        Args:
            end_mode: Battle end condition mode
            max_ticks: Maximum ticks for time-based battles

        Returns:
            BattleServiceResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle - call create_battle() first")
            return BattleServiceResult(success=False, errors=errors)

        if self._is_started:
            errors.append("Battle already started")
            return BattleServiceResult(success=False, errors=errors)

        if not self._team0_ships and not self._team1_ships:
            errors.append("Cannot start battle with no ships")
            return BattleServiceResult(success=False, errors=errors)

        # Create end condition
        end_condition = BattleEndCondition(mode=end_mode)
        if max_ticks is not None:
            end_condition.max_ticks = max_ticks

        # Start the engine
        self._engine.start(
            team1_ships=self._team0_ships,
            team2_ships=self._team1_ships,
            seed=self._seed,
            end_condition=end_condition
        )
        self._is_started = True

        logger.info(f"Battle started: {len(self._team0_ships)} vs {len(self._team1_ships)} ships")

        return BattleServiceResult(success=True, engine=self._engine)

    def update(self) -> BattleServiceResult:
        """
        Run one simulation tick.

        Returns:
            BattleServiceResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle")
            return BattleServiceResult(success=False, errors=errors)

        if not self._is_started:
            errors.append("Battle not started - call start_battle() first")
            return BattleServiceResult(success=False, errors=errors)

        self._engine.update()

        return BattleServiceResult(success=True, engine=self._engine)

    def run_ticks(self, count: int) -> BattleServiceResult:
        """
        Run multiple simulation ticks.

        Args:
            count: Number of ticks to run

        Returns:
            BattleServiceResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle")
            return BattleServiceResult(success=False, errors=errors)

        if not self._is_started:
            errors.append("Battle not started - call start_battle() first")
            return BattleServiceResult(success=False, errors=errors)

        for _ in range(count):
            if self._engine.is_battle_over():
                break
            self._engine.update()

        return BattleServiceResult(success=True, engine=self._engine)

    def is_battle_over(self) -> bool:
        """
        Check if the battle has ended.

        Returns:
            True if battle is over, False otherwise
        """
        if self._engine is None:
            return True
        return self._engine.is_battle_over()

    def get_winner(self) -> Optional[int]:
        """
        Get the winning team ID.

        Returns None only when no battle engine is active. Otherwise
        delegates to BattleEngine.get_winner() which returns 0, 1, or -1.

        Returns:
            0: Team 0 wins
            1: Team 1 wins
            -1: Draw (both teams alive, or both eliminated)
            None: No active battle engine
        """
        if self._engine is None:
            return None
        return self._engine.get_winner()

    def get_battle_state(self) -> Dict[str, Any]:
        """
        Get current battle state.

        Returns:
            Dict with battle state information
        """
        if self._engine is None:
            return {
                'is_started': False,
                'is_over': False,
                'tick_count': 0,
                'team_0_ships': [],
                'team_1_ships': [],
                'winner': None,
                'projectile_count': 0
            }

        # Get ships by team from the engine
        team_0 = [s for s in self._engine.ships if s.team_id == 0]
        team_1 = [s for s in self._engine.ships if s.team_id == 1]

        return {
            'is_started': self._is_started,
            'is_over': self._engine.is_battle_over(),
            'tick_count': self._engine.tick_counter,
            'team_0_ships': team_0 if self._is_started else self._team0_ships,
            'team_1_ships': team_1 if self._is_started else self._team1_ships,
            'winner': self._engine.winner,
            'projectile_count': len(self._engine.projectiles),
            'recent_beams': self._engine.recent_beams
        }

    def get_all_ships(self) -> List['Ship']:
        """
        Get all ships in the battle.

        Returns:
            List of all ships
        """
        if self._engine is None:
            return []

        if self._is_started:
            return list(self._engine.ships)
        else:
            return self._team0_ships + self._team1_ships

    def get_alive_ships(self) -> List['Ship']:
        """
        Get all living ships in the battle.

        Returns:
            List of alive ships
        """
        if self._engine is None:
            return []

        return [s for s in self._engine.ships if s.is_alive]

    def get_engine(self) -> Optional[BattleEngine]:
        """
        Get the underlying BattleEngine.

        Returns:
            BattleEngine instance or None
        """
        return self._engine

    def reset(self) -> None:
        """Reset the service state, clearing any active battle."""
        if self._engine is not None:
            self._engine.logger.close()
        self._engine = None
        self._team0_ships = []
        self._team1_ships = []
        self._is_started = False
        self._seed = None
