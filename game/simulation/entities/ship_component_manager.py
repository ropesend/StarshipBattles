"""ShipComponentManager -- Component lifecycle and access for Ship.

PROJ-240 Phase 1: Extracted from Ship god class.
Ship retains facade methods that delegate here.
"""
import logging
from typing import Callable, List, Tuple, Optional, Iterator, TYPE_CHECKING

from game.core.constants import LayerType
from game.simulation.components.component import Component

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship

logger = logging.getLogger(__name__)


class ShipComponentManager:
    """Manages component lifecycle, caching, and queries for a Ship.

    Owns:
    - Component add/remove/bulk operations
    - Flat component list cache (dirty-flag invalidation)
    - Weapon component cache (dirty-flag invalidation)
    - Component iteration and query methods

    Args:
        ship: The Ship instance this manager serves.
    """

    def __init__(self, ship: 'Ship') -> None:
        self._ship = ship
        # Cache state (moved from Ship.__init__)
        self._components_cache: Optional[List[Component]] = None
        self._components_dirty: bool = True
        self._weapons_cache: Optional[List[Component]] = None
        self._weapons_cache_dirty: bool = True  # PROJ-240 FIX: dirty-flag replaces tick coupling

    # =========================================================================
    # Cache Management
    # =========================================================================

    def _invalidate_components_cache(self) -> None:
        """Mark component caches as dirty for lazy recalculation.

        PROJ-240: Also invalidates weapons cache (was missing before).
        """
        self._components_dirty = True
        self._components_cache = None
        self._weapons_cache_dirty = True

    # =========================================================================
    # Component Attachment (Internal)
    # =========================================================================

    def _attach_component(self, component: Component, layer_type: LayerType,
                          modifier_service=None) -> None:
        """Attach a validated component to a layer and apply mandatory modifiers.

        PROJ-225: Extracted from duplicated logic in add_component and add_components_bulk.
        Does NOT validate or trigger recalculate_stats - caller is responsible for both.

        Args:
            component: The component to attach (must already be validated)
            layer_type: Target layer
            modifier_service: Optional pre-created ModifierService (for bulk efficiency)
        """
        self._ship.layers[layer_type].components.append(component)
        component.layer_assigned = layer_type
        component.ship = self._ship
        component.recalculate_stats()
        # Apply mandatory modifiers (e.g., size mount) immediately upon addition
        if modifier_service is None:
            # LATE IMPORT: services/__init__.py imports VehicleDesignService which imports Ship
            from game.simulation.services.modifier_service import ModifierService
            modifier_service = ModifierService(
                modifier_registry=self._ship._registries.modifiers
            )
        modifier_service.ensure_mandatory_modifiers(component)

    # =========================================================================
    # Component Add / Remove / Bulk
    # =========================================================================

    def add_component(self, component: Component, layer_type: LayerType) -> bool:
        """Validate and add a component to the specified layer."""
        if component is None:
            logger.error("Attempted to add None component to ship")
            return False

        from game.simulation.entities.ship_loader import get_or_create_validator

        # PROJ-252: Use Ship's registries (GameRegistries implements IRegistryProvider)
        result = get_or_create_validator(
            registry_provider=self._ship._registries
        ).validate_addition(self._ship, component, layer_type)

        if not result.is_valid:
            for err in result.errors:
                logger.error(err)
            return False

        self._attach_component(component, layer_type)
        self._ship._cached_summary = {}  # Invalidate UI cache
        self._invalidate_components_cache()

        # Update Stats
        self._ship.recalculate_stats()
        return True

    def add_components_bulk(self, component: Component, layer_type: LayerType,
                            count: int) -> int:
        """Add multiple copies of a component to the specified layer.

        Performs validation for each addition but defers full ship stat
        recalculation until the end.
        Returns the number of components successfully added.
        """
        added_count = 0

        # PROJ-225: Create modifier service once for all additions (not per-component)
        from game.simulation.services.modifier_service import ModifierService
        modifier_service = ModifierService(
            modifier_registry=self._ship._registries.modifiers
        )

        from game.simulation.entities.ship_loader import get_or_create_validator

        for _ in range(count):
            # Must clone for each new instance
            new_comp = component.clone()

            # PROJ-252: Use Ship's registries (GameRegistries implements IRegistryProvider)
            result = get_or_create_validator(
                registry_provider=self._ship._registries
            ).validate_addition(self._ship, new_comp, layer_type)
            if not result.is_valid:
                # Stop adding if we hit a limit
                if added_count == 0:
                    # If the very first one fails, log errors
                    for err in result.errors:
                        logger.error(err)
                break

            self._attach_component(new_comp, layer_type, modifier_service=modifier_service)
            added_count += 1

        if added_count > 0:
            self._invalidate_components_cache()
            self._ship.recalculate_stats()

        return added_count

    def remove_component(self, layer_type: LayerType, index: int) -> Optional[Component]:
        """Remove a component from the specified layer by index."""
        if 0 <= index < len(self._ship.layers[layer_type].components):
            comp = self._ship.layers[layer_type].components.pop(index)
            self._invalidate_components_cache()
            self._ship.recalculate_stats()
            return comp
        logger.warning(
            f"remove_component failed: index {index} out of range "
            f"for layer {layer_type.name}"
        )
        return None

    # =========================================================================
    # Component Access / Query Methods
    # =========================================================================

    def get_all_components(self) -> List[Component]:
        """Return a cached list of all components across all layers.

        PROJ-240 FIX: Returns a defensive copy so callers cannot corrupt
        the internal cache.

        Returns:
            List of Component instances from all layers.
        """
        if self._components_dirty or self._components_cache is None:
            result = []
            for layer_data in self._ship.layers.values():
                result.extend(layer_data.components)
            self._components_cache = result
            self._components_dirty = False
        return list(self._components_cache)  # Defensive copy

    def iter_components(self) -> Iterator[Tuple[LayerType, Component]]:
        """Iterate through (layer_type, component) tuples for all components.

        Yields:
            Tuple of (LayerType, Component) for each component in the ship.
            Iterates through layers in dictionary order.
        """
        for layer_type, layer_data in self._ship.layers.items():
            for component in layer_data.components:
                yield layer_type, component

    def get_components_by_ability(
        self,
        ability_name: str,
        operational_only: bool = True
    ) -> List[Component]:
        """Return all components that have a specific ability.

        Args:
            ability_name: Name of the ability to search for (e.g., 'WeaponAbility').
            operational_only: If True (default), only return operational components.
                            If False, return all components with the ability.

        Returns:
            List of Component instances that have the specified ability.
        """
        result = []
        for layer_data in self._ship.layers.values():
            for comp in layer_data.components:
                if operational_only and not comp.is_operational:
                    continue
                if comp.has_ability(ability_name):
                    result.append(comp)
        return result

    def get_weapon_components_cached(self) -> List[Component]:
        """Get weapon components, cached until invalidated.

        PROJ-240 FIX: Uses dirty-flag invalidation instead of tick parameter.
        Cache is invalidated on component add/remove/stats recalculation.

        Returns:
            List of operational Component instances with WeaponAbility.
        """
        if self._weapons_cache_dirty or self._weapons_cache is None:
            self._weapons_cache = self.get_components_by_ability(
                'WeaponAbility', operational_only=True
            )
            self._weapons_cache_dirty = False
        return list(self._weapons_cache)  # Defensive copy (see get_all_components)

    def get_components_by_layer(self, layer_type: LayerType) -> List[Component]:
        """Return all components in a specific layer.

        Args:
            layer_type: The LayerType to get components from.

        Returns:
            List of Component instances in the specified layer.
            Returns empty list if layer doesn't exist or has no components.
            Returns a fresh list each call (not a reference to internal storage).
        """
        layer_data = self._ship.layers.get(layer_type)
        if layer_data is None:
            return []
        return list(layer_data.components)

    def has_components(self) -> bool:
        """Check if ship has any components.

        Returns:
            True if ship has at least one component in any layer, False otherwise.
        """
        for layer_data in self._ship.layers.values():
            if layer_data.components:
                return True
        return False

    def find_component_with_index(
        self,
        predicate: Callable[[Component], bool]
    ) -> Optional[Tuple[LayerType, int, Component]]:
        """Find first component matching predicate, with its location.

        Args:
            predicate: Function that returns True for matching component

        Returns:
            Tuple of (layer_type, index, component) or None if not found
        """
        for layer_type, layer_data in self._ship.layers.items():
            for idx, comp in enumerate(layer_data.components):
                if predicate(comp):
                    return (layer_type, idx, comp)
        return None

    def clear_non_hull_components(self) -> None:
        """Remove all components except hull.

        Useful for ship class changes where only the hull is preserved.
        """
        for layer_type, layer_data in self._ship.layers.items():
            if layer_type != LayerType.HULL:
                layer_data.components.clear()
        self._invalidate_components_cache()
        self._ship.recalculate_stats()
