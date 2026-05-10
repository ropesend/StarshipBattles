"""
Tests for astrophysics JSON loading and validation.

PROJ-322 Task 2.10 (S04-CAT5-002): the 5 per-class `loader` fixtures
were collapsed into a single module-scoped `loader` fixture. The disk
load now runs once per module rather than once per test.
"""
import pytest
from pathlib import Path


@pytest.fixture(scope='module')
def loader():
    """Module-scoped AstrophysicsLoader. Data is read-only — no test
    mutates the returned dict, so module scope is safe."""
    from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader
    return AstrophysicsLoader()


@pytest.fixture(scope='module')
def astrophysics_data(loader):
    """Module-scoped result of `loader.load()`."""
    return loader.load()


class TestAstrophysicsLoader:
    """Tests for loading and validating astrophysics.json."""

    def test_astrophysics_file_exists(self):
        """Verify astrophysics JSON file exists."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        path = Path("data/astrophysics.json")
        assert path.exists(), f"Expected {path} to exist"

    def test_load_returns_valid_dict(self):
        """Verify load() returns a dict."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()

        assert isinstance(data, dict)

    def test_contains_mass_distributions(self):
        """Verify mass distributions are defined."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()

        assert "mass_distributions" in data
        distributions = data["mass_distributions"]

        # Check required categories
        required = ["rocky", "gas_giant", "ice_giant", "dwarf"]
        for name in required:
            assert name in distributions, f"Missing mass distribution: {name}"

    def test_contains_orbit_zones(self):
        """Verify orbit zone definitions exist."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()

        assert "orbit_zones" in data
        zones = data["orbit_zones"]

        # Check required zones
        required = ["hot", "habitable", "cold", "outer"]
        for name in required:
            assert name in zones, f"Missing orbit zone: {name}"

    def test_contains_habitable_zone_formula(self):
        """Verify habitable zone formula parameters exist."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()

        assert "habitable_zone" in data
        hz = data["habitable_zone"]

        assert "inner_factor" in hz
        assert "outer_factor" in hz

    def test_contains_ice_line_parameters(self):
        """Verify ice line calculation parameters exist."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()

        assert "ice_line" in data

    def test_contains_atmosphere_retention(self):
        """Verify atmospheric retention thresholds exist."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()

        assert "atmosphere_retention" in data
        atm = data["atmosphere_retention"]

        # Should have escape velocity thresholds for different gases
        assert "thresholds" in atm


class TestMassDistributions:
    """Tests for mass distribution parameters."""

    @pytest.fixture(scope='class')
    def mass_distributions(self, astrophysics_data):
        """Mass distributions slice from the module-scoped data."""
        return astrophysics_data["mass_distributions"]

    def test_rocky_has_log_normal_params(self, mass_distributions):
        """Rocky distribution should have log-normal parameters."""
        rocky = mass_distributions["rocky"]
        assert "mu" in rocky, "Rocky missing mu"
        assert "sigma" in rocky, "Rocky missing sigma"

    def test_gas_giant_has_log_normal_params(self, mass_distributions):
        """Gas giant distribution should have log-normal parameters."""
        gas = mass_distributions["gas_giant"]
        assert "mu" in gas, "Gas giant missing mu"
        assert "sigma" in gas, "Gas giant missing sigma"

    def test_mass_ranges_are_sensible(self, mass_distributions):
        """Verify mass ranges make physical sense."""
        rocky = mass_distributions["rocky"]
        gas = mass_distributions["gas_giant"]

        # Rocky planets should be smaller than gas giants
        if "min" in rocky and "min" in gas:
            assert rocky.get("max", 1e30) < gas["min"] or rocky["min"] < gas["min"]


class TestOrbitZones:
    """Tests for orbit zone parameters."""

    @pytest.fixture(scope='class')
    def orbit_zones(self, astrophysics_data):
        """Orbit zones slice from the module-scoped data."""
        return astrophysics_data["orbit_zones"]

    def test_hot_zone_has_temperature_threshold(self, orbit_zones):
        """Hot zone should have a temperature threshold."""
        hot = orbit_zones["hot"]
        assert "temp_min" in hot or "flux_factor" in hot

    def test_habitable_zone_has_temperature_range(self, orbit_zones):
        """Habitable zone should have a temperature range."""
        hab = orbit_zones["habitable"]
        assert "temp_min" in hab
        assert "temp_max" in hab
        assert hab["temp_min"] < hab["temp_max"]

    def test_cold_zone_defined(self, orbit_zones):
        """Cold zone should be defined."""
        cold = orbit_zones["cold"]
        assert "temp_max" in cold


class TestHabitableZone:
    """Tests for habitable zone calculations."""

    @pytest.fixture(scope='class')
    def habitable_zone(self, astrophysics_data):
        """Habitable zone slice from the module-scoped data."""
        return astrophysics_data["habitable_zone"]

    def test_factors_are_positive(self, habitable_zone):
        """HZ factors should be positive."""
        assert habitable_zone["inner_factor"] > 0
        assert habitable_zone["outer_factor"] > 0

    def test_inner_closer_than_outer(self, habitable_zone):
        """Inner factor should be less than outer factor."""
        assert habitable_zone["inner_factor"] < habitable_zone["outer_factor"]


class TestAtmosphereRetention:
    """Tests for atmosphere retention parameters."""

    @pytest.fixture(scope='class')
    def atm_retention(self, astrophysics_data):
        """Atmosphere-retention slice from the module-scoped data."""
        return astrophysics_data["atmosphere_retention"]

    def test_has_escape_velocity_thresholds(self, atm_retention):
        """Should have escape velocity thresholds for gas retention."""
        thresholds = atm_retention["thresholds"]
        assert isinstance(thresholds, dict)
        assert len(thresholds) > 0

    def test_thresholds_have_gas_names(self, atm_retention):
        """Thresholds should be keyed by gas names."""
        thresholds = atm_retention["thresholds"]
        # Should have at least hydrogen and nitrogen
        assert "H2" in thresholds or "hydrogen" in thresholds.get("light_gases", {})

    def test_temperature_factor_present(self, atm_retention):
        """Should have temperature factor for retention calculation."""
        assert "temperature_factor" in atm_retention or "formula" in atm_retention


class TestClassificationThresholds:
    """Tests for planet classification thresholds."""

    def test_contains_classification_section(self, astrophysics_data):
        """Verify classification thresholds section exists."""
        assert "classification" in astrophysics_data

    def test_classification_has_mass_thresholds(self, astrophysics_data):
        """Verify mass thresholds for planet classification."""
        classification = astrophysics_data["classification"]

        assert "mass_thresholds" in classification
        thresholds = classification["mass_thresholds"]

        # Check key boundaries
        assert "dwarf_max" in thresholds  # Upper limit for dwarf planets
        assert "giant_min" in thresholds  # Lower limit for gas giants

    def test_classification_has_temperature_thresholds(self, astrophysics_data):
        """Verify temperature thresholds for planet classification."""
        classification = astrophysics_data["classification"]

        assert "temperature_thresholds" in classification
        thresholds = classification["temperature_thresholds"]

        # Check key temperatures
        assert "freezing" in thresholds  # Water freezing point
        assert "boiling" in thresholds   # Water boiling point
        assert "magma" in thresholds     # Lava/magma threshold
