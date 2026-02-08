"""
Tests for RaceValidator.

PROJ-66 Phase 7: Tests for validation of race configuration including
budget checks, water ranges, and aptitude ranges.
"""
import pytest
from unittest.mock import MagicMock

from game.ui.screens.race_validator import RaceValidator
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.race_point_budget import RacePointBudget


class TestRaceValidatorBasic:
    """Tests for basic RaceValidator functionality."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return RaceValidator()

    @pytest.fixture
    def valid_config(self):
        """Create a valid race config with all required fields."""
        config = RaceConfig()
        config.name = "Test Race"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"
        # Set defaults that are within budget
        config.water_ideal = 0.5
        config.water_tolerance = 0.2
        return config

    def test_validate_valid_config(self, validator, valid_config):
        """Test that a valid config passes validation."""
        result = validator.validate(valid_config)
        assert result.is_valid is True
        assert result.message is None or result.message == ""

    def test_validate_missing_name(self, validator):
        """Test that missing name fails validation."""
        config = RaceConfig()
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"

        result = validator.validate(config)
        assert result.is_valid is False
        assert "name" in result.message.lower()
        assert "Visuals" in result.message or "Identity" in result.message

    def test_validate_missing_flag(self, validator):
        """Test that missing flag fails validation."""
        config = RaceConfig()
        config.name = "Test Race"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"

        result = validator.validate(config)
        assert result.is_valid is False
        assert "flag" in result.message.lower()

    def test_validate_missing_portrait(self, validator):
        """Test that missing portrait fails validation."""
        config = RaceConfig()
        config.name = "Test Race"
        config.flag_id = "flag_001"
        config.theme_id = "Federation"

        result = validator.validate(config)
        assert result.is_valid is False
        assert "portrait" in result.message.lower()

    def test_validate_missing_theme(self, validator):
        """Test that missing theme fails validation."""
        config = RaceConfig()
        config.name = "Test Race"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = ""

        result = validator.validate(config)
        assert result.is_valid is False
        assert "theme" in result.message.lower()


class TestRaceValidatorBudget:
    """Tests for budget validation."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return RaceValidator()

    @pytest.fixture
    def valid_config(self):
        """Create a valid race config."""
        config = RaceConfig()
        config.name = "Test Race"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"
        return config

    def test_validate_over_budget_returns_error(self, validator, valid_config):
        """Test that over-budget config fails validation."""
        # Max out all aptitudes to 100 (massively over budget)
        valid_config.aptitude_strength = 100
        valid_config.aptitude_intelligence = 100
        valid_config.aptitude_constitution = 100
        valid_config.aptitude_dexterity = 100
        valid_config.aptitude_tolerance_other_species = 100
        valid_config.aptitude_cooperation = 100
        valid_config.aptitude_happiness = 100
        valid_config.aptitude_population_growth = 100
        valid_config.aptitude_conflict_tolerance = 100
        # Plus max tolerances
        valid_config.gravity_tolerance = 1.0
        valid_config.temperature_tolerance = 100
        valid_config.water_tolerance = 1.0

        result = validator.validate(valid_config)
        assert result.is_valid is False
        assert "budget" in result.message.lower()
        assert "Aptitudes" in result.message

    def test_validate_within_budget_passes(self, validator, valid_config):
        """Test that within-budget config passes validation."""
        # Default aptitudes (all 50) = 0 points
        # Default tolerances = small cost
        result = validator.validate(valid_config)
        assert result.is_valid is True


class TestRaceValidatorWaterRanges:
    """Tests for water preference validation."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return RaceValidator()

    @pytest.fixture
    def valid_config(self):
        """Create a valid race config."""
        config = RaceConfig()
        config.name = "Test Race"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"
        return config

    def test_validate_water_ideal_out_of_range_high(self, validator, valid_config):
        """Test that water_ideal > 1.0 fails validation."""
        valid_config.water_ideal = 1.5

        result = validator.validate(valid_config)
        assert result.is_valid is False
        assert "water" in result.message.lower()
        assert "Environment" in result.message

    def test_validate_water_ideal_out_of_range_low(self, validator, valid_config):
        """Test that water_ideal < 0.0 fails validation."""
        valid_config.water_ideal = -0.1

        result = validator.validate(valid_config)
        assert result.is_valid is False
        assert "water" in result.message.lower()

    def test_validate_water_tolerance_out_of_range_high(self, validator, valid_config):
        """Test that water_tolerance > 1.0 fails validation."""
        valid_config.water_tolerance = 1.5

        result = validator.validate(valid_config)
        assert result.is_valid is False
        assert "water" in result.message.lower() or "tolerance" in result.message.lower()

    def test_validate_water_valid_range(self, validator, valid_config):
        """Test that valid water ranges pass (within budget)."""
        valid_config.water_ideal = 0.0
        valid_config.water_tolerance = 0.2  # Low tolerance to stay within budget

        result = validator.validate(valid_config)
        assert result.is_valid is True


class TestRaceValidatorAptitudes:
    """Tests for aptitude range validation."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return RaceValidator()

    @pytest.fixture
    def valid_config(self):
        """Create a valid race config."""
        config = RaceConfig()
        config.name = "Test Race"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"
        return config

    def test_validate_aptitude_out_of_range_high(self, validator, valid_config):
        """Test that aptitude > 100 fails validation."""
        valid_config.aptitude_strength = 101

        result = validator.validate(valid_config)
        assert result.is_valid is False
        assert "aptitude" in result.message.lower() or "strength" in result.message.lower()
        assert "Aptitudes" in result.message

    def test_validate_aptitude_out_of_range_low(self, validator, valid_config):
        """Test that aptitude < 1 fails validation."""
        valid_config.aptitude_intelligence = 0

        result = validator.validate(valid_config)
        assert result.is_valid is False
        assert "aptitude" in result.message.lower() or "intelligence" in result.message.lower()

    def test_validate_aptitude_valid_range(self, validator, valid_config):
        """Test that valid aptitude ranges pass (within budget)."""
        valid_config.aptitude_strength = 1     # refunds 49 points
        valid_config.aptitude_intelligence = 60  # costs 11 points
        # Net aptitude cost: 11 - 49 = -38. Tolerance ~41. Total ~3. Within 100.

        result = validator.validate(valid_config)
        assert result.is_valid is True


class TestRaceValidatorNewFields:
    """Tests for validation with all new PROJ-66 fields."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return RaceValidator()

    def test_validate_valid_with_all_new_fields(self, validator):
        """Test that config with all new fields passes validation."""
        config = RaceConfig()
        # Required fields
        config.name = "Humans"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"
        # Identity fields (optional)
        config.faction_name = "Terran Federation"
        config.race_name = "Human"
        config.race_name_plural = "Humans"
        config.government_type = "Federation"
        config.government_organization = "Democracy"
        config.leader_title = "President"
        config.physical_type = "Humanoid"
        config.society_type = "Diplomats"
        # Environment
        config.homeworld_type = "CONTINENTAL"
        config.water_ideal = 0.6
        config.water_tolerance = 0.2
        # Aptitudes (within budget)
        config.aptitude_strength = 50
        config.aptitude_intelligence = 51
        config.aptitude_constitution = 50
        config.aptitude_dexterity = 50
        config.aptitude_tolerance_other_species = 51
        config.aptitude_cooperation = 52
        config.aptitude_happiness = 50
        config.aptitude_population_growth = 50
        config.aptitude_conflict_tolerance = 49

        result = validator.validate(config)
        assert result.is_valid is True

    def test_error_messages_reference_tab_names(self, validator):
        """Test that error messages reference correct tab names."""
        config = RaceConfig()
        config.name = "Test"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"

        # Over budget - should reference Aptitudes tab
        config.aptitude_strength = 100
        config.aptitude_intelligence = 100
        config.aptitude_constitution = 100
        config.aptitude_dexterity = 100
        config.aptitude_tolerance_other_species = 100
        config.aptitude_cooperation = 100
        config.aptitude_happiness = 100
        config.aptitude_population_growth = 100
        config.aptitude_conflict_tolerance = 100
        config.gravity_tolerance = 1.0
        config.temperature_tolerance = 100

        result = validator.validate(config)
        assert result.is_valid is False
        assert "Aptitudes" in result.message

    def test_empty_identity_fields_still_valid(self, validator):
        """Test that empty identity fields don't cause errors (they're optional)."""
        config = RaceConfig()
        config.name = "Test Race"
        config.flag_id = "flag_001"
        config.portrait_id = "portrait_001"
        config.theme_id = "Federation"
        # All identity fields left empty (defaults)

        result = validator.validate(config)
        assert result.is_valid is True
