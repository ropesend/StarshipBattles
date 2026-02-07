"""
Tests for homeworld presets loading and application.

These presets define environmental defaults for each PlanetType,
used to auto-populate race environment settings based on homeworld selection.
"""
import pytest
from game.strategy.data.race_config import RaceConfig


class TestLoadHomeworldPresets:
    """Tests for loading the homeworld presets JSON file."""

    def test_load_homeworld_presets_returns_all_11(self):
        """Verify all 11 planet types have presets defined."""
        from game.strategy.data.homeworld_presets import load_homeworld_presets

        presets = load_homeworld_presets()

        assert len(presets) == 11
        expected_types = [
            "CONTINENTAL", "ARID", "PELAGIC", "MAGMA", "CRYOPLANET",
            "BARREN", "JOVIAN", "ICE_GIANT", "CHTHONIAN", "ICE_DWARF", "PLANETOID"
        ]
        for planet_type in expected_types:
            assert planet_type in presets, f"Missing preset for {planet_type}"


class TestGetPresetForPlanetType:
    """Tests for retrieving individual presets."""

    def test_get_preset_for_continental(self):
        """CONTINENTAL preset should have Earth-like values."""
        from game.strategy.data.homeworld_presets import get_preset_for_planet_type

        preset = get_preset_for_planet_type("CONTINENTAL")

        assert preset is not None
        assert preset["id"] == "CONTINENTAL"
        assert preset["name"] == "Continental"
        assert preset["gravity_ideal"] == 1.0
        assert preset["temperature_ideal"] == 293  # ~20C in Kelvin
        assert preset["water_ideal"] == 0.60
        assert preset["radiation_tolerance"] == 0
        # Earth-like atmosphere
        assert preset["atmosphere_preferences"]["Oxygen"] == 50
        assert preset["atmosphere_preferences"]["Nitrogen"] == 30

    def test_get_preset_for_jovian(self):
        """JOVIAN preset should have gas giant values."""
        from game.strategy.data.homeworld_presets import get_preset_for_planet_type

        preset = get_preset_for_planet_type("JOVIAN")

        assert preset is not None
        assert preset["id"] == "JOVIAN"
        assert preset["name"] == "Jovian"
        assert preset["gravity_ideal"] == 2.5
        assert preset["temperature_ideal"] == 200
        assert preset["water_ideal"] == 0.0
        assert preset["radiation_tolerance"] == 40
        # Hydrogen/Helium atmosphere
        assert preset["atmosphere_preferences"]["Hydrogen"] == 80
        assert preset["atmosphere_preferences"]["Helium"] == 60

    def test_get_preset_for_arid(self):
        """ARID preset should have desert values."""
        from game.strategy.data.homeworld_presets import get_preset_for_planet_type

        preset = get_preset_for_planet_type("ARID")

        assert preset is not None
        assert preset["id"] == "ARID"
        assert preset["temperature_ideal"] == 320  # Hot
        assert preset["water_ideal"] == 0.10  # Low water

    def test_get_preset_for_magma(self):
        """MAGMA preset should have volcanic values."""
        from game.strategy.data.homeworld_presets import get_preset_for_planet_type

        preset = get_preset_for_planet_type("MAGMA")

        assert preset is not None
        assert preset["id"] == "MAGMA"
        assert preset["temperature_ideal"] == 800  # Very hot
        assert preset["water_ideal"] == 0.0
        assert preset["radiation_tolerance"] == 60

    def test_get_preset_for_invalid_type_returns_none(self):
        """Invalid planet type should return None."""
        from game.strategy.data.homeworld_presets import get_preset_for_planet_type

        preset = get_preset_for_planet_type("INVALID_TYPE")

        assert preset is None


class TestApplyPresetToConfig:
    """Tests for applying presets to RaceConfig."""

    def test_apply_preset_to_config_sets_gravity(self):
        """Preset should set gravity_ideal and gravity_tolerance."""
        from game.strategy.data.homeworld_presets import (
            get_preset_for_planet_type, apply_preset_to_config
        )

        config = RaceConfig()
        preset = get_preset_for_planet_type("JOVIAN")

        apply_preset_to_config(preset, config)

        assert config.gravity_ideal == 2.5
        assert config.gravity_tolerance == preset["gravity_tolerance"]

    def test_apply_preset_to_config_sets_temperature(self):
        """Preset should set temperature_ideal and temperature_tolerance."""
        from game.strategy.data.homeworld_presets import (
            get_preset_for_planet_type, apply_preset_to_config
        )

        config = RaceConfig()
        preset = get_preset_for_planet_type("CRYOPLANET")

        apply_preset_to_config(preset, config)

        assert config.temperature_ideal == 200
        assert config.temperature_tolerance == preset["temperature_tolerance"]

    def test_apply_preset_to_config_sets_water(self):
        """Preset should set water_ideal and water_tolerance."""
        from game.strategy.data.homeworld_presets import (
            get_preset_for_planet_type, apply_preset_to_config
        )

        config = RaceConfig()
        preset = get_preset_for_planet_type("PELAGIC")

        apply_preset_to_config(preset, config)

        assert config.water_ideal == 0.95
        assert config.water_tolerance == preset["water_tolerance"]

    def test_apply_preset_to_config_sets_atmosphere(self):
        """Preset should set atmosphere_preferences."""
        from game.strategy.data.homeworld_presets import (
            get_preset_for_planet_type, apply_preset_to_config
        )

        config = RaceConfig()
        preset = get_preset_for_planet_type("ICE_GIANT")

        apply_preset_to_config(preset, config)

        # Ice giant atmosphere
        assert config.atmosphere_preferences["Hydrogen"] == 50
        assert config.atmosphere_preferences["Helium"] == 40
        assert config.atmosphere_preferences["Methane"] == 30

    def test_apply_preset_to_config_sets_radiation_tolerance(self):
        """Preset should set radiation_tolerance."""
        from game.strategy.data.homeworld_presets import (
            get_preset_for_planet_type, apply_preset_to_config
        )

        config = RaceConfig()
        preset = get_preset_for_planet_type("CHTHONIAN")

        apply_preset_to_config(preset, config)

        assert config.radiation_tolerance == 90  # Very high radiation resistance

    def test_apply_preset_to_config_sets_homeworld_type(self):
        """Preset should set homeworld_type on config."""
        from game.strategy.data.homeworld_presets import (
            get_preset_for_planet_type, apply_preset_to_config
        )

        config = RaceConfig()
        preset = get_preset_for_planet_type("CONTINENTAL")

        apply_preset_to_config(preset, config)

        assert config.homeworld_type == "CONTINENTAL"


class TestGetAvailableHomeworldNames:
    """Tests for the dropdown helper function."""

    def test_get_available_homeworld_names_returns_11(self):
        """Should return names for all 11 planet types."""
        from game.strategy.data.homeworld_presets import get_available_homeworld_names

        names = get_available_homeworld_names()

        assert len(names) == 11
        # Should be human-readable names, not enum values
        assert "Continental" in names
        assert "Jovian" in names
        assert "Ice Giant" in names

    def test_get_available_homeworld_names_are_display_names(self):
        """Names should be properly formatted for display."""
        from game.strategy.data.homeworld_presets import get_available_homeworld_names

        names = get_available_homeworld_names()

        # Check formatting
        for name in names:
            assert name[0].isupper(), f"Name '{name}' should be capitalized"
            assert "_" not in name, f"Name '{name}' should not contain underscores"
