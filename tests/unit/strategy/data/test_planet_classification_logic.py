
import pytest
from game.strategy.data.planet import PlanetType
from game.strategy.data.planet_gen import PlanetGenerator


class TestClassificationConfigLoader:
    """Tests for loading classification configuration from astrophysics.json."""

    def test_load_classification_config(self):
        """Verify classification config can be loaded from astrophysics.json."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()

        assert "classification" in data
        classification = data["classification"]

        # Verify all required sections exist
        assert "mass_thresholds" in classification
        assert "temperature_thresholds" in classification
        assert "pressure_thresholds" in classification
        assert "water_coverage_thresholds" in classification

    def test_mass_thresholds_match_existing_logic(self):
        """Verify mass thresholds match the hardcoded values for backward compatibility."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()
        thresholds = data["classification"]["mass_thresholds"]

        # These values must match the hardcoded values in planet_gen.py
        assert thresholds["dwarf_max"] == 2.0e23  # mass < 2.0e23 for dwarf planets
        assert thresholds["giant_min"] == 6.0e24  # mass > 6.0e24 for giants
        assert thresholds["gas_giant_min"] == 1.0e26  # mass > 1.0e26 for jovian

    def test_temperature_thresholds_match_existing_logic(self):
        """Verify temperature thresholds match the hardcoded values."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader

        loader = AstrophysicsLoader()
        data = loader.load()
        thresholds = data["classification"]["temperature_thresholds"]

        # Key temperatures from planet_gen.py _determine_type
        assert thresholds["magma"] == 700  # temp > 700 for magma
        assert "cold_limit" in thresholds  # temp < 200 for cryo barren boundary

    def test_all_planet_types_have_rules(self):
        """Verify all 11 planet types have classification rules defined."""
        from game.strategy.generation.loaders.astrophysics_loader import AstrophysicsLoader
        from game.strategy.data.planet import PlanetType

        loader = AstrophysicsLoader()
        data = loader.load()
        type_rules = data["classification"].get("type_rules", {})

        # All PlanetType values should have rules
        for ptype in PlanetType:
            assert ptype.name in type_rules, f"Missing rule for {ptype.name}"


class TestPlanetClassificationLogic:
    """Unit tests for planet classification rules in planet_gen.py."""
    
    def setup_method(self):
        self.gen = PlanetGenerator()

    # (Classification, Mass(kg), Temp(K), Pressure(Pa), Water(0-1), Atmosphere, Activity)
    @pytest.mark.parametrize("expected_type, mass, temp, pressure, water, atmosphere, activity", [
        (PlanetType.JOVIAN,      1.9e27, 150, 1e12,   0.5, {}, 0.0), # Jupiter
        (PlanetType.ICE_GIANT,   1.0e26, 100, 1e10,   0.5, {}, 0.0), # Neptune
        (PlanetType.CHTHONIAN,   7.0e24, 1000, 500,   0.0, {}, 0.0), # Stripped Core (Mass > 6e24, Hot, Low Press)
        (PlanetType.ICE_DWARF,   1.3e22, 40,  10,     0.9, {}, 0.0), # Pluto (Cold, Small)
        (PlanetType.PLANETOID,   9.0e20, 200, 0,      0.0, {}, 0.0), # Ceres (Warm, Small)
        (PlanetType.MAGMA,       6.0e24, 900, 1e7,    0.0, {}, 0.0), # Hot Earth
        (PlanetType.MAGMA,       6.0e24, 500, 1e7,    0.0, {}, 0.9), # Tectonically Active
        (PlanetType.BARREN,      3.0e23, 400, 100,    0.0, {}, 0.0), # Mercury (Hot, Vacuum)
        (PlanetType.CRYOPLANET,  6.0e24, 150, 1e5,    0.5, {}, 0.0), # Cold Earth
        (PlanetType.CRYOPLANET,  3.0e23, 50,  100,    0.0, {}, 0.0), # Cold Mercury (No water, but cold vacuum usually => Ice/Rock, mapped to Cryo for now logic)
        (PlanetType.PELAGIC,     6.0e24, 290, 1e6,    0.95, {'H2O': 1e6}, 0.0), # Water world
        (PlanetType.ARID,        6.0e24, 290, 1e6,    0.1, {'CO2': 1e6}, 0.0),  # Dry
        (PlanetType.ARID,        6.0e24, 400, 1e7,    0.0, {'CO2': 1e7}, 0.0),  # Venus-like
        (PlanetType.CONTINENTAL, 6.0e24, 288, 101325, 0.7, {'N2': 78000}, 0.0), # Earth
    ])
    def test_classification_logic(self, expected_type, mass, temp, pressure, water, atmosphere, activity):
        """Verify _determine_type classifies correctly based on physical params."""
        p_type = self.gen._determine_type(
            mass=mass, 
            temp=temp, 
            pressure=pressure, 
            water=water, 
            atmosphere=atmosphere,
            activity=activity
        )
        assert p_type == expected_type, \
            f"Expected {expected_type.name}, got {p_type.name} for inputs: M={mass:.1e}, T={temp}, P={pressure}, W={water}"

    def test_edge_cases(self):
        """Test specific edge case boundaries."""
        # Borderline Earth/Arid
        # Temp 280 (Good), Water 0.19 (Low) -> Arid
        p_type = self.gen._determine_type(6e24, 280, 100000, 0.19, {})
        assert p_type == PlanetType.ARID
        
        # Temp 280 (Good), Water 0.20 (Border) -> Continental (fallback) or Arid?
        # Logic: if water < 0.2 -> Arid. If >= 0.2 and <= 0.85 -> Continental check (255<=T<=330, P>5000)
        p_type = self.gen._determine_type(6e24, 280, 100000, 0.20, {})
        assert p_type == PlanetType.CONTINENTAL

