"""
Battle Factory Functions - Convenience functions for creating BattleController instances.

PROJ-132: Moved from game/simulation/battle_controller.py to UI layer.
These factory functions import from both Simulation and AI layers, so they must
live in a higher layer (UI) that is allowed to depend on both.

These are convenience functions for common battle configurations. For full
control, use BattleController directly with explicit AI factory injection.
"""
from typing import List, Optional, Any, TYPE_CHECKING

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.ai.ai_factory import AIControllerFactory

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


def _create_default_ai_factory():
    """
    Create a default AIControllerFactory.

    Returns:
        AIControllerFactory instance
    """
    return AIControllerFactory()


def create_manual_battle(
    team1_ships: List['Ship'],
    team2_ships: List['Ship'],
    seed: Optional[int] = None,
    headless: bool = False,
) -> BattleController:
    """
    Create a controller for a manual battle (Battle Setup screen).

    Args:
        team1_ships: Ships for team 0
        team2_ships: Ships for team 1
        seed: Random seed for determinism
        headless: Run without rendering

    Returns:
        Configured and started BattleController
    """
    controller = BattleController(ai_factory=_create_default_ai_factory())

    config = BattleConfig(
        mode=BattleMode.MANUAL,
        seed=seed,
        headless=headless,
    )

    controller.configure(config)
    controller.add_ships(team1_ships, 0)
    controller.add_ships(team2_ships, 1)
    controller.start()

    return controller


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
    controller = BattleController(ai_factory=_create_default_ai_factory())

    config = BattleConfig(
        mode=BattleMode.TEST,
        seed=seed,
        headless=headless,
        test_scenario=scenario,
        max_ticks=scenario.max_ticks if hasattr(scenario, 'max_ticks') else 100000,
    )

    controller.configure(config)

    return controller


def create_strategy_battle(
    fleet1: Any,
    fleet2: Any,
    seed: Optional[int] = None,
    allow_retreat: bool = True,
) -> BattleController:
    """
    Create a controller for a strategy layer fleet battle.

    Args:
        fleet1: First fleet (team 0)
        fleet2: Second fleet (team 1)
        seed: Random seed for determinism
        allow_retreat: Allow ships to retreat

    Returns:
        Configured BattleController (ships not yet added - call to_battle_ships on fleets)
    """
    controller = BattleController(ai_factory=_create_default_ai_factory())

    config = BattleConfig(
        mode=BattleMode.STRATEGY,
        seed=seed,
        headless=True,
        allow_retreat=allow_retreat,
        source_fleets=(fleet1, fleet2),
    )

    controller.configure(config)

    return controller


def create_hypothetical_battle(
    ships1: List['Ship'],
    ships2: List['Ship'],
    seed: Optional[int] = None,
) -> BattleController:
    """
    Create a controller for a hypothetical (what-if) battle.

    Ships are deep-cloned to ensure no mutation of originals.

    Args:
        ships1: Ships for team 0 (will be cloned)
        ships2: Ships for team 1 (will be cloned)
        seed: Random seed for determinism

    Returns:
        Configured and started BattleController
    """
    controller = BattleController(ai_factory=_create_default_ai_factory())

    config = BattleConfig(
        mode=BattleMode.HYPOTHETICAL,
        seed=seed,
        headless=True,
        isolated=True,
    )

    controller.configure(config)

    # Clone ships to ensure isolation
    from game.simulation.entities.ship_serialization import ShipSerializer

    cloned1 = []
    for ship in ships1:
        data = ShipSerializer.to_dict(ship)
        cloned = ShipSerializer.from_dict(data, registries=ship.registries)
        cloned.x, cloned.y = ship.x, ship.y
        cloned1.append(cloned)

    cloned2 = []
    for ship in ships2:
        data = ShipSerializer.to_dict(ship)
        cloned = ShipSerializer.from_dict(data, registries=ship.registries)
        cloned.x, cloned.y = ship.x, ship.y
        cloned2.append(cloned)

    controller.add_ships(cloned1, 0)
    controller.add_ships(cloned2, 1)
    controller.start()

    return controller
