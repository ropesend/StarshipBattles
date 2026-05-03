"""Ship-CRUD + attribute-setter helper for ``WorkshopViewModel`` (PROJ-309 sub-phase 3.8).

``WorkshopShipOps`` owns all ``VehicleDesignService``-backed CRUD operations
(create / add / remove / pick-up / change-class / validate / clear) plus the
ship attribute setters (name / theme / movement / targeting / design role).

Pattern (mirrors ``WorkshopShipIO`` precedent): the helper takes a back-reference
to the ``WorkshopViewModel`` so it can write to ``viewmodel._last_result`` and
fire ``viewmodel.notify_ship_changed()`` / ``_emit_ship_updated()`` exactly as
the monolith did. This is a pure refactor of internal organisation — no
behaviour change.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, List, Optional

from game.core.constants import LayerType
from game.core.error_codes import ErrorCode
from game.core.exceptions import ValidationException
from game.ui.colors import VEHICLE_DEFAULT

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship
    from game.simulation.services.vehicle_design_service import (
        DesignResult,
        VehicleDesignService,
    )
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel


class WorkshopShipOps:
    """Service-backed ship operations for ``WorkshopViewModel``.

    Args:
        viewmodel: The owning ``WorkshopViewModel``. The helper writes back to
            ``viewmodel._last_result`` and triggers state-change events through
            ``viewmodel.notify_ship_changed()`` / ``viewmodel._emit_ship_updated()``.
        ship_service: ``VehicleDesignService`` for validated ship operations.
    """

    def __init__(
        self,
        viewmodel: "WorkshopViewModel",
        ship_service: "VehicleDesignService",
    ) -> None:
        self._viewmodel = viewmodel
        self._ship_service = ship_service

    # ─────────────────────────────────────────────────────────────────
    # Service-backed CRUD
    # ─────────────────────────────────────────────────────────────────

    def create_default_ship(self, ship_class: str = "Escort") -> "Ship":
        """Create a new ship with default settings using the service.

        PROJ-40: Removed fallback to direct Ship creation - service must succeed.

        Raises:
            ValidationException: If service fails to create ship
        """
        vm = self._viewmodel
        result = self._ship_service.create_ship(
            name="Custom Ship",
            ship_class=ship_class,
            x=vm.screen_width // 2,
            y=vm.screen_height // 2,
            color=VEHICLE_DEFAULT,
        )
        vm._last_result = result

        if result.success and result.ship:
            vm.ship = result.ship
            return result.ship
        else:
            # PROJ-40: No fallback - fail fast with clear error
            error_msg = f"Failed to create ship: {result.errors}"
            logger.error(error_msg)
            raise ValidationException(
                error_msg,
                code=ErrorCode.VALIDATION_FAILED.value,
                context={"operation": "create_ship", "errors": result.errors},
            )

    def add_component(self, component_id: str, layer: LayerType) -> bool:
        """Add a component to the current ship using the service.

        Returns:
            True if successful, False otherwise
        """
        return self._viewmodel._with_ship(
            "add component",
            lambda ship: self._ship_service.add_component(ship, component_id, layer),
            lambda _result: True,
            False,
        )

    def add_component_bulk(
        self, component_id: str, layer: LayerType, count: int
    ) -> int:
        """Add multiple copies of a component using the service.

        Returns:
            Number of components successfully added
        """
        vm = self._viewmodel
        if not vm._require_ship("add components"):
            return 0

        result = self._ship_service.add_component_bulk(
            vm._ship, component_id, layer, count
        )
        vm._last_result = result

        if result.success:
            vm.notify_ship_changed()
            # Return count minus warnings about partial adds
            return count if not result.warnings else count - 1
        return 0

    def add_component_instance(
        self, component: "Component", layer: LayerType
    ) -> bool:
        """Add a pre-constructed component instance to the ship using the service.

        Unlike ``add_component()`` which creates from ID, this accepts an existing
        ``Component`` instance (e.g., one with modifiers already applied).

        Returns:
            True if successful, False otherwise
        """
        return self._viewmodel._with_ship(
            "add component instance",
            lambda ship: self._ship_service.add_component_instance(ship, component, layer),
            lambda _result: True,
            False,
        )

    def remove_component(
        self, layer: LayerType, index: int
    ) -> Optional["Component"]:
        """Remove a component from the current ship using the service.

        Returns:
            The removed component, or None if removal failed
        """
        return self._viewmodel._with_ship(
            "remove component",
            lambda ship: self._ship_service.remove_component(ship, layer, index),
            lambda result: result.removed_component,
            None,
        )

    def pick_up_component(
        self, layer: LayerType, index: int
    ) -> Optional["Component"]:
        """Remove a component for drag-and-drop pick-up.

        Delegates to ``VehicleDesignService.remove_component()`` for validated
        removal, then clears the selection. This is the correct path for the
        drag-and-drop "pick up" gesture in InteractionController — it must not
        call ``ship.remove_component()`` directly.

        Returns:
            The removed component for use as ``dragged_item``, or None if removal failed
        """
        # Route through the viewmodel's public ``remove_component`` so the
        # selection-clearing semantics stay identical to the monolith.
        removed = self._viewmodel.remove_component(layer, index)
        if removed is not None:
            self._viewmodel.clear_selection()
        return removed

    def change_ship_class(
        self, new_class: str, migrate_components: bool = True
    ) -> bool:
        """Change the ship's vehicle class using the service.

        Args:
            new_class: Target vehicle class
            migrate_components: If True, attempts to keep components and fit them
                into new layers. If False, clears all components.

        Returns:
            True if successful, False otherwise
        """
        vm = self._viewmodel
        if not vm._require_ship("change class"):
            return False

        result = self._ship_service.change_class(
            vm._ship, new_class, migrate_components=migrate_components
        )
        vm._last_result = result

        if result.success:
            vm.clear_selection()
            vm.notify_ship_changed()
            return True
        else:
            logger.warning(f"Failed to change class: {result.errors}")
            return False

    def validate_design(self) -> Any:
        """Validate the current ship design using the service.

        Returns:
            ValidationResult from the service, or None if no ship.
        """
        vm = self._viewmodel
        if not vm._ship:
            return None
        return self._ship_service.validate_design(vm._ship)

    def get_available_components_for_layer(self, layer: LayerType) -> List[str]:
        """Get component IDs that can be added to the specified layer."""
        vm = self._viewmodel
        if not vm._ship:
            return []
        return self._ship_service.get_available_components(vm._ship, layer)

    def get_ship_summary(self) -> dict:
        """Get a summary of the current ship's stats."""
        vm = self._viewmodel
        if not vm._ship:
            return {}
        return self._ship_service.get_ship_summary(vm._ship)

    def clear_design(self) -> None:
        """Clear the current ship design (keeping hull)."""
        vm = self._viewmodel
        if not vm._require_ship("clear design"):
            return

        logger.info("Clearing ship design")
        vm._ship.clear_non_hull_components()

        vm._ship.movement_policy = "kite_max"
        vm._ship.targeting_policy = "standard"
        vm._ship.name = "Custom Ship"

        vm.clear_selection()
        vm.notify_ship_changed()

    # ─────────────────────────────────────────────────────────────────
    # Ship attribute setters (direct mutation + SHIP_UPDATED)
    # ─────────────────────────────────────────────────────────────────

    def set_ship_name(self, name: str) -> None:
        """Set the ship's name via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if name is unchanged.
        """
        vm = self._viewmodel
        if not vm._require_ship("set ship name"):
            return

        if vm._ship.name == name:
            return  # No change, skip event emission

        vm._ship.name = name
        vm._emit_ship_updated()

    def set_ship_theme(self, theme_id: str) -> None:
        """Set the ship's visual theme via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if theme is unchanged.
        """
        vm = self._viewmodel
        if not vm._require_ship("set ship theme"):
            return

        if vm._ship.theme_id == theme_id:
            return  # No change, skip event emission

        vm._ship.theme_id = theme_id
        vm._emit_ship_updated()

    def set_ship_movement_policy(self, policy_id: str) -> None:
        """Set the ship's movement policy via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if policy is unchanged.
        """
        vm = self._viewmodel
        if not vm._require_ship("set movement policy"):
            return

        if vm._ship.movement_policy == policy_id:
            return  # No change, skip event emission

        vm._ship.movement_policy = policy_id
        vm._emit_ship_updated()

    def set_ship_targeting_policy(self, policy_id: str) -> None:
        """Set the ship's targeting policy via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if policy is unchanged.
        """
        vm = self._viewmodel
        if not vm._require_ship("set targeting policy"):
            return

        if vm._ship.targeting_policy == policy_id:
            return  # No change, skip event emission

        vm._ship.targeting_policy = policy_id
        vm._emit_ship_updated()

    def set_ship_design_role(self, role_id: str) -> None:
        """Set the ship's design role via the ViewModel.

        Args:
            role_id: Design role identifier (e.g., "line_combatant", "carrier")
        """
        vm = self._viewmodel
        if not vm._require_ship("set design role"):
            return

        if vm._ship.design_role == role_id:
            return

        vm._ship.design_role = role_id
        vm._emit_ship_updated()
