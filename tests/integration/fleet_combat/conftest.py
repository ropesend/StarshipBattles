"""
Shared fixtures for fleet combat tests.

PROJ-50: Updated to use fresh_registries for strict DI.
PROJ-126: Updated to inject AIControllerFactory.
"""

import pytest

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleService
from game.ai.ai_factory import AIControllerFactory
from tests.fixtures.ships import create_test_ship


@pytest.fixture
def ai_factory():
    """Create an AIControllerFactory for tests."""
    return AIControllerFactory()


@pytest.fixture
def battle_service(ai_factory):
    """Create a fresh BattleService with AI factory injection."""
    svc = BattleService()
    # Store factory for injection
    svc._test_ai_factory = ai_factory

    # Wrap create_battle to inject factory
    original_create_battle = svc.create_battle

    def wrapped_create_battle(*args, **kwargs):
        if 'ai_factory' not in kwargs:
            kwargs['ai_factory'] = svc._test_ai_factory
        return original_create_battle(*args, **kwargs)

    svc.create_battle = wrapped_create_battle
    return svc


@pytest.fixture
def two_ship_teams(fresh_registries):
    """Create two teams of ships for battle testing.

    Ships are positioned close enough for weapons to engage (within ~2000 units).
    """
    team1 = [
        create_test_ship(
            name="Team1_Attacker",
            x=500,
            y=400,
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
    ]
    team2 = [
        create_test_ship(
            name="Team2_Defender",
            x=2000,
            y=400,
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
    ]
    return team1, team2


@pytest.fixture
def fleet_battle_teams(fresh_registries):
    """Create multi-ship fleets for larger scale testing.

    Ships are positioned close enough for weapons to engage.
    """
    team1 = [
        create_test_ship(
            name=f"Fleet1_Ship{i}",
            x=500 + (i * 200),
            y=400 + (i * 100),
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
            add_shields=1,
            registries=fresh_registries,
        )
        for i in range(3)
    ]
    team2 = [
        create_test_ship(
            name=f"Fleet2_Ship{i}",
            x=2000 + (i * 200),
            y=400 + (i * 100),
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
            add_shields=1,
            registries=fresh_registries,
        )
        for i in range(3)
    ]
    return team1, team2
