"""
BattleConfig and BattleMode - Configuration structures for battle modes.

Extracted from battle_controller.py (PROJ-90) to eliminate circular imports.
Other modules can now import these without importing the full BattleController.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, Any, TYPE_CHECKING

from game.core.constants import SimulationConstants

if TYPE_CHECKING:
    from game.simulation.systems.battle_end_conditions import IEndCondition


class BattleMode(Enum):
    """Types of battle execution modes.

    Used as a label for logging and UI display, NOT as a behavior switch.
    All battle behavior is configured through BattleConfig fields.
    """
    MANUAL = "manual"           # Battle Setup screen
    TEST = "test"               # Combat Lab
    STRATEGY = "strategy"       # Strategy layer fleet combat
    HYPOTHETICAL = "hypothetical"  # Planning simulations (isolated)


class ReturnDestination(Enum):
    """Where to navigate after the battle ends."""
    BATTLE_SETUP = "battle_setup"
    TEST_LAB = "test_lab"
    STRATEGY = "strategy"


def _default_end_condition() -> 'IEndCondition':
    from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition
    return TeamEliminatedCondition()


@dataclass
class BattleConfig:
    """Configuration for a battle instance.

    The battle simulator is a pure engine — it receives ships, runs the
    simulation, and reports results. BattleConfig contains ONLY data
    that the simulator needs. Caller-specific concerns (test validation,
    fleet updates) are handled by the caller after the battle.
    """
    mode: BattleMode = BattleMode.MANUAL
    seed: Optional[int] = None
    end_condition: Any = field(default_factory=_default_end_condition)
    absolute_max_ticks: int = SimulationConstants.ABSOLUTE_MAX_TICKS

    # Entry/exit
    return_destination: ReturnDestination = ReturnDestination.BATTLE_SETUP
    show_results: bool = True

    # Simulation options
    headless: bool = False
    start_paused: bool = False
    enable_logging: bool = True

    # Battle features — available to ALL modes
    allow_retreat: bool = False
    allow_reinforcements: bool = False
    environmental_effects: Optional[Any] = None

    # Ship isolation (clone ships to prevent mutation of originals)
    isolated: bool = True

    # Caller metadata — stored on config for callers to read back after battle.
    # The simulator does NOT use these fields.
    test_scenario: Optional[Any] = None   # Combat Lab: scenario with validate()
    source_fleets: Optional[Tuple[Any, Any]] = None  # Strategy: fleet references

    # Map bounds for retreat calculations
    map_bounds: Tuple[float, float, float, float] = (
        0, 0, SimulationConstants.DEFAULT_MAP_SIZE, SimulationConstants.DEFAULT_MAP_SIZE
    )
