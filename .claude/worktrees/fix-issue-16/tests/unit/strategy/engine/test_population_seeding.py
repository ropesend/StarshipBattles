"""Tests for initial population seeding in game session and quickstart."""
import pytest
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.data.race_config import RaceConfig
from game.strategy.quickstart_builder import QuickstartBuilder


class TestHomeColonyPopulationSeeding:
    """Test population seeding when game session is created."""

    def test_home_colony_has_initial_population(self):
        """Home colony should have population after game initialization."""
        # Create a race config for the player
        race_config = RaceConfig(race_id="test_race", name="Test Race")

        player = PlayerConfig(
            name="Test Empire",
            theme="Federation",
            is_human=True,
            race_config=race_config
        )

        config = GameConfig(
            players=[player],
            galaxy_radius=4000,
            system_count=5
        )

        session = GameSession(config=config)
        empire = session.empires[0]

        # Empire should have a home colony
        assert len(empire.colonies) > 0, "Empire should have at least one colony"

        home_colony = empire.colonies[0]

        # Home colony should have max population
        assert home_colony.total_population == home_colony.max_population, \
            "Home colony should be at max population"

    def test_initial_population_correct_race_id(self):
        """Initial population should match the empire's race_id."""
        race_config = RaceConfig(race_id="humans", name="Humans")

        player = PlayerConfig(
            name="Human Empire",
            theme="Federation",
            is_human=True,
            race_config=race_config
        )

        config = GameConfig(
            players=[player],
            galaxy_radius=4000,
            system_count=5
        )

        session = GameSession(config=config)
        empire = session.empires[0]
        home_colony = empire.colonies[0]

        # Check that population has correct race_id
        assert len(home_colony.populations) == 1, "Should have exactly one species"
        assert home_colony.populations[0].race_id == "humans"

    def test_initial_happiness_is_positive(self):
        """Initial population should have positive happiness."""
        race_config = RaceConfig(race_id="test_race", name="Test Race")

        player = PlayerConfig(
            name="Test Empire",
            theme="Federation",
            is_human=True,
            race_config=race_config
        )

        config = GameConfig(
            players=[player],
            galaxy_radius=4000,
            system_count=5
        )

        session = GameSession(config=config)
        empire = session.empires[0]
        home_colony = empire.colonies[0]

        # Happiness should be positive (we use 0.7 as starting value)
        assert home_colony.populations[0].happiness >= 0.5

    def test_no_explicit_race_config_gets_default_and_population(self):
        """Empire without explicit race_config gets a default and has population seeded (BUG-88)."""
        # Player without race_config - GameInitializer creates a default
        player = PlayerConfig(
            name="No Race Empire",
            theme="Federation",
            is_human=True,
            race_config=None
        )

        config = GameConfig(
            players=[player],
            galaxy_radius=4000,
            system_count=5
        )

        session = GameSession(config=config)
        empire = session.empires[0]

        # Empire should have a race_config (auto-created by GameInitializer)
        assert empire.race_config is not None

        # Empire should have a colony with population seeded
        assert len(empire.colonies) > 0
        home_colony = empire.colonies[0]
        assert home_colony.total_population > 0


class TestQuickstartPopulationSeeding:
    """Test that quickstart games have population properly seeded."""

    def test_quickstart_has_population(self):
        """Quickstart game should seed population on home colony."""
        config = QuickstartBuilder.build_1p_config(
            galaxy_radius=4000,
            system_count=5
        )

        # Verify race_config is passed through
        assert config.players[0].race_config is not None, \
            "Quickstart should include race_config in PlayerConfig"

        session = GameSession(config=config)
        empire = session.empires[0]

        # Should have home colony with population
        assert len(empire.colonies) > 0, "Empire should have a colony"
        home_colony = empire.colonies[0]
        assert home_colony.total_population > 0, "Home colony should have population"

    def test_quickstart_2p_both_have_population(self):
        """Both players in 2P quickstart should have population."""
        config = QuickstartBuilder.build_2p_config(
            galaxy_radius=4000,
            system_count=10  # Need enough systems for 2 players
        )

        session = GameSession(config=config)

        for i, empire in enumerate(session.empires):
            assert len(empire.colonies) > 0, f"Empire {i} should have a colony"
            home_colony = empire.colonies[0]
            assert home_colony.total_population > 0, \
                f"Empire {i} home colony should have population"
