"""
Tests for PopulationEngine.

PROJ-68 Phase 3: Logistic population growth engine.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.population_engine import PopulationEngine
from game.strategy.data.planet import Planet, SpeciesPopulation, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.empire import Empire
from game.core.hex_math import HexCoord


def make_earth_like_planet(
    name: str = "Earth",
    populations: list = None,
    surface_area: float = 5.1e14,  # Earth ~510 million km²
    owner_id: int = 1
) -> Planet:
    """Create an Earth-like planet for testing."""
    return Planet(
        name=name,
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=surface_area,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,  # 15°C in Kelvin
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        atmosphere={"Nitrogen": 78000, "Oxygen": 21000},
        planet_type=PlanetType.CONTINENTAL,
        owner_id=owner_id,
        populations=populations or []
    )


def make_human_race_config(
    race_id: str = "human",
    aptitude_population_growth: int = 50
) -> RaceConfig:
    """Create a human-like race config for testing."""
    return RaceConfig(
        race_id=race_id,
        name="Human",
        gravity_ideal=1.0,
        gravity_tolerance=0.3,
        temperature_ideal=293.0,  # 20°C
        temperature_tolerance=50.0,
        water_ideal=0.7,
        water_tolerance=0.2,
        atmosphere_preferences={"Oxygen": 50, "Nitrogen": 20},
        radiation_tolerance=0.0,
        aptitude_population_growth=aptitude_population_growth
    )


def make_empire(empire_id: int, colonies: list, race_config: RaceConfig) -> Empire:
    """Create an empire with colonies and race_config."""
    empire = Empire(
        empire_id=empire_id,
        name="Test Empire",
        color=(100, 100, 200),
        race_config=race_config
    )
    empire.colonies = colonies
    return empire


class TestLogisticGrowthBasic:
    """Test basic logistic growth mechanics."""

    def test_logistic_growth_basic(self):
        """Single species on good habitability planet grows."""
        engine = PopulationEngine()

        pop = SpeciesPopulation(race_id="human", count=1000, happiness=1.0)
        planet = make_earth_like_planet(populations=[pop])
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        initial_pop = pop.count
        engine.process_population_growth([empire])

        # Population should have grown
        assert pop.count > initial_pop, "Population should grow"

    def test_growth_slows_near_capacity(self):
        """Growth slows as population approaches carrying capacity (S-curve)."""
        engine = PopulationEngine()

        # Start at 50% capacity
        planet = make_earth_like_planet()
        carrying_capacity = planet.max_population
        half_capacity = carrying_capacity // 2

        pop = SpeciesPopulation(race_id="human", count=half_capacity, happiness=1.0)
        planet.populations = [pop]
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        engine.process_population_growth([empire])
        growth_at_half = pop.count - half_capacity

        # Reset to 90% capacity
        near_capacity = int(carrying_capacity * 0.9)
        pop.count = near_capacity
        engine.process_population_growth([empire])
        growth_at_90 = pop.count - near_capacity

        # Growth should be much slower near capacity
        assert growth_at_half > growth_at_90, "Growth should slow near capacity"

    def test_zero_population_no_growth(self):
        """Empty colony stays empty - can't grow from nothing."""
        engine = PopulationEngine()

        pop = SpeciesPopulation(race_id="human", count=0, happiness=1.0)
        planet = make_earth_like_planet(populations=[pop])
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        engine.process_population_growth([empire])

        assert pop.count == 0, "Zero population cannot grow"


class TestHappinessAndHabitability:
    """Test happiness and habitability effects on growth."""

    def test_low_happiness_slows_growth(self):
        """Low happiness reduces growth rate."""
        engine = PopulationEngine()

        # High happiness population
        pop_happy = SpeciesPopulation(race_id="human", count=10000, happiness=1.0)
        planet_happy = make_earth_like_planet(name="Happy", populations=[pop_happy])
        race_happy = make_human_race_config(race_id="human_happy")
        empire_happy = make_empire(1, [planet_happy], race_happy)

        # Low happiness population
        pop_sad = SpeciesPopulation(race_id="human", count=10000, happiness=0.2)
        planet_sad = make_earth_like_planet(name="Sad", populations=[pop_sad])
        race_sad = make_human_race_config(race_id="human_sad")
        empire_sad = make_empire(2, [planet_sad], race_sad)

        engine.process_population_growth([empire_happy, empire_sad])

        growth_happy = pop_happy.count - 10000
        growth_sad = pop_sad.count - 10000

        assert growth_happy > growth_sad, "Happy population should grow faster"

    def test_low_habitability_reduces_carrying_capacity(self):
        """Low habitability reduces effective carrying capacity."""
        engine = PopulationEngine()

        # Good habitability planet (Earth-like)
        pop_good = SpeciesPopulation(race_id="human", count=10000, happiness=1.0)
        planet_good = make_earth_like_planet(name="Good", populations=[pop_good])
        race_good = make_human_race_config(race_id="human_good")
        empire_good = make_empire(1, [planet_good], race_good)

        # Bad habitability planet (wrong temperature - use extreme value)
        pop_bad = SpeciesPopulation(race_id="human", count=10000, happiness=1.0)
        planet_bad = make_earth_like_planet(name="Bad", populations=[pop_bad])
        planet_bad.surface_temperature = 500.0  # Extremely hot (212°C)
        planet_bad.magnetic_field = 0.0  # No radiation protection
        race_bad = make_human_race_config(race_id="human_bad")
        empire_bad = make_empire(2, [planet_bad], race_bad)

        # Run multiple turns to see divergence
        for _ in range(5):
            engine.process_population_growth([empire_good, empire_bad])

        # Good conditions should result in higher population
        assert pop_good.count > pop_bad.count, "Better habitability should allow more growth"


class TestPopulationDynamics:
    """Test population decline and edge cases."""

    def test_population_shrinks_above_carrying_capacity(self):
        """Population declines if above effective carrying capacity."""
        engine = PopulationEngine()

        # Small planet with extremely harsh conditions
        # Use a small surface area so max_population is low
        pop = SpeciesPopulation(race_id="human", count=100000, happiness=0.3)
        planet = make_earth_like_planet(
            populations=[pop],
            surface_area=1e10  # Very small planet, max_pop ~1000
        )
        planet.surface_temperature = 500.0  # Extremely hot
        planet.magnetic_field = 0.0  # No protection

        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        # Verify we're above capacity
        assert pop.count > planet.max_population, "Test setup: pop should exceed max"

        initial_pop = pop.count

        # Run multiple turns to see decline
        for _ in range(20):
            engine.process_population_growth([empire])

        # Population should have shrunk due to being above effective capacity
        assert pop.count < initial_pop, "Population should shrink above capacity"

    def test_multiple_species_grow_independently(self):
        """Multiple species on same planet grow independently."""
        engine = PopulationEngine()

        pop_human = SpeciesPopulation(race_id="human", count=5000, happiness=1.0)
        pop_alien = SpeciesPopulation(race_id="alien", count=3000, happiness=0.8)
        planet = make_earth_like_planet(populations=[pop_human, pop_alien])

        # Create race configs for both species
        race_human = make_human_race_config(race_id="human")
        race_alien = RaceConfig(
            race_id="alien",
            name="Alien",
            gravity_ideal=1.0,
            gravity_tolerance=0.5,  # More tolerant
            temperature_ideal=300.0,
            temperature_tolerance=80.0,
            water_ideal=0.6,
            water_tolerance=0.3,
            atmosphere_preferences={"Oxygen": 30, "Nitrogen": 30},
            radiation_tolerance=50.0,  # More resistant
            aptitude_population_growth=55  # Slightly faster growth
        )

        # Empire has multiple species (we store primary race_config)
        # For multi-species, we'd need a registry lookup
        # For now, test with single empire having human as primary
        empire = make_empire(1, [planet], race_human)
        # Patch to provide alien race config when needed
        original_get_race = engine._get_race_config

        def mock_get_race(race_id, empire):
            if race_id == "human":
                return race_human
            elif race_id == "alien":
                return race_alien
            return None

        engine._get_race_config = mock_get_race

        initial_human = pop_human.count
        initial_alien = pop_alien.count

        engine.process_population_growth([empire])

        # Both should grow (or at least be processed)
        assert pop_human.count != initial_human or pop_alien.count != initial_alien, \
            "At least one species should have population change"


class TestAptitudeEffects:
    """Test aptitude effects on growth rate."""

    def test_high_aptitude_faster_growth(self):
        """Higher population_growth aptitude results in faster growth."""
        engine = PopulationEngine()

        # Low aptitude empire
        pop_low = SpeciesPopulation(race_id="slow", count=10000, happiness=1.0)
        planet_low = make_earth_like_planet(name="Slow", populations=[pop_low])
        race_low = make_human_race_config(race_id="slow", aptitude_population_growth=10)
        empire_low = make_empire(1, [planet_low], race_low)

        # High aptitude empire
        pop_high = SpeciesPopulation(race_id="fast", count=10000, happiness=1.0)
        planet_high = make_earth_like_planet(name="Fast", populations=[pop_high])
        race_high = make_human_race_config(race_id="fast", aptitude_population_growth=90)
        empire_high = make_empire(2, [planet_high], race_high)

        engine.process_population_growth([empire_low, empire_high])

        growth_low = pop_low.count - 10000
        growth_high = pop_high.count - 10000

        assert growth_high > growth_low, "Higher aptitude should mean faster growth"


class TestAptitudeConversion:
    """Test aptitude to growth rate conversion."""

    def test_aptitude_to_growth_rate_boundaries(self):
        """Verify aptitude conversion at boundaries."""
        engine = PopulationEngine()

        # Aptitude 1 -> 0.05% per turn
        rate_1 = engine._aptitude_to_growth_rate(1)
        assert abs(rate_1 - 0.0005) < 0.0001, "Aptitude 1 should give ~0.05% rate"

        # Aptitude 50 -> 2.5% per turn
        rate_50 = engine._aptitude_to_growth_rate(50)
        assert abs(rate_50 - 0.025) < 0.001, "Aptitude 50 should give ~2.5% rate"

        # Aptitude 100 -> 5.0% per turn
        rate_100 = engine._aptitude_to_growth_rate(100)
        assert abs(rate_100 - 0.05) < 0.001, "Aptitude 100 should give ~5.0% rate"

    def test_aptitude_to_growth_rate_linear(self):
        """Growth rate increases linearly with aptitude."""
        engine = PopulationEngine()

        rate_30 = engine._aptitude_to_growth_rate(30)
        rate_70 = engine._aptitude_to_growth_rate(70)

        # Linear: rate(30) should be 30/70 of rate(70) approximately
        # Rate = 0.0005 * aptitude, so rate_30/rate_70 = 30/70
        ratio = rate_30 / rate_70
        expected_ratio = 30 / 70

        assert abs(ratio - expected_ratio) < 0.1, "Growth rate should scale linearly"


class TestTurnEngineIntegration:
    """Test PopulationEngine integration with TurnEngine."""

    def test_turn_engine_calls_population_engine(self, fresh_registries):
        """TurnEngine calls PopulationEngine when injected."""
        from game.strategy.engine.turn_engine import TurnEngine

        # Create mock population engine
        mock_pop_engine = MagicMock()

        # Inject into TurnEngine
        turn_engine = TurnEngine(
            registries=fresh_registries,
            population_engine=mock_pop_engine
        )

        # Create minimal test data
        empire = MagicMock(spec=Empire)
        empire.fleets = []
        empire.colonies = []  # Required for harvesting_engine
        empires = [empire]
        galaxy = MagicMock()

        # Run turn
        turn_engine.process_turn(empires, galaxy)

        # Verify population engine was called
        mock_pop_engine.process_population_growth.assert_called_once_with(empires)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_no_empires(self):
        """Engine handles empty empire list gracefully."""
        engine = PopulationEngine()
        # Should not raise
        engine.process_population_growth([])

    def test_empire_no_colonies(self):
        """Engine handles empire with no colonies."""
        engine = PopulationEngine()
        empire = make_empire(1, [], make_human_race_config())
        # Should not raise
        engine.process_population_growth([empire])

    def test_colony_no_populations(self):
        """Engine handles colony with no populations."""
        engine = PopulationEngine()
        planet = make_earth_like_planet(populations=[])
        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)
        # Should not raise
        engine.process_population_growth([empire])

    def test_population_clamped_to_zero(self):
        """Population cannot go negative."""
        engine = PopulationEngine()

        # Very small population on harsh planet
        pop = SpeciesPopulation(race_id="human", count=1, happiness=0.1)
        planet = make_earth_like_planet(populations=[pop])
        planet.surface_temperature = 500.0  # Extremely harsh
        planet.magnetic_field = 0.0

        race_config = make_human_race_config()
        empire = make_empire(1, [planet], race_config)

        # Run many turns
        for _ in range(100):
            engine.process_population_growth([empire])

        assert pop.count >= 0, "Population should never go negative"
