"""
DataService - Facade over data loading operations.

This service provides a clean interface for accessing game data
including components, modifiers, and vehicle classes.
"""
from typing import Dict, Any, List, Optional

from game.core.registry import (
    RegistryManager,
    get_component_registry,
    get_modifier_registry,
    get_vehicle_classes
)
from game.core.logger import log_info, log_warning


class DataService:
    """
    Service layer for game data access.

    Provides a facade over the registry system, offering convenient
    methods for querying components, modifiers, and vehicle classes.
    """

    def is_loaded(self) -> bool:
        """
        Check if game data has been loaded.

        Returns:
            True if registries are populated
        """
        components = get_component_registry()
        vehicle_classes = get_vehicle_classes()

        return len(components) > 0 and len(vehicle_classes) > 0

    def get_components(self) -> Dict[str, Any]:
        """
        Get all component definitions.

        Returns:
            Dictionary of component definitions keyed by ID
        """
        return get_component_registry()

    def get_modifiers(self) -> Dict[str, Any]:
        """
        Get all modifier definitions.

        Returns:
            Dictionary of modifier definitions keyed by ID
        """
        return get_modifier_registry()

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """
        Get all vehicle class definitions.

        Returns:
            Dictionary of vehicle class definitions keyed by name
        """
        return get_vehicle_classes()

    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific component definition.

        Args:
            component_id: Component ID to look up

        Returns:
            Component definition dict or None if not found
        """
        return get_component_registry().get(component_id)

    def get_modifier(self, modifier_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific modifier definition.

        Args:
            modifier_id: Modifier ID to look up

        Returns:
            Modifier definition dict or None if not found
        """
        return get_modifier_registry().get(modifier_id)

    def get_vehicle_class(self, class_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific vehicle class definition.

        Args:
            class_name: Class name to look up (e.g., "Escort")

        Returns:
            Vehicle class definition dict or None if not found
        """
        return get_vehicle_classes().get(class_name)

    def get_components_by_classification(
        self,
        classification: str
    ) -> List[str]:
        """
        Get component IDs filtered by major classification.

        Args:
            classification: Classification to filter by (e.g., "Weapons", "Engines")

        Returns:
            List of component IDs matching the classification
        """
        result = []
        for comp_id, component in get_component_registry().items():
            # Component objects have major_classification attribute
            comp_class = getattr(component, 'major_classification', None)
            if comp_class == classification:
                result.append(comp_id)
        return result

    def get_components_by_ability(
        self,
        ability_name: str
    ) -> List[str]:
        """
        Get component IDs that have a specific ability.

        Args:
            ability_name: Ability name to filter by

        Returns:
            List of component IDs with the ability
        """
        result = []
        for comp_id, component in get_component_registry().items():
            # Component objects have has_ability() method
            if hasattr(component, 'has_ability') and component.has_ability(ability_name):
                result.append(comp_id)
        return result

    def get_classes_by_type(
        self,
        vehicle_type: str
    ) -> List[str]:
        """
        Get vehicle class names filtered by type.

        Args:
            vehicle_type: Type to filter by (e.g., "Ship", "Fighter")

        Returns:
            List of class names matching the type
        """
        result = []
        for class_name, class_data in get_vehicle_classes().items():
            if class_data.get('type') == vehicle_type:
                result.append(class_name)
        return result

    def get_component_count(self) -> int:
        """
        Get total number of loaded components.

        Returns:
            Count of components in registry
        """
        return len(get_component_registry())

    def get_modifier_count(self) -> int:
        """
        Get total number of loaded modifiers.

        Returns:
            Count of modifiers in registry
        """
        return len(get_modifier_registry())

    def get_class_count(self) -> int:
        """
        Get total number of loaded vehicle classes.

        Returns:
            Count of vehicle classes in registry
        """
        return len(get_vehicle_classes())

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of loaded data.

        Returns:
            Dict with counts and status information
        """
        return {
            'is_loaded': self.is_loaded(),
            'component_count': self.get_component_count(),
            'modifier_count': self.get_modifier_count(),
            'class_count': self.get_class_count(),
            'classifications': self._get_unique_classifications(),
            'vehicle_types': self._get_unique_vehicle_types()
        }

    def _get_unique_classifications(self) -> List[str]:
        """Get list of unique component classifications."""
        classifications = set()
        for component in get_component_registry().values():
            # Component objects have major_classification attribute
            classification = getattr(component, 'major_classification', None)
            if classification:
                classifications.add(classification)
        return sorted(classifications)

    def _get_unique_vehicle_types(self) -> List[str]:
        """Get list of unique vehicle types."""
        types = set()
        for class_data in get_vehicle_classes().values():
            vehicle_type = class_data.get('type')
            if vehicle_type:
                types.add(vehicle_type)
        return sorted(types)
