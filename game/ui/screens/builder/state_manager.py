"""
BuilderStateManager - Centralized state management for ship builder.

PROJ-44 Phase 7 Task 7.3: Extracted from BuilderScreen to reduce
complexity and improve testability.

Manages:
- Component selection (single and multi-select)
- Template modifiers for new components
- Pending action queue (for confirmation dialogs)
- Drag/drop state tracking

All UI panels can reference this manager for consistent state.
"""
from typing import List, Tuple, Optional, Callable, Dict, Any, Union


class BuilderStateManager:
    """
    Manages builder UI state separately from rendering logic.

    Attributes:
        ship: The ship being edited
        selected_components: List of (layer_type, index, component) tuples
        template_modifiers: Dict of modifier_id -> value for new components
        pending_action: Tuple of (action_type, data) awaiting confirmation
        dragged_item: Component currently being dragged
        on_selection_changed_callback: Optional callback when selection changes
    """

    def __init__(self, ship):
        """
        Initialize state manager.

        Args:
            ship: The ship entity being edited
        """
        self._ship = ship
        self._selected_components: List[Tuple] = []
        self._template_modifiers: Dict[str, Any] = {}
        self._pending_action: Optional[Tuple[str, Any]] = None
        self._dragged_item = None
        self.on_selection_changed_callback: Optional[Callable] = None

    @property
    def ship(self):
        """Get the ship being edited."""
        return self._ship

    @ship.setter
    def ship(self, value):
        """Set a new ship and clear selection."""
        self._ship = value
        self.clear_selection()

    @property
    def selected_components(self) -> List[Tuple]:
        """Get list of selected components as (layer, index, component) tuples."""
        return self._selected_components

    @selected_components.setter
    def selected_components(self, value: List[Tuple]):
        """Set selected components directly (for compatibility)."""
        self._selected_components = value

    @property
    def selected_component(self) -> Optional[Tuple]:
        """
        Get the primary selected component.

        Returns the last component in selection (most recently selected),
        or None if nothing is selected.
        """
        return self._selected_components[-1] if self._selected_components else None

    @property
    def template_modifiers(self) -> Dict[str, Any]:
        """Get template modifiers applied to newly created components."""
        return self._template_modifiers

    @property
    def pending_action(self) -> Optional[Tuple[str, Any]]:
        """Get pending action awaiting confirmation."""
        return self._pending_action

    @property
    def dragged_item(self):
        """Get currently dragged component."""
        return self._dragged_item

    @dragged_item.setter
    def dragged_item(self, value):
        """Set dragged component."""
        self._dragged_item = value

    def on_selection_changed(
        self,
        new_selection: Union[None, Any, List],
        append: bool = False,
        toggle: bool = False
    ) -> None:
        """
        Handle selection changes with multi-select support.

        Args:
            new_selection: Component, tuple, list of components/tuples, or None
            append: If True, add to existing selection instead of replacing
            toggle: If True, toggle selection state (Ctrl+Click behavior)
        """
        if new_selection is None:
            if not append:
                self._selected_components = []
        else:
            # Normalize to list
            if not isinstance(new_selection, list):
                new_selection = [new_selection]

            # Normalize each item to (layer, index, component) tuple
            norm_selection = self._normalize_selection(new_selection)

            if append:
                self._handle_append_selection(norm_selection, toggle)
            else:
                self._selected_components = norm_selection

        # Notify listeners
        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(self.selected_component)

    def _normalize_selection(self, items: List) -> List[Tuple]:
        """
        Normalize selection items to (layer, index, component) tuples.

        Handles:
        - Already normalized tuples
        - Bare component objects (looks up in ship)
        """
        normalized = []
        for item in items:
            if isinstance(item, tuple) and len(item) == 3:
                normalized.append(item)
            elif hasattr(item, 'id'):
                # It's a component - find it in ship
                found = self._find_component_in_ship(item)
                if found:
                    normalized.append(found)
                else:
                    # Not in ship (template/dragged) - use placeholder
                    normalized.append((None, -1, item))
        return normalized

    def _find_component_in_ship(self, component) -> Optional[Tuple]:
        """
        Find a component in the ship's layers.

        Returns:
            (layer_type, index, component) tuple or None if not found
        """
        for layer_type, layer_data in self._ship.layers.items():
            try:
                idx = layer_data['components'].index(component)
                return (layer_type, idx, component)
            except ValueError:
                continue
        return None

    def _handle_append_selection(self, norm_selection: List[Tuple], toggle: bool) -> None:
        """
        Handle appending to existing selection with homogeneity enforcement.

        Args:
            norm_selection: Normalized selection items to add
            toggle: If True, toggle items that are already selected
        """
        if not self._selected_components or not norm_selection:
            # Nothing to compare against or nothing to add
            if not self._selected_components:
                self._selected_components = norm_selection
            else:
                # Add unique items
                self._add_unique_to_selection(norm_selection, toggle)
            return

        # Enforce homogeneity - all items must have same definition ID
        current_def_id = self._selected_components[0][2].id
        matches_type = all(item[2].id == current_def_id for item in norm_selection)

        if not matches_type:
            # Different type - replace selection entirely
            self._selected_components = norm_selection
        else:
            # Same type - add unique items
            self._add_unique_to_selection(norm_selection, toggle)

    def _add_unique_to_selection(self, norm_selection: List[Tuple], toggle: bool) -> None:
        """
        Add items to selection, handling uniqueness and toggle behavior.

        Uses object identity (not definition ID) for uniqueness.
        """
        current_objs = {c[2] for c in self._selected_components}

        for item in norm_selection:
            if item[2] in current_objs:
                if toggle:
                    # Toggle OFF - remove from selection
                    self._selected_components = [
                        x for x in self._selected_components if x[2] is not item[2]
                    ]
            else:
                # Not in selection - add it
                self._selected_components.append(item)

    def clear_selection(self) -> None:
        """Clear all selected components."""
        self._selected_components = []
        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(None)

    def remove_from_selection(self, component) -> None:
        """
        Remove a specific component from selection.

        Args:
            component: The component to remove (matches by identity)
        """
        self._selected_components = [
            x for x in self._selected_components if x[2] is not component
        ]
        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(self.selected_component)

    # --- Template Modifiers ---

    def set_template_modifiers(self, modifiers: Dict[str, Any]) -> None:
        """
        Set template modifiers for new components.

        Args:
            modifiers: Dict of modifier_id -> value
        """
        self._template_modifiers = dict(modifiers)

    def clear_template_modifiers(self) -> None:
        """Clear all template modifiers."""
        self._template_modifiers = {}

    # --- Pending Actions ---

    def set_pending_action(self, action_type: str, data: Any) -> None:
        """
        Queue an action awaiting confirmation.

        Args:
            action_type: Type of action (e.g., 'change_class', 'clear_design')
            data: Action-specific data
        """
        self._pending_action = (action_type, data)

    def clear_pending_action(self) -> None:
        """Clear pending action without executing."""
        self._pending_action = None

    def get_and_clear_pending_action(self) -> Optional[Tuple[str, Any]]:
        """
        Get and clear pending action atomically.

        Returns:
            The pending action tuple or None
        """
        action = self._pending_action
        self._pending_action = None
        return action

    # --- Full State Management ---

    def clear_all(self) -> None:
        """Clear all state (selection, modifiers, pending action, dragged item)."""
        self._selected_components = []
        self._template_modifiers = {}
        self._pending_action = None
        self._dragged_item = None
        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(None)
