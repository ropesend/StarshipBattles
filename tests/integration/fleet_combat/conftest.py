"""
Shared fixtures for fleet combat tests.

PROJ-50: Updated to use fresh_registries for strict DI.
"""

import pytest

from game.simulation.battle_controller import BattleController, BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleService
from tests.fixtures.ships import create_test_ship


@pytest.fixture
def battle_service():
    """Create a fresh BattleService."""
    return BattleService()


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
