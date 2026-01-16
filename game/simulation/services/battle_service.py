"""
BattleService - Abstraction layer between UI and BattleEngine.

This service handles battle creation, ship management, and simulation control,
providing a clean interface for battle screens.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, TYPE_CHECKING

from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
from game.simulation.systems.battle_end_conditions import BattleEndCondition, BattleEndMode
from game.core.logger import log_error, log_info

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


@dataclass
class BattleResult:
    """Result object for battle service operations."""
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
        enable_logging: bool = False
    ) -> BattleResult:
        """
        Create a new battle instance.

        Args:
            seed: Random seed for reproducible battles
            enable_logging: Whether to enable battle logging to file

        Returns:
            BattleResult with the created engine
        """
        try:
            logger = BattleLogger(enabled=enable_logging)
            self._engine = BattleEngine(logger=logger)
            self._team0_ships = []
            self._team1_ships = []
            self._is_started = False
            self._seed = seed

            return BattleResult(
                success=True,
                engine=self._engine
            )

        except Exception as e:
            log_error(f"Failed to create battle: {e}")
            return BattleResult(
                success=False,
                errors=[str(e)]
            )

    def add_ship(
        self,
        ship: 'Ship',
        team_id: int
    ) -> BattleResult:
        """
        Add a ship to the battle.

        Args:
            ship: Ship to add
            team_id: Team identifier (0 or 1)

        Returns:
            BattleResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle - call create_battle() first")
            return BattleResult(success=False, errors=errors)

        if self._is_started:
            errors.append("Cannot add ships after battle has started")
            return BattleResult(success=False, errors=errors)

        # Update ship's team_id
        ship.team_id = team_id

        # Add to appropriate team list
        if team_id == 0:
            self._team0_ships.append(ship)
        else:
            self._team1_ships.append(ship)

        return BattleResult(success=True, engine=self._engine)

    def remove_ship(
        self,
        ship: 'Ship'
    ) -> BattleResult:
        """
        Remove a ship from the battle (before start).

        Args:
            ship: Ship to remove

        Returns:
            BattleResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle")
            return BattleResult(success=False, errors=errors)

        if self._is_started:
            errors.append("Cannot remove ships after battle has started")
            return BattleResult(success=False, errors=errors)

        removed = False
        if ship in self._team0_ships:
            self._team0_ships.remove(ship)
            removed = True
        elif ship in self._team1_ships:
            self._team1_ships.remove(ship)
            removed = True

        if not removed:
            errors.append(f"Ship '{ship.name}' not found in battle")
            return BattleResult(success=False, errors=errors)

        return BattleResult(success=True, engine=self._engine)

    def start_battle(
        self,
        end_mode: BattleEndMode = BattleEndMode.HP_BASED,
        max_ticks: Optional[int] = None
    ) -> BattleResult:
        """
        Start the battle simulation.

        Args:
            end_mode: Battle end condition mode
            max_ticks: Maximum ticks for time-based battles

        Returns:
            BattleResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle - call create_battle() first")
            return BattleResult(success=False, errors=errors)

        if self._is_started:
            errors.append("Battle already started")
            return BattleResult(success=False, errors=errors)

        if not self._team0_ships and not self._team1_ships:
            errors.append("Cannot start battle with no ships")
            return BattleResult(success=False, errors=errors)

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

        log_info(f"Battle started: {len(self._team0_ships)} vs {len(self._team1_ships)} ships")

        return BattleResult(success=True, engine=self._engine)

    def update(self) -> BattleResult:
        """
        Run one simulation tick.

        Returns:
            BattleResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle")
            return BattleResult(success=False, errors=errors)

        if not self._is_started:
            errors.append("Battle not started - call start_battle() first")
            return BattleResult(success=False, errors=errors)

        self._engine.update()

        return BattleResult(success=True, engine=self._engine)

    def run_ticks(self, count: int) -> BattleResult:
        """
        Run multiple simulation ticks.

        Args:
            count: Number of ticks to run

        Returns:
            BattleResult indicating success/failure
        """
        errors = []

        if self._engine is None:
            errors.append("No active battle")
            return BattleResult(success=False, errors=errors)

        if not self._is_started:
            errors.append("Battle not started - call start_battle() first")
            return BattleResult(success=False, errors=errors)

        for _ in range(count):
            if self._engine.is_battle_over():
                break
            self._engine.update()

        return BattleResult(success=True, engine=self._engine)

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

        Returns:
            Winning team ID (0 or 1), -1 for draw, or None if no engine
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
