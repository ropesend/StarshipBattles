"""
ComponentModifierGridPanel - A dedicated panel for displaying modifier impact grid.

This panel sits as a horizontal strip above the Weapons Report panel,
providing more space for the modifier impact grid visualization.
"""
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel
from typing import Optional, TYPE_CHECKING

from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

if TYPE_CHECKING:
    from game.simulation.components.component import Component


class ComponentModifierGridPanel:
    """
    Panel wrapper for the ModifierImpactGrid widget.

    Provides a dedicated horizontal strip panel with more space for
    displaying modifier effects compared to the embedded grid in
    ComponentDetailPanel.
    """

    def __init__(self, manager: pygame_gui.UIManager, rect: pygame.Rect, event_bus=None):
        """
        Initialize the ComponentModifierGridPanel.

        Args:
            manager: pygame_gui UIManager
            rect: Position and size of the panel
            event_bus: EventBus for subscribing to selection/update events
        """
        self.manager = manager
        self.rect = rect
        self.event_bus = event_bus

        # Create the background panel
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#component_modifier_grid_panel'
        )

        # Title label
        self.title_label = UILabel(
            relative_rect=pygame.Rect(10, 5, 250, 20),
            text="── Component Modifier Grid ──",
            manager=manager,
            container=self.panel
        )

        # Create the modifier impact grid inside this panel
        # Leave space for title at top
        grid_y = 28
        grid_rect = pygame.Rect(
            5,
            grid_y,
            rect.width - 10,
            rect.height - grid_y - 5
        )
        self.modifier_grid = ModifierImpactGrid(
            manager,
            self.panel,
            grid_rect
        )

        # Current state
        self.current_component: Optional['Component'] = None

        # Subscribe to events
        if event_bus:
            from game.ui.screens.builder_utils import BuilderEvents
            event_bus.subscribe(BuilderEvents.SELECTION_CHANGED, self._on_selection_changed)
            event_bus.subscribe(BuilderEvents.SHIP_UPDATED, self._on_ship_updated)

        # Panel is always visible (persistent) - shows "no modifier effects" when nothing selected

    def _on_selection_changed(self, selection_data):
        """Handle component selection changes."""
        if selection_data and isinstance(selection_data, tuple):
            self.update_component(selection_data[2])
        elif selection_data and hasattr(selection_data, 'id'):
            self.update_component(selection_data)
        else:
            self.update_component(None)

    def _on_ship_updated(self, _data):
        """Refresh grid when ship/component changes."""
        if self.current_component:
            self.modifier_grid.update(self.current_component)

    def update_component(self, component: Optional['Component']):
        """
        Update the panel with a new component.

        Args:
            component: Component to display modifier effects for, or None
        """
        self.current_component = component

        if component and component.modifiers:
            self.modifier_grid.update(component)
        else:
            # Show "no modifier effects to display" message (grid handles this)
            self.modifier_grid.update(None)

    def draw(self, screen: pygame.Surface):
        """
        Draw custom content on top of pygame_gui elements.

        Called after the UI manager's draw() to render the grid
        with rotated headers and custom drawing.

        Args:
            screen: Surface to draw on
        """
        if self.panel.visible:
            self.modifier_grid.draw(screen)

    def handle_event(self, event) -> bool:
        """
        Handle pygame events.

        Args:
            event: pygame event

        Returns:
            True if event was consumed
        """
        if self.panel.visible:
            return self.modifier_grid.handle_event(event)
        return False

    def show(self):
        """Show the panel."""
        self.panel.show()

    def hide(self):
        """Hide the panel."""
        self.panel.hide()

    def kill(self):
        """Clean up all UI elements."""
        self.modifier_grid.kill()
        if self.panel and self.panel.alive():
            self.panel.kill()
