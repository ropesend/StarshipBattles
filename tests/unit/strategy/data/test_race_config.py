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

    def test_to_dict_includes_all_new_fields(self):
        """Test that to_dict includes all new identity, homeworld, water, and aptitude fields."""
        config = RaceConfig(
            faction_name="Test Faction",
            race_name="Testlings",
            race_name_plural="Testlings",
            government_type="Empire",
            government_organization="Autocracy",
            leader_title="Emperor",
            physical_type="Humanoid",
            society_type="Explorers",
            homeworld_type="CONTINENTAL",
            water_ideal=0.6,
            water_tolerance=0.25,
            aptitude_strength=7,
            aptitude_intelligence=8,
        )

        data = config.to_dict()

        # Identity fields
        assert data["faction_name"] == "Test Faction"
        assert data["race_name"] == "Testlings"
        assert data["race_name_plural"] == "Testlings"
        assert data["government_type"] == "Empire"
        assert data["government_organization"] == "Autocracy"
        assert data["leader_title"] == "Emperor"
        assert data["physical_type"] == "Humanoid"
        assert data["society_type"] == "Explorers"

        # Homeworld & water fields
        assert data["homeworld_type"] == "CONTINENTAL"
        assert data["water_ideal"] == 0.6
        assert data["water_tolerance"] == 0.25

        # Aptitude fields (all 9)
        assert data["aptitude_strength"] == 7
        assert data["aptitude_intelligence"] == 8
        assert data["aptitude_constitution"] == 5
        assert data["aptitude_dexterity"] == 5
        assert data["aptitude_tolerance_other_species"] == 5
        assert data["aptitude_cooperation"] == 5
        assert data["aptitude_happiness"] == 5
        assert data["aptitude_population_growth"] == 5
        assert data["aptitude_conflict_tolerance"] == 5

    def test_from_dict_with_all_new_fields(self):
        """Test from_dict restores all new fields correctly."""
        data = {
            "name": "Test",
            "faction_name": "Restored Faction",
            "race_name": "Restorlings",
            "race_name_plural": "Restorlings",
            "government_type": "Federation",
            "government_organization": "Democracy",
            "leader_title": "President",
            "physical_type": "Reptilian",
            "society_type": "Diplomats",
            "homeworld_type": "OCEANIC",
            "water_ideal": 0.8,
            "water_tolerance": 0.1,
            "aptitude_strength": 3,
            "aptitude_intelligence": 9,
            "aptitude_constitution": 4,
            "aptitude_dexterity": 6,
            "aptitude_tolerance_other_species": 8,
            "aptitude_cooperation": 7,
            "aptitude_happiness": 6,
            "aptitude_population_growth": 5,
            "aptitude_conflict_tolerance": 2,
        }

        config = RaceConfig.from_dict(data)

        assert config.faction_name == "Restored Faction"
        assert config.race_name == "Restorlings"
        assert config.government_type == "Federation"
        assert config.homeworld_type == "OCEANIC"
        assert config.water_ideal == 0.8
        assert config.aptitude_strength == 3
        assert config.aptitude_intelligence == 9

    def test_from_dict_backward_compatible(self):
        """Test that old race data (missing new fields) loads with defaults."""
        # Simulating old format race file
        old_data = {
            "race_id": "old_race",
            "name": "Old Race",
            "flag_id": "flag_001",
            "portrait_id": "portrait.jpg",
            "theme_id": "Federation",
            "gravity_ideal": 1.0,
            "gravity_tolerance": 0.3,
            "temperature_ideal": 293.0,
            "temperature_tolerance": 50.0,
            "atmosphere_preferences": {"Oxygen": 0.0},
            "radiation_tolerance": 0.0,
            "bio_description": "Old bio",
            "socio_description": "Old socio",
        }

        config = RaceConfig.from_dict(old_data)

        # Original fields preserved
        assert config.name == "Old Race"
        assert config.flag_id == "flag_001"

        # New fields should get defaults
        assert config.faction_name == ""
        assert config.race_name == ""
        assert config.government_type == ""
        assert config.homeworld_type == ""
        assert config.water_ideal == 0.5
        assert config.water_tolerance == 0.2
        assert config.aptitude_strength == 5
        assert config.aptitude_intelligence == 5

    def test_serialization_round_trip_complete(self):
        """Test complete round-trip serialization preserves all fields."""
        original = RaceConfig(
            race_id="complete_test",
            name="Complete Race",
            faction_name="Complete Faction",
            race_name="Completers",
            race_name_plural="Completers",
            government_type="Alliance",
            government_organization="Republic",
            leader_title="Chancellor",
            physical_type="Avian",
            society_type="Scientists",
            flag_id="flag_complete",
            portrait_id="complete.jpg",
            theme_id="Romulans",
            homeworld_type="ARID",
            gravity_ideal=1.2,
            gravity_tolerance=0.4,
            temperature_ideal=310.0,
            temperature_tolerance=45.0,
            water_ideal=0.3,
            water_tolerance=0.15,
            radiation_tolerance=25.0,
            aptitude_strength=6,
            aptitude_intelligence=7,
            aptitude_constitution=8,
            aptitude_dexterity=4,
            aptitude_tolerance_other_species=5,
            aptitude_cooperation=6,
            aptitude_happiness=7,
            aptitude_population_growth=3,
            aptitude_conflict_tolerance=9,
            bio_description="Complete bio",
            socio_description="Complete socio",
        )

        data = original.to_dict()
        restored = RaceConfig.from_dict(data)

        # All fields must match
        assert restored.race_id == original.race_id
        assert restored.name == original.name
        assert restored.faction_name == original.faction_name
        assert restored.race_name == original.race_name
        assert restored.government_type == original.government_type
        assert restored.homeworld_type == original.homeworld_type
        assert restored.water_ideal == original.water_ideal
        assert restored.water_tolerance == original.water_tolerance
        assert restored.aptitude_strength == original.aptitude_strength
        assert restored.aptitude_intelligence == original.aptitude_intelligence
        assert restored.aptitude_constitution == original.aptitude_constitution
        assert restored.aptitude_conflict_tolerance == original.aptitude_conflict_tolerance


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

    def test_validate_water_ideal_out_of_range(self):
        """Test that water_ideal outside 0-1 fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            water_ideal=1.5,  # Out of range
        )
        is_valid, message = config.validate()
        assert is_valid is False
        assert "water" in message.lower()

    def test_validate_water_tolerance_out_of_range(self):
        """Test that water_tolerance outside 0-1 fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            water_tolerance=-0.1,  # Out of range
        )
        is_valid, message = config.validate()
        assert is_valid is False
        assert "water" in message.lower()

    def test_validate_aptitude_below_minimum(self):
        """Test that aptitude below 1 fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            aptitude_strength=0,  # Below minimum
        )
        is_valid, message = config.validate()
        assert is_valid is False
        assert "aptitude" in message.lower()

    def test_validate_aptitude_above_maximum(self):
        """Test that aptitude above 10 fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            aptitude_intelligence=11,  # Above maximum
        )
        is_valid, message = config.validate()
        assert is_valid is False
        assert "aptitude" in message.lower()

    def test_validate_invalid_government_type(self):
        """Test that invalid government type fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            government_type="InvalidType",  # Not in list
        )
        is_valid, message = config.validate()
        assert is_valid is False
        assert "government" in message.lower()

    def test_validate_invalid_homeworld_type(self):
        """Test that invalid homeworld type fails validation."""
        config = RaceConfig(
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            homeworld_type="INVALID_PLANET",  # Not a valid PlanetType
        )
        is_valid, message = config.validate()
        assert is_valid is False
        assert "homeworld" in message.lower()

    def test_validate_valid_race_with_all_new_fields(self):
        """Test that a fully populated race with all new fields passes validation."""
        from game.strategy.data.race_config import (
            GOVERNMENT_TYPES, GOVERNMENT_ORGANIZATIONS, LEADER_TITLES,
            PHYSICAL_TYPES, SOCIETY_TYPES
        )
        config = RaceConfig(
            name="Complete Race",
            flag_id="flag_complete",
            portrait_id="complete.jpg",
            theme_id="Federation",
            faction_name="Complete Empire",
            race_name="Completers",
            race_name_plural="Completers",
            government_type=GOVERNMENT_TYPES[0],  # Valid
            government_organization=GOVERNMENT_ORGANIZATIONS[0],  # Valid
            leader_title=LEADER_TITLES[0],  # Valid
            physical_type=PHYSICAL_TYPES[0],  # Valid
            society_type=SOCIETY_TYPES[0],  # Valid
            homeworld_type="CONTINENTAL",  # Valid PlanetType
            water_ideal=0.6,
            water_tolerance=0.2,
            aptitude_strength=7,
            aptitude_intelligence=8,
            aptitude_constitution=6,
            aptitude_dexterity=5,
            aptitude_tolerance_other_species=4,
            aptitude_cooperation=5,
            aptitude_happiness=6,
            aptitude_population_growth=7,
            aptitude_conflict_tolerance=5,
        )
        is_valid, message = config.validate()
        assert is_valid is True
        assert message == ""

    def test_validate_empty_optional_fields_passes(self):
        """Test that empty optional identity fields pass validation."""
        config = RaceConfig(
            name="Minimal Race",
            flag_id="flag_001",
            portrait_id="portrait.jpg",
            theme_id="Federation",
            # All identity fields empty - should pass
            government_type="",
            government_organization="",
            leader_title="",
            physical_type="",
            society_type="",
            homeworld_type="",
        )
        is_valid, message = config.validate()
        assert is_valid is True


class TestRaceConfigConstantLists:
    """Tests for constant lists defined in race_config module."""

    def test_government_types_list_has_14_items(self):
        """Test GOVERNMENT_TYPES has all 14 types."""
        from game.strategy.data.race_config import GOVERNMENT_TYPES
        assert len(GOVERNMENT_TYPES) == 14
        assert "Empire" in GOVERNMENT_TYPES
        assert "Hegemony" in GOVERNMENT_TYPES
        assert "Alliance" in GOVERNMENT_TYPES

    def test_government_organizations_list_has_13_items(self):
        """Test GOVERNMENT_ORGANIZATIONS has all 13 types."""
        from game.strategy.data.race_config import GOVERNMENT_ORGANIZATIONS
        assert len(GOVERNMENT_ORGANIZATIONS) == 13
        assert "Anarchy" in GOVERNMENT_ORGANIZATIONS
        assert "Democracy" in GOVERNMENT_ORGANIZATIONS

    def test_leader_titles_list_has_27_items(self):
        """Test LEADER_TITLES has all 27 titles."""
        from game.strategy.data.race_config import LEADER_TITLES
        assert len(LEADER_TITLES) == 27
        assert "Central Speaker" in LEADER_TITLES
        assert "Chairman" in LEADER_TITLES

    def test_physical_types_list_has_14_items(self):
        """Test PHYSICAL_TYPES has all 14 types."""
        from game.strategy.data.race_config import PHYSICAL_TYPES
        assert len(PHYSICAL_TYPES) == 14
        assert "Felinoid" in PHYSICAL_TYPES
        assert "Caninoid" in PHYSICAL_TYPES

    def test_society_types_list_has_17_items(self):
        """Test SOCIETY_TYPES has all 17 types."""
        from game.strategy.data.race_config import SOCIETY_TYPES
        assert len(SOCIETY_TYPES) == 17
        assert "Artisans" in SOCIETY_TYPES
        assert "Berserkers" in SOCIETY_TYPES

    def test_aptitude_names_list_has_9_items(self):
        """Test APTITUDE_NAMES has all 9 aptitudes."""
        from game.strategy.data.race_config import APTITUDE_NAMES
        assert len(APTITUDE_NAMES) == 9
        assert "strength" in APTITUDE_NAMES
        assert "intelligence" in APTITUDE_NAMES
        assert "constitution" in APTITUDE_NAMES
        assert "dexterity" in APTITUDE_NAMES
        assert "tolerance_other_species" in APTITUDE_NAMES
        assert "cooperation" in APTITUDE_NAMES
        assert "happiness" in APTITUDE_NAMES
        assert "population_growth" in APTITUDE_NAMES
        assert "conflict_tolerance" in APTITUDE_NAMES


class TestRaceConfigIdentityFields:
    """Tests for identity fields added to RaceConfig."""

    def test_create_race_with_identity_fields_defaults(self):
        """Test that identity fields have correct defaults."""
        config = RaceConfig()

        assert config.faction_name == ""
        assert config.race_name == ""
        assert config.race_name_plural == ""
        assert config.government_type == ""
        assert config.government_organization == ""
        assert config.leader_title == ""
        assert config.physical_type == ""
        assert config.society_type == ""

    def test_create_race_with_custom_identity(self):
        """Test creating a race with all identity fields set."""
        config = RaceConfig(
            faction_name="Rossarian Empire",
            race_name="Rossarian",
            race_name_plural="Rossarians",
            government_type="Empire",
            government_organization="Autocracy",
            leader_title="Emperor",
            physical_type="Felinoid",
            society_type="Conquerors",
        )

        assert config.faction_name == "Rossarian Empire"
        assert config.race_name == "Rossarian"
        assert config.race_name_plural == "Rossarians"
        assert config.government_type == "Empire"
        assert config.government_organization == "Autocracy"
        assert config.leader_title == "Emperor"
        assert config.physical_type == "Felinoid"
        assert config.society_type == "Conquerors"


class TestRaceConfigHomeworldWaterFields:
    """Tests for homeworld and water preference fields."""

    def test_default_water_preferences(self):
        """Test that water preferences have correct defaults."""
        config = RaceConfig()

        assert config.water_ideal == 0.5
        assert config.water_tolerance == 0.2
        assert config.homeworld_type == ""

    def test_create_race_with_homeworld_type(self):
        """Test setting homeworld type."""
        config = RaceConfig(
            homeworld_type="CONTINENTAL",
            water_ideal=0.7,
            water_tolerance=0.15,
        )

        assert config.homeworld_type == "CONTINENTAL"
        assert config.water_ideal == 0.7
        assert config.water_tolerance == 0.15


class TestRaceConfigAptitudeFields:
    """Tests for aptitude attribute fields."""

    def test_default_aptitudes_are_5(self):
        """Test that all aptitudes default to 5."""
        config = RaceConfig()

        assert config.aptitude_strength == 5
        assert config.aptitude_intelligence == 5
        assert config.aptitude_constitution == 5
        assert config.aptitude_dexterity == 5
        assert config.aptitude_tolerance_other_species == 5
        assert config.aptitude_cooperation == 5
        assert config.aptitude_happiness == 5
        assert config.aptitude_population_growth == 5
        assert config.aptitude_conflict_tolerance == 5

    def test_create_race_with_custom_aptitudes(self):
        """Test creating a race with custom aptitude values."""
        config = RaceConfig(
            aptitude_strength=8,
            aptitude_intelligence=3,
            aptitude_constitution=7,
            aptitude_dexterity=4,
            aptitude_tolerance_other_species=6,
            aptitude_cooperation=2,
            aptitude_happiness=9,
            aptitude_population_growth=1,
            aptitude_conflict_tolerance=10,
        )

        assert config.aptitude_strength == 8
        assert config.aptitude_intelligence == 3
        assert config.aptitude_constitution == 7
        assert config.aptitude_dexterity == 4
        assert config.aptitude_tolerance_other_species == 6
        assert config.aptitude_cooperation == 2
        assert config.aptitude_happiness == 9
        assert config.aptitude_population_growth == 1
        assert config.aptitude_conflict_tolerance == 10
