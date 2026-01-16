"""
BuilderViewModel - Central ViewModel for Ship Builder MVVM architecture.

Manages all builder state and notifies views via EventBus when state changes.
Extracted from BuilderSceneGUI for better separation of concerns and testability.

Uses ShipBuilderService for ship operations, providing validation and error handling.
"""
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component, get_all_components
from game.simulation.services import ShipBuilderService, ShipBuilderResult
from game.core.registry import get_modifier_registry

import logging
logger = logging.getLogger(__name__)


class BuilderViewModel:
    """
    Central ViewModel for Ship Builder.
    
    Holds all builder state and emits events via EventBus when state changes.
    Views subscribe to events and update themselves accordingly.
    
    Events emitted:
        - SHIP_UPDATED: When ship or its properties change
        - SELECTION_CHANGED: When component selection changes
        - TEMPLATE_MODIFIERS_CHANGED: When template modifiers change
        - DRAG_STATE_CHANGED: When drag operation starts/ends
    """
    
    def __init__(self, event_bus, screen_width: int, screen_height: int):
        """
        Initialize the ViewModel.

        Args:
            event_bus: EventBus instance for emitting state change notifications
            screen_width: Screen width for ship positioning
            screen_height: Screen height for ship positioning
        """
        self.event_bus = event_bus
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Service layer for ship operations
        self._ship_service = ShipBuilderService()

        # Last operation result (for error display)
        self._last_result: Optional[ShipBuilderResult] = None

        # Core state
        self._ship: Optional[Ship] = None
        self._selected_components: List[Tuple[LayerType, int, Component]] = []
        self._template_modifiers: Dict[str, Any] = {}
        self._dragged_item: Optional[Component] = None
        self._available_components: List[Component] = []
        self._show_hull_layer: bool = False
        
    # ─────────────────────────────────────────────────────────────────
    # Ship Property
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def ship(self) -> Optional[Ship]:
        """The ship currently being edited."""
        return self._ship
    
    @ship.setter
    def ship(self, value: Ship):
        self._ship = value
        self._emit_ship_updated()
        
    def _emit_ship_updated(self):
        """Emit SHIP_UPDATED event."""
        self.event_bus.emit('SHIP_UPDATED', self._ship)
        
    def notify_ship_changed(self):
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
    
    @property
    def primary_selection(self) -> Optional[Tuple[LayerType, int, Component]]:
        """The primary (last) selected component, or None if nothing selected."""
        return self._selected_components[-1] if self._selected_components else None
    
    @property
    def selected_component(self) -> Optional[Tuple[LayerType, int, Component]]:
        """Alias for primary_selection for backward compatibility."""
        return self.primary_selection
        
    def select_component(self, new_selection, append: bool = False, toggle: bool = False):
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
        """Convert various selection formats to normalized tuples."""
        norm_selection = []
        for item in items:
            if isinstance(item, tuple) and len(item) == 3:
                norm_selection.append(item)
            elif hasattr(item, 'id'):  # It's a component
                # Find it in ship
                found = False
                if self._ship:
                    for l_type, l_data in self._ship.layers.items():
                        try:
                            idx = l_data['components'].index(item)
                            norm_selection.append((l_type, idx, item))
                            found = True
                            break
                        except ValueError:
                            continue
                if not found:
                    # Template/dragged component
                    norm_selection.append((None, -1, item))
        return norm_selection
        
    def _handle_append_selection(self, norm_selection: List, toggle: bool):
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
                
    def _emit_selection_changed(self):
        """Emit SELECTION_CHANGED event."""
        self.event_bus.emit('SELECTION_CHANGED', self.primary_selection)
        
    def clear_selection(self):
        """Clear all selected components."""
        self._selected_components = []
        self._emit_selection_changed()
        
    # ─────────────────────────────────────────────────────────────────
    # Template Modifiers Property
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def template_modifiers(self) -> Dict[str, Any]:
        """Modifiers to apply to new components."""
        return self._template_modifiers
    
    @template_modifiers.setter
    def template_modifiers(self, value: Dict[str, Any]):
        self._template_modifiers = value
        self.event_bus.emit('TEMPLATE_MODIFIERS_CHANGED', value)
        
    def set_template_modifier(self, mod_id: str, value: Any):
        """Set a single template modifier value."""
        self._template_modifiers[mod_id] = value
        self.event_bus.emit('TEMPLATE_MODIFIERS_CHANGED', self._template_modifiers)
        
    def remove_template_modifier(self, mod_id: str):
        """Remove a template modifier."""
        if mod_id in self._template_modifiers:
            del self._template_modifiers[mod_id]
            self.event_bus.emit('TEMPLATE_MODIFIERS_CHANGED', self._template_modifiers)
            
    def clear_template_modifiers(self):
        """Clear all template modifiers."""
        self._template_modifiers = {}
        self.event_bus.emit('TEMPLATE_MODIFIERS_CHANGED', self._template_modifiers)
        
    # ─────────────────────────────────────────────────────────────────
    # Drag State Property
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def dragged_item(self) -> Optional[Component]:
        """The component currently being dragged, or None."""
        return self._dragged_item
    
    @dragged_item.setter
    def dragged_item(self, value: Optional[Component]):
        self._dragged_item = value
        self.event_bus.emit('DRAG_STATE_CHANGED', value)
        
    # ─────────────────────────────────────────────────────────────────
    # Available Components Property
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def available_components(self) -> List[Component]:
        """List of available components for the current ship configuration."""
        return self._available_components
    
    def refresh_available_components(self):
        """Refresh the available components list from registry."""
        self._available_components = get_all_components()
        
    # ─────────────────────────────────────────────────────────────────
    # Hull Layer Visibility
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def show_hull_layer(self) -> bool:
        """Whether the hull layer is visible in the structure panel."""
        return self._show_hull_layer
    
    @show_hull_layer.setter
    def show_hull_layer(self, value: bool):
        if self._show_hull_layer != value:
            self._show_hull_layer = value
            self.event_bus.emit('HULL_LAYER_VISIBILITY_CHANGED', value)
    
    def toggle_hull_layer(self) -> bool:
        """Toggle hull layer visibility and return the new state."""
        self.show_hull_layer = not self._show_hull_layer
        return self._show_hull_layer
        
    # ─────────────────────────────────────────────────────────────────
    # Modifier Synchronization
    # ─────────────────────────────────────────────────────────────────
    
    def sync_modifiers_to_selection(self):
        """
        Synchronize modifiers from primary selection to all selected components.
        
        Called when modifiers change on the primary selected component.
        """
        if not self._selected_components or len(self._selected_components) <= 1:
            return
            
        primary = self.primary_selection
        if not primary:
            return
            
        editing_comp = primary[2]
        
        for item in self._selected_components:
            comp = item[2]
            if comp is editing_comp:
                continue
                
            # Copy modifiers
            comp.modifiers = []
            for m in editing_comp.modifiers:
                new_m = m.__class__(m.definition, m.value)
                comp.modifiers.append(new_m)
            comp.recalculate_stats()
            
        editing_comp.recalculate_stats()
        self.notify_ship_changed()
        
    # ─────────────────────────────────────────────────────────────────
    # Ship Operations (Service-backed)
    # ─────────────────────────────────────────────────────────────────

    @property
    def last_result(self) -> Optional[ShipBuilderResult]:
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
        """Create a new ship with default settings using the service."""
        result = self._ship_service.create_ship(
            name="Custom Ship",
            ship_class=ship_class,
            x=self.screen_width // 2,
            y=self.screen_height // 2,
            color=(100, 100, 255)
        )
        self._last_result = result

        if result.success and result.ship:
            self.ship = result.ship
            return result.ship
        else:
            # Fallback to direct creation if service fails
            logger.warning(f"Service failed to create ship: {result.errors}")
            ship = Ship(
                "Custom Ship",
                self.screen_width // 2,
                self.screen_height // 2,
                (100, 100, 255),
                ship_class=ship_class
            )
            ship.recalculate_stats()
            self.ship = ship
            return ship

    def add_component(self, component_id: str, layer: LayerType) -> bool:
        """
        Add a component to the current ship using the service.

        Args:
            component_id: ID of the component to add
            layer: Target layer

        Returns:
            True if successful, False otherwise
        """
        if not self._ship:
            logger.error("Cannot add component: no ship")
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
        if not self._ship:
            logger.error("Cannot add components: no ship")
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

    def remove_component(self, layer: LayerType, index: int) -> Optional[Component]:
        """
        Remove a component from the current ship using the service.

        Args:
            layer: Layer containing the component
            index: Index of the component

        Returns:
            The removed component, or None if removal failed
        """
        if not self._ship:
            logger.error("Cannot remove component: no ship")
            return None

        result = self._ship_service.remove_component(self._ship, layer, index)
        self._last_result = result

        if result.success:
            self.notify_ship_changed()
            return result.removed_component
        else:
            logger.warning(f"Failed to remove component: {result.errors}")
            return None

    def change_ship_class(self, new_class: str) -> bool:
        """
        Change the ship's vehicle class using the service.

        Args:
            new_class: Target vehicle class

        Returns:
            True if successful, False otherwise
        """
        if not self._ship:
            logger.error("Cannot change class: no ship")
            return False

        result = self._ship_service.change_class(self._ship, new_class)
        self._last_result = result

        if result.success:
            self.clear_selection()
            self.notify_ship_changed()
            return True
        else:
            logger.warning(f"Failed to change class: {result.errors}")
            return False

    def validate_design(self):
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

    def clear_design(self):
        """Clear the current ship design (keeping hull)."""
        if not self._ship:
            return

        logger.info("Clearing ship design")

        for layer_type, layer_data in self._ship.layers.items():
            if layer_type == LayerType.HULL:
                continue
            layer_data['components'] = []
            layer_data['hp_pool'] = 0
            layer_data['max_hp_pool'] = 0
            layer_data['mass'] = 0
            layer_data['hp'] = 0

        self._template_modifiers = {}
        self._ship.ai_strategy = "standard_ranged"
        self._ship.name = "Custom Ship"
        self._ship.recalculate_stats()

        self.clear_selection()
        self.notify_ship_changed()
