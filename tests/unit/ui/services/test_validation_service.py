"""Unit tests for ValidationService.

PROJ-43: Tests for the ValidationService facade that decouples UI from simulation.
"""
from unittest.mock import MagicMock, patch
import pytest

from game.ui.services.validation_service import ValidationService


class TestValidationService:
    """Tests for ValidationService class."""

    def test_validate_addition_delegates_to_validator(self):
        """Test validate_addition calls the underlying validator."""
        # Create mock validator
        mock_validator = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_result.errors = []
        mock_validator.validate_addition.return_value = mock_result

        # Create mock ship and component
        mock_ship = MagicMock()
        mock_component = MagicMock()
        mock_layer = MagicMock()

        service = ValidationService(validator=mock_validator)
        result = service.validate_addition(mock_ship, mock_component, mock_layer)

        mock_validator.validate_addition.assert_called_once_with(
            mock_ship, mock_component, mock_layer
        )
        assert result == mock_result

    def test_validate_addition_returns_invalid_result(self):
        """Test validate_addition returns invalid result from validator."""
        mock_validator = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = False
        mock_result.errors = ['Component too heavy for layer']
        mock_validator.validate_addition.return_value = mock_result

        mock_ship = MagicMock()
        mock_component = MagicMock()
        mock_layer = MagicMock()

        service = ValidationService(validator=mock_validator)
        result = service.validate_addition(mock_ship, mock_component, mock_layer)

        assert result.is_valid is False
        assert 'Component too heavy for layer' in result.errors

    def test_service_creates_default_validator_when_none_provided(self):
        """Test service creates/gets default validator when none injected."""
        with patch('game.ui.services.validation_service.get_or_create_validator') as mock_get:
            mock_validator = MagicMock()
            mock_result = MagicMock()
            mock_result.is_valid = True
            mock_validator.validate_addition.return_value = mock_result
            mock_get.return_value = mock_validator

            service = ValidationService()
            service.validate_addition(MagicMock(), MagicMock(), MagicMock())

            mock_get.assert_called()

    def test_validate_design_delegates_to_validator(self):
        """Test validate_design calls the underlying validator."""
        mock_validator = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_result.errors = []
        mock_result.warnings = []
        mock_validator.validate_design.return_value = mock_result

        mock_ship = MagicMock()

        service = ValidationService(validator=mock_validator)
        result = service.validate_design(mock_ship)

        mock_validator.validate_design.assert_called_once_with(mock_ship)
        assert result == mock_result

    def test_validate_design_returns_warnings(self):
        """Test validate_design includes warnings from validator."""
        mock_validator = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_result.errors = []
        mock_result.warnings = ['Ship has no weapons']
        mock_validator.validate_design.return_value = mock_result

        mock_ship = MagicMock()

        service = ValidationService(validator=mock_validator)
        result = service.validate_design(mock_ship)

        assert result.is_valid is True
        assert 'Ship has no weapons' in result.warnings
