"""BattleConfig - operational configuration for a `BattleController` instance.

PROJ-269 Phase 6 reshape: `BattleMode` enum + the per-mode variant fields
(`team_modifiers`, `global_modifiers`, `environmental_effects`,
`source_fleets`, `per_tick_callback`) were deleted. All variant behavior
moved to `BattleSpec` / `run_battle`. What remains here is a thin
operational-options bag for the visual-mode `BattleController` flow that
`BattleScreen` still drives per-frame (until Task 6.9 migrates that path
through `run_battle` as well).

`ReturnDestination` is also retained because the post-battle UI flow
(`BattleScreen._on_battle_ended()` → `app._return_to(destination)`) still
keys off it.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, Any, TYPE_CHECKING

from game.core.constants import SimulationConstants

if TYPE_CHECKING:
    from game.simulation.systems.battle_end_conditions import IEndCondition


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
    """Operational configuration for a `BattleController` instance.

    Carries only fields that affect HOW a battle runs (visual vs
    headless, paused vs ticking, what scene to return to). Everything
    that affects WHAT the battle is — ships, modifiers, end conditions,
    boundary, formations — lives on `BattleSpec` and flows through
    `run_battle(spec)`.
    """
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

    # Battle features (visual-mode toggles).
    allow_retreat: bool = False
    allow_reinforcements: bool = False

    # Caller metadata — stored on config for callers to read back after battle.
    # The simulator does NOT use this field.
    test_scenario: Optional[Any] = None   # Combat Lab: scenario with validate()

    # Map bounds for retreat calculations.
    map_bounds: Tuple[float, float, float, float] = (
        0, 0, SimulationConstants.DEFAULT_MAP_SIZE, SimulationConstants.DEFAULT_MAP_SIZE
    )
