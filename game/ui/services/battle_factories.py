"""
Battle Factory Functions - Convenience functions for creating BattleController instances.

PROJ-132: Moved from game/simulation/battle_controller.py to UI layer.
These factory functions import from both Simulation and AI layers, so they must
live in a higher layer (UI) that is allowed to depend on both.

These are convenience functions for common battle configurations. For full
control, use BattleController directly with explicit AI factory injection.

PROJ-141: DUP-UI2-002, DUP-UI2-006 remediation - extracted helper functions
to reduce duplication across factory functions.
"""
from typing import List, Optional, Any, TYPE_CHECKING

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.ai.ai_factory import AIControllerFactory
from game.simulation.entities.ship_serialization import ShipSerializer

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


def _create_default_ai_factory() -> AIControllerFactory:
    """
    Create a default AIControllerFactory.

    Returns:
        AIControllerFactory instance
    """
    return AIControllerFactory()


def _create_controller_with_config(config: BattleConfig) -> BattleController:
    """
    Create and configure a BattleController with the given config.

    This helper reduces boilerplate across factory functions.
    PROJ-141: DUP-UI2-002 remediation.

    Args:
        config: Battle configuration

    Returns:
        Configured (but not started) BattleController
    """
    controller = BattleController(ai_factory=_create_default_ai_factory())
    controller.configure(config)
    return controller


def create_started_battle_controller(
    config: BattleConfig,
    team0_ships: List['Ship'],
    team1_ships: List['Ship'],
    *,
    ai_factory: Optional[AIControllerFactory] = None,
) -> BattleController:
    """
    Create, configure, populate, and start a battle controller.

    This centralizes the common battle bootstrap flow shared by UI entry
    points so startup behavior stays consistent.
    """
    controller = BattleController(ai_factory=ai_factory or _create_default_ai_factory())
    controller.configure(config)
    controller.add_ships(team0_ships, 0)
    controller.add_ships(team1_ships, 1)
    controller.start()
    return controller


def _clone_ships(ships: List['Ship']) -> List['Ship']:
    """
    Create deep copies of ships via serialization.

    This ensures complete isolation - cloned ships share no state
    with originals. Position (x, y) is preserved on the clones.
    PROJ-141: DUP-UI2-006 remediation.

    Args:
        ships: Ships to clone

    Returns:
        List of cloned ships with preserved positions
    """
    if not ships:
        return []

    cloned = []
    for ship in ships:
        data = ShipSerializer.to_dict(ship)
        clone = ShipSerializer.from_dict(data, registries=ship.registries)
        clone.x, clone.y = ship.x, ship.y
        cloned.append(clone)

    return cloned


def create_manual_battle(
    team0_ships: List['Ship'],
    team1_ships: List['Ship'],
    seed: Optional[int] = None,
    headless: bool = False,
) -> BattleController:
    """
    Create a controller for a manual battle (Battle Setup screen).

    Args:
        team0_ships: Ships for team 0
        team1_ships: Ships for team 1
        seed: Random seed for determinism
        headless: Run without rendering

    Returns:
        Configured and started BattleController
    """
    config = BattleConfig(
        mode=BattleMode.MANUAL,
        seed=seed,
        headless=headless,
    )

    return create_started_battle_controller(config, team0_ships, team1_ships)


def create_test_battle(
    scenario: 'CombatScenario',
    headless: bool = True,
    seed: Optional[int] = None,
) -> BattleController:
    """
    Create a controller for a Combat Lab test.

    Args:
        scenario: Test scenario to run
        headless: Run without rendering
        seed: Random seed for determinism

    Returns:
        Configured BattleController (not started - scenario handles setup)
    """
    config = BattleConfig(
        mode=BattleMode.TEST,
        seed=seed,
        headless=headless,
        test_scenario=scenario,
    )

    return _create_controller_with_config(config)


def create_strategy_battle(
    fleet0: Any,
    fleet1: Any,
    seed: Optional[int] = None,
    allow_retreat: bool = True,
) -> BattleController:
    """
    Create a controller for a strategy layer fleet battle.

    Args:
        fleet0: Fleet for team 0
        fleet1: Fleet for team 1
        seed: Random seed for determinism
        allow_retreat: Allow ships to retreat

    Returns:
        Configured BattleController (ships not yet added - call to_battle_ships on fleets)
    """
    config = BattleConfig(
        mode=BattleMode.STRATEGY,
        seed=seed,
        headless=True,
        allow_retreat=allow_retreat,
    )

    return _create_controller_with_config(config)


def create_hypothetical_battle(
    ships0: List['Ship'],
    ships1: List['Ship'],
    seed: Optional[int] = None,
) -> BattleController:
    """
    Create a controller for a hypothetical (what-if) battle.

    Ships are deep-cloned to ensure no mutation of originals.

    Args:
        ships0: Ships for team 0 (will be cloned)
        ships1: Ships for team 1 (will be cloned)
        seed: Random seed for determinism

    Returns:
        Configured and started BattleController
    """
    config = BattleConfig(
        mode=BattleMode.HYPOTHETICAL,
        seed=seed,
        headless=True,
    )

    # Clone ships to ensure isolation (PROJ-141: DUP-UI2-006)
    return create_started_battle_controller(
        config,
        _clone_ships(ships0),
        _clone_ships(ships1),
    )
