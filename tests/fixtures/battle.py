"""
Shared battle engine fixtures for tests.

This module provides reusable battle engine fixtures that can be used across all tests,
eliminating boilerplate battle setup code and ensuring consistent test setups.

Usage in tests:
    def test_something(battle_engine):
        # battle_engine is automatically provided by pytest
        assert battle_engine.ships == []

    def test_with_factory():
        # Or use factory directly for custom setup
        from tests.fixtures.battle import create_battle_engine
        engine = create_battle_engine(enable_logging=True)

Available fixtures:
    - battle_engine: Clean BattleEngine with no ships
    - battle_engine_with_ships: BattleEngine with two opposing ships
    - mock_battle_engine: Mock battle engine for unit tests
    - mock_battle_screen: Mock battle screen with engine

PROJ-281 helpers for migrating legacy ``BattleScreen.start(team0, team1)``
callers to the spec-based path:
    - make_minimal_spec: build a minimal ``BattleSpec`` from ``{team_id: [Ship, ...]}``
"""
import os
import pytest
from typing import Dict, List, TYPE_CHECKING
from unittest.mock import Mock

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.battle_spec import BattleSpec
    from game.simulation.entities.ship import Ship

from game.core.paths import Paths
from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
from game.ai.ai_factory import AIControllerFactory
from tests.fixtures.ships import create_test_ship


# =============================================================================
# PROJ-281: make_minimal_spec — build a minimal BattleSpec for test callers
# migrating off the legacy BattleScreen.start(team0, team1) path
# =============================================================================

def make_minimal_spec(
    ships_by_team: Dict[int, List["Ship"]],
    *,
    seed: int = 0,
    max_ticks: int = 1000,
    telemetry_level=None,
) -> "BattleSpec":
    """Build a minimal ``BattleSpec`` for unit tests.

    Replaces the legacy ``BattleScreen.start(team0, team1)`` setup shape.
    Each team gets one TaskForce/Squadron containing all its ships. Ships'
    current position/angle/velocity are used as-is (the caller is
    responsible for positioning). No modifiers, no boundary restrictions,
    no post-battle hook — MINIMAL telemetry by default.

    Args:
        ships_by_team: {team_id: [Ship, ...]} — typically {0: team0_ships, 1: team1_ships}
        seed: Random seed (default 0)
        max_ticks: Duration for the default TickLimitCondition
        telemetry_level: Optional override. Defaults to ``TelemetryLevel.MINIMAL``
            — test callers that need per-ship weapon or hit records can
            pass ``TelemetryLevel.NORMAL`` or ``DETAILED``.

    Returns:
        A fully-populated ``BattleSpec`` ready for
        ``BattleController.start_from_spec(spec, ...)`` or
        ``run_battle(spec, ...)``.
    """
    from game.core.math import Vector2
    from game.simulation.battle_spec import (
        BattleSpec, EntryVector, ShipSpec,
        SquadronSpec, TaskForceSpec, TeamSpec, CombatPolicies,
    )
    from game.simulation.combat.boundary import UnboundedRegion
    from game.simulation.combat.formation import FormationShape, FormationSpec
    from game.simulation.combat.modifier_stack import ModifierStack
    from game.simulation.combat.telemetry import TelemetryLevel
    from game.simulation.systems.battle_end_conditions import TickLimitCondition

    if telemetry_level is None:
        telemetry_level = TelemetryLevel.MINIMAL

    teams = []
    for team_id in sorted(ships_by_team.keys()):
        ships = ships_by_team[team_id]
        ship_specs = tuple(
            ShipSpec(
                instance_id=f"test:{team_id}:{i}",
                design_id=getattr(ship, "design_id", "") or f"test_design_{team_id}_{i}",
                theme_id=getattr(ship, "theme_id", "") or "Federation",
                name=getattr(ship, "name", f"TestShip_{team_id}_{i}"),
                position=Vector2(ship.x, ship.y),
                angle=ship.angle,
                velocity=Vector2(ship.velocity) if hasattr(ship.velocity, 'x') else Vector2(0, 0),
                components=(),
            )
            for i, ship in enumerate(ships)
        )
        squadron = SquadronSpec(
            squadron_id=f"test-sq-{team_id}",
            policies=CombatPolicies(),
            ships=ship_specs,
        )
        task_force = TaskForceSpec(
            task_force_id=f"test-tf-{team_id}",
            formation=FormationSpec(
                shape=FormationShape.LINE_ABREAST,
                spacing=100.0,
            ),
            policies=CombatPolicies(),
            squadrons=(squadron,),
        )
        teams.append(TeamSpec(
            team_id=team_id,
            name=f"TestTeam{team_id}",
            entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
            fleet_hierarchy=(task_force,),
        ))

    return BattleSpec(
        seed=seed,
        telemetry_level=telemetry_level,
        boundary=UnboundedRegion(),
        end_condition=TickLimitCondition(max_ticks=max_ticks),
        absolute_max_ticks=max_ticks * 2,
        teams=tuple(teams),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


def start_battle_screen_with_minimal_spec(
    screen,
    ships_by_team: Dict[int, List["Ship"]],
    *,
    headless: bool = False,
    start_paused: bool = False,
    seed: int = 0,
    max_ticks: int = 1000,
):
    """PROJ-281: drop-in replacement for legacy ``BattleScreen.start(team0, team1)``.

    Encapsulates the 8-line spec-based migration pattern so each of the 47
    test call sites can be a single function call instead of repeating the
    boilerplate:

        # Before (legacy shim):
        scene.start([ship1], [ship2], headless=True)

        # After (spec-based):
        start_battle_screen_with_minimal_spec(
            scene, {0: [ship1], 1: [ship2]}, headless=True,
        )

    End-condition defaults to ``TeamEliminatedCondition`` to match the
    legacy shim's semantics — migrating tests that assert
    ``is_battle_over()`` after killing one team keep the expected
    behavior. ``max_ticks`` still applies as the safety ceiling via
    ``absolute_max_ticks = max_ticks * 2``.

    Args:
        screen: A ``BattleScreen`` instance — the target of ``start_battle``.
        ships_by_team: {team_id: [Ship, ...]} — typically
            ``{0: team0_ships, 1: team1_ships}``.
        headless: Passed into ``BattleConfig``.
        start_paused: Passed into ``BattleConfig``.
        seed: Deterministic seed for the spec and BattleConfig.
        max_ticks: Safety ceiling for the absolute_max_ticks guardrail.

    Returns:
        The running ``BattleController`` (for tests that need to drive
        ``controller.update()`` or query ``controller.service.get_engine()``).
    """
    import dataclasses

    from game.ai.ai_factory import AIControllerFactory
    from game.simulation.battle_config import BattleConfig
    from game.simulation.battle_controller import BattleController
    from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition

    spec = make_minimal_spec(ships_by_team, seed=seed, max_ticks=max_ticks)
    # Legacy-shim parity: TeamEliminatedCondition matches `BattleScreen.start()`.
    spec = dataclasses.replace(spec, end_condition=TeamEliminatedCondition())

    # Flatten ships in the same iteration order the spec compiler uses.
    ordered_ships: List["Ship"] = []
    for team_id in sorted(ships_by_team.keys()):
        ordered_ships.extend(ships_by_team[team_id])

    idx = [0]

    def _ship_builder(ship_spec, team_id):
        _ = ship_spec, team_id
        ship = ordered_ships[idx[0]]
        idx[0] += 1
        return ship

    config = BattleConfig(
        headless=headless,
        start_paused=start_paused,
        seed=seed,
        end_condition=spec.end_condition,
        absolute_max_ticks=spec.absolute_max_ticks,
    )

    controller = BattleController()
    controller.start_from_spec(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=_ship_builder,
        config=config,
    )

    screen.start_battle(controller)
    return controller


# =============================================================================
# Factory Functions
# =============================================================================

def create_battle_engine(enable_logging: bool = False, log_filename: str = None) -> BattleEngine:
    """
    Create a battle engine for testing.

    Args:
        enable_logging: If True, enable battle logging (default: False)
        log_filename: Filename for battle log if logging enabled (default: output/logs/test_battle_log.txt)

    Returns:
        Configured BattleEngine instance
    """
    if log_filename is None:
        log_filename = os.path.join(Paths.LOGS_DIR, "test_battle_log.txt")
    logger = BattleLogger(filename=log_filename, enabled=enable_logging)
    # PROJ-126: Create factory and inject to engine (engine calls set_grid automatically)
    factory = AIControllerFactory()
    engine = BattleEngine(logger=logger, ai_factory=factory)
    return engine


def create_battle_engine_with_ships(
    team0_count: int = 1,
    team1_count: int = 1,
    enable_logging: bool = False,
    *,
    registries: 'GameRegistries',
) -> BattleEngine:
    """
    Create a battle engine with ships already added.

    PROJ-50: Strict DI - registries is required keyword-only argument.

    Args:
        team0_count: Number of ships for team 0
        team1_count: Number of ships for team 1
        enable_logging: If True, enable battle logging
        registries: GameRegistries for DI (required keyword-only)

    Returns:
        BattleEngine with ships configured
    """
    engine = create_battle_engine(enable_logging=enable_logging)

    # Create team 0 ships (left side)
    team0_ships = []
    for i in range(team0_count):
        ship = create_test_ship(
            name=f"Team0Ship{i}",
            x=100 + (i * 50),
            y=400,
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
            registries=registries,
        )
        team0_ships.append(ship)

    # Create team 1 ships (right side)
    team1_ships = []
    for i in range(team1_count):
        ship = create_test_ship(
            name=f"Team1Ship{i}",
            x=700 + (i * 50),
            y=400,
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
            registries=registries,
        )
        team1_ships.append(ship)

    # Start the battle
    engine.start(team0_ships, team1_ships)

    return engine


def create_mock_battle_engine() -> Mock:
    """
    Create a mock battle engine for unit tests.

    Returns a Mock object with common BattleEngine attributes/methods stubbed.

    Returns:
        Mock object mimicking BattleEngine interface
    """
    engine = Mock()
    engine.tick_counter = 0
    engine.ships = []
    engine.projectiles = []
    engine.recent_beams = []
    engine.winner = None
    engine.update = Mock()
    engine.is_battle_over = Mock(return_value=False)
    engine.start = Mock()
    engine.grid = Mock()
    engine.collision_system = Mock()
    engine.projectile_manager = Mock()
    return engine


def create_mock_battle_screen(engine: Mock = None) -> Mock:
    """
    Create a mock battle screen for unit tests.

    Args:
        engine: Mock battle engine to use (creates new one if None)

    Returns:
        Mock object mimicking BattleScreen interface
    """
    if engine is None:
        engine = create_mock_battle_engine()

    scene = Mock()
    scene.engine = engine
    scene.headless_mode = False
    scene.sim_paused = True
    scene.camera = Mock()
    scene.camera.fit_objects = Mock()
    return scene


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def battle_engine():
    """
    Create a clean battle engine with no ships.

    Returns a BattleEngine instance with logging disabled.
    """
    return create_battle_engine()


@pytest.fixture
def battle_engine_with_ships(fresh_registries):
    """
    Create a battle engine with two opposing ships.

    Returns a BattleEngine with one ship per team, ready for combat simulation.

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    return create_battle_engine_with_ships(registries=fresh_registries)


@pytest.fixture
def mock_battle_engine():
    """
    Create a mock battle engine for unit tests.

    Returns a Mock object with common BattleEngine methods stubbed.
    Useful for testing code that depends on BattleEngine without
    needing full simulation.
    """
    return create_mock_battle_engine()


@pytest.fixture
def mock_battle_screen(mock_battle_engine):
    """
    Create a mock battle screen with engine.

    Returns a Mock object with common BattleScreen attributes set.
    The engine attribute is set to the mock_battle_engine fixture.
    """
    return create_mock_battle_screen(engine=mock_battle_engine)
