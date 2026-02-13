"""
BattleConfig and BattleMode - Configuration structures for battle modes.

Extracted from battle_controller.py (PROJ-90) to eliminate circular imports.
Other modules can now import these without importing the full BattleController.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, Any

from game.simulation.systems.battle_end_conditions import BattleEndMode
from game.core.constants import SimulationConstants

# PROJ-113: Removed TYPE_CHECKING import from test_framework to fix layer violation.
# CombatScenario type hint replaced with Any - test_framework is not part of game layers.


class BattleMode(Enum):
    """Types of battle execution modes."""
    MANUAL = "manual"           # Battle Setup screen
    TEST = "test"               # Combat Lab
    STRATEGY = "strategy"       # Strategy layer fleet combat
    HYPOTHETICAL = "hypothetical"  # Planning simulations (isolated)


@dataclass
class BattleConfig:
    """Configuration for a battle instance."""
    mode: BattleMode = BattleMode.MANUAL
    seed: Optional[int] = None
    max_ticks: int = SimulationConstants.DEFAULT_MAX_TICKS
    end_mode: BattleEndMode = BattleEndMode.HP_BASED

    # Mode-specific options
    headless: bool = False
    start_paused: bool = False
    enable_logging: bool = True
    allow_retreat: bool = False
    allow_reinforcements: bool = False

    # For test mode (CombatScenario from test_framework)
    test_scenario: Optional[Any] = None

    # For strategy mode
    source_fleets: Optional[Tuple[Any, Any]] = None

    # For hypothetical mode
    isolated: bool = True  # Never mutate source ships

    # Map bounds for retreat calculations
    map_bounds: Tuple[float, float, float, float] = (
        0, 0, SimulationConstants.DEFAULT_MAP_SIZE, SimulationConstants.DEFAULT_MAP_SIZE
    )
