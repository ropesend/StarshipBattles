"""
BattleStateManager - Handles battle state serialization.

Extracted from BattleController (PROJ-29 SIM-03) to separate concerns.
Manages:
- Capturing battle state (save)
- Restoring battle state (load)
- State data structure management
"""
from typing import Dict, Optional, List, Tuple, Any, TYPE_CHECKING

from game.simulation.battle_state import BattleState
from game.simulation.systems.battle_end_conditions import BattleEndMode
from game.simulation.battle_config import BattleConfig, BattleMode

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class BattleStateManager:
    """
    Manages battle state serialization and deserialization.

    Handles:
    - Capturing current battle state from engine
    - Restoring battle configuration from saved state
    - Extracting ship data from saved state
    - State validation
    """

    def capture_state(
        self,
        engine: Any,
        config: 'BattleConfig'
    ) -> BattleState:
        """
        Capture current battle state from engine.

        Args:
            engine: BattleEngine instance
            config: Current BattleConfig

        Returns:
            BattleState with complete battle state

        Raises:
            RuntimeError: If no engine available
        """
        if not engine:
            raise RuntimeError("No engine available to capture state from")

        return BattleState.capture_from_engine(
            engine,
            mode=config.mode.value,
            seed=config.seed,
            allow_retreat=config.allow_retreat,
            allow_reinforcements=config.allow_reinforcements,
        )

    def restore_config_from_state(
        self,
        state: BattleState
    ) -> BattleConfig:
        """
        Restore battle configuration from saved state.

        Args:
            state: BattleState to restore from

        Returns:
            BattleConfig reconstructed from state

        Raises:
            ValueError: If state has invalid mode
        """
        try:
            mode = BattleMode(state.mode)
        except ValueError:
            raise ValueError(f"Invalid battle mode in state: {state.mode}")

        return BattleConfig(
            mode=mode,
            seed=state.seed,
            max_ticks=state.max_ticks or 100000,
            end_mode=BattleEndMode[state.end_mode],
            allow_retreat=state.allow_retreat,
            allow_reinforcements=state.allow_reinforcements,
        )

    def extract_ships_from_state(
        self,
        state: BattleState
    ) -> Tuple[List['Ship'], Dict[int, str]]:
        """
        Extract ships and ID mapping from saved state.

        Args:
            state: BattleState containing ship states

        Returns:
            Tuple of (list of ships, {id(ship): ship_id} mapping)
        """
        ships = []
        id_map = {}

        for ship_id, ship_state in state.ships.items():
            ship = ship_state.to_ship()
            ships.append(ship)
            id_map[id(ship)] = ship_id

        return ships, id_map

    def validate_state(self, state: Optional[BattleState]) -> bool:
        """
        Validate that a state object is usable.

        Args:
            state: BattleState to validate

        Returns:
            True if state is valid and usable
        """
        if state is None:
            return False

        # Check required attributes
        if not hasattr(state, 'mode'):
            return False
        if not hasattr(state, 'ships'):
            return False

        return True
