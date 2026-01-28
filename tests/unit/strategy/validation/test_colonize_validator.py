"""
Tests for ColonizeValidator.

PROJ-36: Tests for centralized colonize order validation.
Migrated from test_turn_engine.py::TestColonizeValidation.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
    return galaxy


@pytest.fixture
def mock_fleet():
    """Create a mock fleet."""
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    return fleet


@pytest.fixture
def mock_planet():
    """Create a mock unowned planet."""
    planet = MagicMock()
    planet.name = "Test Planet"
    planet.owner_id = None  # Unowned
    planet.location = HexCoord(0, 0)
    return planet


# =============================================================================
# Test: Basic Validation
# =============================================================================


class TestColonizeValidatorBasic:
    """Tests for basic colonize validation."""

    def test_validate_no_fleet(self, mock_galaxy):
        """Validation fails when fleet is None."""
        from game.strategy.validation import ColonizeValidator

        result = ColonizeValidator.validate(mock_galaxy, None, None)

        assert result.is_valid is False
        assert "fleet" in result.message.lower()

    def test_validate_unowned_planet(self, mock_galaxy, mock_fleet, mock_planet):
        """Valid colonize order on unowned planet."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is True

    def test_validate_owned_planet_fails(self, mock_galaxy, mock_fleet, mock_planet):
        """Cannot colonize already-owned planet."""
        from game.strategy.validation import ColonizeValidator

        mock_planet.owner_id = 1  # Already owned
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "ALREADY_OWNED"

    def test_validate_wrong_location(self, mock_galaxy, mock_fleet, mock_planet):
        """Cannot colonize planet from different location."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = []  # No planets at fleet location
        mock_fleet.location = HexCoord(100, 100)  # Far away

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "WRONG_LOCATION"


# =============================================================================
# Test: "Any" Planet Validation
# =============================================================================


class TestColonizeValidatorAnyPlanet:
    """Tests for colonize validation with 'Any' planet target."""

    def test_validate_any_planet_success(self, mock_galaxy, mock_fleet, mock_planet):
        """Validate colonize order with 'Any' planet (None target)."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is True
        assert "candidate" in result.message.lower()

    def test_validate_any_no_candidates(self, mock_galaxy, mock_fleet):
        """Colonize 'Any' fails when no unowned planets at location."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = []

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is False
        assert result.error_code == "NO_CANDIDATES"

    def test_validate_any_skips_owned_planets(self, mock_galaxy, mock_fleet, mock_planet):
        """Colonize 'Any' skips already-owned planets."""
        from game.strategy.validation import ColonizeValidator

        mock_planet.owner_id = 1  # Owned
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is False
        assert result.error_code == "NO_CANDIDATES"


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestColonizeValidatorEdgeCases:
    """Tests for edge cases in colonize validation."""

    def test_multiple_planets_finds_valid_candidate(self, mock_galaxy, mock_fleet):
        """When multiple planets exist, finds a valid unowned candidate."""
        from game.strategy.validation import ColonizeValidator

        owned_planet = MagicMock()
        owned_planet.owner_id = 1
        owned_planet.name = "Owned Planet"

        unowned_planet = MagicMock()
        unowned_planet.owner_id = None
        unowned_planet.name = "Unowned Planet"

        mock_galaxy.get_planets_at_global_hex.return_value = [owned_planet, unowned_planet]
        mock_fleet.location = HexCoord(0, 0)

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is True

    def test_validate_specific_planet_not_at_location(self, mock_galaxy, mock_fleet, mock_planet):
        """Specific planet validation fails if planet is not at fleet location."""
        from game.strategy.validation import ColonizeValidator

        other_planet = MagicMock()
        other_planet.owner_id = None
        other_planet.name = "Other Planet"

        # Planet at location is different from target
        mock_galaxy.get_planets_at_global_hex.return_value = [other_planet]
        mock_fleet.location = HexCoord(0, 0)

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "WRONG_LOCATION"

    def test_fleet_moved_between_validation_and_execution(self, mock_galaxy, mock_fleet, mock_planet):
        """Validation reflects current fleet location, not cached location."""
        from game.strategy.validation import ColonizeValidator

        # Initially valid
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result1 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result1.is_valid is True

        # Fleet moves away
        mock_fleet.location = HexCoord(100, 100)
        mock_galaxy.get_planets_at_global_hex.return_value = []

        result2 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result2.is_valid is False
        assert result2.error_code == "WRONG_LOCATION"

    def test_planet_colonized_between_validation_and_execution(self, mock_galaxy, mock_fleet, mock_planet):
        """Validation reflects current planet ownership, not cached state."""
        from game.strategy.validation import ColonizeValidator

        # Initially valid
        mock_planet.owner_id = None
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result1 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result1.is_valid is True

        # Planet colonized by another empire
        mock_planet.owner_id = 2

        result2 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result2.is_valid is False
        assert result2.error_code == "ALREADY_OWNED"


# =============================================================================
# Test: Error Messages
# =============================================================================


class TestColonizeValidatorMessages:
    """Tests for error message content."""

    def test_no_fleet_message_mentions_fleet(self, mock_galaxy):
        """Error message for no fleet mentions 'fleet'."""
        from game.strategy.validation import ColonizeValidator

        result = ColonizeValidator.validate(mock_galaxy, None, None)

        assert "fleet" in result.message.lower()

    def test_already_owned_message_mentions_planet_name(self, mock_galaxy, mock_fleet, mock_planet):
        """Error message for owned planet mentions planet name."""
        from game.strategy.validation import ColonizeValidator

        mock_planet.name = "Alpha Centauri IV"
        mock_planet.owner_id = 1
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert mock_planet.name in result.message

    def test_no_candidates_message_is_clear(self, mock_galaxy, mock_fleet):
        """Error message for no candidates is descriptive."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = []

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert "colonizable" in result.message.lower() or "no" in result.message.lower()
