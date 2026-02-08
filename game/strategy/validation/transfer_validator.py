"""
TransferValidator - Validates TRANSFER orders for fleets.

PROJ-68: Validates cargo transfer operations between fleets and colonies.
"""
from typing import Any, Dict
from game.core.validation import ValidationResult, validation_result


class TransferValidator:
    """Validates TRANSFER orders for cargo operations between fleets and colonies."""

    # Valid cargo types
    VALID_CARGO_TYPES = {"passengers"}  # Extensible for future cargo types

    # Valid directions
    VALID_DIRECTIONS = {"load", "unload"}

    @staticmethod
    def validate(
        galaxy: Any,
        fleet: Any,
        planet: Any,
        cargo_type: str,
        direction: str,
        amount: int,
        species_id: str = None
    ) -> ValidationResult:
        """
        Validate if a fleet can perform a transfer operation with a colony.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting the transfer
            planet: The Planet object (colony)
            cargo_type: Type of cargo to transfer (e.g., 'passengers')
            direction: 'load' (colony→fleet) or 'unload' (fleet→colony)
            amount: Units to transfer (0 = all available)

        Returns:
            ValidationResult with error codes:
            - FLEET_NOT_FOUND: Fleet does not exist
            - PLANET_NOT_FOUND: Planet does not exist
            - INVALID_DIRECTION: direction must be 'load' or 'unload'
            - INVALID_CARGO_TYPE: cargo_type not recognized
            - NOT_AT_PLANET: Fleet is not at the planet's location
            - NOT_COLONIZED: Planet is not colonized
            - NO_CARGO_SPACE: Fleet has no available cargo capacity (for load)
            - NO_CARGO_TO_UNLOAD: Fleet has no cargo of this type (for unload)
            - NO_POPULATION: Colony has no population of the race (for load passengers)
        """
        # 1. Validate fleet exists
        if not fleet:
            return validation_result(False, "Fleet does not exist.", "FLEET_NOT_FOUND")

        # 2. Validate planet exists
        if not planet:
            return validation_result(False, "Planet does not exist.", "PLANET_NOT_FOUND")

        # 3. Validate direction
        if direction not in TransferValidator.VALID_DIRECTIONS:
            return validation_result(
                False,
                f"Invalid direction '{direction}'. Must be 'load' or 'unload'.",
                "INVALID_DIRECTION"
            )

        # 4. Validate cargo_type
        if cargo_type not in TransferValidator.VALID_CARGO_TYPES:
            return validation_result(
                False,
                f"Invalid cargo type '{cargo_type}'.",
                "INVALID_CARGO_TYPE"
            )

        # 5. Validate fleet is at planet location
        # Use galaxy to find planet's global hex
        planets_at_hex = galaxy.get_planets_at_global_hex(fleet.location)
        if planet not in planets_at_hex:
            return validation_result(
                False,
                f"Fleet is not at {planet.name}'s location.",
                "NOT_AT_PLANET"
            )

        # 6. Validate planet is colonized
        if planet.owner_id is None:
            return validation_result(
                False,
                f"Planet {planet.name} is not colonized.",
                "NOT_COLONIZED"
            )

        # 7. Direction-specific validation
        if direction == "load":
            return TransferValidator._validate_load(fleet, planet, cargo_type, amount, species_id)
        else:  # unload
            return TransferValidator._validate_unload(fleet, planet, cargo_type, amount, species_id)

    @staticmethod
    def _validate_load(
        fleet: Any,
        planet: Any,
        cargo_type: str,
        amount: int,
        species_id: str = None
    ) -> ValidationResult:
        """Validate a load operation (colony → fleet)."""
        # For passengers, check fleet has cargo capacity
        if cargo_type == "passengers":
            capacity = fleet.get_fleet_cargo_capacity("passengers")
            current = fleet.get_fleet_cargo_current("passengers")
            available_space = capacity - current

            if available_space <= 0:
                return validation_result(
                    False,
                    "Fleet has no available passenger capacity.",
                    "NO_CARGO_SPACE"
                )

            # Check colony has population
            if planet.total_population <= 0:
                return validation_result(
                    False,
                    f"{planet.name} has no population to load.",
                    "NO_POPULATION"
                )

            if species_id:
                has_species = any(p.race_id == species_id and p.count > 0 for p in planet.populations)
                if not has_species:
                    return validation_result(
                        False,
                        f"{planet.name} has no {species_id} population to load.",
                        "NO_POPULATION"
                    )

        return validation_result(True, "Transfer load is valid.")

    @staticmethod
    def _validate_unload(
        fleet: Any,
        planet: Any,
        cargo_type: str,
        amount: int,
        species_id: str = None
    ) -> ValidationResult:
        """Validate an unload operation (fleet → colony)."""
        # Check fleet has cargo to unload
        if cargo_type == "passengers":
            current_cargo = fleet.get_fleet_cargo_current("passengers")
            if current_cargo <= 0:
                return validation_result(
                    False,
                    "Fleet has no passengers to unload.",
                    "NO_CARGO_TO_UNLOAD"
                )

        return validation_result(True, "Transfer unload is valid.")
