"""Drag-and-drop interaction controller for the ship builder UI.

Handles mouse interactions, component selection, and drag-drop operations
between the component palette and ship view.
"""
import pygame
from game.core.profiling import profile_action


class InteractionController:
    """Manages drag-drop and selection interactions in the ship builder.

    This controller handles all mouse-based interactions including:
    - Component selection via left-click
    - Drag-and-drop from palette to ship view
    - Clone operations (Alt+click on existing component)
    - Multi-placement mode (Shift held during drop)
    - Hover detection for visual feedback

    The controller maintains selection state and coordinates with registered
    drop targets to determine valid drop locations.

    Attributes:
        builder: The BuilderSceneGUI instance this controller belongs to.
        view: The ShipBuilderView for visual representation.
        dragged_item: Currently dragged component, or None.
        selected_component: Currently selected component tuple (layer, index, comp), or None.
        hovered_component: Component currently under mouse cursor, or None.
        drop_targets: List of registered DropTarget instances.
    """

    def __init__(self, builder, view):
        """Initialize the interaction controller.

        Args:
            builder: The BuilderSceneGUI instance providing access to ship,
                panels, and callback methods.
            view: The ShipBuilderView for coordinate translation and
                component hit detection.
        """
        self.builder = builder
        self.view = view
        self.dragged_item = None
        self.selected_component = None
        self.hovered_component = None
        self.drop_targets = []

    def register_drop_target(self, target):
        """Register a drop target that can accept component drops.

        Args:
            target: Object implementing the DropTarget interface:
                - can_accept_drop(pos) -> bool: Check if position is valid
                - accept_drop(pos, component, count) -> bool: Handle the drop
                - suppress_toggle() (optional): Prevent UI toggle on drop
        """
        self.drop_targets.append(target)

    def handle_event(self, event):
        """Process mouse events for drag-drop and selection.

        Handles MOUSEBUTTONDOWN and MOUSEBUTTONUP events for left-click:
        - Click on component: Select it (first click) or pick up (second click)
        - Alt+click on component: Clone it and start dragging
        - Click on empty space: Deselect current selection
        - Release while dragging: Drop at current position
        - Shift+release: Drop and continue dragging a clone (multi-place mode)

        Args:
            event: Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Left Click
                # Ignore clicks if over detail panel (which sits inside/over the view)
                if self.builder.detail_panel.rect.collidepoint(event.pos):
                    return

                if self.view.rect.collidepoint(event.pos) and not self.dragged_item:
                    found = self.view.get_component_at(event.pos, self.builder.ship)
                    if found:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                            # Clone
                            original = found[2]
                            self.dragged_item = original.clone()
                            for m in original.modifiers:
                                new_m = m.definition.create_modifier(m.value)
                                self.dragged_item.modifiers.append(new_m)
                            self.dragged_item.recalculate_stats()
                        elif self.selected_component == found:
                            # Pick up
                            layer, index, comp = found
                            self.builder.ship.remove_component(layer, index)
                            self.dragged_item = comp
                            self.selected_component = None
                            self.builder.on_selection_changed(None)
                            self.builder.update_stats()
                        else:
                            # Select
                            self.selected_component = found
                            self.builder.on_selection_changed(found)
                    else:
                        # Deselect
                        self.selected_component = None
                        self.builder.on_selection_changed(None)
                        
        elif event.type == pygame.MOUSEBUTTONUP:
             if event.button == 1 and self.dragged_item:
                 keys = pygame.key.get_pressed()
                 shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                 
                 item_to_clone = self.dragged_item
                 self._handle_drop(event.pos)
                 
                 if shift_held:
                     self.dragged_item = item_to_clone.clone()
                     for m in item_to_clone.modifiers:
                        self.dragged_item.add_modifier(m.definition.id)
                        new_m = self.dragged_item.get_modifier(m.definition.id)
                        if new_m: new_m.value = m.value
                     self.dragged_item.recalculate_stats()
                 else:
                      self.dragged_item = None
                      self.builder.left_panel.deselect_all()  # Clear selection when no longer carrying

    def update(self):
        """Update hover state based on current mouse position.

        Called each frame to track which component (if any) is under the
        mouse cursor. Updates hovered_component for visual feedback.
        """
        mx, my = pygame.mouse.get_pos()
        self.hovered_component = None
        if self.view.rect.collidepoint(mx, my):
             found = self.view.get_component_at((mx, my), self.builder.ship)
             if found:
                 self.hovered_component = found[2]

    @profile_action("Builder: Drop Component")
    def _handle_drop(self, pos):
        comp = self.dragged_item
        
        # Check bulk add count
        count = self.builder.left_panel.get_add_count()

        handled = False
        for target in self.drop_targets:
            if target.can_accept_drop(pos):
                target.suppress_toggle()

                if target.accept_drop(pos, comp, count):
                    handled = True
                    break
        
        if not handled:
             # Just return, drop cancelled/ignored
             return
