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
            return ValidationResult.error("Species name is required (set in Identity tab)")

        # Flag selection required
        if not race_config.flag_id:
            return ValidationResult.error("Please select a flag (Visuals tab)")

        # Portrait selection required
        if not race_config.portrait_id:
            return ValidationResult.error("Please select a portrait (Visuals tab)")

        # Theme selection required
        if not race_config.theme_id:
            return ValidationResult.error("Please select a ship theme (Ships tab)")

        # PROJ-283 Phase 4: water_ideal/_tolerance fields deleted; water bounds
        # are enforced by `EnvironmentalPreference.validate()` at construction
        # time on `race_config.preferences["water"]`. Per-tab range validation
        # for the new model lives in the Phase 5 UI rebuild.

        # Validate aptitudes in range (1-100). PROJ-283 Phase 4 dropped
        # `aptitude_happiness` and `aptitude_population_growth` (now expressed
        # via `base_happiness` and `base_reproduction_rate`).
        aptitude_fields = [
            ("Strength", race_config.aptitude_strength),
            ("Intelligence", race_config.aptitude_intelligence),
            ("Constitution", race_config.aptitude_constitution),
            ("Dexterity", race_config.aptitude_dexterity),
            ("Tolerance of Others", race_config.aptitude_tolerance_other_species),
            ("Cooperation", race_config.aptitude_cooperation),
            ("Conflict Tolerance", race_config.aptitude_conflict_tolerance),
        ]
        for apt_name, apt_value in aptitude_fields:
            if not (1 <= apt_value <= 100):
                return ValidationResult.error(f"Aptitude {apt_name} must be between 1 and 100 (Aptitudes tab)")

        # Validate budget
        if not self._budget.is_within_budget(race_config):
            remaining = self._budget.get_remaining_points(race_config)
            return ValidationResult.error(
                f"Species is over point budget by {abs(remaining)} points. "
                f"Reduce aptitudes or tolerance on the Aptitudes tab."
            )

        return ValidationResult.success()
