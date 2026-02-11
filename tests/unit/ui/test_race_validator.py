"""
Unit tests for RaceValidator.

PROJ-12 Phase 4: TDD tests written before implementation.
Tests the race configuration validation logic.
"""

import pytest
from unittest.mock import MagicMock


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def complete_race_config():
    """Create a complete, valid race config mock."""
    config = MagicMock()
    config.name = "Test Race"
    config.flag_id = "flag_01"
    config.portrait_id = "portrait_01"
    config.theme_id = "theme_01"
    # Add PROJ-66 fields for budget validation
    config.water_ideal = 0.5
    config.water_tolerance = 0.2
    config.gravity_tolerance = 0.3
    config.temperature_tolerance = 50.0
    config.radiation_tolerance = 0.0
    config.atmosphere_preferences = {}
    # Default aptitudes (all 5 = 0 cost)
    config.aptitude_strength = 5
    config.aptitude_intelligence = 5
    config.aptitude_constitution = 5
    config.aptitude_dexterity = 5
    config.aptitude_tolerance_other_species = 5
    config.aptitude_cooperation = 5
    config.aptitude_happiness = 5
    config.aptitude_population_growth = 5
    config.aptitude_conflict_tolerance = 5
    return config


@pytest.fixture
def empty_race_config():
    """Create an empty race config mock."""
    config = MagicMock()
    config.name = ""
    config.flag_id = None
    config.portrait_id = None
    config.theme_id = None
    # Add PROJ-66 fields for budget validation
    config.water_ideal = 0.5
    config.water_tolerance = 0.2
    config.gravity_tolerance = 0.3
    config.temperature_tolerance = 50.0
    config.radiation_tolerance = 0.0
    config.atmosphere_preferences = {}
    # Default aptitudes
    config.aptitude_strength = 5
    config.aptitude_intelligence = 5
    config.aptitude_constitution = 5
    config.aptitude_dexterity = 5
    config.aptitude_tolerance_other_species = 5
    config.aptitude_cooperation = 5
    config.aptitude_happiness = 5
    config.aptitude_population_growth = 5
    config.aptitude_conflict_tolerance = 5
    return config


# =============================================================================
# Test: RaceValidator Creation
# =============================================================================

class TestRaceValidatorCreation:
    """Tests for RaceValidator initialization."""

    def test_race_validator_can_be_imported(self):
        """RaceValidator can be imported from module."""
        from game.ui.screens.race_validator import RaceValidator

        assert RaceValidator is not None

    def test_race_validator_can_be_instantiated(self):
        """RaceValidator can be created."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()

        assert validator is not None

    def test_race_validator_has_validate_method(self):
        """RaceValidator has validate method."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()

        assert hasattr(validator, 'validate')
        assert callable(validator.validate)


# =============================================================================
# Test: ValidationResult
# =============================================================================

class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_can_be_imported(self):
        """ValidationResult can be imported."""
        from game.ui.screens.race_validator import ValidationResult

        assert ValidationResult is not None

    def test_validation_result_has_is_valid_field(self):
        """ValidationResult has is_valid field."""
        from game.ui.screens.race_validator import ValidationResult

        result = ValidationResult(is_valid=True)

        assert result.is_valid is True

    def test_validation_result_has_message_field(self):
        """ValidationResult has message property."""
        from game.core.validation import ValidationResult

        result = ValidationResult(is_valid=False, errors=["Error"])

        assert result.message == "Error"

    def test_validation_result_default_message_is_empty(self):
        """ValidationResult default message is empty string."""
        from game.ui.screens.race_validator import ValidationResult

        result = ValidationResult(is_valid=True)

        assert result.message == ""


# =============================================================================
# Test: Validation Logic
# =============================================================================

class TestValidationLogic:
    """Tests for validation rules."""

    def test_validate_complete_config_returns_valid(self, complete_race_config):
        """Complete config validates successfully."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()

        result = validator.validate(complete_race_config)

        assert result.is_valid is True
        assert result.message == ""

    def test_validate_missing_name_returns_invalid(self, complete_race_config):
        """Missing name returns validation error."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.name = ""

        result = validator.validate(complete_race_config)

        assert result.is_valid is False
        assert "name" in result.message.lower()

    def test_validate_whitespace_name_returns_invalid(self, complete_race_config):
        """Whitespace-only name returns validation error."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.name = "   "

        result = validator.validate(complete_race_config)

        assert result.is_valid is False
        assert "name" in result.message.lower()

    def test_validate_none_name_returns_invalid(self, complete_race_config):
        """None name returns validation error."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.name = None

        result = validator.validate(complete_race_config)

        assert result.is_valid is False
        assert "name" in result.message.lower()

    def test_validate_missing_flag_returns_invalid(self, complete_race_config):
        """Missing flag_id returns validation error."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.flag_id = None

        result = validator.validate(complete_race_config)

        assert result.is_valid is False
        assert "flag" in result.message.lower()

    def test_validate_missing_portrait_returns_invalid(self, complete_race_config):
        """Missing portrait_id returns validation error."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.portrait_id = None

        result = validator.validate(complete_race_config)

        assert result.is_valid is False
        assert "portrait" in result.message.lower()

    def test_validate_missing_theme_returns_invalid(self, complete_race_config):
        """Missing theme_id returns validation error."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.theme_id = None

        result = validator.validate(complete_race_config)

        assert result.is_valid is False
        assert "theme" in result.message.lower()

    def test_validate_returns_first_error_found(self, empty_race_config):
        """Validate returns the first error encountered."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()

        result = validator.validate(empty_race_config)

        assert result.is_valid is False
        # Name is checked first
        assert "name" in result.message.lower()


# =============================================================================
# Test: Error Message Quality
# =============================================================================

class TestErrorMessageQuality:
    """Tests for user-friendly error messages."""

    def test_error_message_mentions_identity_tab_for_name(self, complete_race_config):
        """Name error mentions Identity tab (PROJ-66 moved name to Identity tab)."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.name = ""

        result = validator.validate(complete_race_config)

        assert "identity" in result.message.lower()

    def test_error_message_mentions_visuals_tab_for_flag(self, complete_race_config):
        """Flag error mentions Visuals tab."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.flag_id = None

        result = validator.validate(complete_race_config)

        assert "visuals" in result.message.lower()

    def test_error_message_mentions_ships_tab_for_theme(self, complete_race_config):
        """Theme error mentions Ships tab."""
        from game.ui.screens.race_validator import RaceValidator

        validator = RaceValidator()
        complete_race_config.theme_id = None

        result = validator.validate(complete_race_config)

        assert "ships" in result.message.lower()
