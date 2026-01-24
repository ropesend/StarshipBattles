"""
ShipComponentManager - Handles component and layer management for ships.

This class encapsulates all component-related operations that were previously
embedded in the Ship class. It manages:
- Layer initialization and configuration
- Adding/removing components with validation
- Component queries (by ability, by layer, iteration)
- Bulk component operations

PROJ-12: God Class Decomposition - Phase 2
"""
import math
from typing import TYPE_CHECKING, Dict, List, Optional, Any, Iterator, Tuple, Callable

from game.simulation.components.component import Component, LayerType
from game.core.logger import log_debug, log_info, log_warning, log_error
from game.core.registry import get_vehicle_classes

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class ShipComponentManager:
    """
    Manages ship components and layers.

    This class handles all component-related operations for a ship, including
    layer initialization, component addition/removal, and component queries.
    The Ship class delegates component operations to this manager.

    Attributes:
        layers: Dictionary mapping LayerType to layer data (components, restrictions, etc.)
    """

    def __init__(self, ship: 'Ship'):
        """
        Initialize the component manager.

        Args:
            ship: The ship this manager is associated with.
        """
        self._ship = ship
        self.layers: Dict[LayerType, Dict[str, Any]] = {}

    def initialize_layers(self) -> None:
        """
        Initialize or re-initialize layers based on ship's vehicle class.

        Creates layers based on the vehicle class definition. Always creates
        a HULL layer, then adds layers specified in the class definition.
        Calculates layer radii based on mass capacity percentages.
        """
        class_def = get_vehicle_classes().get(self._ship.ship_class, {})
        self.layers = {}
        layer_defs = class_def.get('layers', [])

        # Fallback if no layers defined in vehicle class
        if not layer_defs:
            layer_defs = [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                {"type": "INNER", "radius_pct": 0.5, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.8, "restrictions": []},
                {"type": "ARMOR", "radius_pct": 1.0, "restrictions": []}
            ]

        # Force HULL layer existence (Index 0)
        self.layers[LayerType.HULL] = {
            'components': [],
            'radius_pct': 0.0,
            'restrictions': ['HullOnly'],
            'max_mass_pct': 100.0,
            'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0
        }

        for l_def in layer_defs:
            l_type_str = l_def.get('type')
            try:
                l_type = LayerType[l_type_str]
                # Avoid overwriting HULL if it was somehow in data
                if l_type == LayerType.HULL:
                    continue

                self.layers[l_type] = {
                    'components': [],
                    'radius_pct': l_def.get('radius_pct', 0.5),
                    'restrictions': l_def.get('restrictions', []),
                    'max_mass_pct': l_def.get('max_mass_pct', 1.0),
                    'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0
                }
            except KeyError:
                log_warning(f"Unknown LayerType {l_type_str} in class {self._ship.ship_class}")

        # Recalculate layer radii based on max_mass_pct (Area proportional to mass capacity)
        self._recalculate_layer_radii()

    def _recalculate_layer_radii(self) -> None:
        """Recalculate layer radii based on mass capacity percentages."""
        # Sort layers: HULL -> CORE -> INNER -> OUTER -> ARMOR
        layer_order = [LayerType.HULL, LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]

        # Filter layers present in this ship
        present_layers = [l for l in layer_order if l in self.layers]

        # Calculate total mass capacity (sum of max_mass_pct)
        # HULL is structural (radius 0), so excluded from area-proportional calculation
        total_capacity_pct = sum(
            self.layers[l]['max_mass_pct'] for l in present_layers if l != LayerType.HULL
        )

        if total_capacity_pct > 0:
            cumulative_mass_pct = 0.0
            for l_type in present_layers:
                if l_type == LayerType.HULL:
                    self.layers[l_type]['radius_pct'] = 0.0
                    continue
                cumulative_mass_pct += self.layers[l_type]['max_mass_pct']
                # Area = pi * r^2. Mass proportional to Area.
                self.layers[l_type]['radius_pct'] = math.sqrt(cumulative_mass_pct / total_capacity_pct)

    def add_component(self, component: Optional[Component], layer_type: LayerType) -> bool:
        """
        Validate and add a component to the specified layer.

        Args:
            component: The component to add (None returns False)
            layer_type: The layer to add the component to

        Returns:
            True if component was added successfully, False otherwise
        """
        if component is None:
            log_error("Attempted to add None component to ship")
            return False

        from game.simulation.entities.ship_loader import get_or_create_validator
        result = get_or_create_validator().validate_addition(self._ship, component, layer_type)

        if not result.is_valid:
            for err in result.errors:
                log_error(err)
            return False

        self.layers[layer_type]['components'].append(component)
        component.layer_assigned = layer_type
        component.ship = self._ship
        component.recalculate_stats()

        # Apply mandatory modifiers (e.g., size mount) immediately upon addition
        from game.simulation.services.modifier_service import ModifierService
        ModifierService.ensure_mandatory_modifiers(component)

        # Invalidate ship's cached summary
        if hasattr(self._ship, '_cached_summary'):
            self._ship._cached_summary = {}

        # Update Stats
        self._ship.recalculate_stats()
        return True

    def add_components_bulk(self, component: Component, layer_type: LayerType, count: int) -> int:
        """
        Add multiple copies of a component to the specified layer.

        Performs validation for each addition but defers full ship stat
        recalculation until the end.

        Args:
            component: The component to clone and add
            layer_type: The layer to add components to
            count: Number of copies to add

        Returns:
            Number of components successfully added
        """
        from game.simulation.entities.ship_loader import get_or_create_validator
        from game.simulation.services.modifier_service import ModifierService

        added_count = 0

        for _ in range(count):
            # Must clone for each new instance
            new_comp = component.clone()

            result = get_or_create_validator().validate_addition(self._ship, new_comp, layer_type)
            if not result.is_valid:
                # Stop adding if we hit a limit
                if added_count == 0:
                    for err in result.errors:
                        log_error(err)
                break

            self.layers[layer_type]['components'].append(new_comp)
            new_comp.layer_assigned = layer_type
            new_comp.ship = self._ship
            new_comp.recalculate_stats()
            ModifierService.ensure_mandatory_modifiers(new_comp)
            added_count += 1

        if added_count > 0:
            self._ship.recalculate_stats()

        return added_count

    def remove_component(self, layer_type: LayerType, index: int) -> Optional[Component]:
        """
        Remove a component from the specified layer by index.

        Args:
            layer_type: The layer to remove from
            index: Index of the component to remove

        Returns:
            The removed component, or None if index was invalid
        """
        if 0 <= index < len(self.layers[layer_type]['components']):
            comp = self.layers[layer_type]['components'].pop(index)
            self._ship.recalculate_stats()
            return comp
        log_warning(f"remove_component failed: index {index} out of range for layer {layer_type.name}")
        return None

    def get_all_components(self) -> List[Component]:
        """
        Return a list of all components across all layers.

        Returns:
            List of Component instances from all layers (HULL, CORE, INNER, OUTER, ARMOR).
            Returns a fresh list each call (not a reference to internal storage).
        """
        result = []
        for layer_data in self.layers.values():
            result.extend(layer_data['components'])
        return result

    def iter_components(self) -> Iterator[Tuple[LayerType, Component]]:
        """
        Iterate through (layer_type, component) tuples for all components.

        Yields:
            Tuple of (LayerType, Component) for each component in the ship.
            Iterates through layers in dictionary order.
        """
        for layer_type, layer_data in self.layers.items():
            for component in layer_data['components']:
                yield layer_type, component

    def get_components_by_ability(
        self,
        ability_name: str,
        operational_only: bool = True
    ) -> List[Component]:
        """
        Return all components that have a specific ability.

        Args:
            ability_name: Name of the ability to search for (e.g., 'WeaponAbility').
            operational_only: If True (default), only return operational components.
                            If False, return all components with the ability.

        Returns:
            List of Component instances that have the specified ability.
        """
        result = []
        for layer_data in self.layers.values():
            for comp in layer_data['components']:
                if operational_only and not comp.is_operational:
                    continue
                if comp.has_ability(ability_name):
                    result.append(comp)
        return result

    def get_components_by_layer(self, layer_type: LayerType) -> List[Component]:
        """
        Return all components in a specific layer.

        Args:
            layer_type: The LayerType to get components from.

        Returns:
            List of Component instances in the specified layer.
            Returns empty list if layer doesn't exist or has no components.
            Returns a fresh list each call (not a reference to internal storage).
        """
        layer_data = self.layers.get(layer_type)
        if layer_data is None:
            return []
        return list(layer_data['components'])

    def has_components(self) -> bool:
        """
        Check if ship has any components.

        Returns:
            True if ship has at least one component in any layer, False otherwise.
        """
        for layer_data in self.layers.values():
            if layer_data['components']:
                return True
        return False

    def find_component_with_index(
        self,
        predicate: Callable[[Component], bool]
    ) -> Optional[Tuple[LayerType, int, Component]]:
        """
        Find first component matching predicate, with its location.

        Args:
            predicate: Function that returns True for matching component

        Returns:
            Tuple of (layer_type, index, component) or None if not found
        """
        for layer_type, layer_data in self.layers.items():
            for idx, comp in enumerate(layer_data['components']):
                if predicate(comp):
                    return (layer_type, idx, comp)
        return None

    def clear_non_hull_components(self) -> None:
        """
        Remove all components except hull.

        Useful for ship class changes where only the hull is preserved.
        """
        for layer_type, layer_data in self.layers.items():
            if layer_type != LayerType.HULL:
                layer_data['components'].clear()
        self._ship.recalculate_stats()
