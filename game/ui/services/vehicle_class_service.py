"""
Vehicle Class Service for UI layer.

PROJ-43: This service provides a facade for vehicle class data access,
allowing UI code to work with vehicle classes without directly importing from
game.simulation.entities.ship.

The service encapsulates:
- Vehicle class registry access
- Vehicle type enumeration
- Class filtering by type
- Max mass lookups
"""
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from game.core.registry import get_default_registry_provider
from game.core.protocols import IRegistryProvider

if TYPE_CHECKING:
    pass


class VehicleClassService:
    """Service for accessing vehicle class data.

    This class provides a clean interface for UI code to access vehicle class
    information without directly importing from the simulation layer.

    Usage:
        service = VehicleClassService()
        all_classes = service.get_all_classes()
        types = service.get_vehicle_types()
        ship_classes = service.get_classes_for_type('Ship')
    """

    def __init__(self, registry_provider: Optional[IRegistryProvider] = None):
        """Initialize the VehicleClassService.

        Args:
            registry_provider: Optional registry provider for dependency injection.
                If None, uses get_default_registries().
        """
        self._provider = registry_provider

    def _get_provider(self) -> IRegistryProvider:
        """Get the registry provider, using default if not injected."""
        if self._provider is None:
            self._provider = get_default_registry_provider()
        return self._provider

    def get_all_classes(self) -> Dict[str, Any]:
        """Get all vehicle classes from the registry.

        Returns:
            Dictionary mapping class names to class definitions.
        """
        provider = self._get_provider()
        return provider.get_vehicle_classes()

    def get_class_definition(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific vehicle class definition by name.

        Args:
            class_name: The vehicle class name (e.g., 'Escort', 'Frigate').

        Returns:
            The class definition dictionary, or None if not found.
        """
        classes = self.get_all_classes()
        return classes.get(class_name)

    def get_vehicle_types(self) -> List[str]:
        """Get a sorted list of unique vehicle types.

        Returns:
            Sorted list of vehicle type names (e.g., ['Craft', 'Ship']).
        """
        classes = self.get_all_classes()
        types = set(cls.get('type', 'Ship') for cls in classes.values())
        return sorted(list(types))

    def get_classes_for_type(self, vehicle_type: str) -> List[Tuple[str, int]]:
        """Get all classes that match a vehicle type.

        Args:
            vehicle_type: The vehicle type to filter by (e.g., 'Ship', 'Craft').

        Returns:
            List of (class_name, max_mass) tuples for matching classes.
        """
        classes = self.get_all_classes()
        result = []
        for name, cls_def in classes.items():
            if cls_def.get('type', 'Ship') == vehicle_type:
                max_mass = cls_def.get('max_mass', 0)
                result.append((name, max_mass))
        return result

    def get_max_mass(self, class_name: str) -> int:
        """Get the max_mass value for a vehicle class.

        Args:
            class_name: The vehicle class name.

        Returns:
            The max_mass value, or 0 if class not found or field missing.
        """
        cls_def = self.get_class_definition(class_name)
        if cls_def is None:
            return 0
        return cls_def.get('max_mass', 0)

    def get_type_for_class(self, class_name: str) -> str:
        """Get the vehicle type for a given class name.

        Args:
            class_name: The vehicle class name.

        Returns:
            The vehicle type string, or 'Ship' as default.
        """
        cls_def = self.get_class_definition(class_name)
        if cls_def is None:
            return 'Ship'
        return cls_def.get('type', 'Ship')
