"""
Shared fixtures for gameplay loop integration tests.
"""
import json
import os
import tempfile
import pytest

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy


class InstantBattleResolver(IBattleResolver):
    """Battle resolver that instantly declares team 0 the winner.

    Skips the full simulation, returning an immediate result where
    team 0 keeps all ships and team 1 loses everything.
    """

    def resolve_battle(self, fleets, modifiers=None, seed=None, registries=None,
                       environmental_effects=None):
        fleet_list = list(fleets)
        survivors = {i: [] for i in range(len(fleet_list))}
        survivors[0] = list(
            fleet_list[0].battle.to_battle_ships(team_id=0, registries=registries)
        )
        return BattleResult(
            winner=0,
            tick_count=1,
            team_survivors=survivors,
        )


@pytest.fixture
def minimal_config():
    """Create minimal game config for testing."""
    config = GameConfig()
    config.galaxy_radius = 500
    config.system_count = 3
    config.players = [
        PlayerConfig(name="Player", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="Enemy", is_human=False, color=(200, 100, 0)),
    ]
    return config


@pytest.fixture
def game_session(minimal_config):
    """Create a game session with minimal configuration."""
    session = GameSession(config=minimal_config)
    return session


@pytest.fixture
def turn_engine(fresh_registries):
    """Create a standalone turn engine for isolated tests.

    Uses InstantBattleResolver to avoid running full combat simulations.
    """
    return TurnEngine(
        battle_resolver=InstantBattleResolver(),
        registries=fresh_registries,
    )


@pytest.fixture
def simple_galaxy():
    """Create a simple galaxy with a few systems."""
    galaxy = Galaxy(radius=500)
    galaxy.generate_systems(count=5, min_dist=100)
    galaxy.generate_warp_lanes()
    return galaxy


@pytest.fixture
def two_empire_setup(simple_galaxy):
    """Create two empires with colonies and fleets."""
    empire1 = Empire(0, "Player", (0, 100, 200))
    empire2 = Empire(1, "Enemy", (200, 100, 0))

    # Give each empire a colony
    systems = list(simple_galaxy.systems.values())
    if len(systems) >= 2:
        if systems[0].planets:
            empire1.add_colony(systems[0].planets[0])
        if systems[1].planets:
            empire2.add_colony(systems[1].planets[0])

    return empire1, empire2, simple_galaxy


@pytest.fixture
def test_savegame_dir():
    """Create temporary savegame directory with test designs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create designs directory structure for empire 0
        designs_dir = os.path.join(tmpdir, "designs", "empire_0")
        os.makedirs(designs_dir, exist_ok=True)

        # Create test ship design
        ship_design = {
            "name": "Test Frigate",
            "vehicle_type": "Ship",
            "vehicle_class": "Frigate",
            "mass": 5000,
            "layers": {
                "core": {
                    "components": [
                        {
                            "id": "basic_reactor",
                            "position": [0, 0]
                        }
                    ]
                }
            }
        }

        with open(os.path.join(designs_dir, "test_frigate.json"), "w") as f:
            json.dump(ship_design, f)

        yield tmpdir
