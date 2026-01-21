"""
Unit tests for RaceConfig dataclass.
"""
import pytest
import tempfile
import os
import json

from game.strategy.data.race_config import RaceConfig, DEFAULT_ATMOSPHERE_PREFERENCES


class TestRaceConfigBasic:
    """Basic RaceConfig functionality tests."""

    def test_create_default_race_config(self):
        """Test creating a RaceConfig with default values."""
        config = RaceConfig()

        assert config.race_id == ""
        assert config.name == ""
        assert config.theme_id == "Federation"
        assert config.gravity_ideal == 1.0
        assert config.gravity_tolerance == 0.3
        assert config.temperature_ideal == 293.0
        assert config.temperature_tolerance == 50.0

    def test_create_race_config_with_values(self):
        """Test creating a RaceConfig with specified values."""
        config = RaceConfig(
            race_id="test_race",
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait_001.jpg",
            theme_id="Klingons",
            gravity_ideal=1.5,
            gravity_tolerance=0.5,
        )

        assert config.race_id == "test_race"
        assert config.name == "Test Race"
        assert config.flag_id == "flag_001"
        assert config.portrait_id == "portrait_001.jpg"
        assert config.theme_id == "Klingons"
        assert config.gravity_ideal == 1.5
        assert config.gravity_tolerance == 0.5

    def test_atmosphere_preferences_defaults(self):
        """Test that atmosphere preferences are initialized with defaults."""
        config = RaceConfig()

        assert "Oxygen" in config.atmosphere_preferences
        assert "Nitrogen" in config.atmosphere_preferences
        assert "Carbon Dioxide" in config.atmosphere_preferences
        assert "Methane" in config.atmosphere_preferences
        assert "Hydrogen" in config.atmosphere_preferences
        assert "Helium" in config.atmosphere_preferences

        # All should be 0.0 by default
        for gas, value in config.atmosphere_preferences.items():
            assert value == 0.0

    def test_atmosphere_preferences_custom(self):
        """Test setting custom atmosphere preferences."""
        custom_prefs = {"Oxygen": 50.0, "Methane": -75.0}
        config = RaceConfig(atmosphere_preferences=custom_prefs)

        # Custom values should be set
        assert config.atmosphere_preferences["Oxygen"] == 50.0
        assert config.atmosphere_preferences["Methane"] == -75.0

        # Missing defaults should be filled in
        assert "Nitrogen" in config.atmosphere_preferences


class TestRaceConfigSerialization:
    """RaceConfig serialization tests."""

    def test_to_dict_all_fields(self):
        """Test to_dict includes all fields."""
        config = RaceConfig(
            race_id="test_id",
            name="Test Name",
            flag_id="flag_123",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            gravity_ideal=1.2,
            gravity_tolerance=0.4,
            temperature_ideal=300.0,
            temperature_tolerance=60.0,
            radiation_tolerance=25.0,
            bio_description="Test bio",
            socio_description="Test socio",
            created_date="2026-01-01T00:00:00",
            modified_date="2026-01-02T00:00:00",
        )

        data = config.to_dict()

        assert data["race_id"] == "test_id"
        assert data["name"] == "Test Name"
        assert data["flag_id"] == "flag_123"
        assert data["portrait_id"] == "portrait.jpg"
        assert data["theme_id"] == "Federation"
        assert data["gravity_ideal"] == 1.2
        assert data["gravity_tolerance"] == 0.4
        assert data["temperature_ideal"] == 300.0
        assert data["temperature_tolerance"] == 60.0
        assert data["radiation_tolerance"] == 25.0
        assert data["bio_description"] == "Test bio"
        assert data["socio_description"] == "Test socio"
        assert data["created_date"] == "2026-01-01T00:00:00"
        assert data["modified_date"] == "2026-01-02T00:00:00"
        assert "atmosphere_preferences" in data

    def test_from_dict_all_fields(self):
        """Test from_dict restores all fields."""
        data = {
            "race_id": "restored_id",
            "name": "Restored Name",
            "flag_id": "flag_456",
            "portrait_id": "restored.jpg",
            "theme_id": "Romulans",
            "gravity_ideal": 0.8,
            "gravity_tolerance": 0.2,
            "temperature_ideal": 280.0,
            "temperature_tolerance": 40.0,
            "atmosphere_preferences": {"Oxygen": 100.0},
            "radiation_tolerance": -50.0,
            "bio_description": "Restored bio",
            "socio_description": "Restored socio",
            "created_date": "2025-12-01T00:00:00",
            "modified_date": "2025-12-15T00:00:00",
        }

        config = RaceConfig.from_dict(data)

        assert config.race_id == "restored_id"
        assert config.name == "Restored Name"
        assert config.flag_id == "flag_456"
        assert config.portrait_id == "restored.jpg"
        assert config.theme_id == "Romulans"
        assert config.gravity_ideal == 0.8
        assert config.gravity_tolerance == 0.2
        assert config.temperature_ideal == 280.0
        assert config.temperature_tolerance == 40.0
        assert config.radiation_tolerance == -50.0
        assert config.bio_description == "Restored bio"
        assert config.socio_description == "Restored socio"

    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves all data."""
        original = RaceConfig(
            race_id="round_trip_test",
            name="Round Trip Race",
            flag_id="flag_rt",
            portrait_id="rt_portrait.jpg",
            theme_id="Atlantians",
            gravity_ideal=1.8,
            gravity_tolerance=0.6,
            temperature_ideal=350.0,
            temperature_tolerance=80.0,
            atmosphere_preferences={"Oxygen": 75.0, "Methane": -25.0},
            radiation_tolerance=10.0,
            bio_description="Bio text here",
            socio_description="Socio text here",
        )

        data = original.to_dict()
        restored = RaceConfig.from_dict(data)

        assert restored.race_id == original.race_id
        assert restored.name == original.name
        assert restored.flag_id == original.flag_id
        assert restored.portrait_id == original.portrait_id
        assert restored.theme_id == original.theme_id
        assert restored.gravity_ideal == original.gravity_ideal
        assert restored.gravity_tolerance == original.gravity_tolerance
        assert restored.temperature_ideal == original.temperature_ideal
        assert restored.temperature_tolerance == original.temperature_tolerance
        assert restored.radiation_tolerance == original.radiation_tolerance
        assert restored.bio_description == original.bio_description
        assert restored.socio_description == original.socio_description

    def test_from_dict_missing_fields_uses_defaults(self):
        """Test that from_dict uses defaults for missing fields."""
        data = {"name": "Minimal Race"}

        config = RaceConfig.from_dict(data)

        assert config.name == "Minimal Race"
        assert config.race_id == ""  # Default
        assert config.theme_id == "Federation"  # Default
        assert config.gravity_ideal == 1.0  # Default


class TestRaceConfigFileIO:
    """RaceConfig file I/O tests."""

    def test_save_and_load(self):
        """Test saving and loading a race config."""
        config = RaceConfig(
            race_id="file_test",
            name="File Test Race",
            flag_id="flag_file",
            portrait_id="file_portrait.jpg",
            theme_id="Federation",
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            # Save
            assert config.save(filepath) is True

            # Verify file exists
            assert os.path.exists(filepath)

            # Load
            loaded = RaceConfig.load(filepath)

            assert loaded is not None
            assert loaded.race_id == "file_test"
            assert loaded.name == "File Test Race"
            assert loaded.flag_id == "flag_file"

            # Timestamps should be set
            assert loaded.created_date != ""
            assert loaded.modified_date != ""

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        result = RaceConfig.load("/nonexistent/path/race.json")
        assert result is None

    def test_save_updates_modified_date(self):
        """Test that save updates the modified date."""
        config = RaceConfig(name="Timestamp Test")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            assert config.modified_date == ""

            config.save(filepath)

            assert config.modified_date != ""
            assert config.created_date != ""

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)


class TestRaceConfigValidation:
    """RaceConfig validation tests."""

    def test_validate_complete_config(self):
        """Test that a complete config passes validation."""
        config = RaceConfig(
            name="Valid Race",
            flag_id="flag_valid",
            portrait_id="valid_portrait.jpg",
            theme_id="Federation",
        )

        is_valid, message = config.validate()
        assert is_valid is True
        assert message == ""

    def test_validate_missing_name(self):
        """Test that missing name fails validation."""
        config = RaceConfig(
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
        )

        is_valid, message = config.validate()
        assert is_valid is False
        assert "name" in message.lower()

    def test_validate_missing_flag(self):
        """Test that missing flag fails validation."""
        config = RaceConfig(
            name="Test Race",
            portrait_id="portrait.jpg",
            theme_id="Federation",
        )

        is_valid, message = config.validate()
        assert is_valid is False
        assert "flag" in message.lower()

    def test_validate_missing_portrait(self):
        """Test that missing portrait fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            theme_id="Federation",
        )

        is_valid, message = config.validate()
        assert is_valid is False
        assert "portrait" in message.lower()

    def test_validate_missing_theme(self):
        """Test that missing theme fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="",
        )

        is_valid, message = config.validate()
        assert is_valid is False
        assert "theme" in message.lower()

    def test_validate_gravity_out_of_range(self):
        """Test that out-of-range gravity fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            gravity_ideal=5.0,  # Out of range
        )

        is_valid, message = config.validate()
        assert is_valid is False
        assert "gravity" in message.lower()

    def test_validate_temperature_out_of_range(self):
        """Test that out-of-range temperature fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            temperature_ideal=500.0,  # Out of range
        )

        is_valid, message = config.validate()
        assert is_valid is False
        assert "temperature" in message.lower()

    def test_validate_description_too_long(self):
        """Test that overly long description fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            bio_description="x" * 501,  # Too long
        )

        is_valid, message = config.validate()
        assert is_valid is False
        assert "description" in message.lower()

    def test_is_complete(self):
        """Test is_complete returns correct status."""
        incomplete = RaceConfig(name="Incomplete")
        assert incomplete.is_complete() is False

        complete = RaceConfig(
            name="Complete",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
        )
        assert complete.is_complete() is True
