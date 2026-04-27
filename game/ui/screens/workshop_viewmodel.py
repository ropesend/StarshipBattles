"""
WorkshopViewModel - Central ViewModel for Design Workshop MVVM architecture (renamed from BuilderViewModel).

Manages all workshop state and notifies views via EventBus when state changes.
Extracted from DesignWorkshopScreen for better separation of concerns and testability.

Uses VehicleDesignService for ship operations, providing validation and error handling.

PROJ-38: Added context parameter for dependency injection via WorkshopContext.
PROJ-40: Moved cross-layer imports to TYPE_CHECKING, removed backward-compat fallbacks.
"""
from __future__ import annotations

from typing import List, Tuple, Optional, TYPE_CHECKING, Any

from game.simulation.services.vehicle_design_service import VehicleDesignService
from game.ui.screens.builder_utils import BuilderEvents
from game.ui.colors import VEHICLE_DEFAULT
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.core.constants import LayerType

import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component
    from game.simulation.services.vehicle_design_service import DesignResult
    from game.ui.screens.workshop_context import WorkshopContext
    from game.core.registry import GameRegistries


class WorkshopViewModel:
    """
    Central ViewModel for Design Workshop (renamed from BuilderViewModel).
    
    Holds all builder state and emits events via EventBus when state changes.
    Views subscribe to events and update themselves accordingly.
    
    Events emitted:
        - SHIP_UPDATED: When ship or its properties change
        - SELECTION_CHANGED: When component selection changes
        - TEMPLATE_MODIFIERS_CHANGED: When template modifiers change
        - DRAG_STATE_CHANGED: When drag operation starts/ends
    """
    
    def __init__(self, event_bus, screen_width: int, screen_height: int,
                 *, context: Optional[WorkshopContext] = None):
        """
        Initialize the ViewModel.

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
                context={"class": "WorkshopViewModel", "missing": "context.registries"}
            )
        self._registries: GameRegistries = context.registries

        # Service layer for ship operations - PROJ-38: Pass registries
        self._ship_service = VehicleDesignService(registries=self._registries)

        # Last operation result (for error display)
        self._last_result: Optional[DesignResult] = None

        # Core state
        self._ship: Optional[Ship] = None
        self._selected_components: List[Tuple[LayerType, int, Component]] = []
        self._dragged_item: Optional[Component] = None
        self._available_components: List[Component] = []
        self._show_hull_layer: bool = False
        
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
    def ship(self) -> Optional[Ship]:
        """The ship currently being edited."""
        return self._ship
    
    @ship.setter
    def ship(self, value: Ship) -> None:
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
    def selected_components(self) -> List[Tuple[LayerType, int, Component]]:
        """List of currently selected components as (layer, index, component) tuples."""
        return self._selected_components

    @selected_components.setter
    def selected_components(self, value: List[Tuple[LayerType, int, Component]]) -> None:
        """Set the selected components list directly."""
        self._selected_components = value

    @property
    def primary_selection(self) -> Optional[Tuple[LayerType, int, Component]]:
        """The primary (last) selected component, or None if nothing selected."""
        return self._selected_components[-1] if self._selected_components else None

    def select_component(self, new_selection, append: bool = False, toggle: bool = False) -> None:
        """
        Handle selection changes.
        
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
        
    def _normalize_selection(self, items: List) -> List[Tuple[LayerType, int, Component]]:
        """Convert various selection formats to normalized tuples.

        Uses duck typing (hasattr check for 'id') because selection logic accepts
        both real Component instances and mock objects in tests.
        """
        norm_selection = []
        for item in items:
            if isinstance(item, tuple) and len(item) == 3:
                norm_selection.append(item)
            elif hasattr(item, 'id'):  # Component-like object
                # Find it in ship
                found = False
                if self._ship:
                    for l_type, l_data in self._ship.layers.items():
                        try:
                            idx = l_data.components.index(item)
                            norm_selection.append((l_type, idx, item))
                            found = True
                            break
                        except ValueError:
                            continue
                if not found:
                    # Template/dragged component
                    norm_selection.append((None, -1, item))
        return norm_selection
        
    def _handle_append_selection(self, norm_selection: List, toggle: bool) -> None:
        """Handle append/toggle selection logic."""
        if not self._selected_components:
            self._selected_components = norm_selection
            return
            
        if not norm_selection:
            return
            
        # Enforce homogeneity - all selected must be same component type
        current_def_id = self._selected_components[0][2].id
        matches_type = all(item[2].id == current_def_id for item in norm_selection)
        
        if not matches_type:
            # Different type - replace selection
            self._selected_components = norm_selection
            return
            
        # Add/toggle unique items (by object identity)
        current_objs = {c[2] for c in self._selected_components}
        for item in norm_selection:
            if item[2] in current_objs:
                if toggle:
                    # Toggle OFF
                    self._selected_components = [
                        x for x in self._selected_components if x[2] is not item[2]
                    ]
            else:
                self._selected_components.append(item)
                
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
    def dragged_item(self) -> Optional[Component]:
        """The component currently being dragged, or None."""
        return self._dragged_item
    
    @dragged_item.setter
    def dragged_item(self, value: Optional[Component]) -> None:
        self._dragged_item = value
        self.event_bus.emit(BuilderEvents.DRAG_STATE_CHANGED, value)
        
    # ─────────────────────────────────────────────────────────────────
    # Available Components Property
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def available_components(self) -> List[Component]:
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
        """Copy modifiers from primary to all other selected components."""
        primary = self.primary_selection
        if not primary:
            return

        editing_comp = primary[2]

        for item in self._selected_components:
            comp = item[2]
            if comp is editing_comp:
                continue

            from game.ui.screens.builder.modifier_utils import copy_modifiers
            copy_modifiers(editing_comp, comp)
        
    # ─────────────────────────────────────────────────────────────────
    # Ship Operations (Service-backed)
    # ─────────────────────────────────────────────────────────────────

    @property
    def last_result(self) -> Optional[DesignResult]:
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

    def create_default_ship(self, ship_class: str = "Escort") -> Ship:
        """Create a new ship with default settings using the service.

        PROJ-40: Removed fallback to direct Ship creation - service must succeed.

        Raises:
            ValidationException: If service fails to create ship
        """
        result = self._ship_service.create_ship(
            name="Custom Ship",
            ship_class=ship_class,
            x=self.screen_width // 2,
            y=self.screen_height // 2,
            color=VEHICLE_DEFAULT
        )
        self._last_result = result

        if result.success and result.ship:
            self.ship = result.ship
            return result.ship
        else:
            # PROJ-40: No fallback - fail fast with clear error
            error_msg = f"Failed to create ship: {result.errors}"
            logger.error(error_msg)
            raise ValidationException(
                error_msg,
                code=ErrorCode.VALIDATION_FAILED.value,
                context={"operation": "create_ship", "errors": result.errors}
            )

    def add_component(self, component_id: str, layer: LayerType) -> bool:
        """
        Add a component to the current ship using the service.

        Args:
            component_id: ID of the component to add
            layer: Target layer

        Returns:
            True if successful, False otherwise
        """
        if not self._require_ship("add component"):
            return False

        result = self._ship_service.add_component(self._ship, component_id, layer)
        self._last_result = result

        if result.success:
            self.notify_ship_changed()
            return True
        else:
            logger.warning(f"Failed to add component: {result.errors}")
            return False

    def add_component_bulk(self, component_id: str, layer: LayerType, count: int) -> int:
        """
        Add multiple copies of a component using the service.

        Args:
            component_id: ID of the component to add
            layer: Target layer
            count: Number of copies to add

        Returns:
            Number of components successfully added
        """
        if not self._require_ship("add components"):
            return 0

        result = self._ship_service.add_component_bulk(
            self._ship, component_id, layer, count
        )
        self._last_result = result

        if result.success:
            self.notify_ship_changed()
            # Return count minus warnings about partial adds
            return count if not result.warnings else count - 1
        return 0

    def add_component_instance(self, component: Component, layer: LayerType) -> bool:
        """
        Add a pre-constructed component instance to the ship using the service.

        Unlike add_component() which creates from ID, this accepts an existing
        Component instance (e.g., one with modifiers already applied).

        Args:
            component: The component instance to add
            layer: Target layer

        Returns:
            True if successful, False otherwise
        """
        if not self._require_ship("add component instance"):
            return False

        result = self._ship_service.add_component_instance(self._ship, component, layer)
        self._last_result = result

        if result.success:
            self.notify_ship_changed()
            return True
        else:
            logger.warning(f"Failed to add component instance: {result.errors}")
            return False

    def remove_component(self, layer: LayerType, index: int) -> Optional[Component]:
        """
        Remove a component from the current ship using the service.

        Args:
            layer: Layer containing the component
            index: Index of the component

        Returns:
            The removed component, or None if removal failed
        """
        if not self._require_ship("remove component"):
            return None

        result = self._ship_service.remove_component(self._ship, layer, index)
        self._last_result = result

        if result.success:
            self.notify_ship_changed()
            return result.removed_component
        else:
            logger.warning(f"Failed to remove component: {result.errors}")
            return None

    def pick_up_component(self, layer: LayerType, index: int) -> Optional[Component]:
        """Remove a component for drag-and-drop pick-up.

        Delegates to VehicleDesignService.remove_component() for validated removal,
        then clears the selection. This is the correct path for the drag-and-drop
        "pick up" gesture in InteractionController — it must not call
        ship.remove_component() directly.

        Args:
            layer: Layer containing the component
            index: Index of the component to remove

        Returns:
            The removed component for use as dragged_item, or None if removal failed
        """
        removed = self.remove_component(layer, index)
        if removed is not None:
            self.clear_selection()
        return removed

    def change_ship_class(self, new_class: str, migrate_components: bool = True) -> bool:
        """
        Change the ship's vehicle class using the service.

        Args:
            new_class: Target vehicle class
            migrate_components: If True, attempts to keep components and fit them
                                into new layers. If False, clears all components.

        Returns:
            True if successful, False otherwise
        """
        if not self._require_ship("change class"):
            return False

        result = self._ship_service.change_class(
            self._ship, new_class, migrate_components=migrate_components
        )
        self._last_result = result

        if result.success:
            self.clear_selection()
            self.notify_ship_changed()
            return True
        else:
            logger.warning(f"Failed to change class: {result.errors}")
            return False

    def validate_design(self) -> Any:
        """
        Validate the current ship design using the service.

        Returns:
            ValidationResult from the service
        """
        if not self._ship:
            return None
        return self._ship_service.validate_design(self._ship)

    def get_available_components_for_layer(self, layer: LayerType) -> List[str]:
        """
        Get component IDs that can be added to the specified layer.

        Args:
            layer: Target layer

        Returns:
            List of valid component IDs
        """
        if not self._ship:
            return []
        return self._ship_service.get_available_components(self._ship, layer)

    def get_ship_summary(self) -> dict:
        """
        Get a summary of the current ship's stats.

        Returns:
            Dict with key ship statistics
        """
        if not self._ship:
            return {}
        return self._ship_service.get_ship_summary(self._ship)

    def clear_design(self) -> None:
        """Clear the current ship design (keeping hull)."""
        if not self._require_ship("clear design"):
            return

        logger.info("Clearing ship design")
        self._ship.clear_non_hull_components()

        self._ship.movement_policy = "kite_max"
        self._ship.targeting_policy = "standard"
        self._ship.name = "Custom Ship"

        self.clear_selection()
        self.notify_ship_changed()

    def set_ship_name(self, name: str) -> None:
        """
        Set the ship's name via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if name is unchanged.

        Args:
            name: New name for the ship
        """
        if not self._require_ship("set ship name"):
            return

        if self._ship.name == name:
            return  # No change, skip event emission

        self._ship.name = name
        self._emit_ship_updated()

    def set_ship_theme(self, theme_id: str) -> None:
        """
        Set the ship's visual theme via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if theme is unchanged.

        Args:
            theme_id: Theme identifier (e.g., "Federation", "Klingon")
        """
        if not self._require_ship("set ship theme"):
            return

        if self._ship.theme_id == theme_id:
            return  # No change, skip event emission

        self._ship.theme_id = theme_id
        self._emit_ship_updated()

    def set_ship_movement_policy(self, policy_id: str) -> None:
        """Set the ship's movement policy via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if policy is unchanged.

        Args:
            policy_id: Movement policy identifier (e.g., "kite_max", "brawl_close")
        """
        if not self._require_ship("set movement policy"):
            return

        if self._ship.movement_policy == policy_id:
            return  # No change, skip event emission

        self._ship.movement_policy = policy_id
        self._emit_ship_updated()

    def set_ship_targeting_policy(self, policy_id: str) -> None:
        """Set the ship's targeting policy via the ViewModel.

        Encapsulates direct ship mutation and emits SHIP_UPDATED event.
        Does not emit if policy is unchanged.

        Args:
            policy_id: Targeting policy identifier (e.g., "standard", "sniper")
        """
        if not self._require_ship("set targeting policy"):
            return

        if self._ship.targeting_policy == policy_id:
            return  # No change, skip event emission

        self._ship.targeting_policy = policy_id
        self._emit_ship_updated()

    def set_ship_design_role(self, role_id: str) -> None:
        """Set the ship's design role via the ViewModel.

        Args:
            role_id: Design role identifier (e.g., "line_combatant", "carrier")
        """
        if not self._require_ship("set design role"):
            return

        if self._ship.design_role == role_id:
            return

        self._ship.design_role = role_id
        self._emit_ship_updated()

    # ─────────────────────────────────────────────────────────────────
    # Quick-Add (Component Palette '+' Button)
    # ─────────────────────────────────────────────────────────────────

    def resolve_target_layer(
        self, component: Component, selected_layer: Optional[LayerType] = None
    ) -> Optional[LayerType]:
        """Resolve which layer to place a component in for quick-add.

        Rules:
        1. If selected_layer is valid for the component, use it.
        2. If selected_layer is invalid, find the nearest valid layer
           (preferring inner layers on ties).
        3. If no selected_layer, use the innermost valid layer.
        4. HULL is never a valid quick-add target.

        Args:
            component: The component template to check placement for.
            selected_layer: Currently active/filtered layer, or None.

        Returns:
            The target LayerType, or None if no valid layer exists.
        """
        if not self._ship:
            return None

        from game.simulation.validation.ship_validator import LayerRestrictionDefinitionRule
        restriction_rule = LayerRestrictionDefinitionRule()

        # Collect valid non-HULL layers
        valid_layers = []
        for l_type in self._ship.layers:
            if l_type == LayerType.HULL:
                continue
            if restriction_rule.validate(self._ship, component, l_type).is_valid:
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

        Args:
            component_id: ID of the component to add.
            selected_layer: Currently active/filtered layer, or None.
            count: Number of copies to add (default 1).

        Returns:
            True if at least one component was added, False otherwise.
        """
        if not self._require_ship("quick-add component"):
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

        if count > 1:
            return self.add_component_bulk(component_id, target_layer, count) > 0
        return self.add_component(component_id, target_layer)

    # ─────────────────────────────────────────────────────────────────
    # Component Movement Between Layers
    # ─────────────────────────────────────────────────────────────────

    def resolve_move_target(
        self,
        component: Component,
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
        if not self._ship:
            return None

        from game.simulation.validation.ship_validator import LayerRestrictionDefinitionRule
        restriction_rule = LayerRestrictionDefinitionRule()

        # Sort ship layers by value, excluding HULL
        ship_layers = sorted(
            [l for l in self._ship.layers if l != LayerType.HULL],
            key=lambda l: l.value,
        )

        if direction == "up":
            # Layers with lower value than source, in descending order (nearest first)
            candidates = [l for l in reversed(ship_layers) if l.value < source_layer.value]
        else:
            # Layers with higher value than source, in ascending order (nearest first)
            candidates = [l for l in ship_layers if l.value > source_layer.value]

        for candidate in candidates:
            if restriction_rule.validate(self._ship, component, candidate).is_valid:
                return candidate

        return None

    def move_component(
        self, source_layer: LayerType, index: int, target_layer: LayerType
    ) -> bool:
        """Move a single component from one layer to another.

        Preserves the component instance (modifiers, state). Mass budget
        violations produce warnings but do not block the move.

        Args:
            source_layer: Layer to move from.
            index: Index of the component in the source layer.
            target_layer: Layer to move to.

        Returns:
            True if successful, False otherwise.
        """
        if not self._require_ship("move component"):
            return False

        result = self._ship_service.move_component(
            self._ship, source_layer, index, target_layer
        )
        self._last_result = result

        if result.success:
            self.notify_ship_changed()
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

        Args:
            group_key: The group key identifying which components to move.
            source_layer: Layer to move from.
            target_layer: Layer to move to.

        Returns:
            True if at least one component was moved, False otherwise.
        """
        if not self._require_ship("move component group"):
            return False

        if source_layer not in self._ship.layers:
            return False

        from game.ui.screens.builder.grouping_strategies import get_component_group_key

        # Collect indices of matching components (reverse order for safe removal)
        layer_comps = self._ship.layers[source_layer].components
        indices = [
            i for i, c in enumerate(layer_comps)
            if get_component_group_key(c) == group_key
        ]

        if not indices:
            return False

        # Move in reverse index order to avoid shifting
        for idx in reversed(indices):
            self._ship_service.move_component(
                self._ship, source_layer, idx, target_layer
            )

        self.notify_ship_changed()
        return True
