"""Tests for ShipValidatorHelper (PROJ-88 Phase 3).

Tests the validation helper extracted from Ship class.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.simulation.entities.ship_validator_helper import ShipValidatorHelper


class TestShipValidatorHelperCheckValidity:
    """Tests for check_validity method."""

    def test_check_validity_returns_true_for_valid_ship(self):
        """check_validity returns True when validation passes."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_result.errors = []

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            result = helper.check_validity()

            assert result is True
            mock_ship.recalculate_stats.assert_called_once()

    def test_check_validity_returns_false_for_invalid_ship(self):
        """check_validity returns False when validation fails."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = False
        mock_result.errors = ["Mass budget exceeded by 100"]

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            result = helper.check_validity()

            assert result is False

    def test_check_validity_sets_mass_limits_ok_true_when_no_mass_error(self):
        """check_validity sets ship.mass_limits_ok to True when no mass error."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_result.errors = []

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            helper.check_validity()

            assert mock_ship.mass_limits_ok is True

    def test_check_validity_sets_mass_limits_ok_false_when_mass_error(self):
        """check_validity sets ship.mass_limits_ok to False when mass budget exceeded."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = False
        mock_result.errors = ["Mass budget exceeded by 100"]

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            helper.check_validity()

            assert mock_ship.mass_limits_ok is False


class TestShipValidatorHelperGetValidationWarnings:
    """Tests for get_validation_warnings method."""

    def test_get_validation_warnings_returns_list(self):
        """get_validation_warnings returns list of warning strings."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.warnings = ["Consider adding more armor", "Low fuel capacity"]

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            warnings = helper.get_validation_warnings()

            assert warnings == ["Consider adding more armor", "Low fuel capacity"]

    def test_get_validation_warnings_returns_empty_list_when_no_warnings(self):
        """get_validation_warnings returns empty list when no warnings."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.warnings = []

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            warnings = helper.get_validation_warnings()

            assert warnings == []


class TestShipValidatorHelperGetMissingRequirements:
    """Tests for get_missing_requirements method."""

    def test_get_missing_requirements_returns_empty_for_valid_ship(self):
        """get_missing_requirements returns empty list for valid ship."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = True
        mock_result.errors = []

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            missing = helper.get_missing_requirements()

            assert missing == []

    def test_get_missing_requirements_returns_errors_for_invalid_ship(self):
        """get_missing_requirements returns formatted errors for invalid ship."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = False
        mock_result.errors = ["Missing bridge", "No engines"]

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            missing = helper.get_missing_requirements()

            assert missing == ["\u26a0 Missing bridge", "\u26a0 No engines"]

    def test_get_missing_requirements_prefixes_with_warning_emoji(self):
        """get_missing_requirements prefixes each error with warning emoji."""
        mock_ship = MagicMock()
        mock_result = MagicMock()
        mock_result.is_valid = False
        mock_result.errors = ["Error one"]

        with patch(
            'game.simulation.entities.ship_validator_helper.get_or_create_validator'
        ) as mock_get_validator:
            mock_validator = MagicMock()
            mock_validator.validate_design.return_value = mock_result
            mock_get_validator.return_value = mock_validator

            helper = ShipValidatorHelper(mock_ship)
            missing = helper.get_missing_requirements()

            # \u26a0 is the warning sign unicode character
            assert all(m.startswith("\u26a0 ") for m in missing)
