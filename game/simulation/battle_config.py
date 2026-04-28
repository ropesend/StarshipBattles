"""BattleConfig - operational configuration for a `BattleController` instance.

PROJ-269 Phase 6 reshape: `BattleMode` enum + the per-mode variant fields
(`team_modifiers`, `global_modifiers`, `environmental_effects`,
`source_fleets`, `per_tick_callback`) were deleted. All variant behavior
moved to `BattleSpec` / `run_battle`. What remains here is a thin
operational-options bag for the visual-mode `BattleController` flow that
`BattleScreen` still drives per-frame.

PROJ-270 Task 5.4: `map_bounds` tuple deleted. Arena boundary is
carried on `BattleSpec.boundary` (`BoundaryRegion` ADT — origin-centered
rect, circle, or unbounded). `BattleController.configure(config, spec)`
consumes it directly.

PROJ-270 Phase 10: `ReturnDestination` re-export deleted. Import from
`game.core.return_destination` directly.
"""
from dataclasses import dataclass, field
from typing import Optional, Any, TYPE_CHECKING

from game.core.constants import SimulationConstants
from game.core.return_destination import ReturnDestination  # Used by default= below

if TYPE_CHECKING:
    from game.simulation.systems.battle_end_conditions import IEndCondition


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

    # PROJ-312 — Replay playback flags.
    # When `replay_mode` is True the BattleScreen renders a "REPLAY MODE"
    # badge, suppresses the post-battle outcome flow (returns to the Event
    # Log on exit), and capture is skipped (Phase 3 honors this via the
    # spec compiler passing `capture_context=None`). Production wiring sets
    # `replay_id` and `captured_telemetry_level` so the screen can display
    # provenance + emit a divergence warning when the runtime telemetry
    # level differs from what was captured.
    replay_mode: bool = False
    replay_id: Optional[str] = None
    captured_telemetry_level: Optional[Any] = None
