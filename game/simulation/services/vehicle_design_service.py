"""
Vehicle Design Service (renamed from ShipBuilderService).

Provides an abstraction layer between UI and Ship domain objects,
handling vehicle creation, component management, and design validation.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, TYPE_CHECKING

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import get_or_create_validator
from game.simulation.components.component import Component, create_component
from game.simulation.components.component_constants import LayerType
from game.core.registry import (
    get_component_registry, get_vehicle_classes, get_default_registry_provider,
    get_default_registries, GameRegistries
)
from game.core.logger import log_error, log_warning, log_info

if TYPE_CHECKING:
    from game.core.validation import ValidationResult
    from game.core.protocols import IRegistryProvider


@dataclass
class DesignResult:
    """Result of a design operation (renamed from ShipBuilderResult)."""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ship: Optional[Ship] = None
    removed_component: Optional[Component] = None


class VehicleDesignService:
    """
    Service for vehicle design operations (renamed from ShipBuilderService).

    Provides an abstraction between the UI and Ship domain objects,
    encapsulating validation, component management, and class changes.

    PROJ-27: Added registry injection for testability.
    PROJ-38: Added GameRegistries support for constructor injection.

    Usage:
        # New DI pattern (preferred)
        service = VehicleDesignService(registries=game_registries)

        # Transitional pattern (uses default registries)
        service = VehicleDesignService()

        # Legacy pattern (uses IRegistryProvider)
        service = VehicleDesignService(registry=provider)
    """

    def __init__(
        self,
        registry: Optional['IRegistryProvider'] = None,
        *,
        registries: Optional[GameRegistries] = None
    ):
        """
        Initialize the VehicleDesignService.

        Args:
            registry: Optional IRegistryProvider for dependency injection (legacy).
            registries: Optional GameRegistries for dependency injection (preferred).
                       If None, falls back to registry or get_default_registries().
        """
        # PROJ-38: Prefer GameRegistries if provided
        if registries is not None:
            self._registries = registries
            self._registry = None  # Not using legacy provider
        elif registry is not None:
            # Legacy: Use IRegistryProvider
            self._registry = registry
            self._registries = None
        else:
            # Transitional fallback to default registries
            try:
                self._registries = get_default_registries()
                self._registry = None
            except RuntimeError:
                # Default registries not set yet - use legacy provider
                self._registry = get_default_registry_provider()
                self._registries = None

    def _get_vehicle_classes(self):
        """Get vehicle_classes from either GameRegistries or IRegistryProvider."""
        if self._registries is not None:
            return self._registries.vehicle_classes
        return self._registry.get_vehicle_classes()

    def _get_components(self):
        """Get component registry from either GameRegistries or IRegistryProvider."""
        if self._registries is not None:
            return self._registries.components
        return self._registry.get_components()

    def create_ship(
        self,
        name: str,
        ship_class: str,
        theme_id: str = "Federation",
        x: float = 0.0,
        y: float = 0.0,
        color: tuple = (100, 100, 255),
        team_id: int = 0
    ) -> DesignResult:
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
            DesignResult with the created ship or errors
        """
        errors = []
        warnings = []

        # Validate class exists - PROJ-27/38: Use injected registry
        vehicle_classes = self._get_vehicle_classes()
        if ship_class not in vehicle_classes:
            warnings.append(f"Unknown ship class '{ship_class}', using defaults")

        try:
            # PROJ-38: Pass registries to Ship constructor
            ship = Ship(
                name=name,
                x=x,
                y=y,
                color=color,
                team_id=team_id,
                ship_class=ship_class,
                theme_id=theme_id,
                registries=self._registries
            )
            ship.recalculate_stats()

            return DesignResult(
                success=True,
                ship=ship,
                warnings=warnings
            )

        except Exception as e:
            log_error(f"Failed to create ship: {e}")
            errors.append(str(e))
            return DesignResult(
                success=False,
                errors=errors
            )

    def add_component(
        self,
        ship: Ship,
        component_id: str,
        layer: LayerType
    ) -> DesignResult:
        """
        Add a component to the ship.

        Args:
            ship: The ship to modify
            component_id: ID of the component to add
            layer: Target layer for the component

        Returns:
            DesignResult indicating success/failure
        """
        errors = []

        # Create the component
        component = create_component(component_id)
        if component is None:
            errors.append(f"Component '{component_id}' not found in registry")
            return DesignResult(success=False, errors=errors)

        # Use ship's add_component which handles validation
        success = ship.add_component(component, layer)

        if not success:
            errors.append(f"Failed to add '{component_id}' to {layer.name}")
            return DesignResult(success=False, errors=errors)

        return DesignResult(success=True, ship=ship)

    def add_component_instance(
        self,
        ship: Ship,
        component: Component,
        layer: LayerType
    ) -> DesignResult:
        """
        Add a pre-constructed component instance to the ship.

        Unlike add_component() which creates from ID, this accepts an existing
        Component instance (e.g., one with modifiers already applied).

        Args:
            ship: The ship to modify
            component: The component instance to add
            layer: Target layer for the component

        Returns:
            DesignResult indicating success/failure
        """
        errors = []

        if component is None:
            errors.append("Cannot add None component")
            return DesignResult(success=False, errors=errors)

        # Use ship's add_component which handles validation
        success = ship.add_component(component, layer)

        if not success:
            errors.append(f"Failed to add '{component.name}' to {layer.name}")
            return DesignResult(success=False, errors=errors)

        return DesignResult(success=True, ship=ship)

    def add_component_bulk(
        self,
        ship: Ship,
        component_id: str,
        layer: LayerType,
        count: int
    ) -> DesignResult:
        """
        Add multiple copies of a component to the ship.

        Args:
            ship: The ship to modify
            component_id: ID of the component to add
            layer: Target layer for the components
            count: Number of components to add

        Returns:
            DesignResult with count of successfully added components
        """
        errors = []
        warnings = []

        # Create the base component
        component = create_component(component_id)
        if component is None:
            errors.append(f"Component '{component_id}' not found in registry")
            return DesignResult(success=False, errors=errors)

        # Use ship's bulk add method
        added_count = ship.add_components_bulk(component, layer, count)

        if added_count == 0:
            errors.append(f"Could not add any '{component_id}' to {layer.name}")
            return DesignResult(success=False, errors=errors)

        if added_count < count:
            warnings.append(f"Only added {added_count} of {count} requested components")

        return DesignResult(
            success=True,
            ship=ship,
            warnings=warnings
        )

    def remove_component(
        self,
        ship: Ship,
        layer: LayerType,
        index: int
    ) -> DesignResult:
        """
        Remove a component from the ship by layer and index.

        Args:
            ship: The ship to modify
            layer: Layer containing the component
            index: Index of the component within the layer

        Returns:
            DesignResult with the removed component
        """
        errors = []

        # Validate layer exists
        if layer not in ship.layers:
            errors.append(f"Layer {layer.name} does not exist on ship")
            return DesignResult(success=False, errors=errors)

        # Validate index
        layer_components = ship.layers[layer]['components']
        if index < 0 or index >= len(layer_components):
            errors.append(f"Invalid component index {index} for layer {layer.name}")
            return DesignResult(
                success=False,
                errors=errors,
                removed_component=None
            )

        # Remove component
        removed = ship.remove_component(layer, index)

        if removed is None:
            errors.append(f"Failed to remove component at index {index}")
            return DesignResult(
                success=False,
                errors=errors,
                removed_component=None
            )

        return DesignResult(
            success=True,
            ship=ship,
            removed_component=removed
        )

    def change_class(
        self,
        ship: Ship,
        new_class: str,
        migrate_components: bool = True
    ) -> DesignResult:
        """
        Change the ship's vehicle class.

        This may affect:
        - Available layers
        - Mass budget
        - Component compatibility

        Args:
            ship: The ship to modify
            new_class: Target vehicle class
            migrate_components: If True, attempts to keep components and fit them
                                into new layers. If False, clears all components.

        Returns:
            DesignResult indicating success/failure
        """
        errors = []

        # Validate new class exists - PROJ-27/38: Use injected registry
        vehicle_classes = self._get_vehicle_classes()
        if new_class not in vehicle_classes:
            errors.append(f"Unknown vehicle class '{new_class}'")
            return DesignResult(success=False, errors=errors)

        old_class = ship.ship_class

        # Delegate to Ship.change_class which handles all the migration logic
        ship.change_class(new_class, migrate_components=migrate_components)

        log_info(f"Changed {ship.name} from {old_class} to {new_class} "
                 f"(migrate_components={migrate_components})")

        return DesignResult(
            success=True,
            ship=ship
        )

    def validate_design(self, ship: Ship) -> 'ValidationResult':
        """
        Validate the complete ship design.

        Note: This method always uses the singleton-backed validator via
        get_or_create_validator(), regardless of the registry passed to the
        constructor. Full registry injection into the validator is out of
        scope for PROJ-27. For isolated testing of validation, mock the
        validator directly.

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
        # PROJ-27/38: Use injected registry instead of singleton
        registry = self._get_components()

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
