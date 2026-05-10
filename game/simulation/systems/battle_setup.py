"""Battle-setup helpers — initial start-of-battle state assembly.

PROJ-382 Phase 5: extracted from ``battle_engine.py`` to bring the parent
module under the 500 LOC ceiling.  Three free functions implement the
``start_teams`` -> ``_initialize_start_state`` -> ``_log_initial_status``
flow that fires once per battle to seed the engine's ship list, AI
controllers, RNG, end condition, and aura manager.

The functions take an explicit ``engine`` parameter rather than ``self``
because they were extracted from ``BattleEngine`` methods; the engine
provides all the collaborator references (ships, ai_controllers,
projectile_manager, collision_system, aura_manager, logger,
combat_events).  This keeps the module free of a circular dependency
on ``battle_engine``.
"""
from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Dict, List, Optional

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.simulation.combat.damage_calculator import DamageCalculator
from game.simulation.systems.battle_end_conditions import (
    IEndCondition,
    TeamEliminatedCondition,
)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.interfaces.ai_controller import IAIController
    from game.simulation.systems.battle_engine import BattleEngine


logger = logging.getLogger(__name__)


def initialize_start_state(
    engine: "BattleEngine",
    seed: Optional[int],
    end_condition: Optional[IEndCondition],
    absolute_max_ticks: Optional[int],
) -> None:
    """Shared start-of-battle state reset for ``start`` / ``start_teams``."""
    engine.rng = random.Random(seed)
    engine.collision_system.rng = engine.rng
    from game.simulation.entities.ship_combat_engine import ShipCombatEngine
    ShipCombatEngine._damage_calculator = DamageCalculator(rng=engine.rng)

    engine.ships = []
    engine.ai_controllers = []
    engine.projectile_manager.clear()
    engine.recent_beams = []
    engine.tick_counter = 0
    engine.winner = None
    engine.retreated_ships = []

    engine.end_condition = end_condition if end_condition is not None else TeamEliminatedCondition()
    if absolute_max_ticks is not None:
        engine._absolute_max_ticks = absolute_max_ticks


def start_teams(
    engine: "BattleEngine",
    teams: Dict[int, List["Ship"]],
    *,
    seed: Optional[int] = None,
    end_condition: Optional[IEndCondition] = None,
    absolute_max_ticks: Optional[int] = None,
    ai_controllers: Optional[List["IAIController"]] = None,
) -> None:
    """N-team battle setup.  Each key in ``teams`` is the team_id."""
    initialize_start_state(engine, seed, end_condition, absolute_max_ticks)

    # Assign team_ids + append ships.
    ships_per_team: Dict[int, List["Ship"]] = {}
    for team_id, team_ships in teams.items():
        if not isinstance(team_ships, list):
            team_ships = [team_ships]
        for s in team_ships:
            s.team_id = team_id
            engine.ships.append(s)
        ships_per_team[team_id] = list(team_ships)

    if ai_controllers is not None:
        engine.ai_controllers = list(ai_controllers)
    elif engine._ai_factory is not None:
        # PROJ-312: forward the per-battle seeded RNG to the factory so
        # every controller it builds (and every behavior they own —
        # ErraticBehavior in particular) consumes a deterministic RNG.
        # Pattern #18 (Per-Battle RNG).
        engine._ai_factory.set_rng(engine.rng)
        # Phase 3 Task 3.3: AI factory's ``enemy_team_id`` is a 2-team
        # artifact. For N teams, we pass any non-self team id as a hint —
        # Task 3.4 refines the AI to scan all enemies.
        engine.ai_controllers = []
        all_team_ids = list(ships_per_team.keys())
        for team_id, team_ships in ships_per_team.items():
            enemy_candidates = [tid for tid in all_team_ids if tid != team_id]
            enemy_hint = enemy_candidates[0] if enemy_candidates else team_id
            controllers = engine._ai_factory.create_for_ships(
                team_ships, enemy_team_id=enemy_hint
            )
            engine.ai_controllers.extend(controllers)
    else:
        raise ValidationException(
            "BattleEngine requires AI configuration",
            code=ErrorCode.MISSING_DEPENDENCY.value,
            context={"missing": "ai_controllers and ai_factory", "operation": "start_teams"}
        )

    for s in engine.ships:
        engine._initialize_ship(s)
    # PROJ-269 Phase 5.5: thread the engine's modifier_stack (populated by
    # run_battle from spec) into the aura manager for effect application.
    engine.aura_manager.initialize(engine.ships, modifier_stack=engine.modifier_stack)
    engine.logger.start_session()
    engine.logger.log(
        f"Battle started: {sum(len(t) for t in teams.values())} ships "
        f"across {len(teams)} teams"
    )
    log_initial_status(engine)


def log_initial_status(engine: "BattleEngine") -> None:
    """Per-ship initial-state log line emitted at battle start."""
    for s in engine.ships:
        fuel = s.resources.get_value("fuel")
        status_msg = (
            f"Ship '{s.name}' (Team {s.team_id}): HP={s.hp}/{s.max_hp} "
            f"Mass={s.mass} Thrust={s.total_thrust} Fuel={fuel} "
            f"TurnSpeed={s.turn_speed:.2f} MaxSpeed={s.max_speed:.2f}"
        )
        engine.logger.log(status_msg)
        logger.info(status_msg)
        # Removed Derelict Warning
        if s.total_thrust <= 0:
            engine.logger.log(f"WARNING: {s.name} has NO THRUST!")
        if s.turn_speed <= 0.01:
            engine.logger.log(f"WARNING: {s.name} has LOW/NO TURN SPEED ({s.turn_speed:.4f})!")
