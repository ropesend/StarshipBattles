"""Integration tests for PROJ-219: Galaxy wiring in GameInitializer and GameSession.

Verifies that:
- GameInitializer.initialize() sets galaxy on all empires
- GameSession.from_dict() sets galaxy on all empires after deserialization
- Fleets added after load auto-register with galaxy
"""
import pytest

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance


@pytest.fixture
def small_game_session():
    """Create a small game session for testing."""
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="Player1", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="Player2", is_human=False, color=(200, 100, 0)),
    ]
    return GameSession(config=config)


class TestGameInitializerGalaxyWiring:
    """Tests for GameInitializer setting galaxy on empires."""

    def test_game_initializer_sets_galaxy_on_empires(self, small_game_session):
        """After GameInitializer.initialize(), all empires have _galaxy set."""
        session = small_game_session
        for empire in session.empires:
            assert empire._galaxy is not None, (
                f"Empire '{empire.name}' has no galaxy reference after initialization"
            )
            assert empire._galaxy is session.galaxy, (
                f"Empire '{empire.name}' galaxy reference doesn't match session galaxy"
            )

    def test_fleet_added_after_init_auto_registers(self, small_game_session, fresh_registries):
        """Fleets added after init are automatically registered with galaxy."""
        session = small_game_session
        empire = session.empires[0]

        fleet = Fleet(9999, empire.id, HexCoord(0, 0), speed=15.0)
        fleet.ships = [make_mock_ship_instance("Scout", empire.id, registries=fresh_registries)]
        empire.add_fleet(fleet)

        # Fleet should be queryable via galaxy registry
        found = session.galaxy.get_fleet_by_id(9999)
        assert found is fleet, "Fleet added after init should be auto-registered with galaxy"


class TestGameSessionFromDictGalaxyWiring:
    """Tests for GameSession.from_dict() setting galaxy on empires."""

    def test_game_session_from_dict_sets_galaxy_on_empires(self, small_game_session):
        """After from_dict(), all empires have _galaxy set."""
        session = small_game_session

        # Serialize and deserialize
        data = session.to_dict()
        restored = GameSession.from_dict(data)

        for empire in restored.empires:
            assert empire._galaxy is not None, (
                f"Empire '{empire.name}' has no galaxy reference after from_dict"
            )
            assert empire._galaxy is restored.galaxy, (
                f"Empire '{empire.name}' galaxy reference doesn't match restored galaxy"
            )

    def test_new_fleet_after_load_registers_automatically(self, small_game_session, fresh_registries):
        """Fleets added after save/load auto-register with galaxy."""
        session = small_game_session

        # Serialize and deserialize
        data = session.to_dict()
        restored = GameSession.from_dict(data)

        empire = restored.empires[0]
        fleet = Fleet(8888, empire.id, HexCoord(5, 5), speed=15.0)
        fleet.ships = [make_mock_ship_instance("Scout", empire.id, registries=fresh_registries)]
        empire.add_fleet(fleet)

        # Fleet should be queryable via galaxy registry
        found = restored.galaxy.get_fleet_by_id(8888)
        assert found is fleet, "Fleet added after load should be auto-registered with galaxy"
