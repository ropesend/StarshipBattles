"""
ShipBuilderService - Abstraction layer between UI and Ship domain objects.

This service handles ship creation, component management, and design validation,
providing a clean interface for the builder UI.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, TYPE_CHECKING

from game.simulation.entities.ship import Ship, get_or_create_validator
from game.simulation.components.component import Component, LayerType, create_component
from game.core.registry import get_component_registry, get_vehicle_classes
from game.core.logger import log_error, log_warning, log_info

if TYPE_CHECKING:
    from game.simulation.ship_validator import ValidationResult


@dataclass
class ShipBuilderResult:
    """Result object for ship builder operations."""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ship: Optional[Ship] = None
    removed_component: Optional[Component] = None


class ShipBuilderService:
    """
    Service layer for ship building operations.

    Provides an abstraction between the UI and Ship domain objects,
    encapsulating validation, component management, and class changes.
    """

    def create_ship(
        self,
        name: str,
        ship_class: str,
        theme_id: str = "Federation",
        x: float = 0.0,
        y: float = 0.0,
        color: tuple = (100, 100, 255),
        team_id: int = 0
    ) -> ShipBuilderResult:
        """
        Create a new ship with the specified parameters.

        Args:
            name: Ship name
            ship_class: Vehicle class (e.g., "Escort", "Cruiser")
            theme_id: Visual theme identifier
            x: Initial X position
            y: Initial Y position
            color: RGB color tuple
            team_id: Team identifier

        Returns:
            ShipBuilderResult with the created ship or errors
        """
        errors = []
        warnings = []

        # Validate class exists
        vehicle_classes = get_vehicle_classes()
        if ship_class not in vehicle_classes:
            warnings.append(f"Unknown ship class '{ship_class}', using defaults")

        try:
            ship = Ship(
                name=name,
                x=x,
                y=y,
                color=color,
                team_id=team_id,
                ship_class=ship_class,
                theme_id=theme_id
            )
            ship.recalculate_stats()

            return ShipBuilderResult(
                success=True,
                ship=ship,
                warnings=warnings
            )

        except Exception as e:
            log_error(f"Failed to create ship: {e}")
            errors.append(str(e))
            return ShipBuilderResult(
                success=False,
                errors=errors
            )

    def add_component(
        self,
        ship: Ship,
        component_id: str,
        layer: LayerType
    ) -> ShipBuilderResult:
        """
        Add a component to the ship.

        Args:
            ship: The ship to modify
            component_id: ID of the component to add
            layer: Target layer for the component

        Returns:
            ShipBuilderResult indicating success/failure
        """
        errors = []

        # Create the component
        component = create_component(component_id)
        if component is None:
            errors.append(f"Component '{component_id}' not found in registry")
            return ShipBuilderResult(success=False, errors=errors)

        # Use ship's add_component which handles validation
        success = ship.add_component(component, layer)

        if not success:
            errors.append(f"Failed to add '{component_id}' to {layer.name}")
            return ShipBuilderResult(success=False, errors=errors)

        return ShipBuilderResult(success=True, ship=ship)

    def add_component_bulk(
        self,
        ship: Ship,
        component_id: str,
        layer: LayerType,
        count: int
    ) -> ShipBuilderResult:
        """
        Add multiple copies of a component to the ship.

        Args:
            ship: The ship to modify
            component_id: ID of the component to add
            layer: Target layer for the components
            count: Number of components to add

        Returns:
            ShipBuilderResult with count of successfully added components
        """
        errors = []
        warnings = []

        # Create the base component
        component = create_component(component_id)
        if component is None:
            errors.append(f"Component '{component_id}' not found in registry")
            return ShipBuilderResult(success=False, errors=errors)

        # Use ship's bulk add method
        added_count = ship.add_components_bulk(component, layer, count)

        if added_count == 0:
            errors.append(f"Could not add any '{component_id}' to {layer.name}")
            return ShipBuilderResult(success=False, errors=errors)

        if added_count < count:
            warnings.append(f"Only added {added_count} of {count} requested components")

        return ShipBuilderResult(
            success=True,
            ship=ship,
            warnings=warnings
        )

    def remove_component(
        self,
        ship: Ship,
        layer: LayerType,
        index: int
    ) -> ShipBuilderResult:
        """
        Remove a component from the ship by layer and index.

        Args:
            ship: The ship to modify
            layer: Layer containing the component
            index: Index of the component within the layer

        Returns:
            ShipBuilderResult with the removed component
        """
        errors = []

        # Validate layer exists
        if layer not in ship.layers:
            errors.append(f"Layer {layer.name} does not exist on ship")
            return ShipBuilderResult(success=False, errors=errors)

        # Validate index
        layer_components = ship.layers[layer]['components']
        if index < 0 or index >= len(layer_components):
            errors.append(f"Invalid component index {index} for layer {layer.name}")
            return ShipBuilderResult(
                success=False,
                errors=errors,
                removed_component=None
            )

        # Remove component
        removed = ship.remove_component(layer, index)

        if removed is None:
            errors.append(f"Failed to remove component at index {index}")
            return ShipBuilderResult(
                success=False,
                errors=errors,
                removed_component=None
            )

        return ShipBuilderResult(
            success=True,
            ship=ship,
            removed_component=removed
        )

    def change_class(
        self,
        ship: Ship,
        new_class: str
    ) -> ShipBuilderResult:
        """
        Change the ship's vehicle class.

        This may affect:
        - Available layers
        - Mass budget
        - Component compatibility

        Args:
            ship: The ship to modify
            new_class: Target vehicle class

        Returns:
            ShipBuilderResult indicating success/failure
        """
        errors = []
        warnings = []

        # Validate new class exists
        vehicle_classes = get_vehicle_classes()
        if new_class not in vehicle_classes:
            errors.append(f"Unknown vehicle class '{new_class}'")
            return ShipBuilderResult(success=False, errors=errors)

        old_class = ship.ship_class

        # Store existing components (excluding hull)
        existing_components = [
            (layer_type, comp.id)
            for layer_type, comp in ship.iter_components()
            if layer_type != LayerType.HULL
        ]

        # Change class and reinitialize layers
        ship.ship_class = new_class
        ship._initialize_layers()

        # Update mass budget from new class
        class_def = vehicle_classes.get(new_class, {})
        ship.max_mass_budget = class_def.get('max_mass', 1000)

        # Auto-equip default hull for new class
        default_hull_id = class_def.get('default_hull_id')
        if default_hull_id:
            hull_component = create_component(default_hull_id)
            if hull_component and LayerType.HULL in ship.layers:
                ship.layers[LayerType.HULL]['components'].append(hull_component)
                hull_component.layer_assigned = LayerType.HULL
                hull_component.ship = ship

        # Try to restore compatible components
        restored_count = 0
        for layer_type, comp_id in existing_components:
            if layer_type in ship.layers:
                component = create_component(comp_id)
                if component:
                    if ship.add_component(component, layer_type):
                        restored_count += 1
                    else:
                        warnings.append(
                            f"Could not restore '{comp_id}' to {layer_type.name}"
                        )

        ship.recalculate_stats()

        log_info(f"Changed {ship.name} from {old_class} to {new_class}, "
                 f"restored {restored_count}/{len(existing_components)} components")

        return ShipBuilderResult(
            success=True,
            ship=ship,
            warnings=warnings
        )

    def validate_design(self, ship: Ship) -> 'ValidationResult':
        """
        Validate the complete ship design.

        Args:
            ship: The ship to validate

        Returns:
            ValidationResult from the ship validator
        """
        validator = get_or_create_validator()
        return validator.validate_design(ship)

    def get_available_components(
        self,
        ship: Ship,
        layer: LayerType
    ) -> List[str]:
        """
        Get list of component IDs that can be added to the specified layer.

        Args:
            ship: The ship (for context like vehicle type)
            layer: The target layer

        Returns:
            List of valid component IDs
        """
        available = []
        validator = get_or_create_validator()
        registry = get_component_registry()

        for comp_id in registry.keys():
            component = create_component(comp_id)
            if component is None:
                continue

            # Check if component can be added to this layer
            result = validator.validate_addition(ship, component, layer)
            if result.is_valid:
                available.append(comp_id)

        return available

    def get_layer_info(self, ship: Ship, layer: LayerType) -> dict:
        """
        Get information about a specific layer.

        Args:
            ship: The ship
            layer: The layer to query

        Returns:
            Dict with layer information (components, restrictions, etc.)
        """
        if layer not in ship.layers:
            return {}

        layer_data = ship.layers[layer]
        return {
            'components': [
                {
                    'id': c.id,
                    'name': c.name,
                    'is_operational': c.is_operational
                }
                for c in layer_data['components']
            ],
            'restrictions': layer_data.get('restrictions', []),
            'radius_pct': layer_data.get('radius_pct', 1.0)
        }

    def get_ship_summary(self, ship: Ship) -> dict:
        """
        Get a summary of ship stats and status.

        Args:
            ship: The ship to summarize

        Returns:
            Dict with key ship statistics
        """
        return {
            'name': ship.name,
            'class': ship.ship_class,
            'mass': ship.mass,
            'max_mass': ship.max_mass_budget,
            'mass_percent': (ship.mass / ship.max_mass_budget * 100)
                           if ship.max_mass_budget > 0 else 0,
            'hp': ship.hp,
            'max_hp': ship.max_hp,
            'total_thrust': ship.total_thrust,
            'max_speed': ship.max_speed,
            'turn_speed': ship.turn_speed,
            'component_count': len(ship.get_all_components()),
            'is_valid': self.validate_design(ship).is_valid
        }
