"""
WorkshopViewModel - Central ViewModel for Design Workshop MVVM architecture (renamed from BuilderViewModel).

Manages all workshop state and notifies views via EventBus when state changes.
Extracted from DesignWorkshopScreen for better separation of concerns and testability.

Uses VehicleDesignService for ship operations, providing validation and error handling.

PROJ-38: Added context parameter for dependency injection via WorkshopContext.
PROJ-40: Moved cross-layer imports to TYPE_CHECKING, removed backward-compat fallbacks.
PROJ-309 sub-phase 3.8: Internal decomposition into ``WorkshopShipOps``,
    ``WorkshopLayerOps`` and ``workshop_viewmodel_selection`` helpers. Public API
    surface unchanged — every method/property remains on this class as a one-line
    delegator. Selection state still lives here.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional, TYPE_CHECKING, Tuple

from game.core.constants import LayerType
from game.core.error_codes import ErrorCode
from game.core.exceptions import ValidationException
from game.simulation.services.vehicle_design_service import VehicleDesignService
from game.ui.screens.builder_utils import BuilderEvents
from game.ui.screens.workshop_viewmodel_layer_ops import WorkshopLayerOps
from game.ui.screens.workshop_viewmodel_selection import (
    apply_append_selection,
    normalize_selection,
    sync_modifiers_to_selection,
)
from game.ui.screens.workshop_viewmodel_ship_ops import WorkshopShipOps

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship
    from game.simulation.services.vehicle_design_service import DesignResult
    from game.ui.screens.workshop_context import WorkshopContext


class WorkshopViewModel:
    """Central ViewModel for Design Workshop (renamed from BuilderViewModel).

    Holds all builder state and emits events via EventBus when state changes.
    Views subscribe to events and update themselves accordingly.

    Events emitted:
        - SHIP_UPDATED: When ship or its properties change
        - SELECTION_CHANGED: When component selection changes
        - TEMPLATE_MODIFIERS_CHANGED: When template modifiers change
        - DRAG_STATE_CHANGED: When drag operation starts/ends

    Internal organisation (PROJ-309 sub-phase 3.8):
        - Selection algorithms: ``workshop_viewmodel_selection`` module-level functions.
          Selection STATE lives on this class.
        - Service-backed CRUD + attribute setters: ``WorkshopShipOps`` (private ``_ship_ops``).
        - Layer-restriction + movement: ``WorkshopLayerOps`` (private ``_layer_ops``).

        Every public method on this class is the same name and signature as before;
        the helpers are an internal implementation detail.
    """

    def __init__(
        self,
        event_bus,
        screen_width: int,
        screen_height: int,
        *,
        context: Optional["WorkshopContext"] = None,
    ):
        """Initialize the ViewModel.

        PROJ-38: Added context parameter for dependency injection.
        PROJ-40: Context with registries is now required (no fallback to globals).

        Args:
            event_bus: EventBus instance for emitting state change notifications
            screen_width: Screen width for ship positioning
            screen_height: Screen height for ship positioning
            context: WorkshopContext with registries for DI (required for proper operation)

        Raises:
            ValidationException: If context is None or context.registries is None
        """
        self.event_bus = event_bus
        self.screen_width = screen_width
        self.screen_height = screen_height

        # PROJ-40: Require registries via context (no fallback)
        if context is None or context.registries is None:
            raise ValidationException(
                "WorkshopViewModel requires registries in context",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "WorkshopViewModel", "missing": "context.registries"},
            )
        self._registries: "GameRegistries" = context.registries

        # Service layer for ship operations - PROJ-38: Pass registries
        self._ship_service = VehicleDesignService(registries=self._registries)

        # Last operation result (for error display)
        self._last_result: Optional["DesignResult"] = None

        # Core state
        self._ship: Optional["Ship"] = None
        self._selected_components: List[Tuple[LayerType, int, "Component"]] = []
        self._dragged_item: Optional["Component"] = None
        self._available_components: List["Component"] = []
        self._show_hull_layer: bool = False

        # PROJ-309 sub-phase 3.8: Compose the helper modules. Selection helpers
        # are module-level functions (no state), so they aren't bound here.
        self._ship_ops = WorkshopShipOps(self, self._ship_service)
        self._layer_ops = WorkshopLayerOps(self, self._ship_service, self._registries)

    def _require_ship(self, operation: str) -> bool:
        """Check if a ship is loaded. Logs warning if not.

        Returns True if ship exists, False otherwise.
        """
        if not self._ship:
            logger.warning("Cannot %s: no ship loaded", operation)
            return False
        return True

    # ─────────────────────────────────────────────────────────────────
    # Ship Property
    # ─────────────────────────────────────────────────────────────────

    @property
    def ship(self) -> Optional["Ship"]:
        """The ship currently being edited."""
        return self._ship

    @ship.setter
    def ship(self, value: "Ship") -> None:
        self._ship = value
        self._emit_ship_updated()

    def _emit_ship_updated(self) -> None:
        """Emit SHIP_UPDATED event."""
        self.event_bus.emit(BuilderEvents.SHIP_UPDATED, self._ship)

    def notify_ship_changed(self) -> None:
        """Call when ship's internal state has changed (e.g., components added)."""
        if self._ship:
            self._ship.recalculate_stats()
        self._emit_ship_updated()

    # ─────────────────────────────────────────────────────────────────
    # Selection Property
    # ─────────────────────────────────────────────────────────────────

    @property
    def selected_components(self) -> List[Tuple[LayerType, int, "Component"]]:
        """List of currently selected components as (layer, index, component) tuples."""
        return self._selected_components

    @selected_components.setter
    def selected_components(
        self, value: List[Tuple[LayerType, int, "Component"]]
    ) -> None:
        """Set the selected components list directly."""
        self._selected_components = value

    @property
    def primary_selection(self) -> Optional[Tuple[LayerType, int, "Component"]]:
        """The primary (last) selected component, or None if nothing selected."""
        return self._selected_components[-1] if self._selected_components else None

    def select_component(
        self, new_selection, append: bool = False, toggle: bool = False
    ) -> None:
        """Handle selection changes.

        Args:
            new_selection: Single component tuple (layer, idx, comp), list of them, or None
            append: If True, add to existing selection instead of replacing
            toggle: If True, toggles selection state of existing items (Ctrl+Click)
        """
        if new_selection is None:
            if not append:
                self._selected_components = []
        else:
            if not isinstance(new_selection, list):
                new_selection = [new_selection]

            # Normalize to tuples
            norm_selection = self._normalize_selection(new_selection)

            if append:
                self._handle_append_selection(norm_selection, toggle)
            else:
                self._selected_components = norm_selection

        self._emit_selection_changed()

    def _normalize_selection(
        self, items: List
    ) -> List[Tuple[LayerType, int, "Component"]]:
        """Convert various selection formats to normalized tuples.

        Thin wrapper over ``workshop_viewmodel_selection.normalize_selection``.
        """
        return normalize_selection(items, self._ship)

    def _handle_append_selection(self, norm_selection: List, toggle: bool) -> None:
        """Handle append/toggle selection logic.

        Thin wrapper over ``workshop_viewmodel_selection.apply_append_selection``.
        """
        self._selected_components = apply_append_selection(
            self._selected_components, norm_selection, toggle
        )

    def _emit_selection_changed(self) -> None:
        """Emit SELECTION_CHANGED event."""
        self.event_bus.emit(BuilderEvents.SELECTION_CHANGED, self.primary_selection)

    def clear_selection(self) -> None:
        """Clear all selected components."""
        self._selected_components = []
        self._emit_selection_changed()

    # ─────────────────────────────────────────────────────────────────
    # Drag State Property
    # ─────────────────────────────────────────────────────────────────

    @property
    def dragged_item(self) -> Optional["Component"]:
        """The component currently being dragged, or None."""
        return self._dragged_item

    @dragged_item.setter
    def dragged_item(self, value: Optional["Component"]) -> None:
        self._dragged_item = value
        self.event_bus.emit(BuilderEvents.DRAG_STATE_CHANGED, value)

    # ─────────────────────────────────────────────────────────────────
    # Available Components Property
    # ─────────────────────────────────────────────────────────────────

    @property
    def available_components(self) -> List["Component"]:
        """List of available components for the current ship configuration."""
        return self._available_components

    def refresh_available_components(self) -> None:
        """Refresh the available components list from registry.

        PROJ-40: Removed fallback to global get_all_components() - use registries.
        """
        self._available_components = list(self._registries.components.values())

    # ─────────────────────────────────────────────────────────────────
    # Hull Layer Visibility
    # ─────────────────────────────────────────────────────────────────

    @property
    def show_hull_layer(self) -> bool:
        """Whether the hull layer is visible in the structure panel."""
        return self._show_hull_layer

    @show_hull_layer.setter
    def show_hull_layer(self, value: bool) -> None:
        if self._show_hull_layer != value:
            self._show_hull_layer = value
            self.event_bus.emit(BuilderEvents.HULL_LAYER_VISIBILITY_CHANGED, value)

    def toggle_hull_layer(self) -> bool:
        """Toggle hull layer visibility and return the new state."""
        self.show_hull_layer = not self._show_hull_layer
        return self._show_hull_layer

    # ─────────────────────────────────────────────────────────────────
    # Modifier Synchronization
    # ─────────────────────────────────────────────────────────────────

    def on_modifier_changed(self) -> None:
        """Called when any modifier changes on the primary selected component.

        Syncs modifiers to other selected components (multi-selection),
        then always triggers ship stat recalculation and SHIP_UPDATED event.
        """
        if not self._selected_components:
            return

        if len(self._selected_components) > 1:
            self._sync_modifiers_to_selection()

        self.notify_ship_changed()

    def _sync_modifiers_to_selection(self) -> None:
        """Copy modifiers from primary to all other selected components.

        Thin wrapper over ``workshop_viewmodel_selection.sync_modifiers_to_selection``.
        """
        primary = self.primary_selection
        if not primary:
            return
        sync_modifiers_to_selection(primary[2], self._selected_components)

    # ─────────────────────────────────────────────────────────────────
    # Result Accessors (Service-backed operation results)
    # ─────────────────────────────────────────────────────────────────

    @property
    def last_result(self) -> Optional["DesignResult"]:
        """The result of the last service operation."""
        return self._last_result

    @property
    def last_errors(self) -> List[str]:
        """Errors from the last operation, if any."""
        return self._last_result.errors if self._last_result else []

    @property
    def last_warnings(self) -> List[str]:
        """Warnings from the last operation, if any."""
        return self._last_result.warnings if self._last_result else []

    # ─────────────────────────────────────────────────────────────────
    # Ship Operations — delegated to WorkshopShipOps
    # ─────────────────────────────────────────────────────────────────

    def create_default_ship(self, ship_class: str = "Escort") -> "Ship":
        """Create a new ship with default settings using the service.

        Raises:
            ValidationException: If service fails to create ship
        """
        return self._ship_ops.create_default_ship(ship_class)

    def add_component(self, component_id: str, layer: LayerType) -> bool:
        """Add a component to the current ship using the service."""
        return self._ship_ops.add_component(component_id, layer)

    def add_component_bulk(
        self, component_id: str, layer: LayerType, count: int
    ) -> int:
        """Add multiple copies of a component using the service."""
        return self._ship_ops.add_component_bulk(component_id, layer, count)

    def add_component_instance(
        self, component: "Component", layer: LayerType
    ) -> bool:
        """Add a pre-constructed component instance to the ship using the service."""
        return self._ship_ops.add_component_instance(component, layer)

    def remove_component(
        self, layer: LayerType, index: int
    ) -> Optional["Component"]:
        """Remove a component from the current ship using the service."""
        return self._ship_ops.remove_component(layer, index)

    def pick_up_component(
        self, layer: LayerType, index: int
    ) -> Optional["Component"]:
        """Remove a component for drag-and-drop pick-up.

        Delegates to ``VehicleDesignService.remove_component()`` for validated
        removal, then clears the selection.
        """
        return self._ship_ops.pick_up_component(layer, index)

    def change_ship_class(
        self, new_class: str, migrate_components: bool = True
    ) -> bool:
        """Change the ship's vehicle class using the service."""
        return self._ship_ops.change_ship_class(new_class, migrate_components)

    def validate_design(self) -> Any:
        """Validate the current ship design using the service."""
        return self._ship_ops.validate_design()

    def get_available_components_for_layer(self, layer: LayerType) -> List[str]:
        """Get component IDs that can be added to the specified layer."""
        return self._ship_ops.get_available_components_for_layer(layer)

    def get_ship_summary(self) -> dict:
        """Get a summary of the current ship's stats."""
        return self._ship_ops.get_ship_summary()

    def clear_design(self) -> None:
        """Clear the current ship design (keeping hull)."""
        self._ship_ops.clear_design()

    def set_ship_name(self, name: str) -> None:
        """Set the ship's name via the ViewModel."""
        self._ship_ops.set_ship_name(name)

    def set_ship_theme(self, theme_id: str) -> None:
        """Set the ship's visual theme via the ViewModel."""
        self._ship_ops.set_ship_theme(theme_id)

    def set_ship_movement_policy(self, policy_id: str) -> None:
        """Set the ship's movement policy via the ViewModel."""
        self._ship_ops.set_ship_movement_policy(policy_id)

    def set_ship_targeting_policy(self, policy_id: str) -> None:
        """Set the ship's targeting policy via the ViewModel."""
        self._ship_ops.set_ship_targeting_policy(policy_id)

    def set_ship_design_role(self, role_id: str) -> None:
        """Set the ship's design role via the ViewModel."""
        self._ship_ops.set_ship_design_role(role_id)

    # ─────────────────────────────────────────────────────────────────
    # Layer Resolution + Quick-Add — delegated to WorkshopLayerOps
    # ─────────────────────────────────────────────────────────────────

    def resolve_target_layer(
        self,
        component: "Component",
        selected_layer: Optional[LayerType] = None,
    ) -> Optional[LayerType]:
        """Resolve which layer to place a component in for quick-add."""
        return self._layer_ops.resolve_target_layer(component, selected_layer)

    def quick_add_component(
        self,
        component_id: str,
        selected_layer: Optional[LayerType] = None,
        count: int = 1,
    ) -> bool:
        """Add a component via quick-add ('+' button in component palette)."""
        return self._layer_ops.quick_add_component(
            component_id, selected_layer, count
        )

    # ─────────────────────────────────────────────────────────────────
    # Component Movement Between Layers — delegated to WorkshopLayerOps
    # ─────────────────────────────────────────────────────────────────

    def resolve_move_target(
        self,
        component: "Component",
        source_layer: LayerType,
        direction: str,
    ) -> Optional[LayerType]:
        """Find the next valid layer in the given direction."""
        return self._layer_ops.resolve_move_target(component, source_layer, direction)

    def move_component(
        self, source_layer: LayerType, index: int, target_layer: LayerType
    ) -> bool:
        """Move a single component from one layer to another."""
        return self._layer_ops.move_component(source_layer, index, target_layer)

    def move_component_group(
        self,
        group_key: str,
        source_layer: LayerType,
        target_layer: LayerType,
    ) -> bool:
        """Move all components matching a group_key from one layer to another."""
        return self._layer_ops.move_component_group(
            group_key, source_layer, target_layer
        )
