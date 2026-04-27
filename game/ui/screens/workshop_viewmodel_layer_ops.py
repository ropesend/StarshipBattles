"""Layer-resolution + movement helper for ``WorkshopViewModel`` (PROJ-309 sub-phase 3.8).

``WorkshopLayerOps`` owns the layer-restriction algorithms used for:
- quick-add ('+' button) target-layer resolution
- move-up / move-down direction search
- single-component and group movement between layers

State mutation flows back through ``self._viewmodel.add_component*`` /
``notify_ship_changed()`` exactly as the monolith. The helper itself is
stateless beyond its constructor wiring.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from game.core.constants import LayerType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.components.component import Component
    from game.simulation.services.vehicle_design_service import VehicleDesignService
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel


class WorkshopLayerOps:
    """Layer-resolution + component movement for ``WorkshopViewModel``.

    Args:
        viewmodel: The owning ``WorkshopViewModel``. Used to read ``_ship``
            and to drive ``add_component`` / ``add_component_bulk`` /
            ``notify_ship_changed`` for state mutation.
        ship_service: ``VehicleDesignService`` for validated move operations.
        registries: ``GameRegistries`` used by ``create_component`` lookups.
    """

    def __init__(
        self,
        viewmodel: "WorkshopViewModel",
        ship_service: "VehicleDesignService",
        registries: "GameRegistries",
    ) -> None:
        self._viewmodel = viewmodel
        self._ship_service = ship_service
        self._registries = registries

    # ─────────────────────────────────────────────────────────────────
    # Quick-Add (Component Palette '+' Button)
    # ─────────────────────────────────────────────────────────────────

    def resolve_target_layer(
        self,
        component: "Component",
        selected_layer: Optional[LayerType] = None,
    ) -> Optional[LayerType]:
        """Resolve which layer to place a component in for quick-add.

        Rules:
        1. If selected_layer is valid for the component, use it.
        2. If selected_layer is invalid, find the nearest valid layer
           (preferring inner layers on ties).
        3. If no selected_layer, use the innermost valid layer.
        4. HULL is never a valid quick-add target.

        Returns:
            The target LayerType, or None if no valid layer exists.
        """
        ship = self._viewmodel._ship
        if not ship:
            return None

        from game.simulation.validation.ship_validator import (
            LayerRestrictionDefinitionRule,
        )

        restriction_rule = LayerRestrictionDefinitionRule()

        # Collect valid non-HULL layers
        valid_layers = []
        for l_type in ship.layers:
            if l_type == LayerType.HULL:
                continue
            if restriction_rule.validate(ship, component, l_type).is_valid:
                valid_layers.append(l_type)

        if not valid_layers:
            return None

        # If selected layer is valid, use it directly
        if selected_layer is not None and selected_layer in valid_layers:
            return selected_layer

        # If selected layer given but invalid, find nearest valid layer
        if selected_layer is not None:
            valid_layers.sort(
                key=lambda l: (abs(l.value - selected_layer.value), l.value)
            )
            return valid_layers[0]

        # No selection: return innermost valid layer
        return min(valid_layers, key=lambda l: l.value)

    def quick_add_component(
        self,
        component_id: str,
        selected_layer: Optional[LayerType] = None,
        count: int = 1,
    ) -> bool:
        """Add a component via quick-add ('+' button in component palette).

        Resolves the target layer automatically, then adds the component.

        Returns:
            True if at least one component was added, False otherwise.
        """
        vm = self._viewmodel
        if not vm._require_ship("quick-add component"):
            return False

        from game.simulation.components.component import create_component

        comp_template = create_component(component_id, registries=self._registries)
        if comp_template is None:
            logger.warning("Quick-add failed: component '%s' not found", component_id)
            return False

        target_layer = self.resolve_target_layer(comp_template, selected_layer)
        if target_layer is None:
            logger.warning(
                "Quick-add failed: no valid layer for '%s'", component_id
            )
            return False

        # Drive state mutation through the viewmodel so its public delegators
        # remain the single seam for ship modification (and any future hooks
        # placed there).
        if count > 1:
            return vm.add_component_bulk(component_id, target_layer, count) > 0
        return vm.add_component(component_id, target_layer)

    # ─────────────────────────────────────────────────────────────────
    # Component Movement Between Layers
    # ─────────────────────────────────────────────────────────────────

    def resolve_move_target(
        self,
        component: "Component",
        source_layer: LayerType,
        direction: str,
    ) -> Optional[LayerType]:
        """Find the next valid layer in the given direction.

        Searches layer-by-layer from source_layer in the specified direction,
        skipping HULL and layers where the component fails restriction validation.

        Args:
            component: The component to move.
            source_layer: Current layer of the component.
            direction: "up" (toward inner / lower value) or "down" (toward outer).

        Returns:
            The target LayerType, or None if no valid layer in that direction.
        """
        ship = self._viewmodel._ship
        if not ship:
            return None

        from game.simulation.validation.ship_validator import (
            LayerRestrictionDefinitionRule,
        )

        restriction_rule = LayerRestrictionDefinitionRule()

        # Sort ship layers by value, excluding HULL
        ship_layers = sorted(
            [l for l in ship.layers if l != LayerType.HULL],
            key=lambda l: l.value,
        )

        if direction == "up":
            # Layers with lower value than source, in descending order (nearest first)
            candidates = [l for l in reversed(ship_layers) if l.value < source_layer.value]
        else:
            # Layers with higher value than source, in ascending order (nearest first)
            candidates = [l for l in ship_layers if l.value > source_layer.value]

        for candidate in candidates:
            if restriction_rule.validate(ship, component, candidate).is_valid:
                return candidate

        return None

    def move_component(
        self, source_layer: LayerType, index: int, target_layer: LayerType
    ) -> bool:
        """Move a single component from one layer to another.

        Preserves the component instance (modifiers, state). Mass budget
        violations produce warnings but do not block the move.

        Returns:
            True if successful, False otherwise.
        """
        vm = self._viewmodel
        if not vm._require_ship("move component"):
            return False

        result = self._ship_service.move_component(
            vm._ship, source_layer, index, target_layer
        )
        vm._last_result = result

        if result.success:
            vm.notify_ship_changed()
            return True
        else:
            logger.warning("Failed to move component: %s", result.errors)
            return False

    def move_component_group(
        self,
        group_key: str,
        source_layer: LayerType,
        target_layer: LayerType,
    ) -> bool:
        """Move all components matching a group_key from one layer to another.

        Iterates in reverse index order to avoid index shifting during removal.

        Returns:
            True if at least one component was moved, False otherwise.
        """
        vm = self._viewmodel
        if not vm._require_ship("move component group"):
            return False

        if source_layer not in vm._ship.layers:
            return False

        from game.ui.screens.builder.grouping_strategies import get_component_group_key

        # Collect indices of matching components (reverse order for safe removal)
        layer_comps = vm._ship.layers[source_layer].components
        indices = [
            i for i, c in enumerate(layer_comps)
            if get_component_group_key(c) == group_key
        ]

        if not indices:
            return False

        # Move in reverse index order to avoid shifting
        for idx in reversed(indices):
            self._ship_service.move_component(
                vm._ship, source_layer, idx, target_layer
            )

        vm.notify_ship_changed()
        return True
