import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIScrollingContainer, UIDropDownMenu
from ui.builder.components import ComponentListItem


# Local reference to BuilderEvents to avoid circular import.
# The full import chain was: ui.builder -> game.ui.__init__ -> builder_screen -> ui.builder
# We lazily import on first use instead.
_BuilderEvents = None

def _get_builder_events():
    """Lazy import of BuilderEvents to break circular import."""
    global _BuilderEvents
    if _BuilderEvents is None:
        from game.ui.screens.builder_utils import BuilderEvents
        _BuilderEvents = BuilderEvents
    return _BuilderEvents

class BuilderLeftPanel:
    def __init__(self, builder, manager, rect, event_bus=None, viewmodel=None):
        self.builder = builder
        self.viewmodel = viewmodel or builder.viewmodel
        self.manager = manager
        self.rect = rect
        self.items = []
        self.selected_item = None
        self.event_bus = event_bus
        
        if event_bus:
            event_bus.subscribe(_get_builder_events().REGISTRY_RELOADED, self.on_registry_reloaded)
        
        # Store original order of components for sorting
        self.component_order_map = {c.id: i for i, c in enumerate(self.viewmodel.available_components)}
        
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
        
        # Scroll Container 
        # Shifted down to room for Bulk Add UI
        self.list_y = 125 # Was 80
        self.list_y = 125 # Was 80
        container_height = rect.height - 130 # Full height minus offsets
        self.scroll_container = UIScrollingContainer(
            relative_rect=pygame.Rect(5, self.list_y, rect.width - 10, container_height),
            manager=manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        # Bulk Add UI (y=80)
        # Layout: Label "Count:" | Entry | <<< | << | < | Slider | > | >> | >>>
        # Widths: 40 | 45 | 25 | 25 | 25 | Slider | 25 | 25 | 25
        u_y = 80
        
        # Label
        UILabel(pygame.Rect(5, u_y, 45, 25), "Count:", manager=manager, container=self.panel)
        
        from pygame_gui.elements import UITextEntryLine, UIHorizontalSlider, UIButton
        
        # Entry
        self.count_entry = UITextEntryLine(pygame.Rect(50, u_y, 45, 25), manager=manager, container=self.panel)
        self.count_entry.set_text("1")
        self.count_entry.set_allowed_characters('numbers')
        
        btn_w = 30
        gap = 2
        
        # Buttons (All on left now)
        # Sequence: m100, m10, m1, p1, p10, p100
        start_btns = 100
        
        self.btn_m100 = UIButton(pygame.Rect(start_btns, u_y, btn_w, 25), "<<<", manager=manager, container=self.panel, object_id='#mini_arrow_btn')
        self.btn_m10  = UIButton(pygame.Rect(start_btns + btn_w + gap, u_y, btn_w, 25), "<<", manager=manager, container=self.panel, object_id='#mini_arrow_btn')
        self.btn_m1   = UIButton(pygame.Rect(start_btns + (btn_w + gap)*2, u_y, btn_w, 25), "<", manager=manager, container=self.panel, object_id='#mini_arrow_btn')
        
        # Start Positive buttons immediately after
        p_start = start_btns + (btn_w + gap)*3
        
        self.btn_p1   = UIButton(pygame.Rect(p_start, u_y, btn_w, 25), ">", manager=manager, container=self.panel, object_id='#mini_arrow_btn')
        self.btn_p10  = UIButton(pygame.Rect(p_start + btn_w + gap, u_y, btn_w, 25), ">>", manager=manager, container=self.panel, object_id='#mini_arrow_btn')
        self.btn_p100 = UIButton(pygame.Rect(p_start + (btn_w + gap)*2, u_y, btn_w, 25), ">>>", manager=manager, container=self.panel, object_id='#mini_arrow_btn')
        
        # Slider takes remaining space
        slider_x = p_start + (btn_w + gap)*3 + 5
        slider_w = rect.width - slider_x - 10
        
        self.count_slider = UIHorizontalSlider(pygame.Rect(slider_x, u_y, slider_w, 25), 1, (1, 1000), manager=manager, container=self.panel)
        
        # Row 2 (Removed, single line now)
        u_y += 35
        
        # Remove old button definitions if any references remain (not needed for replace)
        # Update event handler to respect new button names/logic


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
        all_types = sorted(list(set(c.type_str for c in self.viewmodel.available_components)))
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
        self.layer_filter_options = ["All Layers"] + [l.name for l in self.viewmodel.ship.layers.keys()]
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

    def on_registry_reloaded(self, data):
        """Handle registry reload event - refresh component list and filter options."""
        # Update available components from new registry data
        from game.simulation.components.component import get_all_components
        self.viewmodel._available_components = get_all_components()
        self.component_order_map = {c.id: i for i, c in enumerate(self.viewmodel.available_components)}
        
        # Update type filter options
        all_types = sorted(list(set(c.type_str for c in self.viewmodel.available_components)))
        self.type_filter_options = ["All Types"] + all_types
        if self.current_type_filter not in self.type_filter_options:
            self.current_type_filter = "All Types"
        
        # Rebuild the filter dropdown
        y_filters = 40
        self.filter_type_dropdown.kill()
        self.filter_type_dropdown = UIDropDownMenu(
            options_list=self.type_filter_options,
            starting_option=self.current_type_filter,
            relative_rect=pygame.Rect(5, y_filters, (self.rect.width//2)-10, 30),
            manager=self.manager,
            container=self.panel
        )
        self.filter_type_dropdown.change_layer(5)
        
        # Refresh the component list
        self.update_component_list()
        
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


        
        # Update hover state for component list items
        mx, my = pygame.mouse.get_pos()
        hovered_item = self.get_hovered_list_item(mx, my)
        for item in self.items:
            # Don't override selected state with hover
            if item != self.selected_item:
                item.set_hovered(item == hovered_item)
                 
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
        
    def deselect_all(self):
        """Deselect all items in the list."""
        for item in self.items:
            item.set_selected(False)
        self.selected_item = None
        
    def update_component_list(self):
        """Filter, sort, and populate the component list."""
        # Clear existing
        for item in self.items:
            item.kill()
        self.items = []
        
        # 1. Filter by Vehicle Type (Implicit)
        v_type = getattr(self.viewmodel.ship, 'vehicle_type', "Ship")
        filtered = [c for c in self.viewmodel.available_components if v_type in c.allowed_vehicle_types]
        
        # 1b. Exclude Hulls (they belong in the structural layout, not the palette)
        filtered = [c for c in filtered if c.type_str != "Hull"]

        # 2. Filter by Component Type
        if self.current_type_filter != "All Types":
            filtered = [c for c in filtered if c.type_str == self.current_type_filter]
            
        # 3. Filter by Layer
        # 3. Filter by Layer
        
        # Refresh options map based on current ship layers
        current_ship_layers = [l.name for l in self.viewmodel.ship.layers.keys()]
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

        
        from game.simulation.ship_validator import LayerRestrictionDefinitionRule
        from game.simulation.entities.ship import LayerType
        # Create a temporary rule instance for filtering
        restriction_rule = LayerRestrictionDefinitionRule()

        if self.current_layer_filter != "All Layers":
             # Filter by specific layer (find the LayerType enum from name)
             # self.builder.ship.layers keys are LayerType enums
             target_layer = None
             for l_key in self.viewmodel.ship.layers.keys():
                 if l_key.name == self.current_layer_filter:
                     target_layer = l_key
                     break
             
             if target_layer:
                 filtered = [c for c in filtered if restriction_rule.validate(self.viewmodel.ship, c, target_layer).is_valid]
        else:
             # "All Layers": Show if compatible with AT LEAST ONE of the CURRENT ship's layers
             valid_layer_types = list(self.viewmodel.ship.layers.keys())
             filtered = [
                 c for c in filtered 
                 if any(restriction_rule.validate(self.viewmodel.ship, c, l_type).is_valid for l_type in valid_layer_types)
             ]
        
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
                sprite_mgr=self.builder.sprite_mgr,
                ship_context=self.viewmodel.ship
            )
            self.items.append(item)
            y += item.height
            
        # Update Scroll Area
        self.scroll_container.set_scrollable_area_dimensions((item_width, y))
        
    def draw(self, screen):
        # Draw hover highlight overlay for hovered items
        for item in self.items:
            if getattr(item, 'is_hovered', False) and item != self.selected_item:
                # Get the absolute rect of the item
                abs_rect = item.get_abs_rect()
                # Check if it's visible in the scroll container
                container_rect = self.scroll_container.get_abs_rect()
                if container_rect.colliderect(abs_rect):
                    # Clip to container bounds
                    clipped = abs_rect.clip(container_rect)
                    # Draw semi-transparent highlight
                    highlight_surf = pygame.Surface((clipped.width, clipped.height), pygame.SRCALPHA)
                    highlight_surf.fill((80, 80, 120, 100))  # Semi-transparent blue-ish
                    screen.blit(highlight_surf, clipped.topleft)



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
                    # Deselect others, select clicked item while it's being carried
                    for i in self.items: i.set_selected(False)
                    item.set_selected(True)
                    self.selected_item = item
                    return ('select_component_type', item.component)



        # Handle Bulk Add UI
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.count_slider:
                val = int(event.value)
                self.count_entry.set_text(str(val))
                return None
                
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == self.count_entry:
                try:
                    val = int(event.text)
                    val = max(1, min(1000, val))
                    self.count_slider.set_current_value(val)
                except ValueError:
                    pass
                return None
                
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            current = int(self.count_slider.get_current_value())
            new_val = current
            
            # Simple Increments
            if event.ui_element == self.btn_m1: new_val = current - 1
            elif event.ui_element == self.btn_p1: new_val = current + 1
            
            # Snap Logic
            # << / >> : Snap to 10
            elif event.ui_element == self.btn_p10:
                # Next multiple of 10. (12 -> 20, 20 -> 30)
                # (current // 10 + 1) * 10
                new_val = (current // 10 + 1) * 10
            elif event.ui_element == self.btn_m10:
                # Prev multiple of 10. (12 -> 10, 10 -> 0 -> 1 min)
                # If current % 10 == 0: subtract 10
                # Else: floor(current / 10) * 10
                if current % 10 == 0:
                    new_val = current - 10
                else:
                    new_val = (current // 10) * 10
                    
            # <<< / >>> : Snap to 100
            elif event.ui_element == self.btn_p100:
                new_val = (current // 100 + 1) * 100
            elif event.ui_element == self.btn_m100:
                if current % 100 == 0:
                    new_val = current - 100
                else:
                    new_val = (current // 100) * 100
            
            if new_val != current:
                new_val = max(1, min(1000, new_val))
                self.count_slider.set_current_value(new_val)
                self.count_entry.set_text(str(new_val))
                return None
        
        return None

    def get_add_count(self):
        """Return the current value of the bulk add counter."""
        try:
            val = int(self.count_entry.get_text())
            return max(1, min(1000, val))
        except ValueError:
            return 1
        
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
