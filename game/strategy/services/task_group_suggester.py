"""
Task group suggester — auto-suggests fleet organization.

Examines ship design roles and capabilities to suggest a fleet hierarchy
(TaskForces and Squadrons) for combat organization.

The suggestion is a one-shot function: call suggest_task_groups(ships)
to get a list of TaskForces. The player can accept, modify, or discard.
"""

import logging
from typing import List, Dict, TYPE_CHECKING

from game.strategy.data.fleet_hierarchy import BattleRole, CombatPolicy
from game.strategy.data.task_force import TaskForce
from game.strategy.data.squadron import Squadron

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance

logger = logging.getLogger(__name__)

# Role -> battle role mapping for grouping
_ROLE_TO_BATTLE_ROLE: Dict[str, BattleRole] = {
    "line_combatant": BattleRole.MAIN_BODY,
    "assault_ship": BattleRole.MAIN_BODY,
    "command_ship": BattleRole.MAIN_BODY,
    "fleet_escort": BattleRole.SCREEN,
    "interceptor": BattleRole.SCREEN,
    "missile_platform": BattleRole.MAIN_BODY,
    "raider": BattleRole.VANGUARD,
    "scout": BattleRole.VANGUARD,
    "carrier": BattleRole.RESERVE,
    "support_ship": BattleRole.RESERVE,
}

# Battle role -> default targeting policy
_ROLE_TO_TARGETING: Dict[BattleRole, str] = {
    BattleRole.MAIN_BODY: "focus_strongest",
    BattleRole.SCREEN: "anti_fighter",
    BattleRole.VANGUARD: "focus_nearest",
    BattleRole.RESERVE: "distributed",
}

# Battle role -> default movement policy
_ROLE_TO_MOVEMENT: Dict[BattleRole, str] = {
    BattleRole.MAIN_BODY: "hold_range",
    BattleRole.SCREEN: "advance",
    BattleRole.VANGUARD: "advance",
    BattleRole.RESERVE: "hold_position",
}

# Battle role -> suggested group name
_ROLE_TO_NAME: Dict[BattleRole, str] = {
    BattleRole.MAIN_BODY: "Battle Line",
    BattleRole.SCREEN: "Escort Screen",
    BattleRole.VANGUARD: "Vanguard",
    BattleRole.RESERVE: "Support Group",
    BattleRole.FLANKER_LEFT: "Left Flank",
    BattleRole.FLANKER_RIGHT: "Right Flank",
}


def suggest_task_groups(ships: List['ShipInstance']) -> List[TaskForce]:
    """Suggest fleet organization based on ship design roles.

    Groups ships by their effective_role into TaskForces with
    appropriate battle roles and default policies.

    Args:
        ships: All ships in the fleet (flat list).

    Returns:
        List of suggested TaskForces. Each contains a Squadron
        with the grouped ships.
    """
    if not ships:
        return []

    # Group ships by their battle role bucket
    buckets: Dict[BattleRole, List['ShipInstance']] = {}
    for ship in ships:
        role = ship.effective_role or "line_combatant"
        battle_role = _ROLE_TO_BATTLE_ROLE.get(role, BattleRole.MAIN_BODY)

        if battle_role not in buckets:
            buckets[battle_role] = []
        buckets[battle_role].append(ship)

    # Create a TaskForce for each non-empty bucket
    task_forces: List[TaskForce] = []
    for battle_role, group_ships in buckets.items():
        name = _ROLE_TO_NAME.get(battle_role, "Task Force")
        targeting = _ROLE_TO_TARGETING.get(battle_role)
        movement = _ROLE_TO_MOVEMENT.get(battle_role)

        tf = TaskForce(
            name=name,
            policy=CombatPolicy(targeting=targeting, movement=movement),
            battle_role=battle_role,
        )

        # Create a squadron within the task force for the ships
        sq = Squadron(
            name=name,
            battle_role=battle_role,
        )
        for ship in group_ships:
            sq.add_ship(ship)

        tf.add_squadron(sq)
        task_forces.append(tf)

    # Sort: MAIN_BODY first, then SCREEN, then others
    role_order = {
        BattleRole.MAIN_BODY: 0,
        BattleRole.SCREEN: 1,
        BattleRole.VANGUARD: 2,
        BattleRole.FLANKER_LEFT: 3,
        BattleRole.FLANKER_RIGHT: 4,
        BattleRole.RESERVE: 5,
    }
    task_forces.sort(key=lambda tf: role_order.get(tf.battle_role, 99))

    return task_forces
