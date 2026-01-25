"""
Race Validator - Validates race configuration before saving.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

Provides user-friendly validation messages indicating which tab/section
needs attention.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


@dataclass
class ValidationResult:
    """Result of race configuration validation.

    Attributes:
        is_valid: True if configuration is valid for saving
        message: Error message if invalid, empty string if valid
    """
    is_valid: bool
    message: str = ""


class RaceValidator:
    """
    Validator for race configuration.

    Checks that all required fields are present:
    - Race name (Visuals tab)
    - Flag selection (Visuals tab)
    - Portrait selection (Visuals tab)
    - Ship theme selection (Ships tab)
    """

    def __init__(self):
        """Initialize the race validator."""
        pass

    def validate(self, race_config: 'RaceConfig') -> ValidationResult:
        """
        Validate all required fields before saving.

        Checks fields in order and returns the first error found.

        Args:
            race_config: The RaceConfig to validate

        Returns:
            ValidationResult with is_valid and error message
        """
        # Name is required
        name = race_config.name
        if not name or (isinstance(name, str) and not name.strip()):
            return ValidationResult(
                is_valid=False,
                message="Race name is required (set in Visuals tab)"
            )

        # Flag selection required
        if not race_config.flag_id:
            return ValidationResult(
                is_valid=False,
                message="Please select a flag (Visuals tab)"
            )

        # Portrait selection required
        if not race_config.portrait_id:
            return ValidationResult(
                is_valid=False,
                message="Please select a portrait (Visuals tab)"
            )

        # Theme selection required
        if not race_config.theme_id:
            return ValidationResult(
                is_valid=False,
                message="Please select a ship theme (Ships tab)"
            )

        return ValidationResult(is_valid=True, message="")
