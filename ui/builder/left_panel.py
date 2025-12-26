import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIScrollingContainer, UIDropDownMenu
from builder_components import ModifierEditorPanel
from ui.builder.components import ComponentListItem

class BuilderLeftPanel:
    def __init__(self, builder, manager, rect):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        self.items = []
        self.selected_item = None
        
        # Store original order of components for sorting
        self.component_order_map = {c.id: i for i, c in enumerate(builder.available_components)}
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#left_panel'
        )
        
        # Title
        UILabel(
            relative_rect=pygame.Rect(10, 5, 100, 30),
            text="Components",
            manager=manager,
            container=self.panel
        )
        
        # Scroll Container - Created FIRST to ensure Dropdowns draw on top (Z-order)
        self.list_y = 80
        container_height = (rect.height // 2) - 85
        self.scroll_container = UIScrollingContainer(
            relative_rect=pygame.Rect(5, self.list_y, rect.width - 10, container_height),
            manager=manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )

        # Controls Row 1: Sort
        self.sort_options = [
            "Default (JSON Order)", 
            "Name (A-Z)", 
            "Classification", 
            "Type", 
            "Mass (Low-High)", 
            "Mass (High-Low)"
        ]
        self.current_sort = "Default (JSON Order)"
        self.sort_dropdown = UIDropDownMenu(
            options_list=self.sort_options,
            starting_option=self.current_sort,
            relative_rect=pygame.Rect(rect.width - 160, 5, 150, 30),
            manager=manager,
            container=self.panel
        )
        self.sort_dropdown.change_layer(5) # Ensure above list
        
        # Controls Row 2: Filters
        y_filters = 40
        
        # Filter: Type
        # Gather all types
        all_types = sorted(list(set(c.type_str for c in builder.available_components)))
        self.type_filter_options = ["All Types"] + all_types
        self.current_type_filter = "All Types"
        
        self.filter_type_dropdown = UIDropDownMenu(
            options_list=self.type_filter_options,
            starting_option=self.current_type_filter,
            relative_rect=pygame.Rect(5, y_filters, (rect.width//2)-10, 30),
            manager=manager,
            container=self.panel
        )
        self.filter_type_dropdown.change_layer(5)
        
        # Filter: Layer
        # Initial population - will be updated dynamically
        self.layer_filter_options = ["All Layers"] + [l.name for l in builder.ship.layers.keys()]
        self.current_layer_filter = "All Layers"
        self.filter_layer_dropdown = UIDropDownMenu(
            options_list=self.layer_filter_options,
            starting_option=self.current_layer_filter,
            relative_rect=pygame.Rect((rect.width//2)+5, y_filters, (rect.width//2)-10, 30),
            manager=manager,
            container=self.panel
        )
        self.filter_layer_dropdown.change_layer(5)

        
        # Modifier Panel
        self.modifier_panel = ModifierEditorPanel(
            manager=manager,
            container=self.panel,
            width=rect.width,
            preset_manager=builder.preset_manager,
            on_change_callback=self._on_modifier_change
        )
        self.rebuild_modifier_ui()
        
    def update(self, dt):
        """Update panel logic."""
        # Check for expanded dropdowns and track which one
        self._dropdown_expanded = False
        self._expanded_dropdown = None
        dropdowns = [self.sort_dropdown, self.filter_type_dropdown, self.filter_layer_dropdown]
        for dd in dropdowns:
             if dd.current_state == dd.menu_states['expanded']:
                 self._dropdown_expanded = True
                 self._expanded_dropdown = dd
                 break
        
        # Hide list and OTHER dropdowns when one dropdown is open
        if self._dropdown_expanded:
             if self.scroll_container.visible:
                 self.scroll_container.hide()
             # Hide the other dropdowns (not the expanded one)
             for dd in dropdowns:
                 if dd != self._expanded_dropdown and dd.visible:
                     dd.hide()
        else:
             if not self.scroll_container.visible:
                 self.scroll_container.show()
             # Show all dropdowns
             for dd in dropdowns:
                 if not dd.visible:
                     dd.show()

        # Update Modifier Panel
        if hasattr(self.modifier_panel, 'update'):
            self.modifier_panel.update(dt)
                 
    def is_dropdown_expanded(self):
        """Check if any filter/sort dropdown is currently expanded."""
        return getattr(self, '_dropdown_expanded', False)
        
    def get_hovered_list_item(self, mx, my):
        """
        Returns the ComponentListItem that the mouse is hovering over, if any.
        Returns None if mouse is not over an item or if a dropdown is expanded.
        """
        if self.is_dropdown_expanded():
            return None
            
        # Check if mouse is within the scroll container's visible area
        container_rect = self.scroll_container.get_abs_rect()
        if not container_rect.collidepoint(mx, my):
            return None
            
        # Find which item is hovered
        for item in self.items:
            # Get the absolute rect of the item's panel
            item_abs_rect = item.panel.get_abs_rect()
            # Also need to check it's within the visible scroll area (clip)
            if item_abs_rect.collidepoint(mx, my):
                # Check if this part of the item is actually visible (not scrolled out)
                if container_rect.contains(item_abs_rect) or container_rect.colliderect(item_abs_rect):
                    return item
        return None
        
    def update_component_list(self):
        """Filter, sort, and populate the component list."""
        # Clear existing
        for item in self.items:
            item.kill()
        self.items = []
        
        # 1. Filter by Vehicle Type (Implicit)
        v_type = getattr(self.builder.ship, 'vehicle_type', "Ship")
        filtered = [c for c in self.builder.available_components if v_type in c.allowed_vehicle_types]
        
        # 2. Filter by Component Type
        if self.current_type_filter != "All Types":
            filtered = [c for c in filtered if c.type_str == self.current_type_filter]
            
        # 3. Filter by Layer
        # 3. Filter by Layer
        
        # Refresh options map based on current ship layers
        current_ship_layers = [l.name for l in self.builder.ship.layers.keys()]
        expected_options = ["All Layers"] + sorted(current_ship_layers)
        
        # If options changed (e.g. ship class changed), rebuild dropdown
        # Note: We can't easily check internal options of UIDropDownMenu in all versions, but we can check our list
        if expected_options != self.layer_filter_options:
            self.layer_filter_options = expected_options
            # Reset filter if current selection is invalid
            if self.current_layer_filter not in self.layer_filter_options:
                self.current_layer_filter = "All Layers"
                
            # Recreate dropdown (cleanest way to update options)
            self.filter_layer_dropdown.kill()
            y_filters = 40
            self.filter_layer_dropdown = UIDropDownMenu(
                options_list=self.layer_filter_options,
                starting_option=self.current_layer_filter,
                relative_rect=pygame.Rect((self.rect.width//2)+5, y_filters, (self.rect.width//2)-10, 30),
                manager=self.manager,
                container=self.panel
            )
            self.filter_layer_dropdown.change_layer(5)

        if self.current_layer_filter != "All Layers":
             # Filter by specific layer
             filtered = [c for c in filtered if any(l.name == self.current_layer_filter for l in c.allowed_layers)]
        else:
             # "All Layers": Only show components compatible with AT LEAST ONE of the CURRENT ship's layers
             # Access ship layers via builder
             valid_layer_types = set(self.builder.ship.layers.keys())
             # Filter items that have at least one allowed layer that is present on this ship
             filtered = [c for c in filtered if any(l in valid_layer_types for l in c.allowed_layers)]
        
        # 4. Sort
        if self.current_sort == "Default (JSON Order)":
            filtered.sort(key=lambda c: self.component_order_map.get(c.id, 9999))
        elif self.current_sort == "Classification":
            # Sort by Classification, then Name
            filtered.sort(key=lambda c: (c.data.get('major_classification', 'Unknown'), c.name))
        elif self.current_sort == "Mass (Low-High)":
            filtered.sort(key=lambda c: c.mass)
        elif self.current_sort == "Mass (High-Low)":
            filtered.sort(key=lambda c: c.mass, reverse=True)
        elif self.current_sort == "Name (A-Z)":
            filtered.sort(key=lambda c: c.name)
        elif self.current_sort == "Type":
            filtered.sort(key=lambda c: (c.type_str, c.name))
            
        # Create Items
        item_width = self.scroll_container.get_container().get_rect().width
        y = 0
        for comp in filtered:
            item = ComponentListItem(
                component=comp,
                manager=self.manager,
                container=self.scroll_container,
                y_pos=y,
                width=item_width,
                sprite_mgr=self.builder.sprite_mgr
            )
            self.items.append(item)
            y += item.height
            
        # Update Scroll Area
        self.scroll_container.set_scrollable_area_dimensions((item_width, y))
        
    def draw(self, screen):
        # Icons are now drawn by UIImage widgets inside slots
        pass

    def _on_modifier_change(self):
        if self.builder.selected_component:
            self.builder.selected_component[2].recalculate_stats()
        self.builder.ship.recalculate_stats()
        self.builder.right_panel.update_stats_display(self.builder.ship)

    def rebuild_modifier_ui(self):
        editing_component = self.builder.selected_component[2] if self.builder.selected_component else None
        half_page_y = self.rect.height // 2
        self.modifier_panel.rebuild(editing_component, self.builder.template_modifiers)
        self.modifier_panel.layout(half_page_y)

    def handle_event(self, event):
        # Handle Sort Dropdown
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.sort_dropdown:
                self.current_sort = event.text
                self.update_component_list()
                return None
            elif event.ui_element == self.filter_type_dropdown:
                self.current_type_filter = event.text
                self.update_component_list()
                return None
            elif event.ui_element == self.filter_layer_dropdown:
                self.current_layer_filter = event.text
                self.update_component_list()
                return None
            
        # Handle Item Clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for item in self.items:
                if event.ui_element == item.button:
                    # Deselect others
                    for i in self.items: i.set_selected(False)
                    item.set_selected(True)
                    self.selected_item = item
                    return ('select_component_type', item.component)

        # Modifier Panel
        action = self.modifier_panel.handle_event(event)
        return action
        
    def get_hovered_component(self, mx, my):
        # Check if mouse is over any item button
        # Using pygame_gui check_hover logic might be tricky since button is internal
        # But we can check if button.rect contains mouse
        
        # Simple check: iterate visible items?
        # ComponentListItem is wrapper, self.button is the UI element
        for item in self.items:
            # We must use the absolute rect of the button
            # But button.rect is relative to container? No, pygame_gui element.rect is usually absolute screen rect 
            # OR relative depends on container. 
            # In pygame_gui 0.6.x, .rect is usually absolute screen position for interaction.
            # Let's trust button.rect.collidepoint
            if item.button.rect.collidepoint(mx, my):
                return item.component
        return None
