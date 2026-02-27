"""
SuperweaponValidator - Validates superweapon orders for fleets.

PROJ-102 Phase 4: Business logic validation for strategic superweapon orders.
"""
from typing import Any, Dict, List, Optional
from game.core.validation import ValidationResult
from game.strategy.services.component_inspector import (
    find_ship_with_ability as _inspector_find_ship,
    ship_has_ability,
)


class SuperweaponValidator:
    """Validates superweapon orders for fleets."""

    @staticmethod
    def find_ship_with_ability(
        fleet,
        ability_name: str,
        component_registry: Dict[str, Any]
    ) -> Optional[Any]:
        """Find a ship in the fleet with a specific ability.

        Args:
            fleet: The Fleet object
            ability_name: Name of ability to find (e.g., "DestroyPlanet")
            component_registry: Component registry dict for ability lookup

        Returns:
            The first ship with the ability, or None if not found.
        """
        return _inspector_find_ship(fleet.ships, ability_name, component_registry)

    @staticmethod
    def validate_implode_planet(
        galaxy,
        fleet,
        target_planet,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate if a fleet can implode (destroy) a planet.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object
            target_planet: The Planet to destroy
            component_registry: Optional component registry for ability lookup

        Returns:
            ValidationResult with is_valid and message.
        """
        # Check target planet exists
        if target_planet is None:
            return ValidationResult.error("No target planet specified.")

        # Check for DestroyPlanet ability
        if component_registry is not None:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "DestroyPlanet", component_registry
            )
            if ship is None:
                return ValidationResult.error("No ship in fleet has DestroyPlanet ability.")

        return ValidationResult.success()

    @staticmethod
    def validate_stellerate_star(
        galaxy,
        fleet,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate if a fleet can stellerate (destroy) the star at its location.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object
            component_registry: Optional component registry for ability lookup

        Returns:
            ValidationResult with is_valid and message.
        """
        # Check for DestroyStar ability
        if component_registry is not None:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "DestroyStar", component_registry
            )
            if ship is None:
                return ValidationResult.error("No ship in fleet has DestroyStar ability.")

        # Check fleet is at a star system
        system = galaxy.get_system_at_location(fleet.location)
        if system is None:
            return ValidationResult.error("Fleet must be at a star system to destroy a star.")

        # Check system has stars (stars is always [] or populated)
        if not system.stars:
            return ValidationResult.error("System has no stars to destroy.")

        return ValidationResult.success()

    @staticmethod
    def validate_open_warp_point(
        galaxy,
        fleet,
        target_system_name: str,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate if a fleet can open a warp point to a target system.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object
            target_system_name: Name of target system
            component_registry: Optional component registry for ability lookup

        Returns:
            ValidationResult with is_valid and message.
        """
        # Check for OpenWarpPoint ability
        if component_registry is not None:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "OpenWarpPoint", component_registry
            )
            if ship is None:
                return ValidationResult.error("No ship in fleet has OpenWarpPoint ability.")

        # Check fleet is at a star system
        current_system = galaxy.get_system_at_location(fleet.location)
        if current_system is None:
            return ValidationResult.error("Fleet must be at a star system to open a warp point.")

        # Check target system exists
        target_system = galaxy.name_map.get(target_system_name)
        if target_system is None:
            return ValidationResult.error(f"Target system '{target_system_name}' does not exist.")

        # Check warp link doesn't already exist (warp_points always exists)
        for wp in current_system.warp_points:
            if wp.destination_id == target_system_name:
                return ValidationResult.error(f"Warp link to '{target_system_name}' already exists.")

        return ValidationResult.success()

    @staticmethod
    def validate_close_warp_point(
        galaxy,
        fleet,
        warp_point_dest_id: str,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate if a fleet can close a warp point.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object
            warp_point_dest_id: Destination ID of warp point to close
            component_registry: Optional component registry for ability lookup

        Returns:
            ValidationResult with is_valid and message.
        """
        # Check for CloseWarpPoint ability
        if component_registry is not None:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "CloseWarpPoint", component_registry
            )
            if ship is None:
                return ValidationResult.error("No ship in fleet has CloseWarpPoint ability.")

        # Check fleet is at a star system
        current_system = galaxy.get_system_at_location(fleet.location)
        if current_system is None:
            return ValidationResult.error("Fleet must be at a star system to close a warp point.")

        # Check warp point with matching destination exists at fleet's hex
        found_warp_point = False
        for wp in current_system.warp_points:
            # Check if fleet is at this warp point's location
            wp_global = current_system.global_location + wp.location
            if fleet.location == wp_global and wp.destination_id == warp_point_dest_id:
                found_warp_point = True
                break

        if not found_warp_point:
            return ValidationResult.error(f"No warp point to '{warp_point_dest_id}' at fleet location.")

        return ValidationResult.success()

    @staticmethod
    def validate_create_dyson_sphere(
        galaxy,
        fleet,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate if a fleet can create a Dyson Sphere at its location.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object
            component_registry: Optional component registry for ability lookup

        Returns:
            ValidationResult with is_valid and message.
        """
        # Check for CreateDysonSphere ability
        if component_registry is not None:
            ship = SuperweaponValidator.find_ship_with_ability(
                fleet, "CreateDysonSphere", component_registry
            )
            if ship is None:
                return ValidationResult.error("No ship in fleet has CreateDysonSphere ability.")

        # Check fleet is at a star system
        current_system = galaxy.get_system_at_location(fleet.location)
        if current_system is None:
            return ValidationResult.error("Fleet must be at a star system to create a Dyson Sphere.")

        # Check system has stars (stars always exists on StarSystem)
        if not current_system.stars:
            return ValidationResult.error("System must have stars to create a Dyson Sphere.")

        return ValidationResult.success()

    @staticmethod
    def validate_self_destruct(
        fleet,
        ship_ids: List[str],
        component_registry: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate if ships can self-destruct.

        Args:
            fleet: The Fleet object
            ship_ids: List of ship IDs to self-destruct
            component_registry: Optional component registry for ability lookup

        Returns:
            ValidationResult with is_valid and message.
        """
        # Check ship list is not empty
        if not ship_ids:
            return ValidationResult.error("No ships specified for self-destruct.")

        # Build ship ID lookup
        ships_by_id = {ship.id: ship for ship in fleet.ships}

        # Validate each ship
        for ship_id in ship_ids:
            # Check ship exists in fleet
            ship = ships_by_id.get(ship_id)
            if ship is None:
                return ValidationResult.error(f"Ship '{ship_id}' not found in fleet.")

            # Check ship has SelfDestruct ability
            if component_registry is not None:
                if not ship_has_ability(ship, 'SelfDestruct', component_registry):
                    return ValidationResult.error(f"Ship '{ship_id}' does not have SelfDestruct ability.")

        return ValidationResult.success()
