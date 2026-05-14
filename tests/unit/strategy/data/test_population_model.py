"""
Tests for population data model (PROJ-68 Phase 1).

Tests SpeciesPopulation dataclass, Planet population tracking,
max_population calculation, and Empire.race_config storage.
"""
import pytest
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def earth_like_planet():
    """Create an Earth-like planet for testing (~5.1e14 m² surface area)."""
    return Planet(
        name="Terra Nova",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.972e24,
        radius=6.371e6,
        surface_area=5.1e14,  # Earth's surface area in m²
        density=5514,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.71,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )


@pytest.fixture
def small_planetoid():
    """Create a small planetoid (Ceres-like, ~2.8e12 m² surface)."""
    return Planet(
        name="Ceres Station",
        location=HexCoord(1, 0),
        orbit_distance=5,
        mass=9.39e20,
        radius=4.73e5,  # 473 km
        surface_area=2.8e12,  # Ceres surface area in m²
        density=2162,
        surface_gravity=0.27,
        surface_pressure=0,
        surface_temperature=168,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.0,
        planet_type=PlanetType.PLANETOID,
    )


# =============================================================================
# SpeciesPopulation Tests
# =============================================================================

class TestSpeciesPopulation:
    """Tests for SpeciesPopulation dataclass."""

    def test_species_population_defaults(self):
        """Test SpeciesPopulation initializes with correct defaults."""
        pop = SpeciesPopulation(race_id="humans")

        assert pop.race_id == "humans"
        assert pop.count == 0
        assert pop.happiness == 0.5

    def test_species_population_with_values(self):
        """Test SpeciesPopulation with explicit values."""
        pop = SpeciesPopulation(
            race_id="aliens",
            count=1000,
            happiness=0.8
        )

        assert pop.race_id == "aliens"
        assert pop.count == 1000
        assert pop.happiness == 0.8

    def test_species_population_happiness_bounds(self):
        """Test happiness can be set to boundary values."""
        pop_min = SpeciesPopulation(race_id="sad_folk", happiness=0.0)
        pop_max = SpeciesPopulation(race_id="happy_folk", happiness=1.0)

        assert pop_min.happiness == 0.0
        assert pop_max.happiness == 1.0


# =============================================================================
# Planet Population Tests
# =============================================================================

class TestPlanetPopulation:
    """Tests for Planet population features."""

    def test_planet_max_population_earth_like(self, earth_like_planet):
        """Test max_population for Earth-like planet (~51M units for Earth surface)."""
        # Formula: surface_area_m2 / 1_000_000 * 100 / 1000
        # = 5.1e14 / 1e6 * 100 / 1000 = 51,000,000 (51M units)
        # 1 unit = 1000 people, so 51B people capacity
        max_pop = earth_like_planet.max_population

        # Earth should support ~51 million units (51 billion people)
        assert max_pop == 51_000_000

    def test_planet_max_population_small_body(self, small_planetoid):
        """Test max_population for small planetoid is proportionally smaller."""
        # Ceres: 2.8e12 m² -> 2.8e12 / 1e6 * 100 / 1000 = 280,000 units
        max_pop = small_planetoid.max_population

        assert max_pop == 280_000

    def test_planet_total_population_empty(self, earth_like_planet):
        """Test total_population is 0 when no species present."""
        assert earth_like_planet.total_population == 0

    def test_planet_total_population_single_species(self, earth_like_planet):
        """Test total_population with single species."""
        earth_like_planet.populations = [
            SpeciesPopulation(race_id="humans", count=5000)
        ]

        assert earth_like_planet.total_population == 5000

    def test_planet_total_population_multi_species(self, earth_like_planet):
        """Test total_population sums across multiple species."""
        earth_like_planet.populations = [
            SpeciesPopulation(race_id="humans", count=5000),
            SpeciesPopulation(race_id="aliens", count=3000),
            SpeciesPopulation(race_id="synthetics", count=1500)
        ]

        assert earth_like_planet.total_population == 9500


# =============================================================================
# Planet Serialization Tests
# =============================================================================

class TestPlanetPopulationSerialization:
    """Tests for Planet population serialization."""

    def test_planet_populations_serialization_roundtrip(self, earth_like_planet):
        """Test populations survive to_dict/from_dict roundtrip."""
        earth_like_planet.populations = [
            SpeciesPopulation(race_id="humans", count=5000, happiness=0.75),
            SpeciesPopulation(race_id="aliens", count=3000, happiness=0.60)
        ]

        # Serialize
        data = earth_like_planet.to_dict()

        # Verify serialized structure
        assert 'populations' in data
        assert len(data['populations']) == 2
        assert data['populations'][0]['race_id'] == 'humans'
        assert data['populations'][0]['count'] == 5000
        assert data['populations'][0]['happiness'] == 0.75

        # Deserialize
        restored = Planet.from_dict(data)

        # Verify restored data
        assert len(restored.populations) == 2
        assert restored.populations[0].race_id == "humans"
        assert restored.populations[0].count == 5000
        assert restored.populations[0].happiness == 0.75
        assert restored.populations[1].race_id == "aliens"
        assert restored.populations[1].count == 3000

    def test_planet_empty_populations_backward_compat(self, earth_like_planet):
        """Test from_dict handles missing populations key (backward compat)."""
        data = earth_like_planet.to_dict()

        # Remove populations key to simulate old save file
        if 'populations' in data:
            del data['populations']

        # Should load without error, defaulting to empty list
        restored = Planet.from_dict(data)

        assert restored.populations == []
        assert restored.total_population == 0


# =============================================================================
# Empire RaceConfig Tests
# =============================================================================

class TestEmpireRaceConfig:
    """Tests for Empire.race_config storage."""

    def test_empire_race_config_storage(self):
        """Test Empire can store and retrieve race_config."""
        from game.strategy.data.race_config import RaceConfig

        # Create a simple race config
        race_config = RaceConfig(race_id="test_race", race_name="Test Race")

        # Create empire with race config
        empire = Empire(
            empire_id=1,
            name="Test Empire",
            color=(255, 0, 0),
            race_config=race_config
        )

        assert empire.race_config is not None
        assert empire.race_config.race_id == "test_race"
        assert empire.race_config.race_name == "Test Race"

    def test_empire_race_config_none_by_default(self):
        """Test Empire has no race_config by default."""
        empire = Empire(
            empire_id=1,
            name="Test Empire",
            color=(255, 0, 0)
        )

        assert empire.race_config is None

    def test_empire_race_config_serialization_roundtrip(self):
        """Test Empire.race_config survives to_dict/from_dict roundtrip.

        PROJ-283 Phase 4: legacy `water_ideal`/`temperature_ideal` fields
        deleted; environmental preferences round-trip via
        `race_config.preferences[<factor_id>]`.
        """
        from game.strategy.data.race_config import RaceConfig
        from game.strategy.data.environmental_preference import EnvironmentalPreference
        from game.strategy.data.habitability_factors import get_factor

        # Create race config with non-default preferences on water + temperature.
        race_config = RaceConfig(
            race_id="test_race",
            race_name="Test Race",
        )
        water = get_factor("water")
        race_config.preferences["water"] = EnvironmentalPreference(
            setpoint=0.5, tolerance=0.2,
            min_value=water.min_value, max_value=water.max_value, step=water.step,
        )
        temperature = get_factor("temperature")
        race_config.preferences["temperature"] = EnvironmentalPreference(
            setpoint=295, tolerance=temperature.default_tolerance,
            min_value=temperature.min_value, max_value=temperature.max_value,
            step=temperature.step,
        )

        # Create empire with race config
        empire = Empire(
            empire_id=1,
            name="Test Empire",
            color=(255, 0, 0),
            race_config=race_config
        )

        # Serialize
        data = empire.to_dict()

        # Verify race_config is in serialized data
        assert 'race_config' in data
        assert data['race_config']['race_id'] == 'test_race'

        # Deserialize (galaxy=None is fine for this test)
        restored = Empire.from_dict(data, galaxy=None)

        # Verify restored data
        assert restored.race_config is not None
        assert restored.race_config.race_id == "test_race"
        assert restored.race_config.race_name == "Test Race"
        assert restored.race_config.preferences["water"].setpoint == 0.5
        assert restored.race_config.preferences["water"].tolerance == 0.2
        assert restored.race_config.preferences["temperature"].setpoint == 295

    def test_empire_race_config_backward_compat(self):
        """Test from_dict handles missing race_config (backward compat)."""
        # Simulate old save file without race_config
        data = {
            'id': 1,
            'name': 'Old Empire',
            'color': [255, 0, 0],
            'colony_ids': [],
            'fleets': [],
            'built_ship_designs': []
        }

        # Should load without error
        restored = Empire.from_dict(data, galaxy=None)

        assert restored.race_config is None
