"""
Race Validator - Validates race configuration before saving.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.
PROJ-21: ValidationResult now imported from game.core.validation.
PROJ-66 Phase 7: Added budget, water range, and aptitude range validation.

Provides user-friendly validation messages indicating which tab/section
needs attention.
"""
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.race_point_budget import RacePointBudget

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class RaceValidator:
    """
    Validator for race configuration.

    Checks that all required fields are present:
    - Race name (Identity tab)
    - Flag selection (Visuals tab)
    - Portrait selection (Visuals tab)
    - Ship theme selection (Ships tab)
    - Budget constraints (Aptitudes tab)
    - Water preferences in range (Environment tab)
    - Aptitudes in valid range (Aptitudes tab)
    """

    def __init__(self):
        """Initialize the race validator."""
        self._budget = RacePointBudget()

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
                errors=["Species name is required (set in Identity tab)"]
            )

        # Flag selection required
        if not race_config.flag_id:
            return ValidationResult(
                is_valid=False,
                errors=["Please select a flag (Visuals tab)"]
            )

        # Portrait selection required
        if not race_config.portrait_id:
            return ValidationResult(
                is_valid=False,
                errors=["Please select a portrait (Visuals tab)"]
            )

        # Theme selection required
        if not race_config.theme_id:
            return ValidationResult(
                is_valid=False,
                errors=["Please select a ship theme (Ships tab)"]
            )

        # Validate water preferences in range
        if not (0.0 <= race_config.water_ideal <= 1.0):
            return ValidationResult(
                is_valid=False,
                errors=["Water ideal must be between 0% and 100% (Environment tab)"]
            )

        if not (0.0 <= race_config.water_tolerance <= 1.0):
            return ValidationResult(
                is_valid=False,
                errors=["Water tolerance must be between 0% and 100% (Environment tab)"]
            )

        # Validate aptitudes in range (1-100)
        aptitude_fields = [
            ("Strength", race_config.aptitude_strength),
            ("Intelligence", race_config.aptitude_intelligence),
            ("Constitution", race_config.aptitude_constitution),
            ("Dexterity", race_config.aptitude_dexterity),
            ("Tolerance of Others", race_config.aptitude_tolerance_other_species),
            ("Cooperation", race_config.aptitude_cooperation),
            ("Happiness", race_config.aptitude_happiness),
            ("Population Growth", race_config.aptitude_population_growth),
            ("Conflict Tolerance", race_config.aptitude_conflict_tolerance),
        ]
        for apt_name, apt_value in aptitude_fields:
            if not (1 <= apt_value <= 100):
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Aptitude {apt_name} must be between 1 and 100 (Aptitudes tab)"]
                )

        # Validate budget
        if not self._budget.is_within_budget(race_config):
            remaining = self._budget.get_remaining_points(race_config)
            return ValidationResult(
                is_valid=False,
                errors=[f"Species is over point budget by {abs(remaining)} points. "
                        f"Reduce aptitudes or tolerance on the Aptitudes tab."]
            )

        return ValidationResult(is_valid=True)
