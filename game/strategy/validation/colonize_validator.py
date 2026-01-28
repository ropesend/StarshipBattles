"""
ColonizeValidator - Validates COLONIZE orders for fleets.

PROJ-36: Extracted from TurnEngine to centralize validation.
"""
from game.core.validation import ValidationResult, validation_result


class ColonizeValidator:
    """Validates COLONIZE orders for fleets."""

    @staticmethod
    def validate(galaxy, fleet, target_planet) -> ValidationResult:
        """
        Validate if a fleet can colonize a specific planet.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting to colonize
            target_planet: The Planet object or None for 'Any'

        Returns:
            ValidationResult with error codes:
            - NO_CANDIDATES: No colonizable planets at location
            - ALREADY_OWNED: Target planet is already owned
            - WRONG_LOCATION: Target planet is not at fleet location
        """
        # 1. Base Validation: Fleet must exist
        if not fleet:
            return validation_result(False, "Fleet does not exist.")

        # 2. Get System/Location Context - Use O(1) spatial index
        # Get all planets at the fleet's global hex location
        all_planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        valid_candidates = [p for p in all_planets_at_hex if p.owner_id is None]

        # 3. Check Logic
        if target_planet is None:
            # "Any Planet"
            if not valid_candidates:
                return validation_result(False, "No colonizable planets at this location.", "NO_CANDIDATES")
            return validation_result(True, "Valid candidate found.")

        else:
            # Specific Planet
            if target_planet.owner_id is not None:
                return validation_result(False, f"Planet {target_planet.name} is already owned.", "ALREADY_OWNED")

            # Check if planet is in valid candidates (verifies location)
            # We strictly check reference equality or ID equality if we had IDs
            if target_planet not in valid_candidates:
                # Determine detailed reason for better feedback
                # If owner is none (checked above), then it must be location.
                return validation_result(False, f"Planet {target_planet.name} is not at fleet location.", "WRONG_LOCATION")

            return validation_result(True, "Planet is valid for colonization.")
