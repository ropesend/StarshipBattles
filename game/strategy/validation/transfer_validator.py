"""
TransferValidator - Validates TRANSFER orders for fleets.

PROJ-68: Validates cargo transfer operations between fleets and colonies.
"""
from typing import Any, Dict
from game.core.validation import ValidationResult


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
        target: Any,
        cargo_type: str,
        direction: str,
        amount: int,
        species_id: str = None,
        skip_location_check: bool = False,
        projected_cargo: int = None
    ) -> ValidationResult:
        """
        Validate if a fleet can perform a transfer operation with a colony or another fleet.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting the transfer (source for unload, target for load)
            target: The Planet or Fleet object to transfer with
            cargo_type: Type of cargo to transfer (e.g., 'passengers')
            direction: 'load' (target->fleet) or 'unload' (fleet->target)
            amount: Units to transfer (0 = all available)

        Returns:
            ValidationResult with error codes
        """
        # 1. Validate fleet exists
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet does not exist."], error_code="FLEET_NOT_FOUND")

        # 2. Validate target exists
        if not target:
            return ValidationResult(is_valid=False, errors=["Target does not exist."], error_code="TARGET_NOT_FOUND")

        # 3. Validate direction
        if direction not in TransferValidator.VALID_DIRECTIONS:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid direction '{direction}'. Must be 'load' or 'unload'."],
                error_code="INVALID_DIRECTION"
            )

        # 4. Validate cargo_type
        if cargo_type not in TransferValidator.VALID_CARGO_TYPES:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid cargo type '{cargo_type}'."],
                error_code="INVALID_CARGO_TYPE"
            )

        # 5. Validate location (skip when queuing orders with auto-move)
        from game.core.protocols import is_planet, is_fleet
        
        if is_planet(target) and not skip_location_check:
            # PROJ-68: Check if fleet is in the system containing the target planet
            fleet_system = galaxy.get_system_at_location(fleet.location)
            target_system = None
            
            # Find system containing target planet
            for sys in galaxy.systems.values():
                if target in sys.planets:
                    target_system = sys
                    break
            
            if fleet_system != target_system:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Fleet is not at {target.name}'s system."],
                    error_code="NOT_AT_PLANET"
                )
            if target.owner_id is None:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Planet {target.name} is not colonized."],
                    error_code="NOT_COLONIZED"
                )
        elif is_fleet(target):
            if fleet.location != target.location:
                return ValidationResult(
                    is_valid=False,
                    errors=["Fleets are not at the same location."],
                    error_code="NOT_CO_LOCATED"
                )
            if fleet.id == target.id:
                return ValidationResult(
                    is_valid=False,
                    errors=["Cannot transfer cargo to the same fleet."],
                    error_code="SAME_ENTITY"
                )

        # 6. Direction-specific validation
        if is_planet(target):
            if direction == "load":
                return TransferValidator._validate_load(fleet, target, cargo_type, amount, species_id, projected_cargo)
            else:  # unload
                return TransferValidator._validate_unload(fleet, target, cargo_type, amount, species_id, projected_cargo)
        else: # fleet
            return TransferValidator._validate_fleet_transfer(fleet, target, cargo_type, direction, amount, species_id)

    @staticmethod
    def _validate_fleet_transfer(
        fleet: Any,
        target_fleet: Any,
        cargo_type: str,
        direction: str,
        amount: int,
        species_id: str = None
    ) -> ValidationResult:
        """Validate a transfer between two fleets."""
        if cargo_type == "passengers":
            source = fleet if direction == "unload" else target_fleet
            dest = target_fleet if direction == "unload" else fleet
            
            # Check source has cargo
            current_cargo = source.get_fleet_cargo_current("passengers")
            if current_cargo <= 0:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Source fleet {source.id} has no passengers to transfer."],
                    error_code="NO_CARGO_TO_UNLOAD"
                )
            
            # Check destination has space
            capacity = dest.get_fleet_cargo_capacity("passengers")
            current = dest.get_fleet_cargo_current("passengers")
            if current >= capacity:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Destination fleet {dest.id} has no passenger capacity."],
                    error_code="NO_CARGO_SPACE"
                )
        
        return ValidationResult()

    @staticmethod
    def _validate_load(
        fleet: Any,
        planet: Any,
        cargo_type: str,
        amount: int,
        species_id: str = None,
        projected_cargo: int = None
    ) -> ValidationResult:
        """Validate a load operation (colony -> fleet)."""
        from game.core.logger import log_info
        # For passengers, check fleet has cargo capacity
        if cargo_type == "passengers":
            capacity = fleet.get_fleet_cargo_capacity("passengers")
            # Use projected cargo if provided (accounts for earlier queued orders)
            current = projected_cargo if projected_cargo is not None else fleet.get_fleet_cargo_current("passengers")
            available_space = capacity - current
            log_info(f"DIAG _validate_load: capacity={capacity}, current/projected={current}, available_space={available_space}, projected_cargo_param={projected_cargo}")

            if available_space <= 0:
                log_info(f"DIAG _validate_load: REJECTED - NO_CARGO_SPACE")
                return ValidationResult(
                    is_valid=False,
                    errors=["Fleet has no available passenger capacity."],
                    error_code="NO_CARGO_SPACE"
                )

            # Check colony has population
            if planet.total_population <= 0:
                log_info(f"DIAG _validate_load: REJECTED - NO_POPULATION on {planet.name}")
                return ValidationResult(
                    is_valid=False,
                    errors=[f"{planet.name} has no population to load."],
                    error_code="NO_POPULATION"
                )

            if species_id:
                has_species = any(p.race_id == species_id and p.count > 0 for p in planet.populations)
                log_info(f"DIAG _validate_load: species_id={species_id}, has_species={has_species}")
                if not has_species:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"{planet.name} has no {species_id} population to load."],
                        error_code="NO_POPULATION"
                    )

        log_info(f"DIAG _validate_load: PASSED")
        return ValidationResult()


    @staticmethod
    def _validate_unload(
        fleet: Any,
        planet: Any,
        cargo_type: str,
        amount: int,
        species_id: str = None,
        projected_cargo: int = None
    ) -> ValidationResult:
        """Validate an unload operation (fleet -> colony)."""
        # Check fleet has cargo to unload (use projected if available)
        if cargo_type == "passengers":
            current_cargo = projected_cargo if projected_cargo is not None else fleet.get_fleet_cargo_current("passengers")
            if current_cargo <= 0:
                return ValidationResult(
                    is_valid=False,
                    errors=["Fleet has no passengers to unload."],
                    error_code="NO_CARGO_TO_UNLOAD"
                )

        return ValidationResult()
