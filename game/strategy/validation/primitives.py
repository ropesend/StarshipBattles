"""Shared validator primitive functions.

Composable validation functions that can be reused across strategy validators.
Return None on success, or a ValidationResult on failure.

PROJ-176: Created to eliminate duplicate fleet/planet/system resolution code.
"""
from typing import Optional, TYPE_CHECKING

from game.core.validation import ValidationResult

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.galaxy import Galaxy


def require_fleet(session, fleet_id: int, empire_id: int) -> Optional[ValidationResult]:
    """Validate that a fleet exists and belongs to the specified empire.

    Args:
        session: The game session (must have empires list)
        fleet_id: The fleet ID to validate
        empire_id: The expected owner's empire ID

    Returns:
        None if valid, ValidationResult with error if invalid.
    """
    # Find the fleet
    fleet = None
    for empire in session.empires:
        for f in empire.fleets:
            if f.id == fleet_id:
                fleet = f
                break
        if fleet:
            break

    if fleet is None:
        return ValidationResult.error("Fleet not found.")

    if fleet.owner_id != empire_id:
        return ValidationResult.error("Fleet does not belong to this empire.")

    return None


def require_planet(session, planet_id: int) -> Optional[ValidationResult]:
    """Validate that a planet exists in the galaxy.

    Args:
        session: The game session (must have galaxy with systems)
        planet_id: The planet ID to validate

    Returns:
        None if valid, ValidationResult with error if invalid.
    """
    for system in session.galaxy.systems.values():
        for planet in system.planets:
            if planet.id == planet_id:
                return None

    return ValidationResult.error("Planet not found.")


def require_system_at_location(galaxy: 'Galaxy', location: 'HexCoord') -> Optional[ValidationResult]:
    """Validate that a system exists at the specified location.

    Args:
        galaxy: The galaxy to search
        location: The hex coordinate to check

    Returns:
        None if valid, ValidationResult with error if invalid.
    """
    system = galaxy.get_system_at_location(location)
    if system is None:
        return ValidationResult.error("No system at this location.")

    return None
